# AIP-C01 Practice Exam 2

A second full-length, domain-weighted mock exam for the AWS Certified Generative AI Developer –
Professional (AIP-C01) certification. **Distinct from Practice Exam 1** — the item writers were given
Exam 1's question stems as a do-not-repeat list and instructed to cover different services, edge
cases, and angles within the same tasks. Scenario-based, with multiple-response items. **Every answer
key was fact-checked against current official AWS documentation** during generation (0 keys needed
correction that run). A July 2026 independent re-audit kept every credited answer but refreshed
supporting details that had gone stale — Q3/Q26 (custom-model on-demand deployment now exists),
Q19 (ingestion quota figures), two Select-TWO/THREE header mismatches (Q19, Q57), and the
multi-select option tables — see the correction notes inside the affected analysis files.

## Contents

| File | Purpose |
|------|---------|
| `questions/AIP-C01-Mock-Exam-2-Questions.md` | The 65 questions (no answers). |
| `AIP-C01-Mock-Exam-2_AnswerSheet.md` | Blank answer sheet. |
| `analysis/AIP-C01_Q*-Q*_Analysis.md` | Full per-question analysis (bundled in 5s). Source of truth for correct answers. |

## Exam composition (same blueprint weighting as Exam 1)

| Domain | Weight | Questions |
|--------|--------|-----------|
| D1 — FM Integration, Data, Compliance | 31% | Q01–Q20 (20) |
| D2 — Implementation & Integration | 26% | Q21–Q37 (17) |
| D3 — AI Safety, Security, Governance | 20% | Q38–Q50 (13) |
| D4 — Operational Efficiency & Optimization | 12% | Q51–Q58 (8) |
| D5 — Testing, Validation, Troubleshooting | 11% | Q59–Q65 (7) |

65 scored questions, 12 multiple-response (Select TWO/THREE). Passing score on the real exam is 750/1000.

> **Format coverage:** the official exam guide defines four question types — multiple choice,
> multiple response, **ordering** (arrange 3–5 steps), and **matching** (pair items to 3–7 prompts).
> This drill uses only the first two; practice the other two formats with
> [`../AIP-C01-Format-Drills/`](../AIP-C01-Format-Drills/Ordering-Matching-Drills.md).

## How to take it

1. Time-box ~150 minutes for 65 questions (the real exam is 180 min for 75).
2. Answer from the questions file; fill in `AIP-C01-Mock-Exam-2_AnswerSheet.md` (record confidence honestly).
3. Grade against the `analysis/` files.
4. Ask Claude Code to grade your completed answer sheet against the `analysis/` files and write
   `analysis/AIP-C01_Performance_Analysis.md` — score, incorrect-answer deep-dives, weak-topic
   drill-down, and study recommendations.

## Notes

- Generated practice material, not real exam questions — grounded in the AIP guides and verified
  against AWS docs. Re-check fast-moving figures before relying on them.
- Take Exam 1 and Exam 2 on different days; compare your performance-analysis weak topics across both
  to find persistent gaps. Want more? Ask Claude Code for "Practice Exam 3."
