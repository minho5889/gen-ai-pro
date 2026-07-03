# AIP-C01 Practice Exam 2 — Analysis (Q21-Q25)

## Question 21

### 1. Question Summary
**Scenario:** A logistics company is building a single Strands Agents workflow that must coordinate several specialist agents. The process is a repeatable nightly ETL-style sequence: validate inbound manifests, enrich them against a reference dataset, reconcile against shipment records, and emit a report. The sub-tasks have a fixed dependency order that never changes between runs, several enrichment sub-tasks can run in parallel, and the team wants to encapsulate the whole thing as one reusable, non-conversational tool that other agents can call. The model should not be deciding the path at runtime.

**Ask:** Which Strands Agents multi-agent primitive best fits this requirement?

### 2. Domain Mapping
**Domain:** 2.1 Agentic AI and tool integrations
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ Swarm, because the agents can self-organize and hand off to the best-suited peer
- **B** ✅ Workflow, because it is a pre-defined task graph (DAG) executed deterministically with parallelism as one reusable, non-conversational tool
- **C** ❌ Graph, because the model picks which edge to follow at each node based on conditional logic
- **D** ❌ Agents-as-tools, because an orchestrator model decides at runtime which specialist to invoke

### 4. Correct Answer Deep-Dive
**Answer: B**

The Strands Workflow primitive is a pre-defined task graph (a DAG) executed as one reusable, non-conversational tool with deterministic, parallel flow fixed by the dependency graph and no cycles - exactly a repeatable nightly pipeline whose order never changes. Swarm (emergent peer handoffs with cycles) and Graph (model picks edges with branching/loops) both let the model decide the flow at runtime, which the scenario explicitly forbids. Agents-as-tools is hierarchical delegation where the orchestrator model chooses the specialist - again runtime decision-making, not a fixed DAG.

### 5. Key Takeaway
The Strands Workflow primitive is a pre-defined task graph (a DAG) executed as one reusable, non-conversational tool with deterministic, parallel flow fixed by the dependency graph and no cycles - exactly a repeatable nightly pipeline whose order never changes.

---

## Question 22

### 1. Question Summary
**Scenario:** A bank operates an agentic assistant for mortgage customers built entirely on Amazon Bedrock Agents. A supervisor Bedrock Agent is associated with three collaborator Bedrock Agents (existing-mortgage, new-mortgage, and general-questions). Product owners report that most customer questions are cleanly about exactly one of these areas, and they are seeing higher-than-necessary response latency. They want the supervisor to send each query to the single most appropriate collaborator, which produces the final answer, rather than gathering and combining contributions from several collaborators.

**Ask:** Which configuration of Amazon Bedrock multi-agent collaboration meets this requirement?

### 2. Domain Mapping
**Domain:** 2.1 Agentic AI and tool integrations
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ Plain Supervisor mode, so the supervisor synthesizes the collaborators' contributions into one final response
- **B** ✅ Supervisor with routing mode, so the supervisor routes the query to the single most appropriate collaborator, which produces the final response and reduces latency
- **C** ❌ Replace the design with AWS Agent Squad's intent classifier, because Bedrock cannot route to a single collaborator
- **D** ❌ Enable conversation history so the supervisor shares full context with every collaborator on each turn

### 4. Correct Answer Deep-Dive
**Answer: B**

Bedrock multi-agent collaboration has two modes: plain Supervisor (gather and synthesize contributions from several collaborators) and Supervisor with routing (send the query to one collaborator that produces the final response, which AWS notes reduces latency because the supervisor is not waiting on and combining multiple responses). Plain Supervisor (A) is the synthesize mode the team wants to avoid. Agent Squad (C) is an unnecessary rebuild and the premise that Bedrock cannot route is false. Conversation history (D) shares context but does not change the synthesize-versus-route behavior and does not reduce latency.

### 5. Key Takeaway
Bedrock multi-agent collaboration has two modes: plain Supervisor (gather and synthesize contributions from several collaborators) and Supervisor with routing (send the query to one collaborator that produces the final response, which AWS notes reduces latency because the supervisor is not waiting on and combining multiple responses).

---

## Question 23

### 1. Question Summary
**Scenario:** A team is hardening an agent that calls internal tools through MCP servers. A user with broad administrator entitlements asks the agent to clone a production database into a pre-production environment. The agent legitimately needs only READ (to copy the source) and CREATE (to write the clone). The security review must prevent a hallucinated or prompt-injected destructive step (for example, a DELETE on the source) from ever succeeding, and must keep a token minted for one MCP server from being replayed against another.

**Ask:** Which TWO practices directly address these requirements? (Select TWO.)

### 2. Domain Mapping
**Domain:** 2.1 Agentic AI, tool integrations, and MCP security
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ Have the MCP server reuse the user's admin token for downstream calls so permissions stay consistent
- **B** ❌ Issue an explicitly scoped, purpose-generated downstream token carrying only READ and CREATE, so a hallucinated DELETE fails
- **C** ❌ Retrieve a different token per tool and validate the audience (aud) claim so a token minted for one server cannot be replayed against another
- **D** ❌ Grant the action-group Lambda role AdministratorAccess and rely on Bedrock Guardrails to block destructive intent
- **E** ❌ Disable CloudTrail logging on the MCP servers to reduce token exposure in logs
- **F** ❌ Propagate the user identity by widening every tool role to match the user's session permissions

### 4. Correct Answer Deep-Dive
**Answer: BC**

Least privilege through scoped, purpose-generated tokens (only READ and CREATE here) makes a hallucinated or injected DELETE fail even though the human is an admin - the canonical clone-DB rule. Token isolation - a different token per tool plus aud-claim validation - prevents a token for one server being replayed against another. Reusing the admin token (A) and widening tool roles to the user's permissions (F) are the exact credential-propagation antipatterns being prevented. AdministratorAccess plus Guardrails (D) is not least privilege - Guardrails filter content, they do not constrain IAM actions. Disabling CloudTrail (E) removes audit, the opposite of hardening.

### 5. Key Takeaway
Least privilege through scoped, purpose-generated tokens (only READ and CREATE here) makes a hallucinated or injected DELETE fail even though the human is an admin - the canonical clone-DB rule.

---

## Question 24

### 1. Question Summary
**Scenario:** A platform team needs to expose an internal document-intelligence tool through an MCP server. The tool maintains large warm in-memory caches and persistent streaming connections that must survive across many requests, bundles heavy native processing libraries, must sustain stable high-throughput concurrency, and has to run inside a VPC alongside the private data stores it fronts. They will run the server themselves (they are not using a fully managed tool-access service).

**Ask:** Which compute option is the best home for this remote MCP server?

### 2. Domain Mapping
**Domain:** 2.1 Agentic AI, MCP server hosting
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ AWS Lambda, because it auto-scales and scales to zero for cost efficiency
- **B** ❌ A local stdio subprocess on each user's machine
- **C** ✅ Amazon ECS on AWS Fargate as a long-lived containerized service
- **D** ❌ Amazon API Gateway with a mock integration

### 4. Correct Answer Deep-Dive
**Answer: C**

Long-lived warm caches, persistent streaming connections, heavy native dependencies, stable high concurrency, and VPC residence are precisely the profile AWS maps to Amazon ECS on Fargate - a long-lived container with full runtime control and VPC/ALB/WAF integration that supports MCP's stateful transport mode. Lambda (A) suits lightweight, stateless, bursty tools with short bounded execution and cannot hold long-lived sessions or warm caches across calls. A local subprocess (B) is for a single developer, not a shared enterprise tool. API Gateway with a mock integration (D) does not host server logic at all.

### 5. Key Takeaway
Long-lived warm caches, persistent streaming connections, heavy native dependencies, stable high concurrency, and VPC residence are precisely the profile AWS maps to Amazon ECS on Fargate - a long-lived container with full runtime control and VPC/ALB/WAF integration that supports MCP's stateful transport mode.

---

## Question 25

### 1. Question Summary
**Scenario:** An agentic data-cleanup workflow calls an external enrichment API through an action group. During an outage the external API began timing out, and the agent kept retrying the call across many iterations, piling up requests and exhausting Lambda concurrency until other workloads were starved. The team wants a control that, once failures or timeouts against that dependency exceed a threshold, stops routing requests to it and fails fast (or degrades), then probes periodically to detect recovery.

**Ask:** Which safeguarding control matches this requirement?

### 2. Domain Mapping
**Domain:** 2.1 Agentic AI, safeguarding loops
**Task:** Task 2.1

### 3. Option Analysis
- **A** ❌ A per-call timeout on the action-group Lambda function
- **B** ❌ A maximum-iterations cap on the agent's reason-act-observe loop
- **C** ✅ A circuit breaker (for example, implemented with Step Functions and DynamoDB) that opens when failures exceed a threshold and probes for recovery
- **D** ❌ Bedrock Guardrails denied-topics policy on the enrichment responses

### 4. Correct Answer Deep-Dive
**Answer: C**

A circuit breaker bounds repeated failures across many calls: when failures or timeouts to a dependency exceed a threshold it opens the circuit, returns immediate failures instead of letting timeouts cascade and exhaust resources, then probes periodically to detect recovery. A per-call timeout (A) bounds one call's duration but does not stop the agent from repeatedly retrying a failing dependency. Maximum iterations (B) bounds loop count generally but is not the fail-fast-on-repeated-failure control. Guardrails (D) govern content safety, not dependency failure handling.

### 5. Key Takeaway
A circuit breaker bounds repeated failures across many calls: when failures or timeouts to a dependency exceed a threshold it opens the circuit, returns immediate failures instead of letting timeouts cascade and exhaust resources, then probes periodically to detect recovery.

---

