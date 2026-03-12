from __future__ import annotations

from typing import Any

from generator.msgdecline_generator import MsgDeclineGenerator
from generator.lightweight_generator import LightweightGenerator


class BaseActionHandler:
    action_name = "reply"

    async def handle(self, **_: Any) -> str | None:
        return self.action_name


class IgnoreActionHandler(BaseActionHandler):
    action_name = "ignore"

    async def handle(self, **_: Any) -> None:
        return None


class ReplyActionHandler(BaseActionHandler):
    action_name = "reply"


class DryReplyActionHandler(BaseActionHandler):
    action_name = "dry_reply"

    def __init__(self):
        self.gen = LightweightGenerator()

    async def handle(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        return await self.gen.dry_reply(
            message=kwargs.get("message", ""),
            mood=None,  # not wired yet
            frndship_title=user.frndship_title if user else "Stranger",
            chat_history=kwargs.get("chat_history", []),
            req_id=kwargs.get("req_id", "000"),
        )


class EndConvoActionHandler(BaseActionHandler):
    action_name = "end_convo"

    def __init__(self):
        self.gen = LightweightGenerator()

    async def handle(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        return await self.gen.end_convo(
            message=kwargs.get("message", ""),
            frndship_title=user.frndship_title if user else "Stranger",
            mood=None,  # not wired yet
            chat_history=kwargs.get("chat_history", []),
            req_id=kwargs.get("req_id", "000"),
        )


class ChangeTopicActionHandler(BaseActionHandler):
    action_name = "change_topic"

    def __init__(self):
        self.gen = LightweightGenerator()

    async def handle(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        return await self.gen.change_topic(
            message=kwargs.get("message", ""),
            frndship_title=user.frndship_title if user else "Stranger",
            mood=None,  # not wired yet
            chat_history=kwargs.get("chat_history", []),
            req_id=kwargs.get("req_id", "000"),
        )


class AskQuestionActionHandler(BaseActionHandler):
    action_name = "ask_question"

    def __init__(self):
        self.gen = LightweightGenerator()

    async def handle(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        return await self.gen.ask_question(
            message=kwargs.get("message", ""),
            frndship_title=user.frndship_title if user else "Stranger",
            mood=None,  # not wired yet
            chat_history=kwargs.get("chat_history", []),
            req_id=kwargs.get("req_id", "000"),
        )


class HelpActionHandler(BaseActionHandler):
    action_name = "help"


class StatCheckActionHandler(BaseActionHandler):
    action_name = "stat_check"

    def __init__(self):
        self.gen = LightweightGenerator()

    async def handle(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        # Use the .get_stats() method from UserModel
        user_stats = user.get_stats() if user else {}

        return await self.gen.stat_check(
            message=kwargs.get("message", ""),
            user_name=user.name if user else "Player",
            user_stats=user_stats,
            req_id=kwargs.get("req_id", "000"),
        )


class GameTopicActionHandler(BaseActionHandler):
    action_name = "game_topic"

    def __init__(self):
        self.gen = LightweightGenerator()

    async def handle(self, **kwargs: Any) -> str:
        user = kwargs.get("user")
        return await self.gen.game_topic(
            message=kwargs.get("message", ""),
            frndship_title=user.frndship_title if user else "Stranger",
            mood=None,  # not wired yet
            chat_history=kwargs.get("chat_history", []),
            req_id=kwargs.get("req_id", "000"),
        )


class ActUnknowingActionHandler(BaseActionHandler):
    action_name = "act_unknowing"

    def __init__(self):
        self.msg_decline = MsgDeclineGenerator()

    async def handle(self, **kwargs: Any) -> str:
        return await self.msg_decline.generate(
            msg=kwargs.get("message", ""),
            req_id=kwargs.get("req_id", "000"),
        )