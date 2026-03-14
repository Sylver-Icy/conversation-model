"""
Unit tests for generator classes with mocked LLM calls.
"""

import pytest
from unittest.mock import AsyncMock
from tests.conftest import _make_chat_response, set_generator_response


# ---------------------------------------------------------------------------
# ChatGenerator
# ---------------------------------------------------------------------------

class TestChatGenerator:
    @pytest.mark.asyncio
    async def test_generate_returns_string(self, mock_openai_client):
        set_generator_response(mock_openai_client, "oh it's you again")
        from generator.msg_generator import ChatGenerator
        gen = ChatGenerator()
        reply = await gen.generate(
            user_msg="hello",
            user_id=1,
            user_name="TestPlayer",
            frndship_title="Casual",
            mood="happy",
            chat_history=[],
            req_id="t01",
        )
        assert reply == "oh it's you again"

    @pytest.mark.asyncio
    async def test_generate_calls_embedding_for_context(self, mock_openai_client):
        set_generator_response(mock_openai_client, "sure thing")
        from generator.msg_generator import ChatGenerator
        gen = ChatGenerator()
        await gen.generate(
            user_msg="how are you?",
            user_id=1,
            mood="neutral",
            req_id="t02",
        )
        # embeddings.create should be called (for context_model)
        assert mock_openai_client.embeddings.create.called

    @pytest.mark.asyncio
    async def test_generate_adds_reply_to_history(self, mock_openai_client):
        import regulators.context_model as cm
        set_generator_response(mock_openai_client, "added to memory test")
        from generator.msg_generator import ChatGenerator
        gen = ChatGenerator()
        await gen.generate(
            user_msg="remember this",
            user_id=1,
            mood="neutral",
            req_id="t03",
        )
        # The reply should be stored in context history via add_to_history
        contents = [h["content"] for h in cm.history]
        assert "added to memory test" in contents

    @pytest.mark.asyncio
    async def test_generate_handles_exception(self, mock_openai_client):
        mock_openai_client.chat.completions.create.side_effect = Exception("API down")
        from generator.msg_generator import ChatGenerator
        gen = ChatGenerator()
        reply = await gen.generate(
            user_msg="test", user_id=1, mood="neutral", req_id="t04"
        )
        assert "lagged" in reply or "again" in reply


# ---------------------------------------------------------------------------
# LightweightGenerator
# ---------------------------------------------------------------------------

class TestLightweightGenerator:
    @pytest.mark.asyncio
    async def test_dry_reply(self, mock_openai_client):
        set_generator_response(mock_openai_client, "k.")
        from generator.lightweight_generator import LightweightGenerator
        gen = LightweightGenerator()
        reply = await gen.dry_reply(
            message="lol", mood="irritated", frndship_title="Casual",
            chat_history=[], req_id="t05"
        )
        assert reply == "k."

    @pytest.mark.asyncio
    async def test_end_convo(self, mock_openai_client):
        set_generator_response(mock_openai_client, "bye loser")
        from generator.lightweight_generator import LightweightGenerator
        gen = LightweightGenerator()
        reply = await gen.end_convo(
            message="gotta go", frndship_title="Bestie",
            mood="happy", chat_history=[], req_id="t06"
        )
        assert reply == "bye loser"

    @pytest.mark.asyncio
    async def test_change_topic(self, mock_openai_client):
        set_generator_response(mock_openai_client, "anyway, ever fought Bardok?")
        from generator.lightweight_generator import LightweightGenerator
        gen = LightweightGenerator()
        reply = await gen.change_topic(
            message="...", frndship_title="Friend",
            mood="neutral", chat_history=[], req_id="t07"
        )
        assert "Bardok" in reply

    @pytest.mark.asyncio
    async def test_stat_check(self, mock_openai_client):
        set_generator_response(mock_openai_client, "you have 1000 gold, big spender")
        from generator.lightweight_generator import LightweightGenerator
        gen = LightweightGenerator()
        reply = await gen.stat_check(
            message="how much gold?", user_name="Alex",
            user_stats={"gold": 1000}, req_id="t08"
        )
        assert "1000" in reply

    @pytest.mark.asyncio
    async def test_handles_api_error(self, mock_openai_client):
        from openai import OpenAIError
        mock_openai_client.chat.completions.create.side_effect = OpenAIError("rate limited")
        from generator.lightweight_generator import LightweightGenerator
        gen = LightweightGenerator()
        reply = await gen.dry_reply(
            message="test", mood=None, frndship_title="Stranger",
            chat_history=[], req_id="t09"
        )
        assert "scattered" in reply


# ---------------------------------------------------------------------------
# MsgDeclineGenerator
# ---------------------------------------------------------------------------

class TestMsgDeclineGenerator:
    @pytest.mark.asyncio
    async def test_generates_decline(self, mock_openai_client):
        set_generator_response(mock_openai_client, "what's a 'python'?")
        from generator.msgdecline_generator import MsgDeclineGenerator
        gen = MsgDeclineGenerator()
        reply = await gen.generate(msg="what is Python?", req_id="t10")
        assert reply == "what's a 'python'?"


# ---------------------------------------------------------------------------
# HelpGenerator
# ---------------------------------------------------------------------------

class TestHelpGenerator:
    @pytest.mark.asyncio
    async def test_generates_help_response(self, mock_openai_client):
        set_generator_response(mock_openai_client, "Battle is a 1v1 system...")
        from generator.help_generator import HelpGenerator
        gen = HelpGenerator()
        reply = await gen.generate(
            message="how does battle work?",
            req_id="t11",
        )
        assert "Battle" in reply

    @pytest.mark.asyncio
    async def test_uses_reason_for_retrieval(self, mock_openai_client):
        set_generator_response(mock_openai_client, "the loadout lets you equip stuff")
        from generator.help_generator import HelpGenerator
        gen = HelpGenerator()
        reply = await gen.generate(
            message="what about that?",
            req_id="t12",
            reason="user asking about loadout system",
        )
        assert isinstance(reply, str)

    @pytest.mark.asyncio
    async def test_handles_empty_content(self, mock_openai_client):
        from types import SimpleNamespace
        empty_response = SimpleNamespace(
            choices=[SimpleNamespace(
                message=SimpleNamespace(content=None, refusal=None),
                finish_reason="stop",
            )],
            usage=SimpleNamespace(prompt_tokens=10, completion_tokens=0),
        )
        mock_openai_client.chat.completions.create.return_value = empty_response
        from generator.help_generator import HelpGenerator
        gen = HelpGenerator()
        reply = await gen.generate(message="test", req_id="t13")
        assert "weird" in reply or "again" in reply
