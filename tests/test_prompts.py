"""
Unit tests for prompt builder functions.
"""

import pytest
from prompts.behaviour import FRNDSHIP_MAP
from prompts.character_profile import create_character_prompt
from prompts.lightweight_prompts import (
    dry_reply_prompt,
    end_convo_prompt,
    change_topic_prompt,
    ask_question_prompt,
    game_topic_prompt,
    stat_check_prompt,
)
from prompts.msg_decline import lore_decline_prompt


# ---------------------------------------------------------------------------
# Behaviour map
# ---------------------------------------------------------------------------

class TestFrndshipMap:
    def test_all_titles_have_descriptions(self):
        expected = ["Stranger", "Acquaintance", "Casual", "Friend",
                    "Close Friend", "Bestie", "Veyra's favourite 💖"]
        for title in expected:
            assert title in FRNDSHIP_MAP
            assert len(FRNDSHIP_MAP[title]) > 0


# ---------------------------------------------------------------------------
# Character profile prompt
# ---------------------------------------------------------------------------

class TestCharacterPrompt:
    def test_contains_user_name(self):
        prompt = create_character_prompt(
            user_name="Alex", frndship_title="Casual", mood="happy",
            chat_context=[], chat_history=[], req_id="t01"
        )
        assert "Alex" in prompt

    def test_contains_mood(self):
        prompt = create_character_prompt(
            user_name="Test", frndship_title="Friend", mood="angry",
            chat_context=[], chat_history=[], req_id="t02"
        )
        assert "angry" in prompt

    def test_contains_friendship_behavior(self):
        prompt = create_character_prompt(
            user_name="Test", frndship_title="Bestie", mood="neutral",
            chat_context=[], chat_history=[], req_id="t03"
        )
        assert FRNDSHIP_MAP["Bestie"] in prompt

    def test_includes_context_and_history(self):
        ctx = ["remembered: you called me cute last time"]
        hist = [{"author": "User", "role": "user", "content": "hey"}]
        prompt = create_character_prompt(
            user_name="Test", frndship_title="Casual", mood="happy",
            chat_context=ctx, chat_history=hist, req_id="t04"
        )
        assert "remembered: you called me cute last time" in prompt
        assert "hey" in prompt

    def test_includes_recent_game_events(self):
        prompt = create_character_prompt(
            user_name="Test",
            frndship_title="Casual",
            mood="happy",
            chat_context=[],
            chat_history=[],
            req_id="t04b",
            game_events=[{"summary": "Won the lottery with 3 ticket(s) and pocketed 1200 gold."}],
        )
        assert "Won the lottery with 3 ticket(s) and pocketed 1200 gold." in prompt

    def test_never_mentions_ai_or_bot(self):
        prompt = create_character_prompt(
            user_name="Test", frndship_title="Casual", mood="neutral",
            chat_context=[], chat_history=[], req_id="t05"
        )
        # The prompt should instruct Veyra to NOT be AI, not casually mention "AI"
        assert "not" in prompt.lower() or "never" in prompt.lower()


# ---------------------------------------------------------------------------
# Lightweight prompts
# ---------------------------------------------------------------------------

class TestDryReplyPrompt:
    def test_contains_message_and_friendship(self):
        prompt = dry_reply_prompt("lol ok", "happy", "Casual", [])
        assert "lol ok" in prompt
        assert "Casual" in prompt

    def test_includes_mood_when_provided(self):
        prompt = dry_reply_prompt("whatever", "angry", "Friend", [])
        assert "angry" in prompt

    def test_no_mood_does_not_crash(self):
        prompt = dry_reply_prompt("test", None, "Stranger", [])
        assert "test" in prompt

    def test_includes_recent_history(self):
        hist = [
            {"author": "User", "content": "msg1"},
            {"author": "Veyra", "content": "msg2"},
        ]
        prompt = dry_reply_prompt("test", None, "Casual", hist)
        assert "msg1" in prompt
        assert "msg2" in prompt


class TestEndConvoPrompt:
    def test_contains_goodbye_instruction(self):
        prompt = end_convo_prompt("bye!", "Casual", "happy", [])
        assert "bye" in prompt.lower() or "ending" in prompt.lower()


class TestChangeTopicPrompt:
    def test_contains_natlade_topics(self):
        prompt = change_topic_prompt("...", "Casual", None, [])
        assert "Bardok" in prompt or "battle" in prompt or "quest" in prompt


class TestAskQuestionPrompt:
    def test_contains_instruction_to_ask(self):
        prompt = ask_question_prompt("hi", "Friend", "happy", [])
        assert "ask" in prompt.lower()


class TestGameTopicPrompt:
    def test_contains_game_reference(self):
        prompt = game_topic_prompt("Bardok is strong", "Casual", None, [])
        assert "Bardok is strong" in prompt


class TestStatCheckPrompt:
    def test_includes_stats(self):
        stats = {"gold": 1000, "lvl": 10, "exp": 2500}
        prompt = stat_check_prompt("how much gold?", stats, "Alex")
        assert "gold" in prompt
        assert "1000" in prompt
        assert "Alex" in prompt

    def test_warns_not_to_invent_stats(self):
        prompt = stat_check_prompt("test", {"gold": 50}, "Test")
        assert "INVENT" in prompt or "invent" in prompt


# ---------------------------------------------------------------------------
# Lore decline prompt
# ---------------------------------------------------------------------------

class TestLoreDeclinePrompt:
    def test_contains_user_question(self):
        prompt = lore_decline_prompt("who is Elon Musk?", "t01")
        assert "Elon Musk" in prompt

    def test_returns_string(self):
        prompt = lore_decline_prompt("what is Python?", "t02")
        assert isinstance(prompt, str)
        assert len(prompt) > 0
