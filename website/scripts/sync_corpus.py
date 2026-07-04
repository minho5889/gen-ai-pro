#!/usr/bin/env python3
"""Section-aware chunker + corpus sync + batched Knowledge Base ingestion.

Architecture: functional core / imperative shell. The core (``clean`` through
``build_chunks``) is pure — text in, chunks out — and unit-tested in
``tests/test_sync_corpus.py``. The shell (``load_documents``, ``dry_run``,
``sync``, ``main``) owns every file read, S3 call, and ingestion poll.

Chunking strategy (why NONE + pre-chunking beats the built-ins here): the
corpus is textbook markdown with a strong heading hierarchy, so we split on
that hierarchy (## sections, ### subsections), prepend a breadcrumb header so
each embedding carries its own context, strip Mermaid noise, keep chunks
60-600 words (paragraph-boundary splits with one-paragraph overlap, fragments
merged forward), and emit a metadata sidecar per chunk. Bedrock ingests with
chunking_strategy=NONE — our chunks land as-is.

Ingestion is batched: one StartIngestionJob per sync run, never per file
(guide 02's buffer-and-orchestrate lesson; ingestion is job-based).

Usage:
    python3 sync_corpus.py --dry-run
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

# --------------------------- functional core ---------------------------------


def clean(text: str) -> str:
    """Strip markup that embeds as noise.

    Mermaid code blocks become a placeholder and ``<details>``/``<summary>``
    tags are removed (their text content stays — Q&A pairs embed well).

    Args:
        text: Raw markdown.

    Returns:
        Markdown ready for chunking.
    """
    text = re.sub(
        r"```mermaid.*?```", "[architecture diagram - see source guide]", text, flags=re.S
    )
    text = re.sub(r"</?(details|summary)>", "", text)
    return text.strip()


def split_headings(text: str, level: int):
    """Split markdown at one heading level.

    Args:
        text: Markdown to split.
        level: Heading level (2 for ``##``, 3 for ``###``).

    Yields:
        ``(heading, body)`` tuples in document order. A leading body before the
        first heading (or the whole text when no headings exist) yields with
        ``heading=None``. Bodies include any deeper-level headings.
    """
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


def size_windows(body: str) -> list[str]:
    """Split an oversized body at paragraph boundaries.

    Consecutive windows overlap by one paragraph so no idea is orphaned at a
    boundary.

    Args:
        body: Section text exceeding ``MAX_WORDS``.

    Returns:
        Window strings, each targeting ``TARGET_WORDS``.
    """
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


def chunk_document(doc_id: str, text: str, breadcrumb_root: str, meta: dict) -> list[tuple]:
    """Chunk one document into breadcrumbed, retrieval-sized units.

    Args:
        doc_id: Stable identifier used as the S3 key prefix (e.g. file stem).
        text: Raw markdown of the document.
        breadcrumb_root: Human-readable document name for breadcrumb headers.
        meta: Base metadata attached to every chunk (source_file/guide/domain/type).

    Returns:
        ``(key, content, metadata)`` tuples; ``content`` starts with the
        breadcrumb line, ``metadata`` extends ``meta`` with breadcrumb/section.
    """
    chunks = []
    for sec, sec_body in split_headings(clean(text), 2):
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
                key = f"{doc_id}/{len(chunks):03d}.md"
                chunks.append(
                    (key, content, {**meta, "breadcrumb": crumb + suffix, "section": sec})
                )
    return chunks


def build_chunks(documents: list[tuple]) -> list[tuple]:
    """Chunk every document in the corpus.

    Args:
        documents: ``(doc_id, text, breadcrumb_root, meta)`` tuples, e.g. from
            ``load_documents``.

    Returns:
        Concatenated ``(key, content, metadata)`` chunk tuples.
    """
    chunks = []
    for doc_id, text, root, meta in documents:
        chunks += chunk_document(doc_id, text, root, meta)
    return chunks


def sidecar(meta: dict) -> str:
    """Render a chunk's Bedrock KB metadata sidecar.

    Args:
        meta: Chunk metadata attributes.

    Returns:
        JSON body for the ``<key>.metadata.json`` object.
    """
    return json.dumps({"metadataAttributes": dict(meta)})


def stats(chunks: list[tuple]) -> str:
    """Summarize a chunk set for humans.

    Args:
        chunks: ``(key, content, metadata)`` tuples.

    Returns:
        Multi-line summary (count, word distribution, type breakdown).
    """
    words = sorted(len(c.split()) for _, c, _ in chunks)
    by_type: dict[str, int] = {}
    for _, _, m in chunks:
        by_type[m["type"]] = by_type.get(m["type"], 0) + 1
    return (
        f"{len(chunks)} chunks\n"
        f"words/chunk: min {words[0]}, median {words[len(words) // 2]}, max {words[-1]}\n"
        f"by type: {by_type}"
    )


# --------------------------- imperative shell --------------------------------


def load_documents() -> list[tuple]:
    """Read the corpus from the repo.

    Returns:
        ``(doc_id, text, breadcrumb_root, meta)`` tuples for guides, cram
        sheets, and the exam blueprint.
    """
    docs = []
    for fname, (no, topic, domain) in GUIDES.items():
        path = REPO / "guides" / fname
        meta = {"source_file": fname, "guide": no, "domain": domain, "type": "guide"}
        docs.append((path.stem, path.read_text(encoding="utf-8"), f"Guide {no} - {topic}", meta))
    for cram in sorted((REPO / "_cram").glob("cram-d*.md")):
        domain = cram.stem.split("-")[1]
        meta = {"source_file": cram.name, "guide": 0, "domain": domain, "type": "cram"}
        docs.append(
            (cram.stem, cram.read_text(encoding="utf-8"), f"Cram sheet {domain.upper()}", meta)
        )
    bp = REPO / "AIP-C01-Exam-Blueprint.md"
    meta = {"source_file": bp.name, "guide": 0, "domain": "all", "type": "blueprint"}
    docs.append((bp.stem, bp.read_text(encoding="utf-8"), "Official Exam Blueprint", meta))
    return docs


def dry_run(chunks: list[tuple]) -> None:
    """Write chunks to ``./out`` for inspection and print stats.

    Args:
        chunks: ``(key, content, metadata)`` tuples.
    """
    out = Path(__file__).parent / "out"
    for key, content, meta in chunks:
        p = out / key
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_text(content, encoding="utf-8")
        (out / (key + ".metadata.json")).write_text(sidecar(meta), encoding="utf-8")
    print(f"-> {out}\n{stats(chunks)}")


def sync(chunks: list[tuple], bucket: str, kb_id: str, ds_id: str) -> None:
    """Diff-upload chunks to S3 and run one batched ingestion job.

    Uploads only changed objects (md5 vs ETag), deletes stale keys, then
    starts a single StartIngestionJob and polls it to completion.

    Args:
        chunks: ``(key, content, metadata)`` tuples.
        bucket: Corpus S3 bucket name.
        kb_id: Bedrock Knowledge Base id.
        ds_id: Data source id within the knowledge base.

    Raises:
        SystemExit: If the ingestion job ends in a non-COMPLETE state.
    """
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


def main() -> None:
    """Parse arguments and run a dry-run or a full sync."""
    ap = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    ap.add_argument("--dry-run", action="store_true", help="chunk locally to ./out, no AWS calls")
    ap.add_argument("--bucket")
    ap.add_argument("--kb-id")
    ap.add_argument("--data-source-id")
    args = ap.parse_args()

    chunks = build_chunks(load_documents())
    if args.dry_run:
        dry_run(chunks)
        return
    if not (args.bucket and args.kb_id and args.data_source_id):
        ap.error("--bucket, --kb-id and --data-source-id are required (or use --dry-run)")
    sync(chunks, args.bucket, args.kb_id, args.data_source_id)


if __name__ == "__main__":
    main()
