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

app = FastAPI()

@app.post("/chat")
def chat(req: Message):
    return {"reply": user.respond(req.text)}

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)