# AIP-C01 Practice Exam 2 — Analysis (Q61-Q65)

## Question 61

### 1. Question Summary
**Scenario:** A bank is replacing the foundation model behind a high-traffic loan-explanation assistant. The change is high-stakes, and compliance forbids exposing any customer to a potentially incorrect explanation from the new model. The team still wants to know how the new model behaves on the bank's actual production request distribution — real phrasing, real edge cases, real load — before any decision to roll it out. The assistant is built on Amazon Bedrock (no SageMaker endpoints).

**Ask:** Which validation approach meets both the zero-exposure requirement and the real-traffic requirement, and how is it implemented for a Bedrock workload?

### 2. Domain Mapping
**Domain:** Task 5.1 — Deployment-time validation
**Task:** Task 5.1

### 3. Option Analysis
- **A** ✅ Shadow testing — dual-invoke production and shadow models on each request in application code, serve only the production response, and log the shadow response for offline comparison
- **B** ❌ Canary deployment — use a Bedrock deployment guardrail to route 5% of live traffic to the new model and auto-roll-back on a CloudWatch alarm
- **C** ❌ A/B testing — split live traffic and compare user feedback scores between the two models
- **D** ❌ CloudWatch Synthetics canary — drive the new model with scripted synthetic traffic on a schedule

### 4. Correct Answer Deep-Dive
**Answer: A**

Shadow testing gives both properties: the shadow receives a copy of real production traffic but its responses are logged and never served, so no customer is exposed. For a Bedrock workload there is no managed shadow variant, so you implement it at the application layer by dual-invoking both models on the same request and logging the shadow output. B is wrong on two counts: it exposes 5% of real users (not zero exposure), and Bedrock has no built-in deployment guardrail/endpoint traffic-splitting — that is a SageMaker mechanism. C exposes users and reads the wrong signal for this goal. D uses synthetic, not real production, traffic, so it does not meet the real-traffic-distribution requirement.

### 5. Key Takeaway
Shadow testing gives both properties: the shadow receives a copy of real production traffic but its responses are logged and never served, so no customer is exposed.

---

## Question 62

### 1. Question Summary
**Scenario:** A production service calls Amazon Bedrock under bursty load. The team wraps all InvokeModel calls in an exponential-backoff-with-jitter retry loop using the botocore Config retries setting. After deployment, HTTP 429 ThrottlingExceptions are handled well, but the team observes that a subset of requests still fail after exhausting all retry attempts, each ending in AccessDeniedException, and another subset fail immediately with ValidationException for long-document prompts.

**Ask:** What is the root-cause issue with the current retry design?

### 2. Domain Mapping
**Domain:** Task 5.2 — Troubleshooting FM API errors
**Task:** Task 5.2

### 3. Option Analysis
- **A** ❌ The retry mode should be 'adaptive' instead of 'standard'; switching it will resolve both the AccessDeniedException and the ValidationException failures
- **B** ✅ Exponential backoff is being applied to non-retryable client errors; AccessDeniedException is an authorization fix and ValidationException is a request-size fix — neither can ever succeed by retrying
- **C** ❌ The max_attempts value is too low; raising it will eventually allow the AccessDeniedException and ValidationException requests to succeed
- **D** ❌ Bedrock requires a cross-Region inference profile for retries to work, and its absence is causing both error types

### 4. Correct Answer Deep-Dive
**Answer: B**

AWS specifies exponential backoff for transient errors only — ThrottlingException, ModelTimeoutException, ServiceUnavailableException, InternalServerException, and network errors — and explicitly warns NOT to retry ValidationException or AccessDeniedException. AccessDeniedException is an authorization/permissions problem; ValidationException (here, the long-document prompt exceeding the model's max context length) is a malformed-for-this-model request. Retrying either wastes calls and can never succeed. The fixes are to correct IAM permissions and to shrink/chunk the input or lower max_tokens. A, C, and D all assume a retry-configuration tweak can fix non-retryable client errors, which is the canonical trap.

### 5. Key Takeaway
AWS specifies exponential backoff for transient errors only — ThrottlingException, ModelTimeoutException, ServiceUnavailableException, InternalServerException, and network errors — and explicitly warns NOT to retry ValidationException or AccessDeniedException.

---

## Question 63

### 1. Question Summary
**Scenario:** An Amazon Bedrock workload sends prompts that comfortably fit well within the chosen model's maximum context window. The application sets max_tokens to 32,000 to be safe, even though typical completions are under 1,200 tokens. Under modest, steady request volume the team is surprised to be throttled with HTTP 429 ThrottlingException carrying the message 'Too many tokens, please wait before trying again,' even though request-per-minute volume is low.

**Ask:** What is causing the throttling, and what is the most direct remediation?

### 2. Domain Mapping
**Domain:** Task 5.2 — Troubleshooting throttling vs context window
**Task:** Task 5.2

### 3. Option Analysis
- **A** ❌ The prompt exceeds the context window; switch to a model with a larger context window
- **B** ✅ Bedrock deducts (input tokens + max_tokens) from the TPM quota at the start of each request, so the oversized max_tokens inflates the deduction and trips the token-rate quota — reduce max_tokens to the expected completion size
- **C** ❌ The model is generating tokens too slowly; enable latency-optimized inference to reduce token-rate pressure
- **D** ❌ ThrottlingException on tokens is only request-rate based; add exponential backoff and the issue will clear without other changes

### 4. Correct Answer Deep-Dive
**Answer: B**

Bedrock enforces TPM and RPM quotas concurrently, and at the start of every request it deducts (Total input tokens + max_tokens) from the TPM/TPD quota. An oversized max_tokens (32,000) inflates that up-front deduction far beyond the ~1,200 tokens actually generated, so it can trip the token-rate quota even when prompt size and request volume are both modest — exactly the 'Too many tokens' message. The direct fix AWS prescribes is to reduce max_tokens. A is wrong because the prompt already fits the context window — this is a quota issue, not an input-too-long issue. C confuses throughput with quota deduction. D is wrong because the message proves throttling can be token-rate based, and backoff alone treats the symptom while the oversized max_tokens keeps re-triggering it.

### 5. Key Takeaway
Bedrock enforces TPM and RPM quotas concurrently, and at the start of every request it deducts (Total input tokens + max_tokens) from the TPM/TPD quota.

---

## Question 64

### 1. Question Summary
**Scenario:** A RAG application worked well at launch. To improve quality, an engineer swaps the embedding model used by the Amazon Bedrock Knowledge Base to a newer Titan embedding model and redeploys. Immediately afterward, retrieval quality collapses: queries return chunks that are nearly random, context relevance scores plummet, and answers become unusable — even though the underlying documents and the generator model are unchanged.

**Ask:** What is the root cause, and what must the team do to restore retrieval quality?

### 2. Domain Mapping
**Domain:** Task 5.2 — RAG retrieval/embedding diagnostics
**Task:** Task 5.2

### 3. Option Analysis
- **A** ❌ The new embedding model is lower quality; revert the application code to the previous deployment and no data changes are needed
- **B** ✅ Query vectors are now produced by the new model while the stored chunk vectors were produced by the old model, so they occupy different vector spaces — re-ingest/sync the data source so the corpus is re-embedded with the new model
- **C** ❌ The reranker is misconfigured for the new embeddings; enable the Rerank API and the existing index will work as-is
- **D** ❌ The Knowledge Base needs a larger top-k to compensate for the new embedding dimensions; raise top-k and the issue resolves

### 4. Correct Answer Deep-Dive
**Answer: B**

Changing the embedding model changes how queries are encoded, but the stored chunk vectors were encoded by the OLD model and were not automatically re-computed. Query and document vectors now live in incompatible vector spaces, so similarity search returns near-random matches. AWS requires that changing the embedding configuration be followed by re-ingesting/syncing the data source, which re-parses, re-chunks, re-embeds, and re-indexes the corpus with the new model. The operating rule is one consistent embedding model for both query and corpus. A is wrong because reverting code alone leaves a corpus that still must match whatever model the queries use, and the symptom is a space mismatch, not model quality. C and D try to compensate downstream for a fundamental embedding-space mismatch that only re-embedding can fix.

### 5. Key Takeaway
Changing the embedding model changes how queries are encoded, but the stored chunk vectors were encoded by the OLD model and were not automatically re-computed.

---

## Question 65

### 1. Question Summary
**Scenario:** A platform team is hardening the release process for a Bedrock-based generative assistant. They want offline quality gates plus the right runtime instrumentation to troubleshoot incidents. During design review, several proposals are made about what to put in CI/CD and what signals to monitor in CloudWatch. The team is on the bedrock-runtime endpoint and uses streaming (ConverseStream) for the chat path.

**Ask:** Which TWO actions are correct and defensible against AWS documentation? (Select TWO.)

### 2. Domain Mapping
**Domain:** Task 5.1/5.2 — Evaluation and troubleshooting design judgment
**Task:** Task 5.1

### 3. Option Analysis
- **A** ✅ Add a regression quality gate that re-runs a fixed golden dataset against each candidate version and fails the build if scores fall below the recorded baseline threshold
- **B** ❌ Rely on a built-in AWS/Bedrock 'HallucinationRate' CloudWatch metric to alarm on hallucinations, since Bedrock emits it automatically once invocation logging is enabled
- **C** ✅ Derive Output Tokens Per Second (OTPS) from OutputTokenCount, InvocationLatency, and TimeToFirstToken to distinguish a workload change (stable OTPS) from a service-side throughput degradation (dropping OTPS) when InvocationLatency rises
- **D** ❌ Assume Amazon Bedrock Model Invocation Logging captures every request and response automatically, so no enablement step is needed before incidents occur
- **E** ❌ Use exact-match accuracy and F1 as the primary golden-dataset metrics for the open-ended chat outputs, since they are the most objective scores available

### 4. Correct Answer Deep-Dive
**Answer: AC**

A is correct: the golden-dataset regression quality gate that re-runs a fixed dataset and fails the build below the recorded baseline is the AWS-prescribed offline gate (GENPERF01-BP01 ground truth + CI/CD quality gate). C is correct: AWS documents OTPS = OutputTokenCount / (InvocationLatency − TimeToFirstToken) × 1000 to decompose a latency rise into a workload change (stable OTPS) versus throughput degradation (dropping OTPS), and TimeToFirstToken is available because the chat path streams. B is wrong: there is NO native AWS/Bedrock quality/hallucination-rate metric — the quality signal must be derived from Guardrails grounding scores, golden-dataset/judge custom metrics, or Logs Insights. D is wrong: Model Invocation Logging is disabled by default and must be explicitly enabled with a destination configured in advance. E is wrong: exact-match accuracy/F1 need a closed output space and a single correct label, which open-ended chat lacks — use semantic (BERTScore) or LLM-as-a-judge scoring.

### 5. Key Takeaway
A is correct: the golden-dataset regression quality gate that re-runs a fixed dataset and fails the build below the recorded baseline is the AWS-prescribed offline gate (GENPERF01-BP01 ground truth + CI/CD quality gate).

---

