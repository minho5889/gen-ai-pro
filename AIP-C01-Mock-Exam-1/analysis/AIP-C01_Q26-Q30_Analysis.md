# AIP-C01 Practice Exam 1 — Analysis (Q26-Q30)

## Question 26

### 1. Question Summary
**Scenario:** A high-volume support classifier sees mostly routine tickets with a small fraction of genuinely ambiguous, complex cases. Leadership wants to cut model spend substantially while keeping answer quality essentially unchanged, and the team can add a confidence check on each response.

**Ask:** Which design best meets the cost and quality goals?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.2

### 3. Option Analysis
- **A** ❌ Route every request to the largest flagship model and enable Provisioned Throughput to reduce per-token cost
- **B** ✅ Send every request first to a small, fast, inexpensive model and escalate only low-confidence cases to a larger model (model cascading)
- **C** ❌ Enable a Global cross-Region inference profile so requests route to the cheapest available Region
- **D** ❌ Fine-tune the flagship model so it answers all cases more cheaply

### 4. Correct Answer Deep-Dive
**Answer: B**

Model cascading/tiering sends all traffic to a cheap fast model first and escalates only the minority of low-confidence or complex queries to a more capable model. Because most real traffic is routine, the bulk is served cheaply with little quality loss, which directly satisfies 'cut spend substantially, keep quality.' A spends more on every request. A Global profile (C) optimizes routing/throughput, not the cost-versus-capability tradeoff across query difficulty, and is never a residency answer. Fine-tuning (D) adds training and Provisioned Throughput cost and does not implement difficulty-based routing.

### 5. Key Takeaway
Model cascading/tiering sends all traffic to a cheap fast model first and escalates only the minority of low-confidence or complex queries to a more capable model.

---

## Question 27

### 1. Question Summary
**Scenario:** A claims-processing application orchestrates two foundation-model calls with a mandatory human approval gate in between: the model drafts a settlement letter, an adjuster must approve or reject it, and only then does a second model finalize the document. The team initially built this as a single Lambda and a chain of AWS Step Functions Express workflows. They want durable, auditable, retryable control flow and a reliable pause for the human decision.

**Ask:** Which TWO changes produce a correct, auditable design? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.1

### 3. Option Analysis
- **A** ✅ Implement the orchestration in AWS Step Functions using its optimized Amazon Bedrock integration instead of one long-running Lambda
- **B** ✅ Use a Step Functions Standard workflow with a Wait for Callback (task token) state for the human approval gate
- **C** ❌ Keep the Express workflow and add a Wait for Callback state for the approval gate
- **D** ❌ Replace the human gate with a fixed 5-minute Lambda timer that auto-approves
- **E** ❌ Raise the single Lambda's timeout to 15 minutes so it can wait for the adjuster inside one invocation

### 4. Correct Answer Deep-Dive
**Answer: A, B**

Step Functions with the optimized Bedrock integration (A) gives durable, retryable, auditable, multi-step FM orchestration instead of a fragile single Lambda. The human gate that must pause and resume requires the Wait for Callback (.waitForTaskToken) pattern, and that pattern is supported only on Standard workflows, not Express (B is correct, C is wrong on the workflow-type constraint). D removes the human approval the scenario mandates. E fights the design: a single Lambda cannot cleanly pause for an out-of-band human decision and still leaves weak retry/audit semantics; the 15-minute cap is also not the right tool for an indefinite human wait.

### 5. Key Takeaway
Step Functions with the optimized Bedrock integration (A) gives durable, retryable, auditable, multi-step FM orchestration instead of a fragile single Lambda.

---

## Question 28

### 1. Question Summary
**Scenario:** A central platform team runs an LLM gateway: Amazon Cognito authenticates each user, then the gateway's Lambda calls Amazon Bedrock using a single IAM role attached to the Lambda. Finance reports that all Bedrock spend appears under that one role, so they cannot attribute cost to individual business units. The team already turned on Cost Explorer and CloudTrail and still sees only the one identity.

**Ask:** What is the correct fix for per-business-unit cost attribution?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.3

### 3. Option Analysis
- **A** ❌ Enable AWS Cost Explorer granular grouping and re-run the report
- **B** ✅ Have the gateway call sts:AssumeRole per user against a Bedrock-scoped role, passing the user/tenant as the role-session-name and the business unit as session tags
- **C** ❌ Switch the gateway from REST API Gateway to an HTTP API to expose the caller identity
- **D** ❌ Move every business unit into its own AWS account before any further work

### 4. Correct Answer Deep-Dive
**Answer: B**

A single shared gateway role erases per-user identity in billing, which is why Cost Explorer and CloudTrail only ever show that one role. AWS's recommended multi-tenant pattern (Scenario 4) is for the gateway to assume a Bedrock-scoped role per user, using the tenant/user as the role-session-name and the business unit as session tags, which then appear in CUR 2.0 for attribution. A and C surface nothing new because the underlying identity is still the shared role. Account-per-tenant (D) is a heavier strong-isolation strategy, not the targeted attribution fix this scenario needs.

### 5. Key Takeaway
A single shared gateway role erases per-user identity in billing, which is why Cost Explorer and CloudTrail only ever show that one role.

---

## Question 29

### 1. Question Summary
**Scenario:** A platform team wants a partner in a separate AWS account to query a specific Amazon Bedrock Knowledge Base. By analogy to how they share an Amazon S3 bucket, they plan to attach a resource-based policy to the Knowledge Base granting the partner account access.

**Ask:** Will this approach work, and what is the correct mechanism?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.3

### 3. Option Analysis
- **A** ✅ Yes, attach a resource-based policy to the Knowledge Base just as you would an S3 bucket policy
- **B** ❌ No, Bedrock does not support resource-based policies on GenAI resources; cross-account access uses an assumed role in the owning account plus identity-based policies and SCPs
- **C** ❌ Yes, but the resource policy works only for the Retrieve action and not RetrieveAndGenerate
- **D** ❌ No, cross-account sharing requires migrating the Knowledge Base into the partner account

### 4. Correct Answer Deep-Dive
**Answer: A**

Yes — the S3-bucket-policy analogy now holds for knowledge bases. Amazon Bedrock supports attaching a resource-based policy directly to a managed knowledge base (via PutResourcePolicy / GetResourcePolicy / DeleteResourcePolicy), naming the partner account's principals and granting the data-plane query actions. That is exactly the cross-account sharing mechanism: the owner attaches the resource policy, and the calling principal in the partner account also needs a matching identity-based policy on the knowledge base ARN (standard cross-account evaluation — both sides must allow). Know the caveats: it works for managed knowledge bases only (type MANAGED, not VECTOR); the grantable actions are bedrock:Retrieve and bedrock:GetDocumentContent (control-plane operations like GetKnowledgeBase or UpdateKnowledgeBase cannot be granted cross-account and stay with the owner); and wildcards are not allowed in the Resource or Action elements. B states the older general rule — most Bedrock GenAI resources still don't take resource-based policies, and assumed-role patterns remain valid — but it is wrong here because knowledge bases are now the documented exception for cross-account querying. C is wrong because the policy grants both Retrieve and GetDocumentContent, not Retrieve alone (the grain of truth: RetrieveAndGenerate is not a grantable resource-policy action). D is unnecessary — sharing works in place without migrating the resource.

> Note: answer key corrected during AWS-doc fact-check. Source: https://docs.aws.amazon.com/bedrock/latest/userguide/kb-managed-cross-account.html

### 5. Key Takeaway
Managed Bedrock knowledge bases support resource-based policies (PutResourcePolicy) for cross-account querying — scoped to bedrock:Retrieve and bedrock:GetDocumentContent, requiring an allow on both the resource policy and the caller's identity policy; control-plane operations never cross accounts.

---

## Question 30

### 1. Question Summary
**Scenario:** A gaming company wants ultra-low latency to 5G mobile users for a generative-AI feature and proposes 'running the Amazon Bedrock model at the edge inside an AWS Wavelength Zone.' Compliance has no data-residency constraint; the only goal is minimal latency to mobile devices.

**Ask:** What is the correct architecture?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.3

### 3. Option Analysis
- **A** ❌ Deploy the Amazon Bedrock inference data plane into the Wavelength Zone
- **B** ✅ Place the application/inference-orchestration tier in the Wavelength Zone and let the Bedrock model call go to the parent Region
- **C** ❌ Use AWS Local Zones instead, because they support VPC interface endpoints directly to Bedrock
- **D** ❌ Self-host the model on AWS Outposts inside the carrier facility

### 4. Correct Answer Deep-Dive
**Answer: B**

Amazon Bedrock is a Regional, serverless service; there is no documented way to run its inference data plane on Wavelength, Local Zones, or Outposts, which host only EC2-based compute and storage. The correct pattern is to put the latency-sensitive application/orchestration tier at the edge (Wavelength) while the model invocation still goes to Bedrock in the parent Region. A is impossible. C is wrong on two counts: Bedrock does not run in Local Zones, and Local Zones do not support VPC endpoints. D self-hosting on Outposts is unnecessary and does not provide Bedrock.

### 5. Key Takeaway
Amazon Bedrock is a Regional, serverless service; there is no documented way to run its inference data plane on Wavelength, Local Zones, or Outposts, which host only EC2-based compute and storage.

---

