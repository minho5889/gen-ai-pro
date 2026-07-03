# AIP-C01 Practice Exam 1 — Analysis (Q11-Q15)

## Question 11

### 1. Question Summary
**Scenario:** A support chatbot on a Bedrock knowledge base backed by Amazon OpenSearch Serverless answers conceptual questions well but keeps missing answers when users paste exact error codes such as ThrottlingException or specific product SKUs. An engineer set overrideSearchType to HYBRID on a different knowledge base backed by S3 Vectors and reports it made no difference there.

**Ask:** Which explanation and remediation are correct?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.5

### 3. Option Analysis
- **A** ✅ On OpenSearch Serverless, set overrideSearchType to HYBRID to add keyword matching for exact tokens; on the S3 Vectors KB, HYBRID is unsupported and silently falls back to semantic search, so a hybrid-capable store is required for that behavior
- **B** ❌ Increase numberOfResults to 50 on both knowledge bases; exact-token misses are caused by too few results
- **C** ❌ Set overrideSearchType to SEMANTIC on the OpenSearch KB to force vector-only matching of the error codes
- **D** ❌ Switch the embedding model to a higher dimension on both; larger vectors capture exact strings

### 4. Correct Answer Deep-Dive
**Answer: A**

Missed exact tokens (error codes, SKUs) is the classic weakness of pure semantic search; HYBRID adds keyword/lexical matching and OpenSearch Serverless supports it. On S3 Vectors, HYBRID is unsupported and Bedrock silently falls back to semantic (no error), which is exactly why the engineer saw no change — a hybrid-capable store (Aurora/RDS, OpenSearch Serverless, MongoDB Atlas) is required. B floods the context window without fixing precision. C forces vector-only, the opposite of what is needed. D does not make embeddings match literal strings.

### 5. Key Takeaway
Missed exact tokens (error codes, SKUs) is the classic weakness of pure semantic search; HYBRID adds keyword/lexical matching and OpenSearch Serverless supports it.

---

## Question 12

### 1. Question Summary
**Scenario:** A RAG team operating in the us-east-1 (N. Virginia) Region observes that the genuinely best chunk is often retrieved but ranked too low to make it into the top few chunks sent to the model, so answers miss it. They want to add a second relevance pass to reorder candidates before generation and must choose a reranker model that is actually available in their Region.

**Ask:** Which technique and reranker model should they use?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.5

### 3. Option Analysis
- **A** ❌ Query decomposition with Amazon Rerank 1.0
- **B** ❌ Reranking with Amazon Rerank 1.0, which is the default reranker in every Region
- **C** ✅ Reranking with Cohere Rerank 3.5, because Amazon Rerank 1.0 is not available in us-east-1
- **D** ❌ Increase numberOfResults so the best chunk is included even at a low rank; no reranker is needed

### 4. Correct Answer Deep-Dive
**Answer: C**

The symptom — right chunk retrieved but ranked too low to be used — is exactly what reranking fixes by adding a second relevance pass that reorders candidates. The region trap: Amazon Rerank 1.0 is not available in us-east-1, so only Cohere Rerank 3.5 works there. A misnames the technique (decomposition is for multi-part questions, not reordering). B states a false availability. D floods context without ensuring the best chunk reaches the top few that actually enter the prompt.

### 5. Key Takeaway
The symptom — right chunk retrieved but ranked too low to be used — is exactly what reranking fixes by adding a second relevance pass that reorders candidates.

---

## Question 13

### 1. Question Summary
**Scenario:** Users frequently ask multi-part comparison questions of a Bedrock knowledge base, such as 'Did the Phoenix or Denver region have higher Q3 revenue, and which grew faster?' A single flat semantic retrieval returns chunks for one region or the other but never enough to compare both at once, so answers are incomplete.

**Ask:** Which managed retrieval capability addresses this, and how is it enabled?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.5

### 3. Option Analysis
- **A** ❌ Metadata filtering on a region attribute, configured in the vectorSearchConfiguration
- **B** ✅ Query decomposition, enabled by setting orchestrationConfiguration.queryTransformationConfiguration.type to QUERY_DECOMPOSITION on a RetrieveAndGenerate request
- **C** ❌ Hybrid search, enabled by setting overrideSearchType to HYBRID on a Retrieve request
- **D** ❌ Reranking, enabled via the standalone Rerank API on the bedrock-agent-runtime endpoint

### 4. Correct Answer Deep-Dive
**Answer: B**

Multi-part questions that no single chunk answers are the canonical case for query decomposition: it splits the question into sub-queries, retrieves each, and combines them. As a managed feature it is set via orchestrationConfiguration.queryTransformationConfiguration.type = QUERY_DECOMPOSITION on RetrieveAndGenerate (it lives there, not on bare Retrieve, because the generation step combines the sub-answers). A (metadata filtering) narrows candidates but does not split the question. C (hybrid) helps exact-token recall, not multi-part decomposition. D (reranking) reorders candidates but still cannot assemble a both-regions comparison from a single retrieval.

### 5. Key Takeaway
Multi-part questions that no single chunk answers are the canonical case for query decomposition: it splits the question into sub-queries, retrieves each, and combines them.

---

## Question 14

### 1. Question Summary
**Scenario:** A multi-tenant assistant on a Bedrock knowledge base has two problems: a retrieval is returning chunks belonging to other tenants (an access-control leak), and a separate query surfaced a 2021 policy when the user clearly asked about the 2024 policy (a relevance problem). The documents come from an Amazon S3 data source.

**Ask:** Which single knowledge base capability addresses BOTH problems, and how is the metadata supplied?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ❌ Amazon Bedrock Guardrails, which scrub the retrieved chunks so other tenants' content and outdated policies are removed
- **B** ✅ Metadata filtering at query time on attributes such as tenant ID and year, with metadata supplied via per-file .metadata.json sidecar files (each ≤ 10 KB) for the S3 source
- **C** ❌ Reranking, which reorders results so only the current tenant's 2024 chunks reach the top
- **D** ❌ Increasing numberOfResults so the correct tenant and year chunks are guaranteed to be included

### 4. Correct Answer Deep-Dive
**Answer: B**

Metadata filtering pre-filters the candidate set before semantic search, simultaneously enforcing access control (scope to the user's tenant) and sharpening relevance (restrict to year 2024). For an S3 source, metadata is supplied via per-file .metadata.json sidecar files, each 10 KB or smaller. A is the classic trap: Guardrails apply to input and generated output, NOT to retrieved reference chunks, so they cannot fix a tenant leak in retrieval. C and D do not enforce access control — other tenants' chunks remain eligible.

### 5. Key Takeaway
Metadata filtering pre-filters the candidate set before semantic search, simultaneously enforcing access control (scope to the user's tenant) and sharpening relevance (restrict to year 2024).

---

## Question 15

### 1. Question Summary
**Scenario:** A pricing chatbot built on a Bedrock knowledge base keeps returning confident, well-cited answers that quote last year's prices, even though the source documents in S3 were updated weeks ago. The retrieval and generation pipeline shows no errors and the citations look authoritative. Going forward the business will tolerate a fixed nightly refresh cadence.

**Ask:** What is the root cause, and which refresh architecture is the simplest fit for the stated cadence?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ❌ A Guardrail is filtering out the new prices; disable the guardrail and the current prices will appear
- **B** ✅ Stale retrieval — the index was never re-synced after the S3 documents changed; run StartIngestionJob (incremental) and automate it with EventBridge Scheduler invoking a Lambda that calls StartIngestionJob
- **C** ❌ The embedding dimension is too small; re-embed the corpus at a higher dimension to capture the new prices
- **D** ❌ numberOfResults is too low; raise it so the new price chunks are returned

### 4. Correct Answer Deep-Dive
**Answer: B**

This is the stale-retrieval failure mode: RAG only stays current if the index reflects the source, and grounding plus citations mask out-of-date chunks. The fix is an incremental StartIngestionJob, and because a nightly cadence is acceptable, the simplest architecture is the scheduled pattern: EventBridge Scheduler → Lambda → StartIngestionJob. A is wrong (guardrails act on input/output, not data freshness). C and D address retrieval quality, not freshness — the new content was never ingested.

### 5. Key Takeaway
This is the stale-retrieval failure mode: RAG only stays current if the index reflects the source, and grounding plus citations mask out-of-date chunks.

---

