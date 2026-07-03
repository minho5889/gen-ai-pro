# AIP-C01 Practice Exam 2 — Analysis (Q31-Q35)

## Question 31

### 1. Question Summary
**Scenario:** A security team requires that all traffic from application instances to Amazon Bedrock stay on the AWS network with no path over the public internet, no internet gateway, no NAT, and no public IPs on the instances. An engineer suggests creating a gateway VPC endpoint for Bedrock, similar to how they connect privately to Amazon S3.

**Ask:** What is the correct way to provide private connectivity to Bedrock, and what is wrong with the proposal?

### 2. Domain Mapping
**Domain:** 2.3 Enterprise integration - private connectivity
**Task:** Task 2.3

### 3. Option Analysis
- **A** ❌ Create a gateway VPC endpoint for Bedrock, exactly as the engineer proposed
- **B** ✅ Use an AWS PrivateLink interface VPC endpoint (for example, the bedrock-runtime endpoint service); gateway endpoints exist only for S3 and DynamoDB, not Bedrock
- **C** ❌ Attach a resource-based endpoint policy to the Bedrock Knowledge Base to restrict network access
- **D** ❌ Route the traffic through a Site-to-Site VPN from a Local Zone subnet to Bedrock

### 4. Correct Answer Deep-Dive
**Answer: B**

Bedrock private connectivity uses AWS PrivateLink interface VPC endpoints (per-API endpoint services like com.amazonaws.{region}.bedrock-runtime), which keep traffic on the AWS network with no IGW/NAT/public IP. Gateway VPC endpoints exist only for Amazon S3 and DynamoDB, so the engineer's gateway-endpoint proposal (A) is wrong for Bedrock. Bedrock GenAI resources do not support resource-based policies (C) - an endpoint policy attaches to the endpoint, not the Knowledge Base, and is not the connectivity mechanism. Local Zones do not support VPC endpoints or Site-to-Site VPN (D), so that path is invalid.

### 5. Key Takeaway
Bedrock private connectivity uses AWS PrivateLink interface VPC endpoints (per-API endpoint services like com.amazonaws.{region}.bedrock-runtime), which keep traffic on the AWS network with no IGW/NAT/public IP.

---

## Question 32

### 1. Question Summary
**Scenario:** A marketing app lets users generate two-minute promotional videos with Amazon Nova Reel. The first build exposes an Amazon API Gateway REST endpoint backed by a Lambda that invokes the model synchronously and returns the finished video in the response. In testing, every request fails with a gateway timeout. An engineer proposes raising the Lambda timeout to 15 minutes.

**Ask:** What is the correct integration design, and why does raising the Lambda timeout not help?

### 2. Domain Mapping
**Domain:** 2.4 FM API integration
**Task:** Task 2.4

### 3. Option Analysis
- **A** ❌ Increase the Lambda timeout to 15 minutes; the failure is purely a Lambda duration problem
- **B** ✅ Nova Reel video generation is asynchronous-only via StartAsyncInvoke (output to S3); a synchronous request also exceeds the API Gateway integration timeout, which binds long before Lambda's limit
- **C** ❌ Switch to Provisioned Throughput so the synchronous call returns within 29 seconds
- **D** ❌ Return the video as base64 inline in the synchronous response to avoid the timeout

### 4. Correct Answer Deep-Dive
**Answer: B**

Nova Reel video generation is asynchronous-only through StartAsyncInvoke, writing output to S3, and a two-minute clip takes many minutes - far beyond any synchronous window. Independently, the API Gateway integration timeout (29s default for REST) binds long before Lambda's 15-minute limit, so raising the Lambda timeout (A) misidentifies the binding constraint. Provisioned Throughput (C) changes capacity/billing, not the fundamentally async generation or the API Gateway ceiling. Base64 inline (D) does not address the multi-minute generation time or the timeout.

### 5. Key Takeaway
Nova Reel video generation is asynchronous-only through StartAsyncInvoke, writing output to S3, and a two-minute clip takes many minutes - far beyond any synchronous window.

---

## Question 33

### 1. Question Summary
**Scenario:** A nightly pipeline must summarize 500,000 archived contracts (text) as cheaply as possible with no latency requirement. The team wants to minimize compute and avoid API rate limits or polling loops, and they need to be notified when each processing job reaches a terminal state. They also note that none of the summaries require tool calling or strict JSON-schema enforcement.

**Ask:** Which TWO choices best fit this workload? (Select TWO.)

### 2. Domain Mapping
**Domain:** 2.4 FM API integration
**Task:** Task 2.4

### 3. Option Analysis
- **A** ❌ Use CreateModelInvocationJob batch inference with JSONL input in S3 for the high-volume, non-urgent, cost-optimized work
- **B** ❌ Use StartAsyncInvoke for each individual document
- **C** ❌ React to Bedrock job state-change events with an Amazon EventBridge rule instead of polling
- **D** ❌ Poll GetModelInvocationJob in a Lambda loop every 30 seconds to detect completion
- **E** ❌ Front the pipeline with a synchronous API Gateway endpoint for each document
- **F** ❌ Use Provisioned Throughput so the batch completes faster than on-demand

### 4. Correct Answer Deep-Dive
**Answer: AC**

Batch inference (CreateModelInvocationJob) with JSONL-in-S3 is the high-volume, non-urgent, cost-optimized path (~50% discount), and it is compatible here because no tool calling or structured output is needed. An EventBridge rule on Bedrock job state-change events delivers completion notifications without a polling loop, minimizing compute and avoiding rate limits. StartAsyncInvoke (B) is for single long-running generations, not 500k records. Polling (D) is the antipattern the question rules out. A synchronous endpoint (E) is wrong for long batch work. Provisioned Throughput (F) does not apply to batch and is not the cost-minimizing choice.

### 5. Key Takeaway
Batch inference (CreateModelInvocationJob) with JSONL-in-S3 is the high-volume, non-urgent, cost-optimized path (~50% discount), and it is compatible here because no tool calling or structured output is needed.

---

## Question 34

### 1. Question Summary
**Scenario:** A customer-support app fronts Amazon Bedrock with API Gateway and Lambda. At peak, many users hit the same model simultaneously and the application begins returning ThrottlingException errors. An engineer raises the Lambda reserved concurrency to allow more simultaneous executions, but the throttling persists and even gets worse.

**Ask:** What is the correct architectural fix for the throttling?

### 2. Domain Mapping
**Domain:** 2.4 FM API integration - resilient throughput
**Task:** Task 2.4

### 3. Option Analysis
- **A** ❌ Raise Lambda reserved concurrency further until the throttling clears
- **B** ✅ Buffer bursty traffic with an Amazon SQS queue in front of a Lambda worker to smooth concurrency against Bedrock's account quotas, and apply exponential backoff with jitter on retries
- **C** ❌ Switch every request to the streaming API (ConverseStream) to avoid throttling
- **D** ❌ Move the workload to a synchronous Step Functions Express workflow

### 4. Correct Answer Deep-Dive
**Answer: B**

Raising Lambda concurrency just sends more concurrent requests to Bedrock and pushes the throttling downstream onto the model's account quota - which is why it persists or worsens. The architectural fix is to buffer bursty traffic with SQS in front of a Lambda worker, smoothing concurrency against Bedrock quotas, combined with exponential backoff with jitter on retries. Streaming (C) changes time-to-first-byte, not the request rate against quotas. A Step Functions Express workflow (D) does not buffer or rate-limit the calls to Bedrock and does not address the quota pressure.

### 5. Key Takeaway
Raising Lambda concurrency just sends more concurrent requests to Bedrock and pushes the throttling downstream onto the model's account quota - which is why it persists or worsens.

---

## Question 35

### 1. Question Summary
**Scenario:** A team is building a streaming chatbot front end. Requirements: users must authenticate with an Amazon Cognito User Pool, the team wants to write the least custom authentication/authorization code possible, and tokens must stream to the browser as the model generates them. They are deciding among Lambda function URL streaming, an API Gateway WebSocket API, and AWS AppSync GraphQL subscriptions.

**Ask:** Which front-end streaming pattern best fits the Cognito-with-least-custom-auth requirement?

### 2. Domain Mapping
**Domain:** 2.5 Application integration and dev tools
**Task:** Task 2.5

### 3. Option Analysis
- **A** ❌ Lambda function URL with response streaming
- **B** ❌ API Gateway WebSocket API
- **C** ✅ AWS AppSync GraphQL subscriptions
- **D** ❌ A synchronous API Gateway REST endpoint returning a buffered response

### 4. Correct Answer Deep-Dive
**Answer: C**

AppSync integrates natively with Cognito User Pools and handles the handshake and token refresh with no custom authorizer, so it is the least-custom-auth streaming option (startStream returns immediately, offloads to SQS, and a processing Lambda pushes each token via a publishToken mutation). Lambda function URLs (A) have no built-in Cognito authorizer - you must use IAM/SigV4 or manual JWT verification. WebSocket APIs (B) also lack a built-in Cognito authorizer and need a Lambda authorizer to validate the JWT. A buffered REST response (D) is not streaming at all. Picking WebSocket 'because it is real-time' when the differentiator is managed Cognito auth is the trap.

### 5. Key Takeaway
AppSync integrates natively with Cognito User Pools and handles the handshake and token refresh with no custom authorizer, so it is the least-custom-auth streaming option (startStream returns immediately, offloads to SQS, and a processing Lambda pushes each token via a publishToken mutation).

---

