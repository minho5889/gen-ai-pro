# AIP-C01 Practice Exam 2 — Analysis (Q46-Q50)

## Question 46

### 1. Question Summary
**Scenario:** A healthcare RAG application ingests documents from a third-party Pinecone vector store and a Confluence wiki, and also ingests case files from an Amazon S3 bucket. Architecture review requires least-privilege credential handling for every data source and vector store connection, with no long-lived secrets hardcoded anywhere.

**Ask:** Which TWO statements about credential handling for these connections are correct?

### 2. Domain Mapping
**Domain:** 3.2 Data security and privacy controls
**Task:** Task 3.2

### 3. Option Analysis
- **A** ✅ The Pinecone vector-store connection references a Secrets Manager secret ARN (credentialsSecretArn) holding its API key
- **B** ✅ The Confluence data-source connector authenticates with credentials (API token or OAuth 2.0) stored in AWS Secrets Manager
- **C** ❌ The Amazon S3 connector must also store an API key in Secrets Manager, scoped by a condition key
- **D** ❌ First-party vector stores like Pinecone authenticate via IAM and need no secret
- **E** ❌ All three connections share a single Secrets Manager secret to minimize secret sprawl

### 4. Correct Answer Deep-Dive
**Answer: AB**

Third-party vector stores (Pinecone, Redis Enterprise Cloud) reference a credentialsSecretArn in Secrets Manager (A), and SaaS data-source connectors like Confluence authenticate with API tokens or OAuth 2.0 credentials in Secrets Manager (B). C is wrong — the S3 connector is governed by IAM and needs no secret. D is wrong on two counts: Pinecone is third-party (not first-party), and it is the first-party stores (OpenSearch Serverless, Aurora) that use IAM. E is wrong and unsafe — least privilege scopes each role to a specific secret ARN (via bedrock:ThirdPartyKnowledgeBaseCredentialsSecretArn), not a shared secret.

### 5. Key Takeaway
Third-party vector stores (Pinecone, Redis Enterprise Cloud) reference a credentialsSecretArn in Secrets Manager (A), and SaaS data-source connectors like Confluence authenticate with API tokens or OAuth 2.0 credentials in Secrets Manager (B).

---

## Question 47

### 1. Question Summary
**Scenario:** A security team must be alerted when a privileged user signing in from an unfamiliar geography deletes a Bedrock guardrail or repoints the S3 bucket that holds the fine-tuning training data. They already have a CloudWatch alarm on InvocationsIntervened and Model Invocation Logging writing to S3, but neither has surfaced these configuration-tampering events.

**Ask:** Which combination of services delivers detection of this tampering?

### 2. Domain Mapping
**Domain:** 3.3 AI governance and compliance
**Task:** Task 3.3

### 3. Option Analysis
- **A** ✅ AWS CloudTrail recording the management API calls and caller identity, with Amazon GuardDuty analyzing those events to flag suspicious Bedrock activity
- **B** ❌ Model Invocation Logging in S3 queried with Amazon Athena, which captures the deletion request body
- **C** ❌ A CloudWatch alarm on InvocationsIntervened, which spikes when a guardrail is deleted
- **D** ❌ AWS Config rules alone, which alert on the unfamiliar sign-in location

### 4. Correct Answer Deep-Dive
**Answer: A**

Guardrail deletion and bucket repointing are control-plane management actions; CloudTrail records them with caller identity and source IP, and GuardDuty analyzes CloudTrail events to surface suspicious Bedrock activity such as tampering from an unusual location. B is wrong — Model Invocation Logging captures inference content (prompts/completions), not configuration-change API calls. C is wrong — InvocationsIntervened counts content interventions, not deletions, and would not spike from a delete. D is wrong — Config evaluates resource configuration compliance but does not provide the location-aware threat detection GuardDuty adds.

### 5. Key Takeaway
Guardrail deletion and bucket repointing are control-plane management actions; CloudTrail records them with caller identity and source IP, and GuardDuty analyzes CloudTrail events to surface suspicious Bedrock activity such as tampering from an unusual location.

---

## Question 48

### 1. Question Summary
**Scenario:** A compliance officer wants an auditable record of every InvokeAgent and RetrieveAndGenerate call made by the company's Bedrock agents and Knowledge Bases — who called, when, against which resource. They have a multi-Region CloudTrail trail delivering to S3 and assume agent and KB invocations are captured automatically, but the trail shows none of them.

**Ask:** Why are these calls missing, and how are they captured?

### 2. Domain Mapping
**Domain:** 3.3 AI governance and compliance
**Task:** Task 3.3

### 3. Option Analysis
- **A** ✅ InvokeAgent, Retrieve, and RetrieveAndGenerate are CloudTrail data events, which are off by default and must be explicitly enabled with advanced event selectors by resource type
- **B** ❌ These calls are only recorded by Model Invocation Logging, which must be enabled separately
- **C** ❌ Agent and KB calls are management events that require the trail to be single-Region to appear
- **D** ❌ CloudTrail cannot record agent or Knowledge Base invocations; only CloudWatch metrics can

### 4. Correct Answer Deep-Dive
**Answer: A**

InvokeAgent, InvokeInlineAgent, Retrieve, RetrieveAndGenerate, and InvokeFlow are classified as CloudTrail data events — off by default — and must be turned on via advanced event selectors keyed to resource types like AWS::Bedrock::AgentAlias and AWS::Bedrock::KnowledgeBase. B is wrong: Model Invocation Logging captures inference content for bedrock-runtime model calls, not the who/when of agent/KB API calls. C inverts the facts — these are data events, not management events, and multi-Region is correct for coverage. D is false; CloudTrail does record them once data events are enabled.

### 5. Key Takeaway
InvokeAgent, InvokeInlineAgent, Retrieve, RetrieveAndGenerate, and InvokeFlow are classified as CloudTrail data events — off by default — and must be turned on via advanced event selectors keyed to resource types like AWS::Bedrock::AgentAlias and AWS::Bedrock::KnowledgeBase.

---

## Question 49

### 1. Question Summary
**Scenario:** A lending model was demonstrated to be fair across demographic groups at launch using SageMaker Clarify. Six months later, as the live applicant population diverges from the original training distribution, the model's behavior may have become biased, but nobody has re-measured. Leadership asks for an automated control that establishes a baseline and an acceptable range for a bias metric like DPPL, periodically evaluates the live model, and raises a CloudWatch alert when the metric drifts outside that range.

**Ask:** Which capability provides this continuous, automated bias-drift detection?

### 2. Domain Mapping
**Domain:** 3.4 Responsible AI principles
**Task:** Task 3.4

### 3. Option Analysis
- **A** ✅ Amazon SageMaker Model Monitor bias drift monitoring (ModelBiasMonitor), which has Clarify evaluate the live model against a baseline and alerts via CloudWatch when bias drifts out of range
- **B** ❌ A one-time SageMaker Clarify pre-training bias report rerun manually each quarter
- **C** ❌ An Amazon Bedrock guardrail with the sensitive-information filter to catch biased outputs at inference
- **D** ❌ A SageMaker Model Card risk-rating field set to 'high' to flag potential drift

### 4. Correct Answer Deep-Dive
**Answer: A**

Model Monitor bias drift monitoring (ModelBiasMonitor) establishes a baseline and acceptable range for metrics like DPPL, has Clarify evaluate the live model periodically, and raises CloudWatch alerts when bias drifts outside the range — exactly the continuous, automated need. B is a manual point-in-time check, not automated continuous monitoring, and pre-training metrics evaluate data, not live predictions. C is a runtime content filter for harmful/PII content, not a fairness/bias drift detector. D is documentation metadata, not a detection mechanism.

### 5. Key Takeaway
Model Monitor bias drift monitoring (ModelBiasMonitor) establishes a baseline and acceptable range for metrics like DPPL, has Clarify evaluate the live model periodically, and raises CloudWatch alerts when bias drifts outside the range — exactly the continuous, automated need.

---

## Question 50

### 1. Question Summary
**Scenario:** An AI governance committee is standardizing transparency documentation. For each foundation model the company consumes from AWS, it wants to reference AWS's own documented guidance on the model's intended use and limitations. Separately, for each model the company builds and deploys itself, it must produce a governed internal record capturing intended uses, a risk rating, training details, and evaluation results, with an immutable version history for auditors.

**Ask:** Which TWO statements correctly distinguish the artifacts the committee should use?

### 2. Domain Mapping
**Domain:** 3.4 Responsible AI principles
**Task:** Task 3.4

### 3. Option Analysis
- **A** ✅ For an AWS-provided model's documented intended use and limitations, the committee reads an AWS AI Service Card, which is authored by AWS
- **B** ✅ For its own models, the committee creates SageMaker Model Cards, which carry a risk-rating field (unknown, low, medium, high) and an immutable version history
- **C** ❌ The committee should author AWS AI Service Cards to document its own internally built models
- **D** ❌ SageMaker Model Cards are authored by AWS and read by the customer for AWS models
- **E** ❌ Both artifacts are interchangeable since both document intended use and limitations

### 4. Correct Answer Deep-Dive
**Answer: AB**

AI Service Cards are authored by AWS and read by customers — the right reference for an AWS model's intended use and limitations (A). SageMaker Model Cards are customer-authored governance documents with a risk-rating enum (unknown/low/medium/high) and immutable version history (any edit other than approval-status change creates a new version) (B). C inverts authorship — customers do not author AI Service Cards. D inverts authorship of Model Cards — customers author them. E is false; the artifacts differ precisely on who authors them and which side of the line you are on.

### 5. Key Takeaway
AI Service Cards are authored by AWS and read by customers — the right reference for an AWS model's intended use and limitations (A).

---

