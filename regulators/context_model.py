from dotenv import load_dotenv
import os

from openai import OpenAI
import numpy as np

load_dotenv()  # loads .env
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


# each item: { "content": str, "embedding": np.array, "role": str, "user_name": str or None }
history = []

def embed_text(text: str):
    """Embed a piece of text using OpenAI embeddings."""
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=text
    )
    # convert to numpy array
    return np.array(response.data[0].embedding)

def cosine(a, b):
    return np.dot(a, b) / (np.linalg.norm(a) * np.linalg.norm(b))

def fetch_context(message: str, user_name: str, top_k=7, per_group=10, max_history=150):
    global history

    # Normalize input
    message = message.strip().lower()

    query_emb = embed_text(message)

    # PERSONAL POOL
    personal_pool = [
        item for item in history
        if item.get("user_name") == user_name
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
        if item.get("user_name") != user_name
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
            "user_name": user_name
        })

    if len(history) > max_history:
        history.pop(0)

    return final_contexts

def add_to_history(message: str, role = "assistant", user_name=None, max_history=150):
    # Normalize input
    message = message.strip().lower()
    emb = embed_text(message)
    if len(message) > 3:
        history.append({
            "content": message,
            "embedding": emb,
            "role": role,
            "user_name": user_name
        })
    if len(history) > max_history:
        history.pop(0)