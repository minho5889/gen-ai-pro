# AIP-C01 Practice Exam 1 — Analysis (Q61-Q65)

## Question 61

### 1. Question Summary
**Scenario:** An ML platform team uses LLM-as-a-judge in Amazon Bedrock to benchmark several candidate models. A reviewer raises two concerns: (1) one candidate model is from the same family as the chosen judge model, and (2) re-running the same evaluation produces slightly different scores between runs. The comparison feeds a high-stakes go/no-go launch decision.

**Ask:** Which approach correctly addresses both concerns using AWS-recommended practices?

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.1

### 3. Option Analysis
- **A** ❌ Supply a custom in-house judge model that shares no architecture with any candidate, and accept a single run as authoritative since the custom judge removes all bias
- **B** ✅ Use a consistent evaluator model and fixed configuration across all comparisons for reproducibility, and add human spot checks for this critical comparison given the self-preference risk from the shared-family candidate
- **C** ❌ Switch the metric set to the automatic accuracy/robustness/toxicity categories, because programmatic metrics are deterministic and bias-free
- **D** ❌ Increase the number of prompts to 10,000 so the larger sample averages out both the non-determinism and the self-preference bias without any human review

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: AWS recommends a consistent evaluator model and documented configuration for reproducible cross-model benchmarking (foundation models, including the judge, are non-deterministic), and recommends occasional human spot checks for critical comparisons — especially relevant here because a candidate shares a family/architecture with the judge (self-preference/architectural-bias risk). A is the classic trap: you cannot bring your own judge model — judge models are AWS-curated from the Nova/Claude/Llama/Mistral families; and no judge is bias-free, so a single run is not authoritative for a high-stakes decision. C abandons the semantic, human-like judgment the scenario needs and the automatic categories do not measure the same qualities. D wrongly assumes more prompts cancels a systematic self-preference bias (it does not) and explicitly drops the human calibration AWS recommends for critical comparisons.

### 5. Key Takeaway
Correct: AWS recommends a consistent evaluator model and documented configuration for reproducible cross-model benchmarking (foundation models, including the judge, are non-deterministic), and recommends occasional human spot checks for critical comparisons — especially relevant here because a candidate shares a family/architecture with the judge (self-preference/architectural-bias risk).

---

## Question 62

### 1. Question Summary
**Scenario:** A service calls Amazon Bedrock at high concurrency. Under load it returns frequent HTTP 429 ThrottlingExceptions. Separately, a batch of requests carrying very long prompts consistently fails with ValidationException no matter how many times they are retried. The team currently wraps every Bedrock call in a single exponential-backoff-with-jitter retry loop.

**Ask:** What is the correct way to handle these two failure clusters?

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.2

### 3. Option Analysis
- **A** ❌ Keep one retry loop and catch a ContextWindowOverflow exception to separate the long-prompt failures from the throttles
- **B** ❌ Apply exponential backoff with jitter to both, and raise max_tokens on the throttled calls so they finish in fewer retries
- **C** ✅ Retry the ThrottlingExceptions with backoff and jitter, and stop retrying the ValidationExceptions — instead shorten/chunk the prompt or lower max_tokens
- **D** ❌ Remove all retry logic and rely on cross-Region inference profiles to eliminate both error types automatically

### 4. Correct Answer Deep-Dive
**Answer: C**

Correct: exponential backoff with jitter is for transient errors only (ThrottlingException, ModelTimeoutException, ServiceUnavailableException, InternalServerException, network), so it is right for the 429s. ValidationException is a non-retryable client error — the long prompt exceeds the model's max context length, so retrying can never succeed; the fix is to correct the request. A names a nonexistent exception: there is no ContextWindowOverflow — input-too-long surfaces as ValidationException. B is the planted trap (do not retry ValidationException) and also worsens throttling, because Bedrock deducts input + max_tokens from the TPM quota up front, so raising max_tokens consumes quota faster. D throws away the AWS-prescribed backoff for transient throttles; cross-Region profiles add capacity but do not fix a malformed (too-long) request.

### 5. Key Takeaway
Correct: exponential backoff with jitter is for transient errors only (ThrottlingException, ModelTimeoutException, ServiceUnavailableException, InternalServerException, network), so it is right for the 429s.

---

## Question 63

### 1. Question Summary
**Scenario:** A CloudWatch alarm fires because InvocationLatency on a streaming chat workload built on Amazon Bedrock ConverseStream has climbed steadily over the past week. Before paging the on-call engineer, the team wants to determine whether this is a workload change (users requesting longer answers) or a genuine service-side throughput degradation, because the remediation differs.

**Ask:** Which single derived signal lets the team distinguish the two causes, and how is it interpreted?

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.2

### 3. Option Analysis
- **A** ❌ EstimatedTPMQuotaUsage — if it is near the quota ceiling, the model is generating tokens more slowly
- **B** ✅ Output Tokens Per Second (OTPS), computed from OutputTokenCount, InvocationLatency, and TimeToFirstToken — stable OTPS means longer outputs (workload change); dropping OTPS means service-side throughput degradation
- **C** ❌ InvocationThrottles — a rising throttle count proves the increased latency is caused by quota throttling
- **D** ❌ A built-in AWS/Bedrock response-latency-quality metric that flags whether slow responses are also low quality

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: OTPS = OutputTokenCount / (InvocationLatency - TimeToFirstToken) * 1000 decomposes latency that looks identical on a chart. Stable OTPS with high latency means per-token throughput is fine and the model is simply producing longer outputs (workload change — cap max_tokens/tighten prompt); dropping OTPS means each token is generated more slowly (genuine service-side degradation worth paging on). This works on streaming traffic because TimeToFirstToken is emitted for streaming operations only, which matches the ConverseStream workload. A misuses EstimatedTPMQuotaUsage — AWS warns it is an approximation, and quota usage does not decompose latency. C conflates throttling with latency; throttled requests are a separate signal and do not explain rising InvocationLatency. D names a metric that does not exist — AWS/Bedrock is operational only.

### 5. Key Takeaway
Correct: OTPS = OutputTokenCount / (InvocationLatency - TimeToFirstToken) * 1000 decomposes latency that looks identical on a chart.

---

## Question 64

### 1. Question Summary
**Scenario:** Before promoting a new foundation model to a high-traffic Bedrock-backed assistant, a team needs to observe how it behaves on genuine production inputs — real phrasing, real edge cases, real load — but is unwilling to expose even a single user to a potentially bad response. An architect proposes 'just enable a Bedrock deployment guardrail that splits endpoint traffic and rolls back on a CloudWatch alarm.'

**Ask:** Which response correctly identifies the validation pattern and corrects the architect's assumption?

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.1

### 3. Option Analysis
- **A** ❌ Use a canary deployment routing 1-5% of live traffic to the new model; this is the only zero-exposure option and Bedrock provides the traffic-splitting natively
- **B** ✅ Use shadow testing — mirror a copy of live traffic to the new model and log its responses without serving them; Bedrock has no native endpoint traffic-splitting, so implement this at the application/routing layer
- **C** ❌ Use A/B testing on a small slice and compare user-feedback scores; the architect is correct that Bedrock deployment guardrails handle the rollback
- **D** ❌ Use a CloudWatch Synthetics canary to mirror production traffic to the new model with automatic rollback via a Bedrock deployment guardrail

### 4. Correct Answer Deep-Dive
**Answer: B**

Correct: shadow testing mirrors a copy of live traffic to the new variant and logs its responses but never serves them, so it validates behavior under genuine production conditions with zero user-facing risk — exactly the requirement. The architect's assumption is wrong: production variants, shadow production variants, and deployment guardrails with alarm-driven rollback are Amazon SageMaker AI capabilities; Bedrock has no native endpoint traffic-splitting and these patterns are implemented at the application/routing layer. A is wrong twice: a canary exposes a small live slice (not zero exposure) and Bedrock does not split endpoint traffic natively. C exposes real users via A/B and repeats the false Bedrock-guardrail claim. D conflates a CloudWatch Synthetics canary (a scripted synthetic-traffic monitor, not a live-traffic mirror) with shadow testing and again invents a Bedrock deployment guardrail.

### 5. Key Takeaway
Correct: shadow testing mirrors a copy of live traffic to the new variant and logs its responses but never serves them, so it validates behavior under genuine production conditions with zero user-facing risk — exactly the requirement.

---

## Question 65

### 1. Question Summary
**Scenario:** A team is hardening the release process for a RAG application on Amazon Bedrock. They want two guarantees grounded in AWS's named guidance: (1) no release should ship if answer faithfulness regresses below the recorded baseline, and (2) a new RAG configuration must be validated against real production inputs with zero user exposure before any rollout.

**Ask:** Which THREE statements correctly describe AWS-aligned ways to meet these requirements? (Select THREE)

### 2. Domain Mapping
**Domain:** Domain 5: Testing, Validation, and Troubleshooting
**Task:** Task 5.1

### 3. Option Analysis
- **A** ✅ Implement a golden-dataset regression quality gate that re-runs a fixed ground-truth dataset against the candidate, scores faithfulness, and fails the build when scores drop below a predefined threshold (AWS Prescriptive Guidance CI/CD gate)
- **B** ✅ Establish the baseline-before-change discipline against ground-truth data per the Well-Architected Generative AI Lens best practice GENOPS03-BP01 ('Implement prompt template management')
- **C** ✅ Use shadow testing to validate the new configuration on a mirrored copy of production traffic whose responses are logged but never served, satisfying zero user exposure
- **D** ❌ Enable a built-in CloudWatch hallucination-rate metric in the AWS/Bedrock namespace and fail the build automatically when it exceeds a threshold
- **E** ❌ Credit the automated 'fail-the-build-below-threshold' quality gate to the Well-Architected Generative AI Lens, since the Lens owns all CI/CD quality gates
- **F** ❌ Use a canary deployment routing 5% of live traffic to the new configuration, since a small live slice is functionally equivalent to zero user exposure

### 4. Correct Answer Deep-Dive
**Answer: A, B, C**

Correct: A is the regression gate — re-running a fixed golden dataset, scoring (e.g., faithfulness), and failing the build below a predefined threshold, which AWS Prescriptive Guidance owns. B is the baseline discipline from the Generative AI Lens GENOPS03-BP01 (whose verified title is 'Implement prompt template management,' yet whose content prescribes capturing a baseline against ground-truth data). C is shadow testing, the zero-exposure pattern (mirrored, logged, never served). D names a metric that does not exist — AWS/Bedrock is operational only, so the quality signal must be derived (Guardrails grounding scores, golden-dataset/judge custom metrics, or Logs Insights). E misattributes ownership: the automated CI/CD gate is AWS Prescriptive Guidance, while the Lens owns the baseline-and-ground-truth discipline. F is wrong because a canary exposes a small live slice of real users (1-5%), which is not zero exposure.

### 5. Key Takeaway
Correct: A is the regression gate — re-running a fixed golden dataset, scoring (e.g., faithfulness), and failing the build below a predefined threshold, which AWS Prescriptive Guidance owns.

---

