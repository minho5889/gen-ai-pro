# How to Study for AIP-C01 with NotebookLM

This is the top-level guide that ties together the 5 per-domain NotebookLM playbooks into one study system. Read this first, then work each domain.

## The overall approach

- **One notebook per domain.** The folder `_notebooklm/by-domain/` has 5 folders (`d1`..`d5`). Each is its own NotebookLM notebook. Upload the contents of a folder (see its `_UPLOAD-THIS-FOLDER.md`), then open that folder's `MASTER-PROMPTS.md` and copy prompts straight into NotebookLM.
- **Three tools, three jobs.** Use the right one for the right purpose:
  - **NotebookLM** = recall, understanding, and synthesis. It is your daily active-recall and Socratic-tutor engine.
  - **The Mock Exams** (`AIP/AIP-C01-Mock-Exam-1` and `AIP/AIP-C01-Mock-Exam-2`) = exam-representative, fact-checked practice. These are the ground truth for "am I exam-ready?"
  - **Live AWS docs + Claude Code** = confirming fast-moving facts (Bedrock quotas, AgentCore, model names/limits, new features).
- **Critical truth: NotebookLM cannot fact-check itself.** It answers ONLY from the sources you uploaded and CANNOT check against live AWS docs. It can confidently restate an outdated or wrong detail from a guide. So you must (a) prompt it to flag uncertainty, and (b) confirm any volatile fact against real AWS docs or the mock exams before you trust it. It also does NOT generate architecture diagrams from content — structure comes from the **Mind Map** and from the decision trees written into the guides themselves.

## Recommended order across domains

Sequence by exam weight and dependency. D1 and D2 are the foundation (57% of the exam combined and prerequisite vocabulary for everything else), so they come first.

| Order | Domain | Weight | Why here | Rough time |
|---|---|---|---|---|
| 1 | **D1** | 31% | Largest slice; foundational concepts everything builds on | ~1 week |
| 2 | **D2** | 26% | Second largest; builds directly on D1 | ~1 week |
| 3 | **D3** | 20% | Applies D1/D2 to real workloads | ~4-5 days |
| 4 | **D4** | 12% | Narrower; depends on prior domains | ~3 days |
| 5 | **D5** | 11% | Smallest; finish here | ~2-3 days |

After all five, spend a final week on **interleaved review across all domains + both mock exams**. Total: roughly 4-5 weeks at a steady pace; compress or stretch to fit your timeline.

## Weekly cadence template (per domain)

Each step names the learning-science reason so you build the *why*, not just the routine. Interleave subtopics within the domain rather than blocking one at a time.

- **Day 1 — Encode + structure.** Generate the **Mind Map** and listen to an **Audio Deep Dive** while reading the guide. *Dual coding:* pairing visual structure with verbal explanation builds two retrieval routes.
- **Day 2 — First retrieval.** Generate a **Quiz** (medium) and a **Flashcard** set. Answer *before* reading the source. *Active recall:* retrieval beats re-reading. Mark "Missed it!" honestly.
- **Day 3 — Understand the misses.** Open a **Custom Socratic Chat** (see below) and have it interrogate every concept you missed. Ask "why?" and "why NOT the distractor?" *Elaborative interrogation:* forcing explanations turns shallow facts into durable understanding.
- **Day 4 — Interleave.** Mix question types: retake quiz, do a few flashcards, ask 2-3 chat questions, and **Save to note** the best answers. *Interleaving:* mixing tasks within the domain improves discrimination between similar concepts.
- **Day 5+ (spaced) — Only-missed + transfer.** Retake **"Only cards you missed"** a few days later (*spaced repetition*: re-exposure at intervals fights forgetting). Then run a **scenario-defense drill**: ask the chat for a NOVEL scenario, commit to an answer, defend it, and have it grade you. Use **Audio Debate** for any design choice with real trade-offs. *Transfer:* AIP-C01 is scenario/design-based, so practice applying rules to new situations, not reciting them.
- **Throughout — Calibrate.** Before each quiz answer, note how confident you are; compare to whether you got it right. *Calibration:* this exposes what you only *think* you know.

### The Custom Socratic Chat persona

In **Configure Chat → Style → Custom**, paste something like:

> You are a Socratic AIP-C01 tutor. Ask me one question at a time, wait for my answer, then probe with "why?" and "why not the other option?". Use clickable citations to the source. If a fact may be outdated or you are unsure, say so explicitly and tell me to confirm it against live AWS docs.

## Which feature for which goal

| Goal | Feature |
|---|---|
| Active recall | **Quiz** + **Flashcards** (answer before reviewing) |
| Deep understanding | **Custom Socratic Chat** (elaborative interrogation) |
| Passive review / dual coding | **Audio Deep Dive** (or "The Brief" for a quick pass) |
| Contested design choices / trade-offs | **Audio Debate** |
| Seeing structure | **Mind Map** |
| Transfer to novel problems | **Scenario-defense drill** in chat ("give me a new scenario and grade my answer") |
| Calibration | **Confidence tracking** (rate confidence, compare to correctness) |
| Spaced repetition | **Flashcards → "Only cards you missed"**, revisited across days (export CSV to Anki if you want) |

## Build transferable study skills

The habits here outlast this exam and apply to any future cert or technical topic:

- **Retrieve before review** — always try to recall first; struggling to retrieve is what builds memory.
- **Defend your answer** — explaining *why*, and why the alternative is wrong, is the difference between recognition and real understanding.
- **Confirm, don't trust** — treat any single AI source as a draft. Cross-check volatile facts against authoritative docs. This is the single most valuable habit for fast-moving AI/cloud topics.

## Caveats

- **UI labels shift.** NotebookLM's exact menu names (Style, Length, format names) change often — adapt if a label differs from what's described here.
- **Confirm volatile facts elsewhere.** Bedrock quotas, AgentCore details, model names/limits, and any "newest feature" claim must be verified against live AWS docs and the mock exams, not NotebookLM.
