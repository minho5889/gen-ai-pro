# Domain 3 — AI Safety, Security & Governance — NotebookLM Master Prompts

**Notebook:** D3 (20% of AIP-C01). **Upload the contents of `_UPLOAD-THIS-FOLDER.md`:** guide `03-AI-Safety-Security-Governance.md` + `cram-d3.md` + `AIP-C01-Exam-Blueprint.md`.
**Study philosophy:** Recall first, review second — and *confirm fast-moving facts elsewhere*. NotebookLM only knows your sources and **cannot fact-check live AWS docs**, so treat point-in-time facts (Bedrock quotas, Comprehend prompt-safety sunset, Audit Manager framework status, compliance scope) as suspect and verify against AWS docs + the fact-checked Mock Exams.

This domain's spine: **defense-in-depth** (Layer 1 input → Layer 2 model controls → Layer 3 output verification; Guardrails spans all three) and **"no single control is ever the answer."** The prompts below drill *that*, plus the named distractors below.

---

## The study loop (run in order)

### Block 1 — Socratic tutor (the centerpiece)

**Feature + path:** Chat → Configure Chat → Style: **Custom** (paste below) → set Length: Default. Then chat one scenario at a time.

```
You are my exam coach for AWS AIP-C01 Domain 3 (AI Safety, Security & Governance). Use ONLY the uploaded sources. Teach by active recall and elaborative interrogation — never lecture first.

LOOP, one scenario at a time:
1. Pose ONE realistic, scenario/design-style question (like the real exam — applied, not "define X"). Give 4 plausible options.
2. STOP. Make me answer AND justify before you reveal anything. Do not show the answer until I respond.
3. After I answer: tell me right/wrong, give the correct choice, and for EVERY distractor explain specifically why it is wrong (not just why the right one is right).
4. Add clickable citations to the source location for each claim.
5. If any fact is point-in-time or version/quota-specific (Bedrock limits, Comprehend prompt-safety sunset Apr 30 2026, Audit Manager GenAI Framework v2 status, compliance certifications), flag it: "verify against live AWS docs — I can't." If the sources don't cover it, say so rather than guessing.
6. Ask me to rate my confidence 1-5, and track it vs. whether I was right.

Deliberately drill THESE D3 traps — rotate through them:
- Filter-strength INVERSION: HIGH = most aggressive (blocks down to LOW confidence), LOW = least. "Low sounds safer" is the trap.
- "Guardrails alone covers RAG" — FALSE: Guardrails do NOT scrub retrieved chunks or source corpus (where indirect injection + source PII live). Safest RAG screens at 3 points: pre-ingestion, retrieved chunks, final answer.
- Input-filtering-alone vs output-check-alone — each is blind where the other sees; defense-in-depth needs both.
- MASK/anonymize exists ONLY on the sensitive-info (PII) filter; "Block a specific word/competitor name" = Word filter, NOT Denied topics (which = themes).
- Contextual grounding: invented facts = grounding score; answers-wrong-question = relevance score. Higher threshold = stricter. Output-only; NOT free-form chat.
- CloudTrail does NOT contain prompt/response content (responseElements null) — content lives in Model Invocation Logging (off by default). Blocked content is still plaintext in those logs.
- Data events (InvokeAgent / Retrieve / RetrieveAndGenerate / InvokeFlow) are OFF by default; mgmt events on by default.
- Base-model "we don't train on your data" guarantee does NOT cover your fine-tune — it can memorize and replay training-set PII. Redact before customization.
- 8 Responsible AI dimensions (veracity-and-robustness is ONE combined dim; 9 is the trap).
- AI Service Card = AWS authors, you READ. Model Card = YOU write (immutable versions, Model Registry).
- Pin a guardrail version via IAM condition key bedrock:GuardrailIdentifier with :N — NOT a versionless resource ARN (which covers all versions). Reusing the enforcement role for RetrieveAndGenerate/InvokeAgent BREAKS (ungoverned internal InvokeModel) — separate roles.
- Express Step Functions has NO human-approval step → use Standard for human-in-the-loop.
- Bedrock uses INTERFACE VPC endpoints (PrivateLink); gateway endpoints are only S3/DynamoDB.
- Prove an image is AI-generated = watermark detection (DetectGeneratedContent); Titan watermark can't be disabled.
- Glue Data Catalog STORES metadata; it does NOT visualize lineage (that's DataZone / SageMaker Catalog via OpenLineage).
- 3rd-party vector store/connector (Pinecone/Redis/SaaS) → Secrets Manager; first-party (OpenSearch Serverless/Aurora/S3) → IAM.
- Control plane (bedrock / bedrock-agent: CreateGuardrail, PutModelInvocationLoggingConfiguration) vs data plane (bedrock-runtime / bedrock-agent-runtime: InvokeModel/Converse). Converse rides on bedrock:InvokeModel.

Start now with scenario 1. Wait for my answer.
```

**Why (learning science):** Active recall + elaborative interrogation — retrieving and defending *before* the reveal, and forcing "why not the distractor," builds the discrimination the scenario-based exam tests. Calibration (confidence vs. correctness) exposes what you only *think* you know.
**When:** Daily core driver, after a first read of guide 03.

---

### Block 2 — Quiz generation (hardest distinctions)

**Feature + path:** Studio → Quiz → click the **pencil** to customize BEFORE generating → Difficulty: **Hard**, Number: **More**.

```
Generate a HARD quiz for AWS AIP-C01 Domain 3. Make every question applied/scenario-style with closely-confusable distractors that exploit these exact confusions:
- HIGH vs LOW filter strength (inversion); NONE/LOW/MEDIUM/HIGH meaning.
- Which Guardrail policy fits: Content filters vs Denied topics vs Word filter vs Sensitive-info (Block vs Mask) vs Contextual grounding (grounding score vs relevance score) vs Automated Reasoning.
- Comprehend (data layer: corpus/S3/chunks, EN+ES) vs Macie (S3 discovery, no redact) vs Guardrails PII (inline at model boundary) vs Comprehend DetectPii vs ContainsPii vs StartPiiEntitiesDetectionJob vs S3 Object Lambda.
- Governance trio: Model Invocation Logging (content) vs CloudTrail (who/when, no content, data events off by default) vs CloudWatch (InvocationsIntervened metric).
- IAM: control vs data plane; bedrock:GuardrailIdentifier :N pinning; interface VPC endpoint (PrivateLink) vs gateway; Secrets Manager vs IAM for connectors/vector stores.
- Responsible AI: 8 dimensions; Clarify (pre-deploy assessment, pre- vs post-training bias metrics, SHAP) vs Guardrails (runtime); AI Service Card (read) vs Model Card (write); DetectGeneratedContent for provenance.
- Defense-in-depth: reject any "single control is enough" framing.
Include a Hint per question and an Explain on each answer that says why each wrong option is wrong. Flag any point-in-time fact as "verify against live AWS docs."
```
After taking it, mark misses and on later days retake **"Only cards you missed."**

**Why (learning science):** Active recall under exam-like discrimination; "Only cards you missed" is your **spaced-repetition** lever across days.
**When:** Day 2+, after Block 1's first pass.

---

### Block 3 — Flashcards (memorizable triggers)

**Feature + path:** Studio → Flashcards → **pencil** → Difficulty: Medium-Hard, Number: More → generate → mark **Got it! / Missed it!** → **Export CSV** into Anki.

```
Create flashcards for AWS AIP-C01 Domain 3 focused on trigger→answer recall and hard numbers. Cards should be "Exam says X → Answer Y (one-line why)". Cover:
- Filter strength: NONE/LOW/MEDIUM/HIGH and which is most aggressive.
- 6 Guardrail policy types and the 6 content-filter categories (Hate/Insults/Sexual/Violence/Misconduct/Prompt Attack).
- Block vs Mask (Mask only on PII filter); Denied topics vs Word filter.
- Grounding score vs relevance score; contextual grounding is output-only, not free-form chat.
- ApplyGuardrail API (screen text, no FM call) vs InvokeModel-with-guardrail.
- Comprehend DetectPii vs ContainsPii vs StartPiiEntitiesDetectionJob vs DetectToxicContent vs DetectGeneratedContent.
- Macie vs Comprehend vs Guardrails PII (where each operates).
- CMK vs AWS-owned key (control/audit/revoke → CMK).
- Model Invocation Logging vs CloudTrail (no content; data events off by default) vs CloudWatch InvocationsIntervened.
- Control plane vs data plane; bedrock:InvokeModel for Converse; GuardrailIdentifier :N pinning; interface endpoint (PrivateLink); Secrets Manager vs IAM connectors.
- 8 RAI dimensions; AI Service Card (read) vs Model Card (write); Clarify pre- vs post-training metrics + SHAP.
- Hard numbers: denied topics ≤30, ≤5 phrases; word list ≤10,000 entries ≤3 words; grounding threshold 0–0.99; Automated Reasoning ≤99% / ≤122,880 tokens / EN-US; Macie score −1 to 100; model risk = unknown/low/medium/high; logging inline body ≤100KB; TLS 1.2.
Keep answers terse. Tag point-in-time facts (e.g., Comprehend prompt-safety sunset, Audit Manager framework status) so I verify them against live AWS docs.
```

**Why (learning science):** Spaced repetition on atomic triggers; CSV→Anki extends spacing beyond a session and offloads the rote layer so chat time goes to reasoning.
**When:** Day 1 build; review across the week.

---

### Block 4 — Audio Overview (passive review + contested choices)

**Feature + path:** Studio → Audio Overview → format **Deep Dive** for first pass (then **The Debate** for design tensions) → **Add a prompt** (below) → Length: Default. Use **Interactive mode** (Beta) to tap Join and ask follow-ups mid-playback.

First-pass focus prompt (Deep Dive):
```
Walk through Domain 3 as defense-in-depth: Layer 1 input filtering → Layer 2 model controls (Guardrails policies) → Layer 3 output verification. Emphasize that Guardrails spans all three and that no single control is ever the full answer. Hit the filter-strength inversion (HIGH = most aggressive), the six Guardrail policy types, the Comprehend-vs-Macie-vs-Guardrails-PII split, and the governance trio (Model Invocation Logging vs CloudTrail vs CloudWatch). Set an expert/exam-prep expertise level.
```
Then switch to **The Debate** for genuinely contested design choices:
```
Debate the contested design calls in Domain 3 where exam takers pick wrong: Guardrails ALONE vs a Step Functions + Lambda workflow (when do you need orchestration / human approval?); Standard vs Express Step Functions for human-in-the-loop; managed Guardrails PII vs hand-rolled Comprehend pipelines for where PII lives; and Guardrails-only vs 3-point RAG screening. Have the hosts argue each side, then converge on the exam-correct rule.
```

**Why (learning science):** Dual coding (verbal channel alongside the visual/structural ones below); The Debate format builds **transfer** by exposing the trade-off reasoning behind contested calls, not just the verdict.
**When:** Commute/passive slots — Deep Dive Day 1, Debate later in the week.

---

### Block 5 — Mind Map + Study Guide (dual coding / structure)

**Feature + path:** Studio → **Mind Map** (visual node graph of the sources) and Studio → **Study Guide**.
Use the Mind Map to *see* the structure: the three defense layers, the six Guardrail policy types branching off Layer 2, the data-layer trio (Macie/Comprehend/KMS), the access-control split (control vs data plane), and the governance trio. Expand nodes you can't yet explain out loud, then go back to Block 1 on those.

```
Generate a Study Guide for Domain 3 organized as decision trees: (1) which Guardrail policy for a given requirement; (2) where PII lives → which service (Macie/Comprehend/Guardrails/KMS); (3) which governance service answers "what was said / who did what / how it behaves"; (4) control vs data plane IAM; (5) the 3-point RAG screening pipeline. End with a table of the named D3 distractor traps and the one-line rule that defeats each.
```

**Why (learning science):** Dual coding — pairing the verbal material with a spatial/structural map strengthens retrieval cues; "explain the node out loud" is a built-in recall check.
**When:** Day 1–2 to build the scaffold; revisit when a sub-area feels fuzzy.

---

### Block 6 — Transfer drill (novel scenarios, you defend + get graded)

**Feature + path:** Chat (keep the Block 1 Custom style, or paste below as a one-off message).

```
Invent a NEW, realistic Domain 3 design scenario I haven't seen — multi-requirement, like the real exam (e.g., "a regulated healthcare RAG app needs PII handled at every stage, an auditable safety trail, and a guardrail enforced on every call"). Give 4 options. Do NOT reveal the answer. After I commit to a choice AND justify the architecture, grade me: what I got right, what I missed, and why each rejected option fails. Then push one level harder: change one constraint (e.g., now it must also stay in-region, or roll back a guardrail safely, or screen an ingested doc for indirect injection) and ask me to adapt. Cite sources, and flag any point-in-time fact as "verify against live AWS docs."
```

**Why (learning science):** Transfer + interleaving — applying rules to *novel* multi-constraint scenarios (and adapting when a constraint changes) is exactly what the design-based exam scores, far beyond recall.
**When:** Day 4 onward, once recall is solid.

---

## Spaced schedule

- **Day 1:** Read guide 03 → Block 5 (Mind Map/Study Guide) → Block 4 Deep Dive audio → build Block 3 flashcards.
- **Day 2:** Block 1 Socratic tutor (1 session) → Block 2 Hard quiz; mark misses.
- **Day 4:** Retake Block 2 **"Only cards you missed"** → Anki review → Block 4 **The Debate**.
- **Day 7:** Block 6 transfer drills → re-run Block 1 only on the traps you still miss.
- Re-loop weakest traps every few days.

---

## Caveat

NotebookLM answers only from your uploaded sources, **cannot fact-check against live AWS docs**, and does not generate architecture diagrams (use the Mind Map / the guide's own descriptions). These exact UI labels move fast — adapt if a label differs. Point-in-time facts (Bedrock quotas, Comprehend prompt-safety sunset, Audit Manager framework status, compliance scope) and exam-representative practice belong to the **fact-checked Mock Exams** — pair them with this notebook.
