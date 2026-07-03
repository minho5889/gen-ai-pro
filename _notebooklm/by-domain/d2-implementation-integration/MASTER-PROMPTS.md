# Domain 2 — Implementation & Integration: NotebookLM Master Prompts

**Notebook:** AIP-C01 Domain 2 (Implementation & Integration, 26% of the exam). **Upload into this notebook:** guide 04 (Agentic AI / AgentCore / Strands / MCP), guide 08 (Enterprise Integration & Deployment), guide 01 (Foundation Models), `cram-d2.md`, and the exam blueprint.
**Study philosophy:** recall first, confirm facts elsewhere. NotebookLM only answers from these sources and cannot check live AWS docs — use it to drill *decision rules and traps*, then verify fast-moving numbers (quotas, AgentCore primitives) against AWS docs and the fact-checked Mock Exams.

---

## The Study Loop (run in order)

### Block 1 — Socratic Tutor (the centerpiece)
**Feature + path:** Chat → Configure Chat → Style: **Custom** (paste below) → Length: Default. Then chat one scenario at a time.
**When:** Every session. This is your main active-recall engine.

```
You are my AIP-C01 Domain 2 (Implementation & Integration) exam tutor. Use ONLY the uploaded sources. Quiz me Socratically, ONE scenario at a time.

Rules for every turn:
1. Give me ONE realistic, design-style scenario question (latency/scale/auth/residency/agency constraints) like the real exam. Offer 4 lettered options.
2. STOP. Make me answer AND justify before you reveal anything. Do not show the answer until I respond.
3. After I answer: tell me right/wrong, give the correct choice with a clickable citation, and explain why EACH distractor is wrong — not just the right one.
4. Then ask me a one-line "why" follow-up to force elaboration.

Deliberately drill these Domain 2 traps:
- Pattern 3 (both sides): over-agency (agent where a single prompt / RAG / Step Functions fits) AND under-management (hand-rolling the loop instead of using the managed primitive, Bedrock Agents).
- Agent vs not: self-contained transform -> prompt; answer-from-docs -> RAG; fixed steps -> Step Functions; steps depend on runtime results -> agent.
- Bedrock Agents (managed primitive, Bedrock-only) vs AgentCore (operating platform, any framework/model) vs Strands (authoring SDK that runs on AgentCore) — they STACK, not either/or; no forced migration.
- MCP hosting: Lambda (stateless/bursty/scale-to-zero) vs ECS Fargate (long-lived, streaming, VPC, heavy deps) vs AgentCore Gateway (managed MCP endpoint, no infra).
- OpenAPI schema must be EXACTLY 3.0.0, NO enum (use description); 3.0.1 and enum are distractors.
- Return of control when reusing existing APIs OR task > 15 min (bypasses Lambda 15-min cap).
- Alias indirection: prod calls the ALIAS not DRAFT/TSTALIASID; edit -> PrepareAgent -> immutable version -> repoint alias; kill-switch = REJECT_INVOCATIONS.
- Bedrock has NO resource-based policies — cross-account = assumed roles + identity policies + SCPs.
- InvokeAgent must scope to the agent-ALIAS ARN (not agent ARN); RetrieveAndGenerate can't be ARN-scoped (uses *).
- Cost attribution (inference profiles / requestMetadata / tags) does NOT deny access — use IAM/SCP on the model ARN to block.
- "Build a gateway for cost visibility" is a distractor — reason is governance/throttling/decoupling.
- Bedrock is Regional — "Bedrock at the edge" (Wavelength/Outposts/Local Zones) is wrong; only the app tier goes to the edge.
- Residency ladder: single country -> In-Region; geography -> Geo profile; no constraint+cheapest -> Global (NEVER a residency answer); EU-operator-only -> European Sovereign Cloud. store=false != zero retention (need data_retention_mode=none).
- Converse API = write-once/swap-modelId; ConverseStream fixes time-to-first-token; StartAsyncInvoke->S3 for long single gens; batch (~50% off) for high-volume non-urgent (no tool use / no structured output).
- The binding limit for a slow model behind REST is the API Gateway 29s integration timeout, NOT Lambda timeout. ThrottlingException at scale -> SQS buffer, NOT raise Lambda concurrency.
- Streaming front-end by auth: Cognito + least code -> AppSync subscriptions; bidirectional multi-turn -> WebSocket API; single-user prototype -> Lambda function URL.
- Amplify conversation route (managed history/UI) vs generation route (single-shot). BDA async InvokeDataAutomationAsync for video/audio/PDF; sync = images only.

After each answer, if any fact could be stale (Bedrock quotas, AgentCore primitive names, timeouts, discounts), say so explicitly and tell me to confirm against live AWS docs — you CANNOT verify against them. Keep going until I say stop. Begin with question 1.
```
**Why (learning science):** Active recall + elaborative interrogation — retrieving and defending *before* seeing the answer, with "why not the distractor" forcing discrimination of look-alikes.

---

### Block 2 — Quiz Generation (hardest distinctions)
**Feature + path:** Studio → Quiz → click the **pencil** to customize BEFORE generating → set Difficulty **Hard**, paste Prompt, Number **More**.
**When:** After a learn pass; retake across days.

```
Generate hard, scenario-based questions on AIP-C01 Domain 2 (Implementation & Integration). Avoid pure recall — every question should present constraints and ask for the right construct/API/primitive. Concentrate on the look-alikes I confuse:
- Bedrock Agents vs AgentCore vs Strands vs Agent Squad; AgentCore primitives (Runtime / Gateway / Identity / Observability / Code Interpreter / Browser).
- MCP hosting choice (Lambda vs ECS Fargate vs AgentCore Gateway).
- Return of control vs Lambda-backed action group; OpenAPI 3.0.0 (no enum) traps.
- Alias indirection + PrepareAgent + REJECT_INVOCATIONS kill-switch.
- RBAC over Bedrock: no resource-based policies; agent-ALIAS ARN for InvokeAgent; RetrieveAndGenerate unscopable; cost attribution != access control; GuardrailIdentifier / ServiceTier condition keys.
- Residency ladder (In-Region vs Geo vs Global vs European Sovereign Cloud); data_retention_mode=none vs store=false; Bedrock-is-Regional/edge trap.
- Invocation mode (sync / ConverseStream / StartAsyncInvoke / batch / SQS buffer / Step Functions) and the API Gateway 29s integration-timeout trap.
- Streaming front-ends by auth (AppSync vs WebSocket vs Lambda function URL); Amplify conversation vs generation; BDA async vs sync.
For each, write a tempting distractor that reflects the common wrong answer. After generating, I will use "Only cards/questions I missed" on later days. Flag any quota/number that may be stale.
```
**Why (learning science):** Active recall + interleaving (mixing subtopics) + spaced repetition via "only missed" retakes on later days.

---

### Block 3 — Flashcards (memorizable triggers)
**Feature + path:** Studio → Flashcards → **pencil** to customize → Difficulty Medium–Hard, paste Prompt → generate. Mark Got it!/Missed it!; **Export CSV → Anki**.
**When:** Daily 5-minute spacing; export to Anki for long-term scheduling.

```
Make flashcards for the memorizable triggers/distinctions in AIP-C01 Domain 2. Front = a terse trigger/scenario; back = the answer + the one-line "why". Cover:
- "Agent warranted?" decision (prompt / RAG / Step Functions / agent).
- Three-layer model: Bedrock Agents = managed primitive; AgentCore = operating platform; Strands = authoring SDK (they stack).
- MCP: Lambda vs ECS Fargate vs AgentCore Gateway; MxN -> M+N.
- OpenAPI exactly 3.0.0, no enum; Return of control (reuse APIs / >15 min); x-requireConfirmation=ENABLED for HITL.
- Alias > DRAFT/TSTALIASID; PrepareAgent to deploy edits; alias state REJECT_INVOCATIONS = kill-switch; agent trace (OrchestrationTrace/FailureTrace).
- No Bedrock resource-based policies; InvokeAgent -> agent-ALIAS ARN; RetrieveAndGenerate uses *; ApplyGuardrail-only for 3rd-party model.
- Residency ladder + data_retention_mode=none; Bedrock is Regional (edge = app tier only); PrivateLink interface endpoint for private Bedrock.
- Converse vs InvokeModel; ConverseStream; StartAsyncInvoke->S3; batch ~50% off (no tool use / no structured output); SQS buffer for throttling; Step Functions for human gate.
- API GW 29s integration timeout; AppSync 30s resolver; Lambda streaming 200 MB.
- Streaming front-ends by auth; Amplify conversation vs generation; BDA async for video/audio/PDF.
Keep numbers on their own cards and label them as point-in-time to verify against AWS docs.
```
**Why (learning science):** Active recall on atomic facts + spaced repetition (Anki scheduling is the durable retention lever).

---

### Block 4 — Audio Overview (passive / dual-coding)
**Feature + path:** Studio → Audio Overview → choose Format → **Add a prompt** (below). Use **Deep Dive** for the first pass; switch to **The Debate** for genuinely contested design choices. Try **Interactive mode** (Beta) to ask follow-ups mid-playback.
**When:** First pass (Deep Dive on a commute), then Debate when two options feel equally plausible.

```
Focus on Domain 2 design DECISIONS that have a defensible "it depends". Debate the contested trade-offs as competing positions, then state the AWS-intended tie-breaker:
- Single prompt vs RAG vs Step Functions vs a true agent (when is agency actually warranted vs over-engineering?).
- Managed primitive (Bedrock Agents) vs hand-rolled loop; and Bedrock Agents vs AgentCore vs Strands (why they stack, not compete).
- MCP server on Lambda vs ECS Fargate vs AgentCore Gateway.
- Per-tenant cost attribution: application inference profiles vs Converse requestMetadata (and why neither is access control).
- Residency: In-Region vs Geo vs Global vs European Sovereign Cloud.
- Invocation mode: sync/streaming vs async vs batch vs SQS-buffered vs Step Functions.
Note any figure that may be stale and remind me to confirm against live AWS docs.
```
**Why (learning science):** Dual coding (verbal channel) + transfer — The Debate format rehearses defending a choice, which is what the scenario-based exam tests.

---

### Block 5 — Mind Map + Study Guide (structure / dual-coding)
**Feature + path:** Studio → **Mind Map** (visual node graph) for structure; Studio → **Study Guide** for a study-focused doc. Open the Mind Map alongside Block 1.
**When:** Early, to build the scaffold; revisit to see where a scenario "lives".

```
Create a Study Guide for Domain 2 organized by the five tasks: 2.1 Agentic AI & tools, 2.2 Model deployment, 2.3 Enterprise integration (gateway/RBAC/residency/CI-CD), 2.4 FM API integration, 2.5 App integration & dev tools. Under each, list the key decision rules as "if the scenario says X -> choose Y because Z", and end each section with its top named distractors. Add inline citations.
```
**Why (learning science):** Dual coding (visual/structural) — the Mind Map and decision-tree layout give the verbal rules a spatial home, aiding retrieval.

---

### Block 6 — Transfer Drill (novel scenarios, then graded)
**Feature + path:** Chat (Custom or Default Style). Paste below; answer in chat; let it grade.
**When:** Later in the loop (Day 7), once recall is solid — this trains application, not memory.

```
Invent a BRAND-NEW Domain 2 scenario I have not seen, with concrete numbers and constraints (traffic shape, latency target, auth model, residency requirement, agency level). Do NOT give options — make me design the answer in prose: which construct/primitive/API, and why. After I respond, grade me 0-5, cite the source rule I matched or missed, name any trap I fell into (e.g. raising Lambda timeout/concurrency, agent where RAG fits, Global for residency, cost attribution as access control), and give one harder variant. Ask me to rate my confidence first so we can compare confidence vs correctness. Flag any fact you can't verify against live AWS docs.
```
**Why (learning science):** Transfer (apply rules to novel cases) + calibration (confidence-vs-correctness check surfaces what you only *think* you know).

---

## Spaced Schedule
- **Day 1:** Block 5 (Study Guide + Mind Map) → Block 1 (Socratic) → Block 4 (Deep Dive audio).
- **Day 2:** Block 2 (Hard quiz) + Block 3 (flashcards, export to Anki).
- **Day 4:** Retake quiz/flashcards **"Only ones I missed"**; Block 4 **The Debate** on contested choices.
- **Day 7:** Block 6 (Transfer drill) + final "only missed" pass.
- Repeat the Day 4/Day 7 cycle until missed-set is near zero.

---

> **Caveat:** NotebookLM answers only from your uploaded sources and **cannot fact-check against live AWS docs** — treat all quotas, timeouts, discounts, and AgentCore primitive names as point-in-time and confirm against current AWS documentation. UI labels above may shift; adapt as needed. Pair this with the fact-checked **Mock Exams** for exam-representative practice.
