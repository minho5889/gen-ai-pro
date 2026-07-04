# AIP-C01 Exam Blueprint — Domains, Tasks, and In-Scope Services

Source: Official AWS Certified Generative AI Developer - Professional (AIP-C01) Exam Guide. Verified content outline. Use this as the source-of-truth reference when authoring deep-dive study guides.

---

## Exam Facts

- 65 scored questions + 10 unscored (75 total)
- Multiple choice (1 correct of 4) and multiple response (2+ correct of 5+)
- Scaled score 100-1000, minimum passing score 750
- Compensatory scoring (pass overall, not per-domain)
- Target candidate: 2+ years building production apps on AWS, general AI/ML or data engineering experience, 1 year hands-on GenAI

Out of scope for the candidate: model development and training, advanced ML techniques, data/feature engineering.

---

## Domain 1: Foundation Model Integration, Data Management, and Compliance (31%)

- Task 1.1: Analyze requirements and design GenAI solutions (architecture design, PoC on Bedrock, WA GenAI Lens).
- Task 1.2: Select and configure FMs (benchmarks/capability analysis, dynamic model switching via Lambda/API Gateway/AppConfig, resilience via Step Functions circuit breakers + Bedrock Cross-Region Inference, customization via SageMaker AI + LoRA + Model Registry).
- Task 1.3: Implement data validation and processing pipelines (Glue Data Quality, SageMaker Data Wrangler, multimodal processing, model-specific input formatting, Comprehend enrichment).
- Task 1.4: Design and implement vector store solutions (Bedrock Knowledge Bases, OpenSearch Neural plugin, RDS/S3, DynamoDB; metadata frameworks; sharding/indexing; data freshness/sync).
- Task 1.5: Design retrieval mechanisms (chunking strategies, Titan embeddings, OpenSearch/Aurora pgvector/Knowledge Bases vector search, hybrid search + rerankers, query expansion/decomposition, function calling + MCP access).
- Task 1.6: Prompt engineering strategies and governance (Bedrock Prompt Management, Guardrails, parameterized templates, approval workflows, CloudTrail usage tracking).

## Domain 2: Implementation and Integration (26%)

- Task 2.1: Agentic AI solutions and tool integrations (Strands Agents, AWS Agent Squad, MCP; ReAct/chain-of-thought via Step Functions; stopping conditions/timeouts/circuit breakers; model ensembles; human-in-the-loop; MCP servers on Lambda/ECS).
- Task 2.2: Model deployment strategies (Lambda on-demand, Bedrock Provisioned Throughput, SageMaker endpoints, container patterns for GPU/memory/token capacity, model cascading).
- Task 2.3: Enterprise integration architectures (API/event-driven integration, API Gateway microservices, identity federation + RBAC + least privilege, Outposts/Wavelength for data residency/edge, CI/CD + GenAI gateway).
- Task 2.4: FM API integrations (Bedrock APIs sync/async with SQS, streaming APIs + WebSockets/SSE, exponential backoff + rate limiting + X-Ray, intelligent model routing).
- Task 2.5: Application integration patterns and dev tools (API Gateway streaming/token limits, Amplify UI, Bedrock Prompt Flows no-code, Bedrock Data Automation, Amazon Q Developer, Strands/Agent Squad orchestration, CloudWatch Logs Insights + X-Ray troubleshooting).

## Domain 3: AI Safety, Security, and Governance (20%)

- Task 3.1: Input and output safety controls (Bedrock Guardrails, custom moderation via Step Functions/Lambda, hallucination reduction via Knowledge Base grounding + confidence scoring + JSON Schema, defense-in-depth, prompt-injection/jailbreak detection).
- Task 3.2: Data security and privacy controls (VPC endpoints, IAM, Lake Formation, Comprehend/Macie PII detection, Bedrock data privacy features, S3 Lifecycle retention, data masking/anonymization).
- Task 3.3: AI governance and compliance (SageMaker model cards, Glue data lineage + Data Catalog, metadata tagging, CloudTrail/CloudWatch Logs audit, drift/bias monitoring, token-level redaction).
- Task 3.4: Responsible AI principles (reasoning displays, confidence metrics, Bedrock agent tracing, fairness metrics + A/B testing, LLM-as-a-judge evaluations, model cards documenting limitations).

## Domain 4: Operational Efficiency and Optimization for GenAI Applications (12%)

- Task 4.1: Cost optimization and resource efficiency (token estimation/tracking, context window optimization, prompt compression/pruning, cost-capability model selection, tiered FM usage, batching, provisioned throughput, semantic/prompt/edge caching).
- Task 4.2: Optimize application performance (pre-computation, latency-optimized Bedrock models, parallel requests, streaming, retrieval/index optimization, temperature/top-k/top-p tuning, A/B testing).
- Task 4.3: Monitoring systems (observability dashboards, CloudWatch token usage + hallucination rate + response quality, Bedrock Model Invocation Logs, anomaly detection, tool-calling observability, vector store monitoring, golden datasets for hallucination detection).

## Domain 5: Testing, Validation, and Troubleshooting (11%)

- Task 5.1: Evaluation systems (relevance/factual accuracy/consistency/fluency metrics, Bedrock Model Evaluations, A/B + canary, user feedback/rating, regression testing + quality gates, RAG evaluation + LLM-as-a-judge, retrieval quality testing, Bedrock Agent evaluations, deployment validation with synthetic workflows).
- Task 5.2: Troubleshoot GenAI applications (context window overflow + dynamic chunking, FM integration/API errors, prompt testing frameworks + version comparison, retrieval/embedding/drift diagnostics, prompt maintenance via CloudWatch Logs + X-Ray + schema validation).

---

## In-Scope AWS Services (verified, non-exhaustive)

Machine Learning (the core cluster):
Amazon Augmented AI, Amazon Bedrock, Amazon Bedrock AgentCore, Amazon Bedrock Knowledge Bases, Amazon Bedrock Prompt Management, Amazon Bedrock Prompt Flows, Amazon Comprehend, Amazon Kendra, Amazon Lex, Amazon Q Business (+ Apps), Amazon Q Developer, Amazon Rekognition, Amazon SageMaker AI, SageMaker Clarify, SageMaker Data Wrangler, SageMaker Ground Truth, SageMaker JumpStart, SageMaker Model Monitor, SageMaker Model Registry, SageMaker Neo, SageMaker Processing, SageMaker Unified Studio, Amazon Textract, Amazon Titan, Amazon Transcribe.

Analytics: Athena, EMR, Glue, Kinesis, OpenSearch Service, QuickSight, MSK.

Application Integration: AppFlow, AppConfig, EventBridge, SNS, SQS, Step Functions.

Compute: App Runner, EC2, Lambda, Lambda@Edge, Outposts, Wavelength.

Containers: ECR, ECS, EKS, Fargate.

Customer Engagement: Amazon Connect.

Database: Aurora, DocumentDB, DynamoDB (+ Streams), ElastiCache, Neptune, RDS.

Developer Tools: Amplify, CDK, CLI, CloudFormation, CodeArtifact, CodeBuild, CodeDeploy, CodePipeline, AWS Tools and SDKs, X-Ray.

Management/Governance: Auto Scaling, Chatbot, CloudTrail, CloudWatch (+ Logs, Synthetics), Cost Anomaly Detection, Cost Explorer, Managed Grafana, Service Catalog, Systems Manager, Well-Architected Tool.

Migration/Transfer: DataSync, Transfer Family.

Networking/Content Delivery: API Gateway, AppSync, CloudFront, ELB, Global Accelerator, PrivateLink, Route 53, VPC.

Security/Identity/Compliance: Cognito, Encryption SDK, IAM, IAM Access Analyzer, IAM Identity Center, KMS, Macie, Secrets Manager, WAF.

Storage: EBS, EFS, S3 (+ Intelligent-Tiering, Lifecycle policies, Cross-Region Replication).
