# AIP-C01 Practice Exam 1 — Questions

65 scored questions, domain-weighted (D1 20, D2 17, D3 13, D4 8, D5 7). Multiple-response items are marked. Record answers on `AIP-C01-Mock-Exam-1_AnswerSheet.md`; correct answers and full analysis live in `analysis/`.

---

## Question 1

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A retail company is designing a new generative AI assistant. The product team has a business goal but disagrees on architecture: latency must stay under one second for a chat UI, the assistant must answer from a product catalog that changes several times per day, and leadership wants confidence that the design follows AWS best practices before a multi-quarter build commits budget. A lead engineer proposes immediately writing production integration code against a flagship reasoning model.

Following the Task 1.1 design discipline, which sequence of actions BEST addresses the team's situation before committing to a full build?

**A.** Fine-tune a flagship model nightly on the catalog, then build the production integration directly against it

**B.** Derive the architecture from the constraints, validate it with a proof-of-concept on Bedrock, and review the design against the Well-Architected Generative AI Lens

**C.** Purchase Provisioned Throughput for the flagship model first to guarantee the sub-second latency budget, then design the rest of the system around it

**D.** Skip the proof-of-concept because a design document already captures the latency, cost, and freshness requirements

---

## Question 2

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A SaaS company runs a customer-support assistant on Amazon Bedrock. Telemetry shows roughly 90 percent of queries are routine FAQ-style questions and about 10 percent are complex multi-step troubleshooting. Finance wants to cut foundation-model spend significantly without measurably degrading answer quality, and the team must be able to change which model serves each tier later without redeploying code.

Which combination of techniques BEST meets both the cost and the operational-flexibility requirements?

**A.** Route all traffic to the flagship model and rely on exponential backoff to control cost

**B.** Implement model cascading (cheap model first, escalate hard queries to a flagship model) and externalize the active model choice in AWS AppConfig behind a Lambda/API Gateway abstraction

**C.** Purchase six-month Provisioned Throughput for the flagship model to obtain volume discounts and serve all traffic from it

**D.** Switch all traffic to batch inference to capture the lower per-token price

---

## Question 3

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A bank fine-tuned an Amazon Bedrock model on labeled examples to enforce a strict house writing style that prompting could not reliably produce. The team now wants to serve this customized model in a production application that receives steady, high-volume traffic. A junior engineer wrote integration code that calls the model on-demand and is puzzled that invocations fail.

What is the root cause, and what is the correct production serving approach?

**A.** The model needs batch inference; reformat the requests as S3 input files

**B.** Customized (fine-tuned) Bedrock models cannot be invoked on-demand; they must be served through Provisioned Throughput, which also requires requesting a Model Unit quota increase before a committed purchase

**C.** The model must be re-imported as a base model so it qualifies for on-demand invocation

**D.** On-demand works for custom models, but the region lacks capacity; enable a cross-Region inference profile

---

## Question 4

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A European financial customer requires that all inference data remain within the EU for regulatory reasons. They still want resilience against single-Region capacity bursts so that throttling does not break their assistant. They are evaluating Bedrock inference profiles. An architect intermittently sees AccessDenied-style failures in CloudTrail during a pilot that used a profile spanning several Regions.

Which choice satisfies the data-residency requirement while still giving cross-Region resilience, and what is the most likely cause of the intermittent failures the architect saw?

**A.** Use a Global inference profile for maximum capacity; the failures are unrelated network errors

**B.** Use an EU geography-scoped inference profile; an SCP or IAM policy was blocking Bedrock inference in one of the profile's destination Regions

**C.** Use single-Region on-demand only; cross-Region inference is incompatible with any residency requirement

**D.** Use an application inference profile in any Region; the failures were caused by exceeding the Model Unit quota

---

## Question 5

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A data engineering team is building the ingestion pipeline that feeds a RAG knowledge base. The corpus is a mix of recorded support phone calls, scanned PDF invoices with tables, and a large structured customer dataset in a data lake that must meet completeness and uniqueness rules before anything is embedded. The team wants each data type routed to the correct AWS service.

Which mapping of data type to processing service is correct for this pipeline? (Select THREE)

**A.** Recorded support calls (audio) → Amazon Transcribe to produce searchable text

**B.** Scanned PDF invoices with tables → Amazon Textract to extract text, forms, and tables

**C.** Large structured data-lake dataset → AWS Glue Data Quality to enforce completeness and uniqueness rules at scale

**D.** Recorded support calls (audio) → Amazon Comprehend to convert speech to text

**E.** Scanned PDF invoices with tables → Amazon Rekognition to extract the table cells

**F.** Large structured data-lake dataset → Amazon Transcribe to validate the rules

---

## Question 6

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

An application sends prompts to a Bedrock model through an ingestion-and-inference pipeline. Intermittently it receives ValidationException errors. The on-call engineer added retry-with-exponential-backoff logic, but the same requests keep failing identically on every retry, wasting quota.

What is the actual root cause and the correct fix?

**A.** The model is throttled; increase the backoff window and add jitter so the retries eventually succeed

**B.** ValidationException is a non-retryable client error from malformed input; fix the pipeline's input-formatting step so requests conform to the expected Bedrock JSON/content-block structure

**C.** The account hit its Model Unit quota; request a quota increase through AWS Support

**D.** The cross-Region inference profile has a blocked destination Region; update the SCP to allow it

---

## Question 7

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A team is selecting an embedding model and a vector store together for a new RAG system. To cut vector-storage cost aggressively, they want to use Amazon Titan Text Embeddings V2 binary vectors, accepting some precision loss. They had planned to store the vectors in Amazon Aurora PostgreSQL with pgvector because the team already runs Aurora.

What is the problem with this plan, and what are the valid ways to resolve it? (Select TWO)

**A.** Switch the vector store to Amazon OpenSearch Serverless (or OpenSearch Managed), the only stores that support binary vectors

**B.** Keep Aurora pgvector but store float32 vectors instead, for example a lower Titan V2 dimension such as 256 to cut storage with minimal accuracy loss

**C.** Keep Aurora and binary vectors; pgvector supports binary embeddings once the extension is upgraded

**D.** Use Amazon S3 Vectors, which is the lowest-cost store and therefore supports binary vectors

**E.** Convert the binary vectors to float32 at query time so Aurora can compare them with the binary index

---

## Question 8

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A legal-tech firm needs RAG over millions of contracts and clauses. The most valuable queries are multi-hop questions that follow relationships between connected documents (how a clause in one contract is affected by clauses in related contracts), and the firm wants more explainable, lower-hallucination answers. Their source documents live in Amazon S3.

Which vector store best fits these requirements?

**A.** Amazon S3 Vectors, because it is the lowest-cost store for millions of vectors

**B.** Amazon OpenSearch Serverless, because it gives millisecond latency at billions of vectors

**C.** Amazon Neptune Analytics (GraphRAG), because it combines vector similarity with graph traversal for multi-hop reasoning over related documents

**D.** Amazon Aurora PostgreSQL with pgvector, because it stores vectors alongside relational data

---

## Question 9

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A company built a cost-optimized RAG system on Amazon S3 Vectors. Two new requirements have surfaced: (1) a customer-facing interactive chat feature with strict millisecond latency, and (2) metadata filter expressions that use the startsWith operator on a document-prefix attribute. The team reports that the startsWith filters fail and latency is too high for the new chat.

Which statement most accurately diagnoses BOTH problems and the correct fix?

**A.** Both issues are bugs; reindex the S3 Vectors store and the filters and latency will be fixed

**B.** S3 Vectors delivers sub-second (not millisecond) latency and startsWith is unsupported on managed knowledge bases; moving to a custom knowledge base with a bring-your-own OpenSearch Serverless store addresses both the latency and the string-operator requirement

**C.** Switch from S3 Vectors to the quick-create managed OpenSearch Serverless index; that alone restores both millisecond latency and startsWith filtering

**D.** Raise numberOfResults and enable hybrid search on S3 Vectors to lower latency and re-enable startsWith

---

## Question 10

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A team ingests well-structured product manuals (chapters, sections, subsections) into a Bedrock knowledge base. They want precise matches but also enough surrounding context in each answer so users are not handed a fragment. They are also debating whether they can switch the chunking approach later if relevance is poor, since they tend to iterate.

Which statement correctly pairs the best chunking strategy with the change-management reality?

**A.** Use FIXED_SIZE with no overlap because manuals are uniform; the chunking strategy can be edited in place later if relevance is poor

**B.** Use HIERARCHICAL chunking so child chunks match precisely while parent chunks supply context; the chunking strategy is fixed at data-source creation and cannot be changed in place — switching requires a new data source and re-ingestion

**C.** Use SEMANTIC chunking because it is always cheapest; you can toggle to HIERARCHICAL later without re-ingesting

**D.** Use NONE so each manual is one chunk for maximum context; chunking can be reconfigured anytime via UpdateDataSource

---

## Question 11

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A support chatbot on a Bedrock knowledge base backed by Amazon OpenSearch Serverless answers conceptual questions well but keeps missing answers when users paste exact error codes such as ThrottlingException or specific product SKUs. An engineer set overrideSearchType to HYBRID on a different knowledge base backed by S3 Vectors and reports it made no difference there.

Which explanation and remediation are correct?

**A.** On OpenSearch Serverless, set overrideSearchType to HYBRID to add keyword matching for exact tokens; on the S3 Vectors KB, HYBRID is unsupported and silently falls back to semantic search, so a hybrid-capable store is required for that behavior

**B.** Increase numberOfResults to 50 on both knowledge bases; exact-token misses are caused by too few results

**C.** Set overrideSearchType to SEMANTIC on the OpenSearch KB to force vector-only matching of the error codes

**D.** Switch the embedding model to a higher dimension on both; larger vectors capture exact strings

---

## Question 12

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A RAG team operating in the us-east-1 (N. Virginia) Region observes that the genuinely best chunk is often retrieved but ranked too low to make it into the top few chunks sent to the model, so answers miss it. They want to add a second relevance pass to reorder candidates before generation and must choose a reranker model that is actually available in their Region.

Which technique and reranker model should they use?

**A.** Query decomposition with Amazon Rerank 1.0

**B.** Reranking with Amazon Rerank 1.0, which is the default reranker in every Region

**C.** Reranking with Cohere Rerank 3.5, because Amazon Rerank 1.0 is not available in us-east-1

**D.** Increase numberOfResults so the best chunk is included even at a low rank; no reranker is needed

---

## Question 13

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

Users frequently ask multi-part comparison questions of a Bedrock knowledge base, such as 'Did the Phoenix or Denver region have higher Q3 revenue, and which grew faster?' A single flat semantic retrieval returns chunks for one region or the other but never enough to compare both at once, so answers are incomplete.

Which managed retrieval capability addresses this, and how is it enabled?

**A.** Metadata filtering on a region attribute, configured in the vectorSearchConfiguration

**B.** Query decomposition, enabled by setting orchestrationConfiguration.queryTransformationConfiguration.type to QUERY_DECOMPOSITION on a RetrieveAndGenerate request

**C.** Hybrid search, enabled by setting overrideSearchType to HYBRID on a Retrieve request

**D.** Reranking, enabled via the standalone Rerank API on the bedrock-agent-runtime endpoint

---

## Question 14

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A multi-tenant assistant on a Bedrock knowledge base has two problems: a retrieval is returning chunks belonging to other tenants (an access-control leak), and a separate query surfaced a 2021 policy when the user clearly asked about the 2024 policy (a relevance problem). The documents come from an Amazon S3 data source.

Which single knowledge base capability addresses BOTH problems, and how is the metadata supplied?

**A.** Amazon Bedrock Guardrails, which scrub the retrieved chunks so other tenants' content and outdated policies are removed

**B.** Metadata filtering at query time on attributes such as tenant ID and year, with metadata supplied via per-file .metadata.json sidecar files (each ≤ 10 KB) for the S3 source

**C.** Reranking, which reorders results so only the current tenant's 2024 chunks reach the top

**D.** Increasing numberOfResults so the correct tenant and year chunks are guaranteed to be included

---

## Question 15

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A pricing chatbot built on a Bedrock knowledge base keeps returning confident, well-cited answers that quote last year's prices, even though the source documents in S3 were updated weeks ago. The retrieval and generation pipeline shows no errors and the citations look authoritative. Going forward the business will tolerate a fixed nightly refresh cadence.

What is the root cause, and which refresh architecture is the simplest fit for the stated cadence?

**A.** A Guardrail is filtering out the new prices; disable the guardrail and the current prices will appear

**B.** Stale retrieval — the index was never re-synced after the S3 documents changed; run StartIngestionJob (incremental) and automate it with EventBridge Scheduler invoking a Lambda that calls StartIngestionJob

**C.** The embedding dimension is too small; re-embed the corpus at a higher dimension to capture the new prices

**D.** numberOfResults is too low; raise it so the new price chunks are returned

---

## Question 16

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

An operations team wants every change to their S3-backed knowledge base reflected within a few minutes, and they expect bursts of hundreds of file changes during deployments. A junior engineer proposes wiring each S3 event directly to a Lambda that immediately calls StartIngestionJob per event. In load testing the design fails badly under bursts.

Why does the naive design fail, and what is the documented event-driven architecture?

**A.** It fails because Lambda concurrency is too low; raise the reserved concurrency and call StartIngestionJob on every event

**B.** It fails because Bedrock ingestion quotas are tight and per-Region (about 5 concurrent jobs per account, 1 per KB, 1 per data source, with StartIngestionJob limited to roughly 0.1 RPS); the documented pattern buffers events in SQS and uses a Step Functions state machine to check quota and call StartIngestionJob, waiting and rechecking when capacity is unavailable

**C.** It fails because S3 event notifications cannot trigger EventBridge; use S3 Lifecycle policies to trigger the sync instead

**D.** It fails because StartIngestionJob is synchronous; switch to IngestKnowledgeBaseDocuments for every changed file and skip buffering entirely

---

## Question 17

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A company wants a knowledge base that answers plain-English questions over a sales database in Amazon Redshift. A teammate insists the first steps are to pick an embedding model, tune numberOfResults, and enable hybrid search, just as they did for their document-based knowledge base.

What is wrong with the teammate's plan, and what is the correct configuration path?

**A.** Nothing is wrong; structured stores use the same embedding and vectorSearchConfiguration knobs as document stores

**B.** A structured store uses no embeddings — Bedrock generates SQL from the question (GenerateQuery) and runs it on Redshift; numberOfResults, search type, and metadata filtering do not apply. Configure the query engine (Redshift Provisioned or Serverless), the storage config, and optionally query generation (table/column descriptions, curated NL-to-SQL examples)

**C.** Structured stores require binary vectors, so they must use OpenSearch Serverless rather than Redshift

**D.** Structured stores require hierarchical chunking of the database rows before querying

---

## Question 18

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A platform team manages prompts in Amazon Bedrock Prompt Management. They deployed a customer-summary prompt as version 5 and discovered it produces noticeably lower-quality summaries than version 4. No one can edit version 5, leadership wants the fastest restoration of quality with no new prompt authoring, and a separate developer is failing to invoke a Prompt Management prompt configured for an Amazon Titan model using the InvokeModel API.

Which two statements correctly resolve these issues? (Select TWO)

**A.** Update the application's prompt reference ARN from version 5 to version 4 to roll back immediately, since versions are immutable snapshots

**B.** Invoke the Titan-configured managed prompt with the Converse API; InvokeModel supports only Claude/Llama managed prompts

**C.** Delete version 5 and recreate version 4 to restore quality, since deletion is the only rollback path

**D.** Edit version 5 in place to match version 4, because the working draft and numbered versions are both mutable

**E.** Add system and inferenceConfig overrides in the InvokeModel request to force the Titan prompt to run

---

## Question 19

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A regulated financial-services organization must prove, for any model output that caused a problem, which prompt version produced it, who approved that prompt, and what the full prompt and response looked like. They use Amazon Bedrock Prompt Management with versioned templates and want an end-to-end audit chain. Their security team also wants to control who can create prompt versions.

Which combination establishes the required governance and audit chain? (Select THREE)

**A.** Use immutable numbered prompt versions (CreatePromptVersion) so each production output traces to an exact, frozen prompt configuration

**B.** Rely on CloudTrail management events (logged by default) to record who called CreatePrompt/CreatePromptVersion and when, and enable RenderPrompt data events to tie a specific prompt version to each invocation

**C.** Enable Bedrock Model Invocation Logging (off by default) to capture the full rendered prompt and model response for each invocation

**D.** Rely on Bedrock Guardrails to record which prompt version produced each output, since guardrails log the prompt lineage

**E.** Store all prompts as string literals in Lambda code and use Git history as the production audit trail

**F.** Use prompt variants as the immutable production artifacts, since variants persist for long-term audit

---

## Question 20

Category: Domain 1: Foundation Model Integration, Data Management, and Compliance

A pipeline prompts a Bedrock model for JSON used by a downstream API. Roughly one call in twenty returns a trailing comma or a wrapping sentence, breaking the parser and forcing a retry. The team also has a business rule that a returned rating field must be an integer between 1 and 5, and they must prevent toxic or PII content from leaving the system. A teammate suggests using a Bedrock Guardrail to guarantee valid JSON.

Which layered approach correctly meets all three needs (well-formed JSON, the 1–5 rating rule, and safety)?

**A.** Use a Bedrock Guardrail to enforce valid JSON and the 1–5 range, and add a longer system prompt for safety

**B.** Use Structured outputs (a JSON Schema output format or strict tool use) to enforce structure, add application-side validation for the 1–5 range that the schema subset cannot express, and use Bedrock Guardrails for toxicity/PII safety

**C.** Raise temperature and add more few-shot examples so the JSON is always valid and within range, and rely on the parser to catch unsafe content

**D.** Use application-side validation alone to enforce structure, range, and safety, since code can check everything deterministically

---

## Question 21

Category: Domain 2: Implementation and Integration

A logistics company is building a customer-service handler. For each inbound message it must look up the order in DynamoDB, then conditionally call a carrier shipping API, and only if the package is confirmed delayed, invoke a billing API to issue a refund credit, and finally reply. The exact sequence of calls and whether the refund step runs depend entirely on what each prior lookup returns. The team wants the fastest path to production and the least orchestration code to own.

Which implementation best fits this requirement?

**A.** A self-managed Converse client-side tool-use loop, where the application detects each tool_use stop reason, executes the call, and re-invokes

**B.** An Amazon Bedrock Agent with action groups for the order, shipping, and billing operations

**C.** A fixed AWS Step Functions Standard workflow that always invokes the order, shipping, and billing tasks in sequence

**D.** A single prompt that instructs the model to describe the steps a downstream system should take

---

## Question 22 (Select TWO)

Category: Domain 2: Implementation and Integration

An MCP server fronts an internal database for an autonomous agent. To move fast, the platform team gave the server's IAM role broad permissions and configured the server to reuse the bearer token that authenticated the end user to the agent. A user who holds administrator privileges asked the agent to clone a production database into pre-production; the model also hallucinated an extra 'clean up the old database' step, and the destructive DELETE succeeded.

Which TWO changes would have contained the blast radius of the model's mistake? (Select TWO)

**A.** Have the MCP server use an explicitly scoped, purpose-generated downstream token carrying only READ and CREATE for this task

**B.** Propagate the user's administrator token unchanged but log every downstream call to CloudTrail for after-the-fact review

**C.** Attach a Bedrock Guardrail with a denied topic for the word 'delete'

**D.** Apply least-privilege IAM to the tool's role and scope permissions to the acceptable scope of impact rather than to intended functionality

**E.** Increase the agent's maximum-iterations limit so it has more chances to self-correct

---

## Question 23

Category: Domain 2: Implementation and Integration

A team exposes an internal 'currency conversion' tool to its agents as a remote MCP server. Each call returns in a few hundred milliseconds, holds no session state between calls, and traffic is spiky: quiet for hours, then hundreds of requests in a burst. The team wants the lowest operational overhead and to avoid paying for idle capacity.

Which compute option should host this MCP server?

**A.** Amazon ECS on AWS Fargate running the server as a long-lived containerized service

**B.** AWS Lambda

**C.** An always-on Amazon EC2 instance behind an Application Load Balancer

**D.** A local stdio subprocess installed on each user's machine

---

## Question 24

Category: Domain 2: Implementation and Integration

A research workflow built with the Strands Agents SDK must coordinate several specialist agents (researcher, architect, coder, reviewer) where the handoff path is not fixed in advance and agents self-organize, passing work to whichever peer is best suited as new findings emerge. A separate billing workflow is a fixed, repeatable ETL-style sequence whose dependency graph never changes and whose independent steps can run in parallel.

Which Strands multi-agent primitives correctly match the two workflows?

**A.** Swarm for the research workflow; Workflow for the billing workflow

**B.** Workflow for the research workflow; Swarm for the billing workflow

**C.** Graph for the research workflow; Agents-as-Tools for the billing workflow

**D.** Agents-as-Tools for the research workflow; Graph for the billing workflow

---

## Question 25

Category: Domain 2: Implementation and Integration

A bank fine-tuned an Amazon Bedrock foundation model on its labeled credit-policy data to enforce a consistent specialized response format that prompting alone could not reliably produce. It now needs to serve this customized model in a steady, high-volume production application and is deciding how to provision inference capacity.

How must the bank serve the fine-tuned model?

**A.** On-demand inference, paying per token with no commitment

**B.** Batch inference with JSONL input and output in Amazon S3

**C.** Provisioned Throughput, purchasing Model Units for the customized model

**D.** A Global cross-Region inference profile for maximum throughput

---

## Question 26

Category: Domain 2: Implementation and Integration

A high-volume support classifier sees mostly routine tickets with a small fraction of genuinely ambiguous, complex cases. Leadership wants to cut model spend substantially while keeping answer quality essentially unchanged, and the team can add a confidence check on each response.

Which design best meets the cost and quality goals?

**A.** Route every request to the largest flagship model and enable Provisioned Throughput to reduce per-token cost

**B.** Send every request first to a small, fast, inexpensive model and escalate only low-confidence cases to a larger model (model cascading)

**C.** Enable a Global cross-Region inference profile so requests route to the cheapest available Region

**D.** Fine-tune the flagship model so it answers all cases more cheaply

---

## Question 27 (Select TWO)

Category: Domain 2: Implementation and Integration

A claims-processing application orchestrates two foundation-model calls with a mandatory human approval gate in between: the model drafts a settlement letter, an adjuster must approve or reject it, and only then does a second model finalize the document. The team initially built this as a single Lambda and a chain of AWS Step Functions Express workflows. They want durable, auditable, retryable control flow and a reliable pause for the human decision.

Which TWO changes produce a correct, auditable design? (Select TWO)

**A.** Implement the orchestration in AWS Step Functions using its optimized Amazon Bedrock integration instead of one long-running Lambda

**B.** Use a Step Functions Standard workflow with a Wait for Callback (task token) state for the human approval gate

**C.** Keep the Express workflow and add a Wait for Callback state for the approval gate

**D.** Replace the human gate with a fixed 5-minute Lambda timer that auto-approves

**E.** Raise the single Lambda's timeout to 15 minutes so it can wait for the adjuster inside one invocation

---

## Question 28

Category: Domain 2: Implementation and Integration

A central platform team runs an LLM gateway: Amazon Cognito authenticates each user, then the gateway's Lambda calls Amazon Bedrock using a single IAM role attached to the Lambda. Finance reports that all Bedrock spend appears under that one role, so they cannot attribute cost to individual business units. The team already turned on Cost Explorer and CloudTrail and still sees only the one identity.

What is the correct fix for per-business-unit cost attribution?

**A.** Enable AWS Cost Explorer granular grouping and re-run the report

**B.** Have the gateway call sts:AssumeRole per user against a Bedrock-scoped role, passing the user/tenant as the role-session-name and the business unit as session tags

**C.** Switch the gateway from REST API Gateway to an HTTP API to expose the caller identity

**D.** Move every business unit into its own AWS account before any further work

---

## Question 29

Category: Domain 2: Implementation and Integration

A platform team wants a partner in a separate AWS account to query a specific Amazon Bedrock Knowledge Base. By analogy to how they share an Amazon S3 bucket, they plan to attach a resource-based policy to the Knowledge Base granting the partner account access.

Will this approach work, and what is the correct mechanism?

**A.** Yes, attach a resource-based policy to the Knowledge Base just as you would an S3 bucket policy

**B.** No, Bedrock does not support resource-based policies on GenAI resources; cross-account access uses an assumed role in the owning account plus identity-based policies and SCPs

**C.** Yes, but the resource policy works only for the Retrieve action and not RetrieveAndGenerate

**D.** No, cross-account sharing requires migrating the Knowledge Base into the partner account

---

## Question 30

Category: Domain 2: Implementation and Integration

A gaming company wants ultra-low latency to 5G mobile users for a generative-AI feature and proposes 'running the Amazon Bedrock model at the edge inside an AWS Wavelength Zone.' Compliance has no data-residency constraint; the only goal is minimal latency to mobile devices.

What is the correct architecture?

**A.** Deploy the Amazon Bedrock inference data plane into the Wavelength Zone

**B.** Place the application/inference-orchestration tier in the Wavelength Zone and let the Bedrock model call go to the parent Region

**C.** Use AWS Local Zones instead, because they support VPC interface endpoints directly to Bedrock

**D.** Self-host the model on AWS Outposts inside the carrier facility

---

## Question 31 (Select TWO)

Category: Domain 2: Implementation and Integration

A regulated EU bank states two requirements for a Bedrock workload: (1) in-scope personal data must be stored and processed only within the EU, and (2) only EU-resident personnel may operate the underlying infrastructure. The team is choosing among standard EU Regions, inference-routing scopes, and AWS partitions.

Which TWO statements correctly address these requirements? (Select TWO)

**A.** A standard EU Region with In-Region (or EU-geographic) inference satisfies the data storage-and-processing requirement

**B.** The AWS European Sovereign Cloud satisfies the EU-resident-personnel operator-access requirement

**C.** EU geographic cross-Region inference by itself satisfies the operator-access requirement

**D.** A Global cross-Region inference profile satisfies the data-residency requirement

**E.** AWS Outposts is required because Amazon Bedrock cannot run in any EU Region

---

## Question 32

Category: Domain 2: Implementation and Integration

A marketing app lets users generate two-minute videos with Amazon Nova Reel. An engineer built an Amazon API Gateway REST endpoint backed by a Lambda that calls the model synchronously and returns the finished video in the response. The endpoint times out, and raising the Lambda timeout to 15 minutes does not help.

What is the underlying problem and the correct approach?

**A.** Lambda needs more memory; increase it and the synchronous call will complete

**B.** Nova Reel video generation is asynchronous-only via StartAsyncInvoke writing to S3, and a synchronous call would also exceed the API Gateway integration timeout regardless of the Lambda limit

**C.** The video must be returned as base64 in the response body to avoid the timeout

**D.** Switch to CreateModelInvocationJob batch inference to render the single video

---

## Question 33

Category: Domain 2: Implementation and Integration

During a marketing push, many users simultaneously hit a Bedrock-backed feature and the application begins returning ThrottlingException errors. An engineer proposes raising the Lambda reserved concurrency so more requests can run at once.

What is the correct architectural fix for the throttling?

**A.** Raise Lambda reserved concurrency so the workers can absorb the burst

**B.** Buffer bursty requests with an Amazon SQS queue in front of a Lambda worker to smooth concurrency against Bedrock quotas, with exponential backoff and jitter on retries

**C.** Move the workload to a synchronous API Gateway endpoint with a longer integration timeout

**D.** Disable retries so failed requests do not add to the load

---

## Question 34

Category: Domain 2: Implementation and Integration

An agent's foundation model is its single reasoning core. The team wants built-in redundancy so that if the primary Region's model endpoint has trouble or the workload bursts, requests are automatically served from another Region, without writing client-side load-balancing code. They enable a system-defined cross-Region inference profile and reference it as the modelId, but invocations now intermittently fail with AccessDenied.

What is the most likely cause of the intermittent AccessDenied?

**A.** An AWS Organizations SCP (or IAM policy) allows the Bedrock invoke actions only in the source Region and blocks one of the profile's destination Regions

**B.** Cross-Region inference profiles cannot be used as a modelId in the Converse API

**C.** The profile adds a per-request routing surcharge that the account budget rejects

**D.** Cross-Region inference requires Provisioned Throughput, which the team has not purchased

---

## Question 35

Category: Domain 2: Implementation and Integration

A team is building a token-streaming chatbot. The primary requirement is to authenticate users with an Amazon Cognito User Pool while writing the least possible custom authentication code; the chat is a standard server-to-client token stream.

Which front-end streaming pattern best fits?

**A.** A Lambda function URL with response streaming

**B.** An Amazon API Gateway WebSocket API

**C.** AWS AppSync GraphQL subscriptions

**D.** A synchronous REST API Gateway endpoint returning a buffered response

---

## Question 36 (Select TWO)

Category: Domain 2: Implementation and Integration

An ingestion pipeline must extract structured data from scanned PDF contracts, call-recording audio, and product videos. The team currently stitches together Amazon Textract, Amazon Transcribe, and Amazon Rekognition with custom glue plus a summarization model, and wants to simplify to a single managed multimodal service.

Which TWO statements are correct about using Amazon Bedrock Data Automation (BDA) here? (Select TWO)

**A.** Use InvokeDataAutomationAsync, because it handles documents, audio, and video and supports EventBridge completion notifications

**B.** Use the synchronous InvokeDataAutomation API for the video and audio files

**C.** BDA provides one unified multimodal API that can replace the hand-built Textract + Transcribe + Rekognition pipeline

**D.** BDA cannot detect or redact PII, so a separate Comprehend step is still required for every modality

**E.** Each modality must be sent to a different AWS AI service and cannot be processed through one API

---

## Question 37

Category: Domain 2: Implementation and Integration

A team deployed an Amazon Bedrock Agent behind an alias that their application invokes. They edited the agent's action group through the console and deployed, but the agent's behavior did not change. Separately, after fixing the issue they ship a new version that misbehaves and need to revert immediately and pause the agent during investigation, all without changing application code or IAM.

Which sequence correctly resolves both the no-effect change and the rollback/pause?

**A.** Restart the action-group Lambda, then delete and recreate the alias to roll back

**B.** Call PrepareAgent to rebuild the DRAFT, cut a new version, and repoint the alias; to revert, repoint the alias to the prior version and set the alias to REJECT_INVOCATIONS to pause

**C.** Increase the agent's memory size to apply the config change, then lower the Lambda timeout to pause it

**D.** Edit the live numbered version in place so the alias automatically picks up both the change and the rollback

---

## Question 38

Category: Domain 3: AI Safety, Security, and Governance

A RAG-based legal-research assistant on Amazon Bedrock uses a Knowledge Base over a corpus of contracts stored in S3. The team has enabled a Bedrock guardrail with the sensitive information filter (MASK) and contextual grounding checks, attached to RetrieveAndGenerate. In production, the assistant still returns citations that expose client names and account numbers, and on one occasion it acted on an instruction that turned out to be hidden inside a contract PDF that had been ingested months earlier.

Which change most directly addresses BOTH the PII-in-citations leak and the instruction that was buried in a source document?

**A.** Increase the contextual grounding threshold toward 0.99 and raise the content-filter Prompt Attack strength to HIGH so the guardrail blocks both issues at the model boundary

**B.** Redact PII from the source corpus before ingestion with an Amazon Comprehend redaction job, and screen the retrieved chunks in the pipeline with ApplyGuardrail before they are concatenated into the prompt

**C.** Switch the guardrail from MASK to BLOCK on the sensitive information filter so any response containing PII is rejected entirely

**D.** Move the guardrail enforcement to the InvokeModel call instead of RetrieveAndGenerate so it can inspect the retrieved context

**E.** Enable Model Invocation Logging so the leaked PII and injected instructions are captured for later review

---

## Question 39

Category: Domain 3: AI Safety, Security, and Governance

A content-moderation pipeline must run an Amazon Comprehend toxicity score on each user message, then apply an organization-specific business rule in a Lambda function, then invoke a Bedrock model, and finally escalate any response that the business rule flags to a human reviewer who must approve it before it is released. Volume is moderate and some reviews can take hours.

Which design satisfies all of these requirements?

**A.** A single Amazon Bedrock guardrail with all six policy types enabled, attached to the InvokeModel call

**B.** An AWS Step Functions Standard workflow that sequences the Comprehend, Lambda, and Bedrock steps and uses a human-approval (task token) step to pause until the reviewer responds

**C.** An AWS Step Functions Express workflow chaining the Comprehend, Lambda, and Bedrock steps with a Choice state that routes flagged content to a human reviewer

**D.** Two sequential ApplyGuardrail calls, one before and one after the model invocation, with Amazon SNS notifying the reviewer

---

## Question 40

Category: Domain 3: AI Safety, Security, and Governance

A retail bank deploys a customer assistant. Compliance set a content filter to LOW strength for the Violence and Insults categories expecting strong protection, but a significant amount of borderline abusive content still reaches customers. Separately, they need the assistant to refuse to give any specific investment recommendations, and to keep a named competitor brand out of all responses.

Which combination of configuration changes correctly addresses all three concerns?

**A.** Raise the content-filter strength to HIGH for Violence and Insults; use a denied topic for investment recommendations; use a word filter custom list for the competitor brand name

**B.** Lower the content-filter strength further to NONE for tighter control; use a word filter for investment advice; use a denied topic for the competitor brand name

**C.** Raise the content-filter strength to HIGH; use a word filter for investment recommendations; use a denied topic for the competitor brand name

**D.** Keep LOW strength; use the sensitive information filter to mask the competitor name; use contextual grounding to block investment advice

---

## Question 41 (Select TWO)

Category: Domain 3: AI Safety, Security, and Governance

A healthcare summarization service on Bedrock must (1) reduce hallucinations by ensuring summaries are supported by the supplied clinical note, and (2) return a strictly parseable JSON object with fixed fields so a downstream EHR system can ingest it without custom parsing. The team is using Anthropic Claude through the Converse API.

Which TWO controls together best meet both requirements? (Select TWO)

**A.** Enable Bedrock Guardrails contextual grounding checks with a grounding threshold to block summaries not supported by the clinical note

**B.** Use Bedrock structured outputs (JSON Schema output format via outputConfig.textFormat) to constrain the response to the required shape

**C.** Enable citations on the Claude call together with the JSON Schema output format so the EHR system gets both provenance and structure

**D.** Set the content-filter Prompt Attack strength to HIGH to prevent the model from fabricating clinical facts

**E.** Use a denied topic named Hallucination to block any response that introduces unsupported information

---

## Question 42

Category: Domain 3: AI Safety, Security, and Governance

A security team needs to determine, before any data is ingested into a vector store, which of several hundred S3 buckets contain credit card numbers, private keys, or other PII. They want continuous, low-cost coverage across the whole estate plus the option to run a deeper scan on a few specific buckets.

Which service and approach should they use?

**A.** Amazon Comprehend DetectPiiEntities run against each object to return entity types and offsets

**B.** Amazon Macie — automated sensitive data discovery for continuous estate-wide sampling, plus targeted discovery jobs for the specific buckets

**C.** An Amazon Bedrock guardrail with the sensitive information filter applied to each bucket

**D.** AWS KMS customer-managed keys with key-usage auditing through CloudTrail

---

## Question 43

Category: Domain 3: AI Safety, Security, and Governance

A bank fine-tunes a Bedrock model on years of historical customer-support transcripts. A reviewer objects, citing PII risk. The project lead replies: "Bedrock does not train its base foundation models on our data, our data is not shared with the model provider, and customization produces a private copy — so the PII in the transcripts is safe."

Why is the project lead's reasoning flawed, and what is the correct mitigation?

**A.** It is not flawed; the base-model and private-copy guarantees fully cover the fine-tuning data

**B.** A fine-tuned model can memorize and later replay its training data, so PII can resurface in outputs; redact the PII (Comprehend) and discover it (Macie) before it enters the training set

**C.** Bedrock shares fine-tuning data with the model provider, so the data must be encrypted in transit before the job

**D.** Fine-tuning data is retained by Bedrock after the job, so an S3 Lifecycle policy must delete it

---

## Question 44

Category: Domain 3: AI Safety, Security, and Governance

A healthcare company serving EU patients must guarantee that Bedrock inference data does not leave the European Union, must be able to rotate and audit the key protecting its Knowledge Base, and must automatically delete stored conversation transcripts after 90 days.

Which set of controls satisfies all three requirements?

**A.** A global cross-Region inference profile; an AWS owned key on the Knowledge Base; an S3 Cross-Region Replication rule for the transcripts

**B.** A geographic (EU) cross-Region inference profile enforced with an aws:RequestedRegion SCP; a customer-managed KMS key on the Knowledge Base; an S3 Lifecycle expiration policy on the transcript bucket

**C.** A geographic (EU) cross-Region inference profile; an AWS owned key on the Knowledge Base; an S3 Lifecycle policy that transitions transcripts to Glacier after 90 days

**D.** AWS PrivateLink endpoints in every EU Region; an AWS owned key; manual deletion of transcripts every quarter

---

## Question 45 (Select TWO)

Category: Domain 3: AI Safety, Security, and Governance

A platform team is hardening IAM for a Bedrock workload. The runtime application calls Anthropic Claude through the Converse API and must be restricted to Anthropic models only. A separate administrator role manages guardrail configuration and invocation logging. The team also enforces a mandatory guardrail on direct invocations using the bedrock:GuardrailIdentifier condition key (Allow on StringEquals plus Deny on StringNotEquals).

Which TWO statements are correct about this design? (Select TWO)

**A.** Granting the runtime role bedrock:InvokeModel scoped to arn:aws:bedrock:*::foundation-model/anthropic.* both authorizes Converse and limits it to Anthropic models

**B.** The runtime role must be granted a dedicated bedrock:Converse action in addition to bedrock:InvokeModel

**C.** The administrator role belongs in the control plane and should hold actions such as CreateGuardrail and PutModelInvocationLoggingConfiguration, not InvokeModel

**D.** The GuardrailIdentifier-enforcing role should also be used for RetrieveAndGenerate so the guardrail covers RAG calls

**E.** The foundation-model ARN must include the account ID to scope it to the team's account

---

## Question 46

Category: Domain 3: AI Safety, Security, and Governance

A Knowledge Base is being assembled with three connections: a Pinecone vector store, a Confluence data source, and an Amazon S3 data source. Security requires that no long-lived credentials be hardcoded anywhere.

For which of these connections is an AWS Secrets Manager secret required?

**A.** All three, because every external connection needs a stored credential

**B.** Pinecone and Confluence; the S3 data source is governed by IAM and needs no secret

**C.** Only the S3 data source, because S3 access keys must be stored as a secret

**D.** Only Pinecone, because vector stores require an API key but SaaS connectors use OAuth handled by Bedrock automatically

---

## Question 47

Category: Domain 3: AI Safety, Security, and Governance

A model-risk team must satisfy two distinct governance asks for the same financial-advisory model. First, they need AWS's own documented statement of an Amazon Nova model's intended uses and limitations. Second, they must produce their own internal governance document for a custom model they fine-tuned, recording its intended uses, a risk rating, and evaluation results, with an immutable change history for auditors.

Which artifacts correctly satisfy the two asks respectively?

**A.** Create an AWS AI Service Card for Nova; read a SageMaker Model Card AWS publishes for the custom model

**B.** Read the AWS AI Service Card AWS publishes for Nova; create a SageMaker Model Card for the custom model

**C.** Read a SageMaker Model Card for Nova; create an AWS AI Service Card for the custom model

**D.** Use Bedrock Guardrails documentation for Nova; use Bedrock Model Evaluation reports as the custom model's governance document

---

## Question 48

Category: Domain 3: AI Safety, Security, and Governance

A compliance team needs three things for a Bedrock chatbot: (1) review the exact text of past prompts and completions, (2) a tamper-detection alert when a user signing in from an unusual location deletes a guardrail or repoints the training-data S3 bucket, and (3) a real-time alarm when blocked/unsafe content spikes. They confirm CloudTrail is active but find no prompt text anywhere.

Which mapping of capabilities to the three needs is correct?

**A.** (1) Enable CloudTrail data events to capture prompt text; (2) CloudWatch alarm on InvocationsIntervened; (3) Model Invocation Logging

**B.** (1) Model Invocation Logging (off by default — enable it; only it captures prompt/response content); (2) CloudTrail management-event records analyzed by Amazon GuardDuty; (3) CloudWatch alarm on InvocationsIntervened

**C.** (1) CloudTrail Event history, which retains prompt bodies for 90 days; (2) AWS Config rules; (3) Model Invocation Logging metric filters

**D.** (1) CloudWatch Logs Insights query over invocation metrics; (2) Model Invocation Logging; (3) CloudTrail data events

---

## Question 49 (Select THREE)

Category: Domain 3: AI Safety, Security, and Governance

A data-governance lead must, for a RAG application, (a) maintain a queryable metadata store of the source corpus and dataset versions, (b) visualize how data flowed from source through transformations to the model output for compliance reporting, and (c) ensure customer PII never persists in application logs, given that blocked content can still appear as plaintext in Model Invocation Logs.

Which TWO statements correctly map services to these needs? (Select TWO)

**A.** The AWS Glue Data Catalog is the persistent metadata store for the corpus and datasets, with crawlers discovering schemas

**B.** The AWS Glue Data Catalog is also where lineage graphs are visualized for compliance reporting

**C.** Amazon DataZone or the SageMaker Catalog consumes Glue lineage and visualizes how data flowed from source to output

**D.** A Bedrock guardrail with the sensitive information filter guarantees PII never reaches application logs

**E.** Amazon Comprehend token-level redaction applied to log output before it propagates keeps PII out of the logs

---

## Question 50

Category: Domain 3: AI Safety, Security, and Governance

A model deemed fair at launch is suspected of becoming biased after months in production as live traffic diverges from the training distribution. Separately, a media customer needs to verify whether a circulating image was generated by Amazon Titan and wants a confidence level with the verdict.

Which two capabilities address these needs respectively?

**A.** SageMaker Clarify pre-training bias metrics for the drift concern; an Amazon Bedrock content filter to verify the image origin

**B.** SageMaker Model Monitor bias drift monitoring (Clarify, with CloudWatch alerts) for the drift concern; watermark detection via the DetectGeneratedContent API for the image

**C.** A one-time SageMaker Clarify post-training bias report for the drift concern; Amazon Macie to verify the image origin

**D.** Bedrock contextual grounding checks for the drift concern; Amazon Comprehend to verify the image origin

---

## Question 51

Category: Domain 4: Operational Efficiency and Optimization

A SaaS company runs a document-summarization feature on Amazon Bedrock using an Anthropic Claude model on the default on-demand path. Over three months the Bedrock bill has roughly tripled while request volume has only grown about 40%. Investigation shows the average summary length has crept up (the prompt now asks for an 'exhaustive, comprehensive' summary), and a 2,200-token static instruction block containing tone rules and worked examples is sent on every call. A platform engineer has filed a ticket recommending the team 'move the workload to a larger, GPU-backed instance type and enable compute autoscaling so summaries process faster and more cost-efficiently.'

Which response correctly evaluates the engineer's recommendation and identifies the most appropriate first actions?

**A.** The recommendation is sound; provision a GPU instance reservation to lock in a lower hourly compute rate and add Auto Scaling to handle the growth

**B.** The recommendation is a category error because on-demand Bedrock is serverless with no instance to scale; instead bound output length (concise instruction plus a maxTokens ceiling) and apply prompt caching to the repeated static instruction block

**C.** The recommendation is partially correct; keep the autoscaling plan but also raise the per-model requests-per-minute quota so more compute is allocated per request

**D.** The recommendation is correct in spirit but should target a smaller EC2 instance, since cost on Bedrock scales with the instance size you select for inference

---

## Question 52

Category: Domain 4: Operational Efficiency and Optimization

A retail company runs a customer-facing FAQ assistant on Amazon Bedrock. Analytics show roughly 70% of incoming questions are paraphrases of a small set of common questions ('how do I reset my password?' vs 'I forgot my password, what do I do?') whose answers are stable for weeks at a time. The remaining 30% are genuinely novel. The team wants to cut both inference cost and latency for the repeated questions, and is willing to build supporting infrastructure on AWS data services.

Which approach best fits the repetition pattern, and what is the key risk to manage?

**A.** Amazon Bedrock prompt caching, because it returns a stored answer for similar questions without invoking the model; manage the cache-write cost on the first call

**B.** Semantic caching using a vector cache (for example, ElastiCache for Valkey vector search), because it matches questions by embedding similarity and returns a stored answer without invoking the model; manage the risk of serving a non-equivalent answer by setting a high similarity threshold and a TTL

**C.** Provisioned Throughput sized to the FAQ volume, because dedicated Model Units cache the common answers in committed capacity; manage the hourly commitment cost

**D.** Amazon Bedrock prompt caching, because the repeated questions form a static prefix that is reprocessed on each call; manage the per-model minimum token threshold

---

## Question 53

Category: Domain 4: Operational Efficiency and Optimization

A media archive company must run a Bedrock foundation model over a back catalog of 250,000 archived articles to generate one-paragraph summaries plus a category label. The results are needed by the end of the week, not in real time, and the goal is the lowest possible cost. An architect proposes building a Bedrock agent that calls an external taxonomy-lookup tool for each article and enforces a strict JSON schema on every response, then running the whole thing as a Bedrock batch inference job to capture the batch discount.

What is the correct assessment of this proposal?

**A.** Batch inference fits the volume and latency profile, but it processes each record independently and supports neither tool calling nor structured-output formatting, so the agent-with-tools-and-strict-JSON design is incompatible with batch

**B.** The proposal is correct as designed; batch inference supports tool calling and structured output as long as each record is submitted independently

**C.** Batch inference is the wrong billing mode entirely; this volume requires Provisioned Throughput because only dedicated Model Units can process 250,000 records

**D.** The proposal should use on-demand inference with high client-side concurrency, because batch inference is more expensive than on-demand for large jobs

---

## Question 54

Category: Domain 4: Operational Efficiency and Optimization

An interactive coding-assistant on Amazon Bedrock receives two distinct complaints in the same sprint. Team A (end users) reports: 'After I hit send, the screen is blank for four to five seconds before any text appears — it feels frozen.' Team B (data platform) runs a nightly job that classifies 40,000 log entries through the same model and reports: 'The job takes far too long to finish end-to-end and keeps failing with ThrottlingException partway through.' A junior engineer proposes a single fix for both: 'lower the temperature parameter and enable response streaming.'

Why does the single proposed fix fail to address both complaints, and what correctly addresses each?

**A.** Lowering temperature speeds up generation, so it fixes Team B; streaming fixes Team A — the proposal is correct for both

**B.** Streaming addresses Team A's perceived-latency (time-to-first-token) complaint, but neither streaming nor temperature helps Team B; Team B needs concurrency managed within the per-model RPM/TPM quotas with retries and backoff (and a committed-capacity option such as Provisioned Throughput or Cross-Region Inference for sustained volume)

**C.** Streaming fixes both, because incremental token delivery also reduces total batch completion time by parallelizing token production

**D.** Temperature fixes both, because a lower-temperature model produces shorter responses, which both speeds up the interactive screen and reduces the nightly job's total time

---

## Question 55

Category: Domain 4: Operational Efficiency and Optimization

A RAG-backed legal-research assistant on Amazon Bedrock with a Knowledge Base has two problems: time to first token is high (users wait several seconds before any text appears) and the per-call input-token cost is high. Investigation shows every query retrieves 50 chunks of about 2,000 characters each and injects all of them into the prompt. The model and prompt template have already been quality-validated and the team does not want to change the model. Answer correctness is currently acceptable and must not regress.

Which change most directly reduces both the high time-to-first-token and the high input-token cost?

**A.** Lower the temperature and top-p so the model samples fewer candidate tokens during prefill, shrinking the input cost

**B.** Enable response streaming so the first token appears sooner, which also lowers the input-token bill

**C.** Tune the retrieval configuration to return fewer, better-targeted chunks (reduce numberOfResults and add reranking), since a smaller retrieved context shortens the prefill phase and lowers input-token volume — while monitoring that answer quality does not drop

**D.** Increase maxTokens so the model can finish faster, reducing the decode phase that is driving time to first token

---

## Question 56

Category: Domain 4: Operational Efficiency and Optimization

A FinOps team operating a production Bedrock workload notes that the bulk of their monthly Bedrock spend is third-party Anthropic Claude usage, which appears on the invoice under the legal entity 'Anthropic, PBC.' They want an automated alert if those specific charges spike unexpectedly. Separately, they want to know which of three internal product teams sharing the same account is responsible for what share of the Bedrock spend. They have already enabled AWS Cost Anomaly Detection and assumed it covers everything.

Which combination correctly satisfies both requirements?

**A.** Rely on Cost Anomaly Detection for the Claude spike alert, and use Cost Explorer grouping by Region to attribute spend to the three teams

**B.** Use AWS Budgets with a filter on the third-party Billing entity to alert on the Claude charges (Cost Anomaly Detection excludes third-party Marketplace products), and use activated cost allocation tags viewed in Cost Explorer to attribute spend across the three teams

**C.** Use Cost Anomaly Detection for the Claude spike alert, and use SageMaker Model Monitor to attribute Bedrock spend across the three teams

**D.** Use a CloudWatch static-threshold alarm on the InputTokenCount metric for the Claude spike, and use Cost Explorer's default service grouping to attribute spend across the three teams

---

## Question 57 (Select TWO)

Category: Domain 4: Operational Efficiency and Optimization

A team is building the standing monitoring program for a production Bedrock assistant. They want CloudWatch alarms in the AWS/Bedrock namespace that reliably catch (1) capacity pressure from quota exhaustion and (2) token-spend growth on a workload whose token volume triples every weekday morning and falls to near zero overnight. A new engineer drafts a plan that includes alarming on 'the Bedrock error metric (which includes throttled requests)' and setting 'a single static threshold on the token-count sum.'

Which TWO statements correctly describe how to build these alarms? (Select TWO)

**A.** To catch capacity pressure you must alarm on the InvocationThrottles metric specifically, because a throttled request is counted as neither an Invocation nor an error and there is no single aggregate error metric in the AWS/Bedrock namespace

**B.** For a token-count metric with strong daily seasonality, use CloudWatch anomaly detection (a learned dynamic baseline that accounts for seasonality) rather than a single static threshold

**C.** A single InvocationServerErrors alarm will capture throttling, because throttles are classified as server-side 5xx errors in the AWS/Bedrock namespace

**D.** Use AWS Cost Anomaly Detection to alarm on the AWS/Bedrock token-count metric in near real time, since it watches CloudWatch operational metrics directly

**E.** A single static threshold is the correct tool for the seasonal token metric as long as you set it just above the overnight trough

---

## Question 58 (Select TWO)

Category: Domain 4: Operational Efficiency and Optimization

An engineering org reviews a production Bedrock workload that is too expensive. Telemetry shows: ~80% of traffic is simple intent-classification handled correctly by a small model in a quality test, while ~20% is complex multi-step reasoning the small model fails; a long static system prompt and a fixed tool-definition block are sent on every call; and overall traffic is spiky and unpredictable. The team must lower cost without dropping quality on the 20% of complex requests, and is asked to choose levers consistent with the Cost Lever Priority.

Which TWO actions are appropriate cost-optimization levers for this workload? (Select TWO)

**A.** Apply Bedrock prompt caching to the repeated static system prompt and tool-definition block so the repeated prefix is not reprocessed or re-billed at full rate

**B.** Route requests by difficulty — send the simple ~80% to the small model and escalate or route the complex ~20% to the larger model (model tiering or cascading), since the small model has been validated to clear the quality bar on the simple traffic

**C.** Purchase Provisioned Throughput sized to peak traffic, because dedicated Model Units are the cheapest option for any workload regardless of traffic shape

**D.** Switch all traffic, including the complex 20%, to the small model to maximize the per-token savings

**E.** Lower the temperature parameter on all requests to reduce the per-token cost of generation

---

## Question 59

Category: Domain 5: Testing, Validation, and Troubleshooting

A fintech team must choose between three foundation models for an open-ended customer-support assistant. Most support tickets have no single correct response, but legal requires an evidence-based, repeatable, defensible comparison before launch. The team also needs to score subjective qualities such as brand voice and empathy, which their automated metrics cannot capture, and they want the heavy, nightly correctness scoring of several thousand prompts to run cheaply and at scale.

Which combination of Amazon Bedrock model-evaluation methods best satisfies all of these requirements?

**A.** Use automatic (programmatic) evaluation with classification accuracy and F1 for the correctness scoring, and human-worker evaluation for brand voice and empathy

**B.** Use LLM-as-a-judge evaluation for the nightly correctness scoring at scale, and human-worker evaluation for the subjective brand-voice and empathy scoring

**C.** Use human-worker evaluation for both the correctness scoring and the brand-voice scoring, because human review is the gold standard for all generative output

**D.** Use automatic (programmatic) evaluation for everything, selecting the toxicity and robustness categories to approximate brand voice and empathy

---

## Question 60

Category: Domain 5: Testing, Validation, and Troubleshooting

A RAG chatbot built on an Amazon Bedrock Knowledge Base gives answers that are incomplete — they read fluently and never contradict the sources, but they routinely omit facts the user needed. A retrieve-and-generate Knowledge Base evaluation reports high context relevance, low context coverage, and high faithfulness.

Which stage is at fault, and what is the correct remediation?

**A.** The generator is hallucinating; add a Guardrails contextual grounding check to block low-grounding responses

**B.** Retrieval has a recall gap; revisit chunking strategy, increase top-k, or improve the embeddings so the needed facts are retrieved

**C.** The generator is ignoring good context; switch to a more capable response-generator model and lower the temperature

**D.** The evaluator model is miscalibrated; re-run the job with a different judge model and supply ground-truth references

---

## Question 61

Category: Domain 5: Testing, Validation, and Troubleshooting

An ML platform team uses LLM-as-a-judge in Amazon Bedrock to benchmark several candidate models. A reviewer raises two concerns: (1) one candidate model is from the same family as the chosen judge model, and (2) re-running the same evaluation produces slightly different scores between runs. The comparison feeds a high-stakes go/no-go launch decision.

Which approach correctly addresses both concerns using AWS-recommended practices?

**A.** Supply a custom in-house judge model that shares no architecture with any candidate, and accept a single run as authoritative since the custom judge removes all bias

**B.** Use a consistent evaluator model and fixed configuration across all comparisons for reproducibility, and add human spot checks for this critical comparison given the self-preference risk from the shared-family candidate

**C.** Switch the metric set to the automatic accuracy/robustness/toxicity categories, because programmatic metrics are deterministic and bias-free

**D.** Increase the number of prompts to 10,000 so the larger sample averages out both the non-determinism and the self-preference bias without any human review

---

## Question 62

Category: Domain 5: Testing, Validation, and Troubleshooting

A service calls Amazon Bedrock at high concurrency. Under load it returns frequent HTTP 429 ThrottlingExceptions. Separately, a batch of requests carrying very long prompts consistently fails with ValidationException no matter how many times they are retried. The team currently wraps every Bedrock call in a single exponential-backoff-with-jitter retry loop.

What is the correct way to handle these two failure clusters?

**A.** Keep one retry loop and catch a ContextWindowOverflow exception to separate the long-prompt failures from the throttles

**B.** Apply exponential backoff with jitter to both, and raise max_tokens on the throttled calls so they finish in fewer retries

**C.** Retry the ThrottlingExceptions with backoff and jitter, and stop retrying the ValidationExceptions — instead shorten/chunk the prompt or lower max_tokens

**D.** Remove all retry logic and rely on cross-Region inference profiles to eliminate both error types automatically

---

## Question 63

Category: Domain 5: Testing, Validation, and Troubleshooting

A CloudWatch alarm fires because InvocationLatency on a streaming chat workload built on Amazon Bedrock ConverseStream has climbed steadily over the past week. Before paging the on-call engineer, the team wants to determine whether this is a workload change (users requesting longer answers) or a genuine service-side throughput degradation, because the remediation differs.

Which single derived signal lets the team distinguish the two causes, and how is it interpreted?

**A.** EstimatedTPMQuotaUsage — if it is near the quota ceiling, the model is generating tokens more slowly

**B.** Output Tokens Per Second (OTPS), computed from OutputTokenCount, InvocationLatency, and TimeToFirstToken — stable OTPS means longer outputs (workload change); dropping OTPS means service-side throughput degradation

**C.** InvocationThrottles — a rising throttle count proves the increased latency is caused by quota throttling

**D.** A built-in AWS/Bedrock response-latency-quality metric that flags whether slow responses are also low quality

---

## Question 64

Category: Domain 5: Testing, Validation, and Troubleshooting

Before promoting a new foundation model to a high-traffic Bedrock-backed assistant, a team needs to observe how it behaves on genuine production inputs — real phrasing, real edge cases, real load — but is unwilling to expose even a single user to a potentially bad response. An architect proposes 'just enable a Bedrock deployment guardrail that splits endpoint traffic and rolls back on a CloudWatch alarm.'

Which response correctly identifies the validation pattern and corrects the architect's assumption?

**A.** Use a canary deployment routing 1-5% of live traffic to the new model; this is the only zero-exposure option and Bedrock provides the traffic-splitting natively

**B.** Use shadow testing — mirror a copy of live traffic to the new model and log its responses without serving them; Bedrock has no native endpoint traffic-splitting, so implement this at the application/routing layer

**C.** Use A/B testing on a small slice and compare user-feedback scores; the architect is correct that Bedrock deployment guardrails handle the rollback

**D.** Use a CloudWatch Synthetics canary to mirror production traffic to the new model with automatic rollback via a Bedrock deployment guardrail

---

## Question 65 (Select THREE)

Category: Domain 5: Testing, Validation, and Troubleshooting

A team is hardening the release process for a RAG application on Amazon Bedrock. They want two guarantees grounded in AWS's named guidance: (1) no release should ship if answer faithfulness regresses below the recorded baseline, and (2) a new RAG configuration must be validated against real production inputs with zero user exposure before any rollout.

Which THREE statements correctly describe AWS-aligned ways to meet these requirements? (Select THREE)

**A.** Implement a golden-dataset regression quality gate that re-runs a fixed ground-truth dataset against the candidate, scores faithfulness, and fails the build when scores drop below a predefined threshold (AWS Prescriptive Guidance CI/CD gate)

**B.** Establish the baseline-before-change discipline against ground-truth data per the Well-Architected Generative AI Lens best practice GENOPS03-BP01 ('Implement prompt template management')

**C.** Use shadow testing to validate the new configuration on a mirrored copy of production traffic whose responses are logged but never served, satisfying zero user exposure

**D.** Enable a built-in CloudWatch hallucination-rate metric in the AWS/Bedrock namespace and fail the build automatically when it exceeds a threshold

**E.** Credit the automated 'fail-the-build-below-threshold' quality gate to the Well-Architected Generative AI Lens, since the Lens owns all CI/CD quality gates

**F.** Use a canary deployment routing 5% of live traffic to the new configuration, since a small live slice is functionally equivalent to zero user exposure

---

