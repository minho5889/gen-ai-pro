# Cram D3 — AI Safety, Security & Governance (20%)

**Frame:** Defense-in-depth for safe GenAI. Content-layer threats sit *on top of* (not instead of) network/IAM/encryption. No single control is ever the answer.

**Tasks:** 3.1 input/output safety (Guardrails) · 3.2 data security & privacy · 3.3 governance/compliance · 3.4 responsible AI. **Weight: 20%.**

**3 layers (memorize in order):** Layer 1 input filtering (Comprehend, Guardrails-input, Lambda) → Layer 2 model controls (Guardrails policies) → Layer 3 output verification (Lambda, JSON Schema, Guardrails-output, PII redaction). Guardrails spans all three.

---

## 3.1 — Input/Output Safety & Guardrails

| Exam says X | Answer Y | Why |
|---|---|---|
| "Reduce hallucinations / safer outputs" | Layered: RAG grounding + contextual grounding + structured output | Pattern 2 is never one control |
| "Input filtering alone secures it" / "output check alone is enough" | Distractor — insufficient | Each layer blind where the other sees |
| "Same safety policy across multiple/non-Bedrock models" | Bedrock Guardrails (model-agnostic, decoupled engine) | Authored once, applied everywhere |
| "Screen text for self-managed/3rd-party model, no FM call" | ApplyGuardrail API (source=INPUT/OUTPUT) | Evaluates arbitrary text; returns GUARDRAIL_INTERVENED or NONE |
| "HIGH filter strength" | Most aggressive — blocks down to LOW confidence | Strength = how much it blocks, NOT model confidence (inverted!) |
| "Replace PII with tag, keep rest of response" | Sensitive-info filter — MASK (reported ANONYMIZED) | Mask exists ONLY on PII filter |
| "Reject whole response if PII present" | Sensitive-info filter — BLOCK | |
| "Block a competitor name / specific word" | Word filter | Denied topics = themes, not words |
| "Keep model off an entire subject area" | Denied topics (≤30 *(ceiling point-in-time)*, name+definition+≤5 phrases) | |
| "Response invents facts not in source" | Contextual grounding — grounding score below threshold | Higher threshold = stricter |
| "Correct but answers wrong question" | Contextual grounding — relevance score below threshold | |
| "Provable/auditable compliance with encoded rules" | Automated Reasoning checks (formal logic, ≤99%, detect-only) | Same family as IAM Access Analyzer |
| "Tune guardrail without blocking real traffic" | Detect mode | Reports in trace, no action |
| "Roll back a guardrail safely" | Point prod at earlier numbered version | DRAFT mutable; versions immutable |
| "Sequence checks / branch on result / escalate to human" | Step Functions + Lambda workflow | Guardrail = one eval; can't orchestrate |
| "One consistent policy across requests" | Guardrails alone (simpler is correct) | |
| "Pause for human approval before release" | **Standard** Step Functions (≤1yr, human-approval) | Express (≤5min) has no human step |
| "Score toxicity and route on the number" | Comprehend DetectToxicContent (7 cats + TOXICITY 0–1) | Numeric → conditional routing |
| "Guarantee parseable/safe response shape" | Structured output via JSON Schema (Layer 3 control) | |
| "Need citations + fixed JSON schema on Claude" | Not possible together → 400 error | Mutually exclusive |
| "Malicious instruction in an ingested doc" | Indirect prompt injection | Covert, persistent, more dangerous |
| "Stop injection payloads at network edge" | AWS WAF (perimeter) | |
| "RAG still leaks PII through citations" | Screen retrieved chunks separately | Guardrails don't scrub retrieved chunks |
| "Confine input like a parameterized SQL query" | Secure prompt template — XML / salted-sequence tags | Separates instructions from data |

**6 policy types:** Content filters (Hate/Insults/Sexual/Violence/Misconduct/Prompt Attack; text+image; strength per category, separate in/out) · Denied topics · Word filters (managed profanity + custom ≤10k) · Sensitive-info (PII, ML + custom regex, Block/Mask) · Contextual grounding (output-only; QA/RAG/summarization, NOT free-form chat) · Automated Reasoning (output, detect-only, English-US, no streaming).

**Strength scale:** NONE=nothing · LOW=HIGH-conf only (least aggressive) · MEDIUM=+MED · HIGH=+LOW (most aggressive).
**Direct vs indirect injection:** Direct = user types it; Indirect = hidden in retrieved/ingested content (the more dangerous one).
**Safest RAG screens at 3 points:** pre-ingestion · retrieved chunks (ApplyGuardrail/Comprehend) · final answer. Guardrail-only covers only the last.

---

## 3.2 — Data Security & Privacy

| Exam says X | Answer Y | Why |
|---|---|---|
| "Find/classify sensitive data in S3" | Amazon Macie | THE S3 discovery service (not inline, doesn't redact) |
| "Redact PII from docs in S3" | Comprehend StartPiiEntitiesDetectionJob | Redaction = async batch; reads/writes S3 |
| "Detect PII + return its location" | Comprehend DetectPiiEntities | type, confidence, char offsets |
| "Return only which PII types present" | Comprehend ContainsPiiEntities | labels only, no offsets |
| "Redact PII as objects retrieved from S3" | S3 Object Lambda + Comprehend | Original stays intact |
| "Mask PII inline in prompt/response" | Guardrails sensitive-info filter | Boundary control at model |
| "Clean RAG source before vector store" | Pre-ingestion redaction (Comprehend) | Guardrails can't reach corpus |
| "Granular (table/column/row) access to the corpus data lake" | **Lake Formation** (over Glue Data Catalog; LF-tags at scale) | IAM/S3 = bucket/prefix level; data-layer control, not boundary |
| "Control + audit the encryption key / revoke" | Customer-managed KMS key (CMK) | AWS owned key not manageable/auditable |
| "Encryption at rest, no key mgmt" | Default AWS owned key | Free, fully managed |
| "Are prompts used to train base model?" | No | Bedrock never trains base on your data |
| "Is data shared with model provider?" | No | Runs in isolated AWS deep-copy |
| "Keep data in US/EU geography" | Geographic cross-Region inference profile | Bounds in-transit routing |
| "Restrict which Regions can be called" | IAM/SCP with `aws:RequestedRegion` | |
| "Auto-delete GenAI data after N days" | S3 Lifecycle expiration policy | |

**Service chain:** Macie discovers → Comprehend redacts → KMS encrypts.
**Comprehend vs Guardrails PII:** Comprehend = data-layer (corpus, pipelines, S3, retrieved chunks; EN+ES only). Guardrails = inline at model boundary (prompt+response; broader langs on Standard). Complementary — use both.
**In transit:** TLS 1.2 (no config). **Encryptable w/ CMK:** customization jobs/custom models, Agents, KBs, Guardrails, Prompt flows, stored sessions.
**Fine-tune trap:** base-model guarantee does NOT protect your own fine-tune — it can memorize & replay training-set PII. Redact before customization.
**Cross-Region inference:** data at rest stays in source Region; in-transit may cross Regions within chosen geography.

---

## 3.2 (cont.) — Access Control

| Exam says X | Answer Y | Why |
|---|---|---|
| "App needs to call a model" | `bedrock-runtime` data plane (InvokeModel/Converse) | Not control plane |
| "Admin configures guardrail/logging" | `bedrock` control plane (CreateGuardrail, PutModelInvocationLoggingConfiguration) | |
| "Grant Converse but no Converse action exists" | Grant `bedrock:InvokeModel` | Converse rides on InvokeModel |
| "Restrict role to Anthropic only" | Resource `...::foundation-model/anthropic.*` | Family allowlist |
| "Why no account ID in model ARN?" | Base models are AWS-owned | `bedrock:{region}::foundation-model/{id}` |
| "Private access, no public internet, no code change" | Interface VPC endpoint (PrivateLink) + Private DNS | No IGW/NAT/VPN/DX; not gateway endpoint |
| "Store Pinecone/Redis API key" | Secrets Manager (`credentialsSecretArn`) | 3rd-party vector store needs secret |
| "Connect KB to OpenSearch Serverless/Aurora" | IAM, no secret | First-party = IAM |
| "Confluence/Salesforce/SharePoint connector auth" | Secrets Manager | S3 connector = IAM, no secret |
| "Mandate specific guardrail on every call" | `bedrock:GuardrailIdentifier` (Allow StringEquals + Deny StringNotEquals) | |
| "Pin a guardrail version in IAM" | Condition key with `:1`, NOT resource ARN | Versionless ARN covers all versions |
| "GuardrailIdentifier enforcement breaks RetrieveAndGenerate/InvokeAgent" | Use a separate role | Composite calls make ungoverned InvokeModel calls |
| "Share a guardrail across accounts" | Not via resource policy — centralize instead | Guardrails have no resource-based policy |

**4 API surfaces:** `bedrock` + `bedrock-agent` (control) · `bedrock-runtime` + `bedrock-agent-runtime` (data). Min inference perms = InvokeModel + InvokeModelWithResponseStream.
**Agent role:** trust = `bedrock.amazonaws.com` + `aws:SourceAccount`/`aws:SourceArn` (confused deputy). Action-group Lambda also needs resource policy admitting Bedrock (both sides).
**ApplyGuardrail on 3rd-party model:** only `bedrock:ApplyGuardrail`, no InvokeModel.

---

## 3.4 — Responsible AI

| Exam says X | Answer Y | Why |
|---|---|---|
| "How many RAI dimensions?" | **Eight** | Veracity-and-robustness is ONE combined dim (9 = trap) |
| "Detect bias in data before training" | Clarify pre-training metrics (model-agnostic, on dataset) | CI, DPL, KL/JS… |
| "Detect bias in model predictions" | Clarify post-training metrics (11, on confusion matrix) | DPPL, DI, CDDPL |
| "Explain which features drove a prediction" | Clarify SHAP feature attribution | Model-agnostic |
| "Evaluate model for bias/toxicity PRE-deployment" | SageMaker Clarify | Assessment tool |
| "Filter harmful content AS generated" | Bedrock Guardrails | Runtime control |
| "AWS documents an AWS model's limits" | AWS AI Service Card | AWS-authored, you READ |
| "Document YOUR model for governance" | SageMaker Model Card | You WRITE; immutable versions; Model Registry |
| "Model risk-rating values" | unknown, low, medium, high | |
| "Prove an image was AI-generated" | Watermark detection — DetectGeneratedContent | Provenance ≠ Guardrails/Macie/Comprehend |
| "Disable Titan image watermark" | Not possible | On by default, always |
| "Show agent's step-by-step reasoning" | Bedrock agent trace — `enableTrace` | Reasoning display |
| "Prescriptive RAI best practices framework" | Well-Architected Responsible AI Lens | Distinct from Generative AI Lens |

**8 dims:** fairness, explainability, privacy & security, safety, controllability, veracity & robustness, governance, transparency. For GenAI: veracity + safety weighted most.
**Clarify FM eval:** fmeval lib (can eval non-AWS models), supports ISO 42001. Bedrock has its own Model Evaluation (auto / human / LLM-as-judge).
**Service-card vs model-card:** AWS docs AWS service (read) vs you doc your model (write).

---

## 3.3 — Governance, Compliance & Auditability

**Three questions, three services:** *What was said* → Model Invocation Logging · *Who did what* → CloudTrail · *How it behaves / how often safety fired* → CloudWatch.

| Exam says X | Answer Y | Why |
|---|---|---|
| "Audit actual prompt/response content" | Model Invocation Logging | Only service capturing inference content |
| "Prompts missing from audit trail" | Logging never enabled (off by default) | Enable via PutModelInvocationLoggingConfiguration |
| "Who created/deleted a guardrail & when" | CloudTrail | Mgmt API call + caller identity |
| "Where is prompt body in CloudTrail?" | It isn't — only call + modelId | responseElements null |
| "Audit InvokeAgent/RetrieveAndGenerate" | CloudTrail **data events** — enable explicitly | Off by default (mgmt events on by default) |
| "Detect spike in blocked/unsafe content" | CloudWatch alarm on **InvocationsIntervened** | Headline guardrail metric (AWS/Bedrock/Guardrails) |
| "Blocked content never in logs" | FALSE | Plaintext in Model Invocation Logs if logging on |
| "Detect tampering w/ safety config from new location" | CloudTrail + **GuardDuty** | GuardDuty analyzes CloudTrail |
| "Store metadata for RAG corpus/datasets" | AWS Glue Data Catalog | Crawlers discover schemas |
| "Visualize how data flowed source→output" | DataZone / SageMaker Catalog (OpenLineage) | Consumes Glue lineage; Glue is store not viz |
| "Trace which corpus version produced answer" | Metadata tagging (LSREL07-BP04) | Lifecycle tags + centralized lineage |
| "Model fair at launch became biased over time" | SageMaker Clarify bias drift monitoring (Model Monitor) | Continuous + CloudWatch alerts |
| "Keep PII out of app logs entirely" | Comprehend token-level redaction | Scrub before it persists |
| "Prebuilt GenAI compliance evidence framework" | Audit Manager GenAI Best Practices Framework v2 | Closed to new customers |

**Model Invocation Logging:** runtime ops only (Converse, ConverseStream, InvokeModel, InvokeModelWithResponseStream); S3 (gzip JSON, inline ≤100KB) or CloudWatch Logs (stream `aws/bedrock/modelinvocations`).
**Compliance stack:** Config (config state) + CloudTrail (activity) + Audit Manager (evidence to framework). Reports via AWS Artifact.

---

## Top Traps (named distractors)

- **Filter-strength inversion** — HIGH = most aggressive, LOW = least. "Low sounds safer" is the trap.
- **Guardrails-alone covers RAG** — does NOT scrub retrieved chunks or source corpus (where indirect injection + source PII live).
- **Input filtering alone / output checking alone** — each blind where the other sees; defense-in-depth needs both.
- **MASK on a non-PII policy** — mask/anonymize exists ONLY on the sensitive-info filter.
- **Denied topics for a specific word/name** — that's a word filter; denied topics = themes.
- **CloudTrail has prompt content** — it doesn't (responseElements null); content = Model Invocation Logging.
- **Blocked content is gone** — still plaintext in Model Invocation Logs if logging enabled.
- **Data events on by default** — InvokeAgent/Retrieve/RetrieveAndGenerate/InvokeFlow are off by default.
- **Base-model guarantee covers your fine-tune** — it doesn't; fine-tunes replay training PII.
- **9 RAI dimensions** — there are 8 (veracity-and-robustness is one).
- **AI Service Card = you author it** — no, AWS authors it; you author Model Cards.
- **Disable Titan watermark** — impossible; always on.
- **Pin guardrail version via resource ARN** — versionless ARN covers all versions; use GuardrailIdentifier `:N`.
- **Guardrail enforcement role reused for RetrieveAndGenerate** — breaks (ungoverned internal calls); separate roles.
- **Express Step Functions for human approval** — Express has no human step; use Standard.
- **Gateway endpoint for Bedrock** — Bedrock uses interface endpoints (PrivateLink); gateway only S3/DynamoDB.
- **Prove image AI-generated with a guardrail** — provenance = watermark detection (DetectGeneratedContent).
- **Glue Data Catalog visualizes lineage** — no; it's the metadata store. Viz = DataZone/SageMaker Catalog.

---

## Decision triggers / mental models

- **Guardrail vs custom workflow:** one consistent policy → Guardrails alone. "and then" / "depending on" / "escalate to reviewer" → Step Functions + Lambda.
- **Standard vs Express SFN:** human-in-the-loop / long-running → Standard. High-volume short, no human → Express.
- **Reduce hallucination:** RAG (supply facts) → contextual grounding (verify answer) → optionally route low scores to HITL. Layer them.
- **PII: where?** in corpus/pipeline/S3 → Comprehend / Macie / KMS (data layer). Inline at invocation → Guardrails PII filter.
- **Comprehend PII:** sync = detect only; redaction = async batch job (S3→S3) or S3 Object Lambda for redact-on-retrieval.
- **KMS key:** need control/audit/revoke → CMK. Just at-rest encryption → AWS owned (default).
- **Vector store/connector auth:** 3rd-party (Pinecone/Redis/SaaS) → Secrets Manager. First-party (OpenSearch Serverless/Aurora/S3) → IAM.
- **Control vs data plane:** "configure/manage" → `bedrock`/`bedrock-agent`. "invoke/run" → `bedrock-runtime`/`bedrock-agent-runtime`.
- **Three governance questions:** content → Model Invocation Logging; who/when → CloudTrail; how/how-often → CloudWatch.
- **Tamper detection:** CloudTrail (record) → GuardDuty (threat on top).
- **Clarify vs Guardrails:** pre-deploy bias/toxicity assessment → Clarify. Runtime content filtering → Guardrails.
- **Service vs Model Card:** AWS's model docs → read AI Service Card. Your model docs → write SageMaker Model Card.
- **RAG screening (3 points):** pre-ingestion → retrieved chunks → final answer.

---

## Hard numbers worth memorizing

- 6 Guardrail policy types; content filters = 6 categories (Hate/Insults/Sexual/Violence/Misconduct/Prompt Attack).
- Filter strength: NONE / LOW / MEDIUM / HIGH.
- Denied topics: ≤30 per guardrail *(ceiling point-in-time — verify)*; definition ≤200 chars (Classic) / ≤1,000 (Standard); ≤5 sample phrases (≤100 chars each).
- Word filter: custom list ≤10,000 entries, ≤3 words each.
- Contextual grounding thresholds: 0 to 0.99 (higher = stricter). Source ≤100k chars, query ≤1k, response ≤5k.
- Automated Reasoning: up to 99% accuracy; source docs ≤122,880 tokens; English-US only.
- Comprehend toxicity: 7 categories + overall TOXICITY (0–1); ≤10 segments of 1KB; English only. PII = EN+ES.
- Comprehend prompt-safety classification closed to new customers after **April 30, 2026** *(point-in-time)*.
- Macie sensitivity score: −1 to 100; findings → EventBridge + Security Hub.
- Model risk rating: unknown / low / medium / high.
- 8 Responsible AI dimensions.
- Feature-attribution drift: NDCG 0–1 (1 = no drift); auto-alert below 0.90.
- Model Invocation Logging S3 inline body ≤100KB (gzip JSON); larger/binary = separate object.
- CloudTrail Event history ≈ 90 days; trail = continuous, multi-Region by default.
- In transit = TLS 1.2; compiled JSON-schema grammars cached ~24h.
- Audit Manager GenAI Best Practices Framework v2 = 8 principles, published June 2024; **closed to new customers** *(point-in-time)*.
- Bedrock: HIPAA-eligible, ISO/SOC, CSA STAR Level 2, FedRAMP High in GovCloud (US-West) *(point-in-time — compliance scope evolves)*; reports via AWS Artifact.
