# Telegram Bot Spec — study assistant on the phone

One page. A Telegram bot as a **second shell over the existing functional cores**: free-chat with
the RAG assistant and mock-exam drills with tappable answer buttons, from an iPhone. Companion to
[CICD-SPEC.md](CICD-SPEC.md); decision rationale (why Telegram over Slack/Discord) is recorded in
the chat log and summarized here: pure-stdlib webhook auth, first-class bot UX (inline keyboards →
drill buttons), friendliest personal rate limits, zero workspace baggage.

## Capabilities (v1)

| Command | Behavior |
|---|---|
| any text | RAG chat: KB retrieve → Nova 2 Lite → answer with `[n]` citations; sent as one message, then progressively `editMessageText`-updated (~1s cadence) while generating |
| `/drill [domain]` | Random mock-exam question as a message with **inline keyboard** (A–F buttons). Single-select: one tap scores. Multi-select: taps toggle ✓ on the keyboard, `Submit` scores — all-or-nothing, like the real exam |
| `/start`, `/help` | Identity binding + usage |

Out of scope v1: group chats, voice, /explain free-recall mode, ops notifications (phase 2 —
SNS → this Lambda → `sendMessage`).

## Architecture

```
Telegram ──POST──> Lambda Function URL (auth NONE — see deviation) ──> handler.py
                                                        │ bank.json (bundled at package time)
                                                        ├─ core.py  (shared with website backend)
                                                        └─ Bedrock: Retrieve + ConverseStream
```

- **Second Lambda, plain handler** (no Web Adapter — Telegram gets updates via its own API calls,
  not a streamed HTTP response). Flow per update: ack-by-doing — send "…", generate, edit.
- **Shared core**: `format_passages` / `build_messages` move to `website/backend/core.py`;
  both Lambdas import it. Telegram packaging stages `.build/` (handler + core + bank) via
  `make telegram-package`; CI does the same before deploy.
- **Question bank bundled, not fetched**: `build_bank.py` re-parses the mock exams (reusing the
  verifier's parser) into `bank.json` at package time. Content edits reach the bot on the next
  deploy — same freshness model as the KB corpus.
- **Stateless drills**: `callback_data` (≤64 bytes) carries `exam:qnum:picks`; each tap re-renders
  the keyboard with the new picks. No DynamoDB. Scoring recomputes from the bundled bank.

## Security — deviation flight plan

**Deviation from the baseline** ("function URLs are IAM-auth behind CloudFront"): Telegram cannot
SigV4-sign, so this one URL is `authorization_type = NONE`. Mitigations, layered:

1. `setWebhook` registers a random `secret_token`; Telegram echoes it in
   `X-Telegram-Bot-Api-Secret-Token`; the handler constant-time-compares and drops mismatches
   before any parsing.
2. **Owner allowlist**: the bot serves exactly one chat id (`telegram_owner_chat_id` Terraform
   var). Unbound state replies to `/start` with your chat id and instructions, nothing else.
3. Bot token lives in **SSM Parameter Store (SecureString)**, created manually
   (`aws ssm put-parameter`) so it never enters Terraform state or GitHub; Lambda reads it at
   cold start with a name-scoped `ssm:GetParameter`.

Flip condition: if Telegram ever supports request signing, or the bot outgrows single-user,
revisit with API Gateway + WAF.

## Known limitations (accepted v1)

- Generation runs inside the webhook invocation (~5–15s). Telegram may re-deliver an update if
  the 200 is slow; single-user impact is a duplicate answer, not corruption. Revisit with
  self-invoke async if it annoys.
- Pseudo-streaming edits are throttled to ~1/s to respect Telegram flood limits.
- Telegram API facts (4096-char messages, 64-byte callback_data, secret_token header) are
  *(point-in-time)* — VERIFICATION-LOG row added.

## Delivery

Terraform (`telegram.tf`: Lambda, URL, IAM, deploy-role grant), `deploy-telegram.yml`
(path-filtered: `website/telegram/**`, `website/backend/core.py`), unit tests for the pure parts
(update parsing, callback encode/decode, keyboard rendering, scoring, message chunking) in
`tests/test_telegram_core.py`. Manual one-times: BotFather token → `put-parameter`;
`make telegram-webhook` registers the URL.
