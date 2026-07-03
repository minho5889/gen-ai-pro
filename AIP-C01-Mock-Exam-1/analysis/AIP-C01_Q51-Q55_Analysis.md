# AIP-C01 Practice Exam 1 — Analysis (Q51-Q55)

## Question 51

### 1. Question Summary
**Scenario:** A SaaS company runs a document-summarization feature on Amazon Bedrock using an Anthropic Claude model on the default on-demand path. Over three months the Bedrock bill has roughly tripled while request volume has only grown about 40%. Investigation shows the average summary length has crept up (the prompt now asks for an 'exhaustive, comprehensive' summary), and a 2,200-token static instruction block containing tone rules and worked examples is sent on every call. A platform engineer has filed a ticket recommending the team 'move the workload to a larger, GPU-backed instance type and enable compute autoscaling so summaries process faster and more cost-efficiently.'

**Ask:** Which response correctly evaluates the engineer's recommendation and identifies the most appropriate first actions?

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.1

### 3. Option Analysis
- **A** ❌ The recommendation is sound; provision a GPU instance reservation to lock in a lower hourly compute rate and add Auto Scaling to handle the growth
- **B** ✅ The recommendation is a category error because on-demand Bedrock is serverless with no instance to scale; instead bound output length (concise instruction plus a maxTokens ceiling) and apply prompt caching to the repeated static instruction block
- **C** ❌ The recommendation is partially correct; keep the autoscaling plan but also raise the per-model requests-per-minute quota so more compute is allocated per request
- **D** ❌ The recommendation is correct in spirit but should target a smaller EC2 instance, since cost on Bedrock scales with the instance size you select for inference

### 4. Correct Answer Deep-Dive
**Answer: B**

On the default on-demand path Bedrock is fully managed and serverless: the caller never provisions instances, so there is no instance type to enlarge, no GPU to reserve, and no compute-hour meter to optimize. This is the canonical Pattern 4 compute-scaling trap. Cost is driven by token volume, so the correct first moves come from the cheapest levers: bound the costlier output dimension (concise instruction + maxTokens) and cache the repeated 2,200-token static prefix so it is not reprocessed or re-billed at full rate on every call. A and D invent compute and a billing dimension that do not exist on this path. C is wrong because a higher RPM quota does not 'allocate more compute per request' and does not address token-driven cost.

### 5. Key Takeaway
On the default on-demand path Bedrock is fully managed and serverless: the caller never provisions instances, so there is no instance type to enlarge, no GPU to reserve, and no compute-hour meter to optimize.

---

## Question 52

### 1. Question Summary
**Scenario:** A retail company runs a customer-facing FAQ assistant on Amazon Bedrock. Analytics show roughly 70% of incoming questions are paraphrases of a small set of common questions ('how do I reset my password?' vs 'I forgot my password, what do I do?') whose answers are stable for weeks at a time. The remaining 30% are genuinely novel. The team wants to cut both inference cost and latency for the repeated questions, and is willing to build supporting infrastructure on AWS data services.

**Ask:** Which approach best fits the repetition pattern, and what is the key risk to manage?

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.1

### 3. Option Analysis
- **A** ❌ Amazon Bedrock prompt caching, because it returns a stored answer for similar questions without invoking the model; manage the cache-write cost on the first call
- **B** ✅ Semantic caching using a vector cache (for example, ElastiCache for Valkey vector search), because it matches questions by embedding similarity and returns a stored answer without invoking the model; manage the risk of serving a non-equivalent answer by setting a high similarity threshold and a TTL
- **C** ❌ Provisioned Throughput sized to the FAQ volume, because dedicated Model Units cache the common answers in committed capacity; manage the hourly commitment cost
- **D** ❌ Amazon Bedrock prompt caching, because the repeated questions form a static prefix that is reprocessed on each call; manage the per-model minimum token threshold

### 4. Correct Answer Deep-Dive
**Answer: B**

The repetition is in the meaning of the questions, not in a static prefix, and the answers are stable, so semantic caching is the fit: it embeds each query, matches by similarity, and on a hit returns the stored answer so the model is never invoked, saving the full generation cost and latency. Its characteristic correctness risk is serving an answer that is similar in wording but different in intent, bounded by a high minimum-similarity threshold and a TTL matched to how fast the data changes. A and D both misapply prompt caching: prompt caching reduces the cost of an invocation that still occurs by reusing a static prefix, and (A) it does not return a stored answer or skip the model. The varying user questions are not a static prefix. C confuses caching with committed capacity; Provisioned Throughput does not cache answers.

### 5. Key Takeaway
The repetition is in the meaning of the questions, not in a static prefix, and the answers are stable, so semantic caching is the fit: it embeds each query, matches by similarity, and on a hit returns the stored answer so the model is never invoked, saving the full generation cost and latency.

---

## Question 53

### 1. Question Summary
**Scenario:** A media archive company must run a Bedrock foundation model over a back catalog of 250,000 archived articles to generate one-paragraph summaries plus a category label. The results are needed by the end of the week, not in real time, and the goal is the lowest possible cost. An architect proposes building a Bedrock agent that calls an external taxonomy-lookup tool for each article and enforces a strict JSON schema on every response, then running the whole thing as a Bedrock batch inference job to capture the batch discount.

**Ask:** What is the correct assessment of this proposal?

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.1

### 3. Option Analysis
- **A** ✅ Batch inference fits the volume and latency profile, but it processes each record independently and supports neither tool calling nor structured-output formatting, so the agent-with-tools-and-strict-JSON design is incompatible with batch
- **B** ❌ The proposal is correct as designed; batch inference supports tool calling and structured output as long as each record is submitted independently
- **C** ❌ Batch inference is the wrong billing mode entirely; this volume requires Provisioned Throughput because only dedicated Model Units can process 250,000 records
- **D** ❌ The proposal should use on-demand inference with high client-side concurrency, because batch inference is more expensive than on-demand for large jobs

### 4. Correct Answer Deep-Dive
**Answer: A**

The volume-bounded, offline, cost-sensitive shape points correctly to batch inference (asynchronous via S3 at a documented discount vs on-demand). But batch processes each record independently with no multi-turn interaction, so it supports neither tool calling (function calling) nor structured-output response formatting. The agent-with-tools and strict-JSON requirements are therefore incompatible with batch. B is the trap: it asserts a capability batch does not have. C is wrong: Provisioned Throughput is for steady high real-time volume (and custom models), and its always-on hourly meter is the wrong fit for a one-time bounded offline job. D is wrong: batch is documented as cheaper than on-demand, not more expensive.

### 5. Key Takeaway
The volume-bounded, offline, cost-sensitive shape points correctly to batch inference (asynchronous via S3 at a documented discount vs on-demand).

---

## Question 54

### 1. Question Summary
**Scenario:** An interactive coding-assistant on Amazon Bedrock receives two distinct complaints in the same sprint. Team A (end users) reports: 'After I hit send, the screen is blank for four to five seconds before any text appears — it feels frozen.' Team B (data platform) runs a nightly job that classifies 40,000 log entries through the same model and reports: 'The job takes far too long to finish end-to-end and keeps failing with ThrottlingException partway through.' A junior engineer proposes a single fix for both: 'lower the temperature parameter and enable response streaming.'

**Ask:** Why does the single proposed fix fail to address both complaints, and what correctly addresses each?

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.2

### 3. Option Analysis
- **A** ❌ Lowering temperature speeds up generation, so it fixes Team B; streaming fixes Team A — the proposal is correct for both
- **B** ✅ Streaming addresses Team A's perceived-latency (time-to-first-token) complaint, but neither streaming nor temperature helps Team B; Team B needs concurrency managed within the per-model RPM/TPM quotas with retries and backoff (and a committed-capacity option such as Provisioned Throughput or Cross-Region Inference for sustained volume)
- **C** ❌ Streaming fixes both, because incremental token delivery also reduces total batch completion time by parallelizing token production
- **D** ❌ Temperature fixes both, because a lower-temperature model produces shorter responses, which both speeds up the interactive screen and reduces the nightly job's total time

### 4. Correct Answer Deep-Dive
**Answer: B**

The two complaints are different problems. Team A's blank-screen wait is a perceived-latency problem on a single request; streaming (ConverseStream / InvokeModelWithResponseStream) surfaces the first token at TimeToFirstToken, fixing it — but streaming does not reduce total generation time. Team B's problem is throughput plus throttling, governed by per-model RPM/TPM quotas: raising concurrency past the quota only generates ThrottlingException, so the fix is managed concurrency within the quota with retries/backoff, and Provisioned Throughput or Cross-Region Inference for sustained volume. Temperature is a randomness/quality control with no direct latency or cost effect, so it helps neither (A, D wrong). C is the classic streaming trap: streaming changes delivery, not generation wall-clock time.

### 5. Key Takeaway
The two complaints are different problems.

---

## Question 55

### 1. Question Summary
**Scenario:** A RAG-backed legal-research assistant on Amazon Bedrock with a Knowledge Base has two problems: time to first token is high (users wait several seconds before any text appears) and the per-call input-token cost is high. Investigation shows every query retrieves 50 chunks of about 2,000 characters each and injects all of them into the prompt. The model and prompt template have already been quality-validated and the team does not want to change the model. Answer correctness is currently acceptable and must not regress.

**Ask:** Which change most directly reduces both the high time-to-first-token and the high input-token cost?

### 2. Domain Mapping
**Domain:** Domain 4: Operational Efficiency and Optimization
**Task:** Task 4.2

### 3. Option Analysis
- **A** ❌ Lower the temperature and top-p so the model samples fewer candidate tokens during prefill, shrinking the input cost
- **B** ❌ Enable response streaming so the first token appears sooner, which also lowers the input-token bill
- **C** ✅ Tune the retrieval configuration to return fewer, better-targeted chunks (reduce numberOfResults and add reranking), since a smaller retrieved context shortens the prefill phase and lowers input-token volume — while monitoring that answer quality does not drop
- **D** ❌ Increase maxTokens so the model can finish faster, reducing the decode phase that is driving time to first token

### 4. Correct Answer Deep-Dive
**Answer: C**

Both symptoms trace to retrieval volume: 50 large chunks form a large input payload, which lengthens the prefill phase (raising TimeToFirstToken) and inflates input-token cost on every call. Retrieving fewer, better-targeted chunks (lower numberOfResults, add reranking) shrinks the prefill and the input bill at once — a two-for-one lever — with the guardrail of not starving the model of needed context. A is wrong: temperature/top-p shape output randomness, not prefill or input cost. B is wrong: streaming improves perceived latency but does nothing for input-token cost and does not shrink the oversized prefill driving TTFT. D is wrong: maxTokens bounds the decode (output) phase, not prefill/TTFT, and raising it cannot reduce input cost.

### 5. Key Takeaway
Both symptoms trace to retrieval volume: 50 large chunks form a large input payload, which lengthens the prefill phase (raising TimeToFirstToken) and inflates input-token cost on every call.

---

