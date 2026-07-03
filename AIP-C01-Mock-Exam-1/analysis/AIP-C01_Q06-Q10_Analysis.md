# AIP-C01 Practice Exam 1 — Analysis (Q06-Q10)

## Question 6

### 1. Question Summary
**Scenario:** An application sends prompts to a Bedrock model through an ingestion-and-inference pipeline. Intermittently it receives ValidationException errors. The on-call engineer added retry-with-exponential-backoff logic, but the same requests keep failing identically on every retry, wasting quota.

**Ask:** What is the actual root cause and the correct fix?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.3

### 3. Option Analysis
- **A** ❌ The model is throttled; increase the backoff window and add jitter so the retries eventually succeed
- **B** ✅ ValidationException is a non-retryable client error from malformed input; fix the pipeline's input-formatting step so requests conform to the expected Bedrock JSON/content-block structure
- **C** ❌ The account hit its Model Unit quota; request a quota increase through AWS Support
- **D** ❌ The cross-Region inference profile has a blocked destination Region; update the SCP to allow it

### 4. Correct Answer Deep-Dive
**Answer: B**

ValidationException is a client error caused by a structurally invalid request, so it fails deterministically on every retry — backoff cannot help. The fix lives in the input-formatting step (Skill 1.3.3): assemble the correct Bedrock JSON/content-block shape before sending. A misreads a client error as throttling. C addresses provisioned-capacity, unrelated to a malformed body. D is the symptom of a blocked destination Region (AccessDenied), not a malformed-input ValidationException.

### 5. Key Takeaway
ValidationException is a client error caused by a structurally invalid request, so it fails deterministically on every retry — backoff cannot help.

---

## Question 7

### 1. Question Summary
**Scenario:** A team is selecting an embedding model and a vector store together for a new RAG system. To cut vector-storage cost aggressively, they want to use Amazon Titan Text Embeddings V2 binary vectors, accepting some precision loss. They had planned to store the vectors in Amazon Aurora PostgreSQL with pgvector because the team already runs Aurora.

**Ask:** What is the problem with this plan, and what are the valid ways to resolve it? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ Switch the vector store to Amazon OpenSearch Serverless (or OpenSearch Managed), the only stores that support binary vectors
- **B** ✅ Keep Aurora pgvector but store float32 vectors instead, for example a lower Titan V2 dimension such as 256 to cut storage with minimal accuracy loss
- **C** ❌ Keep Aurora and binary vectors; pgvector supports binary embeddings once the extension is upgraded
- **D** ❌ Use Amazon S3 Vectors, which is the lowest-cost store and therefore supports binary vectors
- **E** ❌ Convert the binary vectors to float32 at query time so Aurora can compare them with the binary index

### 4. Correct Answer Deep-Dive
**Answer: A, B**

Binary vectors are supported only on OpenSearch Serverless and OpenSearch Managed; every other Bedrock-supported store (including Aurora pgvector and S3 Vectors) holds float32 only. So the two valid resolutions are: move to an OpenSearch store to keep binary, or stay on Aurora and use float32 (a lower Titan V2 dimension like 256 retains ~97% accuracy at ~75% less storage). C is false (pgvector does not store binary in this context). D is false (S3 Vectors is float32 only despite being cheapest). E is incoherent — there is no binary index in Aurora to compare against.

### 5. Key Takeaway
Binary vectors are supported only on OpenSearch Serverless and OpenSearch Managed; every other Bedrock-supported store (including Aurora pgvector and S3 Vectors) holds float32 only.

---

## Question 8

### 1. Question Summary
**Scenario:** A legal-tech firm needs RAG over millions of contracts and clauses. The most valuable queries are multi-hop questions that follow relationships between connected documents (how a clause in one contract is affected by clauses in related contracts), and the firm wants more explainable, lower-hallucination answers. Their source documents live in Amazon S3.

**Ask:** Which vector store best fits these requirements?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ❌ Amazon S3 Vectors, because it is the lowest-cost store for millions of vectors
- **B** ❌ Amazon OpenSearch Serverless, because it gives millisecond latency at billions of vectors
- **C** ✅ Amazon Neptune Analytics (GraphRAG), because it combines vector similarity with graph traversal for multi-hop reasoning over related documents
- **D** ❌ Amazon Aurora PostgreSQL with pgvector, because it stores vectors alongside relational data

### 4. Correct Answer Deep-Dive
**Answer: C**

Neptune Analytics is the GraphRAG option: it pairs vector search with graph traversal so retrieval can follow relationships across connected documents, enabling the multi-hop reasoning and more explainable, lower-hallucination answers the scenario demands; it also works with S3 data sources. S3 Vectors (A) and OpenSearch Serverless (B) retrieve independent passages by similarity but cannot traverse relationships. Aurora pgvector (D) combines SQL and vectors but still does flat similarity, not graph multi-hop.

### 5. Key Takeaway
Neptune Analytics is the GraphRAG option: it pairs vector search with graph traversal so retrieval can follow relationships across connected documents, enabling the multi-hop reasoning and more explainable, lower-hallucination answers the scenario demands; it also works with S3 data sources.

---

## Question 9

### 1. Question Summary
**Scenario:** A company built a cost-optimized RAG system on Amazon S3 Vectors. Two new requirements have surfaced: (1) a customer-facing interactive chat feature with strict millisecond latency, and (2) metadata filter expressions that use the startsWith operator on a document-prefix attribute. The team reports that the startsWith filters fail and latency is too high for the new chat.

**Ask:** Which statement most accurately diagnoses BOTH problems and the correct fix?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ❌ Both issues are bugs; reindex the S3 Vectors store and the filters and latency will be fixed
- **B** ✅ S3 Vectors delivers sub-second (not millisecond) latency and startsWith is unsupported on managed knowledge bases; moving to a custom knowledge base with a bring-your-own OpenSearch Serverless store addresses both the latency and the string-operator requirement
- **C** ❌ Switch from S3 Vectors to the quick-create managed OpenSearch Serverless index; that alone restores both millisecond latency and startsWith filtering
- **D** ❌ Raise numberOfResults and enable hybrid search on S3 Vectors to lower latency and re-enable startsWith

### 4. Correct Answer Deep-Dive
**Answer: B**

S3 Vectors is sub-second (archival/infrequent), not millisecond, so it is wrong for interactive chat; and startsWith/stringContains are unsupported on ANY fully managed knowledge base. The two-sided fix is OpenSearch Serverless for millisecond latency AND bringing your own OpenSearch Serverless store in a custom knowledge base to regain the string operators. A misframes design constraints as bugs. C is the half-right trap: a quick-create managed OpenSearch Serverless index gives millisecond latency but is still a managed KB, so startsWith remains unavailable. D is wrong because S3 Vectors does not support hybrid search and numberOfResults does not cut latency or enable string operators.

### 5. Key Takeaway
S3 Vectors is sub-second (archival/infrequent), not millisecond, so it is wrong for interactive chat; and startsWith/stringContains are unsupported on ANY fully managed knowledge base.

---

## Question 10

### 1. Question Summary
**Scenario:** A team ingests well-structured product manuals (chapters, sections, subsections) into a Bedrock knowledge base. They want precise matches but also enough surrounding context in each answer so users are not handed a fragment. They are also debating whether they can switch the chunking approach later if relevance is poor, since they tend to iterate.

**Ask:** Which statement correctly pairs the best chunking strategy with the change-management reality?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.5

### 3. Option Analysis
- **A** ❌ Use FIXED_SIZE with no overlap because manuals are uniform; the chunking strategy can be edited in place later if relevance is poor
- **B** ✅ Use HIERARCHICAL chunking so child chunks match precisely while parent chunks supply context; the chunking strategy is fixed at data-source creation and cannot be changed in place — switching requires a new data source and re-ingestion
- **C** ❌ Use SEMANTIC chunking because it is always cheapest; you can toggle to HIERARCHICAL later without re-ingesting
- **D** ❌ Use NONE so each manual is one chunk for maximum context; chunking can be reconfigured anytime via UpdateDataSource

### 4. Correct Answer Deep-Dive
**Answer: B**

Hierarchical chunking matches small child chunks for precision then returns their larger parents for context — ideal for sectioned manuals. The governance fact: chunking strategy is immutable after data-source creation; changing it requires a new data source and re-ingestion. A is wrong (no overlap risks cutting context, and chunking is not editable in place). C is wrong (semantic uses an FM and costs more, and you cannot toggle without re-ingesting). D is wrong (NONE stores whole files as single chunks, hurting precision, and chunking is not reconfigurable via UpdateDataSource).

### 5. Key Takeaway
Hierarchical chunking matches small child chunks for precision then returns their larger parents for context — ideal for sectioned manuals.

---

