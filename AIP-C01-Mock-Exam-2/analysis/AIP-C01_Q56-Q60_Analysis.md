# AIP-C01 Practice Exam 2 — Analysis (Q56-Q60)

## Question 56

### 1. Question Summary
**Scenario:** An interactive coding assistant on Bedrock currently sends every request to a flagship model. Analysis shows request difficulty is bimodal but unstable: about 55% of requests can be answered by a small model, but the small model fails the other 45%, and the team cannot reliably predict in advance which bucket a given request falls into. The product has a strict interactive latency SLO. A reviewer suggests a model-cascading pattern: try the small model first and escalate to the flagship only when a validator rejects the small model's output.

**Ask:** What is the principal weakness of the cascading proposal for this specific workload, and what is the better-justified alternative?

### 2. Domain Mapping
**Domain:** Task 4.1/4.2 — Model selection (cascading added-latency risk vs tiering misclassification)
**Task:** Task Task 4.2

### 3. Option Analysis
- **A** ❌ Cascading is ideal here because trying the cheap model first always reduces latency relative to calling the flagship directly
- **B** ✅ With a ~45% escalation rate, nearly half of requests would pay the small model's full latency and then the flagship's full latency in sequence, frequently breaching the interactive SLO; because difficulty is unpredictable up front, a better fit may be sending all traffic to a capable model (or investing in a stronger up-front classifier) rather than paying double latency on almost half the requests
- **C** ❌ Cascading fails only because the validator adds cost; remove the validator and the pattern becomes optimal
- **D** ❌ Use model tiering instead, which guarantees both the lowest latency and the lowest cost because each request runs exactly one model chosen by predicted difficulty

### 4. Correct Answer Deep-Dive
**Answer: B**

Cascading trades average-case cost for worst-case latency: an escalated request waits out the small model in full and then the flagship in full, making it slower than a direct flagship call. That trade only pays off when the escalation rate is low. Here ~45% of requests escalate, so nearly half of all traffic incurs double latency under a strict interactive SLO — the pattern's characteristic latency risk dominates. With unpredictable difficulty, going straight to a capable model (or first building a reliable classifier) is better justified than paying double latency constantly. A is the false 'cascading is always faster' trap. C is wrong — the binding problem is the sequential double latency on escalation, not validator cost. D overstates tiering: tiering needs a reliable up-front prediction, which the scenario says is not available, so it risks misclassifying hard requests onto the weak model.

### 5. Key Takeaway
Cascading trades average-case cost for worst-case latency: an escalated request waits out the small model in full and then the flagship in full, making it slower than a direct flagship call.

---

## Question 57

### 1. Question Summary
**Scenario:** A platform team operates a multi-tenant Bedrock application that internally routes traffic across several models, including third-party LLMs billed under their own legal entities (for example, Anthropic Claude billed as 'Anthropic, PBC'). Leadership asks the team to (1) attribute Bedrock spend to the specific business unit that incurred it for chargeback, (2) receive a proactive alert when the third-party-LLM portion of the bill crosses a planned threshold, and (3) detect a gradual decline in answer quality on a critical question type even while latency and error metrics stay healthy.

**Ask:** Which THREE of the following correctly map to the three requirements? (Select THREE.)

### 2. Domain Mapping
**Domain:** Task 4.3 — Monitoring systems (multi-select: cost attribution, third-party LLM spend, drift)
**Task:** Task Task 4.3

### 3. Option Analysis
- **A** ❌ Activate cost allocation tags (before the spend occurs, since they are not retroactive) and view spend grouped by tag in AWS Cost Explorer to attribute Bedrock cost to each business unit
- **B** ❌ Create an AWS Budget filtered on the third-party Billing entity (legal entity) so an alert fires when that LLM spend crosses the planned threshold
- **C** ❌ Schedule recurring golden-dataset re-runs scored by Amazon Bedrock Evaluations (paired with an EventBridge scheduled rule) to surface gradual quality/hallucination drift
- **D** ❌ Rely on AWS Cost Anomaly Detection to alert on the third-party-LLM spend threshold, since it monitors all Bedrock charges including Marketplace models
- **E** ❌ Alarm on a single static CloudWatch threshold over InvocationLatency to detect the answer-quality decline
- **F** ❌ Use a single aggregate AWS/Bedrock error metric to detect quality drift, since increased hallucination raises the error count

### 4. Correct Answer Deep-Dive
**Answer: ABC**

Cost allocation tags (activated proactively, since tags are not retroactive) viewed through Cost Explorer grouping is the attribution mechanism for chargeback (A). AWS Budgets filtered on the third-party Billing entity is the documented way to alert on third-party-LLM spend, precisely because AWS Cost Anomaly Detection does NOT monitor third-party AWS Marketplace products (B). Scheduled golden-dataset re-runs scored by Bedrock Evaluations is the standing-program pattern for detecting gradual quality/hallucination drift that leaves latency and error metrics healthy (C). D is the canonical Cost Anomaly Detection blind-spot trap — it excludes third-party Marketplace charges. E is wrong because a latency alarm cannot detect a quality decline (the model is still fast and returns 200s). F is wrong because there is no single aggregate error metric and hallucinations do not increment error counts at all.

### 5. Key Takeaway
Cost allocation tags (activated proactively, since tags are not retroactive) viewed through Cost Explorer grouping is the attribution mechanism for chargeback (A).

---

## Question 58

### 1. Question Summary
**Scenario:** A media company must run a Bedrock model over a back catalog of 400,000 archived articles overnight to generate metadata. The work is offline (results needed next morning), volume is large and bounded, and the goal is lowest cost. The proposed design submits the corpus as a Bedrock batch inference job through Amazon S3. A second requirement is added late: each article's output must be enriched by having the model call an external tagging tool (function calling) and must conform to a strictly enforced JSON schema per record.

**Ask:** Which TWO statements are correct about using Bedrock batch inference for this design? (Select TWO.)

### 2. Domain Mapping
**Domain:** Task 4.1 — Cost optimization (multi-select: batch inference fit and its hard constraints)
**Task:** Task Task 4.1

### 3. Option Analysis
- **A** ❌ Batch inference is a good fit for the bulk, offline, cost-sensitive portion: it processes a large bounded request set asynchronously via S3 at a documented discount relative to on-demand, trading away real-time latency
- **B** ❌ The late requirement breaks the batch fit: batch processes each record independently and supports neither tool calling (function calling) nor structured-output/JSON-schema enforcement, so the tool-calling and schema requirements must run on a real-time/async invocation path instead
- **C** ❌ Batch inference guarantees real-time per-record responses, so it satisfies both the bulk processing and the new tool-calling requirement
- **D** ❌ Enabling Bedrock prompt caching on the shared instruction prefix will further cut cost during the batch job, since prompt caching is supported on the batch inference API
- **E** ❌ Provisioned Throughput must be purchased to run any batch job, because batch jobs require dedicated Model Units

### 4. Correct Answer Deep-Dive
**Answer: AB**

Batch inference fits the bulk, offline, cost-sensitive workload exactly — large bounded request set processed asynchronously via S3 at a documented discount, trading away real-time turnaround (A). But the late requirement is incompatible: batch processes each record independently with no multi-turn interaction, so it supports neither tool calling nor structured-output/JSON-schema enforcement; those must run on a different (real-time/async) path (B). C is false (batch is asynchronous, not real-time, and cannot do tool calling). D is the prompt-caching-on-batch trap — prompt caching is supported on the on-demand path, not the batch inference API. E is false — batch does not require (and is in fact not supported on) Provisioned Throughput.

### 5. Key Takeaway
Batch inference fits the bulk, offline, cost-sensitive workload exactly — large bounded request set processed asynchronously via S3 at a documented discount, trading away real-time turnaround (A).

---

## Question 59

### 1. Question Summary
**Scenario:** A retail company runs a customer-support knowledge base in an Amazon Bedrock Knowledge Base. Support leaders complain that the assistant gives answers that are accurate as far as they go but consistently leave out parts of a multi-part question (for example, it answers the return-window question but omits the restocking-fee question). The team builds a labeled evaluation dataset with reference answers and runs a retrieve-and-generate Knowledge Base evaluation job. Context relevance is high (0.91), faithfulness is high (0.93), but one metric is low (0.42), confirming the symptom.

**Ask:** Which built-in Knowledge Base evaluation metric is the 0.42 score, and what does the result tell the team to fix?

### 2. Domain Mapping
**Domain:** Task 5.1 — Evaluation systems
**Task:** Task 5.1

### 3. Option Analysis
- **A** ❌ Builtin.ContextCoverage is low, so the retriever is missing chunks — increase top-k and revisit chunking
- **B** ✅ Builtin.Completeness is low, so the generator is not resolving all parts of the question — the generation stage is at fault
- **C** ❌ Builtin.Faithfulness is low, so the model is hallucinating — enable a contextual grounding check
- **D** ❌ Builtin.CitationPrecision is low, so the response cites passages incorrectly — re-rank the citations

### 4. Correct Answer Deep-Dive
**Answer: B**

Completeness measures how well responses resolve all aspects of the questions, which is exactly the multi-part-omission symptom. With high context relevance AND high faithfulness, the retrieved chunks are on-topic and the answer is grounded in them — so retrieval is healthy and the generator is faithfully but partially answering. That isolates the fault to the generation stage (prompt/model not addressing every sub-question). A is wrong because context coverage being the issue would show as a low coverage score and would require ground truth; the scenario already reports high relevance and the symptom is generator-side omission, not retrieval gaps. C misreads the high (0.93) faithfulness as the problem. D (citation precision) addresses citation correctness, not answer completeness.

### 5. Key Takeaway
Completeness measures how well responses resolve all aspects of the questions, which is exactly the multi-part-omission symptom.

---

## Question 60

### 1. Question Summary
**Scenario:** A team must benchmark three candidate models — including Anthropic Claude variants — for a creative marketing-copy use case where there is no single correct answer. They configure an Amazon Bedrock LLM-as-a-judge model evaluation job and, for fairness, want to choose the judge model. An engineer proposes uploading their own fine-tuned in-house scoring model as the judge because it best understands the brand voice, and separately proposes using a Claude model as the judge to score the candidate Claude outputs.

**Ask:** Which statement correctly identifies the problems with these two proposals?

### 2. Domain Mapping
**Domain:** Task 5.1 — LLM-as-a-judge evaluation
**Task:** Task 5.1

### 3. Option Analysis
- **A** ❌ The in-house judge is fine, but using a Claude judge to score Claude candidates risks self-preference bias and should be spot-checked by humans
- **B** ✅ You cannot bring your own judge model — judges are selected from a Bedrock-curated list — and a judge sharing a family with a candidate risks self-preference bias, so critical comparisons need human spot checks
- **C** ❌ Both proposals are valid; LLM-as-a-judge fully replaces human review, so no spot checks are needed
- **D** ❌ You cannot bring your own judge model, but self-preference bias is not a real concern because Bedrock normalizes all scores to a 0-to-1 scale

### 4. Correct Answer Deep-Dive
**Answer: B**

Two distinct facts both apply. First, Bedrock judge (evaluator) models are selected from an AWS-curated list with AWS-optimized evaluation prompts — you cannot supply your own judge model (you CAN bring your own generated responses, but not your own judge). Second, when the judge shares a family/architecture with a candidate (Claude judging Claude), self-preference bias means the judge may favor its own kin, so AWS recommends human spot checks for critical comparisons. A is wrong because it accepts the BYO judge. C is wrong because LLM-as-a-judge augments rather than replaces human review. D is wrong because 0-to-1 normalization does not eliminate bias.

### 5. Key Takeaway
Two distinct facts both apply.

---

