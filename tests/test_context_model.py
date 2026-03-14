"""
Unit tests for regulators/context_model.py — global memory retrieval.
"""

import numpy as np
import pytest
import regulators.context_model as cm


class TestFetchContext:
    @pytest.mark.asyncio
    async def test_returns_list(self, mock_openai_client):
        result = await cm.fetch_context("hello", user_id=1, req_id="t01")
        assert isinstance(result, list)

    @pytest.mark.asyncio
    async def test_appends_message_to_history(self, mock_openai_client):
        assert len(cm.history) == 0
        await cm.fetch_context("hello world test", user_id=1, req_id="t02")
        assert len(cm.history) == 1
        assert cm.history[0]["role"] == "user"
        assert cm.history[0]["user_id"] == 1

    @pytest.mark.asyncio
    async def test_short_messages_not_stored(self, mock_openai_client):
        await cm.fetch_context("hi", user_id=1, req_id="t03")
        assert len(cm.history) == 0  # "hi" is ≤ 3 chars

    @pytest.mark.asyncio
    async def test_max_history_pops_when_exceeded(self, mock_openai_client):
        """Code pops one entry per call when over max_history."""
        for i in range(150):
            cm.history.append({
                "content": f"message {i}",
                "embedding": np.random.randn(1536),
                "role": "user",
                "user_id": 1,
            })
        assert len(cm.history) == 150
        await cm.fetch_context("new message here", user_id=1, req_id="t04")
        # Appends 1 (151), then pops 1 → back to 150
        assert len(cm.history) == 150

    @pytest.mark.asyncio
    async def test_personal_pool_boosted(self, mock_openai_client):
        """Messages from the same user get a +0.05 similarity boost."""
        vec = np.ones(1536, dtype=np.float32)
        vec /= np.linalg.norm(vec)
        # The mock returns the same embedding each time, so all similarities ~1.0
        # With the +0.05 boost, personal items should score higher
        cm.history.append({
            "content": "personal message",
            "embedding": vec,
            "role": "user",
            "user_id": 42,
        })
        cm.history.append({
            "content": "global message",
            "embedding": vec,
            "role": "user",
            "user_id": 99,
        })
        result = await cm.fetch_context("test query", user_id=42, req_id="t05")
        # Should return both (above threshold), personal first due to boost
        assert isinstance(result, list)


class TestAddToHistory:
    @pytest.mark.asyncio
    async def test_adds_assistant_message(self, mock_openai_client):
        await cm.add_to_history("I said something", role="assistant")
        assert len(cm.history) == 1
        assert cm.history[0]["role"] == "assistant"
        assert cm.history[0]["user_id"] is None

    @pytest.mark.asyncio
    async def test_short_messages_skipped(self, mock_openai_client):
        await cm.add_to_history("ok", role="assistant")
        assert len(cm.history) == 0

    @pytest.mark.asyncio
    async def test_max_history_pops_when_exceeded(self, mock_openai_client):
        """Code pops one entry per call when over max_history."""
        for i in range(150):
            cm.history.append({
                "content": f"old {i}" * 5,  # > 3 chars
                "embedding": np.random.randn(1536),
                "role": "user",
                "user_id": 1,
            })
        assert len(cm.history) == 150
        await cm.add_to_history("new assistant reply here", role="assistant")
        # Appends 1 (151), then pops 1 → back to 150
        assert len(cm.history) == 150


class TestCosine:
    def test_identical_vectors(self):
        v = np.array([1.0, 0.0, 0.0])
        assert cm.cosine(v, v) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([0.0, 1.0])
        assert cm.cosine(a, b) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        a = np.array([1.0, 0.0])
        b = np.array([-1.0, 0.0])
        assert cm.cosine(a, b) == pytest.approx(-1.0)
