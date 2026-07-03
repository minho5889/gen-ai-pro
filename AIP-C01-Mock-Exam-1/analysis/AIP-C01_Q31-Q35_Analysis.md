# AIP-C01 Practice Exam 1 — Analysis (Q31-Q35)

## Question 31

### 1. Question Summary
**Scenario:** A regulated EU bank states two requirements for a Bedrock workload: (1) in-scope personal data must be stored and processed only within the EU, and (2) only EU-resident personnel may operate the underlying infrastructure. The team is choosing among standard EU Regions, inference-routing scopes, and AWS partitions.

**Ask:** Which TWO statements correctly address these requirements? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.3

### 3. Option Analysis
- **A** ✅ A standard EU Region with In-Region (or EU-geographic) inference satisfies the data storage-and-processing requirement
- **B** ✅ The AWS European Sovereign Cloud satisfies the EU-resident-personnel operator-access requirement
- **C** ❌ EU geographic cross-Region inference by itself satisfies the operator-access requirement
- **D** ❌ A Global cross-Region inference profile satisfies the data-residency requirement
- **E** ❌ AWS Outposts is required because Amazon Bedrock cannot run in any EU Region

### 4. Correct Answer Deep-Dive
**Answer: A, B**

Data residency (store and process in the EU) is met by a standard EU Region using In-Region or EU-geographic inference (A). The stricter sovereignty requirement of EU-resident operator access is met by the AWS European Sovereign Cloud, an independent EU-operated partition (B). C is wrong because geographic inference governs where data is processed (location), not who operates the infrastructure. D is wrong because Global inference routes anywhere and is never a residency answer. E is wrong because Bedrock runs in EU Regions, so Outposts is not required.

### 5. Key Takeaway
Data residency (store and process in the EU) is met by a standard EU Region using In-Region or EU-geographic inference (A).

---

## Question 32

### 1. Question Summary
**Scenario:** A marketing app lets users generate two-minute videos with Amazon Nova Reel. An engineer built an Amazon API Gateway REST endpoint backed by a Lambda that calls the model synchronously and returns the finished video in the response. The endpoint times out, and raising the Lambda timeout to 15 minutes does not help.

**Ask:** What is the underlying problem and the correct approach?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.4

### 3. Option Analysis
- **A** ❌ Lambda needs more memory; increase it and the synchronous call will complete
- **B** ✅ Nova Reel video generation is asynchronous-only via StartAsyncInvoke writing to S3, and a synchronous call would also exceed the API Gateway integration timeout regardless of the Lambda limit
- **C** ❌ The video must be returned as base64 in the response body to avoid the timeout
- **D** ❌ Switch to CreateModelInvocationJob batch inference to render the single video

### 4. Correct Answer Deep-Dive
**Answer: B**

Nova Reel video generation is asynchronous-only through StartAsyncInvoke, which returns an invocationArn and writes output to S3; a two-minute clip takes many minutes. Even setting that aside, the binding constraint behind a REST API is the API Gateway integration timeout (default 29 seconds), which fails long before Lambda's 15-minute limit, so raising the Lambda timeout cannot fix it. A and C do not address either the async-only requirement or the integration-timeout ceiling. D batch inference is for high-volume non-urgent JSONL workloads, not a single long video generation (StartAsyncInvoke is the path).

### 5. Key Takeaway
Nova Reel video generation is asynchronous-only through StartAsyncInvoke, which returns an invocationArn and writes output to S3; a two-minute clip takes many minutes.

---

## Question 33

### 1. Question Summary
**Scenario:** During a marketing push, many users simultaneously hit a Bedrock-backed feature and the application begins returning ThrottlingException errors. An engineer proposes raising the Lambda reserved concurrency so more requests can run at once.

**Ask:** What is the correct architectural fix for the throttling?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.4

### 3. Option Analysis
- **A** ❌ Raise Lambda reserved concurrency so the workers can absorb the burst
- **B** ✅ Buffer bursty requests with an Amazon SQS queue in front of a Lambda worker to smooth concurrency against Bedrock quotas, with exponential backoff and jitter on retries
- **C** ❌ Move the workload to a synchronous API Gateway endpoint with a longer integration timeout
- **D** ❌ Disable retries so failed requests do not add to the load

### 4. Correct Answer Deep-Dive
**Answer: B**

ThrottlingException is the model's account-level quota pushing back. Raising Lambda concurrency (A) just sends more concurrent calls to Bedrock and pushes the throttling downstream onto the model, making it worse. The architectural lever is to buffer with SQS in front of a Lambda worker so concurrency is smoothed against Bedrock quotas, combined with exponential backoff and jitter. C does not change the underlying quota pressure. D disabling retries discards transient-failure recovery and does not address the burst.

### 5. Key Takeaway
ThrottlingException is the model's account-level quota pushing back.

---

## Question 34

### 1. Question Summary
**Scenario:** An agent's foundation model is its single reasoning core. The team wants built-in redundancy so that if the primary Region's model endpoint has trouble or the workload bursts, requests are automatically served from another Region, without writing client-side load-balancing code. They enable a system-defined cross-Region inference profile and reference it as the modelId, but invocations now intermittently fail with AccessDenied.

**Ask:** What is the most likely cause of the intermittent AccessDenied?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.4

### 3. Option Analysis
- **A** ✅ An AWS Organizations SCP (or IAM policy) allows the Bedrock invoke actions only in the source Region and blocks one of the profile's destination Regions
- **B** ❌ Cross-Region inference profiles cannot be used as a modelId in the Converse API
- **C** ❌ The profile adds a per-request routing surcharge that the account budget rejects
- **D** ❌ Cross-Region inference requires Provisioned Throughput, which the team has not purchased

### 4. Correct Answer Deep-Dive
**Answer: A**

Because a cross-Region inference profile can route to any of its destination Regions, your SCPs and IAM policies must permit the model-invocation actions in every destination Region. If even one destination Region is blocked, requests that route there fail with AccessDenied while source-Region requests succeed, producing the intermittent pattern. B is false; an inference profile is referenced as the modelId. C is false; cross-Region inference adds no routing or data-transfer cost (priced by source Region). D is false; cross-Region inference does not require Provisioned Throughput.

### 5. Key Takeaway
Because a cross-Region inference profile can route to any of its destination Regions, your SCPs and IAM policies must permit the model-invocation actions in every destination Region.

---

## Question 35

### 1. Question Summary
**Scenario:** A team is building a token-streaming chatbot. The primary requirement is to authenticate users with an Amazon Cognito User Pool while writing the least possible custom authentication code; the chat is a standard server-to-client token stream.

**Ask:** Which front-end streaming pattern best fits?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.5

### 3. Option Analysis
- **A** ❌ A Lambda function URL with response streaming
- **B** ❌ An Amazon API Gateway WebSocket API
- **C** ✅ AWS AppSync GraphQL subscriptions
- **D** ❌ A synchronous REST API Gateway endpoint returning a buffered response

### 4. Correct Answer Deep-Dive
**Answer: C**

AppSync integrates natively with Cognito User Pools and manages the handshake and token refresh with no custom authorizer, making it the least-custom-code answer when managed Cognito auth is the differentiator. A Lambda function URL (A) has no built-in Cognito authorizer and requires IAM/SigV4 or manual JWT verification. A WebSocket API (B) also lacks a built-in Cognito authorizer and needs a Lambda authorizer for the JWT; choosing it 'because it is real-time' when the differentiator is managed auth is the trap. D is not streaming at all.

### 5. Key Takeaway
AppSync integrates natively with Cognito User Pools and manages the handshake and token refresh with no custom authorizer, making it the least-custom-code answer when managed Cognito auth is the differentiator.

---

