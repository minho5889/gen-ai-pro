# AIP-C01 Practice Exam 2 — Analysis (Q36-Q40)

## Question 36

### 1. Question Summary
**Scenario:** An ingestion pipeline must extract structured fields from scanned PDF contracts, transcribe and summarize call-center audio recordings, and produce summaries from product videos. The current proposal stitches together Amazon Textract, Amazon Transcribe, Amazon Rekognition, and a separate summarization model with custom glue code. The team wants a simpler, unified approach and asks which Bedrock Data Automation (BDA) API to use for the video and audio content.

**Ask:** Which statement is correct for this multimodal pipeline?

### 2. Domain Mapping
**Domain:** 2.5 Application integration and dev tools - Bedrock Data Automation
**Task:** Task 2.5

### 3. Option Analysis
- **A** ❌ Use the synchronous InvokeDataAutomation API for the video and audio content to get lowest latency
- **B** ✅ Use InvokeDataAutomationAsync, which handles documents, audio, video, and images through one unified API, replacing the stitched-together Textract/Transcribe/Rekognition pipeline
- **C** ❌ BDA cannot process audio or video, so the Textract/Transcribe/Rekognition stitching must be kept
- **D** ❌ Route everything through Bedrock Knowledge Bases with the default text parser, since BDA does not support PII redaction

### 4. Correct Answer Deep-Dive
**Answer: B**

InvokeDataAutomationAsync is asynchronous and handles all modalities (audio, video, image, document) through one unified API with EventBridge completion notifications, and BDA's unified multimodal API is the GenAI-era replacement for stitching Textract + Transcribe + Rekognition + a summarizer. The synchronous InvokeDataAutomation (A) supports only images, so it is wrong for video and audio. BDA does process audio and video (C is false). BDA does support per-modality PII detection/redaction and can even serve as a Knowledge Base parser, so D is false on both counts.

### 5. Key Takeaway
InvokeDataAutomationAsync is asynchronous and handles all modalities (audio, video, image, document) through one unified API with EventBridge completion notifications, and BDA's unified multimodal API is the GenAI-era replacement for stitching Textract + Transcribe + Rekognition + a summarizer.

---

## Question 37

### 1. Question Summary
**Scenario:** Through an IaC pipeline, an engineer updates a production Bedrock Agent's action group and instructions, deploys the change, and the application (which invokes the agent through its production alias) sees no behavioral change at all. The pipeline updated the agent configuration but the new behavior never took effect.

**Ask:** Which step was almost certainly skipped in the agent deployment flow?

### 2. Domain Mapping
**Domain:** 2.5 Application integration and dev tools - CI/CD for agents
**Task:** Task 2.5

### 3. Option Analysis
- **A** ❌ Restarting the action-group Lambda function so it picks up the new instructions
- **B** ✅ Calling PrepareAgent to rebuild and package the DRAFT, then creating a new immutable version and repointing the production alias to it
- **C** ❌ Increasing the agent's memory size to accommodate the new instructions
- **D** ❌ Re-creating the TSTALIASID test alias before deploying to production

### 4. Correct Answer Deep-Dive
**Answer: B**

Changes to a Bedrock Agent's instructions, action groups, or Knowledge Base associations do not take effect until PrepareAgent rebuilds and packages the DRAFT (status PREPARING to PREPARED), after which you cut a new immutable version and repoint the production alias to it. Omitting Prepare-plus-version-plus-alias-repoint is the classic agent CI/CD trap and exactly matches 'config updated but no behavior change.' Restarting the Lambda (A) does not propagate agent-config changes. Memory size (C) is unrelated. Re-creating the test alias (D) does not affect the production alias the app calls.

### 5. Key Takeaway
Changes to a Bedrock Agent's instructions, action groups, or Knowledge Base associations do not take effect until PrepareAgent rebuilds and packages the DRAFT (status PREPARING to PREPARED), after which you cut a new immutable version and repoint the production alias to it.

---

## Question 38

### 1. Question Summary
**Scenario:** A reasoning-capable model on Amazon Bedrock is used by a legal-research assistant. The team attaches a guardrail with content filters and a denied-topics policy and confirms it blocks unsafe final answers. During red-teaming, a tester notices that the chain-of-thought the model emits before its final answer occasionally contains disallowed content (e.g., a denied topic) even though the visible answer is clean. The team assumed the guardrail would also screen this intermediate reasoning.

**Ask:** Why is the disallowed content appearing in the model's reasoning despite the guardrail, and what is the correct way to characterize this gap?

### 2. Domain Mapping
**Domain:** 3.1 Input and output safety controls
**Task:** Task Task 3.1

### 3. Option Analysis
- **A** ✅ Guardrails evaluate user inputs and model responses but do not evaluate the model's internal reasoning content blocks, so the 'thinking' the model emits before its answer is outside the guardrail's inspection boundary
- **B** ❌ The guardrail's content filters were set to LOW strength, which only blocks high-confidence content; raising them to HIGH will screen the reasoning blocks
- **C** ❌ Denied topics apply only to inputs, not outputs, so the reasoning passed through; switching the policy to evaluate output will close the gap
- **D** ❌ Reasoning content is encrypted by the model and can only be screened by enabling Automated Reasoning checks on the guardrail

### 4. Correct Answer Deep-Dive
**Answer: A**

A guardrail evaluates user inputs and model responses but explicitly does not inspect the model's internal reasoning/thinking content blocks emitted before the final answer. B is a real knob but irrelevant: strength tuning cannot make the guardrail inspect a region it structurally does not evaluate. C is false because denied topics apply to both input and output; the output was clean, the reasoning was not. D conflates Automated Reasoning (a formal-logic policy validating answers against encoded rules) with inspecting reasoning blocks, which it does not do.

### 5. Key Takeaway
A guardrail evaluates user inputs and model responses but explicitly does not inspect the model's internal reasoning/thinking content blocks emitted before the final answer.

---

## Question 39

### 1. Question Summary
**Scenario:** A high-traffic content-moderation pipeline must screen a large stream of user-submitted comments. Each comment is run through a sequence: an Amazon Comprehend toxicity score, a custom Lambda business-rule check, and a Bedrock model call to generate a moderation decision. There is no human reviewer in the path, each execution completes in well under a minute, and the system must sustain a very high invocation rate at the lowest cost for this short-duration event processing.

**Ask:** Which orchestration choice best fits these requirements?

### 2. Domain Mapping
**Domain:** 3.1 Input and output safety controls
**Task:** Task Task 3.1

### 3. Option Analysis
- **A** ✅ An AWS Step Functions Express workflow invoking the Comprehend, Lambda, and Bedrock steps
- **B** ❌ An AWS Step Functions Standard workflow with a human-approval step on every comment
- **C** ❌ A single Amazon Bedrock guardrail with all six policy types enabled, called once per comment
- **D** ❌ A single Lambda function that calls the three services sequentially with no orchestrator

### 4. Correct Answer Deep-Dive
**Answer: A**

Express workflows are built for high-volume, short-duration (up to five minutes) event processing at very high invocation rates and lowest cost, with no human-in-the-loop — exactly this scenario. B is wrong because Standard's durability and human-approval pause are unneeded here and Standard is the wrong cost/throughput profile for high-volume short events. C cannot sequence multiple distinct services or branch — a guardrail is one uniform policy evaluation. D technically chains the calls but lacks the managed state, retry, and observability of Step Functions, and the scenario explicitly describes the Express workflow profile.

### 5. Key Takeaway
Express workflows are built for high-volume, short-duration (up to five minutes) event processing at very high invocation rates and lowest cost, with no human-in-the-loop — exactly this scenario.

---

## Question 40

### 1. Question Summary
**Scenario:** A developer building a RAG summarization feature on Anthropic Claude via the Converse API needs two things at once: the response must conform to a fixed JSON Schema so a downstream service can parse it without custom code, and the response must include inline citations back to the source passages for an audit requirement. Every call returns a 400 error.

**Ask:** What is the most likely cause of the 400 error, and what is the correct resolution?

### 2. Domain Mapping
**Domain:** 3.1 Input and output safety controls
**Task:** Task Task 3.1

### 3. Option Analysis
- **A** ✅ For Anthropic models, structured outputs and citations are mutually exclusive; the developer must choose one — keep citations and parse manually, or drop citations and enforce the JSON Schema
- **B** ❌ The JSON Schema exceeds the 100,000-character grounding-source limit; splitting the schema across multiple calls resolves it
- **C** ❌ Converse does not support JSON Schema output; the developer must switch to InvokeModel, which allows both citations and schemas together
- **D** ❌ Citations require Automated Reasoning checks to be enabled on a guardrail, and enabling that guardrail will allow both features

### 4. Correct Answer Deep-Dive
**Answer: A**

For Anthropic models on Bedrock, structured outputs and citations are mutually exclusive — requesting both in the same call returns a 400. B invents a limit that applies to contextual grounding sources, not schemas; schema-related 400s come from unsupported Draft 2020-12 features, not size. C is false — Converse supports the JSON Schema output format via outputConfig.textFormat, and switching API does not lift the citations conflict. D fabricates a dependency between citations and Automated Reasoning.

### 5. Key Takeaway
For Anthropic models on Bedrock, structured outputs and citations are mutually exclusive — requesting both in the same call returns a 400.

---

