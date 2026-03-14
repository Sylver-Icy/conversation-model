"""
Integration tests for the full Engine pipeline.
Tests the complete flow: message → planner → mood update → handler → response.
"""

import json
import pytest
from unittest.mock import AsyncMock
from types import SimpleNamespace
from tests.conftest import _make_chat_response, planner_response
from engine.msg_gen_engine import Engine
from generator.msg_generator import veyra


@pytest.fixture(autouse=True)
def reset_mood():
    """Reset Veyra's mood state before each test."""
    for mood in veyra.mood_state:
        veyra.mood_state[mood] = 0.0
    yield
    for mood in veyra.mood_state:
        veyra.mood_state[mood] = 0.0


class TestEngineRespond:
    @pytest.mark.asyncio
    async def test_ignore_returns_none(self, mock_openai_client, fake_user):
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore")
        )
        engine = Engine()
        result = await engine.respond("lol", fake_user, [], "t01")
        assert result is None

    @pytest.mark.asyncio
    async def test_reply_returns_string(self, mock_openai_client, fake_user):
        # First call = planner, subsequent calls = generator
        responses = [
            _make_chat_response(planner_response("reply", mood_deltas={"happy": 1, "angry": 0, "irritated": 0, "sad": 0, "flirty": 0})),
            _make_chat_response("hey, what's up?"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        engine = Engine()
        result = await engine.respond("hello!", fake_user, [], "t02")
        assert isinstance(result, str)
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_mood_updated_after_planner(self, mock_openai_client, fake_user):
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore", mood_deltas={"happy": 0, "angry": 3, "irritated": 2, "sad": 0, "flirty": 0})
        )
        engine = Engine()
        await engine.respond("you suck", fake_user, [], "t03")
        assert veyra.mood_state["angry"] > 0
        assert veyra.mood_state["irritated"] > 0

    @pytest.mark.asyncio
    async def test_mood_decays_each_request(self, mock_openai_client, fake_user):
        # Set mood high, then process a neutral message
        veyra.mood_state["angry"] = 10.0
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore", mood_deltas={"happy": 0, "angry": 0, "irritated": 0, "sad": 0, "flirty": 0})
        )
        engine = Engine()
        await engine.respond("ok", fake_user, [], "t04")
        # 10.0 * 0.97 = 9.7 (decay) + 0 (delta) = 9.7
        assert veyra.mood_state["angry"] == pytest.approx(9.7, abs=0.01)

    @pytest.mark.asyncio
    async def test_mood_passed_to_planner(self, mock_openai_client, fake_user):
        veyra.mood_state["angry"] = 8.0
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore")
        )
        engine = Engine()
        await engine.respond("test", fake_user, [], "t05")
        # Verify the planner received the mood in its system prompt
        call_args = mock_openai_client.chat.completions.create.call_args
        system_msg = call_args.kwargs["messages"][0]["content"]
        assert "angry" in system_msg

    @pytest.mark.asyncio
    async def test_help_follow_up_passes_prev_reply(self, mock_openai_client, fake_user, help_follow_up_history):
        responses = [
            _make_chat_response(planner_response("help")),
            _make_chat_response("the loadout lets you pick weapons..."),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        engine = Engine()
        result = await engine.respond(
            "what about the loadout?", fake_user, help_follow_up_history, "t06"
        )
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_unknown_action_falls_back_to_reply(self, mock_openai_client, fake_user):
        # Force planner to return an invalid action (parser will fix it to "reply")
        responses = [
            _make_chat_response(json.dumps({"action": "unknown_action", "reason": "oops"})),
            _make_chat_response("fallback reply"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        engine = Engine()
        result = await engine.respond("test", fake_user, [], "t07")
        assert result == "fallback reply"


class TestEngineNormalizeHistory:
    def test_normalizes_dicts(self):
        raw = [{"role": "user", "content": "hello", "author": "Test"}]
        result = Engine._normalize_history(raw)
        assert result[0]["author"] == "Test"
        assert result[0]["role"] == "user"

    def test_normalizes_strings(self):
        raw = ["hello", "world"]
        result = Engine._normalize_history(raw)
        assert all(entry["role"] == "user" for entry in result)
        assert result[0]["content"] == "hello"

    def test_handles_none(self):
        result = Engine._normalize_history(None)
        assert result == []

    def test_preserves_action_field(self):
        raw = [{"role": "assistant", "content": "...", "action": "help"}]
        result = Engine._normalize_history(raw)
        assert result[0]["action"] == "help"

    def test_mixed_types(self):
        raw = [
            {"role": "user", "content": "hi"},
            "raw string",
            42,
        ]
        result = Engine._normalize_history(raw)
        assert len(result) == 3
        assert result[1]["content"] == "raw string"
        assert result[2]["content"] == "42"
