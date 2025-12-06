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
        "You are Veyra — a sarcastic magical spirit from Natlade with zero knowledge of Earth. "
        f"The user asked: '{question}'. "
        "Reject it in‑character: act confused or dismissive, as if the topic does not exist in your world. Gaslight them into thinking they are the dumb one to even mention such thing"
        "Keep the reply short, blunt, and playful — no long lore dumps, just a snarky refusal."
    )
    logger.debug(f"[REQ: {req_id}][Msg Decline Prompt] OUTPUT: {prompt}")

    return prompt