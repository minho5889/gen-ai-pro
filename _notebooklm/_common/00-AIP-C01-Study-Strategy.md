# AIP-C01 Exam Strategy — AWS Certified Generative AI Developer (Professional)

## Document Metadata

| Field | Value |
|-------|-------|
| Target Exam | AWS Certified Generative AI Developer - Professional (AIP-C01) |
| Format | 65 scored + 10 unscored = 75 questions |
| Question Types | Multiple choice (1 of 4) and multiple response (2+ of 5+) |
| Scoring | Scaled 100-1000, compensatory model |
| Passing Score | 750 (higher than the usual 720 — note this) |
| Level | Professional |
| Source | Official AWS AIP-C01 Exam Guide (verified) |

---

## Profile Context

This certification is the last one I need (alongside ANS-C01) to hold the full AWS catalog. My relevant background going in:

- 3 years AWS Cloud Support Engineer + AI/ML ProServe consulting experience
- AWS Certified Machine Learning — Specialty1 (MLS-C01)
- AWS Certified Machine Learning Engineer — Associate (MLA-C01)
- AWS Certified Solutions Architect — Professional (SAP-C02)
- AWS Certified DevOps Engineer — Professional (DOP-C02)
- AWS Certified Developer — Associate (DVA-C02)
- GenAI Technical Intermediate (L200), AI Foundational (L100), GenAI Essentials accreditations

This is a strong starting position. The ML Specialty and ML Engineer certs cover model evaluation, SageMaker, and data pipelines. The Developer and DevOps certs cover Lambda, API Gateway, Step Functions, CI/CD, and IAM — all of which are heavily reused here. The exam is GenAI-specific developer work layered on top of services I already know.

The gap is depth on the GenAI-native stack: Amazon Bedrock (Agents, Knowledge Bases, Guardrails, Prompt Management, Prompt Flows), AgentCore, Strands Agents, the Model Context Protocol (MCP), and RAG architecture patterns at production scale.

---

## 1. High-Yield Domains (by exam weight)

| Domain | Weight | Readiness | Priority |
|--------|--------|-----------|----------|
| Domain 1: Foundation Model Integration, Data Management, and Compliance | 31% | Medium | CRITICAL — biggest slice, RAG + vector stores live here |
| Domain 2: Implementation and Integration | 26% | Medium-High | HIGH — agentic AI is the gap; integration patterns are familiar |
| Domain 3: AI Safety, Security, and Governance | 20% | Medium | HIGH — Guardrails + Responsible AI are GenAI-specific |
| Domain 4: Operational Efficiency and Optimization | 12% | High | MODERATE — cost/perf maps to existing ops background |
| Domain 5: Testing, Validation, and Troubleshooting | 11% | Medium | MODERATE — GenAI eval differs from traditional ML eval |

Domain 1 + Domain 2 = 57% of the exam. That is where the certification is won or lost. Domain 3 (20%) is the third pillar — Guardrails, PII handling, and Responsible AI show up constantly. Domains 4 and 5 (23% combined) reward existing ops/ML instincts but require learning GenAI-specific failure modes (hallucination detection, token economics, LLM-as-a-judge).

---

## 2. Critical Services to Master

### Must-Learn (GenAI-native gaps — spend ~60% of time here)

#### Amazon Bedrock — The center of the entire exam

- Model selection: capability vs cost vs latency tradeoffs across FM families (Titan, Claude, Llama, etc.)
- Inference options: on-demand, Provisioned Throughput, Cross-Region Inference (for limited regional availability), batch inference
- Bedrock Knowledge Bases: managed RAG, chunking strategies, supported vector stores, reranking
- Bedrock Guardrails: content filters, denied topics, PII redaction, contextual grounding checks
- Bedrock Agents + AgentCore: action groups, memory, tool/function calling, agent tracing
- Bedrock Prompt Management + Prompt Flows: parameterized templates, versioning, approval workflows, no-code orchestration
- Bedrock Model Evaluation: automated, human, and LLM-as-a-judge evaluations
- Model Invocation Logging for observability

#### RAG and Vector Stores — The heart of Domain 1

- Embeddings: Amazon Titan embeddings, dimensionality, domain fit
- Vector store options: OpenSearch Service (Neural/vector plugin), Aurora PostgreSQL with pgvector, OpenSearch Serverless, others
- Chunking: fixed-size, hierarchical, semantic — and when each wins
- Retrieval quality: hybrid search (keyword + vector), reranking, query expansion/decomposition
- Metadata frameworks for filtering and precision

#### Agentic AI — The Domain 2 gap

- Strands Agents and AWS Agent Squad for multi-agent orchestration
- Model Context Protocol (MCP): clients, servers (Lambda for lightweight, ECS for complex tools)
- ReAct and chain-of-thought patterns via Step Functions
- Safeguarded workflows: stopping conditions, timeouts, circuit breakers, IAM resource boundaries

### Reinforce (know basics — fill gaps)

- Amazon Comprehend (PII detection, entity extraction, intent), Amazon Macie (PII in S3)
- Amazon Kendra (enterprise search), Amazon Q (Developer, Business)
- SageMaker AI for fine-tuned/custom model deployment, Model Registry, Model Monitor, Clarify, model cards
- Amazon Textract, Transcribe, Rekognition for multimodal pipelines
- Bedrock Data Automation

### Quick Review (strengths — confirm GenAI-specific edge cases)

- Lambda, API Gateway, Step Functions, EventBridge, SQS/SNS (integration patterns)
- IAM, KMS, Secrets Manager, Cognito, VPC endpoints/PrivateLink (security)
- CloudWatch, X-Ray, CloudTrail (observability)
- CodePipeline/CodeBuild/CodeDeploy (CI/CD for GenAI)

---

## 3. Exam Patterns

### Pattern 1: "Design a RAG architecture" (very frequent — Domain 1)

- Scenario: ground FM responses in a private corpus, keep data current, control cost
- Answer usually involves: Bedrock Knowledge Bases OR OpenSearch/Aurora pgvector + embeddings + chunking strategy
- Trap: choosing a fine-tuned model when RAG is the cheaper, fresher answer

### Pattern 2: "Reduce hallucinations / enforce safe outputs" (Domain 3)

- Answer usually involves: Bedrock Guardrails (contextual grounding), Knowledge Base grounding, structured output via JSON Schema
- Trap: confusing input filtering with output verification — defense-in-depth uses both

### Pattern 3: "Build an autonomous agent that calls tools" (Domain 2)

- Answer usually involves: Bedrock Agents/AgentCore action groups, or Strands Agents + MCP, with Step Functions for control flow
- Trap: hand-rolling orchestration when a managed agent primitive fits

### Pattern 4: "Optimize cost / latency for an FM workload" (Domain 4)

- Answer usually involves: model cascading/tiering, prompt caching, semantic caching, Provisioned Throughput, batching
- Trap: scaling compute when the real lever is token efficiency or a smaller model

### Pattern 5: "Switch models without code changes / survive an outage" (Domain 2)

- Answer usually involves: abstraction via Lambda + AppConfig, Cross-Region Inference, circuit breakers, graceful degradation
- Trap: hardcoding a single model/Region

### Pattern 6: "Evaluate FM quality before production" (Domain 5)

- Answer usually involves: Bedrock Model Evaluation, LLM-as-a-judge, RAG evaluation, golden datasets, canary/A-B testing
- Trap: applying traditional accuracy/F1 metrics to generative output

---

## 4. Proposed Textbook Structure (Deep-Dive Guides)

Following the ANS model: one numbered deep-dive guide per study block, each mapped to exam domains. Build them in priority order.

| Guide | Topic | Primary Domains | Priority |
|-------|-------|-----------------|----------|
| 01 | Foundation Models & Amazon Bedrock Core | D1 (1.1, 1.2), D2 (2.2, 2.4) | CRITICAL |
| 02 | RAG, Vector Stores & Knowledge Bases | D1 (1.3, 1.4, 1.5) | CRITICAL |
| 03 | Prompt Engineering & Management | D1 (1.6) | HIGH |
| 04 | Agentic AI: Agents, AgentCore, Strands, MCP | D2 (2.1, 2.5) | HIGH |
| 05 | Enterprise Integration & Deployment | D2 (2.3, 2.4, 2.5) | MODERATE |
| 06 | AI Safety, Security & Governance | D3 (3.1-3.4) | HIGH |
| 07 | Cost, Performance & Monitoring | D4 (4.1-4.3) | MODERATE |
| 08 | Testing, Evaluation & Troubleshooting | D5 (5.1, 5.2) | MODERATE |

Recommended build order: 01 then 02 then 06 then 04 then 03 then 08 then 07 then 05. This front-loads the two biggest Domain 1 guides plus Guardrails/Responsible AI (Domain 3), which together cover the highest-yield material.

**Status: all 8 guides are built.** Because the build order diverges from the strategy numbering, the on-disk file numbers do not match the strategy guide numbers; refer to each guide by its topic title rather than its number.

---

## 5. Where to Start

1. Start with Guide 01 (Foundation Models & Bedrock Core). Everything else builds on understanding how to select, configure, and invoke FMs on Bedrock.
2. Then Guide 02 (RAG & Vector Stores) — the single densest exam topic.
3. Then Guide 06 (Safety, Security & Governance) — Guardrails appear across multiple domains.

Each guide follows the same format as the ANS DX deep-dive: textbook-depth prose, diagrams, comparison tables, an Exam-Relevant Distinctions checklist, and Knowledge Check quizzes, with a consolidated references section at the end.

---

## 6. Key Mental Models

### RAG vs Fine-Tuning vs Prompt Engineering

**Diagram (described):** This decision tree maps a need to the right technique. If you need current or private facts with low cost and fast iteration, choose RAG using Bedrock Knowledge Bases. If you need domain tone, format, or behavior baked into the model itself, choose fine-tuning with SageMaker plus LoRA. If you need to steer behavior with no infrastructure change, choose prompt engineering combined with Guardrails.

### Defense-in-Depth for Safe GenAI

**Diagram (described):** This diagram shows three layered defenses arranged from input to output. At the input layer, Comprehend or Guardrails filter incoming requests, flowing into prompt-injection detection. At the model layer, Bedrock Guardrails enforce denied topics and contextual grounding. At the output layer, Lambda post-processing flows into JSON Schema validation and then into PII redaction. The key idea is that protections stack across all three stages rather than relying on any single checkpoint.

### Cost Lever Priority (cheapest win first)

**Diagram (described):** This is an ordered list of cost-reduction levers, cheapest win first. First, improve token efficiency through prompt compression and context pruning. Second, add caching, both prompt caching and semantic caching. Third, apply model tiering or cascading, trying a small model first and escalating only when needed. Fourth, and only at steady high volume, adopt Provisioned Throughput and batching.

---

## 7. Top Resources (in priority order)

1. Official AIP-C01 Exam Guide — domains, tasks, in-scope services (the source of truth)
2. Amazon Bedrock User Guide — Knowledge Bases, Agents, Guardrails, Prompt Management
3. AWS Well-Architected Generative AI Lens
4. AWS Skill Builder: AIP-C01 Exam Prep course and GenAI learning plans
5. Strands Agents documentation and Model Context Protocol (MCP) docs
6. Hands-on: build a RAG app + a Bedrock Agent end-to-end (the exam assumes you have done this)
