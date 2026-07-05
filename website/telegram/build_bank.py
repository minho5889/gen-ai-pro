#!/usr/bin/env python3
"""Build bank.json for the Telegram bot from the mock exams.

Shell script (repo-checkout time, never in Lambda): reuses the verifier's
audited parser, adds the option letters each question offers and its exam
domain, and writes the bundle the drill runs on.

Usage: python3 build_bank.py [output_path]
"""

import json
import re
import sys
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO / "agents"))

import exam_bank  # noqa: E402 — the audited, SDK-free exam parser


def build() -> list[dict]:
    """Assemble bank entries from both mock exams.

    Returns:
        Entries with exam/num/multi/text/letters/key/domain/analysis.
    """
    entries = []
    for exam in ("1", "2"):
        for q in exam_bank.parse_exam(exam):
            letters = sorted(set(re.findall(r"(?m)^\*\*([A-F])\.\*\*", q["text"])))
            entries.append(
                {
                    "exam": exam,
                    "num": q["num"],
                    "multi": q["multi"],
                    "text": q["text"],
                    "letters": letters,
                    "key": "".join(sorted(q["key"])),
                    "domain": exam_bank.domain_of(q["num"]),
                    "analysis": q["analysis"],
                }
            )
    return entries


def main() -> None:
    """Write the bank to the given path (default: alongside this script)."""
    out = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(__file__).parent / "bank.json"
    entries = build()
    assert len(entries) == 130, f"expected 130 questions, got {len(entries)}"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(entries), encoding="utf-8")
    print(f"{len(entries)} questions -> {out}")


if __name__ == "__main__":
    main()
