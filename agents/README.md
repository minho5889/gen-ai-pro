# Study Agents — Socratic Tutor & Understanding Verifier

Two local agents built on the **Strands Agents SDK**, grounded in this repo's audited study
material, running entirely on a **locally served model via Ollama**. One teaches, one tests:

| Agent | Role | How it works |
|---|---|---|
| [socratic_tutor.py](socratic_tutor.py) | Your tutor | Teaches by questioning, never lecturing. Grounds every claim by searching and reading the repo's guides through tools, cites (file § section), and only explains after you've genuinely attempted. |
| [verifier.py](verifier.py) | Your understanding verifier | **mc mode:** drills the mock-exam bank — Python picks questions and scores answers deterministically against the audited keys (all-or-nothing multi-select, like the real exam), then the agent explains *why* from the analysis file and probes you with a follow-up. **explain mode:** free recall — you explain a Knowledge Check in your own words and the agent judges it against the guide's model answer. |

## Why Strands, and why a local model

**Strands** — three reasons. It's *model-driven*: you give it a model, a system prompt, and
`@tool`-decorated Python functions, and the SDK runs the reasoning loop — no orchestration
code, which keeps both agents under ~150 lines each. It's *provider-agnostic*: the same code
runs against Ollama today and Bedrock/AgentCore tomorrow by swapping one `model=` line. And
it's *exam-native*: Strands is itself AIP-C01 material (guide 04 §3) — building with it **is**
studying Task 2.1.

**Local model (Ollama)** — your study sessions, wrong answers, and confidence gaps stay on
your machine; unlimited drilling costs zero tokens; works offline. The honest tradeoffs:
small local models are weaker at tool-calling and have small context windows. The design
absorbs both — tools return one *section* at a time (never a 40k-word guide), and the
verifier keeps question-selection and scoring in deterministic Python, using the model only
for what LLMs are actually good at (explaining, probing, judging free-form answers).

## Setup

```bash
# 1. Install and start Ollama (https://ollama.com), then pull a tool-calling-capable model:
ollama pull qwen3:8b          # default; llama3.1:8b also works

# 2. Install the SDK (Python 3.10+):
pip install -r agents/requirements.txt
```

Configuration (env vars): `AIP_AGENT_MODEL` (default `qwen3:8b`), `OLLAMA_HOST`
(default `http://localhost:11434`). Bigger models (e.g. `qwen3:14b`) noticeably improve the
tutor's tool use; the verifier is robust even with small models because scoring never
depends on the model.

## Use

```bash
# Tutor — open-ended session, or jump straight to a topic:
python3 agents/socratic_tutor.py
python3 agents/socratic_tutor.py --topic "Bedrock Knowledge Bases chunking strategies"

# Verifier — multiple-choice drill (both exams, all domains):
python3 agents/verifier.py
python3 agents/verifier.py --domain 3 --exam 1     # D3 questions from Mock Exam 1 only
python3 agents/verifier.py --mode explain --guide 4  # free-recall on Agentic AI

# The loop: tutor a topic → drill it → the scorecard names your weakest domain
# → tutor that → re-drill.
```

Answer `q` mid-drill to stop and get a scorecard (overall, per-domain, weakest-domain
re-study pointer). For a full graded mock-exam sitting with the written report, use the
answer-sheet flow in the exam READMEs instead — this drill is for fast reps.

## Design notes

- **Grounding beats memory.** The tutor's system prompt forbids asserting AWS specifics
  without reading a guide section first — the local model's half-remembered AWS knowledge is
  exactly what we don't want teaching you. Content marked *(point-in-time)* gets called out.
- **Deterministic where it must be, model where it helps.** Mock-exam scoring is letter-set
  comparison in Python against keys the repo has already adversarially verified. No LLM
  grades your multiple-choice answers.
- **Fresh agent per question** in the verifier keeps the local context window small; the
  tutor keeps one conversation (Strands' sliding-window conversation manager handles length).
- Tool reads are locked to `guides/` and `_cram/` inside this repo.

## Troubleshooting

- `Connection refused` → Ollama isn't running (`ollama serve`) or wrong `OLLAMA_HOST`.
- Tutor answers without citing sections / ignores tools → model too weak for tool-calling;
  try `qwen3:14b` or `llama3.1:8b`, and keep questions specific.
- Slow first response → the model is loading into memory; subsequent turns are faster.
- Truncated or confused mid-session → context overflow on a small model; start a new session
  (tutor) or rely on per-question freshness (verifier, automatic).
