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
        label = main_router(message)

        # Branch 1 — Chitchat
        if label == "chitchat":
            return self.chat.generate(message)

        # Branch 2 — Study (do later)
        if label == "study":
            return self.msg_dlcn.generate(message)

        # Branch 3 — Commands
        # Only allow zero-arg commands
        ZERO_ARG = {"start_race", "shop", "inventory"}

        if label in ZERO_ARG:
            return f"running command: {label}"

        # If it's a command but NOT zero-arg → reject
        return self.cmd_dlcn.generate(message)