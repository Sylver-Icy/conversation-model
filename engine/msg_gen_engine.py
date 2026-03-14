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
from generator.msg_generator import veyra
from planner.action_planner import decide_action
from typing import Any


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

    @staticmethod
    def _normalize_history(chat_history: list | None) -> list[dict[str, Any]]:
        """Coerce incoming history into a stable list[dict] shape.

        Accepts mixed payloads (dicts, strings, unknown objects) and returns
        entries with at least: author, role, content.
        """
        normalized: list[dict[str, Any]] = []

        for item in chat_history or []:
            if isinstance(item, dict):
                role = str(item.get("role", "user"))
                author = str(item.get("author", "User" if role == "user" else "Veyra"))
                content = str(item.get("content", ""))

                entry: dict[str, Any] = {
                    "author": author,
                    "role": role,
                    "content": content,
                }
                if "action" in item:
                    entry["action"] = item.get("action")
                normalized.append(entry)
                continue

            if isinstance(item, str):
                normalized.append({"author": "User", "role": "user", "content": item})
                continue

            normalized.append({"author": "User", "role": "user", "content": str(item)})

        return normalized

    async def respond(self, message: str, user: "UserModel", chat_history: list, req_id: str):
        history = self._normalize_history(chat_history)

        decision = await decide_action(history, message, mood=veyra.get_active_mood())
        action = decision["action"]
        reason = decision.get("reason")

        # Apply mood: decay first (natural cooldown), then apply new deltas
        veyra.decay_mood(factor=0.97)
        veyra.update_mood(decision["mood_deltas"])
        veyra.log_state(req_id)
        current_mood = veyra.get_active_mood()

        handler = self.handlers.get(action, self.handlers["reply"])

        # For help action: only pass the previous reply when the last assistant
        # turn was also a help response — activates the follow-up chain.
        prev_reply = None
        if action == "help":
            last_assistant = next(
                (e for e in reversed(history) if e.get("role") == "assistant"),
                None,
            )
            if last_assistant and last_assistant.get("action") == "help":
                prev_reply = last_assistant["content"]

        return await handler.handle(
            message=message,
            user=user,
            chat_history=history,
            req_id=req_id,
            reason=reason,
            prev_reply=prev_reply,
            mood=current_mood,
        )