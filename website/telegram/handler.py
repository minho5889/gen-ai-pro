"""Telegram bot shell: study chat + mock-exam drills on the phone.

See website/TELEGRAM-SPEC.md. Zero pip dependencies; packaged by
``make telegram-package`` together with the shared ``core.py`` and the
``bank.json`` question bank built from the mock exams.

Architecture: functional core / imperative shell. Pure functions (update
parsing, callback codec, keyboards, scoring, chunking) are unit-tested in
``tests/test_telegram_core.py``; the shell owns SSM, the Telegram API, and
Bedrock.
"""

import hmac
import json
import os
import random
import re
import time
import urllib.request
from pathlib import Path

import boto3
import core

TELEGRAM_LIMIT = 4096
CB_PREFIX = "d"  # drill callback namespace

SYSTEM_PROMPT = """\
You are a fast, precise study assistant for the AWS Certified Generative AI
Developer - Professional (AIP-C01) exam, chatting via Telegram. Answer ONLY
from the numbered context passages provided. Be concise (this is a phone):
direct answer first, at most 3 short supporting sentences, cite like [1].
If the passages don't cover it, say so and name the likely guide/domain.
Anything marked (point-in-time) may have drifted — say so.
"""

# --------------------------- functional core ---------------------------------


def parse_update(update: dict) -> dict | None:
    """Classify a Telegram update into the one interaction we handle.

    Args:
        update: Raw update object from the webhook body.

    Returns:
        ``{"kind": "message", "chat_id", "text"}`` or
        ``{"kind": "callback", "chat_id", "message_id", "data", "callback_id"}``,
        or None for update types the bot ignores.
    """
    if "message" in update and "text" in update.get("message", {}):
        m = update["message"]
        return {"kind": "message", "chat_id": m["chat"]["id"], "text": m["text"].strip()}
    if "callback_query" in update:
        cq = update["callback_query"]
        msg = cq.get("message") or {}
        return {
            "kind": "callback",
            "chat_id": (msg.get("chat") or {}).get("id"),
            "message_id": msg.get("message_id"),
            "data": cq.get("data", ""),
            "callback_id": cq.get("id"),
        }
    return None


def encode_cb(exam: str, qnum: int, picks: str, action: str) -> str:
    """Encode drill state into callback_data (Telegram caps it at 64 bytes).

    Args:
        exam: Exam number ("1"/"2").
        qnum: Question number.
        picks: Accumulated letters so far (e.g. "AB").
        action: A letter to toggle, or "go" to submit.

    Returns:
        Compact ``d|exam|qnum|picks|action`` string.
    """
    return f"{CB_PREFIX}|{exam}|{qnum}|{picks}|{action}"


def decode_cb(data: str) -> dict | None:
    """Decode drill callback_data.

    Args:
        data: The callback_data string from a button tap.

    Returns:
        ``{"exam", "qnum", "picks", "action"}`` or None if it isn't ours.
    """
    parts = data.split("|")
    if len(parts) != 5 or parts[0] != CB_PREFIX or not parts[2].isdigit():
        return None
    return {"exam": parts[1], "qnum": int(parts[2]), "picks": parts[3], "action": parts[4]}


def toggle(picks: str, letter: str) -> str:
    """Toggle one letter in the accumulated picks, keeping A-F order.

    Args:
        picks: Current picks (e.g. "AC").
        letter: Letter tapped.

    Returns:
        Updated picks string.
    """
    s = set(picks) ^ {letter}
    return "".join(c for c in "ABCDEF" if c in s)


def drill_keyboard(q: dict, picks: str) -> dict:
    """Build the inline keyboard for a drill question.

    Single-select questions score on first tap; multi-select shows toggles
    (✓ on picked letters) plus a Submit row.

    Args:
        q: Bank entry with ``exam``, ``num``, ``letters``, ``multi``.
        picks: Accumulated picks (multi-select only).

    Returns:
        Telegram ``reply_markup`` dict.
    """
    exam, qnum = str(q["exam"]), q["num"]
    if not q["multi"]:
        row = [
            {"text": letter, "callback_data": encode_cb(exam, qnum, "", letter)}
            for letter in q["letters"]
        ]
        return {"inline_keyboard": [row]}
    row = [
        {
            "text": (f"✓{letter}" if letter in picks else letter),
            "callback_data": encode_cb(exam, qnum, picks, letter),
        }
        for letter in q["letters"]
    ]
    submit = [
        {"text": f"Submit ({picks or '—'})", "callback_data": encode_cb(exam, qnum, picks, "go")}
    ]
    return {"inline_keyboard": [row, submit]}


def score(picks: str, key: str) -> bool:
    """All-or-nothing scoring, like the real exam.

    Args:
        picks: Letters the student chose.
        key: Credited letters (sorted string, e.g. "ACE").

    Returns:
        True only when the sets match exactly.
    """
    return set(picks) == set(key)


def split_message(text: str, limit: int = TELEGRAM_LIMIT) -> list[str]:
    """Split text into Telegram-sized pieces at paragraph/line boundaries.

    Args:
        text: Message text of any length.
        limit: Max characters per piece.

    Returns:
        Non-empty pieces, each within the limit.
    """
    if len(text) <= limit:
        return [text] if text else []
    pieces, cur = [], ""
    for para in text.split("\n"):
        while len(para) > limit:  # pathological single line
            pieces.append(para[:limit])
            para = para[limit:]
        if len(cur) + len(para) + 1 > limit:
            pieces.append(cur)
            cur = para
        else:
            cur = f"{cur}\n{para}" if cur else para
    if cur:
        pieces.append(cur)
    return pieces


def format_drill(q: dict) -> str:
    """Render a drill question for the phone.

    Args:
        q: Bank entry.

    Returns:
        Question header + stem/options text, trimmed to one message.
    """
    sel = f"  [Select {q['multi']}]" if q["multi"] else ""
    head = f"🎯 Exam {q['exam']} Q{q['num']}{sel}\n\n"
    return split_message(head + q["text"])[0]


def format_result(q: dict, picks: str, correct: bool) -> str:
    """Render the scoring verdict plus the audited explanation.

    Args:
        q: Bank entry (carries the analysis block).
        picks: What the student chose.
        correct: Scoring outcome.

    Returns:
        Verdict line + credited answer + trimmed explanation.
    """
    verdict = "✅ Correct." if correct else f"❌ Not quite — you picked {picks or 'nothing'}."
    body = f"{verdict}\nCredited: {', '.join(sorted(q['key']))}\n\n{q['analysis']}"
    return split_message(body)[0]


def pick_question(bank: list[dict], domain: int | None, rng=random) -> dict | None:
    """Choose a random question, optionally domain-filtered.

    Args:
        bank: Loaded bank.json entries.
        domain: 1-5 to filter, or None for all.
        rng: Random source (injectable for tests).

    Returns:
        A bank entry, or None if the filter matches nothing.
    """
    pool = [q for q in bank if domain is None or q["domain"] == domain] if bank else []
    return rng.choice(pool) if pool else None


def parse_drill_command(text: str) -> tuple[bool, int | None]:
    """Parse "/drill" with an optional domain argument.

    Args:
        text: The incoming message text.

    Returns:
        ``(is_drill, domain)`` — domain None when unspecified or invalid.
    """
    m = re.match(r"^/drill(?:@\w+)?(?:\s+(\d))?\s*$", text)
    if not m:
        return False, None
    d = int(m.group(1)) if m.group(1) else None
    return True, d if d in {1, 2, 3, 4, 5} else None


# --------------------------- imperative shell ---------------------------------

KB_ID = os.environ.get("KB_ID", "")
MODEL_ID = os.environ.get("MODEL_ID", "")
OWNER_CHAT_ID = os.environ.get("OWNER_CHAT_ID", "")
PARAM_NAME = os.environ.get("TELEGRAM_PARAM", "/aip-study/telegram")
MAX_TOKENS = int(os.environ.get("MAX_TOKENS", "600"))
TOP_K = int(os.environ.get("TOP_K", "4"))
EXTRA_FIELDS = json.loads(os.environ.get("ADDITIONAL_MODEL_FIELDS_JSON") or "{}")
EDIT_INTERVAL_S = 1.2

_creds: dict | None = None
_bank: list[dict] | None = None


def creds() -> dict:
    """Fetch and cache the bot token + webhook secret from SSM."""
    global _creds
    if _creds is None:
        ssm = boto3.client("ssm")
        raw = ssm.get_parameter(Name=PARAM_NAME, WithDecryption=True)["Parameter"]["Value"]
        _creds = json.loads(raw)
    return _creds


def bank() -> list[dict]:
    """Load and cache the bundled question bank."""
    global _bank
    if _bank is None:
        _bank = json.loads((Path(__file__).parent / "bank.json").read_text(encoding="utf-8"))
    return _bank


def tg(method: str, payload: dict) -> dict:
    """Call one Telegram Bot API method.

    Args:
        method: API method name (sendMessage, editMessageText, ...).
        payload: JSON payload.

    Returns:
        Decoded API response.
    """
    req = urllib.request.Request(
        f"https://api.telegram.org/bot{creds()['token']}/{method}",
        data=json.dumps(payload).encode(),
        headers={"Content-Type": "application/json"},
    )
    with urllib.request.urlopen(req, timeout=20) as r:
        return json.loads(r.read())


def answer_chat(chat_id: int, text: str) -> None:
    """RAG-answer a free-text question with pseudo-streamed edits."""
    placeholder = tg("sendMessage", {"chat_id": chat_id, "text": "…"})
    message_id = placeholder["result"]["message_id"]

    agent_rt = boto3.client("bedrock-agent-runtime")
    bedrock_rt = boto3.client("bedrock-runtime")
    resp = agent_rt.retrieve(
        knowledgeBaseId=KB_ID,
        retrievalQuery={"text": text[:900]},
        retrievalConfiguration={"vectorSearchConfiguration": {"numberOfResults": TOP_K}},
    )
    context_block, sources = core.format_passages(resp.get("retrievalResults", []))

    kwargs = {
        "modelId": MODEL_ID,
        "system": [{"text": SYSTEM_PROMPT}],
        "messages": core.build_messages([], text, context_block),
        "inferenceConfig": {"maxTokens": MAX_TOKENS, "temperature": 0.4, "topP": 0.9},
    }
    if EXTRA_FIELDS:
        kwargs["additionalModelRequestFields"] = EXTRA_FIELDS

    acc, last_edit = "", 0.0
    for event in bedrock_rt.converse_stream(**kwargs)["stream"]:
        delta = event.get("contentBlockDelta", {}).get("delta", {})
        if "text" in delta:
            acc += delta["text"]
            now = time.monotonic()
            if now - last_edit >= EDIT_INTERVAL_S and acc.strip():
                tg(
                    "editMessageText",
                    {"chat_id": chat_id, "message_id": message_id, "text": split_message(acc)[0]},
                )
                last_edit = now
        if "messageStop" in event:
            break

    cites = "\n".join(f"[{s['n']}] {s['breadcrumb']}" for s in sources)
    final = f"{acc.strip() or '(no answer)'}\n\n—\n{cites}"
    pieces = split_message(final)
    tg("editMessageText", {"chat_id": chat_id, "message_id": message_id, "text": pieces[0]})
    for extra in pieces[1:]:
        tg("sendMessage", {"chat_id": chat_id, "text": extra})


def handle_message(chat_id: int, text: str) -> None:
    """Route one text message: commands or free chat."""
    if text.startswith("/start") or text.startswith("/help"):
        tg(
            "sendMessage",
            {
                "chat_id": chat_id,
                "text": (
                    "AIP-C01 study bot.\n"
                    "• Ask anything — answered from your audited guides with citations.\n"
                    "• /drill — random mock-exam question, tap to answer.\n"
                    "• /drill 3 — restrict to domain 3."
                ),
            },
        )
        return
    is_drill, domain = parse_drill_command(text)
    if is_drill:
        q = pick_question(bank(), domain)
        if q is None:
            tg("sendMessage", {"chat_id": chat_id, "text": "No questions match that filter."})
            return
        tg(
            "sendMessage",
            {"chat_id": chat_id, "text": format_drill(q), "reply_markup": drill_keyboard(q, "")},
        )
        return
    answer_chat(chat_id, text)


def handle_callback(cb: dict) -> None:
    """Route one button tap: toggle picks or score."""
    state = decode_cb(cb["data"])
    tg("answerCallbackQuery", {"callback_query_id": cb["callback_id"]})
    if state is None:
        return
    q = next(
        (e for e in bank() if str(e["exam"]) == state["exam"] and e["num"] == state["qnum"]),
        None,
    )
    if q is None:
        return
    if q["multi"] and state["action"] != "go":
        picks = toggle(state["picks"], state["action"])
        tg(
            "editMessageReplyMarkup",
            {
                "chat_id": cb["chat_id"],
                "message_id": cb["message_id"],
                "reply_markup": drill_keyboard(q, picks),
            },
        )
        return
    picks = state["picks"] if q["multi"] else state["action"]
    correct = score(picks, q["key"])
    tg(
        "editMessageReplyMarkup",
        {
            "chat_id": cb["chat_id"],
            "message_id": cb["message_id"],
            "reply_markup": {"inline_keyboard": []},
        },
    )
    tg("sendMessage", {"chat_id": cb["chat_id"], "text": format_result(q, picks, correct)})


def lambda_handler(event: dict, context) -> dict:
    """Webhook entrypoint: authenticate, bind owner, dispatch.

    Args:
        event: Function URL event.
        context: Lambda context (unused).

    Returns:
        HTTP response dict (always 200 once authenticated, so Telegram
        doesn't re-deliver on handled updates).
    """
    headers = {k.lower(): v for k, v in (event.get("headers") or {}).items()}
    given = headers.get("x-telegram-bot-api-secret-token", "")
    if not hmac.compare_digest(given, creds().get("secret", "")):
        return {"statusCode": 403, "body": "forbidden"}

    update = json.loads(event.get("body") or "{}")
    parsed = parse_update(update)
    if parsed is None or parsed.get("chat_id") is None:
        return {"statusCode": 200, "body": "ignored"}

    if str(parsed["chat_id"]) != OWNER_CHAT_ID:
        if parsed["kind"] == "message" and parsed["text"].startswith("/start"):
            tg(
                "sendMessage",
                {
                    "chat_id": parsed["chat_id"],
                    "text": (
                        f"Your chat id is {parsed['chat_id']}. Set "
                        "telegram_owner_chat_id in Terraform and redeploy to bind this bot."
                    ),
                },
            )
        return {"statusCode": 200, "body": "unbound"}

    try:
        if parsed["kind"] == "message":
            handle_message(parsed["chat_id"], parsed["text"])
        else:
            handle_callback(parsed)
    except Exception as exc:  # tell the phone, don't die silently
        tg("sendMessage", {"chat_id": parsed["chat_id"], "text": f"⚠️ {str(exc)[:300]}"})
    return {"statusCode": 200, "body": "ok"}
