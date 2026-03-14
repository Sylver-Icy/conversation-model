"""
Unit tests for planner/action_planner.py — parsing, trimming, decision routing.
"""

import json
import pytest
from planner.action_planner import (
    MOVES,
    _safe_parse_decision,
    _trim_history,
    _serialize_history,
    decide_action,
)


# ---------------------------------------------------------------------------
# _safe_parse_decision tests
# ---------------------------------------------------------------------------

class TestSafeParseDecision:
    def test_valid_json(self):
        raw = json.dumps({
            "action": "reply",
            "reason": "normal message",
            "mood_deltas": {"happy": 1, "angry": 0, "irritated": 0, "sad": 0, "flirty": 0},
        })
        result = _safe_parse_decision(raw)
        assert result["action"] == "reply"
        assert result["reason"] == "normal message"
        assert result["mood_deltas"]["happy"] == 1.0

    def test_invalid_action_falls_back_to_reply(self):
        raw = json.dumps({"action": "dance", "reason": "feeling groovy"})
        result = _safe_parse_decision(raw)
        assert result["action"] == "reply"
        assert "Fallback" in result["reason"]

    def test_missing_action_falls_back(self):
        raw = json.dumps({"reason": "no action given"})
        result = _safe_parse_decision(raw)
        assert result["action"] == "reply"

    def test_empty_json(self):
        result = _safe_parse_decision("{}")
        assert result["action"] == "reply"
        assert result["mood_deltas"] == {"happy": 0.0, "angry": 0.0, "irritated": 0.0, "sad": 0.0, "flirty": 0.0}

    def test_json_embedded_in_markdown(self):
        raw = '```json\n{"action": "ignore", "reason": "spam"}\n```'
        result = _safe_parse_decision(raw)
        assert result["action"] == "ignore"

    def test_missing_mood_deltas_defaults_to_zeros(self):
        raw = json.dumps({"action": "dry_reply", "reason": "meh"})
        result = _safe_parse_decision(raw)
        assert all(v == 0.0 for v in result["mood_deltas"].values())

    def test_partial_mood_deltas_fills_missing(self):
        raw = json.dumps({
            "action": "reply",
            "reason": "test",
            "mood_deltas": {"happy": 2, "angry": -1},
        })
        result = _safe_parse_decision(raw)
        assert result["mood_deltas"]["happy"] == 2.0
        assert result["mood_deltas"]["angry"] == -1.0
        assert result["mood_deltas"]["sad"] == 0.0

    def test_garbage_input_returns_safe_defaults(self):
        result = _safe_parse_decision("not json at all lol")
        assert result["action"] == "reply"
        assert result["reason"] != ""
        assert "mood_deltas" in result

    def test_all_valid_actions_accepted(self):
        for action_name in MOVES:
            raw = json.dumps({"action": action_name, "reason": "test"})
            result = _safe_parse_decision(raw)
            assert result["action"] == action_name

    def test_mood_deltas_cast_to_float(self):
        raw = json.dumps({
            "action": "reply", "reason": "test",
            "mood_deltas": {"happy": "2", "angry": 0, "irritated": 0, "sad": 0, "flirty": 0},
        })
        result = _safe_parse_decision(raw)
        assert isinstance(result["mood_deltas"]["happy"], float)


# ---------------------------------------------------------------------------
# History helpers
# ---------------------------------------------------------------------------

class TestTrimHistory:
    def test_trims_to_max(self):
        history = [{"content": str(i)} for i in range(20)]
        trimmed = _trim_history(history, max_items=10)
        assert len(trimmed) == 10
        assert trimmed[0]["content"] == "10"  # kept the last 10

    def test_short_history_unchanged(self):
        history = [{"content": "a"}, {"content": "b"}]
        assert _trim_history(history, max_items=10) == history

    def test_empty_history(self):
        assert _trim_history([], max_items=10) == []


class TestSerializeHistory:
    def test_returns_valid_json(self):
        history = [{"author": "Test", "content": "hello"}]
        raw = _serialize_history(history)
        parsed = json.loads(raw)
        assert parsed[0]["content"] == "hello"


# ---------------------------------------------------------------------------
# decide_action (with mocked LLM)
# ---------------------------------------------------------------------------

class TestDecideAction:
    @pytest.mark.asyncio
    async def test_returns_action_and_mood_deltas(self, mock_openai_client):
        from tests.conftest import set_planner_response
        set_planner_response(mock_openai_client, "ignore", "low effort", {"happy": 0, "angry": 0, "irritated": 0.5, "sad": 0, "flirty": 0})
        result = await decide_action([], "lol ok")
        assert result["action"] == "ignore"
        assert result["mood_deltas"]["irritated"] == 0.5

    @pytest.mark.asyncio
    async def test_mood_param_injected_into_prompt(self, mock_openai_client):
        from tests.conftest import set_planner_response
        set_planner_response(mock_openai_client, "dry_reply")
        await decide_action([], "whatever", mood="angry")
        call_args = mock_openai_client.chat.completions.create.call_args
        system_msg = call_args.kwargs["messages"][0]["content"]
        assert "angry" in system_msg

    @pytest.mark.asyncio
    async def test_history_included_in_prompt(self, mock_openai_client, short_history):
        from tests.conftest import set_planner_response
        set_planner_response(mock_openai_client, "reply")
        await decide_action(short_history, "test message")
        call_args = mock_openai_client.chat.completions.create.call_args
        user_msg = call_args.kwargs["messages"][1]["content"]
        assert "hey veyra" in user_msg

    @pytest.mark.asyncio
    async def test_uses_json_response_format(self, mock_openai_client):
        from tests.conftest import set_planner_response
        set_planner_response(mock_openai_client, "reply")
        await decide_action([], "hello")
        call_args = mock_openai_client.chat.completions.create.call_args
        assert call_args.kwargs["response_format"] == {"type": "json_object"}
