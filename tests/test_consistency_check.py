"""Unit tests for the consistency checker's functional core.

Positive cases prove clean content passes; negative cases prove the checker
still catches every defect class it was built for (each one was a real bug).
"""

import consistency_check as cc


def _q(n: int, marker: str = "", body: str = "stem?") -> str:
    head = f"## Question {n}" + (f" (Select {marker})" if marker else "")
    return f"{head}\n\n{body}\n\n"


def make_exam(markers: dict[int, str] | None = None) -> str:
    """Build a synthetic 65-question file with optional Select markers."""
    markers = markers or {}
    return "".join(_q(n, markers.get(n, "")) for n in range(1, 66))


class TestMarkers:
    def test_clean_exam_passes(self):
        text = make_exam({5: "TWO"})
        assert cc.marker_findings("1", text, text) == []

    def test_wrong_question_count(self):
        short = "".join(_q(n) for n in range(1, 60))
        assert any("expected 65" in f for f in cc.marker_findings("1", short, short))

    def test_sheet_marker_mismatch(self):
        # The real Exam-2 Q19/Q57 bug: sheet said TWO while questions said THREE.
        q = make_exam({19: "THREE"})
        s = make_exam({19: "TWO"})
        assert any("Q19: marker mismatch" in f for f in cc.marker_findings("2", q, s))

    def test_header_body_disagreement(self):
        # The real Exam-1 Q49 bug: header THREE, body text saying Select TWO.
        text = make_exam().replace(
            "## Question 49\n\nstem?",
            "## Question 49 (Select THREE)\n\nPick them. (Select TWO)",
        )
        assert any("Q49" in f and "body says" in f for f in cc.marker_findings("1", text, text))


class TestTables:
    ANALYSIS = (
        "## Question 19\n\n"
        "- **A** ✅ right one\n- **B** ✅ also right\n- **C** ✅ third\n- **D** ❌ nope\n\n"
        "**Answer: ABC**\n"
    )

    def _files(self, content: str) -> dict[str, str]:
        files = {f"AIP-C01_Q{i:02d}-Q{i + 4:02d}_Analysis.md": "" for i in range(1, 62, 5)}
        files["AIP-C01_Q16-Q20_Analysis.md"] = content
        return files

    def test_matching_table_passes(self):
        assert cc.table_findings("2", self._files(self.ANALYSIS)) == []

    def test_checkmark_answer_mismatch(self):
        # The real Exam-2 bug: multi-select tables showing ❌ on credited letters.
        broken = self.ANALYSIS.replace("- **C** ✅ third", "- **C** ❌ third")
        assert any("Q19" in f for f in cc.table_findings("2", self._files(broken)))

    def test_wrong_file_count(self):
        assert any("expected 13" in f for f in cc.table_findings("1", {}))


class TestLinksAndBanned:
    def test_link_extraction_resolves_relative_paths(self):
        md = {"./docs/a.md": "[x](../guides/01.md) [ext](https://aws.amazon.com) [anchor](#s)"}
        assert cc.link_refs(md) == [("./docs/a.md", "../guides/01.md", "guides/01.md")]

    def test_banned_string_flagged(self):
        md = {"./g.md": "Custom models cannot be invoked on-demand at all."}
        assert any("banned stale string" in f for f in cc.banned_findings(md))

    def test_quoted_correction_note_exempt(self):
        md = {"./g.md": '> Note: an earlier key said "cannot be invoked on-demand".'}
        assert cc.banned_findings(md) == []
