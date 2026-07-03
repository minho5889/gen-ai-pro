# Domain 4 — Operational Efficiency & Optimization · NotebookLM Master Prompts

**Notebook:** D4 (12% of AIP-C01). **Upload into it:** guide 07 (Cost, Performance & Monitoring) + `cram-d4.md` + the blueprint.
**Study philosophy:** retrieve first, review second — and because NotebookLM answers ONLY from your sources and can't see live AWS docs, treat every quota/price/percentage as *verify-live* and confirm with the Claude-Code mock exams.

This domain is **Pattern 4** — "optimize cost/latency for an FM workload." You never scale an instance; you pull **token → caching → tiering/cascading → Provisioned-Throughput/batch** levers (in that order). The traps below are real and recurring; the prompts are built around them.

---

## The study loop (sequenced)

### Block 1 — Socratic tutor (the centerpiece)
**Feature + path:** Chat → Configure Chat → Style: **Custom** (paste below). Set Length: Default. Keep all 3 sources toggled ON.
**When:** Daily driver. Use after a first read; this is where the learning happens.

```
You are my Socratic exam tutor for AWS AIP-C01 Domain 4 (Operational Efficiency & Optimization). Use ONLY the uploaded sources. Drill me one scenario at a time. NEVER reveal the answer until I have committed to a choice AND justified it in one sentence.

Loop each round:
1. Pose ONE realistic, scenario-style question (design/decision, not trivia) on a Domain 4 topic. Prefer the high-yield traps below.
2. Wait for my answer + my justification.
3. Then: say correct/incorrect, give the right answer with a clickable citation to the source, and — critically — explain why EACH plausible distractor is wrong, not just why mine was.
4. Ask me a "why not the other lever?" follow-up to force elaboration.

Rotate through these Domain 4 traps so I see all of them:
- The Pattern-4 compute trap: "bigger instance / autoscale / reserve GPU" is ALWAYS a distractor — on-demand Bedrock is serverless; the lever is tokens or billing mode.
- Cost Lever Priority order: token efficiency → caching → tiering/cascading → PT/batch; earlier lever wins unless ruled out. "Where do I start to cut cost?" → token efficiency.
- Unit of cost = input tokens + output tokens (NOT requests / compute hours / instance size); output priced higher than input.
- Prompt cache (cheapens an invocation that STILL happens, prefix reuse) vs semantic cache (makes the invocation DISAPPEAR on a stored-answer hit). Caching on non-repeating prompts never hits = distractor.
- Semantic cache returning confidently-wrong answers → RAISE the similarity threshold (+ shorter TTL); lowering threshold raises hit rate AND risk.
- Tiering (decide up front by predicted difficulty, run ONE model) vs cascading (try cheap, escalate by measured quality, may run TWO, adds latency) vs Intelligent Prompt Routing (managed, within one family).
- Quality-bar gate (GENCOST01): a downgrade is only a saving if it still clears the task's acceptance criteria.
- Volume shape → billing mode: steady-high-real-time → Provisioned Throughput; large-bounded-offline → batch; spiky/low/unpredictable → on-demand; custom/fine-tuned model → PT (required). PT for spiky traffic and batch for real-time/tool-calling/JSON are distractors.
- Latency "which clock?": blank screen / first token → streaming (perceived only, does NOT cut total time); whole response too slow → maxTokens + faster/latency-optimized model; can't process enough → concurrency within quotas. "Lower temperature to go faster/cheaper" is a distractor (temp/top-k/top-p shape randomness only).
- RAG slow + huge prompts → reduce retrieved context (numberOfResults, chunking, reranking), not caching.
- Monitoring: there is NO aggregate Bedrock "error" metric (client errors, server errors, throttles are 3 distinct metrics; throttle ≠ error). Seasonal/spiky spend → Anomaly Detection (learned baseline), not a static alarm.
- Cost Anomaly Detection is BLIND to third-party Marketplace models (e.g. Anthropic, PBC) → use AWS Budgets with a Billing-entity filter for Claude/Bedrock-Marketplace spend.
- Cross-Region Inference: global profile can route worldwide (cheaper) BUT use a geographic profile when data residency is required.
- Drift detection = scheduled golden-dataset re-runs (Bedrock Evaluations + scheduler); it's a pattern, not a one-click feature.

If a question would hinge on an exact per-token price, a TPM/RPM quota, a batch-discount %, or a similarity-threshold number, FLAG IT: tell me "this is point-in-time, verify against live AWS docs / Service Quotas" rather than asserting it as fact. State clearly that you cannot fact-check against live AWS documentation.

Start now with question 1. Ask me before moving on.
```
**Why (learning science):** active recall + elaborative interrogation — you retrieve and defend *before* seeing the answer, and "why not the distractor?" is where Pattern-4 points are won.

---

### Block 2 — Quiz generation (hardest distinctions)
**Feature + path:** Studio → Quiz → click the **pencil** to customize BEFORE generating. Difficulty: **Hard**. Number: **More**.
**When:** Day 2+, after a Socratic round, to measure retention.

```
Generate a HARD scenario-based quiz on AWS AIP-C01 Domain 4 (Operational Efficiency & Optimization) using only the uploaded sources. Make distractors the *plausible-but-wrong* options the real exam uses. Weight questions toward these distinctions:
- prompt cache (cheapens, model still runs) vs semantic cache (skips the call) — and when caching never hits (non-repeating prompts).
- model tiering vs cascading vs Intelligent Prompt Routing.
- volume shape → Provisioned Throughput vs batch vs on-demand (and the "PT for spiky / batch for real-time-or-tool-calling" traps).
- the latency "which clock?" decision: streaming (perceived) vs maxTokens + latency-optimized model (total) vs concurrency; and the temperature-for-speed trap.
- Cost Anomaly Detection vs AWS Budgets (Marketplace/third-party Claude spend), and the "no single Bedrock error metric" trap.
- the GENCOST01 quality-bar gate on any model downgrade.
Always include the compute-scaling distractor ("bigger instance / autoscale / reserve GPU") as a wrong option in at least one question. For any item that would depend on an exact price or quota, note in the explanation that the figure is point-in-time and must be verified live.
```
After generating, use the **Hint** and **Explain** buttons. Retake **"Only the questions you missed"** on later days — that's your spaced-repetition lever.
**Why (learning science):** active recall + calibration — scenario distractors expose what you only *think* you know; missed-only retakes implement spacing.

---

### Block 3 — Flashcards (memorizable triggers)
**Feature + path:** Studio → Flashcards → **pencil** to customize. Difficulty: Medium. Number: More.
**When:** Build once early; review across days.

```
Create flashcards from the uploaded sources for AWS AIP-C01 Domain 4 trigger→answer recall. Each card = a short "exam-says X" trigger on the front, the lever/service + a one-line WHY on the back. Cover:
- Cost Lever Priority order (token efficiency → caching → tiering/cascading → PT/batch).
- unit of Bedrock cost = input + output tokens; output priced higher.
- prompt vs semantic cache (cheapen-vs-disappear); raise similarity threshold to cut wrong hits.
- tiering vs cascading vs Intelligent Prompt Routing.
- volume shape → PT / batch / on-demand; custom model → PT required.
- latency: streaming = perceived/TTFT only; maxTokens + latency-optimized = total; concurrency within quotas; temperature ≠ speed lever.
- RAG: reduce numberOfResults / chunking / reranking to cut prefill cost+TTFT.
- monitoring: no aggregate error metric (client/server/throttle distinct); seasonal spend → Anomaly Detection; third-party Claude spend → AWS Budgets; drift → scheduled golden-dataset re-runs; global vs geographic CRI for residency.
Mark any card with a number (price, quota, %, threshold) as "VERIFY LIVE" on the back.
```
Mark **Got it! / Missed it!**, then **Export as CSV** into Anki for long-term spacing.
**Why (learning science):** spaced repetition on atomic triggers; CSV→Anki extends spacing past exam week.

---

### Block 4 — Audio Overview (passive review + contested choices)
**Feature + path:** Studio → Audio Overview → **Deep Dive** for the first pass; switch to **The Debate** for genuinely contested design calls. Length: Default. Use **"Add a prompt"** to focus.
**When:** Commute / between active sessions. First-pass = Deep Dive; reinforcement = Debate.

First-pass focus prompt (Deep Dive):
```
Walk through Domain 4 as a cost-and-latency decision playbook for a Bedrock FM workload: the Cost Lever Priority order, prompt vs semantic caching, volume-shape→billing-mode, the latency "which clock?" decision, and the monitoring program (CloudWatch Bedrock metrics, Cost Anomaly Detection vs Budgets, drift re-runs). Emphasize why the compute-scaling option is always wrong here.
```
Debate focus prompt (The Debate):
```
Debate the genuinely contested Domain 4 design choices: model tiering vs cascading vs Intelligent Prompt Routing; Provisioned Throughput vs batch vs on-demand for different volume shapes; prompt caching vs semantic caching; and managed routing vs hand-rolled. Have each side argue the trade-offs (latency, commitment, quality bar) so I hear when each actually wins.
```
Try **Interactive mode** (Beta, English) — tap **Join** to ask the hosts a follow-up like "why isn't temperature a latency lever?" mid-playback.
**Why (learning science):** dual coding (verbal channel) + transfer — Debate format models defending a choice under trade-offs, which mirrors the scenario exam.

---

### Block 5 — Mind Map + Study Guide (dual coding / structure)
**Feature + path:** Studio → **Mind Map** (visual node graph); Studio → **Study Guide** (study doc).
**When:** Early, to see the shape; revisit before the exam to self-test the structure.

Use the **Mind Map** to confirm the four-lever cost spine and the latency-vs-monitoring branches hang together. (NotebookLM does NOT draw architecture diagrams — structure comes from the Mind Map and the guide's own decision trees.) For the Study Guide, scope it:
```
Build a study guide for Domain 4 organized as decision trees: (1) "where do I start to cut FM cost?" down the Cost Lever Priority; (2) "which latency clock?"; (3) "which billing mode?" by volume shape; (4) the standing monitoring program. End with a flat list of named distractors to reject on sight.
```
**Why (learning science):** dual coding — pairing the verbal sources with a visual/structural map strengthens recall of *where* a rule sits in the decision tree.

---

### Block 6 — Transfer drill (apply, don't recall)
**Feature + path:** Chat (Custom style fine; or Default). Paste below.
**When:** Day 7 / final pass — proves you can apply rules to novel cases, which is what the exam tests.

```
Invent a NEW Domain 4 scenario I have not seen — a fresh Bedrock FM workload with a specific volume shape, latency requirement, repetition pattern, and a monitoring or data-residency wrinkle. Give me 4 answer options written like real exam distractors (include one compute-scaling trap). DO NOT reveal the answer. Wait for my pick + my justification. Then grade me: name the correct lever, walk the decision tree that gets there, explain why each distractor fails (especially the cost-lever-order or which-clock reasoning), and cite the source. If any part depends on a live price/quota, flag it as verify-live and say you can't confirm it against current AWS docs. Then give me a second, harder novel scenario.
```
**Why (learning science):** transfer + interleaving — applying rules to unseen cases (not recognizing memorized ones) is the skill the scenario exam grades.

---

## Spaced schedule
- **Day 1:** Read guide 07 → Block 1 (Socratic, ~10 scenarios) → Block 4 Deep Dive audio.
- **Day 2:** Block 2 Hard quiz → Block 3 flashcards (first pass) → Block 5 Mind Map skim.
- **Day 4:** Quiz "only missed" + flashcards "only missed" → Block 4 Debate audio.
- **Day 7:** Block 6 transfer drill → Study Guide structure self-test → flashcards "only missed."
- **Then:** spaced flashcard/quiz "only missed" reviews every few days until exam.

---

> **Caveat:** NotebookLM answers only from your uploaded sources and CANNOT fact-check against live AWS docs — treat every price, TPM/RPM quota, batch/CRI %, and similarity threshold as *verify-live* (Service Quotas / pricing page). These exact UI labels move fast; adapt if one differs. Pair this notebook with the fact-checked Claude-Code Mock Exams for exam-representative practice.
