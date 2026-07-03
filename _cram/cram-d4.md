# Cram D4 — Operational Efficiency & Optimization (12%)

**Frame:** For a Bedrock FM workload, cost = token volume × per-token rate, and latency = TTFT (perceived) + decode (total). You never scale an instance — you pull token/billing/model/serving levers. Owns exam **Pattern 4** ("Optimize cost/latency for an FM workload").

- **4.1 Cost optimization** — token economics, efficiency, caching, model tiering, inference/throughput options.
- **4.2 Performance** — perceived vs total latency, streaming, concurrency, params, retrieval tuning.
- **4.3 Monitoring** — `AWS/Bedrock` metrics, logging, dashboards/alarms, anomaly detection, drift re-runs.

---

## Mental models / decision triggers

- **Cost Lever Priority (in order, ascending commitment):** 1) token efficiency → 2) caching → 3) model tiering/cascading → 4) Provisioned Throughput/batch. Earlier lever wins unless scenario rules it out.
- **Cost trigger:** content repeats? → caching. Else → token efficiency first → cheaper model clears bar? → if no, volume shape decides PT/batch/on-demand.
- **Volume shape → billing mode:** steady-high-real-time → Provisioned Throughput. large-bounded-offline → batch. spiky/low/unpredictable → on-demand. custom (fine-tuned) model → PT (required).
- **Latency trigger — "which clock?":** blank screen / first token → streaming. whole-response too slow → `maxTokens` + faster/latency-optimized model. can't process enough → concurrency within quotas.
- **Tiering vs cascading:** tiering = decide UP FRONT by *predicted* difficulty, run ONE model. cascading = try cheap first, escalate by *measured* quality, may run TWO (adds latency).
- **Prompt vs semantic cache:** prompt = cheapens an invocation that STILL happens (prefix reuse). semantic = makes the invocation DISAPPEAR (stored answer on a hit).
- **Quality bar gate (GENCOST01):** start from smallest/cheapest model, scale UP only to an "acceptable" model. A downgrade is only a saving if it still clears the task's quality acceptance criteria.
- **Token-efficiency ceiling:** reduce tokens only while quality ≥ bar; a drop below the bar is the stop signal, not an acceptable trade.

---

## If the exam says X → answer Y → why

| Exam says | Answer | Why |
|---|---|---|
| FM workload expensive/slow → "bigger instance / autoscale / reserve GPU" | **Distractor (Pattern 4 trap)** | On-demand Bedrock is serverless — no instance to scale; lever is tokens or billing mode |
| "Where do I start to cut FM cost?" | **Token efficiency (lever 1)** | Free, reversible, every call, compounds with later levers |
| Long/verbose responses drive cost | **Concise instruction + `maxTokens`** | Output tokens priced higher than input (autoregressive); output is costliest dimension |
| Unit of cost for a Bedrock call | **Input tokens + output tokens** | Not requests, not compute hours, not instance size |
| Same system prompt / document re-sent every call | **Bedrock prompt caching** | Stateless service re-bills prefix each call; caching skips reprocess (latency) + full re-bill (cost); model still runs |
| Same questions, different words — avoid calling model | **Semantic caching** | Embedding-similarity match returns stored answer; no invocation on hit |
| "Turn on caching" for stream of unique prompts | **Distractor** | Caching needs repetition; nothing repeats → never hits |
| Which caching skips the call vs cheapens it | **Semantic = disappears; prompt = cheaper** | Different intervention points |
| Semantic cache returns confidently-wrong answer | **Raise similarity threshold (+ shorter TTL)** | Lower threshold = higher hit rate but more non-equivalent answers |
| Multi-turn cost grows; must keep older-turn continuity | **Summarize history** | Preserves detail/coherence; truncation drops oldest outright |
| Multi-turn cost grows; cheapest bound, detail not critical | **Truncate to recent-message window** | Adds no processing; just drops oldest |
| Route easy→cheap, hard→flagship, decided up front | **Model tiering** | One model per request by predicted difficulty |
| Try cheap first, escalate only if not good enough | **Model cascading** (risk = added latency) | Conditional 2nd call; escalation pays both models in sequence |
| Managed routing to cheapest capable model *within one family* | **Intelligent Prompt Routing** | Predicts per-request quality, routes within family behind one endpoint |
| Make same model respond faster, no model change | **Latency-optimized inference** | `performanceConfig.latency=optimized`; serving-path config, same outputs |
| Swap to cheaper model, quality unverified | **Distractor unless it clears the quality bar** | GENCOST01 — downgrade only if criteria met |
| Steady high predictable real-time volume; on-demand throttles | **Provisioned Throughput** | Dedicated Model Units guarantee throughput; hourly cost amortizes over steady volume |
| Summarize 200k docs cheaply, no latency need | **Batch inference** | Async via S3 at documented discount; trades real-time |
| Spiky/low/unpredictable traffic | **Stay on-demand** | Pay-per-use, no idle commitment |
| Serve fine-tuned/custom model in production | **Provisioned Throughput (required)** | Custom models cannot use on-demand path |
| Bursty traffic throttles one Region, raise throughput | **Cross-Region Inference profile** | Routes across Regions on capacity checks; no extra routing cost |
| Data must stay in EU / a geography | **Geographic CRI profile (or single-Region)** | Confines processing to geography; global profile routes worldwide |
| Agent tool-calling / strict per-request JSON as a batch job | **Distractor — not batch** | Batch processes records independently; no tool calling, no structured output |
| Blank screen for seconds before output | **Response streaming** | Improves perceived latency (TTFT); does NOT change total generation time |
| Reduce *total* time to complete response | **`maxTokens` + faster/latency-opt model** (not streaming) | Total latency driven by output-token count in decode |
| "Lower temperature to go faster/cheaper" | **Distractor** | temp/top-k/top-p shape randomness only; latency/cost knob is `maxTokens` |
| RAG answers slow + prompts huge | **Reduce retrieved context** (`numberOfResults`, chunking, reranking) | More chunks → bigger prefill → higher TTFT + input cost |
| "Caching makes every request faster" | **Distractor unless content repeats** | Pre-compute/caching needs reuse |
| Alarm on a single Bedrock "error" metric | **Trap — no aggregate error metric** | Client/server errors + throttles are 3 distinct metrics; throttle ≠ invocation and ≠ error |
| Alert when token spend deviates from daily/weekly pattern | **Anomaly detection (learned baseline)** | Static line false-alarms at peak / misses trough on seasonal metric |
| Spend alerts for Anthropic Claude / Bedrock Marketplace model | **AWS Budgets (Billing-entity filter)** | Cost Anomaly Detection excludes third-party Marketplace products |
| Which team/app drives FM spend | **Cost allocation tags + Cost Explorer grouping** | Tags attribute spend (not retroactive); CE groups by tag |
| Detect quality/hallucination drift over time | **Scheduled golden-dataset re-runs (Bedrock Evaluations + scheduler)** | Recurrence is a pattern, not a one-click feature |
| Catch slow latency creep, no single incident | **Standing dashboards + sustained-period latency alarm** | Drift has no triggering event |
| Answer hinges on exact per-token dollar price | **Distractor — verify live** | Prices fast-moving; question tests that you know to look it up |

---

## Top Traps (named distractors)

- **Compute-scaling trap (THE Pattern 4 trap):** "bigger instance / autoscale / reserve GPU" — serverless, no instance; the option exists only to be rejected. Its mere presence signals Pattern 4.
- **Pricing trap:** any precise per-token dollar figure — prices are fast-moving; reason about the model, not the number.
- **Caching on non-repeating work:** "turn on caching" with unique prompts — never hits.
- **Confusing the two caches:** assuming both skip the model (only semantic does) or both just cheapen it.
- **Lowering threshold "reduces" semantic-cache risk:** it RAISES hit rate AND risk.
- **Ignoring the quality bar on a downgrade:** ships wrong answers cheaply = regression, not saving.
- **PT for spiky/low traffic; batch for real-time or tool-calling work:** idle PT meter costs more than on-demand; batch can't do real-time/tools/JSON.
- **Wrong latency lever:** streaming for *total* time (it's perceived only); temperature for speed/cost (it's randomness only).
- **Single error metric / static alarm on seasonal metric:** no aggregate error metric, throttle is its own metric; seasonal metric needs anomaly detection.
- **Cost Anomaly Detection for third-party LLM spend:** blind to Marketplace (e.g. "Anthropic, PBC") — use Budgets.
- **Global CRI profile when residency required:** it can route worldwide; use geographic profile.

---

## Hard numbers worth memorizing

- **Domain 4 weight = 12%.** Pass = 750/1000 scaled (whole exam). [stable]
- **Cost Lever Priority order:** token efficiency → caching → model tiering/cascading → PT/batch. [stable]
- **PT commitment terms:** no-commitment / 1-month / 6-month (longer = deeper discount). [stable]
- **Additive latency model:** `InvocationLatency ≈ TimeToFirstToken + (output tokens ÷ output-tokens-per-second)`. [stable]
- **AWS Budgets:** up to **5 alerts** per budget. [stable]
- **Cost Anomaly Detection:** evaluates **~3×/day** on net unblended cost, up to **~24h** detection delay; GA + free; NOT real-time. [point-in-time/verify]
- **CloudWatch anomaly detector:** up to **~2 weeks** history to train a stable band. [point-in-time/verify]
- **Output token rate:** higher than input across all families (AWS once cited **~3–5×**). Direction stable; **multiple is point-in-time / verify live.**
- **Batch discount:** announced **~50%** below on-demand. [point-in-time/verify]
- **Global CRI profile:** announced **~10%** cheaper than geographic. [point-in-time/verify]
- **Batch concurrency:** ~**10** jobs per model per Region. [point-in-time/verify]
- **Prompt-cache minimum prefix:** ~**1,024** (some Claude) / ~**4,096** tokens; ~**4** checkpoints/request; TTL ~**5 min** (some Claude opt-in ~1 hr). [point-in-time/verify]
- **Prompt caching:** AWS benchmark "up to ~85% latency / ~90% cost." Semantic: "up to ~86% cost / ~88% latency." **Best-case marketing, not guarantees.** [point-in-time/verify]
- **Semantic-cache similarity threshold:** ~**0.95** strict (medical/legal/financial) down to ~**0.75** relaxed; start ~0.90–0.95. [point-in-time guidance/verify]
- **KB `numberOfResults`:** default **5**, max **100**. [point-in-time/verify]
- **All TPM/RPM/tokens-per-day quotas and any $ figure:** per-model/Region, read live from Service Quotas / pricing page. **Never memorize.** [point-in-time]
