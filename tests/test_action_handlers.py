"""
Integration tests for action handlers — verifies each handler dispatches
to the correct generator with the right arguments.
"""

import pytest
from unittest.mock import AsyncMock, patch
from tests.conftest import set_generator_response
from engine.action_handlers import (
    IgnoreActionHandler,
    ReplyActionHandler,
    DryReplyActionHandler,
    EndConvoActionHandler,
    ChangeTopicActionHandler,
    AskQuestionActionHandler,
    HelpActionHandler,
    StatCheckActionHandler,
    GameTopicActionHandler,
    ActUnknowingActionHandler,
)


class TestIgnoreHandler:
    @pytest.mark.asyncio
    async def test_returns_none(self):
        handler = IgnoreActionHandler()
        result = await handler.handle(message="lol", req_id="t01")
        assert result is None


class TestReplyHandler:
    @pytest.mark.asyncio
    async def test_returns_generated_reply(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "hey there")
        handler = ReplyActionHandler()
        result = await handler.handle(
            message="hello",
            user=fake_user,
            chat_history=[],
            req_id="t02",
            mood="happy",
        )
        assert result == "hey there"

    @pytest.mark.asyncio
    async def test_passes_mood_to_generator(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "grr")
        handler = ReplyActionHandler()
        with patch.object(handler.gen, "generate", new_callable=AsyncMock, return_value="grr") as mock_gen:
            await handler.handle(
                message="hey", user=fake_user, chat_history=[],
                req_id="t03", mood="angry",
            )
            _, kwargs = mock_gen.call_args
            assert kwargs["mood"] == "angry"

    @pytest.mark.asyncio
    async def test_trims_history_to_8(self, mock_openai_client, fake_user, long_history):
        set_generator_response(mock_openai_client, "reply")
        handler = ReplyActionHandler()
        with patch.object(handler.gen, "generate", new_callable=AsyncMock, return_value="ok") as mock_gen:
            await handler.handle(
                message="test", user=fake_user, chat_history=long_history,
                req_id="t04", mood="neutral",
            )
            _, kwargs = mock_gen.call_args
            assert len(kwargs["chat_history"]) == 8


class TestDryReplyHandler:
    @pytest.mark.asyncio
    async def test_passes_mood(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "k.")
        handler = DryReplyActionHandler()
        with patch.object(handler.gen, "dry_reply", new_callable=AsyncMock, return_value="k.") as mock_gen:
            await handler.handle(
                message="lol", user=fake_user, chat_history=[],
                req_id="t05", mood="irritated",
            )
            _, kwargs = mock_gen.call_args
            assert kwargs["mood"] == "irritated"


class TestEndConvoHandler:
    @pytest.mark.asyncio
    async def test_returns_goodbye(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "see ya")
        handler = EndConvoActionHandler()
        result = await handler.handle(
            message="bye", user=fake_user, chat_history=[],
            req_id="t06", mood="happy",
        )
        assert result == "see ya"


class TestChangeTopicHandler:
    @pytest.mark.asyncio
    async def test_returns_new_topic(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "so about Bardok...")
        handler = ChangeTopicActionHandler()
        result = await handler.handle(
            message="...", user=fake_user, chat_history=[],
            req_id="t07", mood="neutral",
        )
        assert "Bardok" in result


class TestAskQuestionHandler:
    @pytest.mark.asyncio
    async def test_returns_question(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "what class are you playing?")
        handler = AskQuestionActionHandler()
        result = await handler.handle(
            message="idk", user=fake_user, chat_history=[],
            req_id="t08", mood="neutral",
        )
        assert "?" in result


class TestStatCheckHandler:
    @pytest.mark.asyncio
    async def test_returns_stat_info(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "you have 1000 gold")
        handler = StatCheckActionHandler()
        result = await handler.handle(
            message="how much gold?", user=fake_user,
            chat_history=[], req_id="t09", mood="neutral",
        )
        assert "1000" in result

    @pytest.mark.asyncio
    async def test_uses_get_stats(self, mock_openai_client, fake_user):
        """Verify handler calls user.get_stats() instead of passing the whole object."""
        set_generator_response(mock_openai_client, "stats")
        handler = StatCheckActionHandler()
        with patch.object(handler.gen, "stat_check", new_callable=AsyncMock, return_value="stats") as mock_gen:
            await handler.handle(
                message="my stats", user=fake_user,
                chat_history=[], req_id="t10", mood="neutral",
            )
            _, kwargs = mock_gen.call_args
            # user_stats should NOT contain identity fields
            assert "user_id" not in kwargs["user_stats"]
            assert "name" not in kwargs["user_stats"]
            assert "gold" in kwargs["user_stats"]


class TestGameTopicHandler:
    @pytest.mark.asyncio
    async def test_passes_mood(self, mock_openai_client, fake_user):
        set_generator_response(mock_openai_client, "bardok is tough")
        handler = GameTopicActionHandler()
        with patch.object(handler.gen, "game_topic", new_callable=AsyncMock, return_value="yeah") as mock_gen:
            await handler.handle(
                message="bardok is broken", user=fake_user, chat_history=[],
                req_id="t11", mood="angry",
            )
            _, kwargs = mock_gen.call_args
            assert kwargs["mood"] == "angry"


class TestActUnknowingHandler:
    @pytest.mark.asyncio
    async def test_returns_in_character_decline(self, mock_openai_client):
        set_generator_response(mock_openai_client, "what's a ronaldo?")
        handler = ActUnknowingActionHandler()
        result = await handler.handle(
            message="who is Ronaldo?", req_id="t12",
        )
        assert "ronaldo" in result.lower()
