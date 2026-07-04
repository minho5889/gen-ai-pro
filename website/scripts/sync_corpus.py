#!/usr/bin/env python3
"""Section-aware chunker + corpus sync + batched Knowledge Base ingestion.

Chunking strategy (why NONE + pre-chunking beats the built-ins here):
  The corpus is textbook markdown with a strong heading hierarchy. We split on
  that hierarchy (## sections, ### subsections) so every chunk is one coherent
  teaching unit, then:
    - prepend a breadcrumb header ("Guide 2 - RAG... >> Section 5 >> Hybrid
      Search") so the embedding carries its own context — markedly better
      retrieval than naked mid-document text;
    - replace Mermaid blocks with a placeholder (diagram code embeds as noise);
    - flatten <details> quiz markup (Q&A text embeds well, tags don't);
    - keep chunks 60-600 words: oversized sections split at paragraph
      boundaries with one-paragraph overlap, fragments merged forward;
    - write a .metadata.json sidecar per chunk (guide/domain/type filterable,
      breadcrumb/source_file for display) for future filtered retrieval.
  Bedrock ingests with chunking_strategy=NONE: our chunks land as-is.

Ingestion is batched: one StartIngestionJob per sync run — never per file
(see guide 02's buffer-and-orchestrate pattern; ingestion is job-based).

Usage:
  python3 sync_corpus.py --dry-run                    # chunk to ./out, print stats
  python3 sync_corpus.py --bucket B --kb-id K --data-source-id D
"""

import argparse
import hashlib
import json
import re
import sys
import time
from pathlib import Path

REPO = Path(__file__).resolve().parents[2]
TARGET_WORDS = 450
MAX_WORDS = 600
MIN_WORDS = 60

GUIDES = {  # file -> (strategy_no, topic, primary exam domain)
    "01-Foundation-Models-Bedrock-Core.md": (1, "Foundation Models & Bedrock Core", "d1"),
    "02-RAG-Vector-Stores-Knowledge-Bases.md": (2, "RAG, Vector Stores & Knowledge Bases", "d1"),
    "05-Prompt-Engineering-Management.md": (3, "Prompt Engineering & Management", "d1"),
    "04-Agentic-AI-Agents-AgentCore-Strands-MCP.md": (
        4,
        "Agentic AI: Agents, AgentCore, Strands, MCP",
        "d2",
    ),
    "08-Enterprise-Integration-Deployment.md": (5, "Enterprise Integration & Deployment", "d2"),
    "03-AI-Safety-Security-Governance.md": (6, "AI Safety, Security & Governance", "d3"),
    "07-Cost-Performance-Monitoring.md": (7, "Cost, Performance & Monitoring", "d4"),
    "06-Testing-Evaluation-Troubleshooting.md": (8, "Testing, Evaluation & Troubleshooting", "d5"),
}
SKIP_SECTIONS = {"document metadata", "how to use this guide", "table of contents"}


def clean(text: str) -> str:
    text = re.sub(
        r"```mermaid.*?```", "[architecture diagram - see source guide]", text, flags=re.S
    )
    text = re.sub(r"</?(details|summary)>", "", text)
    return text.strip()


def split_headings(text: str, level: int):
    """Yield (heading, body) at the given heading level; body excludes deeper splits."""
    pattern = re.compile(rf"(?m)^{'#' * level} (.+)$")
    matches = list(pattern.finditer(text))
    if not matches:
        yield None, text
        return
    if matches[0].start() > 0:
        yield None, text[: matches[0].start()]
    for i, m in enumerate(matches):
        end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
        yield m.group(1).strip(), text[m.end() : end]


def size_windows(body: str):
    """Split an oversized body at paragraph boundaries with 1-para overlap."""
    paras = [p for p in re.split(r"\n\s*\n", body) if p.strip()]
    windows, cur, cur_words = [], [], 0
    for p in paras:
        w = len(p.split())
        if cur and cur_words + w > TARGET_WORDS:
            windows.append("\n\n".join(cur))
            cur, cur_words = [cur[-1]], len(cur[-1].split())  # 1-paragraph overlap
        cur.append(p)
        cur_words += w
    if cur:
        windows.append("\n\n".join(cur))
    return windows


def chunk_file(path: Path, breadcrumb_root: str, meta: dict):
    text = clean(path.read_text(encoding="utf-8"))
    chunks = []
    for sec, sec_body in split_headings(text, 2):
        if sec is None or sec.strip().lower() in SKIP_SECTIONS:
            continue
        for sub, body in split_headings(sec_body, 3):
            crumb = " >> ".join(x for x in [breadcrumb_root, sec, sub] if x)
            body = body.strip()
            if not body:
                continue
            parts = [body] if len(body.split()) <= MAX_WORDS else size_windows(body)
            for j, part in enumerate(parts):
                suffix = f" (part {j + 1})" if len(parts) > 1 else ""
                content = f"{crumb}{suffix}\n\n{part.strip()}"
                if len(content.split()) < MIN_WORDS and chunks:
                    prev_key, prev_content, prev_meta = chunks[-1]
                    chunks[-1] = (prev_key, prev_content + "\n\n" + part.strip(), prev_meta)
                    continue
                key = f"{path.stem}/{len(chunks):03d}.md"
                chunks.append(
                    (key, content, {**meta, "breadcrumb": crumb + suffix, "section": sec})
                )
    return chunks


def build_corpus():
    chunks = []
    for fname, (no, topic, domain) in GUIDES.items():
        meta = {"source_file": fname, "guide": no, "domain": domain, "type": "guide"}
        chunks += chunk_file(REPO / "guides" / fname, f"Guide {no} - {topic}", meta)
    for cram in sorted((REPO / "_cram").glob("cram-d*.md")):
        domain = cram.stem.split("-")[1]
        meta = {"source_file": cram.name, "guide": 0, "domain": domain, "type": "cram"}
        chunks += chunk_file(cram, f"Cram sheet {domain.upper()}", meta)
    bp = REPO / "AIP-C01-Exam-Blueprint.md"
    meta = {"source_file": bp.name, "guide": 0, "domain": "all", "type": "blueprint"}
    chunks += chunk_file(bp, "Official Exam Blueprint", meta)
    return chunks


def sidecar(meta: dict) -> str:
    return json.dumps({"metadataAttributes": {k: v for k, v in meta.items()}})


def dry_run(chunks):
    out = Path(__file__).parent / "out"
    for key, content, meta in chunks:
        p = out / key
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        (out / (key + ".metadata.json")).write_text(sidecar(meta), encoding="utf-8")
    words = sorted(len(c.split()) for _, c, _ in chunks)
    mid = words[len(words) // 2]
    print(f"{len(chunks)} chunks -> {out}")
    print(f"words/chunk: min {words[0]}, median {mid}, max {words[-1]}")
    by_type = {}
    for _, _, m in chunks:
        by_type[m["type"]] = by_type.get(m["type"], 0) + 1
    print(f"by type: {by_type}")


def sync(chunks, bucket, kb_id, ds_id):
    import boto3

    s3 = boto3.client("s3")
    desired = {}
    for key, content, meta in chunks:
        desired[key] = content.encode("utf-8")
        desired[key + ".metadata.json"] = sidecar(meta).encode("utf-8")

    existing = {}
    paginator = s3.get_paginator("list_objects_v2")
    for page in paginator.paginate(Bucket=bucket):
        for obj in page.get("Contents", []):
            existing[obj["Key"]] = obj["ETag"].strip('"')

    uploaded = 0
    for key, body in desired.items():
        if existing.get(key) != hashlib.md5(body).hexdigest():
            s3.put_object(Bucket=bucket, Key=key, Body=body)
            uploaded += 1
    stale = [k for k in existing if k not in desired]
    for i in range(0, len(stale), 1000):
        s3.delete_objects(
            Bucket=bucket, Delete={"Objects": [{"Key": k} for k in stale[i : i + 1000]]}
        )
    print(f"uploaded/updated {uploaded}, deleted {len(stale)}, unchanged {len(desired) - uploaded}")

    agent = boto3.client("bedrock-agent")
    job = agent.start_ingestion_job(knowledgeBaseId=kb_id, dataSourceId=ds_id)
    job_id = job["ingestionJob"]["ingestionJobId"]
    print(f"ingestion job {job_id} started", end="", flush=True)
    while True:
        time.sleep(10)
        state = agent.get_ingestion_job(
            knowledgeBaseId=kb_id, dataSourceId=ds_id, ingestionJobId=job_id
        )["ingestionJob"]
        status = state["status"]
        print(".", end="", flush=True)
        if status in {"COMPLETE", "FAILED", "STOPPED"}:
            print(f"\n{status}: {json.dumps(state.get('statistics', {}), default=str)}")
            if status != "COMPLETE":
                sys.exit(1)
            return


def main():
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="chunk locally to ./out, no AWS calls")
    ap.add_argument("--bucket")
    ap.add_argument("--kb-id")
    ap.add_argument("--data-source-id")
    args = ap.parse_args()

    chunks = build_corpus()
    if args.dry_run:
        dry_run(chunks)
        return
    if not (args.bucket and args.kb_id and args.data_source_id):
        ap.error("--bucket, --kb-id and --data-source-id are required (or use --dry-run)")
    sync(chunks, args.bucket, args.kb_id, args.data_source_id)


if __name__ == "__main__":
    main()
