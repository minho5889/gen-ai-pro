# AIP-C01 Practice Exam 1 — Analysis (Q36-Q40)

## Question 36

### 1. Question Summary
**Scenario:** An ingestion pipeline must extract structured data from scanned PDF contracts, call-recording audio, and product videos. The team currently stitches together Amazon Textract, Amazon Transcribe, and Amazon Rekognition with custom glue plus a summarization model, and wants to simplify to a single managed multimodal service.

**Ask:** Which TWO statements are correct about using Amazon Bedrock Data Automation (BDA) here? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.5

### 3. Option Analysis
- **A** ✅ Use InvokeDataAutomationAsync, because it handles documents, audio, and video and supports EventBridge completion notifications
- **B** ❌ Use the synchronous InvokeDataAutomation API for the video and audio files
- **C** ✅ BDA provides one unified multimodal API that can replace the hand-built Textract + Transcribe + Rekognition pipeline
- **D** ❌ BDA cannot detect or redact PII, so a separate Comprehend step is still required for every modality
- **E** ❌ Each modality must be sent to a different AWS AI service and cannot be processed through one API

### 4. Correct Answer Deep-Dive
**Answer: A, C**

InvokeDataAutomationAsync (A) is the asynchronous BDA API that handles all modalities (document, audio, image, video) and supports EventBridge completion notifications; the synchronous InvokeDataAutomation supports only images, so B is wrong for video and audio. BDA's single unified multimodal API (C) is the GenAI-era replacement for stitching individual AI services. D is false because BDA offers per-modality PII detection and redaction. E is false because consolidating modalities into one API is exactly BDA's purpose.

### 5. Key Takeaway
InvokeDataAutomationAsync (A) is the asynchronous BDA API that handles all modalities (document, audio, image, video) and supports EventBridge completion notifications; the synchronous InvokeDataAutomation supports only images, so B is wrong for video and audio.

---

## Question 37

### 1. Question Summary
**Scenario:** A team deployed an Amazon Bedrock Agent behind an alias that their application invokes. They edited the agent's action group through the console and deployed, but the agent's behavior did not change. Separately, after fixing the issue they ship a new version that misbehaves and need to revert immediately and pause the agent during investigation, all without changing application code or IAM.

**Ask:** Which sequence correctly resolves both the no-effect change and the rollback/pause?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.5

### 3. Option Analysis
- **A** ❌ Restart the action-group Lambda, then delete and recreate the alias to roll back
- **B** ✅ Call PrepareAgent to rebuild the DRAFT, cut a new version, and repoint the alias; to revert, repoint the alias to the prior version and set the alias to REJECT_INVOCATIONS to pause
- **C** ❌ Increase the agent's memory size to apply the config change, then lower the Lambda timeout to pause it
- **D** ❌ Edit the live numbered version in place so the alias automatically picks up both the change and the rollback

### 4. Correct Answer Deep-Dive
**Answer: B**

Agent configuration changes (instructions, action groups, KB associations) take effect only after PrepareAgent rebuilds and packages the DRAFT, followed by cutting a new immutable version and repointing the alias, which is the step that was skipped. To revert, you repoint the movable alias to a prior immutable version (no redeploy, no app/IAM change), and to pause you set the alias aliasInvocationState to REJECT_INVOCATIONS via UpdateAgentAlias. A misidentifies the cause and needlessly deletes the alias. C is unrelated to agent config or pausing. D is impossible because numbered versions are immutable snapshots; you never edit a live version in place.

### 5. Key Takeaway
Agent configuration changes (instructions, action groups, KB associations) take effect only after PrepareAgent rebuilds and packages the DRAFT, followed by cutting a new immutable version and repointing the alias, which is the step that was skipped.

---

## Question 38

### 1. Question Summary
**Scenario:** A RAG-based legal-research assistant on Amazon Bedrock uses a Knowledge Base over a corpus of contracts stored in S3. The team has enabled a Bedrock guardrail with the sensitive information filter (MASK) and contextual grounding checks, attached to RetrieveAndGenerate. In production, the assistant still returns citations that expose client names and account numbers, and on one occasion it acted on an instruction that turned out to be hidden inside a contract PDF that had been ingested months earlier.

**Ask:** Which change most directly addresses BOTH the PII-in-citations leak and the instruction that was buried in a source document?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.1

### 3. Option Analysis
- **A** ❌ Increase the contextual grounding threshold toward 0.99 and raise the content-filter Prompt Attack strength to HIGH so the guardrail blocks both issues at the model boundary
- **B** ✅ Redact PII from the source corpus before ingestion with an Amazon Comprehend redaction job, and screen the retrieved chunks in the pipeline with ApplyGuardrail before they are concatenated into the prompt
- **C** ❌ Switch the guardrail from MASK to BLOCK on the sensitive information filter so any response containing PII is rejected entirely
- **D** ❌ Move the guardrail enforcement to the InvokeModel call instead of RetrieveAndGenerate so it can inspect the retrieved context
- **E** ❌ Enable Model Invocation Logging so the leaked PII and injected instructions are captured for later review

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: the guardrail evaluates the input query and the final answer but never scrubs the retrieved reference chunks in between, which is exactly where both source-document PII and indirect prompt injection live. The fix is data-layer screening (pre-ingestion Comprehend redaction) plus screening the retrieved chunks (ApplyGuardrail) — the two points a guardrail cannot reach. A is the defense-in-depth trap: tuning guardrail thresholds and Prompt Attack strength still only touches input/output, not the retrieved context. C blocks PII in the final answer but does nothing for the unscreened retrieved chunks or the buried instruction. D is wrong because moving to InvokeModel does not make a guardrail inspect retrieved context either; the chunk gap exists regardless of which API the guardrail attaches to. E only records the leak, it does not prevent it.

### 5. Key Takeaway
Correct: the guardrail evaluates the input query and the final answer but never scrubs the retrieved reference chunks in between, which is exactly where both source-document PII and indirect prompt injection live.

---

## Question 39

### 1. Question Summary
**Scenario:** A content-moderation pipeline must run an Amazon Comprehend toxicity score on each user message, then apply an organization-specific business rule in a Lambda function, then invoke a Bedrock model, and finally escalate any response that the business rule flags to a human reviewer who must approve it before it is released. Volume is moderate and some reviews can take hours.

**Ask:** Which design satisfies all of these requirements?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.1

### 3. Option Analysis
- **A** ❌ A single Amazon Bedrock guardrail with all six policy types enabled, attached to the InvokeModel call
- **B** ✅ An AWS Step Functions Standard workflow that sequences the Comprehend, Lambda, and Bedrock steps and uses a human-approval (task token) step to pause until the reviewer responds
- **C** ❌ An AWS Step Functions Express workflow chaining the Comprehend, Lambda, and Bedrock steps with a Choice state that routes flagged content to a human reviewer
- **D** ❌ Two sequential ApplyGuardrail calls, one before and one after the model invocation, with Amazon SNS notifying the reviewer

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: the requirement is orchestration with a human-in-the-loop pause that may last hours. Standard Step Functions workflows are durable (up to one year), support pausing for human approval, and natively sequence multiple service steps. A single guardrail performs one uniform policy evaluation per direction and cannot sequence multiple distinct services, branch, or wait for a human, so A fails. C fails because Express workflows are capped at five minutes and cannot wait hours for a human approval. D is just two evaluation steps with a notification; SNS notifies but provides no mechanism to pause the execution and resume on approval.

### 5. Key Takeaway
Correct: the requirement is orchestration with a human-in-the-loop pause that may last hours.

---

## Question 40

### 1. Question Summary
**Scenario:** A retail bank deploys a customer assistant. Compliance set a content filter to LOW strength for the Violence and Insults categories expecting strong protection, but a significant amount of borderline abusive content still reaches customers. Separately, they need the assistant to refuse to give any specific investment recommendations, and to keep a named competitor brand out of all responses.

**Ask:** Which combination of configuration changes correctly addresses all three concerns?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.1

### 3. Option Analysis
- **A** ✅ Raise the content-filter strength to HIGH for Violence and Insults; use a denied topic for investment recommendations; use a word filter custom list for the competitor brand name
- **B** ❌ Lower the content-filter strength further to NONE for tighter control; use a word filter for investment advice; use a denied topic for the competitor brand name
- **C** ❌ Raise the content-filter strength to HIGH; use a word filter for investment recommendations; use a denied topic for the competitor brand name
- **D** ❌ Keep LOW strength; use the sensitive information filter to mask the competitor name; use contextual grounding to block investment advice

### 4. Correct Answer Deep-Dive
**Answer: A**

Correct: filter strength measures how much is blocked, not model confidence — LOW blocks only HIGH-confidence content and is the least aggressive, so raising to HIGH (which also blocks MEDIUM and LOW confidence) is the fix. Investment recommendations are a subject theme, which is exactly what a denied topic targets. A specific competitor brand name is an individual term, which is a word filter custom-list job. B inverts the scale again (NONE blocks nothing) and swaps the two policy roles. C swaps them as well: a denied topic should hold the theme (investment advice) and the word filter should hold the specific brand name. D leaves strength at the broken LOW setting, misuses the PII filter for a brand name, and misuses grounding (which scores source support, not topic policy).

### 5. Key Takeaway
Correct: filter strength measures how much is blocked, not model confidence — LOW blocks only HIGH-confidence content and is the least aggressive, so raising to HIGH (which also blocks MEDIUM and LOW confidence) is the fix.

---

