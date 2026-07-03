# AIP-C01 Practice Exam 1 — Analysis (Q16-Q20)

## Question 16

### 1. Question Summary
**Scenario:** An operations team wants every change to their S3-backed knowledge base reflected within a few minutes, and they expect bursts of hundreds of file changes during deployments. A junior engineer proposes wiring each S3 event directly to a Lambda that immediately calls StartIngestionJob per event. In load testing the design fails badly under bursts.

**Ask:** Why does the naive design fail, and what is the documented event-driven architecture?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ❌ It fails because Lambda concurrency is too low; raise the reserved concurrency and call StartIngestionJob on every event
- **B** ✅ It fails because Bedrock ingestion quotas are tight and per-Region (about 5 concurrent jobs per account, 1 per KB, 1 per data source, with StartIngestionJob limited to roughly 0.1 RPS); the documented pattern buffers events in SQS and uses a Step Functions state machine to check quota and call StartIngestionJob, waiting and rechecking when capacity is unavailable
- **C** ❌ It fails because S3 event notifications cannot trigger EventBridge; use S3 Lifecycle policies to trigger the sync instead
- **D** ❌ It fails because StartIngestionJob is synchronous; switch to IngestKnowledgeBaseDocuments for every changed file and skip buffering entirely

### 4. Correct Answer Deep-Dive
**Answer: B**

Bedrock's ingestion quotas are tight and per-Region (~5 concurrent jobs/account, 1/KB, 1/data source; StartIngestionJob ~0.1 RPS), so firing a sync per event under a burst immediately hits the limits. The documented reference architecture buffers with SQS and orchestrates with Step Functions that checks the quota and calls StartIngestionJob (waiting/rechecking when busy). A misattributes the failure to Lambda concurrency. C is false (S3 events can route to EventBridge; Lifecycle policies do not trigger syncs). D is wrong: StartIngestionJob is asynchronous (returns 202), and while direct ingestion exists for single known documents, the burst-survivable design is the buffer-and-orchestrate pattern.

### 5. Key Takeaway
Bedrock's ingestion quotas are tight and per-Region (~5 concurrent jobs/account, 1/KB, 1/data source; StartIngestionJob ~0.1 RPS), so firing a sync per event under a burst immediately hits the limits.

---

## Question 17

### 1. Question Summary
**Scenario:** A company wants a knowledge base that answers plain-English questions over a sales database in Amazon Redshift. A teammate insists the first steps are to pick an embedding model, tune numberOfResults, and enable hybrid search, just as they did for their document-based knowledge base.

**Ask:** What is wrong with the teammate's plan, and what is the correct configuration path?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.4

### 3. Option Analysis
- **A** ❌ Nothing is wrong; structured stores use the same embedding and vectorSearchConfiguration knobs as document stores
- **B** ✅ A structured store uses no embeddings — Bedrock generates SQL from the question (GenerateQuery) and runs it on Redshift; numberOfResults, search type, and metadata filtering do not apply. Configure the query engine (Redshift Provisioned or Serverless), the storage config, and optionally query generation (table/column descriptions, curated NL-to-SQL examples)
- **C** ❌ Structured stores require binary vectors, so they must use OpenSearch Serverless rather than Redshift
- **D** ❌ Structured stores require hierarchical chunking of the database rows before querying

### 4. Correct Answer Deep-Dive
**Answer: B**

A structured data source uses no embeddings or vector index; Bedrock generates SQL via GenerateQuery and runs it against Redshift, so the vector-path knobs (numberOfResults, semantic/hybrid search, metadata filtering) simply do not exist. The correct work is the structured-store path: query engine (Redshift Provisioned/Serverless), storage config (Redshift databases or Glue Data Catalog), and optional query-generation tuning (descriptions, inclusions/exclusions, curated queries). A applies the wrong playbook. C and D invent embedding/chunking requirements that do not apply to the SQL path.

### 5. Key Takeaway
A structured data source uses no embeddings or vector index; Bedrock generates SQL via GenerateQuery and runs it against Redshift, so the vector-path knobs (numberOfResults, semantic/hybrid search, metadata filtering) simply do not exist.

---

## Question 18

### 1. Question Summary
**Scenario:** A platform team manages prompts in Amazon Bedrock Prompt Management. They deployed a customer-summary prompt as version 5 and discovered it produces noticeably lower-quality summaries than version 4. No one can edit version 5, leadership wants the fastest restoration of quality with no new prompt authoring, and a separate developer is failing to invoke a Prompt Management prompt configured for an Amazon Titan model using the InvokeModel API.

**Ask:** Which two statements correctly resolve these issues? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.6

### 3. Option Analysis
- **A** ✅ Update the application's prompt reference ARN from version 5 to version 4 to roll back immediately, since versions are immutable snapshots
- **B** ✅ Invoke the Titan-configured managed prompt with the Converse API; InvokeModel supports only Claude/Llama managed prompts
- **C** ❌ Delete version 5 and recreate version 4 to restore quality, since deletion is the only rollback path
- **D** ❌ Edit version 5 in place to match version 4, because the working draft and numbered versions are both mutable
- **E** ❌ Add system and inferenceConfig overrides in the InvokeModel request to force the Titan prompt to run

### 4. Correct Answer Deep-Dive
**Answer: A, B**

Numbered versions are immutable snapshots, so the fastest no-authoring rollback is to repoint the reference ARN from :5 to :4 (version 4 still exists unchanged). For the Titan-configured prompt, InvokeModel works only with Claude/Llama managed prompts; Converse is the universal invocation path. C is wrong because you neither need to delete a version nor can you recreate the same numbered version. D is false (versions are immutable). E is false: when invoking a managed prompt you cannot pass system/inferenceConfig/toolConfig/additionalModelRequestFields inline — they are defined in the prompt.

### 5. Key Takeaway
Numbered versions are immutable snapshots, so the fastest no-authoring rollback is to repoint the reference ARN from :5 to :4 (version 4 still exists unchanged).

---

## Question 19

### 1. Question Summary
**Scenario:** A regulated financial-services organization must prove, for any model output that caused a problem, which prompt version produced it, who approved that prompt, and what the full prompt and response looked like. They use Amazon Bedrock Prompt Management with versioned templates and want an end-to-end audit chain. Their security team also wants to control who can create prompt versions.

**Ask:** Which combination establishes the required governance and audit chain? (Select THREE)

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.6

### 3. Option Analysis
- **A** ✅ Use immutable numbered prompt versions (CreatePromptVersion) so each production output traces to an exact, frozen prompt configuration
- **B** ✅ Rely on CloudTrail management events (logged by default) to record who called CreatePrompt/CreatePromptVersion and when, and enable RenderPrompt data events to tie a specific prompt version to each invocation
- **C** ✅ Enable Bedrock Model Invocation Logging (off by default) to capture the full rendered prompt and model response for each invocation
- **D** ❌ Rely on Bedrock Guardrails to record which prompt version produced each output, since guardrails log the prompt lineage
- **E** ❌ Store all prompts as string literals in Lambda code and use Git history as the production audit trail
- **F** ❌ Use prompt variants as the immutable production artifacts, since variants persist for long-term audit

### 4. Correct Answer Deep-Dive
**Answer: A, B, C**

The audit chain is: immutable versions (A) give a frozen, traceable prompt-to-output link; CloudTrail management events record who created/promoted prompts by default, and RenderPrompt data events connect a specific prompt version to each invocation (B); Model Invocation Logging (off by default) captures the full rendered prompt and response (C). D is wrong — Guardrails is a safety control, not a prompt-lineage logger. E reintroduces prompt sprawl and is not an AWS-native traceable chain. F is wrong because variants are transient experimentation artifacts, not immutable versions.

### 5. Key Takeaway
The audit chain is: immutable versions (A) give a frozen, traceable prompt-to-output link; CloudTrail management events record who created/promoted prompts by default, and RenderPrompt data events connect a specific prompt version to each invocation (B); Model Invocation Logging (off by default) captures the full rendered prompt and response (C).

---

## Question 20

### 1. Question Summary
**Scenario:** A pipeline prompts a Bedrock model for JSON used by a downstream API. Roughly one call in twenty returns a trailing comma or a wrapping sentence, breaking the parser and forcing a retry. The team also has a business rule that a returned rating field must be an integer between 1 and 5, and they must prevent toxic or PII content from leaving the system. A teammate suggests using a Bedrock Guardrail to guarantee valid JSON.

**Ask:** Which layered approach correctly meets all three needs (well-formed JSON, the 1–5 rating rule, and safety)?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.6

### 3. Option Analysis
- **A** ❌ Use a Bedrock Guardrail to enforce valid JSON and the 1–5 range, and add a longer system prompt for safety
- **B** ✅ Use Structured outputs (a JSON Schema output format or strict tool use) to enforce structure, add application-side validation for the 1–5 range that the schema subset cannot express, and use Bedrock Guardrails for toxicity/PII safety
- **C** ❌ Raise temperature and add more few-shot examples so the JSON is always valid and within range, and rely on the parser to catch unsafe content
- **D** ❌ Use application-side validation alone to enforce structure, range, and safety, since code can check everything deterministically

### 4. Correct Answer Deep-Dive
**Answer: B**

These are layered, complementary controls. Structured outputs (JSON Schema output format or strict tool use) enforces structure, eliminating the parse-and-retry loop. The JSON Schema subset excludes numeric range constraints (minimum/maximum), so application-side validation enforces the 1–5 rule the schema cannot express. Guardrails is the safety/content layer for toxicity and PII — it does NOT guarantee JSON validity. A is the classic trap (Guardrails cannot enforce JSON/range). C raises non-determinism (the opposite of what is needed) and cannot guarantee structure or safety. D cannot prevent bad output (validation only catches it after the fact) and is not a content-safety control.

### 5. Key Takeaway
These are layered, complementary controls.

---

