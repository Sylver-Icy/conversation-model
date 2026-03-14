"""
Behavioral / scenario tests for the conversation system.
Tests realistic multi-message scenarios to verify the system behaves
as expected end-to-end under different conversation conditions.
"""

import json
import pytest
from tests.conftest import _make_chat_response, planner_response
from engine.msg_gen_engine import Engine
from generator.msg_generator import veyra


@pytest.fixture(autouse=True)
def reset_mood():
    for mood in veyra.mood_state:
        veyra.mood_state[mood] = 0.0
    yield
    for mood in veyra.mood_state:
        veyra.mood_state[mood] = 0.0


class TestMoodAccumulatesAcrossMessages:
    """Verify mood builds up over sequential messages and influences planner."""

    @pytest.mark.asyncio
    async def test_repeated_insults_build_anger(self, mock_openai_client, fake_user):
        engine = Engine()
        insult_deltas = {"happy": -1, "angry": 3, "irritated": 2, "sad": 0, "flirty": -1}
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore", mood_deltas=insult_deltas)
        )

        # Send 3 insults
        for _ in range(3):
            await engine.respond("you're terrible", fake_user, [], "angry-test")

        # Anger should be well above zero
        assert veyra.mood_state["angry"] > 5.0
        assert veyra.get_active_mood() == "angry"

    @pytest.mark.asyncio
    async def test_compliments_build_happiness(self, mock_openai_client, fake_user):
        engine = Engine()
        nice_deltas = {"happy": 3, "angry": -1, "irritated": -1, "sad": 0, "flirty": 2}
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore", mood_deltas=nice_deltas)
        )

        for _ in range(3):
            await engine.respond("you're amazing", fake_user, [], "happy-test")

        assert veyra.mood_state["happy"] > 5.0
        assert veyra.get_active_mood() in ("happy", "flirty")


class TestMoodDecaysOverTime:
    """Verify mood naturally cools off with neutral messages."""

    @pytest.mark.asyncio
    async def test_anger_decays_with_neutral_messages(self, mock_openai_client, fake_user):
        engine = Engine()
        veyra.mood_state["angry"] = 10.0

        # Send 30 neutral messages (zero deltas)
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore")
        )
        for _ in range(30):
            await engine.respond("ok", fake_user, [], "decay-test")

        # 10.0 * (0.97^30) ≈ 4.01 — should have decayed substantially
        assert veyra.mood_state["angry"] < 5.0


class TestActionRouting:
    """Verify different actions route to different handlers correctly."""

    @pytest.mark.asyncio
    async def test_stat_check_returns_stats(self, mock_openai_client, fake_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("stat_check")),
            _make_chat_response("you have 1000 gold, not bad"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        result = await engine.respond("how much gold do I have?", fake_user, [], "route-01")
        assert result is not None
        assert isinstance(result, str)

    @pytest.mark.asyncio
    async def test_help_triggers_retrieval(self, mock_openai_client, fake_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("help", reason="user asking about battle system")),
            _make_chat_response("Battle is a 1v1 PvP system where you..."),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        result = await engine.respond("how does battle work?", fake_user, [], "route-02")
        assert result is not None

    @pytest.mark.asyncio
    async def test_act_unknowing_for_real_world(self, mock_openai_client, fake_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("act_unknowing")),
            _make_chat_response("what's a 'ronaldo'? sounds made up"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        result = await engine.respond("who is Ronaldo?", fake_user, [], "route-03")
        assert result is not None


class TestFriendshipLevelBehavior:
    """Verify friendship level affects prompt content."""

    @pytest.mark.asyncio
    async def test_stranger_gets_cold_prompt(self, mock_openai_client, stranger_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("reply")),
            _make_chat_response("who are you?"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        await engine.respond("hi!", stranger_user, [], "frnd-01")
        # Check the generator was called with the correct friendship title
        calls = mock_openai_client.chat.completions.create.call_args_list
        # The second call is the generator — its system prompt should contain "Stranger"
        if len(calls) >= 2:
            gen_system = calls[1].kwargs["messages"][0]["content"]
            assert "Stranger" in gen_system

    @pytest.mark.asyncio
    async def test_bestie_gets_warm_prompt(self, mock_openai_client, bestie_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("reply")),
            _make_chat_response("omg hiiiii"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        await engine.respond("hey bestie!", bestie_user, [], "frnd-02")
        calls = mock_openai_client.chat.completions.create.call_args_list
        if len(calls) >= 2:
            gen_system = calls[1].kwargs["messages"][0]["content"]
            assert "Bestie" in gen_system


class TestEdgeCases:
    @pytest.mark.asyncio
    async def test_empty_message(self, mock_openai_client, fake_user):
        engine = Engine()
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore")
        )
        result = await engine.respond("", fake_user, [], "edge-01")
        assert result is None

    @pytest.mark.asyncio
    async def test_very_long_message(self, mock_openai_client, fake_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("reply")),
            _make_chat_response("tl;dr"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        long_msg = "a" * 5000
        result = await engine.respond(long_msg, fake_user, [], "edge-02")
        assert result is not None

    @pytest.mark.asyncio
    async def test_special_characters_in_message(self, mock_openai_client, fake_user):
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("reply")),
            _make_chat_response("interesting"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        result = await engine.respond('hello "world" <script>alert(1)</script>', fake_user, [], "edge-03")
        assert result is not None

    @pytest.mark.asyncio
    async def test_none_user_fields_handled(self, mock_openai_client):
        from tests.conftest import FakeUser
        user = FakeUser(current_quest=None, loadout=None)
        engine = Engine()
        responses = [
            _make_chat_response(planner_response("reply")),
            _make_chat_response("sure thing"),
        ]
        mock_openai_client.chat.completions.create.side_effect = responses
        result = await engine.respond("test", user, [], "edge-04")
        assert result is not None
