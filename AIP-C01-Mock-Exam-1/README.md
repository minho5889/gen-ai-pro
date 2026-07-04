# AIP-C01 Practice Exam 1

A full-length, domain-weighted mock exam for the AWS Certified Generative AI Developer – Professional
(AIP-C01) certification. Scenario-based, with multiple-response items, written to mirror the real
exam's style and traps. **Every answer key was fact-checked against current official AWS
documentation** during generation (2 keys were corrected in that pass), and a July 2026 independent
re-audit corrected two more items (Q29's explanation, Q49's question format) and refreshed stale
quota figures (Q16) — see the correction notes inside the affected analysis files.

## Contents

| File | Purpose |
|------|---------|
| `questions/AIP-C01-Mock-Exam-1-Questions.md` | The 65 questions (no answers). Sit the exam from this file. |
| `AIP-C01-Mock-Exam-1_AnswerSheet.md` | Blank answer sheet — record your pick, confidence, per-option reasoning, and what you were unsure about. |
| `analysis/AIP-C01_Q*-Q*_Analysis.md` | Full per-question analysis (bundled in 5s): option-by-option verdicts, correct-answer deep-dive, key takeaway. The source of truth for correct answers. |

## Exam composition (domain-weighted to the real blueprint)

| Domain | Weight | Questions |
|--------|--------|-----------|
| D1 — FM Integration, Data, Compliance | 31% | Q01–Q20 (20) |
| D2 — Implementation & Integration | 26% | Q21–Q37 (17) |
| D3 — AI Safety, Security, Governance | 20% | Q38–Q50 (13) |
| D4 — Operational Efficiency & Optimization | 12% | Q51–Q58 (8) |
| D5 — Testing, Validation, Troubleshooting | 11% | Q59–Q65 (7) |

65 scored questions total (the real exam adds 10 unscored). ~20% are multiple-response (Select TWO/THREE).
Passing score on the real exam is 750/1000 (compensatory — pass overall, not per-domain).

> **Format coverage:** the official exam guide defines four question types — multiple choice,
> multiple response, **ordering** (arrange 3–5 steps), and **matching** (pair items to 3–7 prompts).
> This drill uses only the first two; practice the other two formats with
> [`../AIP-C01-Format-Drills/`](../AIP-C01-Format-Drills/Ordering-Matching-Drills.md).

## How to take it

1. **Time-box it.** The real exam is 180 minutes for 65 scored + 10 unscored = 75 questions (~2.4 min/question). For this 65-question set, aim for ~150 minutes.
2. Answer from the questions file; fill in `AIP-C01-Mock-Exam-1_AnswerSheet.md` as you go (record confidence honestly — it powers the performance analysis).
3. Grade against the `analysis/` files.
4. **Analyze your results.** Ask Claude Code to grade your completed answer sheet against the `analysis/` files and write `analysis/AIP-C01_Performance_Analysis.md` — your score, incorrect-answer deep-dives, weak-topic drill-down, and study recommendations pointing back at the matching guides and cram sheets.

## Notes

- This is generated practice material, not real exam questions. It is grounded in the AIP study guides
  and verified against AWS docs, but always re-check fast-moving figures before relying on them.
- Want more reps? Ask Claude Code to generate "Practice Exam 2" the same way — fresh questions,
  same domain weighting and fact-check pass.
