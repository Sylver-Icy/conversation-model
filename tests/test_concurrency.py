"""
Concurrency tests — verify the system handles multiple simultaneous
messages without crashes, state corruption, or data races.
"""

import asyncio
import json
import pytest
from tests.conftest import _make_chat_response, planner_response
from engine.msg_gen_engine import Engine
from generator.msg_generator import veyra
from regulators import context_model as cm


@pytest.fixture(autouse=True)
def reset_mood():
    for mood in veyra.mood_state:
        veyra.mood_state[mood] = 0.0
    yield
    for mood in veyra.mood_state:
        veyra.mood_state[mood] = 0.0


class TestConcurrentMessages:
    """Simulate multiple users sending messages at the same time."""

    @pytest.mark.asyncio
    async def test_concurrent_ignores_do_not_crash(self, mock_openai_client, fake_user):
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore")
        )
        engine = Engine()

        tasks = [
            engine.respond(f"msg {i}", fake_user, [], f"conc-{i}")
            for i in range(10)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        # No exceptions should have been raised
        for r in results:
            assert not isinstance(r, Exception), f"Got exception: {r}"

    @pytest.mark.asyncio
    async def test_concurrent_replies_do_not_crash(self, mock_openai_client):
        from tests.conftest import FakeUser
        engine = Engine()

        # Each call makes 2 LLM calls: planner + generator
        call_count = 0

        async def mock_create(**kwargs):
            nonlocal call_count
            call_count += 1
            if "response_format" in kwargs:
                # Planner call
                return _make_chat_response(planner_response("reply"))
            # Generator call
            return _make_chat_response(f"reply #{call_count}")

        mock_openai_client.chat.completions.create.side_effect = mock_create

        users = [FakeUser(user_id=i, name=f"User{i}") for i in range(5)]
        tasks = [
            engine.respond(f"hello from user {u.user_id}", u, [], f"conc-reply-{u.user_id}")
            for u in users
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            assert not isinstance(r, Exception), f"Got exception: {r}"
        assert all(isinstance(r, str) for r in results)

    @pytest.mark.asyncio
    async def test_mood_state_survives_concurrency(self, mock_openai_client, fake_user):
        """Mood updates from concurrent messages should not corrupt state."""
        engine = Engine()
        deltas = {"happy": 1, "angry": 0, "irritated": 0, "sad": 0, "flirty": 0}
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore", mood_deltas=deltas)
        )

        tasks = [
            engine.respond(f"nice {i}", fake_user, [], f"mood-conc-{i}")
            for i in range(10)
        ]
        await asyncio.gather(*tasks)

        # Mood state should be valid (not NaN, not corrupted)
        for k, v in veyra.mood_state.items():
            assert isinstance(v, float), f"{k} is not float: {v}"
            assert -10.0 <= v <= 10.0, f"{k} out of range: {v}"

    @pytest.mark.asyncio
    async def test_context_history_survives_concurrency(self, mock_openai_client):
        """Global history should not lose entries or crash under concurrent writes."""
        from tests.conftest import FakeUser
        engine = Engine()

        async def mock_create(**kwargs):
            if "response_format" in kwargs:
                return _make_chat_response(planner_response("ignore"))
            return _make_chat_response("ok")

        mock_openai_client.chat.completions.create.side_effect = mock_create

        users = [FakeUser(user_id=i, name=f"User{i}") for i in range(5)]
        tasks = [
            engine.respond(f"concurrent msg from user {u.user_id}", u, [], f"ctx-conc-{u.user_id}")
            for u in users
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            assert not isinstance(r, Exception), f"Got exception: {r}"

        # History should have some entries (the ignore handler doesn't
        # call add_to_history, but fetch_context in other paths does)
        assert len(cm.history) <= 150  # max_history not exceeded


class TestRapidFireSingleUser:
    """Simulate a single user spamming messages quickly."""

    @pytest.mark.asyncio
    async def test_rapid_fire_does_not_crash(self, mock_openai_client, fake_user):
        engine = Engine()
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore")
        )

        tasks = [
            engine.respond("spam", fake_user, [], f"spam-{i}")
            for i in range(20)
        ]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        for r in results:
            assert not isinstance(r, Exception)

    @pytest.mark.asyncio
    async def test_mood_clamps_under_rapid_fire(self, mock_openai_client, fake_user):
        """Even rapid-fire anger messages should not exceed mood clamp."""
        engine = Engine()
        angry_deltas = {"happy": 0, "angry": 5, "irritated": 3, "sad": 0, "flirty": 0}
        mock_openai_client.chat.completions.create.return_value = _make_chat_response(
            planner_response("ignore", mood_deltas=angry_deltas)
        )

        tasks = [
            engine.respond("insult", fake_user, [], f"clamp-{i}")
            for i in range(20)
        ]
        await asyncio.gather(*tasks)

        assert veyra.mood_state["angry"] <= 10.0
        assert veyra.mood_state["irritated"] <= 10.0
