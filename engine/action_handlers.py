from __future__ import annotations

from typing import Any

from generator.msgdecline_generator import MsgDeclineGenerator


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


class EndConvoActionHandler(BaseActionHandler):
    action_name = "end_convo"


class ChangeTopicActionHandler(BaseActionHandler):
    action_name = "change_topic"


class AskQuestionActionHandler(BaseActionHandler):
    action_name = "ask_question"


class HelpActionHandler(BaseActionHandler):
    action_name = "help"


class StatCheckActionHandler(BaseActionHandler):
    action_name = "stat_check"


class GameTopicActionHandler(BaseActionHandler):
    action_name = "game_topic"


class ActUnknowingActionHandler(BaseActionHandler):
    action_name = "act_unknowing"

    def __init__(self):
        self.msg_decline = MsgDeclineGenerator()

    async def handle(self, **kwargs: Any) -> str:
        return await self.msg_decline.generate(
            msg=kwargs.get("message", ""),
            req_id=kwargs.get("req_id", "000"),
        )