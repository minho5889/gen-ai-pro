"""Unit tests for the chunker's functional core (text in, chunks out)."""

import json

import sync_corpus as sc

DOC = """# Title

## Document Metadata

skipped entirely

## Section 1: Basics

Intro paragraph with enough words to stand alone as retrieval content, padded
until it comfortably clears the minimum threshold for a chunk of its own by
adding several more filler words here and there and everywhere and beyond.

### Deep Dive

```mermaid
graph TD; A-->B
```

<details><summary>Q1: quiz?</summary>Answer text.</details>

Body paragraph one with plenty of additional words repeated words repeated
words repeated words repeated words to pass the minimum chunk word count and
then some extra for good measure so the fragment-merge path stays untouched.
"""


class TestClean:
    def test_mermaid_replaced_and_details_flattened(self):
        cleaned = sc.clean(DOC)
        assert "mermaid" not in cleaned
        assert "[architecture diagram - see source guide]" in cleaned
        assert "<details>" not in cleaned and "Answer text." in cleaned


class TestSplitHeadings:
    def test_sections_and_preamble(self):
        parts = list(sc.split_headings("intro\n\n## A\n\nbody-a\n\n## B\n\nbody-b", 2))
        assert [h for h, _ in parts] == [None, "A", "B"]
        assert "body-b" in parts[2][1]

    def test_no_headings_yields_whole_text(self):
        assert list(sc.split_headings("just text", 2)) == [(None, "just text")]


class TestSizeWindows:
    def test_overlap_is_one_paragraph(self):
        paras = [f"para {i} " + "w " * 200 for i in range(4)]
        windows = sc.size_windows("\n\n".join(paras))
        assert len(windows) >= 2
        # last paragraph of window N reappears at the start of window N+1
        tail = windows[0].split("\n\n")[-1]
        assert windows[1].startswith(tail)


class TestChunkDocument:
    def test_breadcrumbs_keys_and_skips(self):
        chunks = sc.chunk_document("doc01", DOC, "Guide 1 - Basics", {"type": "guide"})
        assert chunks, "expected at least one chunk"
        keys = [k for k, _, _ in chunks]
        assert keys[0] == "doc01/000.md" and len(keys) == len(set(keys))
        assert all(c.startswith("Guide 1 - Basics >> Section 1: Basics") for _, c, _ in chunks)
        assert not any("Document Metadata" in c for _, c, _ in chunks), "skip-section leaked"
        assert all(m["section"] == "Section 1: Basics" for _, _, m in chunks)

    def test_sidecar_shape(self):
        payload = json.loads(sc.sidecar({"guide": 1, "type": "guide"}))
        assert payload == {"metadataAttributes": {"guide": 1, "type": "guide"}}
