from engine.action_handlers import (
    ActUnknowingActionHandler,
    AskQuestionActionHandler,
    ChangeTopicActionHandler,
    DryReplyActionHandler,
    EndConvoActionHandler,
    GameTopicActionHandler,
    HelpActionHandler,
    IgnoreActionHandler,
    ReplyActionHandler,
    StatCheckActionHandler,
)
from planner.action_planner import decide_action


class Engine:
    def __init__(self):
        self.handlers = {
            "ignore": IgnoreActionHandler(),
            "reply": ReplyActionHandler(),
            "dry_reply": DryReplyActionHandler(),
            "end_convo": EndConvoActionHandler(),
            "change_topic": ChangeTopicActionHandler(),
            "ask_question": AskQuestionActionHandler(),
            "help": HelpActionHandler(),
            "stat_check": StatCheckActionHandler(),
            "game_topic": GameTopicActionHandler(),
            "act_unknowing": ActUnknowingActionHandler(),
        }

    async def respond(self, message: str, user_id: int, user_name: str, frndship_title: str, chat_history: list, req_id: str):
        decision = decide_action(chat_history or [], message)
        action = decision["action"]
        handler = self.handlers.get(action, self.handlers["reply"])

        return await handler.handle(
            message=message,
            user_id=user_id,
            user_name=user_name,
            frndship_title=frndship_title,
            chat_history=chat_history,
            req_id=req_id,
            decision=decision,
        )