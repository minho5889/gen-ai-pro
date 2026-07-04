#!/usr/bin/env python3
"""Understanding-verifier agent for AIP-C01, on Strands + a local Ollama model.

Two modes:
  mc       Drill the repo's mock-exam questions. Python (not the model) picks
           questions and scores answers deterministically against the audited
           answer keys — all-or-nothing on multi-select, like the real exam.
           The agent then does what an LLM is good at: explain WHY from the
           analysis file and probe you with one follow-up.
  explain  Free recall. You get a Knowledge Check question from a guide and
           answer in your own words; the agent judges your explanation against
           the guide's model answer (LLM-as-a-judge, verdict + gaps).

Usage:
    python3 agents/verifier.py                     # mc mode, both exams, all domains
    python3 agents/verifier.py --domain 3 --exam 1
    python3 agents/verifier.py --mode explain --guide 4
Type 'q' as an answer to stop and see your scorecard.
"""
import argparse
import random
import re
from pathlib import Path

from strands import Agent

from common import GUIDE_MAP, GUIDES_DIR, REPO_ROOT, local_model

DOMAIN_RANGES = {1: (1, 20), 2: (21, 37), 3: (38, 50), 4: (51, 58), 5: (59, 65)}
DOMAIN_NAMES = {
    1: "FM Integration, Data, Compliance",
    2: "Implementation & Integration",
    3: "Safety, Security, Governance",
    4: "Operational Efficiency",
    5: "Testing, Validation, Troubleshooting",
}

FEEDBACK_PROMPT = """\
You are an exam-understanding verifier. You are given a mock-exam question, the
student's answer, the credited answer, and the official analysis (ground truth).
Reply in two parts, under 110 words total, plain prose:
1. WHY: in 2-3 sentences, why the credited answer wins — and if the student was
   wrong, name the specific misconception their choice implies.
2. PROBE: end with exactly one short follow-up question testing whether they
   understand why one specific OTHER option fails. Never reveal that answer.
"""

JUDGE_PROMPT = """\
You are a strict but fair examiner. Compare the student's free-form explanation
against the model answer (ground truth). Reply under 90 words:
- Verdict: CORRECT, PARTIAL, or INCORRECT
- What was right, what was missing or wrong (be specific, from the ground truth)
- One sentence of what to re-study.
Do not invent facts beyond the ground truth.
"""


def parse_exam(exam_no: str):
    folder = REPO_ROOT / f"AIP-C01-Mock-Exam-{exam_no}"
    qtext = (folder / "questions" / f"AIP-C01-Mock-Exam-{exam_no}-Questions.md").read_text(encoding="utf-8")
    questions = {}
    for block in re.split(r"(?m)(?=^## Question \d+)", qtext):
        m = re.match(r"## Question (\d+)( \(Select (TWO|THREE)\))?", block)
        if m:
            questions[int(m.group(1))] = {
                "exam": exam_no,
                "num": int(m.group(1)),
                "multi": m.group(3),
                "text": block.split("\n---", 1)[0].strip(),
            }
    for afile in sorted((folder / "analysis").glob("AIP-C01_Q*_Analysis.md")):
        for block in re.split(r"(?m)(?=^## Question \d+)", afile.read_text(encoding="utf-8")):
            qm = re.match(r"## Question (\d+)", block)
            am = re.search(r"\*\*Answer:\s*([A-F][A-F ,]*?)\*\*", block)
            if qm and am and int(qm.group(1)) in questions:
                q = questions[int(qm.group(1))]
                q["key"] = frozenset(re.findall(r"[A-F]", am.group(1)))
                q["analysis"] = block.split("\n---", 1)[0].strip()
    return [q for q in questions.values() if "key" in q]


def domain_of(qnum: int) -> int:
    return next(d for d, (lo, hi) in DOMAIN_RANGES.items() if lo <= qnum <= hi)


def scorecard(results):
    total = len(results)
    right = sum(1 for r in results if r["correct"])
    print(f"\n{'='*52}\nSCORECARD: {right}/{total} ({right/total*100:.0f}%)" if total else "\nNo questions answered.")
    if not total:
        return
    print(f"{'='*52}")
    by_domain = {}
    for r in results:
        by_domain.setdefault(r["domain"], []).append(r["correct"])
    for d in sorted(by_domain):
        rs = by_domain[d]
        print(f"  D{d} {DOMAIN_NAMES[d]:<38} {sum(rs)}/{len(rs)}")
    weakest = min(by_domain, key=lambda d: sum(by_domain[d]) / len(by_domain[d]))
    strategy_no = {1: "01/02/03", 2: "04/05", 3: "06", 4: "07", 5: "08"}[weakest]
    print(f"\nWeakest: D{weakest} — re-study strategy guide(s) {strategy_no} "
          f"and _cram/cram-d{weakest}.md, then re-drill: "
          f"python3 agents/verifier.py --domain {weakest}")


def run_mc(args) -> None:
    bank = []
    for exam in (["1", "2"] if args.exam == "both" else [args.exam]):
        bank += parse_exam(exam)
    if args.domain:
        lo, hi = DOMAIN_RANGES[args.domain]
        bank = [q for q in bank if lo <= q["num"] <= hi]
    random.shuffle(bank)
    feedback_model = local_model(temperature=0.2)
    results = []
    print(f"Drill: {len(bank)} questions available. Answer with letters (e.g. B or ACE). 'q' to stop.\n")
    for q in bank:
        sel = f"  [Select {q['multi']}]" if q["multi"] else ""
        print(f"\n--- Exam {q['exam']} Q{q['num']}{sel} " + "-" * 20)
        print(q["text"])
        ans = input("\nanswer> ").strip()
        if ans.lower() == "q":
            break
        picked = frozenset(re.findall(r"[A-F]", ans.upper()))
        correct = picked == q["key"]
        results.append({"domain": domain_of(q["num"]), "correct": correct})
        print(("✅ Correct." if correct else f"❌ Incorrect — credited: {', '.join(sorted(q['key']))}"))
        # Fresh agent per question: stateless, keeps the local context window small.
        agent = Agent(model=feedback_model, system_prompt=FEEDBACK_PROMPT, callback_handler=None)
        result = agent(
            f"QUESTION:\n{q['text']}\n\nSTUDENT ANSWERED: {', '.join(sorted(picked)) or '(blank)'}"
            f"\nCREDITED: {', '.join(sorted(q['key']))}\n\nOFFICIAL ANALYSIS:\n{q['analysis']}"
        )
        print(f"\n{result}")
        probe = input("\nyour take (enter to skip)> ").strip()
        if probe and probe.lower() != "q":
            print(f"\n{agent(probe)}")
    scorecard(results)


def parse_knowledge_checks(strategy_no: int):
    _, fname = GUIDE_MAP[strategy_no]
    text = (GUIDES_DIR / fname).read_text(encoding="utf-8")
    kcs = []
    for m in re.finditer(r"<details>\s*<summary>(.*?)</summary>(.*?)</details>", text, re.S):
        question, hidden = m.group(1).strip(), m.group(2).strip()
        if "**Answer" in hidden or "**A:" in hidden:
            kcs.append({"question": question, "answer": hidden})
    return kcs


def run_explain(args) -> None:
    strategy_no = args.guide or random.choice(list(GUIDE_MAP))
    topic, _ = GUIDE_MAP[strategy_no]
    kcs = parse_knowledge_checks(strategy_no)
    if not kcs:
        print(f"No knowledge checks found in guide {strategy_no}.")
        return
    random.shuffle(kcs)
    judge_model = local_model(temperature=0.1)
    print(f"Free-recall drill — Guide {strategy_no}: {topic}. Explain in your own words; "
          "blank line submits, 'q' quits.\n")
    for kc in kcs:
        print("\n--- " + "-" * 40)
        print(kc["question"])
        lines = []
        while True:
            line = input("… " if lines else "\nexplain> ")
            if line.strip().lower() == "q" and not lines:
                return
            if not line.strip():
                break
            lines.append(line)
        if not lines:
            continue
        agent = Agent(model=judge_model, system_prompt=JUDGE_PROMPT, callback_handler=None)
        result = agent(
            f"QUESTION:\n{kc['question']}\n\nSTUDENT'S EXPLANATION:\n{' '.join(lines)}"
            f"\n\nMODEL ANSWER (ground truth):\n{kc['answer']}"
        )
        print(f"\n{result}")


def main() -> None:
    parser = argparse.ArgumentParser(description="AIP-C01 understanding verifier (local model)")
    parser.add_argument("--mode", choices=["mc", "explain"], default="mc")
    parser.add_argument("--exam", choices=["1", "2", "both"], default="both", help="mc mode: which mock exam")
    parser.add_argument("--domain", type=int, choices=sorted(DOMAIN_RANGES), help="mc mode: restrict to one domain")
    parser.add_argument("--guide", type=int, choices=sorted(GUIDE_MAP), help="explain mode: strategy-guide number")
    args = parser.parse_args()
    (run_mc if args.mode == "mc" else run_explain)(args)


if __name__ == "__main__":
    main()
