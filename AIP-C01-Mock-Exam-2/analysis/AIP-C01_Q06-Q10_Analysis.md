# AIP-C01 Practice Exam 2 — Analysis (Q06-Q10)

## Question 6

### 1. Question Summary
**Scenario:** A RAG application deployed exclusively in the us-east-1 (N. Virginia) Region retrieves the right chunk but often ranks it below the top results that reach the prompt. The team decides to add a reranking pass to reorder candidates by true relevance before generation.

**Ask:** Which reranker model can they use in this Region?

### 2. Domain Mapping
**Domain:** Task 1.5 — Retrieval (reranking, Region trap)
**Task:** Task 1.5

### 3. Option Analysis
- **A** ✅ Cohere Rerank 3.5
- **B** ❌ Amazon Rerank 1.0
- **C** ❌ Amazon Titan Rerank V2
- **D** ❌ Either Amazon Rerank 1.0 or Cohere Rerank 3.5 — both are available everywhere

### 4. Correct Answer Deep-Dive
**Answer: A**

Reranking is the correct tool when the best chunk is retrieved but ranked too low. The Region trap is that Amazon Rerank 1.0 is not available in us-east-1; only Cohere Rerank 3.5 is offered there. B is therefore unavailable in this Region. C is not a real Bedrock reranker model. D is false because of the us-east-1 availability gap for Amazon Rerank 1.0.

### 5. Key Takeaway
Reranking is the correct tool when the best chunk is retrieved but ranked too low.

---

## Question 7

### 1. Question Summary
**Scenario:** A developer is building a customer-support assistant on a Bedrock knowledge base. The application must return a finished, grounded natural-language answer with citations, and follow-up questions like "and what about the second option?" must resolve against earlier turns without the application tracking conversation history itself.

**Ask:** Which runtime operation and configuration meets this with the least custom code?

### 2. Domain Mapping
**Domain:** Task 1.4 — Vector stores (Knowledge Bases runtime API)
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ RetrieveAndGenerate, passing a sessionId to use its built-in short-term conversation memory
- **B** ❌ Retrieve, then maintain conversation history in DynamoDB and call InvokeModel separately
- **C** ❌ GenerateQuery with a sessionId to convert each turn into SQL
- **D** ❌ Retrieve with overrideSearchType set to HYBRID and a custom memory layer

### 4. Correct Answer Deep-Dive
**Answer: A**

RetrieveAndGenerate performs the entire RAG flow in one call and returns a grounded answer with citations; passing a sessionId enables its built-in short-term conversation memory so follow-ups resolve against earlier turns with no app-side history tracking. B works but is the manual path — more code and no built-in memory. C (GenerateQuery) is natural-language-to-SQL for structured stores, not conversational document RAG. D returns raw chunks with no generation and no built-in session memory.

### 5. Key Takeaway
RetrieveAndGenerate performs the entire RAG flow in one call and returns a grounded answer with citations; passing a sessionId enables its built-in short-term conversation memory so follow-ups resolve against earlier turns with no app-side history tracking.

---

## Question 8

### 1. Question Summary
**Scenario:** A company wants natural-language questions answered over a sales database in Amazon Redshift through a Bedrock knowledge base. A teammate insists they must first choose an embedding model and tune numberOfResults and hybrid search to get good results.

**Ask:** What is wrong with the teammate's plan?

### 2. Domain Mapping
**Domain:** Task 1.4 — Vector stores (structured store)
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ A structured (SQL) data store uses no embeddings — Bedrock generates SQL via GenerateQuery and runs it against Redshift, so numberOfResults, search type, and metadata filtering do not apply
- **B** ❌ Embeddings are required, but Redshift cannot host a vector index, so they must copy the data to OpenSearch Serverless first
- **C** ❌ The plan is correct; structured stores use the same vector retrieval knobs as unstructured sources
- **D** ❌ They must enable binary vectors because Redshift only supports 1-bit embeddings

### 4. Correct Answer Deep-Dive
**Answer: A**

A structured data store works fundamentally differently from the embeddings path: there is no vector index. Bedrock generates SQL from the natural-language question (GenerateQuery) and executes it against Redshift as the query engine, so the vector-path knobs — numberOfResults, semantic/hybrid search type, metadata filtering — simply do not exist. B and D apply embeddings concepts that do not pertain to the structured path. C is the misconception the question targets.

### 5. Key Takeaway
A structured data store works fundamentally differently from the embeddings path: there is no vector index.

---

## Question 9

### 1. Question Summary
**Scenario:** An engineer set a data source's dataDeletionPolicy to DELETE on a knowledge base whose vectors live in a self-provisioned Amazon OpenSearch Serverless collection. They plan to delete the knowledge base and believe this will also tear down the OpenSearch Serverless collection, saving them a cleanup step.

**Ask:** What actually happens when they delete the knowledge base?

### 2. Domain Mapping
**Domain:** Task 1.4 — Vector stores (data deletion policy)
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ Bedrock deletes only the embedded data it wrote into the store; it never deletes the underlying vector store (the OpenSearch Serverless collection), which the engineer must remove separately
- **B** ❌ Bedrock deletes both the embeddings and the OpenSearch Serverless collection automatically
- **C** ❌ Bedrock retains the embeddings regardless of policy and deletes the collection
- **D** ❌ DELETE blocks the knowledge base deletion until the collection is emptied manually

### 4. Correct Answer Deep-Dive
**Answer: A**

Under DELETE, Bedrock removes the embedded data it created in the vector store when the knowledge base or data source is deleted — but it never deletes the underlying store itself. The OpenSearch Serverless collection is a resource the engineer owns and must clean up separately. RETAIN would leave even the embeddings in place. B is the common misconception. C and D misstate the policy behavior.

### 5. Key Takeaway
Under DELETE, Bedrock removes the embedded data it created in the vector store when the knowledge base or data source is deleted — but it never deletes the underlying store itself.

---

## Question 10

### 1. Question Summary
**Scenario:** A document-management system emits an event the instant a single contract is updated, and the business needs that one contract reflected in an S3-backed knowledge base within seconds — not on the next nightly batch sync. A full data-source sync that rescans the entire bucket would be far too slow for a single-document change.

**Ask:** Which mechanism fits, and what S3-specific caveat must be handled?

### 2. Domain Mapping
**Domain:** Task 1.4 — Vector stores (freshness / direct ingestion)
**Task:** Task 1.4

### 3. Option Analysis
- **A** ✅ Use IngestKnowledgeBaseDocuments (direct ingestion) for the one document, and also replicate the change in the S3 object so the next StartIngestionJob sync does not overwrite it
- **B** ❌ Use StartIngestionJob on each event, since incremental sync only processes the changed file anyway
- **C** ❌ Use IngestKnowledgeBaseDocuments, which automatically writes the change back into the S3 bucket as well
- **D** ❌ Use DeleteKnowledgeBaseDocuments followed by a full sync to force a refresh

### 4. Correct Answer Deep-Dive
**Answer: A**

Direct ingestion (IngestKnowledgeBaseDocuments) pushes a specific document straight into the vector store in one step — the real-time answer when an event tells you exactly what changed. The S3 caveat: direct-ingestion changes are written to the vector store but NOT back into the bucket, so if the object still holds old content the next StartIngestionJob will overwrite the change; you must replicate it in S3 (and avoid running both against the same source simultaneously). B still rescans the whole source per event and hits ingestion quotas. C is false — direct ingestion does not write back to S3. D deletes content rather than updating it and triggers a slow full sync.

### 5. Key Takeaway
Direct ingestion (IngestKnowledgeBaseDocuments) pushes a specific document straight into the vector store in one step — the real-time answer when an event tells you exactly what changed.

---

