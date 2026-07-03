# Domain 1 Master Prompts — Foundation Model Integration, Data Management & Compliance (31%)

**Notebook:** D1 in NotebookLM. **Upload these sources:** guide 01 (Foundation Models & Bedrock Core), guide 02 (RAG & Vector Stores), guide 05 (Prompt Engineering), `cram-d1.md`, and the blueprint.
**Study philosophy:** *Recall before you review — retrieve the answer yourself, then check the citation. NotebookLM only knows your sources and cannot fact-check live AWS docs, so confirm fast-moving facts (Bedrock quotas, model/Region availability, AgentCore) against real AWS docs and the fact-checked Mock Exams.*

This is the **Domain 1** playbook: it drills *this* domain's real traps — RAG-vs-fine-tune for freshness, the vector-store selection cascade, HYBRID silent fallback, Guardrails-don't-scrub-chunks, custom-model-needs-Provisioned-Throughput, and the structured-output ladder.

---

## The Study Loop (run in order)

### Block 1 — Socratic Tutor (the centerpiece)
**Feature + path:** Chat → Configure Chat → Style: **Custom** (paste below) → set Length: **Longer**. Keep all D1 sources checked.
**When:** Daily active-recall driver, after a first read of the guides.

```
You are my exam tutor for AWS Certified Generative AI Developer – Professional (AIP-C01), Domain 1: Foundation Model Integration, Data Management & Compliance. Use ONLY the uploaded sources.

Rules of engagement:
1. Quiz me ONE scenario-style question at a time, in the design/judgment style of the real exam (a requirement, then "what do you choose?"). Do not dump a list.
2. After you ask, STOP. Make me answer AND justify before you reveal anything.
3. When I answer, tell me if I'm right, then explain WHY the correct option wins and WHY each plausible distractor is wrong — name the distractor.
4. Cite the source for every claim so I can click through. If a fact is a quota, a model/Region availability, or anything time-sensitive, explicitly flag "verify against live AWS docs — I cannot check this."
5. Deliberately drill THIS domain's traps, rotating across them:
   - "Data changes often / private / cite sources" => RAG, NEVER fine-tune (fine-tune is behavior/style, not freshness).
   - Escalation order: prompt -> RAG -> fine-tune -> custom FM (GenAI Lens GENOPS05-BP01).
   - HYBRID silent fallback: requesting HYBRID on S3 Vectors or Neptune throws NO error, quietly runs semantic; hybrid only on Aurora/RDS, OSS, MongoDB Atlas.
   - Binary vectors only on OpenSearch Serverless/Managed (Aurora/Pinecone/S3 Vectors are distractors).
   - Guardrails do NOT scrub retrieved KB chunks — only input query + generated output; sensitive text in citations slips through.
   - Guardrails do NOT guarantee valid JSON — structure = structured outputs + app validation; Guardrails = safety only.
   - Structured-output ladder: prompt steers -> JSON Schema/strict tool use enforces structure -> app validation enforces semantics (min/max, minLength) -> Guardrails enforces safety. Layers, not alternatives.
   - Custom/fine-tuned/distilled/imported models REQUIRE Provisioned Throughput; cannot run on-demand.
   - Chunking is immutable after data-source creation — must recreate + re-ingest.
   - numberOfResults default 5 is a MAX, not a guarantee (hierarchical returns fewer).
   - dataDeletionPolicy DELETE removes only Bedrock's embeddings, never the OpenSearch collection / Aurora cluster.
   - Quick-create = exactly 4 stores: OSS, Aurora PG Serverless, Neptune, S3 Vectors.
   - Embedding-model mismatch (different model at ingest vs query) collapses retrieval — re-embed corpus.
   - Batch supports NEITHER tool calling NOR structured output — rules out agent/strict-JSON scenarios.
   - Retry only transient errors (Throttling/Timeout/ServiceUnavailable/InternalServer); never Validation/AccessDenied.
   - Amazon Rerank 1.0 is NOT in us-east-1 — use Cohere Rerank 3.5 there.
   - startsWith/stringContains unsupported on ANY managed KB — use equals/in/numeric or BYO OSS.
   - Inference profiles: cross-Region = bursts/no custom balancer; geography-scoped = data residency; global = max capacity; application = cost attribution.
6. Track my running score and tell me which trap I keep missing.
Begin now with question 1.
```
**Why (learning science):** Active recall + elaborative interrogation — forcing "why" and "why not the distractor" before reveal builds the discrimination the scenario exam actually tests.

---

### Block 2 — Quiz generation (hardest distinctions)
**Feature + path:** Studio → Quiz → click the **pencil** before generating → Difficulty: **Hard** → Number: **More** → paste Prompt below.
**When:** Day 2+, and as a checkpoint after each Socratic session.

```
Generate hard, scenario-based quiz questions for AIP-C01 Domain 1. Each question presents a requirement and asks for the single best design choice, with distractors drawn from this domain's known traps. Concentrate on the distinctions people confuse:
- RAG vs fine-tune vs prompt (especially freshness/private-data => RAG).
- Vector-store selection cascade: OpenSearch Serverless vs S3 Vectors vs Aurora pgvector vs Neptune GraphRAG (binary vectors, cost vs latency, hybrid support, multi-hop, SQL+vectors).
- HYBRID silent fallback; binary-vector store support; Guardrails scope (no chunk scrubbing, no JSON guarantee).
- Inference modes (on-demand vs Provisioned Throughput vs Batch) and the 4 inference-profile types.
- Chunking strategies (NONE/FIXED_SIZE/SEMANTIC/HIERARCHICAL) and immutability after creation.
- Retrieval APIs (Retrieve vs RetrieveAndGenerate vs +sessionId), reranking, query decomposition.
- Structured-output ladder and prompt governance (variants vs versions, Prompt Optimization, CloudTrail RenderPrompt).
Use the Hint and Explain features. For any quota/model/Region fact, note it may be time-sensitive.
```
**Why (learning science):** Active recall + interleaving (mixing subtopics in one set). **Spaced repetition lever:** re-run **"Only cards you missed"** on Day 4 and Day 7 — that's the spacing.

---

### Block 3 — Flashcards (memorizable triggers)
**Feature + path:** Studio → Flashcards → **pencil** → Difficulty: **Medium** → Number: **More** → paste Prompt. Mark "Got it!" / "Missed it!", then **CSV export to Anki** for long-term spacing.
**When:** Daily warm-up, 5 minutes.

```
Make flashcards for AIP-C01 Domain 1 memorizable triggers and one-line distinctions. Front = the exam trigger phrase; back = the answer + the one-sentence "why". Cover:
- "swap models without rewriting app" => Converse API; "show response as it types" => ConverseStream.
- "custom/fine-tuned model in prod" => Provisioned Throughput required.
- "100k docs overnight cheapest" => Batch; "agent calls tools / strict JSON" => NOT batch.
- Inference profiles: cross-Region / geography-scoped / global / application.
- Stores: OSS Serverless / S3 Vectors (~90% cheaper, sub-second, no hybrid) / Aurora pgvector / Neptune GraphRAG; quick-create = 4 stores.
- Chunking: NONE / FIXED_SIZE (overlap 1-99) / SEMANTIC / HIERARCHICAL (2 levels).
- Titan V2 dims 256/512/1024; 256-dim ~97% accuracy at ~75% less storage; float32=32 bit, binary=1 bit.
- numberOfResults default 5; RetrieveAndGenerate query limit 1000 chars; metadata sidecar <=10KB JSON.
- Cohere Rerank 3.5 in us-east-1; QUERY_DECOMPOSITION; implicit filtering (Claude).
- Prompt: instruction at the END; few-shot for format; zero-shot CoT; self-consistency (temp>0); Chain-of-Draft.
- Governance: variants (transient, up to 3) vs versions (immutable); Prompt Optimization rewrites; CloudTrail RenderPrompt data events.
Flag any number/quota as point-in-time to verify.
```
**Why (learning science):** Active recall on atomic facts; CSV-to-Anki gives true spaced repetition beyond the study session.

---

### Block 4 — Audio Overview (passive review + contested choices)
**Feature + path:** Studio → Audio Overview → choose **Deep Dive** for first pass; choose **The Debate** for contested design calls → **Add a prompt** (below). Try **Interactive mode** (Beta) to ask the hosts a follow-up mid-playback.
**When:** Day 1 (Deep Dive, commute/passive); Day 5 (The Debate, after you know the material).

```
Deep Dive prompt: Walk through AIP-C01 Domain 1 as a decision-making narrative — for each scenario type, the requirement, the chosen pattern, and why the obvious alternative is the trap. Emphasize RAG-vs-fine-tune-vs-prompt escalation, the vector-store selection cascade, inference modes/profiles, and the structured-output + Guardrails layering.

The Debate prompt: Stage debates on the genuinely contested design choices in this domain: (1) RAG vs fine-tune for keeping answers current and private; (2) Bedrock Knowledge Bases (managed) vs hand-rolled RAG plumbing; (3) OpenSearch Serverless vs S3 Vectors vs Aurora pgvector for a given corpus; (4) Provisioned Throughput vs on-demand vs Batch. Have each side state when it wins and the failure mode of the other.
```
**Why (learning science):** Dual coding (verbal channel) + transfer — debating contested calls rehearses the judgment the design-based exam rewards.

---

### Block 5 — Mind Map + Study Guide (structure / dual coding)
**Feature + path:** Studio → **Mind Map** (visual node graph) and Studio → **Study Guide**.
**When:** Early, to build the scaffold; revisit before the transfer drill.

```
Study Guide prompt: Produce a Domain 1 study guide organized as DECISION TREES, not prose: (1) RAG vs fine-tune vs prompt diagnosis; (2) vector-store cascade (managed-vs-custom -> store -> chunking -> tune retrieval); (3) inference mode + profile selection; (4) structured-output ladder. Under each leaf, list the trigger phrase and the trap that sits next to it.
```
**Why (learning science):** Dual coding (visual/structural) — the Mind Map mirrors the cram sheet's decision cascades so you "see" where a node sits when a scenario hits.

---

### Block 6 — Transfer drill (apply to NOVEL scenarios)
**Feature + path:** Chat (Custom style from Block 1 works) → paste below.
**When:** Day 7 and again pre-exam.

```
Invent a NEW, realistic Domain 1 scenario I have not seen — a company with a corpus, a freshness/residency/cost constraint, and a quality symptom. Present it with 4 plausible options (one correct, three drawn from this domain's traps). Ask me to choose AND defend my answer. WAIT for my response. Then grade me: confirm/correct, explain why each distractor fails, cite the source, and flag any time-sensitive fact I should verify in live AWS docs. Then ask: "How confident were you, 1-5?" and tell me whether my confidence matched my correctness. Repeat with a fresh scenario each round, varying the constrained lever (freshness, residency, binary vectors, hybrid, multi-hop, structured output, governance).
```
**Why (learning science):** Transfer (applying rules to unseen cases) + calibration (confidence vs correctness) — the highest-value rehearsal for a scenario/design exam.

---

## Spaced schedule
- **Day 1:** Read guides → Block 5 (Mind Map/Study Guide) → Block 4 Deep Dive (passive).
- **Day 2:** Block 1 Socratic session → Block 2 generate Hard quiz.
- **Day 4:** Block 3 flashcards → Quiz **"Only cards you missed"**.
- **Day 5:** Block 4 **The Debate** on contested choices.
- **Day 7:** Block 6 transfer drill → retake missed cards.
- **Pre-exam:** Block 6 again + missed cards; then take a fact-checked Mock Exam.

> **Caveat:** NotebookLM answers only from your uploaded sources and **cannot fact-check live AWS docs**; UI labels shift over time, so adapt paths if they differ. Pair this with the fact-checked **Mock Exams** for exam-representative practice and to confirm fast-moving facts (Bedrock quotas, model/Region availability, AgentCore).
