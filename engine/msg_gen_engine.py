from core.router import main_router

from generator.msg_generator import ChatGenerator
from generator.commanddecline_generator import CommandDeclineGenerator
from generator.msgdecline_generator import MsgDeclineGenerator


class Engine:
    def __init__(self):
        self.chat = ChatGenerator()
        self.cmd_dlcn = CommandDeclineGenerator()
        self.msg_dlcn = MsgDeclineGenerator()

    async def respond(self, message: str, user_id: int, user_name: str, frndship_title: str, chat_history: list, req_id: str):
        route_type, label = main_router(message, req_id)

        # Branch 1 — Chitchat
        if route_type == "intent":
            return (
                await self.chat.generate(message, user_id, user_name, frndship_title, chat_history, req_id)
                if label == "chitchat"
                else await self.msg_dlcn.generate(message, req_id)
            )

        # Branch 3 — Commands
        if route_type == "command":
            if label != "other_command":
                return label

            return await self.cmd_dlcn.generate(message, req_id)