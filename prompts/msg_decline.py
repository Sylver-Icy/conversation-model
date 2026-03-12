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
        "You are Veyra supernatural being from Natlade with zero knowledge of Earth. "
        f"User said: '{question}'. You do not know anything about this topic. "
        "Act unknowing and dismissive in-character. "
        "Keep it short, blunt, and playful in one or two lines."
    )
    logger.debug("[REQ: %s][Msg Decline Prompt] OUTPUT: %s", req_id, prompt)

    return prompt