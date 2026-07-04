# AIP-C01 Practice Exam 2 — Analysis (Q26-Q30)

## Question 26

### 1. Question Summary
**Scenario:** A regulated insurer fine-tuned a foundation model on Amazon Bedrock to enforce a consistent claims-summary format that prompting could not reliably produce. They now need to run this custom model in production, serving steady high-volume traffic with a predictable latency profile. An engineer's first implementation calls the custom model with on-demand InvokeModel and is receiving validation errors at invocation time.

**Ask:** What is the correct deployment approach, and why is the on-demand attempt failing?

### 2. Domain Mapping
**Domain:** 2.2 Model deployment strategies
**Task:** Task 2.2

### 3. Option Analysis
- **A** ❌ Use batch inference for the custom model, because batch is the only mode that supports fine-tuned models
- **B** ✅ Use Provisioned Throughput for this steady high-volume, latency-sensitive workload; the on-demand call fails because a custom model cannot be invoked directly by its model ARN — it must be served through Provisioned Throughput or first deployed as a custom model deployment (the on-demand path better suited to variable or low traffic)
- **C** ❌ Keep on-demand but request a service quota increase on InvokeModel for custom models
- **D** ❌ Re-host the fine-tuned model on a SageMaker real-time endpoint, because Bedrock cannot serve any custom model

### 4. Correct Answer Deep-Dive
**Answer: B**

The validation error happens because a custom model needs a serving surface before it can be invoked: you cannot call InvokeModel against the custom model's ARN directly. Current Bedrock documentation gives two options — purchase Provisioned Throughput and invoke the provisioned resource, or create a custom model deployment and invoke its deployment ARN for on-demand, pay-per-token inference. For this workload — steady high-volume traffic with a predictable latency profile — Provisioned Throughput is the fit: dedicated capacity with guaranteed throughput and consistent latency, which the on-demand deployment path does not guarantee. Batch inference (A) is for offline bulk work, not steady real-time traffic. C misreads the failure: it is a validation error from invoking an unservable ARN, not a throttle — no quota increase makes direct model-ARN invocation work. Re-hosting on SageMaker (D) is unnecessary, and the premise that Bedrock cannot serve custom models is false — it serves them via Provisioned Throughput or custom model deployments.

> Note: key updated during re-verification — an earlier version stated custom models "can only be invoked through Provisioned Throughput." Current documentation (model-customization-use) also offers on-demand inference via custom model deployments; PT remains the credited choice here because the scenario specifies steady high volume with a predictable latency profile. Point-in-time — re-verify near exam day.

### 5. Key Takeaway
A custom model is never invoked by its model ARN directly — serve it through Provisioned Throughput (steady high volume, guaranteed throughput/latency) or a custom model deployment for on-demand inference (variable or low traffic), and match the choice to the traffic profile.

---

## Question 27

### 1. Question Summary
**Scenario:** A product team wants to cut foundation-model spend on a high-volume Q and A feature with minimal quality loss. Analysis shows roughly 85 percent of incoming questions are routine and can be answered correctly by a small, fast, inexpensive model, while a minority are genuinely complex. They want the bulk of traffic served cheaply and only the hard queries escalated to a larger, more capable model.

**Ask:** Which deployment/serving strategy best fits this goal?

### 2. Domain Mapping
**Domain:** 2.2 Model deployment strategies
**Task:** Task 2.2

### 3. Option Analysis
- **A** ❌ Purchase Provisioned Throughput on the largest model and route all traffic to it for predictable latency
- **B** ✅ Model cascading/tiering: send every request to the small cheap model first, and escalate only the queries it cannot answer confidently to the larger model
- **C** ❌ Run all traffic through batch inference to capture the batch discount
- **D** ❌ Fine-tune the small model on the complex queries so a single model handles everything

### 4. Correct Answer Deep-Dive
**Answer: B**

Model cascading/tiering routes every request to a small, cheap, fast model first and escalates only the queries that fail a confidence check to a larger model; because most traffic is routine, the bulk is served cheaply with minimal quality loss - exactly the 85-percent-routine profile described. Provisioned Throughput on the largest model (A) maximizes cost for all traffic. Batch (C) is for non-interactive offline work and breaks the real-time Q and A experience, plus it does not support tool calling/structured-output workflows. Fine-tuning the small model (D) is the costly, inflexible path and does not address routing routine vs complex traffic by cost.

### 5. Key Takeaway
Model cascading/tiering routes every request to a small, cheap, fast model first and escalates only the queries that fail a confidence check to a larger model; because most traffic is routine, the bulk is served cheaply with minimal quality loss - exactly the 85-percent-routine profile described.

---

## Question 28

### 1. Question Summary
**Scenario:** A company runs a centralized LLM gateway: each user authenticates to the gateway via Amazon Cognito, and the gateway's Lambda calls Amazon Bedrock using one IAM role attached to the gateway compute. Finance reports that all Bedrock spend appears under a single identity and they cannot attribute cost to individual business units. An engineer proposes enabling Cost Explorer and turning on CloudTrail for Bedrock to fix it.

**Ask:** What is the correct fix for per-tenant cost attribution?

### 2. Domain Mapping
**Domain:** 2.3 Enterprise integration architectures
**Task:** Task 2.3

### 3. Option Analysis
- **A** ❌ Enable AWS Cost Explorer and activate cost-allocation tags on the gateway role
- **B** ❌ Turn on CloudTrail data events for Bedrock so each user's calls are itemized
- **C** ✅ Have the gateway call sts:AssumeRole per user on a Bedrock-scoped role, passing the user/tenant as the role-session-name and the business unit as session tags
- **D** ❌ Give every business unit its own Bedrock model alias and tag the aliases

### 4. Correct Answer Deep-Dive
**Answer: C**

A single shared gateway role erases per-user identity in billing, so even built-in granular cost attribution shows only the gateway role. AWS's recommended multi-tenant pattern (Scenario 4) is for the gateway to call sts:AssumeRole per user against a Bedrock-scoped role, passing the tenant/user as the role-session-name and the business unit as session tags, which restores per-tenant attribution in CUR 2.0. Cost Explorer (A) and CloudTrail (B) only ever show the shared role's spend - they cannot manufacture per-user identity that was never presented to Bedrock. Model aliases (D) are not a cost-attribution mechanism for per-tenant invoke spend.

### 5. Key Takeaway
A single shared gateway role erases per-user identity in billing, so even built-in granular cost attribution shows only the gateway role.

---

## Question 29

### 1. Question Summary
**Scenario:** A platform team wants a least-privilege IAM policy that lets an application invoke a specific Bedrock Agent through its production alias. They wrote a policy granting bedrock:InvokeAgent on arn:aws:bedrock:us-east-1:123456789012:agent/ABC123 and the application receives AccessDenied when it calls the agent through the alias.

**Ask:** Why does the call fail, and what is the correct resource ARN?

### 2. Domain Mapping
**Domain:** 2.3 Enterprise integration - identity and RBAC
**Task:** Task 2.3

### 3. Option Analysis
- **A** ✅ InvokeAgent must be granted on the agent-alias ARN (agent-alias/AGENT-ID/ALIAS-ID); the agent ARN is used only for management actions like UpdateAgent and GetAgent
- **B** ❌ Bedrock Agents require a resource-based policy on the agent; attach one granting InvokeAgent
- **C** ❌ The policy must use Resource * because InvokeAgent has no resource type
- **D** ❌ The application must also be granted bedrock:InvokeModel on the agent ARN

### 4. Correct Answer Deep-Dive
**Answer: A**

bedrock:InvokeAgent must be scoped to the agent-alias ARN (agent-alias/AGENT-ID/ALIAS-ID), not the agent ARN - the agent ARN is for management actions such as UpdateAgent and GetAgent. This alias-vs-agent swap is a classic distractor. Bedrock has no resource-based policies (B). InvokeAgent does have a resource type, so Resource * (C) is wrong and over-broad. InvokeModel on the agent ARN (D) is not the missing permission; the issue is the wrong resource ARN for InvokeAgent.

### 5. Key Takeaway
bedrock:InvokeAgent must be scoped to the agent-alias ARN (agent-alias/AGENT-ID/ALIAS-ID), not the agent ARN - the agent ARN is for management actions such as UpdateAgent and GetAgent.

---

## Question 30

### 1. Question Summary
**Scenario:** A healthcare provider must keep in-scope patient data stored and processed only within a single country for legal residency. A solutions architect proposes routing inference through Amazon Bedrock for higher throughput and is evaluating routing scopes and edge options. The team also asks whether they can lower latency to mobile clinic apps over 5G by 'running the model at the edge.'

**Ask:** Which TWO statements are correct for this residency-constrained design? (Select TWO.)

### 2. Domain Mapping
**Domain:** 2.3 Enterprise integration - data residency and edge
**Task:** Task 2.3

### 3. Option Analysis
- **A** ✅ In-Region inference (or a single in-country Region) satisfies the requirement that data must not leave the country
- **B** ❌ Global cross-Region inference satisfies the residency requirement because it is billed at source-Region rates
- **C** ❌ Geographic (Geo) cross-Region inference guarantees data never leaves the single country, since billing stays in the source Region
- **D** ✅ Bedrock cannot be deployed into a Wavelength Zone; place the application/inference-orchestration tier at the 5G edge while the model call still goes to Bedrock in-Region
- **E** ❌ Deploying Bedrock onto AWS Outposts is required so the model runs in-country
- **F** ❌ Enabling cross-Region inference has no effect on where abuse-detection-retained data is stored

### 4. Correct Answer Deep-Dive
**Answer: AD**

In-Region inference (or a single in-country Region) is the strict residency answer - data stays in one Region/country. Bedrock is a Regional, serverless service that does not run on Wavelength/Local Zones/Outposts, so the edge zone hosts the app/orchestration tier for low latency while the model call goes to Bedrock in-Region. Global inference (B) routes anywhere and is never a residency answer. Geo inference (C) keeps data within a geography but may move it between Regions inside that geography, so it does not guarantee a single country. Outposts cannot host Bedrock (E). Enabling cross-Region inference can move abuse-detection-retained data to the destination Region (F is false).

### 5. Key Takeaway
In-Region inference (or a single in-country Region) is the strict residency answer - data stays in one Region/country.

---

