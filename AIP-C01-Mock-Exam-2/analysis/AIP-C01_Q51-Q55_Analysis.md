# AIP-C01 Practice Exam 2 — Analysis (Q51-Q55)

## Question 51

### 1. Question Summary
**Scenario:** A retail company serves a recommendation-explanation feature on Amazon Bedrock using an on-demand foundation model. Traffic is highly diurnal: roughly 90% of all daily invocations land in a four-hour evening window, and the remaining 20 hours are near idle. During the evening peak, on-demand throttling (ThrottlingException) is breaking the experience even after a quota-increase request. A platform engineer proposes purchasing a six-month Provisioned Throughput commitment sized to the evening peak to guarantee capacity and lock in the deepest discount.

**Ask:** Why is the proposed six-month Provisioned Throughput commitment a poor cost-optimization decision for this workload, and what is the more defensible way to address the evening throttling?

### 2. Domain Mapping
**Domain:** Task 4.1 — Cost optimization (Provisioned Throughput economics and the always-on meter)
**Task:** Task 4.1

### 3. Option Analysis
- **A** ❌ It is sound — a six-month commitment earns the deepest discount and guarantees the peak capacity, so it is the correct cost optimization
- **B** ✅ The Provisioned Throughput hourly meter bills the committed Model Units continuously whether or not traffic flows, so a commitment sized to a 4-hour peak would pay for ~20 idle hours a day; address the bursts with Cross-Region Inference to draw on additional Regions' on-demand capacity, or reserve Provisioned Throughput only if sustained volume later justifies it
- **C** ❌ Provisioned Throughput cannot be used for diurnal traffic at all because Model Units expire when idle, so the commitment would be automatically refunded for the idle hours
- **D** ❌ Switch the evening peak to batch inference, which provides guaranteed real-time capacity at a discount while smoothing the bursts

### 4. Correct Answer Deep-Dive
**Answer: B**

Provisioned Throughput is a fixed hourly commitment that bills the provisioned Model Units continuously until the model is deleted, independent of traffic — so sizing a commitment (especially a six-month lock-in) to a 4-hour daily peak pays for roughly 20 idle hours every day, which is more expensive than on-demand for this shape. Provisioned Throughput is cost-effective only for steady, high, sustained volume that keeps the dedicated capacity busy. The defensible fix for bursty traffic that throttles one Region is Cross-Region Inference, which routes requests across additional Regions' capacity at no extra routing/data-transfer cost. A is the trap (the discount is irrelevant if capacity sits idle). C invents a refund/expiry mechanism that does not exist. D is wrong because batch inference is asynchronous and cannot serve real-time interactive traffic.

### 5. Key Takeaway
Provisioned Throughput is a fixed hourly commitment that bills the provisioned Model Units continuously until the model is deleted, independent of traffic — so sizing a commitment (especially a six-month lock-in) to a 4-hour daily peak pays for roughly 20 idle hours every day, which is more expensive than on-demand for this shape.

---

## Question 52

### 1. Question Summary
**Scenario:** An SRE team builds a standing CloudWatch dashboard and alarm set for a high-volume Bedrock workload. To watch capacity pressure they create a metric-math alarm defined as (InvocationClientErrors + InvocationServerErrors) / Invocations, expecting it to fire when the workload starts hitting its tokens-per-minute ceiling at peak. During the next traffic surge users report failures, but the alarm never fires even though the workload was clearly rejecting requests.

**Ask:** Why did the capacity-pressure alarm fail to fire, and how should the team alarm on quota-driven rejections?

### 2. Domain Mapping
**Domain:** Task 4.3 — Monitoring (the AWS/Bedrock throttle metric accounting trap)
**Task:** Task 4.3

### 3. Option Analysis
- **A** ❌ The error metrics are only emitted for streaming operations, so the team must switch to ConverseStream for the alarm to populate
- **B** ✅ Quota-driven rejections are published as InvocationThrottles, a distinct metric that is counted as neither an Invocation nor a client/server error, so it never appears in the error-rate expression; alarm on InvocationThrottles SampleCount directly (and optionally watch EstimatedTPMQuotaUsage for headroom trending)
- **C** ❌ The expression is correct but the evaluation period was too short; lengthening it to 24 hours will surface the throttles
- **D** ❌ Throttled requests are recorded in InvocationServerErrors, so the alarm should have fired — the real cause is that anomaly detection was disabled on the metric

### 4. Correct Answer Deep-Dive
**Answer: B**

In the AWS/Bedrock namespace there is no aggregate error metric, and a throttled request is counted as neither an Invocation (it never succeeded) nor an InvocationClientErrors/InvocationServerErrors value — it lives only in InvocationThrottles. So an error-rate expression built from the two error metrics structurally cannot detect quota throttling. The fix is to alarm on InvocationThrottles directly; EstimatedTPMQuotaUsage (an AWS-stated approximation) helps trend headroom toward the ceiling. A is false — the error/throttle metrics are not streaming-only. C cannot help because the throttle count is absent from the expression regardless of period length. D misstates the accounting (throttles are not server errors).

### 5. Key Takeaway
In the AWS/Bedrock namespace there is no aggregate error metric, and a throttled request is counted as neither an Invocation (it never succeeded) nor an InvocationClientErrors/InvocationServerErrors value — it lives only in InvocationThrottles.

---

## Question 53

### 1. Question Summary
**Scenario:** A document-intelligence pipeline calls a Bedrock model and forwards the model's complete generated response to a downstream parser that cannot begin work until the entire response is available. Operators complain that the end-to-end pipeline latency per document is too high. An engineer proposes switching the call from InvokeModel to InvokeModelWithResponseStream so the response 'comes back faster,' and separately proposes lowering the temperature to '0' to speed up generation.

**Ask:** Evaluate the two proposals against this pipeline's actual latency problem.

### 2. Domain Mapping
**Domain:** Task 4.2 — Performance optimization (perceived vs total latency; the streaming trap)
**Task:** Task 4.2

### 3. Option Analysis
- **A** ❌ Both proposals reduce end-to-end latency: streaming returns the full response sooner and temperature 0 reduces the number of decode steps
- **B** ✅ Neither proposal reduces the latency that matters here. Streaming only improves perceived latency (time to first token) and leaves total InvocationLatency unchanged — and since the parser needs the whole response, perceived latency is irrelevant. Temperature is a randomness/quality control with no direct effect on latency. The real lever is shortening the decode phase: bound output with maxTokens and/or use a faster or latency-optimized model
- **C** ❌ Streaming is correct because it cuts total generation time roughly in half; the temperature change is the only mistake
- **D** ❌ Lower temperature is correct because deterministic output finishes generating faster; streaming is the mistake because it adds event-parsing overhead that increases total latency

### 4. Correct Answer Deep-Dive
**Answer: B**

The downstream parser consumes the whole response, so only total latency (InvocationLatency, the time to the last token) matters; perceived latency is irrelevant when no human is watching a screen. Streaming changes delivery, not generation — the model performs the same prefill and per-token decode passes in the same wall-clock time, so InvocationLatency is unchanged. Temperature, top-k, and top-p shape output randomness/quality, not the number of forward passes, so they do not directly affect latency or cost. Total latency is driven by the output-token count in the decode loop, so the levers are maxTokens and a faster/latency-optimized model. A, C, and D each repeat one of the two canonical traps (streaming reduces total time / sampling params change speed).

### 5. Key Takeaway
The downstream parser consumes the whole response, so only total latency (InvocationLatency, the time to the last token) matters; perceived latency is irrelevant when no human is watching a screen.

---

## Question 54

### 1. Question Summary
**Scenario:** A brokerage builds a customer assistant on Bedrock and adds a customer-implemented semantic cache (Amazon ElastiCache for Valkey vector search) to cut inference cost on repeated questions. Two question types dominate traffic: (1) 'What are your account-maintenance fees?' (policy text that changes a few times a year) and (2) 'What is the current price of <ticker>?' (live market data that changes by the second). To maximize the hit rate and savings, an engineer sets a single low similarity threshold and a single 24-hour TTL across all cached entries.

**Ask:** What is the most significant correctness risk introduced by this configuration, and what is the appropriate mitigation?

### 2. Domain Mapping
**Domain:** Task 4.1 — Cost optimization (semantic caching correctness risk; data freshness)
**Task:** Task 4.1

### 3. Option Analysis
- **A** ❌ There is no correctness risk because semantic caching always re-validates the cached answer against the live model before returning it
- **B** ✅ The low similarity threshold plus a uniform 24-hour TTL will serve stale and non-equivalent answers — especially for live-price queries, where even an exact-intent hit is stale within seconds, and for fee queries where similar-but-different intents collide. Raise the similarity threshold (high, e.g. ~0.95, for low-risk-tolerance financial content), and exclude or short-TTL the dynamic price queries; reserve caching for the stable-answer, repeated questions
- **C** ❌ The only risk is reduced savings; lower the threshold further and shorten the TTL to 1 hour for all entries to fix it
- **D** ❌ Switch from semantic caching to Bedrock prompt caching, which eliminates the correctness risk because it also returns stored answers without invoking the model

### 4. Correct Answer Deep-Dive
**Answer: B**

Semantic caching returns a stored answer in place of a fresh generation, so it carries a genuine staleness/equivalence risk that grows as the similarity threshold is lowered. Live market prices are a poor cache candidate at any threshold because even a correct-intent match is stale within seconds, and a low threshold lets similar-but-distinct fee questions collide. The mitigation is a high similarity threshold for low-risk-tolerance financial content, a TTL matched to data volatility (very short or no caching for live prices, longer for stable policy text), and restricting caching to repeated, stable-answer queries. A is false (semantic caching does not re-validate; that would defeat the savings). C makes the risk worse. D misdescribes prompt caching — prompt caching still invokes the model and caches a static prefix, it does not return stored answers.

### 5. Key Takeaway
Semantic caching returns a stored answer in place of a fresh generation, so it carries a genuine staleness/equivalence risk that grows as the similarity threshold is lowered.

---

## Question 55

### 1. Question Summary
**Scenario:** A RAG assistant built on Amazon Bedrock Knowledge Bases is both slow to show its first token and expensive per call. Investigation shows the retrieval configuration sets numberOfResults to a large value, every retrieved chunk is large, and a reranking pass is not used. The team confirms answers are accurate (they are not missing context), but TimeToFirstToken is high and InputTokenCount per call is large. They want to reduce both the perceived latency and the per-call cost without dropping below the answer-quality bar.

**Ask:** Which change most directly addresses both the high TimeToFirstToken and the high input-token cost for this RAG workload?

### 2. Domain Mapping
**Domain:** Task 4.2 — Performance optimization (RAG retrieval/index latency and input-token cost)
**Task:** Task 4.2

### 3. Option Analysis
- **A** ❌ Enable response streaming so the first token appears sooner; this also lowers the input-token cost
- **B** ✅ Reduce the volume of retrieved context — lower numberOfResults and/or use a reranker (e.g., the Bedrock Rerank API) to send fewer but more pertinent chunks — which shrinks the prompt, shortening the prefill phase (lower TTFT) and lowering input-token cost, while monitoring that answer quality stays above the bar
- **C** ❌ Raise the model's maxTokens ceiling so the prefill phase completes faster
- **D** ❌ Move the workload to Provisioned Throughput, which reduces both prefill latency and input-token billing for retrieved context

### 4. Correct Answer Deep-Dive
**Answer: B**

Retrieved-context volume drives the input-token count, and input tokens are exactly what the prefill phase processes — so a larger context means a longer prefill (higher TimeToFirstToken) and a higher input-token bill on every call. Retrieving fewer, better-targeted chunks (lower numberOfResults, reranking to keep only the most pertinent results) shrinks the prompt and improves both dimensions at once, provided quality stays above the bar (the scenario confirms the context is currently more than needed). A is wrong on cost — streaming improves perceived latency but does not change the input-token count or cost. C is wrong — maxTokens bounds output (decode/total latency and output cost), not prefill or input cost. D conflates a billing-mode commitment with token volume; Provisioned Throughput changes neither prefill time nor input-token count.

### 5. Key Takeaway
Retrieved-context volume drives the input-token count, and input tokens are exactly what the prefill phase processes — so a larger context means a longer prefill (higher TimeToFirstToken) and a higher input-token bill on every call.

---

