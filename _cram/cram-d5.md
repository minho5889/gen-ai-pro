# AIP-C01 Cram — Domain 5: Testing, Validation & Troubleshooting (11%)

**Framing:** How do you *prove* a model / RAG / prompt / output is good enough — before and during rollout? The answer is always a structured evaluation or validation mechanism; never "ship and watch," never a classification metric.

- **Task 5.1 — Evaluation systems:** quality dimensions, Bedrock Model Evaluations, RAG eval, LLM-as-a-judge, golden datasets + regression gates, canary/A-B/shadow, synthetic workflows, agent evals.
- **Task 5.2 — Troubleshoot GenAI apps:** context-window overflow, FM/API errors, prompt testing & version compare, retrieval/embedding/drift diagnostics, CloudWatch Logs + X-Ray + schema validation.

---

## If the exam says X → answer Y → why

### Metrics & reference-availability (S1)
| Exam says | Answer | Why |
|---|---|---|
| Accuracy/precision/recall/F1 on chatbot/summarizer/open-ended | **Distractor** — use BERTScore or LLM-judge | No closed label space, no single correct string; F1 needs a confusion matrix |
| Closed-form task (classify, yes/no, single label) | Accuracy/F1 **are valid** | A confusion matrix exists |
| Correct answer phrased differently than reference | **BERTScore** (semantic), not BLEU/ROUGE | n-gram overlap punishes paraphrases; embeddings compare meaning |
| No gold/reference answer | **Reference-free** → LLM-judge or human | Reference-based metrics need a ground-truth string |
| Gold reference exists | Reference-based metrics apply | Reference availability is the *sole* deciding criterion |
| Friendliness / brand voice / subjective style | **Human evaluation** | Scripts miss subjective qualities |
| Score thousands nightly, cheaply, at scale | **Automatic or LLM-judge**, not human | Human is cost/time/scale-limited (≤50 workers, ≤1000 prompts) |
| Fluent + confident ⇒ correct | **Distractor** — fluency ≠ accuracy | They fail independently; factual signal is faithfulness |

*BLEU = precision/translation; ROUGE = recall/summarization (both reference-based, surface n-gram). BERTScore = reference-based but semantic. Robustness = AWS's consistency dimension (lower delta = more stable).*

### Bedrock Model Evaluation (S2)
| Exam says | Answer | Why |
|---|---|---|
| Compare FMs / validate quality before prod | **Amazon Bedrock Evaluations** | Pattern 6 canonical service |
| Fast/cheap/repeatable scoring of structured task | **Automatic (programmatic)** eval | Objective metrics, no human |
| Rate friendliness/brand voice | **Human-worker** eval | Subjective qualities |
| Human-like nuance at scale w/o human cost | **LLM-as-a-judge** | Judge scores + explains |
| Evaluate on *our* use-case prompts | **Custom JSONL dataset in S3** | Built-in datasets = generic benchmarks, automatic-only |
| Recognized benchmark, no labeled data | **Built-in dataset** | Convenience, automatic jobs only |
| Reviewers must be *our* employees/SMEs | **Custom work team** | ≤50 workers, private workforce via SageMaker Ground Truth |
| Human eval without managing a workforce | **AWS-managed work team** | AWS supplies reviewers (blog-verified) |
| Which job needs an evaluator model? | **LLM-judge + RAG jobs** | Automatic metric computation does not |
| Human-based job S3 output write fails | **Configure CORS** on output bucket | CORS required for human jobs, NOT judge jobs |

*Automatic categories = accuracy, robustness, toxicity — but the computed metric changes by task type: RWK (general gen), BERTScore (summarization), NLP-F1 (Q&A), binary accuracy (classification). Toxicity NOT listed for classification. 4 task types: general gen, summarization, Q&A, classification.*

### RAG Evaluation (S3)
| Exam says | Answer | Why |
|---|---|---|
| Bad RAG answer — retrieval or generation? | **Evaluate two stages separately** | Only stage-split scores localize the fault |
| Are we retrieving the right chunks? | **Context relevance** (`Builtin.ContextRelevance`) | Precision-style; **no ground truth needed** |
| Did retrieval find all needed info? | **Context coverage** (`Builtin.ContextCoverage`) | Recall-style; **requires ground truth** |
| Model invents facts not in sources | **Faithfulness / groundedness** (`Builtin.Faithfulness`) | = avoiding hallucination *w.r.t. retrieved text* |
| Score only retriever, no generation | **Retrieve-only** job | Reports on retrieved data only |
| Score whole pipeline end-to-end | **Retrieve-and-generate** job | Adds generation metrics; needs a response-generator model |
| Evaluate a RAG system hosted *outside* Bedrock | **Bring your own inference responses** (BYOI) | Added at GA |
| Does the answer address the question? | **Correctness** (+ Completeness/Helpfulness) | AWS KB RAG has **no** metric named "answer relevance" |

*RAG triad (TruLens term, not AWS): Query→Context = ContextRelevance; Context→Answer = Faithfulness; Query→Answer = Correctness. `Builtin.Relevance` exists only in the model-eval judge set, NOT the KB RAG set.*

### LLM-as-a-Judge (S4)
| Exam says | Answer | Why |
|---|---|---|
| Score outputs at scale w/ human-like judgment | **LLM-as-a-judge** | Judge scores vs defined criteria |
| Bring your own judge model | **Distractor — not possible** | Judge models AWS-curated (Nova, Claude, Llama, Mistral); you select from the list |
| BLEU/ROUGE can't capture meaning here | **LLM-judge** (semantic nuance) | Judges meaning, not n-grams |
| Judge prefers first/longer/own-family answer | **Position / verbosity / self-preference bias** | Research framing (not AWS-doc'd) |
| Critical comparison — trust judge alone? | **No — add human spot checks** | AWS recommends for critical comparisons |
| Judge shares architecture w/ a candidate | **Calibrate with human review** | Self-preference risk |
| Two models in a judge job | **Generator (produces) + evaluator (scores)** | Distinct roles; generator can be BYO responses |
| Define "good" beyond the 11 built-ins | **Custom metrics** (judge prompt + scale) | GA addition |

### Golden datasets / regression (S5)
| Exam says | Answer | Why |
|---|---|---|
| Repeatable, consistent eval across runs | **Golden / ground-truth dataset** | Same inputs scored same way every run |
| Block release if scores drop below threshold | **Regression quality gate** (AWS Prescriptive Guidance) | "Fail the build below threshold" — CI/CD *offline* gate |
| Who owns "fail build below threshold"? | **Prescriptive Guidance**, NOT the WA Lens | Lens owns baseline discipline; PG owns the gate |
| AWS home of baseline-before-change | **GENOPS03-BP01** (GenAI Lens) | Note: titled "Implement prompt template management," NOT "baseline evaluation" |
| Detect data/concept drift w/ baseline + scheduled jobs | **SageMaker Model Monitor** (ML Lens, MLPERF06-BP04) | Drift taxonomy/tooling is ML-Lens/SageMaker |
| Catch quality loss after silent model update | **Re-run fixed golden dataset on schedule** | Holding inputs fixed isolates model-driven change |
| Fairly compare two prompt versions | **Both vs same versioned golden dataset** | Pin dataset version |

*Golden dataset = ground-truth data (GENPERF01-BP01). Sources: real logs (esp. poor outcomes), expert-curated, synthetic edge/adversarial. Expected output = reference text OR expected facts.*

### Deployment-time validation (S6)
| Exam says | Answer | Why |
|---|---|---|
| Validate new model under real traffic, **zero user impact** | **Shadow testing** | Logged but never served |
| Roll out to small % users with **automatic rollback** | **Canary deployment** | 1–5% live slice + auto-rollback limits blast radius |
| Decide which of two prompts users prefer / complete more | **A/B testing** | Signal = user-outcome metrics, not health SLOs |
| Which signal does A/B compare? | **User feedback / task completion / CTR** | Business outcomes (vs canary's latency/error/cost SLOs) |
| Bedrock auto-splits endpoint traffic for canary | **Distractor — not Bedrock** | Traffic-splitting = SageMaker; Bedrock does it at routing layer |
| Scripted requests on a schedule to monitor endpoint | **CloudWatch Synthetics canary** | A monitor, NOT a canary deployment |
| ProductionVariants / ShadowProductionVariants / deployment guardrails | **SageMaker AI**, never Bedrock | |
| Drive validation without real users | **Synthetic workflows / Synthetics canaries** | Generated test traffic pre-prod |
| Using synthetic data — anything required first? | **Validate it (RAIDP02-BP04)** | Fidelity + bias check; High risk if skipped |

### Observability (S7)
| Exam says | Answer | Why |
|---|---|---|
| Capture exact prompt + response of a bad call | **Model Invocation Logging** | Full request/response/metadata per call |
| Bedrock logs every invocation automatically | **Distractor — off by default** | Must enable + set destination first |
| Where can logs go? | **S3, CloudWatch Logs, or both** | Same-account, same-Region only |
| Large/binary response bodies | **S3 only** | Inline log bodies cap at 100 KB |
| Which endpoint does logging cover? | **`bedrock-runtime` only** | Converse, ConverseStream, InvokeModel, InvokeModelWithResponseStream |
| Prompt/completion size & cost metric | **`InputTokenCount` / `OutputTokenCount`** | `AWS/Bedrock` namespace |
| End-to-end latency metric | **`InvocationLatency`** | Send → last token |
| Time-to-first-token — when emitted? | **`TimeToFirstToken`, streaming only** | ConverseStream / InvokeModelWithResponseStream |
| Throttle/error metrics | **`InvocationThrottles`, `InvocationClientErrors`, `InvocationServerErrors`** | Don't count as `Invocations` |
| Built-in CloudWatch hallucination-rate metric | **Distractor — doesn't exist** | Derive it |
| Native-ish hallucination signal | **Guardrails contextual grounding score** | Grounding + relevance; emits Guardrails metrics |
| See an agent's step-by-step reasoning | **Bedrock Agents trace** (`enableTrace`) | Pre/orchestration/post sub-traces |
| Trace request across service boundaries | **AWS X-Ray** | Distributed path (distinct from reasoning trace) |
| Prereq to view AgentCore/X-Ray traces | **Enable CloudWatch Transaction Search** | One-time per-account |

### Troubleshooting failure modes (S8)
| Symptom | Root cause | Fix |
|---|---|---|
| Fluent but wrong/unsupported; low faithfulness | Parametric memory; missing grounding | Guardrails contextual grounding check (block below threshold); ground with RAG |
| `ValidationException` "input too long" / premature TPM throttle | Input+history+context+completion exceed budget; `max_tokens` too big | Dynamic/hierarchical chunking; context pruning; tune `max_tokens` |
| High `InvocationLatency` / `TimeToFirstToken` | Longer outputs (stable OTPS) vs slower gen (dropping OTPS) | Streaming; prompt caching; latency-optimized inference (preview); reranker; right-size model |
| `ThrottlingException` (HTTP 429) | Hit RPM or TPM quota (enforced concurrently) | Exponential backoff + jitter (transient ONLY); rate limit; cross-Region profiles; quota increase; Provisioned Throughput |
| Wrong/incomplete RAG; low relevance/coverage; degrading | top-k miss; embedding mismatch; drift | Reranker + chunking + query reformulation; **re-embed/re-sync** data source; recurring golden-dataset re-run |
| Candidate version below baseline on golden dataset | New prompt/model/param/RAG-config regressed | Regression quality gate (fail build); **rollback**; schema/output validation |

| Exam says | Answer | Why |
|---|---|---|
| "ContextWindowOverflow exception" | **Distractor — no such exception** | Maps to `ValidationException` + quota `ThrottlingException` |
| Retry the `ValidationException` with backoff | **Distractor — NEVER retry it** | `ValidationException`/`AccessDeniedException` are non-retryable client errors |
| Hitting TPM quota earlier than expected | **Reduce `max_tokens`** | Bedrock deducts `input + max_tokens` up front |
| InvocationLatency rose — workload or service? | **Derive OTPS** | Stable OTPS = longer outputs; dropping OTPS = throughput degradation |
| Cut latency on a reused long system prompt | **Prompt caching** | Caches reused prefixes |
| RAG returns approximately-relevant chunks | **Reranker** | Reorders for relevance, returns fewer-but-better |

---

## Top Traps (named distractors)
- **Traditional metrics (accuracy/precision/recall/F1) on open-ended generation** — the canonical Pattern 6 trap. Use BERTScore or LLM-judge.
- **Fluent/confident ⇒ correct** — fluency and accuracy fail independently.
- **"Accuracy" is one fixed computation in Bedrock automatic eval** — it changes by task type (RWK / BERTScore / NLP-F1 / binary).
- **Bring your own judge/evaluator model** — judges are AWS-curated; you bring *responses*, not the judge.
- **LLM-judge fully replaces human eval** — it scales it; spot checks still needed for critical comparisons.
- **Built-in KB "Answer relevance" metric** — doesn't exist; maps to Correctness (RAGAS naming trap).
- **Bedrock natively splits endpoint traffic** for canary/A-B/shadow — that's SageMaker; Bedrock does it at the routing layer.
- **Canary deployment vs CloudWatch Synthetics canary** — same word, unrelated (rollout-with-rollback vs scripted endpoint monitor).
- **Built-in CloudWatch "hallucination rate" metric** — doesn't exist; derive from Guardrails / golden dataset / Logs Insights.
- **Retry `ValidationException` with backoff** / catch `ContextWindowOverflow` — most exam-critical: backoff is transient-only; neither applies.
- **Misattributing the regression gate to the WA Lens** — "fail build below threshold" is Prescriptive Guidance; the Lens owns the baseline discipline (GENOPS03-BP01).

---

## Decision triggers / mental models
- **Lifecycle order:** offline golden-dataset gate (CI/CD, fail-below-threshold) FIRST → shadow (no exposure) → canary (small slice, "is it safe?") → A/B (user metrics, "which is better?") → human approval. Online only validates what the gate cleared.
- **Reference exists?** → reference-based (BLEU/ROUGE/BERTScore/F1). **No reference?** → reference-free (LLM-judge / human). This is the *sole* criterion.
- **Eval method:** structured + labeled → automatic; subjective (tone/brand) → human; nuance at scale → LLM-judge.
- **Model vs RAG eval:** scoring a model alone → model evaluation; scoring a pipeline → RAG eval (retrieve-only = retriever; retrieve-and-generate = end-to-end).
- **RAG fault attribution:** low retrieval score → fix KB/chunking/embeddings; healthy retrieval + low generation → fix model/prompt/grounding.
- **Shadow vs canary vs A/B:** zero exposure → shadow; safe rollout w/ rollback → canary; pick the winner on outcomes → A/B.
- **Backoff or not:** transient (`ThrottlingException`, `ModelTimeoutException`, `ServiceUnavailableException`, `InternalServerException`, network) → backoff + jitter. Client (`ValidationException`, `AccessDeniedException`) → fix request/perms, never retry.
- **Hallucination signal:** RAG → `Builtin.Faithfulness`; runtime control → Guardrails contextual grounding check. No native CW hallucination metric — always *derived*.

---

## Hard numbers worth memorizing
- Human eval limits: **≤50 workers**, **≤1,000 prompts/job**, compare **≤2 inference sources**.
- Custom dataset: **JSONL in S3, ≤1,000 prompts**; keys `prompt` (required), `referenceResponse` + `category` (optional).
- Custom work team: **≤50 workers** via SageMaker Ground Truth; invite **≤50 emails** at a time.
- Robustness perturbs each prompt **~5×** with semantic-preserving noise; lower delta = more stable.
- RAG/judge metric scores normalized **0–1**. Judge built-in metrics = **11** (4 categories: quality, UX, instruction compliance, safety).
- KB retrieval metrics = **2 only** (context relevance, context coverage). KB generation metrics = **10**.
- Inline invocation-log body cap = **100 KB** (larger → S3 only).
- TPM/TPD burndown = `input tokens + max_tokens` (deducted up front).
- Guardrails contextual grounding threshold range **0–0.99**; use cases = summarization, paraphrasing, QA (NOT conversational QA).
- ThrottlingException = **HTTP 429**; RPM and TPM quotas enforced **concurrently**.
- *(point-in-time)* Prompt caching: AWS cites **up to ~85% latency / ~90% cost** reduction — marketing claim, not SLA.
- *(point-in-time)* LLM-judge cost: blog cites **up to ~98% savings** vs human — directional.
- *(point-in-time)* Automated Reasoning checks: **up to ~99% accuracy** — product-page claim.
- *(point-in-time)* RAG/KB eval + LLM-judge: preview re:Invent 2024 → **GA Apr 2025** (GA added BYOI + citation metrics).
- *(point-in-time)* CloudWatch GenAI observability: preview Jul 2025 → **GA Oct 2025**; latency-optimized inference still **preview**.
- *(point-in-time)* Evaluator-model families: **Nova, Claude, Llama, Mistral** (families durable; exact versions/Regions are snapshots — re-verify).
