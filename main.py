"""
Minimal test runner for the intent classification system.
Reads user input from the console and prints the predicted intent.
This file is just a quick  check for the classifier.
"""
import uuid
from dotenv import load_dotenv
import time


from engine.msg_gen_engine import Engine
from logger import logger

import os
os.environ["TOKENIZERS_PARALLELISM"] = "false"

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel
import uvicorn

load_dotenv()

user = Engine()

class Message(BaseModel):
    text: str
    frndship_title: str
    user_id: int
    user_name: str
    message_history: list

app = FastAPI()

@app.post("/chat")
async def chat(req: Message, api_key: str = Header(default=None)):
    server_key = os.getenv("API_KEY")

    if api_key != server_key:
        raise HTTPException(status_code=403, detail="Unauthorized")

    req_id = uuid.uuid4().hex[:6]

    # Log the incoming message
    logger.info(f"====== ========== REQUEST {req_id} BEGIN ========== ======")
    logger.info(f"[REQ:{req_id}] [Input][{req.user_id}] TEXT: {req.text}")

    start = time.time()

    try:
        reply = await user.respond(
            req.text,
            frndship_title=req.frndship_title,
            user_id=req.user_id,
            user_name=req.user_name,
            chat_history=req.message_history,
            req_id=req_id
        )
    except Exception as e:
        logger.error(f"[REQ:{req_id}] Engine crashed: {e}", exc_info=True)
        reply = "Veyra blacked out mid-thought 💀"

    duration = round((time.time() - start) * 1000, 2)

    logger.info(f"[REQ:{req_id}] [Reply][{req.user_id}] OUTPUT: {reply} | Took {duration}ms")
    logger.info(f"====== ========== REQUEST {req_id} END ========== ======")

    return reply


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)