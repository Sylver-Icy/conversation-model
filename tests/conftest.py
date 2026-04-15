"""
Shared fixtures for the Veyra conversation model test suite.
"""

import sys
import os
from types import SimpleNamespace
from unittest.mock import AsyncMock, MagicMock, patch

import numpy as np
import pytest

# Ensure project root is on sys.path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))


# ---------------------------------------------------------------------------
# Fake OpenAI response builders
# ---------------------------------------------------------------------------

def _make_chat_response(content: str):
    """Build a mock OpenAI chat completion response."""
    message = SimpleNamespace(content=content, refusal=None)
    choice = SimpleNamespace(message=message, finish_reason="stop")
    usage = SimpleNamespace(prompt_tokens=50, completion_tokens=20)
    return SimpleNamespace(choices=[choice], usage=usage)


def _make_embedding_response(dim: int = 1536):
    """Build a mock OpenAI embedding response with a random unit vector."""
    vec = np.random.randn(dim).astype(np.float32)
    vec /= np.linalg.norm(vec)
    data_item = SimpleNamespace(embedding=vec.tolist())
    return SimpleNamespace(data=[data_item])


# ---------------------------------------------------------------------------
# Core fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def mock_openai_client():
    """Patch the shared OpenAI client with a fully async mock.

    The mock exposes:
        client.chat.completions.create(...)  -> _make_chat_response
        client.embeddings.create(...)        -> _make_embedding_response

    Tests can override return values via the returned mock object.
    """
    mock_client = AsyncMock()
    mock_client.chat.completions.create = AsyncMock(
        return_value=_make_chat_response('{"action":"reply","reason":"test","mood_deltas":{"happy":0,"angry":0,"irritated":0,"sad":0,"flirty":0}}')
    )
    mock_client.embeddings.create = AsyncMock(
        return_value=_make_embedding_response()
    )

    with patch("state.client.client", mock_client), \
         patch("planner.action_planner.client", mock_client), \
         patch("generator.msg_generator.client", mock_client), \
         patch("generator.lightweight_generator.client", mock_client), \
         patch("generator.help_generator.client", mock_client), \
         patch("generator.msgdecline_generator.client", mock_client), \
         patch("regulators.context_model.client", mock_client):
        yield mock_client


# ---------------------------------------------------------------------------
# User fixtures
# ---------------------------------------------------------------------------

class FakeUser:
    """Mimics main.UserModel without importing FastAPI dependencies."""

    def __init__(self, **overrides):
        defaults = dict(
            user_id=12345,
            name="TestPlayer",
            frndship_title="Casual",
            gold=1000,
            chips=50,
            current_energy=80,
            exp=2500,
            lvl=10,
            game_events=[],
            campaign_stage=5,
            current_quest=None,
            loadout=None,
        )
        defaults.update(overrides)
        for k, v in defaults.items():
            setattr(self, k, v)

    def get_stats(self) -> dict:
        identity_fields = {"user_id", "name", "frndship_title", "game_events", "current_quest", "loadout"}
        return {k: v for k, v in self.__dict__.items() if k not in identity_fields}


@pytest.fixture()
def fake_user():
    return FakeUser()


@pytest.fixture()
def stranger_user():
    return FakeUser(user_id=99999, name="Stranger", frndship_title="Stranger")


@pytest.fixture()
def bestie_user():
    return FakeUser(user_id=11111, name="Bestie", frndship_title="Bestie")


# ---------------------------------------------------------------------------
# Chat history fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def empty_history():
    return []


@pytest.fixture()
def short_history():
    return [
        {"author": "TestPlayer", "role": "user", "content": "hey veyra"},
        {"author": "Veyra", "role": "assistant", "content": "what do you want?"},
        {"author": "TestPlayer", "role": "user", "content": "just saying hi"},
    ]


@pytest.fixture()
def long_history():
    """20-message history to test trimming."""
    msgs = []
    for i in range(20):
        role = "user" if i % 2 == 0 else "assistant"
        author = "TestPlayer" if role == "user" else "Veyra"
        msgs.append({"author": author, "role": role, "content": f"message {i}"})
    return msgs


@pytest.fixture()
def help_follow_up_history():
    """History where the last assistant message was a help action."""
    return [
        {"author": "TestPlayer", "role": "user", "content": "how does battle work?"},
        {"author": "Veyra", "role": "assistant", "content": "Battle is a 1v1 PvP system...", "action": "help"},
        {"author": "TestPlayer", "role": "user", "content": "what about the loadout?"},
    ]


# ---------------------------------------------------------------------------
# Emotion model fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def fresh_emotion_model():
    """A clean EmotionModel with all moods at 0."""
    from regulators.emotion_model import EmotionModel
    return EmotionModel()


# ---------------------------------------------------------------------------
# Context model reset
# ---------------------------------------------------------------------------

@pytest.fixture(autouse=True)
def reset_context_history():
    """Clear the global context history before each test."""
    import regulators.context_model as cm
    original = cm.history[:]
    cm.history.clear()
    yield
    cm.history.clear()
    cm.history.extend(original)


# ---------------------------------------------------------------------------
# Planner response helpers
# ---------------------------------------------------------------------------

def planner_response(action: str, reason: str = "test", mood_deltas: dict | None = None):
    """Build a mock planner JSON response string."""
    import json
    deltas = mood_deltas or {"happy": 0, "angry": 0, "irritated": 0, "sad": 0, "flirty": 0}
    return json.dumps({"action": action, "reason": reason, "mood_deltas": deltas})


def set_planner_response(mock_client, action: str, reason: str = "test", mood_deltas: dict | None = None):
    """Configure the mock client to return a specific planner decision."""
    mock_client.chat.completions.create.return_value = _make_chat_response(
        planner_response(action, reason, mood_deltas)
    )


def set_generator_response(mock_client, text: str):
    """Configure the mock client to return a specific generated message."""
    mock_client.chat.completions.create.return_value = _make_chat_response(text)
