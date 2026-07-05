"""Shared functional core for every chat shell (website backend, Telegram bot).

Pure functions only — no boto3, no env, no I/O — so both Lambdas can bundle
this file and the unit tests can exercise it directly.
"""


def format_passages(retrieval_results: list[dict]) -> tuple[str, list[dict]]:
    """Turn KB retrieval results into a numbered context block and source list.

    Args:
        retrieval_results: ``retrievalResults`` items from a Retrieve response.

    Returns:
        ``(context_block, sources)`` — the block interleaves ``[n]`` markers and
        breadcrumbs for citation; sources carry n/breadcrumb/score for display.
    """
    passages, sources = [], []
    for i, r in enumerate(retrieval_results, 1):
        text = r.get("content", {}).get("text", "")
        meta = r.get("metadata", {}) or {}
        crumb = meta.get("breadcrumb") or meta.get("source_file") or "study guides"
        passages.append(f"[{i}] ({crumb})\n{text}")
        sources.append({"n": i, "breadcrumb": str(crumb), "score": round(r.get("score", 0), 3)})
    return "\n\n".join(passages), sources


def build_messages(
    history: list[dict], message: str, context_block: str, max_turns: int = 8
) -> list[dict]:
    """Assemble Converse messages from trimmed history plus the grounded turn.

    Args:
        history: Prior turns as role/text dicts (client-supplied, untrusted).
        message: The user's current question.
        context_block: Numbered passages from ``format_passages``.
        max_turns: History turns to keep (oldest dropped first).

    Returns:
        Converse-shaped message list ending with the context-injected user turn.
    """
    msgs = []
    for turn in history[-max_turns:]:
        role = "assistant" if turn.get("role") == "assistant" else "user"
        text = str(turn.get("text", ""))[:4000]
        if text:
            msgs.append({"role": role, "content": [{"text": text}]})
    user_text = f"CONTEXT PASSAGES:\n{context_block}\n\nQUESTION: {message}"
    msgs.append({"role": "user", "content": [{"text": user_text}]})
    return msgs
