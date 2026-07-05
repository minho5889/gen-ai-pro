"""Streaming chat relay: Knowledge Base retrieval -> Nova 2 Lite -> SSE.

Runs as a plain stdlib HTTP server behind the AWS Lambda Web Adapter layer,
which is what gives a Python Lambda true response streaming (natively a
Node-only feature). Zero pip dependencies — boto3 ships in the runtime.

Architecture: functional core / imperative shell. The core (``parse_chat_request``
through ``build_converse_kwargs``) is pure and unit-tested in
``tests/test_app_core.py``; the ``Handler`` shell owns sockets and boto3 calls,
and is covered end-to-end by ``test_smoke.py``.

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
import core
from core import format_passages  # noqa: F401 — re-exported for shells/tests

KB_ID = os.environ["KB_ID"]
MODEL_ID = os.environ["MODEL_ID"]
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "700"))
TOP_K = int(os.environ.get("TOP_K", "4"))
MAX_HISTORY_TURNS = int(os.environ.get("MAX_HISTORY_TURNS", "8"))
# Reasoning pin lives here (e.g. '{"reasoningConfig": {"type": "disabled"}}').
# Field name is point-in-time — verify against current Nova 2 docs.
EXTRA_FIELDS = json.loads(os.environ.get("ADDITIONAL_MODEL_FIELDS_JSON") or "{}")

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

# --------------------------- functional core ---------------------------------


def parse_chat_request(raw: bytes) -> tuple[str, list[dict]]:
    """Validate and unpack a /chat request body.

    Args:
        raw: Request body bytes.

    Returns:
        ``(message, history)`` where history is a list of role/text dicts.

    Raises:
        ValueError: On malformed JSON or an empty message.
    """
    try:
        body = json.loads(raw or b"{}")
    except json.JSONDecodeError as exc:
        raise ValueError(f"invalid JSON: {exc}") from exc
    message = str(body.get("message", "")).strip()
    if not message:
        raise ValueError("empty message")
    history = body.get("history") or []
    return message, history


def build_messages(history: list[dict], message: str, context_block: str) -> list[dict]:
    """Assemble Converse messages with this service's history-trim setting.

    Args:
        history: Prior turns as role/text dicts (client-supplied, untrusted).
        message: The user's current question.
        context_block: Numbered passages from ``core.format_passages``.

    Returns:
        Converse-shaped message list ending with the context-injected user turn.
    """
    return core.build_messages(history, message, context_block, MAX_HISTORY_TURNS)


def build_converse_kwargs(messages: list[dict]) -> dict:
    """Build the converse_stream call arguments.

    Args:
        messages: Output of ``build_messages``.

    Returns:
        Keyword arguments for ``bedrock-runtime.converse_stream``, including the
        reasoning-pin passthrough when configured.
    """
    kwargs = {
        "modelId": MODEL_ID,
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": messages,
        "inferenceConfig": {"maxTokens": MAX_TOKENS, "temperature": 0.4, "topP": 0.9},
    }
    if EXTRA_FIELDS:
        kwargs["additionalModelRequestFields"] = EXTRA_FIELDS
    return kwargs


def sse_frame(event: str, data: dict) -> bytes:
    """Encode one server-sent event.

    Args:
        event: Event name (meta/token/done/error).
        data: JSON-serializable payload.

    Returns:
        The wire bytes for the frame, including the blank-line terminator.
    """
    return f"event: {event}\ndata: {json.dumps(data, ensure_ascii=False)}\n\n".encode()


# --------------------------- imperative shell --------------------------------

agent_rt = boto3.client("bedrock-agent-runtime")
bedrock_rt = boto3.client("bedrock-runtime")


def retrieve(query: str) -> tuple[str, list[dict], int]:
    """Query the Knowledge Base and format the results.

    Args:
        query: The user's question (truncated to the Retrieve limit).

    Returns:
        ``(context_block, sources, retrieval_ms)``.
    """
    t0 = time.monotonic()
    resp = agent_rt.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": query[:900]},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": TOP_K}},
    )
    ms = int((time.monotonic() - t0) * 1000)
    context_block, sources = format_passages(resp.get("retrievalResults", []))
    return context_block, sources, ms


class Handler(BaseHTTPRequestHandler):
    """HTTP shell: routes, headers, and the streaming loop. Logic lives in the core."""

    protocol_version = "HTTP/1.1"

    def log_message(self, fmt, *args):
        """Keep CloudWatch logs terse (adapter logs requests already)."""

    def _sse(self, event: str, data: dict) -> None:
        """Write one SSE frame to the client and flush."""
        self.wfile.write(sse_frame(event, data))
        self.wfile.flush()

    def do_GET(self):
        """Serve /healthz; 404 anything else."""
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
        """Serve /chat: retrieve, stream model tokens as SSE, then close."""
        if self.path != "/chat":
            self.send_response(404)
            self.send_header("Content-Length", "0")
            self.end_headers()
            return
        t_start = time.monotonic()
        try:
            length = int(self.headers.get("Content-Length", "0"))
            message, history = parse_chat_request(self.rfile.read(length))
        except ValueError as exc:
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

            stream = bedrock_rt.converse_stream(
                **build_converse_kwargs(build_messages(history, message, context_block))
            )
            for event in stream["stream"]:
                delta = event.get("contentBlockDelta", {}).get("delta", {})
                if "text" in delta:
                    self._sse("token", {"t": delta["text"]})
                if "messageStop" in event:
                    break
            self._sse("done", {"ttlt_ms": int((time.monotonic() - t_start) * 1000)})
        except Exception as exc:  # surface to the client, don't die silently
            self._sse("error", {"message": str(exc)[:300]})


def main() -> None:
    """Serve forever on ``$PORT`` (the Lambda Web Adapter's upstream)."""
    port = int(os.environ.get("PORT", "8080"))
    ThreadingHTTPServer(("0.0.0.0", port), Handler).serve_forever()


if __name__ == "__main__":
    main()
