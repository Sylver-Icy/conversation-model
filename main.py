"""
FastAPI entry point for the Veyra conversation model.
Receives chat requests, routes them through the action planner, and returns Veyra's reply.
"""
import os
import time
import uuid

from dotenv import load_dotenv

os.environ["TOKENIZERS_PARALLELISM"] = "false"
load_dotenv()

from fastapi import FastAPI, Header, HTTPException
from pydantic import BaseModel, Field
import uvicorn

from engine.msg_gen_engine import Engine
from logger import logger


def _require_env(name: str) -> str:
    value = os.getenv(name)
    if not value:
        raise RuntimeError(f"{name} is required to run the conversation model.")
    return value


_require_env("OPENAI_API_KEY")
SERVER_API_KEY = _require_env("CONVO_MODEL_API_KEY")

engine = Engine()


class UserModel(BaseModel):
    """User identity and game state."""
    user_id: int
    name: str
    frndship_title: str
    gold: int
    chips: int
    current_energy: int
    exp: int
    lvl: int
    game_events: list = Field(default_factory=list)
    campaign_stage: int
    current_quest: str | None = None
    loadout: str | None = None

    def get_stats(self) -> dict:
        """Extract only stat fields, excluding identity fields."""
        identity_fields = {"user_id", "name", "frndship_title", "game_events", "current_quest", "loadout"}
        return {k: v for k, v in self.model_dump().items() if k not in identity_fields}


class Message(BaseModel):
    message: str
    user: UserModel
    message_history: list = Field(default_factory=list)

app = FastAPI()

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/chat")
async def chat(req: Message, api_key: str = Header(default=None)):
    if api_key != SERVER_API_KEY:
        raise HTTPException(status_code=403, detail="Unauthorized")

    req_id = uuid.uuid4().hex[:6]

    # Log the incoming message
    logger.info("====== ========== REQUEST %s BEGIN ========== ======", req_id)
    logger.info("[REQ:%s] [Input][%s] TEXT: %s", req_id, req.user.user_id, req.message)

    start = time.time()

    try:
        reply = await engine.respond(
            message=req.message,
            user=req.user,
            chat_history=req.message_history,
            req_id=req_id
        )
    except (TimeoutError, RuntimeError, ValueError) as e:
        logger.error("[REQ:%s] Engine crashed: %s", req_id, e, exc_info=True)
        reply = "Veyra blacked out mid-thought 💀"

    duration = round((time.time() - start) * 1000, 2)

    logger.info("[REQ:%s] [Reply][%s] OUTPUT: %s | Took %s ms", req_id, req.user.user_id, reply, duration)
    logger.info("====== ========== REQUEST %s END ========== ======", req_id)

    return reply


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=8000)
