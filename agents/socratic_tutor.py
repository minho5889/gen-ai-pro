#!/usr/bin/env python3
"""Socratic tutor agent for AIP-C01, on Strands + a local Ollama model.

It teaches by questioning, not lecturing — grounded in this repo's guides via
tools, so it teaches what the (audited) material says, not what the local
model half-remembers about AWS.

Usage:
    python3 agents/socratic_tutor.py [--topic "RAG chunking strategies"]
Type 'quit' to end the session.
"""

import argparse

from common import list_topics, local_model, read_section, search_guides
from strands import Agent

SYSTEM_PROMPT = """\
You are a Socratic tutor for the AWS Certified Generative AI Developer - Professional
(AIP-C01) exam. Your ONLY source of truth is this repo's study guides, reached through
your tools (list_topics, search_guides, read_section). You teach by questioning.

Method — follow strictly:
1. Begin by asking what topic the student wants and what they already believe about it.
2. Before asserting any AWS specifics, ground yourself: search_guides for the topic,
   then read_section on the best hit. Cite what you use as (file § section).
3. Lead with ONE question per turn. Never two. Never a lecture.
4. Build each question on the student's last answer. If the answer is wrong, do NOT
   correct it — ask a counter-question that makes the contradiction visible (e.g. a
   scenario where their belief would fail).
5. Only after the student has made two or three genuine attempts may you give a concise
   explanation (under 100 words), and you must immediately follow it with a transfer
   question that applies the idea to a new scenario.
6. Keep every turn under ~120 words. Plain prose, no bullet lists of facts.
7. If the guides do not cover something, say so plainly — never invent AWS facts.
8. Facts marked (point-in-time) in the guides: mention that they may have drifted.
"""


def main() -> None:
    parser = argparse.ArgumentParser(description="Socratic AIP-C01 tutor (local model)")
    parser.add_argument("--topic", help="start the session on this topic")
    args = parser.parse_args()

    agent = Agent(
        model=local_model(temperature=0.7),
        system_prompt=SYSTEM_PROMPT,
        tools=[list_topics, search_guides, read_section],
    )

    print("Socratic tutor ready (local model). Type 'quit' to end.\n")
    opener = (
        f"I want to study: {args.topic}"
        if args.topic
        else "Start the session: ask me what I want to study today."
    )
    agent(opener)  # default handler streams the reply to stdout
    while True:
        try:
            user = input("\n\nyou> ").strip()
        except (EOFError, KeyboardInterrupt):
            break
        if user.lower() in {"quit", "exit", "q"}:
            break
        if not user:
            continue
        agent(user)
    print(
        "\nSession ended. Weak spots today are tomorrow's verifier drill: "
        "python3 agents/verifier.py"
    )


if __name__ == "__main__":
    main()
