"""Conversation action planner.

This module asks an LLM to choose a conversational action before reply generation.
It does not generate the reply text itself.
"""

from __future__ import annotations

import asyncio
import json
import os
from typing import Any

from dotenv import load_dotenv
from generator.help_generator import HelpGenerator
from openai import OpenAI

load_dotenv()

MOVES: dict[str, str] = {
    "ignore": "when the message does not require a response (e.g. 'lol', 'ok')",
    "reply": "normal conversational reply",
    "dry_reply": "short or dismissive response",
    "end_convo": "when someone says bye or the conversation naturally ends",
    "change_topic": "conversation stalled, introduce a new topic",
    "ask_question": "ask the user something to continue conversation",
    # --- Veyra-specific moves ---
    "help": (
        "user is asking how a Veyra system works — e.g. 'what is battle?', "
        "'how do I use the shop?', 'how does crafting work?', 'what does a lootbox do?'"
    ),
    "stat_check": (
        "user is asking about their own in-game numbers — e.g. 'how much gold do I have?', "
        "'what level am I?', 'how much EXP until next level?', 'how many tickets do I have?'"
    ),
    "game_topic": (
        "user is discussing Veyra game topics without asking for help or stats try to not use this unless sure this is a game topic this is lowest priority move — "
        "e.g. 'Bardok is so strong', 'bread prices are crazy', 'knight job is the best', "
        "'Stage 10 took me forever'"
    ),
    "act_unknowing": (
        "user explicitly references something from the real world that does not exist in Natlade — "
        "e.g. real people (Ronaldo, Trump, Elon Musk, any real celebrity or athlete), "
        "other games (Genshin Impact, Minecraft, Fortnite, any non-Veyra game), "
        "Earth locations, real-world events, or any figure from real life. "
        "Use SPARINGLY — only when the real-world reference is unambiguous and explicit. "
        "Do NOT use for vague questions, abstract topics, or anything that could plausibly exist in Natlade."
    ),
}

# ---------------------------------------------------------------------------
# Veyra game context injected into every planning request so the LLM can
# correctly distinguish help/stat_check/game_topic from generic replies.
# ---------------------------------------------------------------------------
VEYRA_CONTEXT = """
=== VEYRA DISCORD RPG — SYSTEM SUMMARY ===

WORLD & CHARACTER
- Veyra is a sarcastic, dominant supernatural being from the magical realm of Natlade — she is NOT a bot or AI.
- Natlade is a self-contained fictional world with its own economy, combat, crafting, alchemy, and social systems.
- Veyra has zero knowledge of Earth. Real-world people (politicians, athletes, celebrities), other video games
  (Genshin Impact, Minecraft, etc.), Earth geography, history, science, and current events DO NOT EXIST in Natlade.
- Entities that exist only in Natlade: Bardok (final boss), Veyra's Grimoire, Veil of Darkness, Bardok's Claymore,
  Earthquake (ability), campaign stages, jobs (knight/digger/miner/thief/explorer), shop, marketplace,
  alchemy, lootboxes, quests, casino chips.
- If a user mentions something that clearly comes from Earth or another game, use act_unknowing.

Veyra is a Discord RPG bot with the following core systems:

ECONOMY
- Gold-based currency. Sources: jobs (knight, Digger, Miner, Thief),
  quests , lootboxes , marketplace sales, battle victories.
- Sinks: shop purchases, marketplace fees (7%), transfer fees (5%), battle bets, building purchases.
- Commands: /check wallet, /transfer, /leaderboard, /loan, !repayloan

INVENTORY & SHOP
- Items have rarities: Common, Rare, Epic, Legendary, Paragon.
- Daily shop refreshes every midnight UTC with random items.
- Commands: /check inventory, /shop, /marketplace list, /marketplace buy

COMBAT
- Turn-based 1v1 PvP and PvE campaign. Players equip a weapon + spell loadout.
- Battle winner takes 90% of total bet pot.
- Campaign: 15 stages. Stages 1-10 fight Veyra AI; clearing Stage 10 unlocks Veyra's Grimoire & Veil of Darkness.
  Stages 11-15 fight Bardok; clearing Stage 15 unlocks Bardok's Claymore & Earthquake.
- Commands: /battle, /campaign, /loadout

JOBS & ENERGY
- Energy regenerates every 6 minutes. Jobs cost energy.
- Jobs: knight, digger, miner, thief, explorer.
- Commands: /work <job>

CRAFTING & ALCHEMY
- Mine ores → smelt into bars → sell or use. Requires Coal.
- Upgrade smelter building to unlock higher-tier recipes.
- Alchemy: brew potions with ingredients; potions apply timed effects and strain.
- Commands: /smelt, /brew, /upgrade

QUESTS
- Time-limited objectives (battle, jobs, casino, market, crafting). Streak bonuses apply.
- Commands: /quest, /claimquest

EXPERIENCE & LEVELING
- Gain EXP through battles, jobs, quests, mini-games.
- Commands: /check profile, /check exp

FRIENDSHIP
- Relationship EXP with Veyra through daily interactions. Resets cap at midnight UTC.
- Commands: !helloVeyra, /check friendship

MINI-GAMES & GAMBLING
- Daily number guessing game (!play), coin flip, animal racing, wordle solver.
- Casino: chip-based slots, roulette, coin flip, dungeon raid. Chips ≠ gold.
- Lottery: 10 tickets weekdays, 50 tickets weekends. Commands: /lottery, /casino

REGISTRATION
- New players: !helloVeyra → tutorial (check wallet → !play → /shop → /work).
- Commands: /help, /commandhelp <command>

PLAYER STATS (user_stats table)
- Tracked: battles_won, races_won, longest_quest_streak, weekly_rank1_count, biggest_lottery_win.
=== END VEYRA CONTEXT ===
"""

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))


def _trim_history(history: list[dict[str, Any]], max_items: int = 10) -> list[dict[str, Any]]:
    """Return only the most recent history entries to control prompt size."""
    return history[-max_items:]


def _serialize_history(history: list[dict[str, Any]]) -> str:
    """Render history into a stable JSON string for prompt injection."""
    return json.dumps(history, ensure_ascii=True, indent=2)


def _safe_parse_decision(raw_content: str) -> dict[str, str]:
    """Parse and validate LLM JSON output into the expected decision shape."""
    try:
        data = json.loads(raw_content)
    except json.JSONDecodeError:
        start = raw_content.find("{")
        end = raw_content.rfind("}")
        if start != -1 and end != -1 and end > start:
            data = json.loads(raw_content[start : end + 1])
        else:
            data = {}

    action = str(data.get("action", "")).strip()
    reason = str(data.get("reason", "")).strip()

    if action not in MOVES:
        action = "reply"
        reason = "Fallback: model returned an invalid action."

    if not reason:
        reason = "Selected the best-fit action for the current flow."

    return {"action": action, "reason": reason}


def decide_action(history: list[dict], current_message: str) -> dict:
    """Choose the best conversational action for the current message.

    Args:
        history: Conversation history entries. Each entry should look like:
            {"author": "Name", "role": "user|assistant", "content": "..."}
        current_message: Incoming user message text.

    Returns:
        A dictionary with keys:
            - action: one action from MOVES
            - reason: one short explanation sentence
    """
    recent_history = _trim_history(history, max_items=10)

    system_prompt = (
        "You are a conversation action planner for a Discord-style group chat built around "
        "the Veyra RPG bot. Your task is to choose exactly one action from a predefined move set. "
        "You are NOT allowed to generate a conversational reply. "
        "Return JSON only with keys: action, reason.\n\n"
        + VEYRA_CONTEXT
        + "\n\nUse the Veyra context above to correctly identify when a message is asking "
        "for system help (help), asking about their own stats/currency (stat_check), "
        "or casually discussing game topics (game_topic). "
        "Only fall back to reply/dry_reply/etc. when none of the Veyra-specific moves apply. "
        "Use act_unknowing when a user references something explicitly from the real world (real people, "
        "other games, Earth locations) — but prefer other actions if the message is ambiguous or could fit Natlade."
    )

    user_prompt = (
        "Choose the best action from this MOVES dictionary:\n"
        f"{json.dumps(MOVES, ensure_ascii=True, indent=2)}\n\n"
        "Rules:\n"
        "1) action must be exactly one key from MOVES.\n"
        "2) reason must be one short sentence.\n"
        "3) Return JSON only, no markdown, no code fences, no extra text.\n\n"
        "Conversation history (last up to 10 messages):\n"
        f"{_serialize_history(recent_history)}\n\n"
        f"Current incoming message:\n{current_message}\n\n"
        "Return exactly this schema:\n"
        "{\n"
        "  \"action\": \"<one key from MOVES>\",\n"
        "  \"reason\": \"<one short sentence>\"\n"
        "}"
    )

    response = client.chat.completions.create(
        model="gpt-5-mini",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
        response_format={"type": "json_object"},
    )

    raw_content = response.choices[0].message.content or "{}"
    return _safe_parse_decision(raw_content)


def _parse_cli_input(raw: str) -> tuple[str, str]:
    """Parse `author: message` format; default author is `User`."""
    if ":" in raw:
        author, message = raw.split(":", 1)
        return author.strip() or "User", message.strip()
    return "User", raw.strip()


def _run_cli() -> None:
    """Simple interactive loop for local planner testing."""
    history: list[dict[str, str]] = []
    help_generator = HelpGenerator()

    print("Action Planner CLI — Veyra Edition")
    print("Type messages as `Author: message` for group chat simulation.")
    print("Type `exit` to quit.\n")

    while True:
        raw = input("> ").strip()
        if raw.lower() == "exit":
            print("Exiting.")
            break
        if not raw:
            continue

        author, current_message = _parse_cli_input(raw)

        # Add incoming message to conversation history.
        history.append({"author": author, "role": "user", "content": current_message})

        decision = decide_action(history, current_message)

        if decision["action"] == "help":
            # Only pass prev_reply if the immediately preceding assistant turn
            # was also a help reply — i.e. this is a genuine help follow-up.
            # We tag help entries with action="help" when we append them below.
            last_assistant = next(
                (e for e in reversed(history[:-1]) if e.get("role") == "assistant"),
                None,
            )
            prev_help = (
                last_assistant["content"]
                if last_assistant and last_assistant.get("action") == "help"
                else None
            )
            help_reply = asyncio.run(
                help_generator.generate(
                    message=current_message,
                    req_id="cli-help",
                    reason=decision["reason"],
                    prev_reply=prev_help,
                )
            )
            print(f"current reply {{{decision['action']}: {decision['reason']}}}")
            print(f"model reply: {help_reply}\n")
            history.append({"author": "Veyra", "role": "assistant", "action": "help", "content": help_reply})
        else:
            print(f"{decision['action']}: {decision['reason']}\n")

        # Keep history bounded for both runtime and prompt size control.
        history = _trim_history(history, max_items=10)


if __name__ == "__main__":
    _run_cli()