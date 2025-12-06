"""
Minimal test runner for the intent classification system.
Reads user input from the console and prints the predicted intent.
This file is just a quick  check for the classifier.
"""
from engine.msg_gen_engine import Engine

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI
from pydantic import BaseModel
import uvicorn

user = Engine()

class Message(BaseModel):
    text: str
    frndship_title: str
    user_id: int
    user_name: str
    message_history: list


app = FastAPI()

@app.post("/chat")
async def chat(req: Message):

        reply = await user.respond(
            req.text,
            frndship_title=req.frndship_title,
            user_id=req.user_id,
            user_name=req.user_name,
            chat_history=req.message_history
        )
        return reply


if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)