# AIP-C01 Practice Exam 2 — Analysis (Q01-Q05)

## Question 1

### 1. Question Summary
**Scenario:** A media company is scoping a new generative AI feature and wants to follow AWS's prescribed design discipline before committing engineering resources. Leadership asks the team to systematically review the proposed workload against operational excellence, security, reliability, performance efficiency, cost optimization, and sustainability — but tailored specifically to the characteristics of generative AI rather than generic cloud architecture.

**Ask:** Which AWS resource is the intended mechanism for systematically reviewing a generative AI workload against best practices?

### 2. Domain Mapping
**Domain:** Task 1.1 — Design GenAI solutions
**Task:** Task 1.1

### 3. Option Analysis
- **A** ✅ The AWS Well-Architected Framework Generative AI Lens, accessed through the Well-Architected Tool
- **B** ❌ Amazon Bedrock model evaluation jobs configured with the six WA pillars
- **C** ❌ AWS Trusted Advisor cost and security checks
- **D** ❌ The AWS Pricing Calculator with a generative AI template

### 4. Correct Answer Deep-Dive
**Answer: A**

The Well-Architected Generative AI Lens applies the six Well-Architected pillars to the specifics of GenAI workloads and is accessed through the Well-Architected Tool — this is the named answer whenever a question asks how to systematically review a GenAI design against best practices. Model evaluation (B) assesses model output quality on a dataset, not architectural pillars. Trusted Advisor (C) gives account-level checks, not a GenAI design review. The Pricing Calculator (D) estimates cost only.

### 5. Key Takeaway
The Well-Architected Generative AI Lens applies the six Well-Architected pillars to the specifics of GenAI workloads and is accessed through the Well-Architected Tool — this is the named answer whenever a question asks how to systematically review a GenAI design against best practices.

---

## Question 2

### 1. Question Summary
**Scenario:** A team enabled a system-defined cross-Region inference profile so a popular model can absorb traffic bursts. The profile lists a source Region plus three destination Regions. In testing everything works, but in production a fraction of invocations fail with access-denied-style errors in CloudTrail, seemingly at random. The application code, IAM execution role for the source Region, and model identifier are all confirmed correct.

**Ask:** What is the MOST likely root cause?

### 2. Domain Mapping
**Domain:** Task 1.2 — Select and configure FMs (resilience / SCP)
**Task:** Task 1.2

### 3. Option Analysis
- **A** ✅ A Service Control Policy or IAM policy blocks Bedrock inference in one of the profile's destination Regions, so requests routed there fail
- **B** ❌ Cross-Region inference incurs a data-transfer charge that is exhausting the account budget and causing rejections
- **C** ❌ The destination Regions must be manually opted into in account settings before the profile can route to them
- **D** ❌ The application must implement client-side load balancing across the destination Regions itself

### 4. Correct Answer Deep-Dive
**Answer: A**

Under a cross-Region profile a request can land in any destination Region, and if an SCP or IAM policy blocks Bedrock inference actions in even one destination Region, the requests routed there fail — producing exactly the intermittent access-denied pattern described. The fix is to allow the required Bedrock inference actions across every destination Region. B is wrong: cross-Region inference adds no routing or data-transfer cost. C is wrong: the profile's destination list governs routing even to Regions you did not opt into. D is wrong: Bedrock handles distribution with no client-side balancing.

### 5. Key Takeaway
Under a cross-Region profile a request can land in any destination Region, and if an SCP or IAM policy blocks Bedrock inference actions in even one destination Region, the requests routed there fail — producing exactly the intermittent access-denied pattern described.

---

## Question 3

### 1. Question Summary
**Scenario:** An insurance company fine-tuned a foundation model in Amazon Bedrock to enforce a strict claims-summary format that prompting could not reliably produce. They now plan to serve it to a high-traffic production endpoint and are estimating costs. A junior engineer's plan assumes on-demand per-token pricing identical to the base model.

**Ask:** What must the cost estimate account for that the engineer's plan omits?

### 2. Domain Mapping
**Domain:** Task 1.2 — Select and configure FMs (customization lifecycle)
**Task:** Task 1.2

### 3. Option Analysis
- **A** ✅ A customized model is not served at the base model's on-demand rate — it must either be deployed as a custom model deployment for on-demand inference (custom-model per-token pricing) or served through Provisioned Throughput (billed hourly per Model Unit), and for steady high-traffic serving the Provisioned Throughput hourly cost is the realistic line item
- **B** ❌ Fine-tuned models are only available through batch inference, billed per token at a discount
- **C** ❌ Fine-tuned models require a one-time conversion fee but then use the same on-demand pricing as the base model
- **D** ❌ Fine-tuned models can only be served from Amazon SageMaker endpoints, not Bedrock

### 4. Correct Answer Deep-Dive
**Answer: A**

The engineer's plan misses that a custom model has its own serving surfaces and pricing, distinct from the base model's on-demand rate. Current Bedrock documentation gives two setup options for custom-model inference: purchase Provisioned Throughput (dedicated capacity, billed hourly per Model Unit, with optional 1- or 6-month commitments and an MU quota request), or create a custom model deployment for on-demand inference (invoke via the deployment ARN, pay per token at custom-model pricing — suited to variable or lower-volume traffic). For a high-traffic production endpoint with sustained load, the Provisioned Throughput hourly cost is the number the estimate must carry; either way, "same on-demand per-token pricing as the base model" is the omission. B is wrong: batch is an offline bulk path, not the serving path for this endpoint, and does not bill that way. C invents a conversion fee and keeps base-model on-demand pricing, which is not how custom models are priced. D is wrong: Bedrock serves custom models itself (PT or custom model deployment); SageMaker is a separate hosting option, not a requirement.

> Note: key updated during re-verification — an earlier version stated a custom model "cannot be invoked on-demand" outright. Current documentation (model-customization-use) offers on-demand inference for custom models via custom model deployments; the cost-estimate lesson stands, the absolute claim does not. Point-in-time — re-verify near exam day.

### 5. Key Takeaway
A customized Bedrock model is served through its own surfaces — Provisioned Throughput (hourly per Model Unit; the realistic estimate for steady high traffic) or a custom model deployment for on-demand inference (per-token custom-model pricing) — never automatically at the base model's on-demand rate.

---

## Question 4

### 1. Question Summary
**Scenario:** A RAG ingestion pipeline must process thousands of scanned vendor invoices (PDF images) so that line-item tables and form fields become structured, queryable text before chunking and embedding. The team needs reliable extraction of the tabular and key-value structure, not a holistic natural-language description of each page.

**Ask:** Which AWS service is the correct first processing step for this data?

### 2. Domain Mapping
**Domain:** Task 1.3 — Data validation and pipelines
**Task:** Task 1.3

### 3. Option Analysis
- **A** ✅ Amazon Textract
- **B** ❌ Amazon Transcribe
- **C** ❌ Amazon Comprehend
- **D** ❌ Amazon Translate

### 4. Correct Answer Deep-Dive
**Answer: A**

Amazon Textract extracts text, forms, and tables from scanned documents and images — exactly the structured extraction (tables and key-value pairs) the scenario requires. Transcribe (B) is speech-to-text for audio/video. Comprehend (C) extracts entities, key phrases, sentiment, and PII from text you already have, not structure from scanned images. Translate (D) performs language translation and does no extraction. Note the contrast with a Bedrock multimodal model, which would give holistic understanding rather than the explicit form/table structure called for here.

### 5. Key Takeaway
Amazon Textract extracts text, forms, and tables from scanned documents and images — exactly the structured extraction (tables and key-value pairs) the scenario requires.

---

## Question 5

### 1. Question Summary
**Scenario:** A team using Amazon Titan Text Embeddings V2 wants to cut vector storage cost on a large RAG corpus. They are weighing two float32-preserving options. Their store is Amazon Aurora PostgreSQL with pgvector, and they are willing to accept a small precision loss but must keep retrieval quality high and avoid switching stores.

**Ask:** Which approach BEST meets these constraints?

### 2. Domain Mapping
**Domain:** Task 1.5 — Retrieval (embeddings)
**Task:** Task 1.5

### 3. Option Analysis
- **A** ✅ Configure Titan Text Embeddings V2 to output 256 dimensions, retaining roughly 97% of the 1024-dimension accuracy while cutting storage about 75%
- **B** ❌ Switch to binary (1-bit-per-dimension) embeddings to maximize storage savings
- **C** ❌ Switch to Titan Embeddings G1 and select a 256-dimension output
- **D** ❌ Increase the embedding dimension to 1024 to improve compression efficiency

### 4. Correct Answer Deep-Dive
**Answer: A**

Titan Text Embeddings V2 supports configurable output dimensions (256/512/1024); dropping to 256 keeps roughly 97% of the 1024-dim accuracy at about 75% less storage, stays float32, and is fully compatible with Aurora pgvector — meeting every constraint. B is wrong: binary vectors are only supported on OpenSearch Serverless/Managed, so they would force a store switch, which the scenario forbids. C is wrong: Titan G1/V1 have a fixed dimension and cannot be set to 256. D increases storage rather than cutting it and does not aid compression.

### 5. Key Takeaway
Titan Text Embeddings V2 supports configurable output dimensions (256/512/1024); dropping to 256 keeps roughly 97% of the 1024-dim accuracy at about 75% less storage, stays float32, and is fully compatible with Aurora pgvector — meeting every constraint.

---

