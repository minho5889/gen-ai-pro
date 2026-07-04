# Feasibility — Interactive Study Website with a Nova 2 Lite Chatbot

**Verdict: feasible, and cheaper than expected — with one architecture correction and one latency
caveat.** Build the site with RAG grounding first; fine-tune for *behavior* (not knowledge) second.
"Lightning fast" is achievable, but only if reasoning mode is kept off/minimal and responses stream.

Facts below verified 2026-07-06 (all 🕐 point-in-time — re-verify before committing budget):

| # | Fact | Why it matters |
|---|---|---|
| 1 | Nova 2 Lite supports both **SFT and reinforcement fine-tuning (RFT)** on Bedrock | The fine-tune plan is real, two ways: labeled examples (SFT) or graded feedback (RFT; AWS reports ~66% average accuracy gain over base on targeted tasks) |
| 2 | Customized Nova models deploy to **on-demand inference at the same per-token price as the base model** (PEFT-trained models are compatible with both on-demand and PT) | The usual fine-tune killer — hourly Provisioned Throughput — does not apply. A personal-scale site can serve a custom model for pennies |
| 3 | Nova 2 Lite ≈ **$0.30 / M input, $2.50 / M output** (third-party trackers; confirm on the official pricing page) | A 2k-token-in / 300-token-out chat turn ≈ **$0.0014**. 1,000 turns/month ≈ $1.40 |
| 4 | Nova 2 Lite is a **reasoning-capable** model; benchmark TTFT at *medium reasoning* is ~19 s, while default behavior targets "short internal deliberations… latencies appropriate for interactive applications" | "Lightning fast" and "deep reasoning" are opposite ends of one dial. The chatbot must pin reasoning to off/minimal and stream tokens |
| 5 | 1M-token context in production | Whole cram sheets fit in-context; full guides still shouldn't (cost/latency) — retrieval stays worthwhile |

## The architecture correction: RAG first, fine-tune second

This repo's own doctrine (strategy doc §6, taught by guide 01) applies to itself: **fine-tuning bakes
in tone, format, and behavior — not reliable, updatable facts.** The chatbot's facts are this repo's
audited guides, which still change (see VERIFICATION-LOG). Baking them into weights means retraining
on every content fix and risking confident-stale answers — the exact failure mode the July audit
existed to catch.

So: ground the bot with **RAG over `guides/` + `_cram/`** (they're already section-structured for
chunking), and fine-tune only for what fine-tuning is for — the Socratic/verifier *persona*: short
turns, question-first behavior, citation format, refusal to answer beyond sources. The two study
agents in [`agents/`](../agents/README.md) are the behavioral spec, and their session transcripts
are a natural SFT dataset; the verifier's deterministic scoring could even serve as an RFT grader.

## Reference architecture (lightning-fast path)

```
CloudFront + S3 (or Amplify Hosting)          — static chat UI, global edge
        │  fetch (streaming)
Lambda Function URL, response streaming        — thin token relay, no buffering
        │  ConverseStream
Amazon Bedrock: Nova 2 Lite (reasoning off/minimal)
        ├── Bedrock Knowledge Base — guides/ + _cram/ in S3
        │     vector store: S3 Vectors (cheapest; semantic-only is fine here)
        └── (Phase 3) custom Nova 2 Lite via on-demand custom model deployment
```

Latency budget for perceived "lightning fast": TTFT ≤ ~800 ms. Levers, in order: reasoning
off/minimal (biggest), streaming from the first token (perception), retrieval kept lean (top 3–4
chunks, section-sized), system prompt + persona under prompt caching if available for Nova 2
(verify), Region close to you, no cold-start-prone layers in the Lambda.

## Cost sketch (personal use, monthly)

| Item | Est. |
|---|---|
| Inference, ~1,500 chat turns | ~$2–4 |
| KB storage (S3 Vectors, ~6 MB corpus) + queries | < $1 |
| Hosting (S3+CloudFront or Amplify free tier) | ~$0–1 |
| Lambda + misc | < $1 |
| One-time: SFT job on a small persona dataset | ~tens of $ (verify per-token training price) |
| **Steady state** | **≈ $5/month** |

The fact that makes this work: on-demand custom model deployment at base-model token pricing —
without it (i.e., if serving required Provisioned Throughput), a fine-tuned hobby site would cost
hundreds/month and the recommendation would flip to "don't fine-tune at all."

## Risks / open questions

1. **Reasoning-latency trap** — if the bot is allowed to "think," TTFT explodes (fact 4). Pin the
   config; test TTFT in CI-ish smoke checks.
2. **Fine-tune quality bar** — persona SFT needs a few hundred good examples; garbage transcripts in,
   garbage persona out. Generate + curate from the agents' sessions.
3. **Point-in-time drift** — pricing, RFT availability, prompt-caching support for Nova 2: re-verify
   at build time (this doc's table is dated).
4. **Custom-model deployment regions/limits** — confirm your Region supports on-demand custom
   deployment for Nova 2 Lite before training.
5. **The verifier stays local/deterministic** — the website chatbot should *tutor*; letter-scored
   drilling should keep its deterministic scorer (port `verifier.py`'s logic to the backend, don't
   let the LLM grade).

## Phased plan

1. **Phase 1 — site + grounded chat (a weekend):** static chat UI, Lambda streaming relay, base Nova
   2 Lite + Knowledge Base over the repo. Measure TTFT. No fine-tuning.
2. **Phase 2 — persona dataset:** collect/curate tutor+verifier transcripts into SFT format; define
   an eval set (the guides' Knowledge Checks) to detect regression.
3. **Phase 3 — fine-tune + swap:** SFT (or RFT with the verifier-as-grader), deploy via on-demand
   custom model deployment, A/B against Phase 1 on the eval set; keep whichever wins.
