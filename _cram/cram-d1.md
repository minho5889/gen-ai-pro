# Cram Sheet — Domain 1: FM Integration, Data Management & Compliance (31%)

**Frame:** The largest domain. You don't train models — you *select, invoke, ground, retrieve, prompt, and govern* pre-built FMs on Bedrock. Most questions are "match the requirement to the cheapest/safest pattern."

| Task | Scope | Lives in |
|---|---|---|
| 1.1 | Design GenAI solutions (PoC on Bedrock, WA GenAI Lens) | Bedrock core |
| 1.2 | Select/configure FMs (eval, dynamic switching, resilience, customization) | Bedrock core |
| 1.3 | Data validation & processing pipelines | RAG |
| 1.4 | Vector store solutions (KBs, stores, metadata, freshness) | RAG |
| 1.5 | Retrieval mechanisms (chunking, embeddings, search, rerank, query xform) | RAG |
| 1.6 | Prompt engineering strategies + governance | Prompt |

---

## Mental models / decision triggers

- **RAG vs Fine-tune vs Prompt** = a *diagnosis*: wrong format/tone → **prompt** (cheapest, first); missing/changing/private facts → **RAG**; consistent new behavior/style the model resists → **fine-tune** (last). Escalation order per GenAI Lens GENOPS05-BP01: prompt → RAG → fine-tune → custom FM.
- **"Data changes often / private / cite sources" → RAG, never fine-tune.** (The single most-repeated trap.)
- **Cost-lever priority:** smallest model that clears the bar → add a **cascade** (cheap model first, escalate only hard queries) → batch for offline → provisioned only for steady high volume/custom.
- **Vector store cascade (fixed order):** managed-vs-custom → store → chunking → tune retrieval only if a relevance symptom is described. Default to **Bedrock Knowledge Bases** unless told otherwise.
- **Store selection levers (in order):** binary vectors (hardest) → cost vs latency → query type → ops model.
- **Inference mode:** spiky/low → on-demand; steady high/custom → Provisioned Throughput; bulk offline → batch.
- **Structured-output ladder:** prompt *steers* → JSON Schema / strict tool use *enforces structure* → app validation *enforces semantics* → Guardrails *enforces safety*. Layers, not alternatives.
- **Guardrails enforces; prompts suggest.** "Ensure/enforce regardless of input" → Guardrails.

---

## If exam says X → answer Y → why

### 1.1 / 1.2 — Bedrock core, selection, resilience
| X | Y | Why |
|---|---|---|
| Swap models without rewriting app | Bedrock **Converse API** | One contract across message-capable models; swap = change modelId |
| Convert docs to searchable vectors | **Embedding** model (not generative) | Embeddings = similarity search, not answers |
| Systematically review GenAI best practices | **WA GenAI Lens** (WA Tool) | Pillars applied to GenAI |
| Responses cut off / errors on long input | **Context-window overflow** | System+history+retrieved+output must all fit |
| Manage models, buy throughput, logging | **Control plane** (`bedrock`) vs runtime (`bedrock-runtime`) | Resource mgmt ≠ invoke |
| Choose between 2 models for our use case | **Bedrock model evaluation** on representative data | Beats public benchmarks |
| Subjective/domain-expert quality | **Human-based** evaluation | Not machine-measurable |
| Score cheaply at scale w/ explanations | **LLM-as-a-judge** evaluation | Approximates human at lower cost |
| Cut cost across mixed traffic, minimal quality loss | **Model cascading/tiering** | Cheap first, escalate hard |
| Analyze scanned invoices/images | **Multimodal** model | Modality disqualifies text-only |
| Show response as it types, immediately | **ConverseStream** + SSE/WebSockets | Streaming delivers chunks as generated |
| Many prompts in background, no waiting | **Async via SQS+SDK** (or batch) | Decouples request from response |
| Maintain multi-turn context | **Resend full message history** | Bedrock is stateless; app owns history |
| Use a fine-tuned/custom model in prod | **Provisioned Throughput (required)** | Custom models can't run on-demand |
| Summarize 100k docs overnight cheapest | **Batch inference** (via S3) | Async bulk, lower price |
| Agent must call tools / strict JSON | **NOT batch** | Batch supports neither tool calling nor structured output |
| Bursts / limited single-Region capacity, no custom balancer | **Cross-Region inference profile** | Auto-routes, no extra routing/transfer cost |
| Cross-Region inference fails intermittently | **Check SCP/IAM for a blocked destination Region** | One blocked dest Region fails the whole request |
| Data must not leave EU/US/jurisdiction | **Geography-scoped profile** (or single Region) | Geo profile = fixed destination list |
| Max capacity, no residency constraint | **Global inference profile** | Routes to any commercial Region |
| Attribute Bedrock cost across apps/teams | **Application inference profile** | User-created for cost/usage tracking |
| Switch models with no code deploy | **API Gateway + Lambda abstraction + AppConfig** | Config change reroutes |
| Stop hammering a failing dependency | **Circuit breaker** (Step Functions) | Opens after failures |
| Adapt model cheaply without full retraining | **LoRA / adapters** | Train few params on frozen base |
| Smaller/cheaper model w/ near-teacher quality | **Distillation** | Teacher fine-tunes a student |
| Improve alignment w/ reward fns not labels | **Reinforcement fine-tuning** | Learns from reward scores (Lambda) |
| Version/promote model artifacts | **SageMaker Model Registry** | System of record |
| Handle ThrottlingException at scale | **Retry w/ exponential backoff + jitter** (SDK retry mode) | Transient errors may succeed later |
| Retry ValidationException/AccessDenied | **Don't** (client errors) | Deterministically wrong; wastes quota |
| Prevent one client exhausting Bedrock quota | **API Gateway rate limiting** (usage plans) | Per-client throttle at edge |
| Analyze actual prompts/responses | **Bedrock Model Invocation Logging** → CloudWatch/S3 (OFF by default) | Captures full request/response |
| Find slow/failing hop in GenAI workflow | **X-Ray** tracing | Traces across service boundaries |
| Serverless spiky on-demand calls | **Lambda** | Scales to zero |
| Determinism while tuning prompt | **Temperature 0** (greedy) | Removes sampling noise |
| Output too repetitive / loops | Raise temp or **frequency/presence penalty** | Discourages repeated tokens |
| Hard-cap response length | **maxTokens** (not just output indicator) | Indicator asks; maxTokens enforces |

### 1.3 — Data pipelines
| X | Y | Why |
|---|---|---|
| Validate large datasets vs quality rules at scale | **Glue Data Quality** (DQDL/DeeQu) | Rule-based at scale |
| Interactive explore/clean data | **SageMaker Data Wrangler** | Visual prep |
| Make audio/video searchable | **Amazon Transcribe** | Speech→text |
| Extract forms/tables from scans | **Amazon Textract** | Structured extraction |
| Extract entities / detect PII in text | **Amazon Comprehend** | NLP entity/PII (can also redact) |
| Custom/business-specific validation | **Lambda** | Beyond managed rule engines |
| Large-scale batch transformation | **SageMaker Processing** | Containerized batch jobs |
| Intermittent ValidationException, retries don't help | **Fix input formatting** | Client error — malformed JSON, not transient |

### 1.4 — Vector stores & freshness
| X | Y | Why |
|---|---|---|
| Don't want to build/operate RAG plumbing | **Bedrock Knowledge Bases** | Managed RAG |
| Fully managed, ms latency, scales to billions, no infra | **OpenSearch Serverless** | AWS default; no reindex; only store for Confluence/SharePoint/Salesforce |
| Lowest cost, huge infrequently-queried corpus | **S3 Vectors** | ~90% cheaper; sub-second (not ms); float32; no hybrid |
| Need binary vectors | **OpenSearch Serverless or Managed only** | Others are float32 only |
| Multi-hop reasoning across related docs | **Neptune Analytics (GraphRAG)** | Vector + graph traversal; S3 sources only |
| Vectors beside relational data / SQL+vectors | **Aurora PostgreSQL + pgvector** | Relational + vector in one DB |
| Need cluster-level tuning control | **OpenSearch Managed** (BYO; needs public access) | You size nodes |
| Bedrock should create the index | **Quick-create**: OSS, Aurora PG Serverless, Neptune, S3 Vectors | Exactly 4 stores |
| Filter retrieval by 2024/tenant/category | **Metadata filtering** | Sharpens relevance + access control |
| Auto-build filter from NL query | **Implicit filtering** (Claude models) | From query + schema |
| Cited answer fluent but quotes outdated facts | **Stale retrieval — re-sync** (StartIngestionJob) | Index not synced; incremental |
| Push one known-changed doc immediately | **IngestKnowledgeBaseDocuments** (direct ingestion) | Single step; S3/Custom only |
| What happens to embeddings on KB delete | **dataDeletionPolicy** DELETE vs RETAIN | DELETE removes embeddings, never the store |
| Auto-sync within minutes of S3 landing | S3 events→EventBridge→Lambda→SQS→Step Functions→sync (Pattern A) | Buffer + quota-aware orchestration |
| Nightly/hourly periodic refresh | **EventBridge Scheduler**→Lambda→StartIngestionJob (Pattern B) | Simpler/cheaper |

### 1.5 — Embeddings, chunking, retrieval
| X | Y | Why |
|---|---|---|
| Retrieval garbage after embedding-model change | **Embedding model mismatch** (re-embed corpus) | Query+docs must share one space |
| Configurable embedding dimensions | **Titan Text Embeddings V2** (256/512/1024) | V1/G1 fixed |
| Cut storage, minimal accuracy loss, stay float32 | **Lower Titan V2 to 256-dim** | ~97% accuracy at ~75% less storage |
| Cut storage, accept precision loss | **Binary vectors** (OpenSearch only) | 1 bit vs 32/dim |
| Data already split into coherent passages | **NONE** chunking | One chunk/file, no re-split |
| Unstructured prose, simple default | **FIXED_SIZE** (overlapPercentage 1–99, required) | Predictable; overlap softens boundaries |
| Content has natural topic shifts | **SEMANTIC** chunking | Boundaries at topic change (uses FM — costs more) |
| Structured manual w/ sections | **HIERARCHICAL** chunking | Child matches, parent gives context; not for S3 vector buckets |
| Need to change chunking after ingestion | **Not possible** — new data source + re-ingest | Strategy fixed at creation |
| Queries mix concepts + exact codes/SKUs | **HYBRID search** | Vector for meaning + keyword for tokens |
| Set HYBRID, no error, still semantic | **Store doesn't support hybrid — silent fallback** | Hybrid only on Aurora/RDS, OSS, MongoDB Atlas |
| Best chunk retrieved but ranked too low | **Reranking** | Second relevance pass reorders |
| Reranking in us-east-1, which model? | **Cohere Rerank 3.5** | Amazon Rerank 1.0 NOT in us-east-1 |
| Complex multi-part question | **Query decomposition** (QUERY_DECOMPOSITION on RetrieveAndGenerate) | Split→retrieve each→combine |
| Custom multi-step query rewriting/routing | **Bedrock + Lambda + Step Functions** | Beyond managed primitive |
| How many chunks by default? | **5** (numberOfResults, a max not guarantee) | Hierarchical can return fewer |
| Consistent way for any model to call retrieval | **Function calling** (Converse tool use) | Same tool-use contract across models |
| Open standard wiring agents to tools/data | **MCP** | Universal connector; Bedrock Agents can use MCP servers |
| Finished grounded answer in one call | **RetrieveAndGenerate** | Retrieve + generate + citations |
| Multi-turn chat remembering earlier turns | **RetrieveAndGenerate + sessionId** | Built-in session memory |
| Raw chunks for custom pipeline / eval retrieval | **Retrieve** | Retrieval only, no gen, no memory |
| NL questions over Redshift warehouse | **Structured store via GenerateQuery** | NL→SQL, no embeddings |

### 1.6 — Prompt engineering & governance
| X | Y | Why |
|---|---|---|
| Model does task but format/tone wrong | **Prompt engineering** | Steering needs no weights |
| Behavior must persist across every turn | **Put it in the system prompt** | Re-sent each turn |
| Where does the instruction go? | **At the end**, after context+data | Model reads material before directive |
| Provide input/output examples in prompt | **Few-shot / in-context learning** | Teaches at inference, no weight change |
| Output correct but wrong format/inconsistent | **Few-shot** | Steers content AND format |
| Add "Let's think step by step", no examples | **Zero-shot chain-of-thought** | Elicits reasoning |
| Improve multi-step reasoning accuracy | **Chain-of-thought** (needs large model) | Decomposition reduces errors |
| Generate many paths, take majority answer | **Self-consistency** (temp > 0) | Voting needs divergent paths |
| Cut CoT token/latency cost, keep accuracy | **Chain-of-Draft** | ~75% fewer tokens, ~78% lower latency |
| Decompose task into sequence of prompts | **Prompt chaining** | Each output → next input |
| No-code managed orchestration of multi-step | **Bedrock Flows** | Managed prompt chaining |
| Wrap retrieved data so not treated as instructions | **Delimiters / instruction-data separation** | Reduces (not eliminates) injection |
| Guaranteed schema-conformant JSON, no retries | **Structured outputs (JSON Schema)** | Bedrock enforces; bad schema → 400 |
| Output must drive a function/API/agent action | **Tool use / function calling** (strict) | Args constrained to inputSchema |
| Validate rating 1–5 or code is 8 chars | **App-side validation** | Schema subset excludes min/max, minLength/maxLength |
| Ensure no toxic content / PII leak | **Guardrails** (not prompts) | Safety control; does NOT enforce JSON |
| Invoke managed prompt for non-Claude/Llama model | **Converse API** | InvokeModel only works for Claude/Llama prompts |
| Override system prompt when using managed prompt | **Not possible** — define inside the prompt | Preserves versioning guarantee |
| Roll back a regressed prompt | **Point ARN ref to prior version** | Versions immutable; old one unchanged |
| Central versioned prompt catalog | **Bedrock Prompt Management** | Decouples prompt from code |
| Compare phrasings side-by-side | **Prompt variants** (up to 3, transient) | Experiment; only chosen persists as draft |
| Automatically rewrite/improve a prompt | **Prompt Optimization** (Management never rewrites) | Optimization is the only rewriter |
| Compare prompt perf across models (migration) | **Advanced Prompt Optimization** | Up to 5 models, eval data |
| Track which prompt version produced an output | **CloudTrail RenderPrompt data events** (must enable) | Data event, not management |
| Audit who created/promoted a prompt | **CloudTrail management events** (default on) | CreatePrompt/CreatePromptVersion logged by default |

---

## Top Traps (named distractors)

1. **Fine-tuning for fresh/private facts** — that's RAG's job. Fine-tune is for behavior/style, not freshness.
2. **HYBRID silent fallback** — requesting HYBRID on an unsupported store (S3 Vectors, Neptune) raises NO error; it quietly runs semantic. Hybrid only on Aurora/RDS, OSS, MongoDB Atlas.
3. **Binary vectors anywhere** — only OpenSearch Serverless/Managed store them; pairing with Aurora/Pinecone/S3 Vectors is a distractor.
4. **Guardrails do NOT scrub retrieved KB chunks** — only input query + generated output. Sensitive text in citations slips through.
5. **Guardrails guarantee valid JSON** — wrong control. Structure = structured outputs + app validation; Guardrails = safety only.
6. **Chunking is editable in place** — immutable after data-source creation; must recreate + re-ingest.
7. **Amazon Rerank 1.0 in us-east-1** — not available there; only Cohere Rerank 3.5.
8. **numberOfResults is a guarantee** — it's a max (default 5); hierarchical chunking returns fewer (children collapse into parents).
9. **dataDeletionPolicy DELETE tears down the store** — it only removes Bedrock's embeddings; never the OpenSearch collection/Aurora cluster.
10. **Structured (SQL) store uses the vector knobs** — no embeddings; numberOfResults/search type/metadata filtering don't apply (NL→SQL via GenerateQuery).
11. **Embedding-model mismatch** — different model at ingest vs query collapses retrieval; must re-embed corpus.
12. **Batch supports tool calling / structured output** — it supports neither; rules out agent/strict-JSON scenarios.
13. **Custom model on-demand** — fine-tuned/distilled/imported models REQUIRE Provisioned Throughput.
14. **Retrying client errors** — Validation/AccessDenied are deterministic; only retry transient (Throttling/Timeout/ServiceUnavailable/InternalServer).
15. **System-prompt text alone stops injection** — instructions are requests, not enforcement; need delimiters + Guardrails (defense-in-depth).
16. **Managed-prompt overrides** — can't pass system/inferenceConfig/toolConfig/additionalModelRequestFields alongside a prompt ARN.
17. **startsWith/stringContains on a managed KB** — unsupported on ANY managed KB (incl. quick-create OSS and S3 Vectors); use equals/in/numeric, or BYO OpenSearch Serverless.
18. **Confusing variants with versions** — variants are transient experiments; versions are immutable deploy artifacts.

---

## Hard numbers worth memorizing

- Token ≈ **4 chars**; ~1,000 tokens ≈ **750 words** (model-specific).
- Titan Text Embeddings V2: dims **256 / 512 / 1024** (default 1024); max input **8,192 tokens** (~50k chars).
- Titan V2 **256-dim ≈ 97% accuracy at ~75% less storage** vs 1024-dim. *(point-in-time)*
- Float32 = **32 bits/dim**; binary = **1 bit/dim**.
- Default chunking ≈ **300 tokens**, sentence-aware.
- FIXED_SIZE overlapPercentage **1–99** (required); SEMANTIC bufferSize **0–1**, breakpointPercentileThreshold **50–99**; HIERARCHICAL maxTokens up to **8,192**/level, exactly **2 levels**.
- **numberOfResults default = 5** (max, not guarantee).
- RetrieveAndGenerate query limit = **1,000 characters**.
- Metadata sidecar files: JSON, **≤ 10 KB** each, one per source file.
- OpenSearch Serverless: up to **16,000 dimensions**; scales thousands→billions, no reindex.
- S3 Vectors ≈ **90% cheaper**; sub-second latency. *(point-in-time)*
- Quick-create = exactly **4** stores (OSS, Aurora PG Serverless, Neptune, S3 Vectors).
- Ingestion quotas (per Region): ~**5** concurrent jobs/account, **1**/KB, **1**/data source; StartIngestionJob ~**0.1 RPS** (1 per 10s). *(point-in-time)*
- New embeddings queryable after a few minutes for all stores **except Aurora/RDS** (immediate).
- Self-consistency: **5–20** reasoning paths, ~N× cost.
- Chain-of-Draft: ~**75% fewer tokens**, ~**78% lower latency**. *(point-in-time)*
- Prompt variants: up to **3** for side-by-side comparison.
- Advanced Prompt Optimization: up to **10** templates, **100** eval samples/template, **5** models; default judge = Claude Sonnet 4.6. *(point-in-time)*
- Provisioned Throughput commitment terms: none / **1 month** / **6 months** (longer = deeper discount); sold in **Model Units (MUs)**; needs MU quota increase via AWS Support.
- IAM to invoke a managed prompt: `bedrock:InvokeModel` + `bedrock:RenderPrompt`.
- Cross-Region inference: **no** extra routing/data-transfer cost.
