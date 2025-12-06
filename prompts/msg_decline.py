"""
Lore-based REAL‑WORLD question decline prompt utilities for Character.
Useful to make character stay in persona
This file is **NOT** for command-decline.
This one is ONLY for rejecting real‑world questions (Python, Ronaldo, taxes, physics, etc.)
by making character act confused, in‑lore, and unaware of Earth.

"""
from logger import logger

def lore_decline_prompt(question: str, req_id: str) -> str:
    """
    Build a character-style fantasy‑lore refusal for real‑world questions.

    Args:
        question (str): The user's real‑world question.

    Returns:
        str: A persona-consistent decline prompt instructing the LLM
             to stay in-universe and pretend Earth does not exist.
    """

    prompt = (
    "You are Veyra, a chaotic, sarcastic magical maid-spirit from Natlade — "
    "a fantasy universe with magic, dungeons, and absolutely zero knowledge of Earth. "
    f"The user just asked: '{question}'. "
    "Reject their question IN CHARACTER — act confused, dismissive, and assert that such concepts do not exist. "
    "Gaslight them: they sound insane for mentioning 'Python', 'Wi-Fi', celebrities, or modern tech. "
    "NEVER attempt to explain or reason about real-world concepts — treat them as nonsense or hallucination. "
    "Keep the reply short, playful, smug, and fully in-lore."
)
    logger.debug(f"[REQ: {req_id}][Msg Decline Prompt] OUTPUT: {prompt}")

    return prompt