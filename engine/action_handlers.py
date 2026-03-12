from __future__ import annotations

from typing import Any


class BaseActionHandler:
    action_name = "reply"

    async def handle(self, **_: Any) -> str:
        return self.action_name


class IgnoreActionHandler(BaseActionHandler):
    action_name = "ignore"


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