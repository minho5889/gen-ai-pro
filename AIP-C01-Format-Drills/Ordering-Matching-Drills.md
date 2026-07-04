# AIP-C01 Format Drills — Ordering & Matching

The official AIP-C01 exam guide defines **four** question types: multiple choice, multiple response,
**ordering** (select 3–5 responses and place them in the correct order), and **matching** (match a
list of responses against 3–7 prompts — all pairs must be correct to receive credit). The two mock
exams in this repo drill the first two formats; this file adds targeted reps for the other two.

How to use it: cover the answer, arrange or pair the items on paper, then expand the answer block.
Ordering and matching questions are all-or-nothing on the real exam — partial credit does not exist —
so the goal here is making the *sequences and pairings* automatic, not re-learning the concepts
(the guides own that job). Content is drawn from the deep-dive guides and verified points in this
repo; where a detail is fast-moving, the same point-in-time caveat as everywhere else applies.

7 ordering drills + 7 matching drills, weighted roughly like the real blueprint.

---

## Part 1 — Ordering drills

### O1. RAG ingestion pipeline (Domain 1)

Place these five steps in the order a Bedrock Knowledge Bases ingestion/sync runs them:

- A. Write vectors and associated metadata to the vector store
- B. Chunk the documents per the configured chunking strategy
- C. Connect to the data source and fetch new/modified/deleted documents
- D. Generate embeddings for each chunk with the configured embedding model
- E. Serve the index for retrieval queries

<details><summary>Answer</summary>

**C → B → D → A → E.** Fetch (incremental — only changed documents), chunk, embed, store, serve.
Anchor: chunking happens *before* embedding — a chunk is the unit that gets a vector; you cannot
embed what you have not segmented. (Guide 02.)

</details>

### O2. Advanced retrieval request path (Domain 1)

A production RAG query uses query transformation, hybrid search, and reranking. Order the five stages:

- A. Rerank the candidate set with a reranker model
- B. Run keyword and vector search over the store
- C. Decompose/expand the raw user query
- D. Generate the final answer with the augmented prompt
- E. Insert the top-k reranked chunks into the prompt context

<details><summary>Answer</summary>

**C → B → A → E → D.** Transform the query first (better recall), search (hybrid casts the wide
net), rerank (precision pass over the candidates), augment, generate. Anchor: reranking is *after*
retrieval and *before* the prompt — it never touches the vector store itself. (Guide 02.)

</details>

### O3. Bedrock Agents orchestration turn (Domain 2)

Order the steps of one turn of the agent orchestration loop:

- A. Generate an observation from the action result or Knowledge Base summary
- B. Predict which action-group action to invoke or which Knowledge Base to query
- C. Interpret the input with the FM and generate a rationale
- D. Fold the observation back into the base prompt and re-interpret with the model
- E. Invoke the action (send parameters to the backing Lambda, or return control to the app)

<details><summary>Answer</summary>

**C → B → E → A → D.** Rationale (reason) → predict → invoke (act) → observation (observe) →
augment-and-repeat. This is ReAct running inside the managed service: rationale = reason step,
action = act step, observation = observe step. (Guide 04 §2.)

</details>

### O4. Agent change-to-production flow (Domain 2)

A change must go from an edited agent to production traffic, with a rollback path. Order:

- A. Repoint the production alias to the new version
- B. Edit the DRAFT version's configuration (action group, instructions, guardrail…)
- C. Run PrepareAgent to compile the changes into a testable state
- D. Create an immutable version from the prepared DRAFT
- E. Roll back, if needed, by repointing the alias to the previous version

<details><summary>Answer</summary>

**B → C → D → A → E.** Edit DRAFT → Prepare → immutable version → repoint alias → rollback is
also just repointing the alias. Anchor: nothing takes effect until Prepare, and the app always
calls the *alias*, never a version. (Guide 04; cram-d2.)

</details>

### O5. Defense-in-depth request path (Domain 3)

Order the layers a hardened GenAI request/response passes through, first to last:

- A. Guardrail output policies evaluate the response (including contextual grounding)
- B. Application-side post-processing validates structure (JSON Schema) and redacts before logging
- C. Comprehend-based pre-processing filter screens the raw user input
- D. The foundation model generates the response
- E. Guardrail input policies evaluate the prompt

<details><summary>Answer</summary>

**C → E → D → A → B.** App-level input screen → guardrail input pass → model → guardrail output
pass → app-level output validation. Anchor: input filtering and output verification are different
controls — neither is a superset of the other, which is why both ends exist. (Guide 03.)

</details>

### O6. Cost levers, cheapest win first (Domain 4)

Order these levers in the sequence a cost-optimization effort should try them:

- A. Provisioned Throughput / batch for steady high volume
- B. Token efficiency (prompt compression, context pruning)
- C. Model tiering/cascading (small model first, escalate on need)
- D. Caching (prompt caching, semantic caching)

<details><summary>Answer</summary>

**B → D → C → A.** Trim what you send, avoid re-sending it, downsize who answers it, and only then
buy capacity. Anchor: Provisioned Throughput is the *last* lever, not the first — it pays off only
at sustained volume. (Guide 07; cram-d4; strategy doc §6.)

</details>

### O7. Shipping a model change safely (Domain 5)

Order the evaluation-to-production pipeline for a prompt or model update:

- A. Canary the update on a small slice of live traffic
- B. Define/refresh the golden dataset that represents critical question types
- C. Gate the deployment in CI/CD on the evaluation scores
- D. Run the evaluation (Bedrock Model Evaluations / LLM-as-a-judge) against the golden dataset
- E. Monitor production quality signals and roll back on drift

<details><summary>Answer</summary>

**B → D → C → A → E.** Golden data first (no baseline, no signal), evaluate, gate, canary, monitor.
Anchor: the golden dataset exists *before* the change — it is the yardstick, so it cannot be derived
from the thing being measured. (Guide 06.)

</details>

---

## Part 2 — Matching drills

### M1. Chunking strategy → scenario (Domain 1)

| Prompt | |
|---|---|
| 1. Legal contracts where clause context depends on parent sections | |
| 2. Uniform FAQ snippets; simplest predictable behavior | |
| 3. Documents pre-split upstream; index each file as supplied | |
| 4. Topically meandering transcripts; split where meaning shifts | |

Options: **A.** FIXED_SIZE · **B.** SEMANTIC · **C.** HIERARCHICAL · **D.** NONE

<details><summary>Answer</summary>

**1-C, 2-A, 3-D, 4-B.** Hierarchical preserves parent-child structure; fixed-size is the cheap
default for uniform content; NONE means "my chunks are already made"; semantic splits on meaning
boundaries at embedding cost. (Guide 02.)

</details>

### M2. Vector store → requirement (Domain 1)

| Prompt | |
|---|---|
| 1. Lowest storage cost for a huge, flat corpus with sub-second lookup | |
| 2. Multi-hop reasoning across relationships between linked documents | |
| 3. Co-locate vectors with existing relational rows and SQL filters | |
| 4. Managed hybrid (keyword + vector) search at scale | |

Options: **A.** OpenSearch Serverless · **B.** Aurora PostgreSQL + pgvector · **C.** S3 Vectors · **D.** Neptune Analytics (GraphRAG)

<details><summary>Answer</summary>

**1-C, 2-D, 3-B, 4-A.** S3 Vectors = cheap flat storage; GraphRAG = relationship traversal;
pgvector = relational co-location; OpenSearch = the hybrid-search workhorse. Trap to remember:
requesting hybrid search on a store that doesn't support it does not error — it silently falls
back to semantic-only. (Guide 02; Mock Exam 2 Q16/Q18.)

</details>

### M3. AgentCore component → capability (Domain 2)

| Prompt | |
|---|---|
| 1. Serverless, session-isolated execution for agents, long-running sessions | |
| 2. One managed MCP endpoint that turns APIs/Lambda into agent-reachable tools | |
| 3. Token vault + OAuth so an agent acts on a user's behalf | |
| 4. Multi-strategy memory (semantic, summary, user-preference) across sessions | |
| 5. OpenTelemetry-compatible tracing for agents built on any framework | |

Options: **A.** Gateway · **B.** Observability · **C.** Runtime · **D.** Identity · **E.** Memory

<details><summary>Answer</summary>

**1-C, 2-A, 3-D, 4-E, 5-B.** Runtime hosts, Gateway connects tools, Identity holds credentials,
Memory persists strategies, Observability traces. Trap: multi-strategy memory is AgentCore Memory —
native Bedrock Agents long-term memory is session summarization only. (Guide 04; cram-d2.)

</details>

### M4. Agent technology → role in the stack (Domain 2)

| Prompt | |
|---|---|
| 1. Managed agent primitive inside Bedrock — now in maintenance mode, closed to new customers 2026-07-30 | |
| 2. Open-source, model-driven authoring SDK that runs anywhere | |
| 3. Framework- and model-agnostic operating platform for running agents at scale | |
| 4. Open protocol standardizing how agents reach tools and data (M×N → M+N) | |

Options: **A.** Strands Agents · **B.** MCP · **C.** Bedrock Agents (Classic) · **D.** Bedrock AgentCore

<details><summary>Answer</summary>

**1-C, 2-A, 3-D, 4-B.** The layers stack rather than compete: author with Strands, operate on
AgentCore, connect tools over MCP; Agents Classic is the original managed primitive — existing
workloads continue, new builds point at AgentCore *(status is point-in-time — verify near exam
day)*. (Guide 04.)

</details>

### M5. Guardrails policy → what it does (Domain 3)

| Prompt | |
|---|---|
| 1. Blocks or masks PII in prompts and responses | |
| 2. Blocks whole subject areas defined in natural language | |
| 3. Filters harmful content categories with configurable strength | |
| 4. Flags responses not grounded in the retrieved source or irrelevant to the query | |
| 5. Blocks exact strings/profanity you enumerate | |

Options: **A.** Content filters · **B.** Contextual grounding check · **C.** Sensitive information filter · **D.** Denied topics · **E.** Word filters

<details><summary>Answer</summary>

**1-C, 2-D, 3-A, 4-B, 5-E.** Remember the layering trap: guardrails act at the model boundary —
they do not scrub what Model Invocation Logging writes, and they do not screen retrieved KB chunks
on the way in. (Guide 03.)

</details>

### M6. Caching technique → scenario (Domain 4)

| Prompt | |
|---|---|
| 1. Long shared system-prompt prefix re-sent on every call — make it cheaper | |
| 2. Users ask semantically similar questions — skip the model call entirely | |
| 3. Identical public responses served globally — cache at the CDN | |

Options: **A.** Semantic caching · **B.** Prompt caching · **C.** Edge caching (CloudFront)

<details><summary>Answer</summary>

**1-B, 2-A, 3-C.** The distinction that keeps appearing: prompt caching makes the invocation
*cheaper* (the call still happens); semantic caching makes the invocation *disappear* (a hit
returns the stored answer). (Guide 07; cram-d4.)

</details>

### M7. Evaluation method → question it answers (Domain 5)

| Prompt | |
|---|---|
| 1. "Score thousands of outputs for faithfulness/relevance without human raters" | |
| 2. "Which of two prompts performs better on live traffic, measured safely?" | |
| 3. "Are nuanced brand-tone judgments acceptable? Humans must decide" | |
| 4. "Did retrieval return the right chunks, independent of generation?" | |
| 5. "Run standardized automatic metrics over a built-in or custom dataset" | |

Options: **A.** A/B + canary testing · **B.** LLM-as-a-judge · **C.** Retrieval-quality metrics (context relevance/coverage) · **D.** Human evaluation workflow · **E.** Bedrock Model Evaluations (automatic)

<details><summary>Answer</summary>

**1-B, 2-A, 3-D, 4-C, 5-E.** Anchor: evaluate retrieval and generation separately — a RAG system
can retrieve perfectly and still generate badly, and vice versa; traditional single-number accuracy
metrics belong to closed-form tasks, not open-ended generation. (Guide 06.)

</details>

---

*Generated as a supplement after a July 2026 content audit found the mock exams covered only 2 of
the exam's 4 official question formats. Facts trace to the repo's guides and the official exam
guide; fast-moving details carry the repo's standard point-in-time caveat.*
