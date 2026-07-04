# AIP-C01 Practice Exam 1 — Analysis (Q46-Q50)

## Question 46

### 1. Question Summary
**Scenario:** A Knowledge Base is being assembled with three connections: a Pinecone vector store, a Confluence data source, and an Amazon S3 data source. Security requires that no long-lived credentials be hardcoded anywhere.

**Ask:** For which of these connections is an AWS Secrets Manager secret required?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.2

### 3. Option Analysis
- **A** ❌ All three, because every external connection needs a stored credential
- **B** ✅ Pinecone and Confluence; the S3 data source is governed by IAM and needs no secret
- **C** ❌ Only the S3 data source, because S3 access keys must be stored as a secret
- **D** ❌ Only Pinecone, because vector stores require an API key but SaaS connectors use OAuth handled by Bedrock automatically

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: third-party vector stores (Pinecone, Redis Enterprise Cloud) reference a credentialsSecretArn, and SaaS connectors (Confluence, Salesforce, SharePoint, the web crawler) authenticate with API tokens or OAuth credentials stored in Secrets Manager. The S3 connector is the exception — it is governed by IAM and needs no secret (as are first-party vector stores OpenSearch Serverless and Aurora). A overstates by including S3. C inverts the rule. D wrongly excludes Confluence, which does need a Secrets Manager secret.

### 5. Key Takeaway
Correct: third-party vector stores (Pinecone, Redis Enterprise Cloud) reference a credentialsSecretArn, and SaaS connectors (Confluence, Salesforce, SharePoint, the web crawler) authenticate with API tokens or OAuth credentials stored in Secrets Manager.

---

## Question 47

### 1. Question Summary
**Scenario:** A model-risk team must satisfy two distinct governance asks for the same financial-advisory model. First, they need AWS's own documented statement of an Amazon Nova model's intended uses and limitations. Second, they must produce their own internal governance document for a custom model they fine-tuned, recording its intended uses, a risk rating, and evaluation results, with an immutable change history for auditors.

**Ask:** Which artifacts correctly satisfy the two asks respectively?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.3

### 3. Option Analysis
- **A** ❌ Create an AWS AI Service Card for Nova; read a SageMaker Model Card AWS publishes for the custom model
- **B** ✅ Read the AWS AI Service Card AWS publishes for Nova; create a SageMaker Model Card for the custom model
- **C** ❌ Read a SageMaker Model Card for Nova; create an AWS AI Service Card for the custom model
- **D** ❌ Use Bedrock Guardrails documentation for Nova; use Bedrock Model Evaluation reports as the custom model's governance document

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: AWS AI Service Cards are authored by AWS for AWS services/models — you read the Nova service card. SageMaker Model Cards are customer-authored governance documents for your own model, with a risk-rating field (unknown/low/medium/high), evaluation results, and immutable version history — so you create one for the fine-tuned model. A reverses authorship for both (you do not create a Service Card, AWS does not publish a Model Card for your custom model). C reverses both as well. D conflates documentation/evaluation tooling with the transparency artifacts the asks require.

### 5. Key Takeaway
Correct: AWS AI Service Cards are authored by AWS for AWS services/models — you read the Nova service card.

---

## Question 48

### 1. Question Summary
**Scenario:** A compliance team needs three things for a Bedrock chatbot: (1) review the exact text of past prompts and completions, (2) a tamper-detection alert when a user signing in from an unusual location deletes a guardrail or repoints the training-data S3 bucket, and (3) a real-time alarm when blocked/unsafe content spikes. They confirm CloudTrail is active but find no prompt text anywhere.

**Ask:** Which mapping of capabilities to the three needs is correct?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.3

### 3. Option Analysis
- **A** ❌ (1) Enable CloudTrail data events to capture prompt text; (2) CloudWatch alarm on InvocationsIntervened; (3) Model Invocation Logging
- **B** ✅ (1) Model Invocation Logging (off by default — enable it; only it captures prompt/response content); (2) CloudTrail management-event records analyzed by Amazon GuardDuty; (3) CloudWatch alarm on InvocationsIntervened
- **C** ❌ (1) CloudTrail Event history, which retains prompt bodies for 90 days; (2) AWS Config rules; (3) Model Invocation Logging metric filters
- **D** ❌ (1) CloudWatch Logs Insights query over invocation metrics; (2) Model Invocation Logging; (3) CloudTrail data events

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: Model Invocation Logging is the only service that captures prompt/completion content and is disabled by default, explaining the missing text. Deleting a guardrail and repointing a bucket are control-plane management actions that CloudTrail records; GuardDuty analyzes CloudTrail events to flag suspicious Bedrock activity like a tamper action from an unfamiliar location. A spike in blocked content is the InvocationsIntervened metric, alarmed in CloudWatch. A is wrong because CloudTrail data events still never contain prompt content, and it misorders the other two. C is wrong — CloudTrail never stores prompt bodies, and Config does not provide threat detection. D misassigns all three.

### 5. Key Takeaway
Correct: Model Invocation Logging is the only service that captures prompt/completion content and is disabled by default, explaining the missing text.

---

## Question 49

### 1. Question Summary
**Scenario:** A data-governance lead must, for a RAG application, (a) maintain a queryable metadata store of the source corpus and dataset versions, (b) visualize how data flowed from source through transformations to the model output for compliance reporting, and (c) ensure customer PII never persists in application logs, given that blocked content can still appear as plaintext in Model Invocation Logs.

**Ask:** Which THREE statements correctly map services to these needs? (Select THREE)

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.3

### 3. Option Analysis
- **A** ✅ The AWS Glue Data Catalog is the persistent metadata store for the corpus and datasets, with crawlers discovering schemas
- **B** ❌ The AWS Glue Data Catalog is also where lineage graphs are visualized for compliance reporting
- **C** ✅ Amazon DataZone or the SageMaker Catalog consumes Glue lineage and visualizes how data flowed from source to output
- **D** ❌ A Bedrock guardrail with the sensitive information filter guarantees PII never reaches application logs
- **E** ✅ Amazon Comprehend token-level redaction applied to log output before it propagates keeps PII out of the logs

### 4. Correct Answer Deep-Dive
**Answer: A, C, E**

The scenario maps to three distinct needs and the correct answers are the three accurate service mappings. A is correct: the Glue Data Catalog is the metadata store and crawlers register schemas. C is correct: lineage visualization is DataZone / SageMaker Catalog, which consume Glue lineage. E is correct: Comprehend token-level redaction scrubs PII from log output before it persists — the antidote to the Model Invocation Logging plaintext trap. B is wrong: Glue stores metadata but is not the lineage visualization layer. D is wrong: the guardrail redacts inline at the model boundary but does not control what Model Invocation Logging writes — blocked content still lands as plaintext in the logs.

> Note: answer key corrected during AWS-doc fact-check (source: https://docs.aws.amazon.com/datazone/latest/userguide/datazone-data-lineage.html). The question stem was subsequently corrected from "Select TWO" to "Select THREE" to match the three-part scenario and this key.

### 5. Key Takeaway
Catalog, lineage, and log hygiene are three different jobs: Glue Data Catalog stores the metadata, DataZone / SageMaker Catalog visualizes lineage consumed from Glue, and Comprehend token-level redaction scrubs PII before it lands in logs — a guardrail alone does not control what Model Invocation Logging persists.

---

## Question 50

### 1. Question Summary
**Scenario:** A model deemed fair at launch is suspected of becoming biased after months in production as live traffic diverges from the training distribution. Separately, a media customer needs to verify whether a circulating image was generated by Amazon Titan and wants a confidence level with the verdict.

**Ask:** Which two capabilities address these needs respectively?

### 2. Domain Mapping
**Domain:** Domain 3: AI Safety, Security, and Governance
**Task:** Task 3.4

### 3. Option Analysis
- **A** ❌ SageMaker Clarify pre-training bias metrics for the drift concern; an Amazon Bedrock content filter to verify the image origin
- **B** ✅ SageMaker Model Monitor bias drift monitoring (Clarify, with CloudWatch alerts) for the drift concern; watermark detection via the DetectGeneratedContent API for the image
- **C** ❌ A one-time SageMaker Clarify post-training bias report for the drift concern; Amazon Macie to verify the image origin
- **D** ❌ Bedrock contextual grounding checks for the drift concern; Amazon Comprehend to verify the image origin

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: detecting fairness erosion over time requires continuous bias drift monitoring — SageMaker Model Monitor's ModelBiasMonitor with Clarify establishes a baseline and raises CloudWatch alerts when metrics drift; a launch-day snapshot is insufficient. Image provenance is watermark detection — Titan embeds an invisible watermark by default and DetectGeneratedContent returns a presence verdict with a confidence score. A uses pre-training metrics (a dataset snapshot, not continuous drift) and a content filter cannot establish image origin. C uses a one-time report (not drift monitoring) and Macie discovers S3 sensitive data, not image provenance. D misuses grounding (response-vs-source scoring) and Comprehend (text PII) for tasks neither performs.

### 5. Key Takeaway
Correct: detecting fairness erosion over time requires continuous bias drift monitoring — SageMaker Model Monitor's ModelBiasMonitor with Clarify establishes a baseline and raises CloudWatch alerts when metrics drift; a launch-day snapshot is insufficient.

---

