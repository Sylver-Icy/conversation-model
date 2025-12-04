from core.router import main_router

from generator.msg_generator import ChatGenerator
from generator.commanddecline_generator import CommandDeclineGenerator
from generator.msgdecline_generator import MsgDeclineGenerator


class Engine:
    def __init__(self):
        self.chat = ChatGenerator()
        self.cmd_dlcn = CommandDeclineGenerator()
        self.msg_dlcn = MsgDeclineGenerator()

    def respond(self, message: str):
        route_type, label = main_router(message)

        # Branch 1 — Chitchat
        if route_type == "intent":
            return (
                self.chat.generate(message)
                if label == "chitchat"
                else self.msg_dlcn.generate(message)
            )

        # Branch 3 — Commands
        if route_type == "command":
            if label != "other_command":
                return f"running command: {label}"

            return self.cmd_dlcn.generate(message)