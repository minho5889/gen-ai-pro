# AIP-C01 Practice Exam 2 — Analysis (Q16-Q20)

## Question 16

### 1. Question Summary
**Scenario:** A legal-tech firm needs RAG over millions of contracts stored in Amazon S3. Answers must follow relationships between clauses across related contracts (multi-hop reasoning such as "which clauses in linked agreements affect this indemnity"), and the firm wants more explainable, less hallucination-prone results than flat passage lookup provides. They want a fully managed setup.

**Ask:** Which vector store BEST fits these requirements?

### 2. Domain Mapping
**Domain:** Task 1.4 — Vector stores (GraphRAG selection)
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ Amazon Neptune Analytics (GraphRAG), which combines vector similarity with graph traversal for multi-hop reasoning across connected documents and works with S3 data sources
- **B** ❌ Amazon S3 Vectors, because its low cost suits a large contract corpus
- **C** ❌ Amazon Aurora PostgreSQL with pgvector, to join contract metadata with vector search
- **D** ❌ Amazon OpenSearch Serverless with hybrid search enabled

### 4. Correct Answer Deep-Dive
**Answer: A**

Multi-hop reasoning that follows relationships between connected documents, with more explainable and less hallucination-prone answers, is the defining GraphRAG use case — Amazon Neptune Analytics combines vector similarity with graph traversal and works with S3 sources. S3 Vectors (B) is a flat, low-cost, sub-second store that cannot traverse relationships. Aurora (C) co-locates relational and vector data but does not do graph traversal/multi-hop reasoning. OpenSearch Serverless (D) gives fast hybrid retrieval of independent passages but no relationship traversal.

### 5. Key Takeaway
Multi-hop reasoning that follows relationships between connected documents, with more explainable and less hallucination-prone answers, is the defining GraphRAG use case — Amazon Neptune Analytics combines vector similarity with graph traversal and works with S3 sources.

---

## Question 17

### 1. Question Summary
**Scenario:** An application assembles Bedrock inference requests in a data pipeline and intermittently receives ValidationException errors. The team's retry-with-exponential-backoff logic does not help — the same requests fail identically on every retry.

**Ask:** What is the cause, and what is the actual fix?

### 2. Domain Mapping
**Domain:** Task 1.3 — Data validation and pipelines (ValidationException)
**Task:** Task 1.3

### 3. Option Analysis
- **A** ✅ ValidationException is a client error from a malformed request body, so retrying is pointless — the fix is in the pipeline's input-formatting step, assembling the request into the correct Bedrock JSON/content-block structure
- **B** ❌ ValidationException is a transient throttling signal; the fix is to add more retry attempts with longer backoff
- **C** ❌ ValidationException means the model is overloaded; route the request to a cross-Region inference profile
- **D** ❌ ValidationException indicates the IAM role lacks permissions; attach bedrock:InvokeModel

### 4. Correct Answer Deep-Dive
**Answer: A**

ValidationException is a deterministic client error caused by a malformed request (it does not conform to the expected JSON/message-and-content-block structure), so it fails identically on retry — backoff and retries help only transient server-side errors. The real fix lives in the pipeline's input-formatting step: build the request into the correct Bedrock shape before sending. B and C treat it as transient/capacity, which it is not. D describes AccessDeniedException, a different client error.

### 5. Key Takeaway
ValidationException is a deterministic client error caused by a malformed request (it does not conform to the expected JSON/message-and-content-block structure), so it fails identically on retry — backoff and retries help only transient server-side errors.

---

## Question 18

### 1. Question Summary
**Scenario:** A user-facing assistant runs on a Bedrock knowledge base whose vectors live in Amazon S3 Vectors. Users mix conceptual questions ("how do refunds work?") with exact tokens such as SKUs and error codes like ThrottlingException. The team set overrideSearchType to HYBRID, observed no errors, but exact-token matches still miss.

**Ask:** Which TWO statements explain the situation or correctly fix it? (Select TWO)

### 2. Domain Mapping
**Domain:** Task 1.5 — Retrieval (hybrid search silent fallback)
**Task:** Task 1.5

### 3. Option Analysis
- **A** ✅ Hybrid search is only supported on stores with a filterable text field — Aurora/RDS, OpenSearch Serverless, and MongoDB Atlas; on any other store Bedrock silently falls back to semantic search
- **B** ✅ To get true hybrid behavior, move the knowledge base to a hybrid-capable store such as OpenSearch Serverless so keyword matching actually executes
- **C** ❌ Requesting HYBRID against S3 Vectors raises a ValidationException, so the "no errors" observation is impossible
- **D** ❌ Pure semantic search reliably matches exact tokens, so the chosen search type is irrelevant to the symptom
- **E** ❌ Switching to a higher embedding dimension would resolve the missed exact-token matches

### 4. Correct Answer Deep-Dive
**Answer: AB**

Hybrid (vector + keyword) search is supported only on Aurora/RDS, OpenSearch Serverless, and MongoDB Atlas. The trap is that requesting HYBRID on an unsupported store like S3 Vectors does NOT error — Bedrock silently falls back to semantic search (A), which is exactly why the team sees no error yet gets semantic-only behavior. The remedy is to move to a hybrid-capable store so keyword matching runs (B). C is the inverse of the real behavior — there is no error. D is false: pure semantic search is what drifts on exact tokens. E confuses dimensionality (a semantic-precision/cost knob) with the lexical exact-match problem only hybrid/keyword search solves.

### 5. Key Takeaway
Hybrid (vector + keyword) search is supported only on Aurora/RDS, OpenSearch Serverless, and MongoDB Atlas.

---

## Question 19

### 1. Question Summary
**Scenario:** A team needs every change to their S3-backed knowledge base reflected within minutes, and they expect bursts of hundreds of file changes during deploys. A junior engineer proposes wiring each S3 event directly to a Lambda that calls StartIngestionJob immediately on every event.

**Ask:** Which THREE statements correctly describe why this fails under load and the documented architecture? (Select THREE)

### 2. Domain Mapping
**Domain:** Task 1.4 — Vector stores (event-driven sync quotas)
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ Each StartIngestionJob syncs the data source as a unit (incrementally), and the service enforces real ceilings — an adjustable per-knowledge-base concurrent-ingestion-job quota (50 by default today) plus control-plane throttling on call bursts — so firing a job per file event is redundant work that runs into those ceilings
- **B** ✅ A burst of hundreds of events firing StartIngestionJob directly will pile up redundant sync jobs and get throttled rather than being absorbed
- **C** ✅ The documented reference pattern buffers events through SQS and uses a Step Functions state machine that checks the quota and waits/retries before calling StartIngestionJob
- **D** ❌ Removing the quotas requires no change because StartIngestionJob auto-queues unlimited concurrent jobs internally
- **E** ❌ Each StartIngestionJob re-embeds the entire data source, so the only fix is to disable incremental sync

### 4. Correct Answer Deep-Dive
**Answer: ABC**

The naive design breaks because ingestion is job-based: each StartIngestionJob incrementally syncs the data source as a unit, and the service enforces real ceilings — an adjustable per-knowledge-base concurrent-ingestion-job quota (50 by default per the current Bedrock quota table) plus control-plane throttling on call bursts — so a job per file event is redundant work that runs into those ceilings (A); a burst of hundreds of direct calls piles up throttled, redundant sync jobs instead of being absorbed (B). The documented event-driven reference architecture decouples events from jobs: buffer with SQS and orchestrate with a Step Functions state machine that batches changes and waits/retries before calling StartIngestionJob (C). D is false — there is no unlimited internal queue. E is false — StartIngestionJob is incremental (only added/modified/deleted docs), so a full re-embed is not the issue; the redundant-jobs-plus-throttling dynamic is.

> Note: key updated during re-verification — an earlier version cited ~5 concurrent jobs/account, 1/KB, 1/data source and a ~0.1 RPS API limit, figures not found in current documentation (kb-managed-quotas documents 50 concurrent ingestion jobs per knowledge base). Quotas are point-in-time — re-verify near exam day.

### 5. Key Takeaway
Ingestion is job-based and quota/throttle-bounded — decouple events from jobs: buffer file changes in SQS and batch them into StartIngestionJob calls with Step Functions, because one sync job per file event is redundant work that throttles under bursts.

---

## Question 20

### 1. Question Summary
**Scenario:** A production pipeline must (1) return well-formed JSON conforming to a fixed object shape that downstream APIs consume, and (2) block toxic content and prevent PII leakage in model output. A teammate proposes relying on a single control to satisfy both requirements.

**Ask:** Which TWO statements correctly describe how to layer the controls? (Select TWO)

### 2. Domain Mapping
**Domain:** Task 1.6 — Prompt engineering (structure vs safety layering)
**Task:** Task 1.6

### 3. Option Analysis
- **A** ✅ Structural correctness is enforced by Structured outputs (a JSON Schema output format or strict tool use), not by Guardrails
- **B** ✅ Amazon Bedrock Guardrails is the safety backstop for toxic content and PII filtering, but it does not guarantee valid JSON or schema conformance
- **C** ❌ Amazon Bedrock Guardrails can be configured to enforce that the output is valid JSON matching the schema, replacing the need for structured outputs
- **D** ❌ A low temperature alone guarantees both schema-valid JSON and the absence of toxic or PII content
- **E** ❌ Structured outputs evaluates input and output text against six safety policy types

### 4. Correct Answer Deep-Dive
**Answer: AB**

These controls are complementary layers, not interchangeable. Structural/type correctness is enforced by Structured outputs — a JSON Schema output format or strict tool use (A). Guardrails is the safety and content-governance backstop (content filters, PII filters, denied topics, etc.) for toxic content and PII, but it does not guarantee valid JSON or schema conformance (B). C is the trap — Guardrails does not validate JSON structure. D is false: temperature reduces drift but guarantees neither structure nor safety. E swaps the roles — the six safety policy types belong to Guardrails, not Structured outputs.

### 5. Key Takeaway
These controls are complementary layers, not interchangeable.

---

