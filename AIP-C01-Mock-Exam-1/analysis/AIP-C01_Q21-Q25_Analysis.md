# AIP-C01 Practice Exam 1 — Analysis (Q21-Q25)

## Question 21

### 1. Question Summary
**Scenario:** A logistics company is building a customer-service handler. For each inbound message it must look up the order in DynamoDB, then conditionally call a carrier shipping API, and only if the package is confirmed delayed, invoke a billing API to issue a refund credit, and finally reply. The exact sequence of calls and whether the refund step runs depend entirely on what each prior lookup returns. The team wants the fastest path to production and the least orchestration code to own.

**Ask:** Which implementation best fits this requirement?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ A self-managed Converse client-side tool-use loop, where the application detects each tool_use stop reason, executes the call, and re-invokes
- **B** ✅ An Amazon Bedrock Agent with action groups for the order, shipping, and billing operations
- **C** ❌ A fixed AWS Step Functions Standard workflow that always invokes the order, shipping, and billing tasks in sequence
- **D** ❌ A single prompt that instructs the model to describe the steps a downstream system should take

### 4. Correct Answer Deep-Dive
**Answer: B**

The control flow branches on intermediate results and the number/sequence of tool calls is unknown in advance, which is the signature of a task that needs an agent's model-driven reasoning loop rather than a fixed flow. Among agent options, the requirement for the fastest managed path with the least orchestration code points to Amazon Bedrock Agents, the managed primitive that runs the reason-act-observe loop, action invocation, and conversation state for you (the Pattern 3 'use the managed primitive, do not hand-roll the loop' lesson). A is the self-managed primitive that hand-rolls exactly what Bedrock Agents manages, contradicting 'least orchestration code.' C is deterministic and would issue refunds unconditionally or require hand-coding every branch, brittle for runtime-dependent flow. D cannot call external APIs or take actions.

### 5. Key Takeaway
The control flow branches on intermediate results and the number/sequence of tool calls is unknown in advance, which is the signature of a task that needs an agent's model-driven reasoning loop rather than a fixed flow.

---

## Question 22

### 1. Question Summary
**Scenario:** An MCP server fronts an internal database for an autonomous agent. To move fast, the platform team gave the server's IAM role broad permissions and configured the server to reuse the bearer token that authenticated the end user to the agent. A user who holds administrator privileges asked the agent to clone a production database into pre-production; the model also hallucinated an extra 'clean up the old database' step, and the destructive DELETE succeeded.

**Ask:** Which TWO changes would have contained the blast radius of the model's mistake? (Select TWO)

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.1

### 3. Option Analysis
- **A** ✅ Have the MCP server use an explicitly scoped, purpose-generated downstream token carrying only READ and CREATE for this task
- **B** ❌ Propagate the user's administrator token unchanged but log every downstream call to CloudTrail for after-the-fact review
- **C** ❌ Attach a Bedrock Guardrail with a denied topic for the word 'delete'
- **D** ✅ Apply least-privilege IAM to the tool's role and scope permissions to the acceptable scope of impact rather than to intended functionality
- **E** ❌ Increase the agent's maximum-iterations limit so it has more chances to self-correct

### 4. Correct Answer Deep-Dive
**Answer: A, D**

This is excessive agency (OWASP LLM06). Scoped, purpose-generated downstream tokens (A) mean a hallucinated DELETE simply fails because the credentials never carried DELETE, and least-privilege IAM scoped to acceptable impact (D) is the AWS-named mitigation: assume any granted permission could be used. B keeps the over-broad admin token in play; CloudTrail is detective, not preventive, and does not stop the delete. C is a content filter, not an access control, and cannot reliably prevent the model from selecting a destructive tool. E increases, not decreases, the opportunities to take wrong actions.

### 5. Key Takeaway
This is excessive agency (OWASP LLM06).

---

## Question 23

### 1. Question Summary
**Scenario:** A team exposes an internal 'currency conversion' tool to its agents as a remote MCP server. Each call returns in a few hundred milliseconds, holds no session state between calls, and traffic is spiky: quiet for hours, then hundreds of requests in a burst. The team wants the lowest operational overhead and to avoid paying for idle capacity.

**Ask:** Which compute option should host this MCP server?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ Amazon ECS on AWS Fargate running the server as a long-lived containerized service
- **B** ✅ AWS Lambda
- **C** ❌ An always-on Amazon EC2 instance behind an Application Load Balancer
- **D** ❌ A local stdio subprocess installed on each user's machine

### 4. Correct Answer Deep-Dive
**Answer: B**

Lightweight, stateless, bursty tool calls are the canonical fit for AWS Lambda: it auto-scales to the request rate, scales to zero when idle (no idle cost), bills per use, and each short self-contained call needs no server-side session. ECS on Fargate (A) targets long-running, sessionful, streaming-heavy, or dependency-heavy servers and would pay for idle capacity here. An always-on EC2 instance (C) also pays for idle capacity and adds management overhead. A local subprocess (D) is for a single developer machine, not a shared tool serving many agents.

### 5. Key Takeaway
Lightweight, stateless, bursty tool calls are the canonical fit for AWS Lambda: it auto-scales to the request rate, scales to zero when idle (no idle cost), bills per use, and each short self-contained call needs no server-side session.

---

## Question 24

### 1. Question Summary
**Scenario:** A research workflow built with the Strands Agents SDK must coordinate several specialist agents (researcher, architect, coder, reviewer) where the handoff path is not fixed in advance and agents self-organize, passing work to whichever peer is best suited as new findings emerge. A separate billing workflow is a fixed, repeatable ETL-style sequence whose dependency graph never changes and whose independent steps can run in parallel.

**Ask:** Which Strands multi-agent primitives correctly match the two workflows?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.1

### 3. Option Analysis
- **A** ✅ Swarm for the research workflow; Workflow for the billing workflow
- **B** ❌ Workflow for the research workflow; Swarm for the billing workflow
- **C** ❌ Graph for the research workflow; Agents-as-Tools for the billing workflow
- **D** ❌ Agents-as-Tools for the research workflow; Graph for the billing workflow

### 4. Correct Answer Deep-Dive
**Answer: A**

A Swarm is an autonomous team of agents that self-organize and hand off to the best-suited peer through shared memory with emergent (not pre-fixed) flow, matching the research case. A Workflow is a pre-defined task DAG executed as one reusable tool with deterministic parallel execution and no cycles, matching the fixed ETL-style billing sequence. B inverts the two. Graph is a developer-defined flowchart with conditional branching and loops (used when flow is controlled but dynamic) and Agents-as-Tools is hierarchical delegation under one orchestrator, so C and D mislabel both workflows.

### 5. Key Takeaway
A Swarm is an autonomous team of agents that self-organize and hand off to the best-suited peer through shared memory with emergent (not pre-fixed) flow, matching the research case.

---

## Question 25

### 1. Question Summary
**Scenario:** A bank fine-tuned an Amazon Bedrock foundation model on its labeled credit-policy data to enforce a consistent specialized response format that prompting alone could not reliably produce. It now needs to serve this customized model in a steady, high-volume production application and is deciding how to provision inference capacity.

**Ask:** How must the bank serve the fine-tuned model?

### 2. Domain Mapping
**Domain:** Domain 2: Implementation and Integration
**Task:** Task 2.2

### 3. Option Analysis
- **A** ❌ On-demand inference, paying per token with no commitment
- **B** ❌ Batch inference with JSONL input and output in Amazon S3
- **C** ✅ Provisioned Throughput, purchasing Model Units for the customized model
- **D** ❌ A Global cross-Region inference profile for maximum throughput

### 4. Correct Answer Deep-Dive
**Answer: C**

A customized (fine-tuned, distilled, or imported) Bedrock model can only be invoked through Provisioned Throughput; it cannot be served on-demand. This is one of the most reliably tested deployment facts. On-demand (A) does not serve custom models. Batch inference (B) is its own mode and is not supported for provisioned/custom serving, and the workload is real-time high-volume anyway. Cross-Region inference profiles (D) route on-demand requests across Regions for base models and do not make a fine-tuned model invokable on-demand.

### 5. Key Takeaway
A customized (fine-tuned, distilled, or imported) Bedrock model can only be invoked through Provisioned Throughput; it cannot be served on-demand.

---

