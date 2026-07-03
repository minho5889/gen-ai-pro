# AIP-C01 Practice Exam 1 — Analysis (Q56-Q60)

## Question 56

### 1. Question Summary
**Scenario:** A FinOps team operating a production Bedrock workload notes that the bulk of their monthly Bedrock spend is third-party Anthropic Claude usage, which appears on the invoice under the legal entity 'Anthropic, PBC.' They want an automated alert if those specific charges spike unexpectedly. Separately, they want to know which of three internal product teams sharing the same account is responsible for what share of the Bedrock spend. They have already enabled AWS Cost Anomaly Detection and assumed it covers everything.

**Ask:** Which combination correctly satisfies both requirements?

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.3

### 3. Option Analysis
- **A** ❌ Rely on Cost Anomaly Detection for the Claude spike alert, and use Cost Explorer grouping by Region to attribute spend to the three teams
- **B** ✅ Use AWS Budgets with a filter on the third-party Billing entity to alert on the Claude charges (Cost Anomaly Detection excludes third-party Marketplace products), and use activated cost allocation tags viewed in Cost Explorer to attribute spend across the three teams
- **C** ❌ Use Cost Anomaly Detection for the Claude spike alert, and use SageMaker Model Monitor to attribute Bedrock spend across the three teams
- **D** ❌ Use a CloudWatch static-threshold alarm on the InputTokenCount metric for the Claude spike, and use Cost Explorer's default service grouping to attribute spend across the three teams

### 4. Correct Answer Deep-Dive
**Answer: B**

AWS Cost Anomaly Detection does not monitor third-party AWS Marketplace products, and AWS explicitly includes third-party models on Bedrock (such as Anthropic Claude, billed under 'Anthropic, PBC') in that exclusion — so it has a blind spot for exactly the charges that dominate this bill. The documented alternative is AWS Budgets filtered on the Billing entity. Attribution across teams in a shared account requires cost allocation tags (activated, not retroactive) viewed via Cost Explorer grouping. A relies on the excluded service and uses Region (not team) grouping. C and D are wrong: SageMaker Model Monitor is for model-quality drift not cost attribution, and a CloudWatch token-count alarm watches operational metrics, not billed dollars, and a single static line cannot reliably catch a spend anomaly.

### 5. Key Takeaway
AWS Cost Anomaly Detection does not monitor third-party AWS Marketplace products, and AWS explicitly includes third-party models on Bedrock (such as Anthropic Claude, billed under 'Anthropic, PBC') in that exclusion — so it has a blind spot for exactly the charges that dominate this bill.

---

## Question 57

### 1. Question Summary
**Scenario:** A team is building the standing monitoring program for a production Bedrock assistant. They want CloudWatch alarms in the AWS/Bedrock namespace that reliably catch (1) capacity pressure from quota exhaustion and (2) token-spend growth on a workload whose token volume triples every weekday morning and falls to near zero overnight. A new engineer drafts a plan that includes alarming on 'the Bedrock error metric (which includes throttled requests)' and setting 'a single static threshold on the token-count sum.'

**Ask:** Which TWO statements correctly describe how to build these alarms? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.3

### 3. Option Analysis
- **A** ✅ To catch capacity pressure you must alarm on the InvocationThrottles metric specifically, because a throttled request is counted as neither an Invocation nor an error and there is no single aggregate error metric in the AWS/Bedrock namespace
- **B** ✅ For a token-count metric with strong daily seasonality, use CloudWatch anomaly detection (a learned dynamic baseline that accounts for seasonality) rather than a single static threshold
- **C** ❌ A single InvocationServerErrors alarm will capture throttling, because throttles are classified as server-side 5xx errors in the AWS/Bedrock namespace
- **D** ❌ Use AWS Cost Anomaly Detection to alarm on the AWS/Bedrock token-count metric in near real time, since it watches CloudWatch operational metrics directly
- **E** ❌ A single static threshold is the correct tool for the seasonal token metric as long as you set it just above the overnight trough

### 4. Correct Answer Deep-Dive
**Answer: A, B**

A is correct: the AWS/Bedrock namespace has no aggregate error metric; client errors, server errors, and throttles are distinct metrics, and a throttled invocation is counted as neither an Invocation nor an error, so capacity pressure must be alarmed on InvocationThrottles directly. B is correct: a metric with strong daily seasonality cannot be guarded by one fixed line, so CloudWatch anomaly detection (learned dynamic baseline accounting for seasonality) is the right tool. C is wrong: throttles are their own metric, not 5xx server errors. D is wrong: AWS Cost Anomaly Detection operates on billing/spend data (~3x/day), not on CloudWatch operational metrics. E is wrong: a trough-level static threshold would page constantly at the weekday peak.

### 5. Key Takeaway
A is correct: the AWS/Bedrock namespace has no aggregate error metric; client errors, server errors, and throttles are distinct metrics, and a throttled invocation is counted as neither an Invocation nor an error, so capacity pressure must be alarmed on InvocationThrottles directly.

---

## Question 58

### 1. Question Summary
**Scenario:** An engineering org reviews a production Bedrock workload that is too expensive. Telemetry shows: ~80% of traffic is simple intent-classification handled correctly by a small model in a quality test, while ~20% is complex multi-step reasoning the small model fails; a long static system prompt and a fixed tool-definition block are sent on every call; and overall traffic is spiky and unpredictable. The team must lower cost without dropping quality on the 20% of complex requests, and is asked to choose levers consistent with the Cost Lever Priority.

**Ask:** Which TWO actions are appropriate cost-optimization levers for this workload? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.1

### 3. Option Analysis
- **A** ✅ Apply Bedrock prompt caching to the repeated static system prompt and tool-definition block so the repeated prefix is not reprocessed or re-billed at full rate
- **B** ✅ Route requests by difficulty — send the simple ~80% to the small model and escalate or route the complex ~20% to the larger model (model tiering or cascading), since the small model has been validated to clear the quality bar on the simple traffic
- **C** ❌ Purchase Provisioned Throughput sized to peak traffic, because dedicated Model Units are the cheapest option for any workload regardless of traffic shape
- **D** ❌ Switch all traffic, including the complex 20%, to the small model to maximize the per-token savings
- **E** ❌ Lower the temperature parameter on all requests to reduce the per-token cost of generation

### 4. Correct Answer Deep-Dive
**Answer: A, B**

A is correct (lever 2): the static system prompt and tool-definition block are a repeated prefix, exactly what Bedrock prompt caching targets — cached reads are billed at a reduced rate and not reprocessed. B is correct (lever 3): difficulty varies, the small model is validated on the simple majority, so route simple traffic to it and reserve the larger model for the complex minority via tiering or cascading, preserving the quality bar on the 20%. C is wrong: the traffic is spiky and unpredictable, so Provisioned Throughput's always-on hourly meter would bill for idle capacity — it is not the cheapest option for any workload. D is wrong: it sends the complex 20% to a model that fails them, shipping wrong answers cheaply (quality-bar violation). E is wrong: temperature is a randomness control with no effect on per-token cost.

### 5. Key Takeaway
A is correct (lever 2): the static system prompt and tool-definition block are a repeated prefix, exactly what Bedrock prompt caching targets — cached reads are billed at a reduced rate and not reprocessed.

---

## Question 59

### 1. Question Summary
**Scenario:** A fintech team must choose between three foundation models for an open-ended customer-support assistant. Most support tickets have no single correct response, but legal requires an evidence-based, repeatable, defensible comparison before launch. The team also needs to score subjective qualities such as brand voice and empathy, which their automated metrics cannot capture, and they want the heavy, nightly correctness scoring of several thousand prompts to run cheaply and at scale.

**Ask:** Which combination of Amazon Bedrock model-evaluation methods best satisfies all of these requirements?

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.1

### 3. Option Analysis
- **A** ❌ Use automatic (programmatic) evaluation with classification accuracy and F1 for the correctness scoring, and human-worker evaluation for brand voice and empathy
- **B** ✅ Use LLM-as-a-judge evaluation for the nightly correctness scoring at scale, and human-worker evaluation for the subjective brand-voice and empathy scoring
- **C** ❌ Use human-worker evaluation for both the correctness scoring and the brand-voice scoring, because human review is the gold standard for all generative output
- **D** ❌ Use automatic (programmatic) evaluation for everything, selecting the toxicity and robustness categories to approximate brand voice and empathy

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: subjective qualities (brand voice, empathy) are exactly what scripts miss and humans capture, so human-worker evaluation is the path; nuanced, human-like scoring of thousands of prompts cheaply and at scale is the literal signature of LLM-as-a-judge, which runs at API throughput in hours not weeks. A is the planted Pattern 6 trap — accuracy/F1 require a closed label space and a single correct string, which open-ended support replies lack. C ignores scale: a human-based job caps at up to 1,000 prompts and up to 50 workers, so it cannot do nightly thousands-of-prompts correctness scoring cheaply. D misuses programmatic categories: toxicity and robustness are operational/safety metrics, not measures of brand voice or empathy.

### 5. Key Takeaway
Correct: subjective qualities (brand voice, empathy) are exactly what scripts miss and humans capture, so human-worker evaluation is the path; nuanced, human-like scoring of thousands of prompts cheaply and at scale is the literal signature of LLM-as-a-judge, which runs at API throughput in hours not weeks.

---

## Question 60

### 1. Question Summary
**Scenario:** A RAG chatbot built on an Amazon Bedrock Knowledge Base gives answers that are incomplete — they read fluently and never contradict the sources, but they routinely omit facts the user needed. A retrieve-and-generate Knowledge Base evaluation reports high context relevance, low context coverage, and high faithfulness.

**Ask:** Which stage is at fault, and what is the correct remediation?

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.1

### 3. Option Analysis
- **A** ❌ The generator is hallucinating; add a Guardrails contextual grounding check to block low-grounding responses
- **B** ✅ Retrieval has a recall gap; revisit chunking strategy, increase top-k, or improve the embeddings so the needed facts are retrieved
- **C** ❌ The generator is ignoring good context; switch to a more capable response-generator model and lower the temperature
- **D** ❌ The evaluator model is miscalibrated; re-run the job with a different judge model and supply ground-truth references

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: high context relevance means the retrieved chunks are on-topic and high faithfulness means the generator is correctly grounding its answer in whatever it received, so the generator is behaving well; low context coverage is the recall signal that retrieval is missing some of the information the complete answer needs. Coverage is a retrieval-stage metric, so the fix lives in the retrieval pipeline (chunking, top-k, embeddings). A and C blame the generator, but high faithfulness rules out hallucination and a faithful generator that omits content was simply never handed the missing facts. D misreads the metrics as an evaluator artifact; the three scores are internally consistent and clearly localize the fault to retrieval recall.

### 5. Key Takeaway
Correct: high context relevance means the retrieved chunks are on-topic and high faithfulness means the generator is correctly grounding its answer in whatever it received, so the generator is behaving well; low context coverage is the recall signal that retrieval is missing some of the information the complete answer needs.

---

