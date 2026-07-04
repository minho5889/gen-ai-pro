# AIP-C01 Domain 2 Cram Sheet — Implementation & Integration (26%)

**Framing:** Build, deploy, and wire foundation-model workloads into real apps. Most questions are "pick the right construct/primitive/API for these constraints" — match latency, scale, auth, residency, and agency to the AWS-intended answer; resist over-engineering.

| Task | Topic | Rough weight |
|---|---|---|
| 2.1 | Agentic AI & tool integration (Bedrock Agents, AgentCore, Strands, Agent Squad, MCP, ReAct, HITL, stopping conditions) | largest slice |
| 2.2 | Model deployment strategy (Lambda on-demand, Provisioned Throughput, SageMaker, containers, cascading) | medium |
| 2.3 | Enterprise integration (GenAI gateway, RBAC over Bedrock, data residency/edge, CI/CD) | medium-large |
| 2.4 | FM API integration (sync/async/batch, streaming, backoff, routing) | medium |
| 2.5 | App integration & dev tools (API GW streaming, Amplify AI Kit, BDA, Q Developer, observability) | medium |

---

## If exam says X → answer Y → why (2.1 Agentic AI & Tools)

| If the exam says... | Answer | Why |
|---|---|---|
| Self-contained transform (summarize/classify/rewrite) | Single prompt | No external actions/loop |
| Answer from our docs, one grounded generation | RAG pipeline | Fixed retrieve-then-generate, not a loop |
| Multi-step, sequence depends on intermediate results | Agent | Only a model-driven loop adapts at runtime |
| "Build an autonomous agent that calls tools" | Use the **managed primitive** (Bedrock Agents) | Don't hand-roll loop/tools/memory (Pattern 3 trap) |
| Highly standardized rule-based / same input → same path | RPA or deterministic orchestration, **not** an agent | Agents are nondeterministic, for contextual reasoning |
| Define agent's tools with an API contract | OpenAPI **3.0.0** schema (S3 or inline) | Action group accepts OpenAPI or function def |
| "OpenAPI 3.0.1" or "use enum for allowed values" | Distractor | Must be exactly 3.0.0; no enum — use `description` |
| Reuse existing APIs OR task runs > 15 min | **Return of control** | App executes the action; no Lambda 15-min cap |
| Bedrock invokes a function with action params | Lambda-backed action group | 1 Lambda/action group + resource-based policy for Bedrock |
| Remember context across sessions (native Bedrock Agents) | Long-term memory via `SESSION_SUMMARY` | Native long-term memory = session summarization |
| Semantic/episodic memory strategies | **AgentCore Memory** (separate service) | Multi-strategy memory is not native Bedrock Agents |
| Require user confirmation before an action | `x-requireConfirmation = ENABLED` | Built-in anti-injection HITL safeguard |
| Agent reformats final answer "by default" | Distractor — post-processing is OFF by default | Must explicitly enable |
| Push update to prod without app code change | New version, repoint **alias** | App calls alias; versions are immutable |
| Pause deployed agent w/o delete or IAM change | Alias state → `REJECT_INVOCATIONS` | Kill-switch toggle on the alias |
| Inspect why agent chose a step / failed | Agent **trace** (OrchestrationTrace, FailureTrace) | Exposes rationale, I/O, failure reason |
| Operate agents at scale, any framework, any model | **Amazon Bedrock AgentCore** | Framework- & model-agnostic operating platform |
| Move LangGraph/CrewAI agent POC→prod securely | AgentCore | Bedrock Agents is Bedrock-only |
| "Abandon Bedrock Agents and switch to AgentCore?" | Existing workloads: no forced migration; **new builds: AgentCore** | Bedrock Agents is now **Agents Classic** — maintenance mode, closed to new customers 2026-07-30 *(point-in-time)* |
| Serverless session-isolated host, up to 8 hrs | AgentCore **Runtime** | Secure serverless execution env |
| One endpoint turning APIs/Lambda into agent tools | AgentCore **Gateway** | Managed MCP endpoint |
| Token vault + OAuth, agent acts on user's behalf | AgentCore **Identity** (Cognito-powered) | Agent credential management |
| Trace any-framework agents w/ OpenTelemetry | AgentCore **Observability** (CloudWatch) | OTEL-compatible |
| Run code / operate a website in the agent | Code Interpreter / Browser | AgentCore built-in sandboxed tools |
| "Strands vs AgentCore — which?" | **Both** — Strands authors, AgentCore operates | Stacked layers, not competitors |
| M apps × N tools, too many custom integrations | MCP turns M×N into M+N | One open standard (Anthropic-originated) |
| Lightweight, stateless tool, bursty traffic | **Lambda-hosted MCP server** | Scales to zero, short bounded exec |
| Long-lived sessions, streaming, heavy deps, VPC | **ECS on Fargate** MCP server | Long-lived containers, network control |
| Single secured MCP endpoint, no infra to run | AgentCore Gateway | Managed MCP endpoint, semantic tool selection |
| Supervisor combines answers from specialists | Bedrock multi-agent collaboration (Supervisor) | Coordinates + synthesizes; **max 10** collaborators |
| Route to one right specialist, lowest latency | Supervisor **with routing** | Single-collaborator routing cuts latency |
| Open-source model-driven SDK, runs anywhere | **Strands Agents** | Authoring framework, runs on AgentCore |
| Open-source orchestrator that classifies intent & routes | **AWS Agent Squad** (open source, not managed) | Classifier routing + SupervisorAgent |
| Single agent: context loss, tool overload, hallucinating | Split into specialized agents | Specialization fixes overload (accept added cost/latency) |
| Force model to call one specific tool | `toolChoice: tool` (Claude 3 / Nova only) | SpecificToolChoice |
| Let model decide whether to use a tool | `toolChoice: auto` (default, portable) | AutoToolChoice |
| `stopReason: tool_use` returned | Run tool, return `toolResult`, re-invoke | Act-observe step; `toolUseId` must match |
| Guarantee tool call matches schema | Structured Outputs — `strict: true` | Constrained decoding |

## If exam says X → Y (2.2 Deployment)

| If the exam says... | Answer | Why |
|---|---|---|
| Serverless, spiky, on-demand model calls | **AWS Lambda** | Scales to zero, event-driven |
| Fine-tuned/custom model in production | **Provisioned Throughput** (required) | Custom models can't run on-demand |
| Steady high volume, guaranteed throughput, no throttling | Provisioned Throughput (Model Units) | Dedicated capacity |
| Self-hosted / full hosting control | SageMaker endpoints or ECS/EKS/Fargate containers | Control GPU/memory/token throughput |
| Cut cost on mixed-complexity traffic | **Model cascading/tiering** | Cheap model first, escalate the hard 10% |
| Lower hourly Provisioned price | Longer commitment (1 or 6 mo) | Deeper discount |

## If exam says X → Y (2.3 Enterprise Integration)

| If the exam says... | Answer | Why |
|---|---|---|
| "All teams' Bedrock spend shows under one role" | Gateway `sts:AssumeRole` per user + **session tags** | Shared role erases per-tenant identity (Scenario 4) |
| "Why build a gateway at all?" | Keys, OpenAPI, throttling, allowlisting, decoupling | **NOT** cost visibility — direct IAM already gives that |
| Tag on-demand model cost, tens–thousands of tenants | **Application inference profiles** | Server-side tags on single-model wrapper |
| Per-tenant cost, hundreds-of-thousands+ tenants | `Converse requestMetadata` + invocation logs | Profiles proliferate / hit tag limits |
| Stop Team B from calling a model | IAM policy / SCP on the **model ARN** | Profiles/tags attribute cost, don't deny |
| Production multi-team gateway credentials | **Short-term** Bedrock API keys (≤12h) | Long-term keys are exploration-only |
| Latency regressed after adding chargeback | Move cost calc to daily EventBridge job | Per-request cost calc in hot path adds latency |
| "Usage plans set, so tenants fully isolated" | Add **per-tenant inference concurrency limits** | Multi-layer throttling, not gateway-only |
| Attach a resource policy to a KB/Agent (cross-acct) | **Trap** — Bedrock has no resource-based policies | Use assumed roles + identity policies + SCPs |
| Lock down `InvokeAgent` to a specific agent | Scope to the **agent-ALIAS ARN** | Agent ARN is for management actions only |
| Restrict invocation to one Knowledge Base | Scope `Retrieve` to the KB ARN | `RetrieveAndGenerate` can't be ARN-scoped (uses `*`) |
| Filter a third-party model w/ guardrail, min perms | `bedrock:ApplyGuardrail` **only** | `InvokeModel` needed only with a Bedrock FM |
| AccessDenied after moving to inference profile | Allow FM ARN in **all** profile Regions + profile ARN + `GetInferenceProfile` | Profile ARN alone insufficient |
| Force every call through a specific guardrail | `bedrock:GuardrailIdentifier` condition key | ARN scoping can't pin a guardrail |
| Stop a team using the premium tier | `Deny` w/ `bedrock:ServiceTier` condition key | Tier control, not separate models |
| Strong regulated per-tenant isolation | **Account-per-tenant** (Orgs + SCPs) | No resource policies; RetrieveAndGenerate unscopable |
| "Run Bedrock at the 5G edge for low latency" | Distractor — put **app tier** in Wavelength | Bedrock is Regional; model call stays in-Region |
| Private connectivity to Bedrock, no internet | **PrivateLink interface VPC endpoint** | Gateway endpoints are only S3/DynamoDB |
| Private Bedrock access from Local Zone app | Routes back to parent Region | Local Zones support no VPC endpoints/VPN |
| Data must never leave the country | **In-Region** inference (single in-country Region) | Geo keeps data in geography, not one Region |
| Max throughput, lowest cost, no residency need | **Global** cross-Region inference | Never a residency answer |
| Cross-Region on for a retention-required model | Retained data lands in **destination** Region | Hidden residency violation |
| EU-personnel-only operator access | **AWS European Sovereign Cloud** | Standard EU Region = residency, not sovereignty |
| Worried the model vendor sees our data | Model Deployment Accounts + Zero Operator Access | Providers have no access; no self-host needed |
| Guarantee nothing is persisted | `data_retention_mode = none` | `store=false` alone ≠ zero retention |
| Prod app calls the agent | Call the **alias**, never DRAFT/TSTALIASID | Alias is the indirection over immutable versions |
| Changed agent instructions but no effect | Call **`PrepareAgent`**, cut new version, repoint alias | Config edits need re-Prepare to deploy |
| Catch silent prompt quality regression | **Golden prompt-response regression tests** | Unit tests miss non-deterministic degradation |
| GenAI-specific CI/CD stage | Prompt lint, golden tests, cost-impact gate | Generic pipelines lack these |

## If exam says X → Y (2.4 FM API Integration)

| If the exam says... | Answer | Why |
|---|---|---|
| Write once, run across multiple models | **Converse API** | Consistent contract; swap = `modelId` change |
| Need model's raw native param format | InvokeModel (or `additionalModelRequestFields`) | Lower-level escape hatch |
| Model takes 40s, REST API times out | **API Gateway integration timeout** (29s default), not Lambda | API GW binds first |
| Generate a 2-min video | `StartAsyncInvoke` → S3 | Long single generation exceeds sync window |
| Summarize 250k docs cheaply, no rush | `CreateModelInvocationJob` batch (~50% off) | High-volume, non-urgent |
| Know when batch job finishes, min compute | **EventBridge** job state-change rule | Beats polling Get APIs |
| Bursty traffic → ThrottlingException | **SQS buffer** in front of Lambda worker | Smooths concurrency; raising Lambda concurrency doesn't help |
| Chain several FM calls with a human gate | **Step Functions** (Standard + wait-for-callback) | Durable, retryable, auditable; Express can't wait |
| Chat feels slow to first token | **ConverseStream** streaming | Fixes time-to-first-byte |
| Handle ThrottlingException at scale | Retry w/ **exponential backoff + jitter** (SDK retry mode) | Transient errors may succeed later |
| Retrying ValidationException / AccessDenied | **Don't** — client errors fail deterministically | Wastes quota |
| Route simple vs complex queries to models | Dynamic content-based routing (Step Functions) | Implements the cascade |
| Find slow/failing hop in GenAI workflow | **AWS X-Ray** tracing | Traces across service boundaries |
| Analyze actual prompts/responses | **Bedrock Model Invocation Logging** (OFF by default) → CloudWatch/S3 | Captures full request/response |

## If exam says X → Y (2.5 App Integration & Dev Tools)

| If the exam says... | Answer | Why |
|---|---|---|
| Stream chat w/ Cognito User Pool, **least code** | **AppSync GraphQL subscriptions** | Native Cognito auth; others need custom auth |
| Persistent bidirectional multi-turn chat | API Gateway **WebSocket** API | Bidirectional; needs Lambda authorizer for JWT |
| Lowest-overhead single-user token streaming | **Lambda function URL** w/ streaming | Node native; IAM/manual JWT auth |
| Long FM gen behind REST API times out | Response streaming (timeout up to 15 min) or async | 29s integration timeout binds, not Lambda |
| Edge-optimized REST API needs >29s | Not supported — use Regional or private | Over-29s increase excludes edge-optimized |
| Chatbot needing managed history + UI | Amplify AI Kit **`conversation`** route | `generation` route is single-shot only |
| Process video/audio/PDFs with one API | **`InvokeDataAutomationAsync`** | Synchronous BDA supports images only |
| Orchestrate Textract + Transcribe + Rekognition + glue | **Bedrock Data Automation** unified API | One multimodal API beats stitching services |
| "Customization will leak our private code" (Q Developer) | Not used for training; per-org isolated endpoints | The reassurance, not disabling Q |

---

## Top Traps (named distractors)

- **Pattern 3 (two-sided):** over-agency (agent where a prompt/RAG/Step Functions fits) **and** under-management (hand-rolling the loop instead of Bedrock Agents).
- **Pattern 5:** hardcoding one model ID / one Region — couples you to its availability, price, capacity; forces redeploys. Fix: Converse + Lambda + AppConfig indirection.
- **"Raise the Lambda timeout"** for a slow model — wrong; the binding limit is the **API Gateway 29s integration timeout**.
- **"Raise Lambda concurrency"** for ThrottlingException — pushes throttling onto Bedrock; use **SQS buffer**.
- **"Cost visibility"** as the reason to build a gateway — distractor; reason is governance/throttling/decoupling.
- **Cost attribution ≠ access control** — inference profiles / `requestMetadata` / tags attribute cost, they do **not** deny invocation (use IAM/SCP on model ARN).
- **Bedrock resource-based policies** — don't exist; can't attach a policy to a KB/Agent/Guardrail. Cross-account = assumed roles.
- **`InvokeAgent` on agent ARN** — wrong; must be the **agent-ALIAS ARN**.
- **`RetrieveAndGenerate` ARN-scoped** — can't be; uses `Resource *`.
- **Denying only `InvokeModel`** — leaves `InvokeModelWithResponseStream` (streaming) open; deny both.
- **"Bedrock at the edge"** (Outposts/Wavelength/Local Zones) — Bedrock is Regional; only the app tier goes to the edge.
- **Global inference for residency** — never; Global routes to any Region. Geo keeps data in geography; In-Region for single-country.
- **`store=false` = zero retention** — no; only `data_retention_mode=none`.
- **Long-term Bedrock API keys in production** — exploration-only; use short-term (≤12h).
- **Skipping `PrepareAgent`** — agent config edits silently never deploy.
- **OpenAPI 3.0.1 / `enum`** — must be exactly 3.0.0; no enum (use `description`).
- **Agent post-processing "on by default"** — off by default.
- **Batch for tool-calling / strict JSON** — batch supports neither tool use nor structured output.
- **Synchronous `InvokeDataAutomation` for video** — sync = images only; video/audio/PDF need the **async** API.
- **Amplify `generation` route for a stateful chatbot** — use `conversation` (managed history + UI).
- **Reusing the user's admin/broad token for agent tools** — use scoped, purpose-generated tokens (excessive agency / tool poisoning blast radius).
- **Registering every tool from every MCP server** — drains context linearly; filter or use semantic tool search.

---

## Decision triggers / mental models

- **Agent vs not:** self-contained transform → prompt; answer-from-docs → RAG; fixed steps → Step Functions; steps depend on runtime results → **agent**. Then: agent needed → use the managed primitive, don't build it.
- **RAG vs fine-tune vs prompt:** behavior/tone/format → prompt; current/private/changing facts → **RAG**; consistent baked-in behavior prompting can't enforce → fine-tune (needs Provisioned Throughput). "Changes often / must be current" → RAG, almost always.
- **Cost lever priority (model):** smallest model that clears the bar → add a **cascade** → batch the non-urgent → Provisioned only for steady high volume.
- **Invocation mode:** interactive & fits window → sync (stream if slow to first byte); single long generation → `StartAsyncInvoke`→S3; high-volume non-urgent → batch; bursty/throttling → SQS buffer; multi-step + human gate → Step Functions.
- **Streaming front-end (auth-driven):** Cognito + least code → AppSync subscriptions; bidirectional multi-turn → WebSocket; single-user prototype → Lambda function URL.
- **Deployment substrate:** serverless spiky → Lambda; guaranteed/custom → Provisioned Throughput; self-hosted control → SageMaker / containers.
- **Residency ladder:** single country → In-Region; within a geography → Geo profile; no constraint, cheapest → Global; EU-operator-only → European Sovereign Cloud; US public sector → GovCloud.
- **Agent CI/CD flow:** edit DRAFT → `PrepareAgent` → immutable version → repoint **alias**; rollback = repoint alias; kill-switch = `REJECT_INVOCATIONS`.
- **Agency vs autonomy:** agency = permissions (control with least-privilege role / scoped tools); autonomy = independence (control with HITL approval). Distinct levers.
- **Bedrock Agents vs AgentCore vs Strands:** Agents = managed primitive (Bedrock-only); AgentCore = operating platform (any framework/model); Strands = authoring SDK that runs on AgentCore. They stack — not either/or. *Status: Bedrock Agents is now **Agents Classic** — maintenance mode, closed to new customers 2026-07-30; new builds → AgentCore (point-in-time, verify near exam day).*
- **Stopping/resilience controls:** unbounded loop → stopping conditions (max iterations/timeout/token limits); repeated failures piling up → circuit breaker; one slow call → timeout; primary down → graceful degradation/fallback.

---

## Hard numbers worth memorizing

- API Gateway REST integration timeout: **29s default** (50ms–29,000ms); >29s only for Regional/private (not edge-optimized) *(point-in-time)*.
- API GW HTTP-proxy response streaming timeout: up to **15 min** *(point-in-time)*.
- Lambda response streaming payload: up to **200 MB** (vs 6 MB buffered); first 6 MB uncapped, rest ~2 MB/s *(point-in-time)*.
- AppSync resolver limit: **30s** (why `startStream` must offload to SQS).
- Bedrock batch discount: **~50%** vs on-demand *(point-in-time)*.
- Batch jobs: **~10 concurrent** per model per Region *(point-in-time)*.
- Short-term Bedrock API key: up to **12h**; STS AssumeRole creds valid up to **1h** (cache per user/hour).
- STS default: **~500 AssumeRole/sec/account** *(point-in-time)*.
- Bedrock multi-agent collaboration: **max 10** collaborators per supervisor *(point-in-time)*.
- AgentCore Runtime session: up to **8 hours** *(point-in-time)*.
- Return of control: bypasses Lambda's **15-min** action limit.
- Provisioned Throughput commitment terms: none / **1 mo** / **6 mo** (deeper discount for longer); custom model requires MU quota increase via Support.
- OpenAPI action-group schema version: exactly **`3.0.0`** (no `enum`).
- Global inference ~**10%** cheaper than Geo for some models *(point-in-time, per-model)*.
- Token rough rule: **~4 chars/token**, ~1,000 tokens ≈ ~750 words (model-specific).
- Model Invocation Logging: **OFF by default**; destinations must be same account + Region.
