from logger import logger

import numpy as np

from state.client import client

# each item: { "content": str, "embedding": np.array, "role": str, "user_id": str or None }
history = []

async def embed_text(text: str):
    """Embed a piece of text using OpenAI embeddings."""
    response = await client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    # convert to numpy array
    return np.array(response.data[0].embedding)

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

async def fetch_context(message: str, user_id: int, req_id: str, top_k=7, per_group=10, max_history=150):
    global history

    # Normalize input
    message = message.strip().lower()

    query_emb = await embed_text(message)

    # PERSONAL POOL
    personal_pool = [
        item for item in history
        if item.get("user_id") == user_id
    ]

    personal_scored = []
    for item in personal_pool:
        sim = cosine(query_emb, item["embedding"])
        personal_scored.append((sim, item["content"]))

    personal_scored.sort(key=lambda x: x[0], reverse=True)
    personal_top = personal_scored[:per_group]

    # GLOBAL POOL (everyone except user)
    global_pool = [
        item for item in history
        if item.get("user_id") != user_id
    ]

    global_scored = []
    for item in global_pool:
        sim = cosine(query_emb, item["embedding"])
        global_scored.append((sim, item["content"]))

    global_scored.sort(key=lambda x: x[0], reverse=True)
    global_top = global_scored[:per_group]

    # MERGE + RE-RANK
    combined = personal_top + global_top
    combined.sort(key=lambda x: x[0], reverse=True)

    final_contexts = [content for _, content in combined[:top_k]]

    # Skip useless entries (too short/no signal)
    if len(message) > 3:
        history.append({
            "content": message,
            "embedding": query_emb,
            "role": "user",
            "user_id": user_id
        })

    if len(history) > max_history:
        history.pop(0)
    logger.info(f"[REQ: {req_id} [Context] {final_contexts}")
    return final_contexts

def add_to_history(message: str, role = "assistant", user_id=None, max_history=150):
    # Normalize input
    message = message.strip().lower()
    emb = embed_text(message)
    if len(message) > 3:
        history.append({
            "content": message,
            "embedding": emb,
            "role": role,
            "user_id": user_id
        })
    if len(history) > max_history:
        history.pop(0)