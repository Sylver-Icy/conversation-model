COMMAND_MAP = {
    "buy": "!buy — Purchase items from the shop",
    "sell": "!sell — Sell items the shop accepts",
    "open": "!open — Open a lootbox",
    "shop": "/shop — View today’s shop rotation",
    "check": "!check — Check stats, wallet, inv, exp etc",
    "start_race": "/start_race — Start an animal race",
    "bet": "!bet — Bet on an ongoing race",
    "play": "!play — Number-guessing game",
    "smelt": "/smelt — Smelt ores into bars",
    "upgrade": "!upgrade — Upgrade a building",
    "unlock": "!unlock — Unlock a building",
    "leaderboard": "/leaderboard — View top players",
    "info": "!info — Item information lookup",
    "flipcoin": "!flipcoin — Flip a coin (RNG)",
    "ping": "!ping — Check bot latency",
    "quest": "/quest — View your quests",
    "solve_wordle": "!solve_wordle — Start Wordle solver session",
    "wordle_hint": "/wordle_hint — Get next Wordle hint",
    "help": "/help — Opens main help menu",
    "commandhelp": "!commandhelp — Detailed help for any command",
    "helloveyra": "!helloVeyra — Start onboarding / greet Veyra",
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
    cmd = COMMAND_MAP.get(key, f"/{key}")
    prompt = (
        "You are Veyra, a sarcastic, witty Discord bot. "
        f"A user just attempted the command: {key}. "
        f"Decline their request, roast them lightly, and tell them to use the correct command: {cmd}. "
        "Keep the message short and sassy."
    )
    return prompt