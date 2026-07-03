# Enterprise Integration & Deployment — Deep-Dive Study Guide

## Document Metadata

| Field | Value |
|-------|-------|
| Target Exam | AWS Certified Generative AI Developer - Professional (AIP-C01) |
| Exam Domains Covered | Domain 2: Implementation and Integration (26%) |
| Primary Tasks | Task 2.3 (enterprise integration architectures) and the application-integration portion of Task 2.5 (Amplify UI, API Gateway streaming and token limits, Bedrock Data Automation, Amazon Q Developer), plus the enterprise and deployment framing of Tasks 2.2 and 2.4 that Guides 01 and 04 deferred here |
| Study Guide | Guide 05 of the AIP-C01 Study Strategy (file 08 by build order) |
| Priority Level | MODERATE — enterprise integration reuses SAP/DOP/DVA primitives, so this guide teaches only the GenAI-specific overlay |
| Prerequisite Knowledge | Guide 01 (Foundation Models & Bedrock Core — FM APIs, streaming mechanics, Cross-Region Inference, Provisioned Throughput, deployment modes), Guide 04 (Agentic AI — agent orchestration and AgentCore), Guide 03 (AI Safety, Security & Governance — Guardrails, PII, VPC-endpoint security depth) |
| Source Material | Official AIP-C01 Exam Guide, Amazon Bedrock User Guide, AWS Prescriptive Guidance, AWS Well-Architected (Generative AI Lens, Agentic AI Lens, Data Residency & Hybrid Cloud Lens), AWS Machine Learning and Compute blogs, MCP-researched and live-doc-verified AWS documentation |

Note on numbering: this is Guide 05 in the study strategy but file 08 by build order; earlier guides that cross-reference "Guide 05" mean this file.

---

## How to Use This Guide

This guide closes the open cross-references that Guide 04 left dangling. Guide 04 scoped itself to the agentic portion of Domain 2 (Task 2.1 and the orchestration slice of Task 2.5) and explicitly deferred "the broader deployment and enterprise-integration story" and "the non-agentic parts of 2.5" to this guide (Guide 05). Section 8 of Guide 04 named this guide as the owner of the deployment and enterprise-integration story while it owned only the agentic angle on model flexibility and resilience. Those references resolve here. This guide owns Task 2.3 (enterprise integration architectures) in full, owns the application-integration parts of Task 2.5 that Guide 04 listed as out of scope (API Gateway streaming and token limits, the Amplify UI, Bedrock Data Automation, and Amazon Q Developer), and carries the enterprise and deployment framing of Tasks 2.2 and 2.4 that Guide 01 introduced at the API and inference-mode level but did not extend to multi-team governance and CI/CD.

Because you already hold SAP-C02, DOP-C02, and DVA-C02, this guide deliberately does not re-teach generic API Gateway, Lambda, IAM, CodePipeline, or VPC primitives. It teaches the GenAI-specific overlay on top of constructs you already know: the GenAI gateway pattern and its cost-attribution traps, foundation-model data residency at the edge and in-Region, role-based access control scoped to Bedrock model, Knowledge Base, Agent, and Guardrail resources, and the CI/CD stages unique to promoting prompts, agents, and Knowledge Bases. Where a topic belongs to a neighboring guide, this guide cross-references rather than duplicates: Guide 01 owns the Bedrock FM APIs, streaming mechanics, Cross-Region Inference routing, and Provisioned Throughput depth; Guide 04 owns agent orchestration and AgentCore; Guide 03 owns Guardrails, PII, and VPC-endpoint security depth; and Guides 06 and 07 own evaluation, cost, and monitoring depth.

Each section is written in textbook-depth prose that teaches the reasoning behind each design choice, supplemented by comparison tables and described diagrams. Every section ends with an Exam-Relevant Distinctions checklist and a Knowledge Check quiz that includes at least one multiple-response (Select TWO or Select THREE) question to mirror the exam's question mix. Work the quizzes before revealing answers — active recall is what moves this material into long-term memory.

Several facts in this guide are point-in-time figures verified against live AWS documentation as of mid-2026 — STS limits, API key lifetimes, API Gateway timeouts, batch quotas, and the very recent built-in cost-attribution feature. These are flagged inline so you learn the durable concept and treat the exact number as something to re-verify near your exam date.

---

## Table of Contents

- Section 1: Enterprise GenAI Integration Foundations
- Section 2: The GenAI / LLM Gateway Pattern
- Section 3: Identity, RBAC & Least Privilege Over GenAI Resources
- Section 4: Data Residency & the Edge for FM Workloads
- Section 5: Application Integration & Front-End
- Section 6: CI/CD & Deployment for GenAI
- Section 7: Exam Patterns & Quick Reference
- AWS Documentation References

---

## Section 1: Enterprise GenAI Integration Foundations

### Two Axes That Decide Every Integration Question

When the exam puts a foundation-model workload inside an enterprise architecture, it is almost always asking you to choose a point on two axes. The first axis is the integration style — API-driven (a caller makes a request and waits for, or streams, a response) versus event-driven (a producer emits an event and a consumer reacts to it later, with the two sides decoupled in time). The second axis is the invocation mode — synchronous (the model call blocks until the answer is ready) versus asynchronous (the call starts a job and the result is delivered later, usually to Amazon S3). These two axes are related but not identical, and the most common Domain 2 mistake is conflating them. You can make a synchronous Bedrock call from inside an event-driven architecture (an EventBridge rule triggers a Lambda that calls `Converse` and waits), and you can build an API-driven front end over an asynchronous job (an API returns a job ID immediately and the client polls). The skill the exam tests is matching the workload's latency tolerance, payload size, and durability needs to the right combination.

Your SAP/DVA background already gives you the generic version of this decision. What changes for GenAI is the shape of the constraints. Foundation-model responses are slow relative to ordinary API responses — a multi-paragraph completion can take many seconds, and a long video generation takes minutes. Token streaming exists specifically because waiting for a full completion produces an unacceptable time-to-first-byte for chat. Bedrock enforces account-level throttling quotas that bursty traffic blows through, so the buffering pattern matters more than it does for a typical CRUD API. And some Bedrock operations are async-only because they exceed any reasonable synchronous request window. The integration choices below are the generic patterns re-fitted to those GenAI realities.

### Synchronous Invocation and Its Hard Ceiling

Synchronous invocation is the default mental model: call `InvokeModel` or `Converse`, block, and receive the completion. It is correct for real-time, interactive workloads — a chatbot turn, a single classification, a short summary — where the user is waiting and the response fits comfortably inside the request window. The critical exam fact is that the request window is bounded by the front door, not by the model. When you front a synchronous Bedrock call with Amazon API Gateway and Lambda, the binding constraint is the API Gateway integration timeout, which defaults to 29 seconds for REST APIs (configurable from 50 ms up to 29,000 ms). Lambda's own 15-minute ceiling is almost never what fails first. A scenario that says "the model takes 40 seconds and our API times out" is an API Gateway integration-timeout problem, and "raise the Lambda timeout" is the trap answer. (Section 5 develops the streaming and timeout-increase fixes; here, just hold that synchronous-behind-REST-API-Gateway has a hard ceiling well under a minute by default.)

For interactive workloads that are too slow to wait for in full but still need to feel real-time, the answer is not async — it is streaming. Streaming keeps the request synchronous in spirit (one connection, one logical response) but emits tokens incrementally so the user sees output immediately. Bedrock exposes `ConverseStream` and `InvokeModelWithResponseStream` for this. Streaming is the synchronous-world fix for latency perception; it is not a substitute for async when the total work genuinely exceeds the request window.

### Asynchronous Invocation: Two Distinct Paths

Asynchronous invocation is for work that cannot finish inside a synchronous window or that does not need to. Bedrock offers two distinct async paths, and the exam reliably swaps them to bait you.

The first is the asynchronous runtime API, `StartAsyncInvoke`. It starts a single long-running model invocation, takes the `modelId`, the `modelInput`, and an S3 `outputDataConfig`, and returns an `invocationArn`. The result lands in S3, not in the API response. You check completion with `GetAsyncInvoke`, which returns a status of `InProgress`, `Completed`, or `Failed`. The canonical use case is long-running generation — Amazon Nova Reel video generation is asynchronous-only via `StartAsyncInvoke`, taking on the order of ninety seconds for a six-second clip and roughly fourteen to seventeen minutes for a two-minute clip [FLAG — point-in-time latencies], with output written to a caller-specified bucket. This is the textbook "why async" case: a single generation that vastly exceeds any synchronous request window. Note that `StartAsyncInvoke` model support is limited (Nova Reel and select models), so it is not a universal async path for every foundation model.

The second async path is batch inference via the control-plane operation `CreateModelInvocationJob`. Input is a JSONL file in S3 (each line a `recordId` plus a `modelInput`), output is written to S3, the `invocationType` is either `InvokeModel` or `Converse`, and the job runs at roughly a fifty-percent discount versus on-demand pricing [FLAG — point-in-time discount]. Batch is for large-volume, non-latency-sensitive work — summarizing a quarter-million archived documents overnight. There is a documented limit of around ten concurrent batch jobs per model per Region [FLAG — point-in-time quota], which is exactly why production batch pipelines put a queue (Lambda plus DynamoDB) in front of job submission to throttle as slots free up. The exam discriminator is volume and urgency: a single long generation (one video) is `StartAsyncInvoke`; a high-volume, cost-optimized, non-urgent batch (a hundred thousand documents) is `CreateModelInvocationJob`. Choosing batch for one video, or async-invoke for a hundred thousand documents, is the trap.

**Diagram (described):** This decision flow starts from an "FM workload" node and asks the question "Is it interactive and does it fit the request window?" If yes (a chat turn or short task), the path goes to synchronous `Converse`, then asks a follow-up: "Is it slow to first byte?" — if yes, switch to `ConverseStream` streaming; if no, return a blocking response. Back at the top question, if the answer is no because it is a long single generation, the path goes to `StartAsyncInvoke` writing output to S3. If the answer is no because it is high-volume and non-urgent, the path goes to `CreateModelInvocationJob` batch inference.

### Event-Driven Glue: Polling Versus EventBridge

Once a job runs asynchronously, you need to know when it finishes. The naive approach is polling — a Lambda that loops calling `GetAsyncInvoke` or `GetModelInvocationJob`. The exam-preferred approach is event-driven: Amazon EventBridge receives Bedrock job state-change events for model-customization and batch-inference jobs in near real time, at no cost to receive, and you react with an SNS, SQS, or Lambda target. When a question stresses minimizing cost and compute and avoiding API rate limits or polling, the answer is an EventBridge rule on Bedrock job state-change events, not a polling loop. Choosing polling when EventBridge is on offer is a reliable trap.

Event-driven decoupling also solves the burst problem. Bursty foundation-model traffic that throttles (`ThrottlingException`) should be buffered with Amazon SQS in front of a Lambda worker, which smooths concurrency against Bedrock's quotas, or fanned out with SNS or EventBridge. Simply raising Lambda concurrency does not fix throttling — it just pushes the throttling downstream onto Bedrock. Guide 01 owns the exponential-backoff-with-jitter retry discipline; here, the architectural lever is the queue.

For multi-step orchestration that is not agentic — prompt chaining, a fan-out to several models, a human-approval gate, a long-running pipeline — AWS Step Functions has an optimized service integration with Bedrock (`InvokeModel` and `CreateModelCustomizationJob`), letting you orchestrate FM calls visually in Workflow Studio without hand-rolling Lambda glue. The anti-pattern is a single long-running Lambda that orchestrates several Bedrock calls in sequence; it fights the 15-minute limit, has weak retry semantics, and is hard to audit. Step Functions gives durable, retryable, traceable control flow. (Guide 04 owns the agentic ReAct loop; Step Functions here is the deterministic, non-agentic orchestrator.)

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Model takes 40s, our REST API times out" | API Gateway integration timeout - not Lambda | Default 29s integration timeout binds first |
| "Generate a 2-minute video" | StartAsyncInvoke with S3 output | Long single generation exceeds sync window |
| "Summarize 250k documents cheaply, no rush" | CreateModelInvocationJob batch | High-volume non-urgent, ~50% discount |
| "Know when a batch job finishes, minimize compute" | EventBridge job state-change rule | Event-driven beats polling Get APIs |
| "Bursty traffic causes ThrottlingException" | SQS buffer in front of a Lambda worker | Smooths concurrency against Bedrock quotas |
| "Chain several FM calls with a human gate" | Step Functions optimized Bedrock integration | Durable, retryable, auditable orchestration |
| "Chat feels slow to first token" | ConverseStream streaming | Streaming fixes time-to-first-byte, not total work |

- API-driven versus event-driven is the decoupling axis; synchronous versus asynchronous is the invocation axis — they are independent choices.
- `StartAsyncInvoke` is a single long-running invocation (results to S3); batch inference is high-volume JSONL-in-S3 at a discount — different APIs, different use cases.
- A single long-running Lambda orchestrating multiple Bedrock calls is the anti-pattern; Step Functions is the deterministic alternative.

### Knowledge Check

**Q1:** A media app lets users generate two-minute marketing videos with Amazon Nova Reel. An engineer builds an API Gateway REST endpoint backed by a Lambda that calls the model and returns the video. What is wrong?
- A) Nothing — Lambda can run for 15 minutes
- B) Nova Reel video generation is asynchronous-only via StartAsyncInvoke; a synchronous request will exceed the API Gateway integration timeout
- C) Nova Reel requires Provisioned Throughput
- D) The video must be returned as base64 in the response body

**A:** B — Nova Reel video generation is async-only through `StartAsyncInvoke`, with output written to S3, and a two-minute clip takes roughly 14-17 minutes. Even ignoring that, the API Gateway integration timeout (29s default) fails long before Lambda's 15-minute limit, so "Lambda can run 15 minutes" (A) misidentifies the binding constraint.

**Q2:** Select TWO. A nightly pipeline must summarize 500,000 archived PDFs as cheaply as possible with no latency requirement, and the team wants to be notified when each job completes without burning compute on polling. Which two choices fit?
- A) Use StartAsyncInvoke for each document
- B) Use CreateModelInvocationJob batch inference with JSONL input in S3
- C) Poll GetModelInvocationJob in a Lambda loop every 30 seconds
- D) React to Bedrock job state-change events via an EventBridge rule
- E) Front the pipeline with a synchronous API Gateway endpoint

**A:** B and D — Batch inference (`CreateModelInvocationJob`) is the high-volume, cost-optimized, non-urgent path (~50% discount), and an EventBridge rule on Bedrock job state-change events delivers completion notifications without a polling loop. `StartAsyncInvoke` (A) is for single long-running generations, polling (C) is the anti-pattern the question rules out, and synchronous API Gateway (E) is wrong for a long batch.

**Q3:** True or False — Raising Lambda reserved concurrency is the correct fix for ThrottlingException errors when many users hit a Bedrock model simultaneously.

**A:** False. Raising Lambda concurrency just sends more concurrent requests to Bedrock and pushes the throttling downstream onto the model's account quota. The architectural fix is to buffer with SQS in front of a Lambda worker (smoothing concurrency against Bedrock quotas) and apply exponential backoff with jitter on retries.

**Q4:** A workflow must call one model to draft text, wait for a human to approve it, then call a second model to finalize. An engineer proposes one Lambda that does all three steps. What is the better design and why?

**A:** Use AWS Step Functions with its optimized Bedrock integration and a wait-for-callback (task token) state for the human gate. A single Lambda fights the 15-minute limit, cannot cleanly pause for human approval, and has weak retry and audit semantics. Step Functions gives durable, retryable, traceable control flow for non-agentic multi-step FM orchestration.

> **Source attribution:** Synchronous-versus-asynchronous invocation, `StartAsyncInvoke`/`GetAsyncInvoke`, batch inference via `CreateModelInvocationJob`, EventBridge job state-change events, and the Step Functions optimized Bedrock integration are MCP-researched from the Amazon Bedrock User Guide (batch inference, monitoring with EventBridge), the boto3 bedrock-runtime reference, the Nova video-generation guide, and the AWS Step Functions launch announcement, mapped to Tasks 2.3 and 2.4. Streaming mechanics and retry/backoff depth are owned by Guide 01 and cross-referenced here. Point-in-time flags: Nova Reel latencies, the ~50% batch discount, and the ~10-concurrent-jobs-per-model-per-Region limit are current figures subject to change.

---

## Section 2: The GenAI / LLM Gateway Pattern

### Why a Gateway at All

The single most-tested architecture in Task 2.3 is the centralized GenAI gateway — a managed layer that every team's application calls instead of calling Amazon Bedrock directly. AWS publishes an official prescriptive pattern for it ("Build an internal SaaS service with cost and usage tracking for foundation models on Amazon Bedrock") and a named AWS Solutions Guidance ("Guidance for a Multi-Tenant, Generative AI Gateway with Cost and Usage Tracking on AWS"). The reference shape is Amazon API Gateway plus Lambda in front of Bedrock: each team (tenant) receives an API key, API Gateway routes to an invocation Lambda that logs per-team usage and then calls Bedrock, and the gateway loosely couples model consumers from the endpoint service so it can adapt to changing models, architectures, and invocation methods.

The trap the exam buries here is the justification. If every team simply called Bedrock directly with its own IAM role, you would already get per-principal cost attribution and IAM-policy model governance for free. So the reason to build a gateway is not "because you otherwise can't see costs." The real justifications are centralized credential management (API keys mapped to tenants and cost centers), a standardized OpenAPI interface, usage-plan throttling and quotas, per-tenant model allowlisting, and decoupling consumers from changing models. When a question asks why a gateway is warranted, "to get cost visibility" is the distractor; the governance, throttling, and decoupling reasons are correct.

**Diagram (described):** This left-to-right architecture shows two consumers, "Team A app" and "Team B app," both calling a single "API Gateway" layer that enforces usage plans. API Gateway forwards to an "Invocation Lambda" that logs usage. The Lambda calls Bedrock through a "PrivateLink endpoint," which connects to "Amazon Bedrock." The Lambda also writes "CloudWatch usage logs." Separately, an "EventBridge daily rule" triggers a "Cost-tracking Lambda"; that cost Lambda also reads from the CloudWatch usage logs, and writes "S3 cost per team." The key point is that per-request invocation and daily cost aggregation are separate flows.

### Throttling, Quotas, and Credentials at the Gateway

Per-team throttling and quotas are implemented with API Gateway usage plans plus API keys: a usage plan sets a target request rate (throttling) and quota limits (maximum requests per key per period), and the API key doubles as the centralized credential mechanism mapping each key to a tenant or cost center. This is the generic usage-plan mechanism you already know, with the GenAI overlay that keys correspond to tenants.

The deeper exam point comes from the Well-Architected Agentic AI Lens, which mandates multi-layer tenant-aware throttling, not gateway-only throttling. The anti-pattern is throttling solely at API Gateway while downstream shared resources — model inference, memory, tools — stay unprotected, letting a tenant bypass the API limits with long-running or concurrent operations. The recommended layers are API Gateway usage plans and per-tenant keys at ingress, tenant-aware request queuing that caps concurrent Bedrock inference calls per tenant, per-tenant rate limits on memory and tool endpoints, adaptive throttling (bursting above baseline at low load, strict at high load), per-tenant CloudWatch dashboards and alarms, and noisy-neighbor load testing. So "we set API Gateway usage plans per team, so tenants are fully isolated" is wrong if concurrent inference is unbounded — the correct answer adds per-tenant concurrency limits at the inference layer.

### Cost Attribution: The Central Gateway Trap

Here is the most important single fact in this section. When an LLM gateway authenticates users at its own layer and then calls Bedrock with one IAM role attached to the gateway's compute, every Bedrock call appears in billing as a single identity with no per-user or per-tenant visibility. If a scenario says "all teams' Bedrock spend shows up under one role, we can't tell who spent what," the cause is the shared role — and the fix is not "enable Cost Explorer" or "turn on CloudTrail." The fix is for the gateway to call `sts:AssumeRole` on a Bedrock-scoped role for each user, passing the user identity as the role-session-name and the team, tenant, or cost-center as session tags. This is AWS's recommended Scenario 4 for multi-tenant SaaS: tenant ID as the session name plus session tags.

Bedrock now also offers built-in granular cost attribution: it automatically attributes inference cost to the calling IAM principal (user, assumed role, or federated identity) and surfaces it in AWS Billing, Cost Explorer, and CUR 2.0 — exposed through the CUR 2.0 IAM-principal data export under the `iamPrincipal/` cost-allocation columns — once you enable IAM-principal data in the CUR 2.0 export and activate the relevant cost-allocation tags [FLAG — feature from an April 2026 blog, very recent relative to the exam's knowledge baseline; verify it is assumed knowledge]. But built-in attribution alone still only shows the gateway's role unless per-user session management is added — the two facts compose. Principal tags (static on the IAM user or role) and session tags (passed via STS or an IdP assertion) appear in CUR 2.0 under the `iamPrincipal/` prefix once activated.

The STS scaling facts matter for a high-throughput gateway: `AssumeRole` adds minimal latency, the returned credentials are valid up to one hour and should be cached and reused (one STS call per user per hour, not per request), cache size scales with concurrent users rather than total users, the default STS limit is around 500 `AssumeRole` calls per second per account (request an increase for a busy gateway) [FLAG — point-in-time limit], and session tags are immutable for the life of a session. That immutability is its own exam scenario: if a tenant's cost-center tag was changed but billing still shows the old value, the cause is that session tags are fixed for the cached session's life (up to an hour) and the change only takes effect on the next session.

### Tagging Models for Chargeback: Two Approaches

Separately from per-principal attribution, there are two ways to tag the model usage itself for chargeback, and the exam contrasts them. The first is application inference profiles — server-side, tag-bearing wrappers around a single on-demand model. Before these existed, AWS cost-allocation tagging worked on many Bedrock resources (provisioned and custom models, agents, Knowledge Bases, prompts, prompt flows, batch jobs) but not on on-demand foundation models, so the only way to tag on-demand invoke cost was an application inference profile. An application inference profile has type `APPLICATION` (versus the AWS-managed `SYSTEM_DEFINED` cross-Region routing profiles), is created from a single model ARN or by copying a system-defined profile to inherit cross-Region inference, and is then used as the `modelId` in `Converse` or `InvokeModel`; its tags (TenantID, business-unit, department) drive Budgets and Cost Explorer chargeback. Application inference profiles suit tens to thousands of tenants but proliferate (one profile per model per tenant dimension) and hit tag limits at very large scale.

The second is the `Converse` API `requestMetadata` parameter — client-side key-value tagging (tenantId, departmentId) passed with each request, which does not affect the model response and is captured in Bedrock invocation logs, then processed with Glue ETL into Athena or QuickSight for per-tenant dashboards. `requestMetadata` is the recommended approach at very large scale (hundreds of thousands to millions of tenants, or many required tag dimensions that exceed per-resource tag limits). Picking application inference profiles "for millions of tenants" is the wrong-answer trap; picking `requestMetadata` for a handful of business units is over-engineering.

A subtle but high-value distinction the exam exploits: application inference profiles, `requestMetadata`, and tags are cost-attribution mechanisms — they do not deny invocation. If a question asks how to stop Team B from calling a particular model, that is an access-control problem (an IAM identity policy or SCP scoping the model ARN, covered in Section 3), not a profile or tag.

### Bedrock API Keys

Bedrock offers a GenAI-specific credential mechanism — Bedrock API keys, passed as an `Authorization: Bearer` header or the `AWS_BEARER_TOKEN_BEDROCK` environment variable. There are two types, and the exam tests the choice. Short-term keys last up to twelve hours (or the session duration), inherit the permissions of the generating IAM principal, and are recommended for production. Long-term keys create an IAM user with attached policies and last until an expiration date, and are recommended only for exploration. Choosing long-term keys for a production multi-team gateway is the trap; production answers use short-term keys [FLAG — 12-hour maximum is point-in-time]. All API calls are logged in CloudTrail, but the keys themselves are not logged, and a Bedrock key maps to an IAM user in CUR 2.0.

Finally, a cost-architecture detail: cost calculation belongs out of the hot path. The AWS reference separates the per-request invocation flow (log `team_id`, `model_id`, input and output tokens to CloudWatch, then invoke Bedrock) from a daily EventBridge-scheduled cost-tracking Lambda that pulls the previous day's usage, computes on-demand cost, and writes aggregated cost per team to S3 for S3 Select, Athena, or QuickSight. Putting per-request cost calculation inline adds latency to every invocation; a scenario describing a latency regression after adding chargeback points to exactly this anti-pattern.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "All teams' spend shows under one role" | STS AssumeRole per user with session tags | Shared gateway role erases per-tenant identity |
| "Why build a gateway at all" | Keys, OpenAPI, throttling, allowlisting, decoupling | Not for cost visibility - direct IAM already gives that |
| "Tag on-demand model cost for tens of tenants" | Application inference profiles | Server-side tags on a single-model wrapper |
| "Per-tenant cost for millions of tenants" | Converse requestMetadata plus invocation logs | Profiles proliferate and hit tag limits at scale |
| "Stop Team B from calling Claude Opus" | IAM policy or SCP on the model ARN | Profiles and tags attribute cost, they do not deny |
| "Production multi-team gateway credentials" | Short-term Bedrock API keys | Long-term keys are exploration-only |
| "Latency regressed after adding chargeback" | Move cost calc to a daily EventBridge job | Per-request cost calc in the hot path adds latency |
| "Usage plans set, so tenants fully isolated" | Add per-tenant inference concurrency limits | Multi-layer throttling, not gateway-only |
| "Cost-center tag changed but billing unchanged" | Session tags are immutable for the session life | Change applies on next session, not retroactively |

- Built-in Bedrock cost attribution surfaces the IAM principal in CUR 2.0; it still shows only the gateway role unless the gateway assumes a per-user role.
- CUR 2.0 `line_item_usage_type` already encodes Region, model, and input-versus-output token direction — input/output spend per model is answerable without custom token logging.
- STS credentials are valid up to one hour and must be cached (one call per user per hour); cache size scales with concurrent, not total, users.

### Knowledge Check

**Q1:** A company's LLM gateway authenticates each user with Cognito, then calls Bedrock using a single IAM role attached to the gateway's Lambda. Finance complains they cannot attribute Bedrock spend to individual business units. What is the correct fix?
- A) Enable AWS Cost Explorer
- B) Turn on CloudTrail for Bedrock
- C) Have the gateway call sts:AssumeRole per user, passing tenant as the role-session-name and business unit as session tags
- D) Switch every team to its own AWS account

**A:** C — A single shared role erases per-user identity in billing. Per-user `AssumeRole` with the tenant as the session name and business unit as session tags restores attribution in CUR 2.0 (AWS's Scenario 4). Cost Explorer (A) and CloudTrail (B) show only the shared role's spend; account-per-tenant (D) is a heavier, separate isolation strategy, not the targeted fix.

**Q2:** Select TWO. Which statements about chargeback-tagging Bedrock usage are correct?
- A) Application inference profiles can tag on-demand model invocation cost for cost allocation
- B) On-demand foundation models could always be tagged directly for cost allocation
- C) Converse requestMetadata is recommended when there are hundreds of thousands to millions of tenants
- D) Application inference profiles deny invocation for untagged teams
- E) requestMetadata changes the model's response content

**A:** A and C — Application inference profiles are the mechanism that finally enabled tagging on-demand invoke cost (so B is false — direct tagging of on-demand FMs was not possible), and `requestMetadata` is the recommended large-scale approach. Profiles attribute cost but do not deny invocation (D false), and `requestMetadata` does not affect the response (E false).

**Q3:** True or False — For a production multi-team Bedrock gateway, long-term API keys are the recommended credential mechanism because they do not expire frequently.

**A:** False. Long-term Bedrock API keys create an IAM user and are recommended only for exploration. Production uses short-term keys (up to 12 hours, inheriting the generating principal's permissions). Choosing long-term keys for production is the trap.

**Q4:** A team sets API Gateway usage plans per tenant and concludes tenants are fully isolated. A premium tenant launches many long-running inference calls and degrades others. What was missed?

**A:** Multi-layer tenant-aware throttling. Throttling only at the API Gateway ingress leaves downstream shared inference unprotected; a tenant can bypass request-rate limits with concurrent or long-running operations. The fix adds tenant-aware request queuing that caps concurrent Bedrock inference per tenant, plus per-tenant rate limits on memory and tool endpoints and per-tenant dashboards (Well-Architected Agentic AI Lens AGENTPERF07-BP02).

> **Source attribution:** The gateway reference architecture, per-team usage logging, the daily EventBridge cost-tracking flow, and PrivateLink connectivity are from the AWS ML Blog "Build an internal SaaS service with cost and usage tracking for foundation models on Amazon Bedrock" and the AWS Solutions "Guidance for a Multi-Tenant, Generative AI Gateway." The single-role attribution trap and STS scaling facts are from "Introducing granular cost attribution for Amazon Bedrock"; application inference profiles versus `requestMetadata` from "Track, allocate, and manage your generative AI cost" and "Cost tracking multi-tenant model inference on Amazon Bedrock"; multi-layer throttling from Well-Architected Agentic AI Lens AGENTPERF07-BP02; Bedrock API keys from the Bedrock User Guide. Built-in granular cost attribution is from a very recent (April 2026) blog and the DynamoDB role in the named Guidance is unverified — both flagged. Point-in-time flags: STS 500 calls/sec/account, 12-hour short-term key max, 24-48h tag-activation delay.

---

## Section 3: Identity, RBAC & Least Privilege Over GenAI Resources

### What Is Different About Bedrock's Authorization Model

Your SAP/DVA experience makes generic IAM and Cognito second nature, so this section teaches only what is GenAI-specific and what trips up exactly the experienced candidate. The headline fact: Amazon Bedrock supports identity-based policies, ABAC via tags, temporary credentials, forward-access sessions, and service roles — but it does not support resource-based policies, ACLs, or service-linked roles. The implication is the one a SAP/DOP holder is most likely to get wrong: you cannot attach a resource policy to a specific Knowledge Base, Agent, or Guardrail to grant cross-account access the way you would an S3 bucket or a Lambda function. Access to Bedrock GenAI resources is controlled exclusively through identity-based policies (and SCPs) plus condition keys. Cross-account sharing is done with assumed roles, not resource policies. When a scenario assumes a Knowledge Base resource policy, that is the trap.

### Scoping Access to Specific Models, Knowledge Bases, Agents, and Guardrails

Least privilege over GenAI resources means scoping the `Resource` element to the right ARN for the right action, and each resource type has its own quirks.

To restrict which foundation model a principal may invoke, scope `bedrock:InvokeModel`, `bedrock:InvokeModelWithResponseStream`, and `bedrock:CreateModelInvocationJob` to a specific foundation-model ARN of the form `arn:aws:bedrock:REGION::foundation-model/MODEL-ID`. Note this ARN has no account number — the model is AWS-owned. A `Deny` on `InvokeModel` automatically blocks `Converse` and `StartAsyncInvoke`; to deny everything explicitly you use `bedrock:InvokeModel*` or add `bedrock:Converse` and `bedrock:ConverseStream`. The streaming gotcha matters: `bedrock:InvokeModelWithResponseStream` is a separate action from `bedrock:InvokeModel`, so a policy that denies only `InvokeModel` leaves the streaming path open. To fully deny inference you must cover both.

Knowledge Base access is scoped per-KB by setting the `Resource` to `arn:aws:bedrock:REGION:ACCOUNT:knowledge-base/KB-ID` on `bedrock:Retrieve` and `bedrock:GetKnowledgeBase`. The trap: `bedrock:RetrieveAndGenerate` does not support resource-level permissions — the AWS example policy uses `Resource "*"` for the RetrieveAndGenerate statement. So you cannot lock `RetrieveAndGenerate` to a single KB ARN the way you can with `Retrieve`. True per-KB isolation for the generate path has to come from a different control (a separate role or account, or restricting which KB the application passes).

Agent access is scoped by resource type and action, and the swap is a classic distractor. `bedrock:InvokeAgent` must be granted on the agent-alias ARN (`arn:aws:bedrock:REGION:ACCOUNT:agent-alias/AGENT-ID/ALIAS-ID`), not the agent ARN. Management actions such as `UpdateAgent` and `GetAgent` are granted on the agent ARN (`arn:aws:bedrock:REGION:ACCOUNT:agent/AGENT-ID`). Actions with no resource type (such as `CreateAgent`) require `Resource "*"`. Some actions need multiple resources at once — `AssociateAgentKnowledgeBase` requires permission on both the agent ARN and the Knowledge Base ARN in the same statement, or the call fails.

Guardrail invocation is controlled by `bedrock:ApplyGuardrail` scoped to the guardrail ARN. When applying a guardrail with a Bedrock foundation model you also need `bedrock:InvokeModel`; but when applying a guardrail independently against a third-party (non-Bedrock) model, you need only `bedrock:ApplyGuardrail` — no `InvokeModel`. A trap answer adds `InvokeModel` for the third-party case; the minimum is `ApplyGuardrail` alone. (Guide 03 owns Guardrails policy depth — content filters, denied topics, PII; this is only the IAM-scoping overlay.)

**Diagram (described):** This diagram branches from a single "IAM principal policy" node into four parallel grants, each annotated with a caveat. The first grant is `InvokeModel` on the foundation-model ARN, with a note that the FM ARN has no account number because the model is AWS-owned. The second is `Retrieve` on the Knowledge Base ARN, with a note that `RetrieveAndGenerate` stays at `Resource "*"` and has no resource-level scope. The third is `InvokeAgent` on the agent-alias ARN, with a note that the agent ARN is used for management actions only, not invocation. The fourth is `ApplyGuardrail` on the guardrail ARN.

### Condition Keys and the Inference-Profile Least-Privilege Trap

Bedrock provides GenAI-specific IAM condition keys that the exam likes. `bedrock:GuardrailIdentifier` forces a specific guardrail ARN (or ARN and version) on every `InvokeModel` or `Converse` call — the way to mandate per-tenant safety enforcement, which an ARN-only policy cannot do. `bedrock:InferenceProfileArn` forces invocation only through a designated inference profile (useful to route all traffic through a tagged, cost-allocated profile). `bedrock:ServiceTier` restricts which tiers (the documented values are `reserved`, `priority`, `default`, and `flex` [FLAG — evolving tier set]) a principal may use — the lever for stopping a team from using the premium tier, done with a `Deny` on the condition key, not with separate models or quotas. ABAC is supported through `aws:ResourceTag`, `aws:RequestTag`, and `aws:TagKeys`.

The most common least-privilege trap in this whole area is the inference-profile migration. When a team switches from a bare model ID to a cross-Region or geographic inference profile, they often grant `InvokeModel` on the profile ARN and start getting `AccessDenied`. The fix: you must grant `InvokeModel` on both the inference-profile ARN and the underlying foundation-model ARN in every source and destination Region in the profile's geography — not just the calling Region. Granting only the profile ARN, or only one Region's FM ARN, fails. And if you use an inference profile, omitting `GetInferenceProfile` from the policy breaks invocation (the parallel facts are `GetCustomModel` for custom models, `GetImportedModel` for imported, `GetProvisionedModelThroughput` for provisioned). The convenience policy `AmazonBedrockFullAccess` grants broad access; the documented least-privilege baseline grants the invoke actions plus the right `Get`/`List` actions for the chosen resource type.

### Federation and Per-Tenant Access for GenAI Front-Ends

For a customer-facing GenAI app, the identity-federation pattern is an Amazon Cognito identity pool that exchanges a federated or user-pool token for temporary AWS credentials mapped to an authenticated IAM role. Role mappings can assign different IAM roles per identity provider or per token claim, which is how different tenants get different Bedrock scopes — one role can `InvokeModel` only Model A plus KB-1, another only Model B plus KB-2. Unauthenticated (guest) identities map to a separate, minimal role. The exam trap: leaving the unauthenticated role with Bedrock invoke permissions exposes the app to anonymous model usage and cost — the correct design denies Bedrock on the guest role.

For strong, regulated multi-tenant isolation, the exam-correct answer is often account-per-tenant (AWS Organizations plus SCPs) rather than role mapping plus ABAC, precisely because Bedrock has no resource-based policies and `RetrieveAndGenerate` cannot be ARN-scoped — the lightweight in-account controls cannot fully isolate the generate path. Cognito role mapping plus ABAC (session tags matched against `aws:ResourceTag`) is the lightweight pattern for softer isolation; account-per-tenant is the strong-isolation pattern.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Attach a resource policy to a KB or Agent for cross-account" | Trap - Bedrock has no resource-based policies | Use assumed roles plus identity policies and SCPs |
| "Lock down InvokeAgent to a specific agent" | Scope to the agent-ALIAS ARN | Agent ARN is for management actions only |
| "Restrict invocation to one Knowledge Base" | Scope Retrieve to the KB ARN | RetrieveAndGenerate cannot be ARN-scoped |
| "Per-KB isolation for the generate path" | Separate role or account, not a KB ARN | RetrieveAndGenerate uses Resource * |
| "Filter a third-party model with a guardrail, min perms" | bedrock:ApplyGuardrail only | InvokeModel needed only with a Bedrock FM |
| "AccessDenied after moving to an inference profile" | Allow the FM ARN in all profile Regions too | Profile ARN alone is insufficient |
| "Force every call through a specific guardrail" | bedrock:GuardrailIdentifier condition key | ARN scoping cannot pin a guardrail to a call |
| "Stop a team from using the premium tier" | Deny with bedrock:ServiceTier condition key | Tier control, not separate models or quotas |
| "Strong regulated per-tenant isolation" | Account-per-tenant with Organizations and SCPs | No resource policies; RetrieveAndGenerate not scopable |

- The foundation-model ARN has no account number because the model is AWS-owned; the KB, Agent, and Guardrail ARNs do include the account.
- To fully deny inference, deny both `bedrock:InvokeModel` and `bedrock:InvokeModelWithResponseStream` (this also covers Converse and async invoke).
- Cognito guest (unauthenticated) roles should deny Bedrock to prevent anonymous model usage and cost.

### Knowledge Check

**Q1:** A platform team wants to share a single Knowledge Base with a partner account by attaching a resource-based policy to the Knowledge Base, the way they share an S3 bucket. Will this work?
- A) Yes, Knowledge Bases support resource-based policies
- B) No — Bedrock does not support resource-based policies; cross-account access uses assumed roles plus identity-based policies and SCPs
- C) Yes, but only for Retrieve, not RetrieveAndGenerate
- D) Only if the Knowledge Base is in OpenSearch Serverless

**A:** B — Bedrock supports identity-based policies, ABAC, temporary credentials, and service roles, but not resource-based policies, ACLs, or service-linked roles. Cross-account sharing of a Knowledge Base must use an assumed role in the owning account. This is the SAP/DOP-holder trap — expecting bucket-style resource policies on a GenAI resource.

**Q2:** Select THREE. A least-privilege policy must let an application invoke a model through a geographic cross-Region inference profile and apply a guardrail. Which statements are correct?
- A) Grant InvokeModel on the inference-profile ARN only
- B) Grant InvokeModel on the FM ARN in every source and destination Region of the profile
- C) Include GetInferenceProfile or invocation will fail
- D) bedrock:InvokeModelWithResponseStream is the same action as bedrock:InvokeModel
- E) Use bedrock:GuardrailIdentifier to force the specific guardrail on each call

**A:** B, C, and E — Inference-profile invocation requires `InvokeModel` on both the profile ARN and the underlying FM ARN in all Regions of the geography (so A is insufficient), `GetInferenceProfile` is required or invocation breaks, and `bedrock:GuardrailIdentifier` is the condition key that pins a guardrail to a call. Streaming is a separate action from `InvokeModel` (D false).

**Q3:** A policy grants bedrock:InvokeAgent on arn:aws:bedrock:us-east-1:123456789012:agent/ABC123. The application calls the agent through an alias and gets AccessDenied. Why?

**A:** `InvokeAgent` must be granted on the agent-alias ARN (`agent-alias/AGENT-ID/ALIAS-ID`), not the agent ARN. The agent ARN is used for management actions like `UpdateAgent` and `GetAgent`. Granting `InvokeAgent` on the agent ARN is the classic "which policy actually works" trap.

**Q4:** True or False — Application inference profiles and cost-allocation tags can be used to prevent Team B from invoking a specific model.

**A:** False. Application inference profiles, `requestMetadata`, and tags are cost-attribution mechanisms; they do not deny invocation. To block Team B from a model, use an IAM identity-based policy or SCP scoping the model ARN (optionally a `Deny` with the `bedrock:InferenceProfileArn` condition). Confusing cost attribution with access control is a recurring trap.

> **Source attribution:** The unsupported-resource-policy fact, per-resource ARN scoping for models, Knowledge Bases, Agents, and Guardrails, multi-resource actions, condition keys (`bedrock:GuardrailIdentifier`, `bedrock:InferenceProfileArn`, `bedrock:ServiceTier`), and the inference-profile least-privilege requirement are MCP-researched from the Amazon Bedrock User Guide IAM pages and the Service Authorization Reference for Amazon Bedrock. Cognito identity-pool role mapping is from the CloudFormation `IdentityPoolRoleAttachment` reference. Guardrails policy depth and VPC-endpoint security depth are owned by Guide 03 and cross-referenced. Point-in-time flags: the service-tier value set and the full condition-key list evolve; `RetrieveAndGenerate` resource-level support could change.

---

## Section 4: Data Residency & the Edge for FM Workloads

### The One Fact That Anchors Every Edge Question

Amazon Bedrock is a serverless, Regional service. There is no documented way to deploy the Bedrock inference data plane onto AWS Outposts, Local Zones, or Wavelength Zones — those edge environments run only EC2-based compute and storage (EC2, EBS, self-managed EKS/ECS nodes, ALB in select zones). They do not host Bedrock. So "run Bedrock at the 5G edge for ultra-low latency" is a distractor. The GenAI-specific takeaway is that edge zones host your application or inference-orchestration tier, while the model call still goes to Bedrock in-Region. If a scenario wants ultra-low latency to mobile users, you place the app tier in a Wavelength or Local Zone — not Bedrock itself.

The three edge constructs differ in purpose. AWS Wavelength deploys standard compute and storage at the edge of telecom carriers' 5G networks for ultra-low latency to mobile devices, reached by extending a VPC through a carrier gateway; a Wavelength Zone is a logical extension of a parent Region whose control plane stays in the Region. Wavelength is a latency control, not a residency control. AWS Local Zones extend select AWS services near population and industry centers for low latency and local data processing, with their own internet ingress and Direct Connect support; their control plane also runs in the parent Region. AWS Outposts extends AWS infrastructure on-premises (a rack or 1U/2U servers) for truly local data residency, connected to the parent Region by an encrypted service link that carries the control plane. The pattern is consistent: all three keep their control plane in the parent Region, so none is "fully air-gapped, no Region dependency."

### PrivateLink: Private Connectivity to Bedrock

Bedrock supports AWS PrivateLink interface VPC endpoints, so traffic reaches Bedrock without an internet gateway, NAT, VPN, or Direct Connect, and instances need no public IP. There are endpoint services per API category — `com.amazonaws.{region}.bedrock` (control plane), `bedrock-runtime` (inference), `bedrock-agent`, `bedrock-agent-runtime`, plus FIPS variants. You attach an endpoint policy (a resource-based policy on the endpoint itself, distinct from Bedrock's lack of resource policies on GenAI resources) to scope which principals, actions, and resources pass through. Two exam facts: Bedrock private connectivity is an interface endpoint (gateway endpoints exist only for S3 and DynamoDB — do not confuse them), and Local Zones do not support VPC endpoints or Site-to-Site VPN, so a Bedrock PrivateLink endpoint cannot live in a Local Zone subnet; an app in a Local Zone reaches Bedrock through the parent Region. FIPS endpoint services (`bedrock-fips`, `bedrock-runtime-fips`) are available only in a subset of Regions (us-east-1, us-east-2, us-west-2, ca-central-1, and the GovCloud Regions) [FLAG — point-in-time Region list] and are the answer when FIPS 140-3 validated crypto is required; otherwise standard TLS 1.2-or-higher applies.

### Why Your Data Stays on the AWS Network

The GenAI-specific residency anchor is the Bedrock Model Deployment Account model. In each Region where Bedrock is available, there is one deployment account per model provider, owned and operated by the Bedrock service team; AWS deep-copies the provider's inference software into these accounts, and the model providers themselves have no access. Therefore model providers cannot see your prompts, completions, or logs. When a question worries about "the model vendor seeing our data," this is the fact to reach for — not self-hosting on Outposts. Bedrock further operates a Zero Operator Access model (no service operator can read model input or output) and a default Zero Data Retention posture (by default Bedrock does not store inputs or outputs). Custom (fine-tuned) models are encrypted at rest with an AWS-owned key by default or a customer-managed KMS key, and the training data is not stored by Bedrock after the job completes.

There is an important exception with a residency trap. Abuse detection may retain inputs and outputs for up to thirty days for certain models. If cross-Region inference is enabled for a model that requires retention, the retained data is stored in the destination Region where the request was processed — not the source Region. So enabling cross-Region inference for throughput can quietly move retained data outside the source Region, a subtle residency violation. Bedrock also exposes explicit data-retention modes (`default`, `provider_data_share`, `none`, `inherit`) at account or project scope; setting `none` guarantees zero retention, and if you then call a model that requires retention, Bedrock blocks the request with an error. Note that setting a Responses-API `store=false` does not by itself guarantee zero retention — only `data_retention_mode=none` does.

### Routing Scope and Residency: In-Region, Geographic, Global

Bedrock has three inference-routing scopes, distinguished by the inference-profile or model-ID prefix, and the residency mapping is heavily tested. In-Region inference is strict single-Region. Geographic (Geo) inference (prefixes like `us.`, `eu.`, `apac.`) routes within a geography for higher throughput while keeping data in that geography — the recommended option for most residency and compliance needs, though prompts and outputs may move between Regions within the geography during processing. Global inference (prefix `global.`) routes to any commercial Region worldwide for maximum throughput and the lowest cost (roughly ten percent cheaper than Geographic for some models [FLAG — per-model, point-in-time]), and is always the wrong choice for any residency requirement. All cross-Region options are billed at source-Region rates with no surcharge, and CloudWatch and CloudTrail logging stays in the source Region. The mapping to memorize: "data must never leave a single Region or country" means In-Region inference (or a single in-country Region), not Geo; Geo keeps data in the geography but moves it between Regions inside it; Global is never the residency answer. Guide 01 owns the deeper Cross-Region Inference mechanics, the source-and-destination-Region routing, and the SCP/IAM rule; here the focus is the residency consequence.

A linked SCP trap from Guide 01's domain, restated for residency: geographic cross-Region inference fails if AWS Organizations SCPs allow only the source Region. You must allow all destination Regions of the profile, or `InvokeModel` returns `AccessDenied` despite source-Region access being granted.

### Residency Versus Sovereignty, and the European Sovereign Cloud

The exam distinguishes data residency (keeping data in a Region or country for legal compliance) from data sovereignty (full control and ownership, including operator-access restrictions, resiliency, and technological autonomy). The Well-Architected Data Residency lens frames four scenarios of increasing strictness, A through D, where D — in-scope data stored and processed in-country — is the strictest. A standard in-country Region satisfies residency. Sovereignty's stricter operator-access asks are satisfied by the AWS European Sovereign Cloud — a new, independent cloud partition in Germany, physically and logically separate from existing AWS infrastructure, operated exclusively by EU residents, with separate accounts, billing, and identity and no critical dependency on non-EU infrastructure. So when the requirement is EU-personnel-only operator access or true autonomy during a Region outage, the answer is the European Sovereign Cloud, not a normal EU Region and not EU geographic inference. For US public-sector workloads, Bedrock is available in AWS GovCloud (US-West and US-East) with FedRAMP and IL4/5 authorization for specific models; enabling those models requires accepting the model EULA through a linked standard account first.

**Diagram (described):** This decision flow fans out from a "Residency requirement" node along three questions. The first question, "Must data stay in one country?", has three answers: if yes and strictest, use In-Region inference; if it only needs to stay within a geography, use Geographic inference; if there is no constraint, use Global inference (the cheapest). The second question, "Is operator-access control needed?", branches two ways: if EU personnel only, choose the European Sovereign Cloud; if US public sector, choose AWS GovCloud. The third question, "Must data stay on premises?", leads, if yes, to running the Outposts app tier while the model call still goes to Bedrock in-Region.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Run Bedrock at the 5G edge for low latency" | Distractor - place the app tier in Wavelength | Bedrock is Regional; the model call stays in-Region |
| "Private connectivity to Bedrock, no internet" | PrivateLink interface VPC endpoint | Gateway endpoints are only S3 and DynamoDB |
| "Private Bedrock access from a Local Zone app" | Routes back to the parent Region | Local Zones support no VPC endpoints or VPN |
| "Data must never leave the country" | In-Region inference or single in-country Region | Geo keeps data in the geography, not one Region |
| "Maximum throughput, lowest cost, no residency need" | Global cross-Region inference | Global routes anywhere - never a residency answer |
| "Cross-Region on for a retention-required model" | Retained data lands in the destination Region | A hidden residency violation |
| "EU-personnel-only operator access" | AWS European Sovereign Cloud | Standard EU Region satisfies residency, not sovereignty |
| "Worried the model vendor sees our data" | Model Deployment Accounts and Zero Operator Access | Providers have no access; no self-hosting needed |
| "Guarantee nothing is persisted" | data_retention_mode=none | store=false alone does not guarantee ZDR |

- Outposts, Local Zones, and Wavelength all keep their control plane in the parent Region (Outposts via the encrypted service link) — none is fully air-gapped.
- FIPS Bedrock endpoint services exist only in a subset of Regions; choose them only when FIPS 140-3 crypto is required.
- Custom-model training data is not stored by Bedrock after the job completes; custom models are encrypted with an AWS-owned or customer-managed KMS key.

### Knowledge Check

**Q1:** A gaming company needs ultra-low latency to 5G mobile users for a GenAI feature and wants to "run the model at the edge in a Wavelength Zone." What is the correct architecture?
- A) Deploy Bedrock into the Wavelength Zone
- B) Place the application/inference-orchestration tier in the Wavelength Zone; the Bedrock call still goes to the parent Region
- C) Use Local Zones because they support VPC endpoints to Bedrock
- D) Self-host the model on Outposts in the carrier facility

**A:** B — Bedrock is a Regional, serverless service and does not run on Wavelength, Local Zones, or Outposts. The edge zone hosts the app tier for low latency to mobile devices; the model invocation still reaches Bedrock in-Region. Local Zones (C) do not even support VPC endpoints, so a Bedrock PrivateLink endpoint cannot live there.

**Q2:** Select TWO. A regulated EU customer says in-scope personal data must be stored and processed only within the EU, and only EU-resident personnel may operate the infrastructure. Which two facts apply?
- A) A standard EU Region with In-Region inference satisfies the storage-and-processing requirement
- B) EU geographic cross-Region inference fully satisfies the operator-access requirement
- C) The AWS European Sovereign Cloud satisfies the EU-personnel-only operator-access requirement
- D) Global cross-Region inference satisfies the residency requirement
- E) Outposts is required because Bedrock cannot run in the EU

**A:** A and C — A standard EU Region with In-Region (or EU-geographic) inference meets data residency, but operator-access control (sovereignty) is met by the European Sovereign Cloud, an independent EU-operated partition. Geographic inference (B) addresses location, not operator access; Global inference (D) is never a residency answer; Bedrock runs in EU Regions, so Outposts (E) is not required.

**Q3:** True or False — Enabling geographic cross-Region inference for higher throughput has no effect on where abuse-detection-retained data is stored.

**A:** False. For models that require abuse-detection retention, enabling cross-Region inference causes the retained inputs and outputs to be stored in the destination Region where the request was processed, not the source Region — a subtle residency consequence of turning on cross-Region routing.

**Q4:** A security team worries that the third-party model provider could read the company's prompts and completions. What fact addresses this, and what is the wrong over-reaction?

**A:** Bedrock uses per-provider Model Deployment Accounts that the Bedrock service team owns and operates, into which the provider's software is deep-copied; the providers have no access to those accounts, so they cannot see prompts, completions, or logs (reinforced by Zero Operator Access). The wrong over-reaction is self-hosting the model on Outposts to keep the provider out — unnecessary, because the provider already has no access.

> **Source attribution:** The Bedrock-is-Regional fact, Wavelength/Local Zones/Outposts roles, PrivateLink interface endpoints and FIPS Region list, the Model Deployment Account / Zero Operator Access / Zero Data Retention model, abuse-detection retention and its cross-Region trap, the data-retention modes, the In-Region/Geographic/Global routing scopes, residency-versus-sovereignty, the European Sovereign Cloud, and GovCloud Bedrock are MCP-researched from the Amazon Bedrock User Guide (VPC interface endpoints, data protection, abuse detection, data retention, cross-Region inference, models-Region compatibility), the Wavelength and Local Zones developer guides, AWS Prescriptive Guidance hybrid networking, the Well-Architected Data Residency lens, the European Sovereign Cloud whitepaper, and the GovCloud user guide. Deep Cross-Region Inference mechanics are owned by Guide 01. Point-in-time flags: specific model names in retention docs, the ~10% Global savings, and the FIPS Region list are snapshots to re-verify.

---

## Section 5: Application Integration & Front-End

### Streaming Foundation-Model Output to Clients

The defining front-end challenge for a GenAI app is latency perception. A foundation model can take many seconds to produce a full completion, and a chat UI that shows nothing until the whole answer is ready feels broken. Streaming fixes this by emitting tokens as they arrive, so the user sees output immediately. Bedrock exposes `ConverseStream` and `InvokeModelWithResponseStream` for streaming, and the front-end question is how to carry that stream to the browser. AWS documents three serverless patterns, and the exam picks among them primarily by the authentication requirement, not by "which is the most real-time."

The first pattern is a Lambda function URL with response streaming. It is the lowest-overhead option, native to Node.js (using `awslambda.streamifyResponse()`), and best for single-user or prototype streaming. But function URLs have no built-in Cognito User Pool authorizer — auth must be done with IAM (SigV4) or manual JWT verification inside the function. The second is an API Gateway WebSocket API, which gives a persistent bidirectional connection (`$connect`, `$disconnect`, and a custom route; the server pushes tokens via the Management API using the `connectionId`), best for multi-turn chat. WebSocket also has no built-in Cognito User Pool authorizer — you use a Lambda authorizer validating the Cognito JWT or IAM via an identity pool. The third is AppSync GraphQL subscriptions, the most auth-friendly option because AppSync integrates natively with Cognito User Pools and handles the handshake and token refresh with no custom authorizer; the pattern is a `startStream` mutation that returns a session ID immediately, offloads work to SQS, and a processing Lambda that pushes each token via a `publishToken` mutation fanned out to subscribers.

The auth-driven selection is the key exam reflex: when the scenario emphasizes Cognito User Pool authentication with the least custom code, the answer is AppSync subscriptions, because both the Lambda function URL and the WebSocket API require custom auth. Picking WebSocket "because it is real-time" when the differentiator is managed auth is the trap. WebSocket is justified specifically when you need persistent bidirectional multi-turn conversation; for a single server-to-client token push, server-sent events (SSE) over a streaming HTTP integration or Lambda URL is simpler.

**Diagram (described):** This decision flow starts at "Stream FM output to client" and asks "Cognito User Pool with the least code?" If yes, choose AppSync subscriptions. If no and it is a single push or prototype, choose Lambda URL streaming. If no and it needs bidirectional multi-turn, choose API Gateway WebSocket. A side note on the AppSync branch explains that its `startStream` mutation returns fast and offloads to SQS, after which a processing Lambda streams the tokens.

### API Gateway Timeouts and Streaming Limits

The hard ceiling introduced in Section 1 returns here with its fix. API Gateway REST APIs have a default 29-second integration timeout (configurable 50 ms to 29,000 ms). You can raise it above 29 seconds only through a Service Quotas or Support increase, which may require reducing your account throttle quota, and the increase is supported only for Regional and private REST APIs — not edge-optimized ones. The modern fix is HTTP proxy integration with response streaming (`responseTransferMode=STREAM`): with streaming enabled, the integration timeout can be configured up to fifteen minutes, and tokens flow to the client as they arrive, cutting time-to-first-byte [FLAG — point-in-time timeouts]. A caveat worth knowing: with HTTP_PROXY streaming, API Gateway does not send the HTTP status code or response headers until it has received all headers from the upstream integration.

Lambda response streaming itself supports payloads up to 200 MB (versus 6 MB buffered), with the first 6 MB uncapped and the remainder capped around 2 MB/s, and you are billed for the full function duration even if the client disconnects. The AppSync constraint is a 30-second resolver limit, which is exactly why the `startStream` mutation must return immediately and offload to SQS rather than blocking on the full generation; running the entire Bedrock generation inside the `startStream` resolver is wrong. The IAM granularity reminder from Section 3 applies to all three patterns: streaming uses `bedrock:InvokeModelWithResponseStream`, a separate action from `bedrock:InvokeModel`, so a "secure" policy that governs only `InvokeModel` leaves streaming open.

### AWS Amplify AI Kit

For teams that want a GenAI front end without hand-building IAM, AppSync, and conversation history, the AWS Amplify AI Kit (Amplify Gen 2, TypeScript, code-first) lets you declare GenAI routes in `amplify/data/resource.ts`. A `conversation` route gives a persistent multi-turn chat with managed conversation history in DynamoDB, a system prompt, tool use, and a ready-made React UI component; a `generation` route gives a single-shot typed response. It is backed by Amazon Bedrock and wires Cognito auth automatically. The exam distinction: `conversation` is the route for a chatbot that needs history and a UI; `generation` is the route for a one-shot typed result. Picking `generation` for a chatbot that needs history (or hand-building a DynamoDB history table when the `conversation` route already manages it) is the trap. The AI Kit also abstracts the Converse tool-use contract — instead of hand-writing `toolSpec` JSON, you declare tools in the data schema and Amplify manages registration and execution, re-sending conversation history, system prompt, and tool config on every call since the model is stateless. (Guide 01 owns the raw Converse tool-use contract; Amplify is the managed front-end abstraction over it.)

### Bedrock Data Automation

Amazon Bedrock Data Automation (BDA) extracts, transforms, and generates insights from unstructured multimodal content — documents, images, audio, and video — through one unified API, removing the need to orchestrate several models or do heavy prompt engineering. It produces standard output (default per-modality insights such as video summaries, transcripts, and document chart explanations) and custom output defined with natural-language Blueprints that specify extraction fields and formats. It offers confidence scores and visual grounding (bounding boxes) for trustworthiness, plus per-modality PII detection and redaction, logo detection, PrivateLink, and customer-managed KMS keys. The workflow is `CreateDataAutomationProject`, then invoke, then retrieve results.

Two BDA exam traps stand out. First, the sync-versus-async modality split: `InvokeDataAutomationAsync` is asynchronous and handles all modalities (audio, video, image, document), takes an S3 input plus a project ARN, returns an `invocationArn`, and supports EventBridge completion notifications; `InvokeDataAutomation` (synchronous) supports only images. A pipeline that processes video, audio, or PDFs must use the async API — using the synchronous API for a video pipeline is wrong. Second, BDA versus a do-it-yourself pipeline: when a scenario lists "orchestrate Textract plus Transcribe plus Rekognition plus a summarization model with custom glue," the GenAI-era correct answer is BDA's single unified multimodal API, not stitching individual AI services. BDA also integrates as a parser for Bedrock Knowledge Bases — in a data source's parsing configuration you can choose `parsingStrategy = BEDROCK_DATA_AUTOMATION` (versus `BEDROCK_FOUNDATION_MODEL`) for multimodal or structured extraction, with the default text parser as a fallback if the chosen parser fails.

### Amazon Q Developer

Amazon Q Developer is AWS's generative-AI software-development assistant, built on Amazon Bedrock, working across IDEs (VS Code, JetBrains, Visual Studio, Eclipse), the CLI, and the Console, with agentic coding (read and write files, run commands), automated code reviews, security scanning, documentation generation, and application transformation (Java upgrades, .NET porting). The enterprise-relevant feature is customization: admins can build a customization from the organization's private git repos or S3 buckets so suggestions reflect internal libraries and APIs (inline IDE completion is GA; chat customization was in preview [FLAG — status may have changed]). The data-privacy guarantees are the exam point: private code is not used to train the foundation model, inference endpoints are isolated per organization, and customization access is controlled per developer. So when an enterprise worries that a customization will leak proprietary code into the model, the correct reassurance is the not-used-for-training plus per-org-isolation guarantee — not "turn off Q" or "self-host a model." IP indemnification is a Pro-tier benefit (Pro is around $19 per user per month with higher limits; the Free tier has limited monthly interactions) [FLAG — point-in-time pricing].

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Stream chat with Cognito User Pool, least custom code" | AppSync GraphQL subscriptions | Native Cognito auth; others need custom auth |
| "Persistent bidirectional multi-turn chat" | API Gateway WebSocket API | Bidirectional; needs a Lambda authorizer for JWT |
| "Lowest-overhead single-user token streaming" | Lambda function URL with streaming | Node.js native; IAM or manual JWT auth |
| "Long FM generation behind REST API times out" | Response streaming up to 15 min, or async | The 29s integration timeout binds, not Lambda |
| "Edge-optimized REST API needs over 29s" | Not supported - use Regional or private | The over-29s increase excludes edge-optimized |
| "Chatbot needing managed history and a UI" | Amplify AI Kit conversation route | generation route is single-shot only |
| "Process video, audio, or PDFs with one API" | InvokeDataAutomationAsync | Synchronous BDA supports images only |
| "Orchestrate Textract plus Transcribe plus glue" | Bedrock Data Automation unified API | One multimodal API beats stitching services |
| "Customization will leak our private code" | Not used for training; per-org isolated endpoints | The reassurance, not disabling Q |

- Streaming uses `bedrock:InvokeModelWithResponseStream`, a separate IAM action from `InvokeModel` — a policy governing only `InvokeModel` leaves streaming open.
- AppSync has a 30-second resolver limit; the `startStream` mutation must return immediately and offload to SQS.
- BDA can serve as a Knowledge Base parser (`BEDROCK_DATA_AUTOMATION`) for multimodal documents, with the default text parser as fallback.

### Knowledge Check

**Q1:** A team builds a streaming chatbot and wants to authenticate users with a Cognito User Pool while writing the least custom auth code. Which front-end streaming pattern fits best?
- A) Lambda function URL with response streaming
- B) API Gateway WebSocket API
- C) AppSync GraphQL subscriptions
- D) Synchronous REST API Gateway with a buffered response

**A:** C — AppSync integrates natively with Cognito User Pools and handles the handshake and token refresh with no custom authorizer. Lambda function URLs (A) require IAM/SigV4 or manual JWT verification, and WebSocket (B) needs a Lambda authorizer for the JWT. A buffered REST response (D) is not streaming at all.

**Q2:** Select TWO. An ingestion pipeline must extract structured data from scanned PDFs, call recordings (audio), and product videos. Which two statements are correct?
- A) Use InvokeDataAutomationAsync because it handles documents, audio, and video
- B) Use InvokeDataAutomation (synchronous) for the videos
- C) Bedrock Data Automation can replace a hand-built Textract plus Transcribe plus Rekognition pipeline
- D) BDA cannot redact PII
- E) Each modality requires a different AWS AI service called separately

**A:** A and C — `InvokeDataAutomationAsync` handles all modalities, while the synchronous `InvokeDataAutomation` supports only images (so B is wrong for video), and BDA's unified multimodal API replaces a stitched-together pipeline. BDA supports per-modality PII redaction (D false), and the whole point is one API rather than per-service calls (E false).

**Q3:** A long FM generation behind a Regional REST API Gateway integration times out at 29 seconds. An engineer raises the Lambda timeout to 5 minutes and the problem persists. What actually fixes it?

**A:** The binding constraint is the API Gateway integration timeout, not Lambda's limit. Fixes: enable HTTP proxy response streaming (integration timeout up to 15 minutes) so tokens flow as they arrive, switch to a Lambda function URL or WebSocket streaming pattern, or move the work to an asynchronous pattern. Note the over-29s timeout increase is supported only for Regional and private REST APIs, not edge-optimized.

**Q4:** True or False — The Amplify AI Kit generation route is the right choice for a multi-turn chatbot because it can store conversation history.

**A:** False. The `generation` route gives a single-shot typed response and does not manage conversation history. The `conversation` route is the one that provides persistent multi-turn chat with managed history in DynamoDB and a ready-made UI component. Choosing `generation` for a stateful chatbot is the trap.

> **Source attribution:** The three streaming patterns and their auth tradeoffs are from the AWS Compute Blog "Serverless strategies for streaming LLM responses"; API Gateway timeouts and response streaming from the API Gateway REST timeout help panel and the response-streaming-HTTP developer guide; `InvokeModelWithResponseStream` IAM and `responseStreamingSupported` from the Bedrock API reference; the Amplify AI Kit conversation and generation routes from the AWS Mobile Blog AI Kit posts; Bedrock Data Automation from the BDA GA announcement, the BDA API guide, and the CloudFormation data-source parsing reference; Amazon Q Developer from the Q Developer product pages and the customization blog. Raw Converse tool-use is owned by Guide 01. Point-in-time flags: API Gateway timeouts, BDA modality coverage, Q Developer pricing and chat-customization GA status, and Lambda streaming runtime support are snapshots to re-verify.

---

## Section 6: CI/CD & Deployment for GenAI

### Promoting Agents: Aliases and Immutable Versions

Your DOP background gives you CodePipeline, CodeBuild, and CodeDeploy. What changes for GenAI is what you are promoting — prompts, agents, and Knowledge Base configurations behave differently from application code, and the deployment primitives are Bedrock-specific. Start with agents. A Bedrock Agent has a working DRAFT version and a test alias (`TSTALIASID`) created automatically. To deploy, you create an alias, which auto-creates an immutable numbered version (a snapshot). Applications call `InvokeAgent` against the alias, never against DRAFT or the test alias. Rollback is simply repointing the alias to a previous version — no redeploy. Versions are immutable, so changing production means cutting a new version and repointing the alias. A useful operational kill-switch: you can pause a deployed agent without any IAM change by setting the alias `aliasInvocationState` to `REJECT_INVOCATIONS` (and resume with `ACCEPT_INVOCATIONS`), which is distinct from deleting the alias or version.

The most-missed agent CI/CD fact is `PrepareAgent`. Changing an agent's instructions, action groups, or Knowledge Base association does not take effect until `PrepareAgent` rebuilds and packages the DRAFT (status flows `PREPARING` to `PREPARED`, or `FAILED`), after which you cut a new version and repoint the alias. In an IaC or CI/CD pipeline, any answer that updates agent config but omits the re-Prepare plus version plus alias-repoint is the trap.

**Diagram (described):** This left-to-right deployment flow shows the agent promotion lifecycle: edit the DRAFT config, then call `PrepareAgent`, then create an immutable version, then repoint the alias to that version, after which the application calls `InvokeAgent` on the alias. A rollback branch loops from the alias back to a previous version, illustrating that rollback is just repointing the alias.

### Promoting Prompts as Versioned Assets

Bedrock Prompt Management versions are created with `CreatePromptVersion`, which takes an immutable snapshot of the DRAFT prompt; version IDs are assigned incrementally from 1, and prompts integrate directly with the `Converse` and `InvokeModel` APIs. This lets you promote a versioned prompt independently of application code. The deeper CI/CD discipline comes from AWS Prescriptive Guidance: treat prompts as versioned, source-controlled assets (for example `/prompts/v1/agent-support-en.yaml`), run golden prompt-response regression tests, and deploy agent configurations (tools, instructions, KB URIs) through IaC with CodePipeline, CodeBuild, and CDK or CloudFormation.

The exam point is that GenAI CI/CD adds stages that generic application pipelines do not have. The pipeline should add prompt linting and format validation, golden prompt-response regression tests (promptfoo or pytest) that catch silent prompt degradation, a model cost-impact review at the approval gate, post-deploy smoke tests of agent outputs (CloudWatch Synthetics), and token-usage and cost monitoring via CloudWatch Bedrock token logs and X-Ray. The agent deployment is gated on prompt regression tests passing, tool permissions matching the IAM templates, and validation or confidence thresholds being met. The trap is treating a prompt change like ordinary code with only unit tests, ignoring the non-determinism and silent quality regression that prompts are prone to. Golden-dataset regression testing is the GenAI-specific gate. (Guide 06 owns evaluation depth and Guide 07 owns cost and monitoring; here the focus is the pipeline stage placement.)

**Diagram (described):** This left-to-right pipeline shows the GenAI-specific CI/CD stages in order: prompt and agent config in git, then prompt lint and format validation, then golden regression tests, then an approval gate that includes a cost-impact review, then deploy via IaC, then a post-deploy smoke test, ending with token and cost monitoring. The point is that the lint, golden-regression, cost-impact-gate, smoke-test, and token-monitoring stages are additions a generic application pipeline lacks.

### Knowledge Bases and AgentCore in the Pipeline

Knowledge Base CI/CD centers on the data-source configuration as code: the parsing strategy (Section 5's `BEDROCK_DATA_AUTOMATION` versus `BEDROCK_FOUNDATION_MODEL`), chunking configuration, embedding model, and vector-store wiring are deployed through IaC, and re-ingestion is triggered as a pipeline step when source data or configuration changes. (Guide 02 owns Knowledge Base internals; here it is one more versioned, IaC-deployed GenAI asset.)

For agentic deployments, AgentCore integrates into CI/CD as a managed runtime: agents register with AgentCore Runtime (which handles scaling, routing, and lifecycle, replacing custom service discovery), memory snapshots are promoted alongside code artifacts across dev, staging, and prod, Gateway tool configs are declared in-pipeline, and built-in observability hooks validate reasoning quality and compliance before promotion [FLAG — AgentCore CI/CD is from Prescriptive Guidance and is fast-moving; treat as emerging, not guaranteed exam content]. Guide 04 owns AgentCore depth; this is only its place in the deployment story it explicitly deferred here.

### Exam-Relevant Distinctions

| If the exam says... | The answer is... | Why |
|---|---|---|
| "Production app calls the agent" | Call the ALIAS, never DRAFT or TSTALIASID | Aliases are the indirection layer over versions |
| "Roll back an agent change fast" | Repoint the alias to a prior version | Versions are immutable; no redeploy needed |
| "Changed instructions but no effect" | Call PrepareAgent then cut a new version | Config changes need a re-Prepare to take effect |
| "Pause a live agent without IAM changes" | Set alias state to REJECT_INVOCATIONS | Operational kill-switch, distinct from delete |
| "Catch silent prompt quality regression" | Golden prompt-response regression tests | Unit tests miss non-deterministic degradation |
| "Promote a prompt apart from app code" | CreatePromptVersion immutable snapshot | Prompts version independently of code |
| "What CI/CD stage is GenAI-specific" | Prompt lint, golden tests, cost-impact gate | Generic pipelines lack these stages |

- A new agent version is an immutable snapshot; the alias is the only mutable pointer applications should ever call.
- `PrepareAgent` status flows `PREPARING` to `PREPARED` (or `FAILED`); skip it and config edits silently never deploy.
- Treat prompts, agent configs, and Knowledge Base data-source settings as versioned, source-controlled, IaC-deployed assets.

### Knowledge Check

**Q1:** An engineer updates a Bedrock Agent's action group through the console, then deploys, but the agent's behavior does not change. What step was almost certainly skipped?
- A) Restarting the Lambda function
- B) Calling PrepareAgent to rebuild the DRAFT, then creating a new version and repointing the alias
- C) Increasing the agent's memory size
- D) Re-creating the test alias

**A:** B — Changes to an agent's instructions, action groups, or KB associations do not take effect until `PrepareAgent` rebuilds and packages the DRAFT, after which a new immutable version is cut and the production alias is repointed. Omitting Prepare-plus-version-plus-alias-repoint is the classic agent CI/CD trap.

**Q2:** Select TWO. Which stages are GenAI-specific additions to a CI/CD pipeline that a generic application pipeline would not include?
- A) Golden prompt-response regression tests
- B) Compiling the application
- C) A model cost-impact review at the approval gate
- D) Running container image scans
- E) Provisioning the VPC

**A:** A and C — Golden prompt-response regression tests catch silent, non-deterministic prompt degradation, and a model cost-impact review at the approval gate is unique to FM workloads. Compiling (B), image scanning (D), and VPC provisioning (E) are generic pipeline activities not specific to GenAI.

**Q3:** A production incident requires immediately stopping a deployed agent from serving any requests, but the team wants to preserve the version and alias for forensic review and fast resumption. What is the cleanest action?

**A:** Set the alias `aliasInvocationState` to `REJECT_INVOCATIONS` via `UpdateAgentAlias` (resume later with `ACCEPT_INVOCATIONS`). This pauses invocations without deleting the alias or version and without any IAM change — an operational kill-switch distinct from tearing down the deployment.

**Q4:** True or False — To change a production agent, you should edit the live version in place so the alias automatically picks up the change.

**A:** False. Agent versions are immutable. You change production by editing DRAFT, running `PrepareAgent`, creating a new immutable version, and repointing the alias to it. There is no editing a live version in place; the alias is the indirection that lets you switch and roll back.

> **Source attribution:** Agent versions and aliases, `PrepareAgent`, and the `REJECT_INVOCATIONS` kill-switch are MCP-researched from the Amazon Bedrock User Guide (deploy an agent) and the `PrepareAgent` API reference; `CreatePromptVersion` from the Prompt Management version documentation; the GenAI CI/CD pipeline stages (prompts as versioned assets, golden regression tests, cost-impact gate, smoke tests, AgentCore in-pipeline) from AWS Prescriptive Guidance "CI/CD and automation" for agentic serverless. Evaluation depth is owned by Guide 06, cost and monitoring by Guide 07, Knowledge Base internals by Guide 02, and AgentCore depth by Guide 04. Point-in-time flag: AgentCore CI/CD and the CDK Bedrock alpha constructs are evolving.

---

## Section 7: Exam Patterns & Quick Reference

Every preceding section taught one layer of the enterprise-integration stack: the integration and invocation choices that frame every Domain 2 question (Section 1), the GenAI gateway with its throttling and cost-attribution traps (Section 2), least-privilege RBAC over Bedrock resources (Section 3), data residency and the edge (Section 4), front-end streaming and developer tooling (Section 5), and CI/CD for prompts, agents, and Knowledge Bases (Section 6). This final section introduces no new facts. It is the consolidated quick-reference chapter — the pages you re-read the night before the exam — arranging the scattered decisions and traps the way the exam actually probes them.

This guide is the home of two exam patterns from the strategy guide. Pattern 5's non-agentic facet — "switch models without code changes / survive an outage" — shows up here as the residency-aware routing choice (Section 4) and the gateway decoupling layer (Section 2), complementing Guide 04's agentic treatment. And a broad "design the enterprise integration" pattern threads through every section: choose the integration style, the gateway justification, the RBAC scoping, the residency control, the streaming front end, and the deployment primitive. Most questions in this domain are one of these wearing a costume.

### The Integration Decision Tree

The fastest way to get an enterprise-integration question right is to answer the decisions in order, resisting the urge to jump to a service name. First, characterize the workload's latency and durability. An interactive task that fits the request window is synchronous; if it is only slow to first byte, add streaming. A single long-running generation is `StartAsyncInvoke` to S3. A high-volume, non-urgent batch is `CreateModelInvocationJob`. Bursty traffic that throttles is buffered with SQS. Multi-step non-agentic orchestration is Step Functions.

**Diagram (described):** This decision tree branches from "Characterize the workload" into four workload shapes, each mapping to a service choice. An interactive task that fits the window maps to synchronous `Converse` (add streaming if slow). A single long generation maps to `StartAsyncInvoke` writing to S3. A high-volume, non-urgent workload maps to `CreateModelInvocationJob` batch. Bursty, throttling traffic maps to an SQS buffer in front of a Lambda worker.

Second, if multiple teams share Bedrock, decide on the gateway and how to attribute cost. A gateway is justified by centralized keys, throttling, allowlisting, and decoupling — not cost visibility. Per-tenant attribution through a shared-role gateway requires per-user `AssumeRole` with session tags. Chargeback tagging is application inference profiles for tens-to-thousands of tenants and `Converse` `requestMetadata` for hundreds-of-thousands-plus.

**Diagram (described):** This tree starts at "Multi-team Bedrock access" and branches three ways. The "Why a gateway?" branch resolves to keys, throttling, and decoupling (not cost visibility). The "Attribute cost per tenant?" branch resolves to `AssumeRole` with session tags. The "Chargeback tagging?" branch splits into two: application inference profiles for tens-to-thousands of tenants, and `requestMetadata` at very large scale.

Third, decide the residency control. Data must never leave a country means In-Region inference; within a geography means Geographic; no constraint and maximize throughput means Global. Operator-access control means the European Sovereign Cloud or GovCloud. On-premises means the app tier on Outposts with Bedrock still in-Region.

### Scenario-to-Answer Quick Map

The decision trees teach the reasoning; the table compresses it into pattern-matching reflexes. Read the left column as the cue and produce the middle column before looking at the options — the wrong answers are usually adjacent constructs.

| If the exam scenario says... | Answer pattern | Section |
|---|---|---|
| Interactive chat slow to first token | ConverseStream streaming | §1, §5 |
| Two-minute video generation | StartAsyncInvoke with S3 output | §1 |
| Summarize 250k documents cheaply, no rush | CreateModelInvocationJob batch | §1 |
| Know when a job finishes, minimize compute | EventBridge job state-change rule | §1 |
| Bursty traffic causes ThrottlingException | SQS buffer in front of a Lambda worker | §1 |
| Multi-step FM workflow with a human gate | Step Functions optimized Bedrock integration | §1 |
| All team spend shows under one role | STS AssumeRole per user with session tags | §2 |
| Why build a GenAI gateway | Keys, throttling, allowlisting, decoupling | §2 |
| Tag on-demand cost for thousands of tenants | Application inference profiles | §2 |
| Per-tenant cost for millions of tenants | Converse requestMetadata plus logs | §2 |
| Production multi-team gateway credentials | Short-term Bedrock API keys | §2 |
| Attach a resource policy to a KB or Agent | Trap - Bedrock has no resource policies | §3 |
| Lock down InvokeAgent to one agent | Scope to the agent-ALIAS ARN | §3 |
| AccessDenied after moving to a profile | Allow the FM ARN in all profile Regions | §3 |
| Stop a team from the premium tier | Deny with bedrock:ServiceTier | §3 |
| Strong regulated per-tenant isolation | Account-per-tenant with SCPs | §3 |
| Run Bedrock at the 5G edge | Distractor - app tier in Wavelength only | §4 |
| Private connectivity to Bedrock | PrivateLink interface VPC endpoint | §4 |
| Data must never leave the country | In-Region inference | §4 |
| EU-personnel-only operator access | AWS European Sovereign Cloud | §4 |
| Stream with Cognito, least custom code | AppSync GraphQL subscriptions | §5 |
| Persistent bidirectional multi-turn chat | API Gateway WebSocket | §5 |
| Long FM call times out behind REST API | Response streaming or async, not Lambda timeout | §5 |
| Process video, audio, and PDFs in one API | InvokeDataAutomationAsync | §5 |
| Orchestrate Textract plus Transcribe plus glue | Bedrock Data Automation | §5 |
| Chatbot needing managed history and UI | Amplify AI Kit conversation route | §5 |
| Q Developer customization leaks our code | Not used for training, per-org isolation | §5 |
| Production app calls the agent | Call the ALIAS, never DRAFT | §6 |
| Changed agent config but no effect | PrepareAgent then version then alias | §6 |
| Pause a live agent without IAM changes | Alias state REJECT_INVOCATIONS | §6 |
| Catch silent prompt regression | Golden prompt-response regression tests | §6 |

### Common Exam Traps and Distractors

Distractors in this domain are built from a handful of confusions. Name the confusion and you can usually eliminate two options on sight.

**The Lambda-timeout misdirection.** A long FM call behind a REST API Gateway integration fails at 29 seconds and the trap answer is "raise the Lambda timeout." The binding constraint is the API Gateway integration timeout, not Lambda's 15-minute limit. The fixes are response streaming (up to 15 minutes), a Lambda function URL or WebSocket streaming pattern, or an async pattern — and the over-29s increase is supported only for Regional and private REST APIs, not edge-optimized.

**Sync versus the two async paths.** `StartAsyncInvoke` (single long generation, S3 output) and `CreateModelInvocationJob` (high-volume JSONL batch, ~50% discount, ~10 concurrent jobs per model per Region) are different APIs. Batch for one video, or async-invoke for a hundred thousand documents, is the swap trap. Synchronous behind API Gateway for any long generation is also wrong.

**The shared-role cost-attribution trap.** A gateway calling Bedrock with one role erases per-tenant identity in billing. The fix is per-user `AssumeRole` with session tags — not Cost Explorer, not CloudTrail, and not built-in cost attribution alone (which still shows only the gateway role until per-user sessions are added). And cost-attribution mechanisms (profiles, `requestMetadata`, tags) never deny invocation; access control is IAM or SCP on the model ARN.

**Resource-based-policy assumption on GenAI resources.** Bedrock has no resource-based policies, ACLs, or service-linked roles. You cannot attach a policy to a Knowledge Base, Agent, or Guardrail for cross-account sharing — use assumed roles plus identity policies and SCPs. The companion fact: `RetrieveAndGenerate` cannot be ARN-scoped (only `Retrieve` can), which is part of why strong isolation often means account-per-tenant.

**The agent ARN versus alias ARN swap.** `InvokeAgent` is granted on the agent-alias ARN; management actions on the agent ARN. Production apps call the alias, never DRAFT or the test alias, and config changes require `PrepareAgent` plus a new version plus an alias repoint or they silently do nothing.

**Edge equals residency.** Wavelength, Local Zones, and Outposts are about latency and on-prem processing, not running Bedrock — Bedrock is Regional and serverless. "Data must never leave the country" is In-Region inference; Geographic keeps data in the geography but moves it between Regions; Global is never a residency answer. Sovereignty (operator access) is the European Sovereign Cloud, not a normal EU Region.

**Streaming-front-end selection by the wrong axis.** Picking WebSocket "because it is real-time" when the differentiator is managed Cognito auth is wrong; AppSync subscriptions are the auth-friendly answer. WebSocket is for bidirectional multi-turn. And streaming uses `bedrock:InvokeModelWithResponseStream`, a separate action — denying only `InvokeModel` leaves it open.

### Service-Selection Quick Reference

| Construct | What it is | Reach for it when |
|---|---|---|
| GenAI gateway - API Gateway plus Lambda | Centralized governed Bedrock access layer | Multi-team keys, throttling, allowlisting, decoupling |
| STS AssumeRole per user | Per-tenant identity for billing and scoping | A shared-role gateway hides who spent what |
| Application inference profile | Tag-bearing single-model wrapper | Chargeback for tens to thousands of tenants |
| Converse requestMetadata | Client-side per-request tagging in logs | Chargeback at hundreds of thousands plus tenants |
| PrivateLink interface endpoint | Private path to Bedrock, no internet | Traffic must stay off the public internet |
| Geographic inference profile | Routing inside one geography | Residency within a geography with more throughput |
| European Sovereign Cloud | Independent EU-operated partition | EU operator-access and sovereignty requirements |
| AppSync subscriptions | Cognito-native streaming front end | Stream to authenticated users with least code |
| Bedrock Data Automation | Unified multimodal extraction API | Replace a Textract plus Transcribe plus glue pipeline |
| Agent alias plus version | Immutable snapshot plus mutable pointer | Deploying and rolling back agents |

### Final Domain Mapping

This guide is the enterprise-integration and deployment home of Domain 2 (Implementation and Integration — 26% of the exam). It covers Task 2.3 in full and the application-integration slice of Task 2.5 (API Gateway streaming and token limits, Amplify UI, Bedrock Data Automation, Amazon Q Developer), and carries the enterprise and deployment framing of Tasks 2.2 and 2.4 that Guide 01 introduced at the API and inference-mode level. The agentic portions of Domain 2 (Task 2.1 and the orchestration slice of 2.5) belong to Guide 04, the Bedrock FM API, streaming-mechanics, Cross-Region Inference, and Provisioned Throughput depth belongs to Guide 01, Guardrails and security depth to Guide 03, and evaluation, cost, and monitoring to Guides 06 and 07. With this guide written, every "future Guide 05" cross-reference left open by Guide 04 is now closed.

---

## AWS Documentation References

Every URL below was retrieved and verified through MCP research or against live AWS documentation while the corresponding section was written. References are grouped by section topic and deduplicated — a source cited in more than one section appears once, under the topic it most directly supports.

### Enterprise GenAI Integration Foundations (Section 1)

- [StartAsyncInvoke (boto3 bedrock-runtime reference)](https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/start_async_invoke.html)
- [GetAsyncInvoke (boto3 bedrock-runtime reference)](https://docs.aws.amazon.com/boto3/latest/reference/services/bedrock-runtime/client/get_async_invoke.html)
- [Amazon Nova video generation access](https://docs.aws.amazon.com/nova/latest/userguide/video-gen-access.html)
- [Format and upload your batch inference data](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-data.html)
- [Monitor a batch inference job](https://docs.aws.amazon.com/bedrock/latest/userguide/batch-inference-monitor.html)
- [Monitor Amazon Bedrock job events with EventBridge](https://docs.aws.amazon.com/bedrock/latest/userguide/monitoring-eventbridge.html)
- [Automate Amazon Bedrock batch inference - scalable pipeline](https://aws.amazon.com/blogs/machine-learning/automate-amazon-bedrock-batch-inference-building-a-scalable-and-efficient-pipeline/)
- [AWS Step Functions optimized integration for Amazon Bedrock](https://aws.amazon.com/about-aws/whats-new/2023/11/aws-step-functions-optimized-integration-bedrock/)

### The GenAI / LLM Gateway Pattern (Section 2)

- [Build an internal SaaS service with cost and usage tracking for FMs on Bedrock](https://aws.amazon.com/blogs/machine-learning/build-an-internal-saas-service-with-cost-and-usage-tracking-for-foundation-models-on-amazon-bedrock/)
- [Guidance for a Multi-Tenant, Generative AI Gateway with Cost and Usage Tracking](https://aws.amazon.com/solutions/guidance/multi-tenant-generative-ai-gateway-with-cost-and-usage-tracking-on-aws/)
- [Introducing granular cost attribution for Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/introducing-granular-cost-attribution-for-amazon-bedrock/)
- [Track, allocate, and manage your generative AI cost and usage with Bedrock](https://aws.amazon.com/blogs/machine-learning/track-allocate-and-manage-your-generative-ai-cost-and-usage-with-amazon-bedrock/)
- [Cost tracking multi-tenant model inference on Amazon Bedrock](https://aws.amazon.com/blogs/machine-learning/cost-tracking-multi-tenant-model-inference-on-amazon-bedrock/)
- [Manage multi-tenant Bedrock costs using application inference profiles](https://aws.amazon.com/blogs/machine-learning/manage-multi-tenant-amazon-bedrock-costs-using-application-inference-profiles/)
- [Well-Architected Agentic AI Lens AGENTPERF07-BP02 (tenant-aware throttling)](https://docs.aws.amazon.com/wellarchitected/latest/agentic-ai-lens/agentperf07-bp02.html)
- [Amazon Bedrock API keys](https://docs.aws.amazon.com/bedrock/latest/userguide/api-keys.html)

### Identity, RBAC & Least Privilege (Section 3)

- [How Amazon Bedrock works with IAM](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_service-with-iam.html)
- [Identity-based policy examples for Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples.html)
- [Knowledge base prerequisite permissions](https://docs.aws.amazon.com/bedrock/latest/userguide/knowledge-base-prereq-permissions-general.html)
- [Identity-based policy examples for Bedrock agents](https://docs.aws.amazon.com/bedrock/latest/userguide/security_iam_id-based-policy-examples-agent.html)
- [Permissions to apply guardrails](https://docs.aws.amazon.com/bedrock/latest/userguide/guardrails-permissions.html)
- [Actions, resources, and condition keys for Amazon Bedrock](https://docs.aws.amazon.com/service-authorization/latest/reference/list_amazonbedrock.html)
- [Geographic cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/geographic-cross-region-inference.html)
- [Prerequisites for using inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-profiles-prereq.html)
- [Prerequisites for model inference](https://docs.aws.amazon.com/bedrock/latest/userguide/inference-prereq.html)
- [Manage costs with application inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/cost-mgmt-application-inference-profiles.html)
- [AWS::Cognito::IdentityPoolRoleAttachment](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-resource-cognito-identitypoolroleattachment.html)

### Data Residency & the Edge (Section 4)

- [Use interface VPC endpoints (PrivateLink) with Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/vpc-interface-endpoints.html)
- [Data protection in Amazon Bedrock (Model Deployment Accounts)](https://docs.aws.amazon.com/bedrock/latest/userguide/data-protection.html)
- [Abuse detection in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/abuse-detection.html)
- [Data retention in Amazon Bedrock](https://docs.aws.amazon.com/bedrock/latest/userguide/data-retention.html)
- [Supported Regions and models for inference profiles](https://docs.aws.amazon.com/bedrock/latest/userguide/models-region-compatibility.html)
- [Global cross-Region inference](https://docs.aws.amazon.com/bedrock/latest/userguide/global-cross-region-inference.html)
- [Encrypt custom model jobs and artifacts](https://docs.aws.amazon.com/bedrock/latest/userguide/encryption-custom-job.html)
- [What is AWS Wavelength?](https://docs.aws.amazon.com/wavelength/latest/developerguide/what-is-wavelength.html)
- [How AWS Local Zones work](https://docs.aws.amazon.com/local-zones/latest/ug/how-local-zones-work.html)
- [Hybrid cloud networking best practices (Outposts service link)](https://docs.aws.amazon.com/prescriptive-guidance/latest/hybrid-cloud-best-practices/networking.html)
- [Navigating data residency scenarios (Well-Architected lens)](https://docs.aws.amazon.com/wellarchitected/latest/data-residency-hybrid-cloud-services-lens/navigating-data-residency-scenarios.html)
- [AWS European Sovereign Cloud design approach](https://docs.aws.amazon.com/whitepapers/latest/overview-aws-european-sovereign-cloud/design-approach.html)
- [Amazon Bedrock in AWS GovCloud (US)](https://docs.aws.amazon.com/govcloud-us/latest/UserGuide/govcloud-bedrock.html)

### Application Integration & Front-End (Section 5)

- [Serverless strategies for streaming LLM responses](https://aws.amazon.com/blogs/compute/serverless-strategies-for-streaming-llm-responses/)
- [Configure REST API integration timeout](https://docs.aws.amazon.com/help-panel/apigateway/latest/console/rest-timeout.html)
- [Configure HTTP proxy integration response streaming](https://docs.aws.amazon.com/apigateway/latest/developerguide/response-streaming-http.html)
- [InvokeModelWithResponseStream (API reference)](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_runtime_InvokeModelWithResponseStream.html)
- [Configure Lambda response streaming](https://docs.aws.amazon.com/lambda/latest/dg/configuration-response-streaming.html)
- [Create a customized AI-based chat interface with your application data (Amplify AI Kit)](https://aws.amazon.com/blogs/mobile/create-a-customized-ai-based-chat-interface-with-your-application-data/)
- [Add a conversational interface to any data source (Amplify AI Kit)](https://aws.amazon.com/blogs/mobile/add-a-conversational-interface-to-any-data-source/)
- [Bedrock Data Automation now generally available](https://aws.amazon.com/blogs/aws/get-insights-from-multimodal-content-with-amazon-bedrock-data-automation-now-generally-available/)
- [Use the Bedrock Data Automation API](https://docs.aws.amazon.com/bedrock/latest/userguide/bda-using-api.html)
- [Bedrock data source parsing configuration (BDA parser)](https://docs.aws.amazon.com/AWSCloudFormation/latest/TemplateReference/aws-properties-bedrock-datasource-parsingconfiguration.html)
- [Amazon Q Developer](https://aws.amazon.com/q/developer/)
- [Customize Amazon Q Developer in your IDE with your private code base](https://aws.amazon.com/blogs/aws/customize-amazon-q-developer-in-your-ide-with-your-private-code-base/)
- [Amazon Q Developer pricing and tiers](https://aws.amazon.com/q/developer/build/)

### CI/CD & Deployment for GenAI (Section 6)

- [Deploy an Amazon Bedrock agent (versions and aliases)](https://docs.aws.amazon.com/bedrock/latest/userguide/deploy-agent.html)
- [PrepareAgent (API reference)](https://docs.aws.amazon.com/bedrock/latest/APIReference/API_agent_PrepareAgent.html)
- [Create a prompt version](https://docs.aws.amazon.com/bedrock/latest/userguide/prompt-management-version-create.html)
- [CI/CD and automation for agentic AI on serverless (Prescriptive Guidance)](https://docs.aws.amazon.com/prescriptive-guidance/latest/agentic-ai-serverless/cicd-and-automation.html)
