# AIP-C01 Practice Exam 1 — Analysis (Q41-Q45)

## Question 41

### 1. Question Summary
**Scenario:** A healthcare summarization service on Bedrock must (1) reduce hallucinations by ensuring summaries are supported by the supplied clinical note, and (2) return a strictly parseable JSON object with fixed fields so a downstream EHR system can ingest it without custom parsing. The team is using Anthropic Claude through the Converse API.

**Ask:** Which TWO controls together best meet both requirements? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.1

### 3. Option Analysis
- **A** ✅ Enable Bedrock Guardrails contextual grounding checks with a grounding threshold to block summaries not supported by the clinical note
- **B** ✅ Use Bedrock structured outputs (JSON Schema output format via outputConfig.textFormat) to constrain the response to the required shape
- **C** ❌ Enable citations on the Claude call together with the JSON Schema output format so the EHR system gets both provenance and structure
- **D** ❌ Set the content-filter Prompt Attack strength to HIGH to prevent the model from fabricating clinical facts
- **E** ❌ Use a denied topic named Hallucination to block any response that introduces unsupported information

### 4. Correct Answer Deep-Dive
**Answer: A, B**

Correct: contextual grounding scores the summary against the supplied source and blocks ungrounded (hallucinated) content, directly addressing requirement 1; structured outputs via JSON Schema constrain the response shape so the EHR can parse it deterministically, addressing requirement 2. C is wrong because for Anthropic models structured outputs and citations are mutually exclusive — requesting both in one call returns a 400 error. D is wrong: the Prompt Attack filter targets injection/jailbreak, not fabrication of facts. E is a misuse of denied topics, which block subject themes by name/definition, not the abstract property of being unsupported.

### 5. Key Takeaway
Correct: contextual grounding scores the summary against the supplied source and blocks ungrounded (hallucinated) content, directly addressing requirement 1; structured outputs via JSON Schema constrain the response shape so the EHR can parse it deterministically, addressing requirement 2.

---

## Question 42

### 1. Question Summary
**Scenario:** A security team needs to determine, before any data is ingested into a vector store, which of several hundred S3 buckets contain credit card numbers, private keys, or other PII. They want continuous, low-cost coverage across the whole estate plus the option to run a deeper scan on a few specific buckets.

**Ask:** Which service and approach should they use?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.2

### 3. Option Analysis
- **A** ❌ Amazon Comprehend DetectPiiEntities run against each object to return entity types and offsets
- **B** ✅ Amazon Macie — automated sensitive data discovery for continuous estate-wide sampling, plus targeted discovery jobs for the specific buckets
- **C** ❌ An Amazon Bedrock guardrail with the sensitive information filter applied to each bucket
- **D** ❌ AWS KMS customer-managed keys with key-usage auditing through CloudTrail

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: Macie is the S3 sensitive-data discovery and classification service. Automated sensitive data discovery continuously samples objects across the estate at low cost, and targeted (scheduled) discovery jobs run deeper analysis on chosen buckets. A is wrong: Comprehend detects PII in a given block of text and is not the tool for mapping an entire S3 estate. C is wrong: a guardrail is an inline model-boundary control that never scans buckets. D encrypts data but tells you nothing about what the buckets contain. The chain is Macie discovers, Comprehend redacts, KMS encrypts.

### 5. Key Takeaway
Correct: Macie is the S3 sensitive-data discovery and classification service.

---

## Question 43

### 1. Question Summary
**Scenario:** A bank fine-tunes a Bedrock model on years of historical customer-support transcripts. A reviewer objects, citing PII risk. The project lead replies: "Bedrock does not train its base foundation models on our data, our data is not shared with the model provider, and customization produces a private copy — so the PII in the transcripts is safe."

**Ask:** Why is the project lead's reasoning flawed, and what is the correct mitigation?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.2

### 3. Option Analysis
- **A** ❌ It is not flawed; the base-model and private-copy guarantees fully cover the fine-tuning data
- **B** ✅ A fine-tuned model can memorize and later replay its training data, so PII can resurface in outputs; redact the PII (Comprehend) and discover it (Macie) before it enters the training set
- **C** ❌ Bedrock shares fine-tuning data with the model provider, so the data must be encrypted in transit before the job
- **D** ❌ Fine-tuning data is retained by Bedrock after the job, so an S3 Lifecycle policy must delete it

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: the base-model training guarantee and the private-copy isolation are true, but they protect against the foundation model leaking your data — not against your own fine-tuned model memorizing and replaying training data, which can surface PII in outputs. The mitigation is upstream: discover with Macie and redact with Comprehend before customization. A repeats the lead's error. C is false — your data is not shared with model providers (it runs in an isolated AWS-managed deep copy). D is false — customization data is encrypted and is not retained by Bedrock after the job completes.

### 5. Key Takeaway
Correct: the base-model training guarantee and the private-copy isolation are true, but they protect against the foundation model leaking your data — not against your own fine-tuned model memorizing and replaying training data, which can surface PII in outputs.

---

## Question 44

### 1. Question Summary
**Scenario:** A healthcare company serving EU patients must guarantee that Bedrock inference data does not leave the European Union, must be able to rotate and audit the key protecting its Knowledge Base, and must automatically delete stored conversation transcripts after 90 days.

**Ask:** Which set of controls satisfies all three requirements?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.2

### 3. Option Analysis
- **A** ❌ A global cross-Region inference profile; an AWS owned key on the Knowledge Base; an S3 Cross-Region Replication rule for the transcripts
- **B** ✅ A geographic (EU) cross-Region inference profile enforced with an aws:RequestedRegion SCP; a customer-managed KMS key on the Knowledge Base; an S3 Lifecycle expiration policy on the transcript bucket
- **C** ❌ A geographic (EU) cross-Region inference profile; an AWS owned key on the Knowledge Base; an S3 Lifecycle policy that transitions transcripts to Glacier after 90 days
- **D** ❌ AWS PrivateLink endpoints in every EU Region; an AWS owned key; manual deletion of transcripts every quarter

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: a geographic EU inference profile bounds in-transit cross-Region routing to the EU (data at rest already stays in the source Region), and an aws:RequestedRegion SCP denies non-EU Regions; a customer-managed KMS key gives rotation and CloudTrail-auditable key usage; an S3 Lifecycle expiration policy deletes transcripts after 90 days. A fails on all three (global profile is broad, AWS owned key cannot be audited/rotated by you, CRR copies rather than deletes). C uses an AWS owned key (not auditable/rotatable by you) and transitions to Glacier rather than deleting. D uses an AWS owned key and relies on manual deletion rather than automated expiration.

### 5. Key Takeaway
Correct: a geographic EU inference profile bounds in-transit cross-Region routing to the EU (data at rest already stays in the source Region), and an aws:RequestedRegion SCP denies non-EU Regions; a customer-managed KMS key gives rotation and CloudTrail-auditable key usage; an S3 Lifecycle expiration policy deletes transcripts after 90 days.

---

## Question 45

### 1. Question Summary
**Scenario:** A platform team is hardening IAM for a Bedrock workload. The runtime application calls Anthropic Claude through the Converse API and must be restricted to Anthropic models only. A separate administrator role manages guardrail configuration and invocation logging. The team also enforces a mandatory guardrail on direct invocations using the bedrock:GuardrailIdentifier condition key (Allow on StringEquals plus Deny on StringNotEquals).

**Ask:** Which TWO statements are correct about this design? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.2

### 3. Option Analysis
- **A** ✅ Granting the runtime role bedrock:InvokeModel scoped to arn:aws:bedrock:*::foundation-model/anthropic.* both authorizes Converse and limits it to Anthropic models
- **B** ❌ The runtime role must be granted a dedicated bedrock:Converse action in addition to bedrock:InvokeModel
- **C** ✅ The administrator role belongs in the control plane and should hold actions such as CreateGuardrail and PutModelInvocationLoggingConfiguration, not InvokeModel
- **D** ❌ The GuardrailIdentifier-enforcing role should also be used for RetrieveAndGenerate so the guardrail covers RAG calls
- **E** ❌ The foundation-model ARN must include the account ID to scope it to the team's account

### 4. Correct Answer Deep-Dive
**Answer: A, C**

Correct A: Converse has no dedicated IAM action — it rides on bedrock:InvokeModel, so scoping InvokeModel to foundation-model/anthropic.* both authorizes Converse and restricts it to the Anthropic family. Correct C: managing guardrails and logging are control-plane (bedrock namespace) actions, which a least-privilege admin role holds without runtime InvokeModel. B is wrong — there is no bedrock:Converse action. D is wrong — RetrieveAndGenerate makes behind-the-scenes InvokeModel calls that do not all carry the guardrail, so the StringNotEquals Deny trips and the call fails; use a separate role. E is wrong — foundation-model ARNs carry no account ID because base models are AWS-owned.

### 5. Key Takeaway
Correct A: Converse has no dedicated IAM action — it rides on bedrock:InvokeModel, so scoping InvokeModel to foundation-model/anthropic.* both authorizes Converse and restricts it to the Anthropic family.

---

