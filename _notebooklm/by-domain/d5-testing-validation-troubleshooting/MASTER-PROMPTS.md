# Domain 5 — Testing, Validation & Troubleshooting (11%) · NotebookLM Master Prompts

**Notebook:** "AIP-C01 — D5 Testing/Validation/Troubleshooting." **Upload into it:** guide 06 (Testing, Evaluation & Troubleshooting), `cram-d5.md`, and the AIP-C01 blueprint.
**Study philosophy:** Recall first, then review. NotebookLM answers *only* from these sources and **cannot fact-check live AWS docs** — treat any version/quota/GA-date claim as a snapshot and confirm fast-movers (Bedrock quotas, AgentCore, latency-optimized inference, evaluator-model families/Regions) against real AWS docs + the fact-checked mock exams.

This domain is decided by a few crisp criteria, so the prompts below drill them directly: **reference exists? → reference-based vs reference-free**; **structured/subjective/at-scale → automatic vs human vs LLM-judge**; **retrieval vs generation fault split**; **shadow vs canary vs A/B lifecycle order**; **retryable vs non-retryable FM errors**; and the named "doesn't exist" distractors (`ContextWindowOverflow`, built-in CloudWatch "hallucination rate", "Answer relevance" KB metric, bring-your-own-judge).

---

## The Study Loop (run in order)

### Block 1 — Socratic Tutor (centerpiece, active recall)
**Feature / path:** Chat → Configure Chat → Style: **Custom** (paste below) → Length: Default. Then chat normally; use the **clickable citations** to verify every claim against the source.
**When:** Daily driver after a first read-through. Start here once you've skimmed guide 06.

```
You are my exam coach for AWS AIP-C01 Domain 5 (Testing, Validation & Troubleshooting). Use ONLY the uploaded sources and cite them with clickable citations.

Method:
- Quiz me ONE scenario-style question at a time, in the format of the real exam (a short design/troubleshooting scenario + 4 options). Then STOP and wait for my answer and my one-line justification BEFORE you reveal anything.
- After I answer: tell me right/wrong, then explain WHY the correct option is right AND why EACH distractor is wrong. Make me defend the choice.
- Prioritize these Domain-5 traps and decision points:
  1. Reference exists? -> reference-based (BLEU/ROUGE/BERTScore/F1); none -> reference-free (LLM-judge/human). This is the SOLE criterion.
  2. Traditional metrics (accuracy/precision/recall/F1) on open-ended generation = WRONG; use BERTScore (semantic) or LLM-judge. Paraphrase-correct answer -> BERTScore, NOT BLEU/ROUGE.
  3. "Accuracy" in Bedrock automatic eval is NOT one computation: RWK (general gen) / BERTScore (summarization) / NLP-F1 (Q&A) / binary (classification).
  4. Bring-your-own JUDGE model = impossible (judges are AWS-curated: Nova/Claude/Llama/Mistral). You bring RESPONSES (BYOI), not the judge.
  5. LLM-judge biases: position / verbosity / self-preference (judge favors its own family) -> calibrate with human spot checks for critical comparisons.
  6. RAG fault split: low Context relevance/coverage -> fix KB/chunking/embeddings; healthy retrieval + low Faithfulness -> fix model/prompt/grounding. KB retrieval metrics are only 2 (ContextRelevance=no ground truth, ContextCoverage=needs ground truth). "Answer relevance" KB metric DOESN'T exist -> Correctness.
  7. Deployment lifecycle ORDER: offline golden-dataset gate (fail-below-threshold, CI/CD) -> shadow (zero exposure) -> canary (1-5% + auto-rollback) -> A/B (user-outcome metrics) -> human approval.
  8. Canary DEPLOYMENT vs CloudWatch Synthetics canary (scripted monitor) — same word, unrelated. Bedrock does NOT split endpoint traffic (that's SageMaker ProductionVariants/ShadowProductionVariants).
  9. Errors: retry with backoff+jitter is TRANSIENT-only (ThrottlingException/ModelTimeout/ServiceUnavailable/InternalServer/network). NEVER retry ValidationException or AccessDeniedException. "ContextWindowOverflow exception" DOESN'T exist -> ValidationException + ThrottlingException.
  10. TPM burns down input + max_tokens up front -> early throttling fix = reduce max_tokens. No native CloudWatch "hallucination rate" metric -> derive (Guardrails contextual grounding / golden dataset / Logs Insights).
- If a fact may be time-sensitive (quotas, GA dates, evaluator families/Regions, latency-optimized inference status, exact metric counts), SAY SO explicitly and tell me to confirm against live AWS docs — you cannot verify those.
Begin with question 1. Do not reveal the answer until I respond.
```
**Why (learning science):** Active recall + elaborative interrogation ("why, and why-not-the-distractor") — retrieval before review is what builds durable, transferable memory.

---

### Block 2 — Quiz Generation (hardest distinctions)
**Feature / path:** Studio → Quiz → click the **pencil** (customize *before* generating) → Difficulty: **Hard** → Number: **More** → paste the Prompt below.
**When:** Day 2+, after a Socratic session. Re-take **"Only cards you missed"** on later days.

```
Generate hard, scenario-based questions for AWS AIP-C01 Domain 5. Make distractors plausible and target these specific confusions:
- accuracy/F1 on open-ended generation vs BERTScore vs LLM-judge; BLEU(precision/translation) vs ROUGE(recall/summarization) vs BERTScore(semantic); reference-based vs reference-free.
- Bedrock automatic "accuracy" changing by task type (RWK/BERTScore/NLP-F1/binary); built-in vs custom JSONL dataset; AWS-managed vs custom work team; CORS required for HUMAN jobs only.
- RAG retrieve-only vs retrieve-and-generate; ContextRelevance(no GT) vs ContextCoverage(needs GT) vs Faithfulness; "Answer relevance" doesn't exist; BYOI for non-Bedrock systems.
- LLM-judge bias (position/verbosity/self-preference); judge models are AWS-curated (no BYO judge); generator vs evaluator roles.
- golden dataset regression gate (Prescriptive Guidance, not WA Lens); GENOPS03-BP01 baseline; SageMaker Model Monitor for drift.
- shadow vs canary vs A/B; canary deployment vs CloudWatch Synthetics canary; SageMaker (not Bedrock) splits endpoint traffic.
- retryable (ThrottlingException 429, ModelTimeout, ServiceUnavailable, InternalServer) vs non-retryable (ValidationException, AccessDenied); ContextWindowOverflow doesn't exist; reduce max_tokens for early TPM throttle.
- observability: Model Invocation Logging (off by default, bedrock-runtime only, 100KB inline cap->S3); InvocationLatency vs TimeToFirstToken(streaming only); no native hallucination metric.
Use only the uploaded sources. Add an Explain on each answer.
```
**Why (learning science):** Spaced repetition (re-run only-missed across days) + interleaving (mix subtopics in one set) beats massed single-topic blocks.

---

### Block 3 — Flashcards (memorizable triggers)
**Feature / path:** Studio → Flashcards → **pencil** → Difficulty: Medium → paste Prompt → generate. Mark **Got it! / Missed it!**, then **Export CSV → import to Anki** for long-run spacing.
**When:** Day 1-2 to lock the trigger→answer pairs; review only-missed thereafter.

```
Create flashcards for AWS AIP-C01 Domain 5 as trigger -> answer pairs (front = the exam cue, back = answer + 1-line why). Cover:
- "no reference answer" -> reference-free (LLM-judge/human); "paraphrase differs from reference" -> BERTScore.
- "score thousands nightly cheaply" -> automatic/LLM-judge (humans <=50 workers, <=1000 prompts/job).
- "friendliness/brand voice" -> human eval.
- "are we retrieving right chunks" -> ContextRelevance (no GT); "did we retrieve all needed info" -> ContextCoverage (needs GT); "invents facts not in sources" -> Faithfulness.
- "validate under real traffic, zero user impact" -> shadow; "small % + auto-rollback" -> canary; "which prompt users prefer" -> A/B.
- "input too long / premature TPM throttle" -> ValidationException + reduce max_tokens (burns input+max_tokens up front).
- "ThrottlingException 429" -> backoff+jitter (transient); "ValidationException/AccessDenied" -> NEVER retry, fix request/perms.
- "capture exact prompt+response" -> Model Invocation Logging (off by default); "time to first token" -> TimeToFirstToken (streaming only).
- "fail build below threshold" -> regression quality gate (Prescriptive Guidance); "baseline-before-change" -> GENOPS03-BP01.
Hard numbers to drill: humans <=50 workers/<=1000 prompts/<=2 sources; custom JSONL <=1000 prompts; KB retrieval metrics = 2; judge built-ins = 11; inline log cap = 100KB. Use only uploaded sources.
```
**Why (learning science):** Active recall on atomic facts; CSV→Anki gives a true spaced-repetition engine beyond the session.

---

### Block 4 — Audio Overview (passive / dual-coding)
**Feature / path:** Studio → Audio Overview → choose format → **Add a prompt** (below). Use **Interactive mode** (Beta, tap Join) to ask follow-ups mid-playback.
- **First pass:** Format **Deep Dive** — focus prompt below.
- **Contested design choices:** Format **The Debate** — for genuinely two-sided calls (RAG-grounding vs Guardrails for hallucination control; LLM-judge-at-scale vs human spot checks; managed Bedrock Evaluations vs hand-rolled harness).

```
Focus this overview on AWS AIP-C01 Domain 5 decision rules, at an exam-ready level: (1) reference-based vs reference-free metric choice and why traditional accuracy/F1 fails on open-ended generation; (2) Bedrock Model vs RAG vs Agent evaluations and when each is used; (3) LLM-as-a-judge — value, the three biases (position/verbosity/self-preference), and why human spot checks remain; (4) the deployment validation lifecycle order: offline golden-dataset gate -> shadow -> canary -> A/B; (5) troubleshooting: retryable vs non-retryable FM API errors, context-window overflow, and why ContextWindowOverflow is not a real exception. Call out any fact that is time-sensitive and remind me to verify it against live AWS docs.
```
**Why (learning science):** Dual coding — pairing a verbal/audio channel with the visual/structural ones reinforces memory through two routes; Debate format builds transfer by forcing both sides of a tradeoff.

---

### Block 5 — Mind Map + Study Guide (structure / dual-coding)
**Feature / path:** Studio → **Mind Map** (visual node graph) and Studio → **Study Guide** (study-focused doc).
**When:** Early, to see the domain's skeleton; revisit before the exam as a fast structural review.
**How to use:** Walk the Mind Map's branches as the domain's decision trees — *Metric choice* (reference? → method), *Eval service* (model/RAG/agent), *Validation lifecycle* (gate→shadow→canary→A/B), *Troubleshooting* (error class → fix). For anything ambiguous, ask Chat:

```
From the sources, lay out Domain 5 as 4 decision trees with the exact branch conditions: (a) metric selection (reference availability, then task type), (b) eval method (structured/subjective/at-scale -> automatic/human/LLM-judge), (c) deployment validation order (offline gate -> shadow -> canary -> A/B, with the signal each uses), (d) FM error triage (retryable vs non-retryable, with the named exceptions). Cite each branch.
```
**Why (learning science):** Dual coding + chunking — a visual map of how the rules relate is recalled faster under time pressure than a flat list.

---

### Block 6 — Transfer Drill (application, not recall)
**Feature / path:** Chat (Custom or Default). Run after you can pass Blocks 1-3.
**When:** Day 7+ and in the final days — this mirrors the real scenario/design-based exam.

```
Invent a NOVEL Domain-5 scenario I have not seen, drawn only from the sources (e.g., a RAG support bot returning fluent-but-unsupported answers under rising latency, or a nightly eval that must gate a CI/CD release). Give me a realistic design/troubleshooting question with 4 options. WAIT for my answer + my reasoning. Then grade me: state the correct option, explain why, dissect each distractor, and tell me which decision rule I should have applied (e.g. retrieval-vs-generation fault split, retryable-vs-non-retryable, lifecycle order). After grading, ask my CONFIDENCE (1-5) and note whether it matched correctness. Flag any time-sensitive fact I should verify against live AWS docs.
```
**Why (learning science):** Transfer — applying a rule to a new scenario (not a memorized one) + calibration (confidence vs correctness) reveals what you only *think* you know.

---

## Spaced Schedule (suggested)
- **Day 1:** Read guide 06 → Block 5 (Mind Map/Study Guide) → Block 4 Deep Dive audio.
- **Day 2:** Block 1 (Socratic) → generate Block 2 quiz + Block 3 flashcards.
- **Day 4:** Re-take **"Only cards you missed"** (quiz + flashcards) → one Block 1 session on weak traps.
- **Day 7:** Block 6 transfer drill → Block 4 **The Debate** on a contested tradeoff → re-run only-missed.
- **Pre-exam:** Mind Map skim + transfer drill + only-missed.

---

> **Caveat:** NotebookLM cannot fact-check against live AWS docs and these UI labels shift — adapt paths if a label differs, and treat all quotas/GA-dates/version claims as snapshots. Pair this with the **fact-checked Mock Exams** for exam-representative practice.
