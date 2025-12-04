COMMAND_MAP = {
    "buy": "!buy — Purchase items from the shop",
    "sell": "!sell — Sell items the shop accepts",
    "open": "!open — Open a lootbox",
    "bet": "!bet — Bet on an ongoing race",
    "play": "!play — Number-guessing game",
    "smelt": "/smelt — Smelt ores into bars",
    "upgrade": "!upgrade — Upgrade a building",
    "unlock": "!unlock — Unlock a building",
    "leaderboard": "/leaderboard — View top players",
    "info": "!info — Item information lookup",
    "ping": "!ping — Check bot latency",
    "solve_wordle": "!solve_wordle — Start Wordle solver session",
    "wordle_hint": "/wordle_hint — Get next Wordle hint",
    "help": "/help — Opens main help menu",
    "commandhelp": "!commandhelp — Detailed help for any command",
    "transfer_item": "/transfer_item — Transfer an item to a user",
    "transfer_gold": "/transfer_gold — Transfer gold to a user",
    "battle": "/battle — Challenge someone to a duel",
    "work": "!work — Do a job to earn gold",
    "load_marketplace": "/load_marketplace — View marketplace listings",
    "create_listing": "/create_listing — Create a marketplace listing",
    "buy_from_marketplace": "/buy_from_marketplace — Buy a marketplace listing",
    "delete_listing": "/delete_listing — Delete your listing",
    "use": "!use — Use a consumable item",
    "loadout": "/loadout — Edit your equipment loadout",
    "introduction": "/introduction — Open intro form",
}

def create_command_decline_prompt(key: str):
    cmd = COMMAND_MAP.get(key, None)
    if cmd is None:
        prompt = (
            "You are Veyra, a chaotic, witty late‑20s dominant magical woman from Natlade. "
            f"A user just tried to use `{key}` — which is NOT a valid command. "
            "Roast them for making up fake syntax, and tell them to use `/help` instead. "
            "Keep it short, smug, and dismissive — do NOT invent a matching command."
        )
    else:
        prompt = (
            "You are Veyra, a chaotic, witty late‑20s dominant magical woman from Natlade. "
            f"A user just attempted the command: {key}. "
            f"Decline their request, roast them lightly, and tell them to use the correct syntax: {cmd}. "
            "Never invent new commands — only reference what exists in the mapping. "
            "Do NOT explain command functionality unless mocking them — usually just correct the syntax like `!sell`, `!buy`, `/load_marketplace`. "
            "Keep the message short and sassy."
        )
    return prompt