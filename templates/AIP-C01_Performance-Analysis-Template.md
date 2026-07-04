# AIP-C01 Performance Analysis — Output Template

The spec for grading a completed mock-exam answer sheet. When asked to "grade my answer sheet,"
produce `analysis/AIP-C01_Performance_Analysis.md` inside the exam folder, following this structure
exactly — consistent structure is what makes attempts comparable across Exam 1, Exam 2, and retakes.

**Inputs:** the filled `*_AnswerSheet.md` (answers + per-question confidence) and the exam's
`analysis/` files (source of truth for correct answers).
**Scoring:** 1 point per fully-correct question — multiple-response questions score all-or-nothing
(exactly the credited letters, no partial credit), matching the real exam. Report percentages to one
decimal.

---

## 1. Score summary

| Metric | Value |
|---|---|
| Raw score | N / 65 (NN.N%) |
| Scaled estimate* | ~NNN / 1000 |
| Pass line | 750 (≈ 48-49 / 65 raw, varies by form) |
| Verdict | PASS-TRACK / BORDERLINE / NOT YET |

*Linear approximation: `100 + (raw/65) × 900`. The real exam equates scores per form; treat this as
a rough gauge only.

## 2. Per-domain breakdown

| Domain | Questions | Correct | % | Exam weight | Weighted drag |
|---|---|---|---|---|---|
| D1 — FM Integration, Data, Compliance | Q01–Q20 | n/20 | | 31% | |
| D2 — Implementation & Integration | Q21–Q37 | n/17 | | 26% | |
| D3 — Safety, Security, Governance | Q38–Q50 | n/13 | | 20% | |
| D4 — Operational Efficiency | Q51–Q58 | n/8 | | 12% | |
| D5 — Testing, Validation, Troubleshooting | Q59–Q65 | n/7 | | 11% | |

"Weighted drag" = (1 − domain %) × exam weight — sorts where lost points cost the most.

## 3. Incorrect-answer review

One entry per missed question, hardest-hit domains first:

### Qnn — [one-line topic] (Domain n, Task n.n)
- **Your answer:** X (confidence: high/med/low) · **Correct:** Y
- **Why Y wins / why X fails:** 2-3 sentences, from the analysis file's option verdicts.
- **Re-study:** [guide-file § section] · [cram-dN row/anchor]

## 4. Confidence calibration

| | Correct | Incorrect |
|---|---|---|
| High confidence | n (well-calibrated) | n ← **priority: confidently wrong** |
| Medium | n | n |
| Low confidence | n (lucky or under-confident) | n (known gaps) |

List every high-confidence-incorrect question number — those are mislearned facts, not gaps, and they
cost the most on exam day.

## 5. Weak-topic rollup

Group misses by exam-guide Task (not by question). For each task with ≥2 misses: task id, what the
misses have in common, and the single guide section + cram row that covers it.

## 6. Recommendations (ordered)

1. Re-study list in priority order: weighted drag × miss count, confidently-wrong topics first.
2. Which cram sheets to re-skim the night before.
3. Whether to sit the other mock exam now or after re-study (borderline → re-study first).
4. If ordering/matching fluency was shaky, point at `AIP-C01-Format-Drills/`.
5. Standing reminder: re-verify point-in-time facts in `VERIFICATION-LOG.md` near exam day.
