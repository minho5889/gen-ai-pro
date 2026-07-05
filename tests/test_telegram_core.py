"""Unit tests for the Telegram bot's functional core (no Telegram, no AWS)."""

import handler as h


class TestParseUpdate:
    def test_text_message(self):
        u = {"message": {"chat": {"id": 42}, "text": " hi "}}
        assert h.parse_update(u) == {"kind": "message", "chat_id": 42, "text": "hi"}

    def test_callback(self):
        u = {
            "callback_query": {
                "id": "cb1",
                "data": "d|1|16|A|go",
                "message": {"chat": {"id": 42}, "message_id": 7},
            }
        }
        parsed = h.parse_update(u)
        assert parsed["kind"] == "callback" and parsed["message_id"] == 7

    def test_ignored_update_types(self):
        assert h.parse_update({"edited_message": {}}) is None
        assert h.parse_update({"message": {"chat": {"id": 1}, "photo": []}}) is None


class TestCallbackCodec:
    def test_roundtrip_and_size(self):
        data = h.encode_cb("2", 57, "ABC", "go")
        assert len(data.encode()) <= 64  # Telegram's callback_data cap
        assert h.decode_cb(data) == {"exam": "2", "qnum": 57, "picks": "ABC", "action": "go"}

    def test_rejects_foreign_data(self):
        assert h.decode_cb("other|1|2") is None
        assert h.decode_cb("d|1|x|A|go") is None

    def test_toggle_keeps_order(self):
        assert h.toggle("AC", "B") == "ABC"
        assert h.toggle("ABC", "B") == "AC"


class TestKeyboardAndScoring:
    SINGLE = {"exam": "1", "num": 3, "multi": None, "letters": ["A", "B", "C", "D"]}
    MULTI = {"exam": "2", "num": 19, "multi": "THREE", "letters": ["A", "B", "C", "D", "E"]}

    def test_single_select_one_row_scores_on_tap(self):
        kb = h.drill_keyboard(self.SINGLE, "")
        (row,) = kb["inline_keyboard"]
        assert [b["text"] for b in row] == ["A", "B", "C", "D"]
        assert h.decode_cb(row[1]["callback_data"])["action"] == "B"

    def test_multi_select_toggles_and_submit(self):
        kb = h.drill_keyboard(self.MULTI, "AB")
        letters, submit = kb["inline_keyboard"]
        assert letters[0]["text"] == "✓A" and letters[2]["text"] == "C"
        state = h.decode_cb(submit[0]["callback_data"])
        assert state["picks"] == "AB" and state["action"] == "go"

    def test_all_or_nothing_scoring(self):
        assert h.score("ACE", "ACE") and h.score("CEA", "ACE")
        assert not h.score("AC", "ACE") and not h.score("ACEB", "ACE")


class TestFormatting:
    def test_split_message_respects_limit_and_lines(self):
        text = "\n".join(f"line {i} " + "x" * 90 for i in range(80))
        pieces = h.split_message(text, limit=1000)
        assert all(len(p) <= 1000 for p in pieces)
        assert "".join(pieces).replace("\n", "") == text.replace("\n", "")

    def test_pick_question_domain_filter(self):
        bank = [{"domain": 1, "num": 1}, {"domain": 3, "num": 40}]

        class FixedRng:
            @staticmethod
            def choice(pool):
                return pool[0]

        assert h.pick_question(bank, 3, rng=FixedRng)["num"] == 40
        assert h.pick_question(bank, 5, rng=FixedRng) is None

    def test_parse_drill_command(self):
        assert h.parse_drill_command("/drill") == (True, None)
        assert h.parse_drill_command("/drill 3") == (True, 3)
        assert h.parse_drill_command("/drill 9") == (True, None)
        assert h.parse_drill_command("what is /drill?") == (False, None)
