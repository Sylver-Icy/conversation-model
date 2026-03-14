"""
Unit tests for regulators/emotion_model.py — pure state management, no LLM.
"""

import pytest
from regulators.emotion_model import EmotionModel


class TestMoodUpdate:
    def test_apply_positive_deltas(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 3, "flirty": 1.5})
        assert em.mood_state["happy"] == 3.0
        assert em.mood_state["flirty"] == 1.5
        assert em.mood_state["angry"] == 0.0  # unchanged

    def test_apply_negative_deltas(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 5})
        em.update_mood({"happy": -2})
        assert em.mood_state["happy"] == 3.0

    def test_clamp_upper_bound(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"angry": 15})
        assert em.mood_state["angry"] == 10.0

    def test_clamp_lower_bound(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"sad": -15})
        assert em.mood_state["sad"] == -10.0

    def test_ignores_unknown_keys(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"rage": 5, "happy": 1})
        assert em.mood_state["happy"] == 1.0
        assert "rage" not in em.mood_state

    def test_empty_deltas_no_change(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({})
        assert all(v == 0.0 for v in em.mood_state.values())


class TestMoodDecay:
    def test_decay_reduces_values(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 10, "angry": -10})
        em.decay_mood(factor=0.5)
        assert em.mood_state["happy"] == 5.0
        assert em.mood_state["angry"] == -5.0

    def test_decay_default_factor(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"irritated": 10})
        em.decay_mood()  # default 0.97
        assert em.mood_state["irritated"] == pytest.approx(9.7, abs=0.01)

    def test_repeated_decay_converges_to_zero(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 10})
        for _ in range(200):
            em.decay_mood(factor=0.95)
        assert abs(em.mood_state["happy"]) < 0.01

    def test_zero_moods_stay_zero(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.decay_mood(factor=0.97)
        assert all(v == 0.0 for v in em.mood_state.values())


class TestGetActiveMood:
    def test_returns_highest_mood(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 2, "angry": 5, "flirty": 1})
        assert em.get_active_mood() == "angry"

    def test_all_zero_returns_deterministic(self, fresh_emotion_model):
        em = fresh_emotion_model
        # When all moods are 0, max() returns the first key iterated
        mood = em.get_active_mood()
        assert mood in em.mood_state

    def test_negative_moods_lowest_are_not_dominant(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": -5, "angry": -3, "flirty": 1})
        assert em.get_active_mood() == "flirty"

    def test_mood_tracks_after_multiple_updates(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 5})
        assert em.get_active_mood() == "happy"
        em.update_mood({"angry": 8})
        assert em.get_active_mood() == "angry"
        em.update_mood({"angry": -10})  # angry goes to -2
        assert em.get_active_mood() == "happy"


class TestLogState:
    def test_log_state_does_not_crash(self, fresh_emotion_model):
        em = fresh_emotion_model
        em.update_mood({"happy": 3})
        em.log_state("test-001")  # should not raise
