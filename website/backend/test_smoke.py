#!/usr/bin/env python3
"""SSE contract smoke test for app.py — no AWS, no pip deps.

Injects a stub boto3 in-process, boots the real server on an ephemeral port,
and asserts: /healthz, 400 on bad input, and the full streaming contract
(meta with sources -> tokens -> done) with a cleanly terminated connection.
Run: python3 test_smoke.py   (exit 0 = pass) — CI runs this on every push.
"""

import json
import os
import sys
import threading
import types
import urllib.error
import urllib.request

# ---- stub boto3 before importing app ----------------------------------------


class _AgentRT:
    def retrieve(self, **kw):
        assert kw["knowledgeBaseId"] == "KB-TEST"
        return {
            "retrievalResults": [
                {
                    "content": {"text": "Prompt caching cheapens repeated prefixes."},
                    "metadata": {"breadcrumb": "Guide 7 >> Prompt Caching"},
                    "score": 0.91,
                },
                {
                    "content": {"text": "Semantic caching skips the model call."},
                    "metadata": {"breadcrumb": "Cram sheet D4"},
                    "score": 0.84,
                },
            ]
        }


class _BedrockRT:
    def converse_stream(self, **kw):
        assert kw["modelId"] == "test-model"
        assert "CONTEXT PASSAGES" in kw["messages"][-1]["content"][0]["text"]
        return {
            "stream": iter(
                [
                    {"contentBlockDelta": {"delta": {"text": "Caching cheapens [1] "}}},
                    {"contentBlockDelta": {"delta": {"text": "or removes [2] the call."}}},
                    {"messageStop": {"stopReason": "end_turn"}},
                ]
            )
        }


stub = types.ModuleType("boto3")
stub.client = lambda name, **kw: {
    "bedrock-agent-runtime": _AgentRT(),
    "bedrock-runtime": _BedrockRT(),
}[name]
sys.modules["boto3"] = stub

os.environ.update({"KB_ID": "KB-TEST", "MODEL_ID": "test-model"})
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import app  # noqa: E402  (imports the stub above)

# ---- boot the real server on an ephemeral port -------------------------------

from http.server import ThreadingHTTPServer  # noqa: E402

server = ThreadingHTTPServer(("127.0.0.1", 0), app.Handler)
port = server.server_address[1]
threading.Thread(target=server.serve_forever, daemon=True).start()
base = f"http://127.0.0.1:{port}"

failures = []


def check(name, cond):
    print(("PASS " if cond else "FAIL ") + name)
    if not cond:
        failures.append(name)


# 1. health
with urllib.request.urlopen(f"{base}/healthz", timeout=5) as r:
    check("healthz 200/ok", r.status == 200 and r.read() == b"ok")

# 2. bad request
try:
    urllib.request.urlopen(
        urllib.request.Request(
            f"{base}/chat", data=b"{}", headers={"Content-Type": "application/json"}
        ),
        timeout=5,
    )
    check("empty message -> 400", False)
except urllib.error.HTTPError as e:
    check("empty message -> 400", e.code == 400)

# 3. streaming contract (urlopen returns only after the server closes the
#    connection — hanging here would mean the Connection: close fix regressed)
req = urllib.request.Request(
    f"{base}/chat",
    data=json.dumps(
        {
            "message": "caching?",
            "history": [{"role": "user", "text": "hi"}, {"role": "assistant", "text": "hello"}],
        }
    ).encode(),
    headers={"Content-Type": "application/json"},
)
with urllib.request.urlopen(req, timeout=10) as r:
    raw = r.read().decode()

events = []
for frame in raw.strip().split("\n\n"):
    ev, data = "message", ""
    for line in frame.split("\n"):
        if line.startswith("event: "):
            ev = line[7:].strip()
        elif line.startswith("data: "):
            data += line[6:]
    events.append((ev, json.loads(data)))

kinds = [e for e, _ in events]
check(
    "event order meta->tokens->done",
    kinds[0] == "meta" and kinds[-1] == "done" and kinds.count("token") == 2,
)
check(
    "meta carries 2 breadcrumbed sources",
    len(events[0][1]["sources"]) == 2 and "Guide 7" in events[0][1]["sources"][0]["breadcrumb"],
)
text = "".join(d["t"] for e, d in events if e == "token")
check("tokens assemble the reply", text == "Caching cheapens [1] or removes [2] the call.")
check("done reports ttlt_ms", isinstance(events[-1][1].get("ttlt_ms"), int))

server.shutdown()
if failures:
    sys.exit(f"{len(failures)} smoke-test failure(s)")
print("smoke test: all green")
