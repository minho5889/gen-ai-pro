"""Unit tests for the chat backend's functional core (no server, no AWS)."""

import json

import app
import pytest


class TestParseChatRequest:
    def test_valid(self):
        raw = json.dumps({"message": " hi ", "history": [{"role": "user", "text": "x"}]}).encode()
        message, history = app.parse_chat_request(raw)
        assert message == "hi" and history == [{"role": "user", "text": "x"}]

    @pytest.mark.parametrize("raw", [b"", b"{}", b'{"message": "  "}', b"not json"])
    def test_invalid_raises(self, raw):
        with pytest.raises(ValueError):
            app.parse_chat_request(raw)


class TestFormatPassages:
    def test_numbering_breadcrumbs_and_fallbacks(self):
        block, sources = app.format_passages(
            [
                {"content": {"text": "T1"}, "metadata": {"breadcrumb": "G1 >> S1"}, "score": 0.91},
                {"content": {"text": "T2"}, "metadata": {}, "score": 0.5},
            ]
        )
        assert block.startswith("[1] (G1 >> S1)\nT1")
        assert "[2] (study guides)\nT2" in block
        assert sources == [
            {"n": 1, "breadcrumb": "G1 >> S1", "score": 0.91},
            {"n": 2, "breadcrumb": "study guides", "score": 0.5},
        ]


class TestBuildMessages:
    def test_history_trim_role_coercion_and_context(self):
        history = [{"role": "user", "text": f"t{i}"} for i in range(20)]
        history[-1]["role"] = "weird"  # untrusted input coerces to user
        msgs = app.build_messages(history, "q?", "CTX")
        assert len(msgs) == app.MAX_HISTORY_TURNS + 1
        assert msgs[-2]["role"] == "user"
        assert "CONTEXT PASSAGES:\nCTX" in msgs[-1]["content"][0]["text"]
        assert msgs[-1]["content"][0]["text"].endswith("QUESTION: q?")


class TestConverseKwargs:
    def test_shape_and_reasoning_passthrough(self):
        kwargs = app.build_converse_kwargs([{"role": "user", "content": [{"text": "x"}]}])
        assert kwargs["modelId"] == "test-model"
        assert kwargs["inferenceConfig"]["maxTokens"] == app.MAX_TOKENS
        assert "additionalModelRequestFields" not in kwargs  # EXTRA_FIELDS empty in tests


class TestSseFrame:
    def test_wire_format(self):
        frame = app.sse_frame("token", {"t": "héllo"})
        assert frame == 'event: token\ndata: {"t": "héllo"}\n\n'.encode()
