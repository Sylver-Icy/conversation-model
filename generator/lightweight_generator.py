"""
Lightweight LLM-based action generators.
Handles concurrent low-complexity responses with minimal prompt engineering.
"""

from prompts.lightweight_prompts import (
    dry_reply_prompt,
    end_convo_prompt,
    change_topic_prompt,
    ask_question_prompt,
    game_topic_prompt,
    stat_check_prompt,
)
from state.client import client
from openai import OpenAIError
from logger import logger


class LightweightGenerator:
    """Single generator for all lightweight actions using gpt-5-mini."""

    def __init__(self):
        self.client = client

    async def _call(self, prompt: str, req_id: str) -> str:
        """Shared LLM call for all lightweight actions."""
        try:
            response = await self.client.chat.completions.create(
                model="gpt-5-mini",
                messages=[{"role": "user", "content": prompt}],
                max_completion_tokens=1500,
            )
            return response.choices[0].message.content or "..."
        except OpenAIError as e:
            logger.error("[REQ: %s] LightweightGenerator error: %s", req_id, e)
            return "my thoughts scattered—what was that?"

    async def dry_reply(
        self,
        message: str,
        mood: str | None,
        frndship_title: str,
        chat_history: list,
        req_id: str,
        **_
    ) -> str:
        """Short dismissive reply."""
        prompt = dry_reply_prompt(message, mood, frndship_title, chat_history)
        return await self._call(prompt, req_id)

    async def end_convo(
        self,
        message: str,
        frndship_title: str,
        mood: str | None,
        chat_history: list,
        req_id: str,
        **_
    ) -> str:
        """In-character goodbye."""
        prompt = end_convo_prompt(message, frndship_title, mood, chat_history)
        return await self._call(prompt, req_id)

    async def change_topic(
        self,
        message: str,
        frndship_title: str,
        mood: str | None,
        chat_history: list,
        req_id: str,
        **_
    ) -> str:
        """Introduce a new in-universe topic."""
        prompt = change_topic_prompt(message, frndship_title, mood, chat_history)
        return await self._call(prompt, req_id)

    async def ask_question(
        self,
        message: str,
        frndship_title: str,
        mood: str | None,
        chat_history: list,
        req_id: str,
        **_
    ) -> str:
        """Ask user something to continue."""
        prompt = ask_question_prompt(message, frndship_title, mood, chat_history)
        return await self._call(prompt, req_id)

    async def game_topic(
        self,
        message: str,
        frndship_title: str,
        mood: str | None,
        chat_history: list,
        req_id: str,
        **_
    ) -> str:
        """Casual chat about game topics."""
        prompt = game_topic_prompt(message, frndship_title, mood, chat_history)
        return await self._call(prompt, req_id)

    async def stat_check(
        self,
        message: str,
        user_name: str,
        user_stats: dict,
        req_id: str,
        frndship_title: str = "Stranger",
        **_
    ) -> str:
        """Narrate user stats in-character."""
        prompt = stat_check_prompt(message, user_stats, user_name, frndship_title)
        return await self._call(prompt, req_id)
