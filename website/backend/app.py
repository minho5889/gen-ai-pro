"""Streaming chat relay: Knowledge Base retrieval -> Nova 2 Lite -> SSE.

Runs as a plain stdlib HTTP server behind the AWS Lambda Web Adapter layer,
which is what gives a Python Lambda true response streaming (natively a
Node-only feature). Zero pip dependencies — boto3 ships in the runtime.

Contract:
  POST /chat  {"message": str, "history": [{"role": "user"|"assistant", "text": str}]}
  -> text/event-stream:
       event: meta    data: {"retrieval_ms": int, "sources": [...]}   (once, first)
       event: token   data: {"t": str}                                 (many)
       event: done    data: {"ttlt_ms": int}                           (once, last)
       event: error   data: {"message": str}
"""

import json
import os
import time
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer

import boto3

KB_ID = os.environ["KB_ID"]
MODEL_ID = os.environ["MODEL_ID"]
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "700"))
TOP_K = int(os.environ.get("TOP_K", "4"))
MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", "8"))
# Reasoning pin lives here (e.g. '{"reasoningConfig": {"type": "disabled"}}').
# Field name is point-in-time — verify against current Nova 2 docs.
EXTRA_FIELDS = json.loads(os.environ.get("ADDITIONAL_MODEL_FIELDS_JSON") or "{}")

agent_rt = boto3.client("bedrock-agent-runtime")
bedrock_rt = boto3.client("bedrock-runtime")

SYSTEM_PROMPT = """\
You are a fast, precise study assistant for the AWS Certified Generative AI
Developer - Professional (AIP-C01) exam. Answer ONLY from the numbered context
passages provided; they come from the student's audited study guides. Rules:
- Be concise: direct answer first, then at most 3 short supporting sentences.
- Cite passages inline like [1] or [2] wherever you use them.
- If the passages don't cover the question, say exactly that and suggest which
  guide/domain likely covers it. Never fill gaps from general knowledge.
- Anything a passage marks (point-in-time): note it may have drifted.
"""


def retrieve(query: str):
    t0 = time.monotonic()
    resp = agent_rt.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": query[:900]},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": TOP_K}},
    )
    ms = int((time.monotonic() - t0) * 1000)
    passages, sources = [], []
    for i, r in enumerate(resp.get("retrievalResults", []), 1):
        text = r.get("content", {}).get("text", "")
        meta = r.get("metadata", {}) or {}
        crumb = meta.get("breadcrumb") or meta.get("source_file") or "study guides"
        passages.append(f"[{i}] ({crumb})\n{text}")
        sources.append({"n": i, "breadcrumb": str(crumb), "score": round(r.get("score", 0), 3)})
    return "\n\n".join(passages), sources, ms


def build_messages(history, message, context_block):
    msgs = []
    for turn in history[-MAX_HISTORY_TURNS:]:
        role = "assistant" if turn.get("role") == "assistant" else "user"
        text = str(turn.get("text", ""))[:4000]
        if text:
            msgs.append({"role": role, "content": [{"text": text}]})
    user_text = f"CONTEXT PASSAGES:\n{context_block}\n\nQUESTION: {message}"
    msgs.append({"role": "user", "content": [{"text": user_text}]})
    return msgs


class Handler(BaseHTTPRequestHandler):
    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):  # keep CloudWatch logs terse
        pass

    def _sse(self, event: str, data: dict):
        payload = f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n"
        self.wfile.write(payload.encode("utf-8"))
        self.wfile.flush()

    def do_GET(self):
        if self.path == "/healthz":
            body = b"ok"
            self.send_response(200)
            self.send_header("Content-Length", str(len(body)))
            self.end_headers()
            self.wfile.write(body)
        else:
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()

    def do_POST(self):
        if self.path != "/chat":
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        t_start = time.monotonic()
        try:
            length = int(self.headers.get("Content-Length", "0"))
            body = json.loads(self.rfile.read(length) or b"{}")
            message = str(body.get("message", "")).strip()
            history = body.get("history") or []
            if not message:
                raise ValueError("empty message")
        except (ValueError, json.JSONDecodeError) as exc:
            err = json.dumps({"message": f"bad request: {exc}"}).encode()
            self.send_response(400)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(err)))
            self.end_headers()
            self.wfile.write(err)
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/event-stream; charset=utf-8")
        self.send_header("Cache-Control", "no-cache")
        self.send_header("X-Accel-Buffering", "no")
        # Streaming body has no Content-Length; close the connection to mark
        # end-of-stream (otherwise HTTP/1.1 keep-alive leaves clients hanging).
        self.send_header("Connection", "close")
        self.end_headers()
        self.close_connection = True

        try:
            context_block, sources, retrieval_ms = retrieve(message)
            self._sse("meta", {"retrieval_ms": retrieval_ms, "sources": sources})

            kwargs = dict(
                modelId=MODEL_ID,
                system=[{"text": SYSTEM_PROMPT}],
                messages=build_messages(history, message, context_block),
                inferenceConfig={"maxTokens": MAX_TOKENS, "temperature": 0.4, "topP": 0.9},
            )
            if EXTRA_FIELDS:
                kwargs["additionalModelRequestFields"] = EXTRA_FIELDS

            stream = bedrock_rt.converse_stream(**kwargs)
            for event in stream["stream"]:
                delta = event.get("contentBlockDelta", {}).get("delta", {})
                if "text" in delta:
                    self._sse("token", {"t": delta["text"]})
                if "messageStop" in event:
                    break
            self._sse("done", {"ttlt_ms": int((time.monotonic() - t_start) * 1000)})
        except Exception as exc:  # surface to the client, don't die silently
            self._sse("error", {"message": str(exc)[:300]})


def main():
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
