# AIP-C01 Practice Exam 1 — Analysis (Q01-Q05)

## Question 1

### 1. Question Summary
**Scenario:** A retail company is designing a new generative AI assistant. The product team has a business goal but disagrees on architecture: latency must stay under one second for a chat UI, the assistant must answer from a product catalog that changes several times per day, and leadership wants confidence that the design follows AWS best practices before a multi-quarter build commits budget. A lead engineer proposes immediately writing production integration code against a flagship reasoning model.

**Ask:** Following the Task 1.1 design discipline, which sequence of actions BEST addresses the team's situation before committing to a full build?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.1

### 3. Option Analysis
- **A** ❌ Fine-tune a flagship model nightly on the catalog, then build the production integration directly against it
- **B** ✅ Derive the architecture from the constraints, validate it with a proof-of-concept on Bedrock, and review the design against the Well-Architected Generative AI Lens
- **C** ❌ Purchase Provisioned Throughput for the flagship model first to guarantee the sub-second latency budget, then design the rest of the system around it
- **D** ❌ Skip the proof-of-concept because a design document already captures the latency, cost, and freshness requirements

### 4. Correct Answer Deep-Dive
**Answer: B**

Task 1.1 prescribes deriving the architecture from business need and constraints, validating feasibility with a Bedrock PoC (which surfaces real latency/cost/quality), and reviewing against the WA Generative AI Lens. A is wrong because nightly fine-tuning is the classic freshness trap (RAG is the answer for daily-changing catalog data) and jumping straight to build skips validation. C commits capacity before the design exists and ignores that on-demand suits a chat workload until volume is proven. D contradicts the explicit guidance that a PoC surfaces realities a design document cannot.

### 5. Key Takeaway
Task 1.1 prescribes deriving the architecture from business need and constraints, validating feasibility with a Bedrock PoC (which surfaces real latency/cost/quality), and reviewing against the WA Generative AI Lens.

---

## Question 2

### 1. Question Summary
**Scenario:** A SaaS company runs a customer-support assistant on Amazon Bedrock. Telemetry shows roughly 90 percent of queries are routine FAQ-style questions and about 10 percent are complex multi-step troubleshooting. Finance wants to cut foundation-model spend significantly without measurably degrading answer quality, and the team must be able to change which model serves each tier later without redeploying code.

**Ask:** Which combination of techniques BEST meets both the cost and the operational-flexibility requirements?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.2

### 3. Option Analysis
- **A** ❌ Route all traffic to the flagship model and rely on exponential backoff to control cost
- **B** ✅ Implement model cascading (cheap model first, escalate hard queries to a flagship model) and externalize the active model choice in AWS AppConfig behind a Lambda/API Gateway abstraction
- **C** ❌ Purchase six-month Provisioned Throughput for the flagship model to obtain volume discounts and serve all traffic from it
- **D** ❌ Switch all traffic to batch inference to capture the lower per-token price

### 4. Correct Answer Deep-Dive
**Answer: B**

Cascading sends the 90 percent routine traffic to a cheap, fast model and escalates only the 10 percent that genuinely need the flagship, cutting cost with minimal quality loss; storing the active model in AppConfig behind a Lambda/API Gateway layer lets the team swap models by config change with no redeploy. A leaves all traffic on the expensive model. C pays flagship rates for the routine bulk and a long commitment for spiky interactive traffic. D abandons real-time behavior the support chat requires and does not address dynamic switching.

### 5. Key Takeaway
Cascading sends the 90 percent routine traffic to a cheap, fast model and escalates only the 10 percent that genuinely need the flagship, cutting cost with minimal quality loss; storing the active model in AppConfig behind a Lambda/API Gateway layer lets the team swap models by config change with no redeploy.

---

## Question 3

### 1. Question Summary
**Scenario:** A bank fine-tuned an Amazon Bedrock model on labeled examples to enforce a strict house writing style that prompting could not reliably produce. The team now wants to serve this customized model in a production application that receives steady, high-volume traffic. A junior engineer wrote integration code that calls the model on-demand and is puzzled that invocations fail.

**Ask:** What is the root cause, and what is the correct production serving approach?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.2

### 3. Option Analysis
- **A** ❌ The model needs batch inference; reformat the requests as S3 input files
- **B** ✅ A customized Bedrock model cannot be invoked like a base model — it must be given its own serving surface, and for steady high-volume production that is Provisioned Throughput (a committed purchase also requires a Model Unit quota increase first)
- **C** ❌ The model must be re-imported as a base model so it qualifies for on-demand invocation
- **D** ❌ On-demand works for custom models, but the region lacks capacity; enable a cross-Region inference profile

### 4. Correct Answer Deep-Dive
**Answer: B**

The code fails because a custom model has no base-model on-demand path — it must be served through a surface of its own. For this steady, high-volume production workload that surface is Provisioned Throughput (committed purchases require a Model Unit quota increase through AWS Support first). Current docs also offer a custom model deployment for on-demand inference, but it carries no throughput guarantee and suits variable or low traffic, not this workload. A is wrong: batch is not supported for provisioned/custom serving and the workload is real-time. C is fabricated. D misattributes the failure to capacity; cross-Region profiles route base-model on-demand traffic and do not serve a custom model.

> Note: key updated during re-verification — an earlier version stated custom models "cannot be invoked on-demand" outright. Current documentation (model-customization-use) also offers on-demand inference via custom model deployments; PT remains the credited choice for this steady high-volume scenario. Point-in-time — re-verify near exam day.

### 5. Key Takeaway
A custom Bedrock model needs its own serving surface — Provisioned Throughput for steady high-volume, guaranteed-throughput traffic (MU quota increase before a committed purchase), or a custom model deployment for on-demand inference on variable traffic.

---

## Question 4

### 1. Question Summary
**Scenario:** A European financial customer requires that all inference data remain within the EU for regulatory reasons. They still want resilience against single-Region capacity bursts so that throttling does not break their assistant. They are evaluating Bedrock inference profiles. An architect intermittently sees AccessDenied-style failures in CloudTrail during a pilot that used a profile spanning several Regions.

**Ask:** Which choice satisfies the data-residency requirement while still giving cross-Region resilience, and what is the most likely cause of the intermittent failures the architect saw?

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.2

### 3. Option Analysis
- **A** ❌ Use a Global inference profile for maximum capacity; the failures are unrelated network errors
- **B** ✅ Use an EU geography-scoped inference profile; an SCP or IAM policy was blocking Bedrock inference in one of the profile's destination Regions
- **C** ❌ Use single-Region on-demand only; cross-Region inference is incompatible with any residency requirement
- **D** ❌ Use an application inference profile in any Region; the failures were caused by exceeding the Model Unit quota

### 4. Correct Answer Deep-Dive
**Answer: B**

A geography-scoped (EU) profile has a fixed destination list within the EU, satisfying residency while still distributing load across EU Regions. The intermittent AccessDenied pattern under a multi-Region profile is the textbook symptom of an SCP/IAM policy that blocks a destination Region: a single blocked destination fails the request. A violates residency (Global can route to any commercial Region) and ignores the policy cause. C is false because geo-scoped profiles exist precisely for this. D conflates an application profile (a cost-tracking construct) with residency scope and misattributes the cause to MU quotas.

### 5. Key Takeaway
A geography-scoped (EU) profile has a fixed destination list within the EU, satisfying residency while still distributing load across EU Regions.

---

## Question 5

### 1. Question Summary
**Scenario:** A data engineering team is building the ingestion pipeline that feeds a RAG knowledge base. The corpus is a mix of recorded support phone calls, scanned PDF invoices with tables, and a large structured customer dataset in a data lake that must meet completeness and uniqueness rules before anything is embedded. The team wants each data type routed to the correct AWS service.

**Ask:** Which mapping of data type to processing service is correct for this pipeline? (Select THREE)

### 2. Domain Mapping
**Domain:** Domain 1: Foundation Model Integration, Data Management, and Compliance
**Task:** Task 1.3

### 3. Option Analysis
- **A** ✅ Recorded support calls (audio) → Amazon Transcribe to produce searchable text
- **B** ✅ Scanned PDF invoices with tables → Amazon Textract to extract text, forms, and tables
- **C** ✅ Large structured data-lake dataset → AWS Glue Data Quality to enforce completeness and uniqueness rules at scale
- **D** ❌ Recorded support calls (audio) → Amazon Comprehend to convert speech to text
- **E** ❌ Scanned PDF invoices with tables → Amazon Rekognition to extract the table cells
- **F** ❌ Large structured data-lake dataset → Amazon Transcribe to validate the rules

### 4. Correct Answer Deep-Dive
**Answer: A, B, C**

Transcribe converts speech to text (the entry point for audio into RAG); Textract extracts text, forms, and tables from scans; Glue Data Quality enforces rule-based validation (completeness, uniqueness) at scale on data-lake datasets via DQDL. D is wrong because Comprehend extracts entities/PII from existing text, not speech-to-text. E is wrong because Rekognition analyzes images for objects/scenes, not document tables. F is nonsense (Transcribe is audio-to-text, not a rule validator).

### 5. Key Takeaway
Transcribe converts speech to text (the entry point for audio into RAG); Textract extracts text, forms, and tables from scans; Glue Data Quality enforces rule-based validation (completeness, uniqueness) at scale on data-lake datasets via DQDL.

---

