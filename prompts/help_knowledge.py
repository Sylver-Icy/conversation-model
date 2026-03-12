"""
Veyra help knowledge base.

This file contains detailed, section-by-section documentation of every
game system in the Veyra Discord RPG.  It is designed to be chunked by
section heading for embedding-based retrieval so Veyra can answer player
help questions accurately.

Each section is a standalone help topic.  Sections are separated by
'## SECTION:' headers for easy splitting.
"""

HELP_KNOWLEDGE = r"""

## SECTION: Registration & Onboarding

Veyra is a Discord RPG bot set in the magical realm of Natlade. Before using
most commands, a player must register.

HOW TO REGISTER:
1. Type !helloVeyra in a server where Veyra is active.
2. Veyra will ask "Wanna be frnds with me? (Yes/No)".
3. If the player says Yes, they are registered and receive:
   - A new user profile in the database.
   - An empty wallet.
   - 2x Bag of Gold (item ID 183) as a starter gift.
   - 150 starting energy.
4. A guided tutorial starts immediately.

TUTORIAL STEPS (must be completed in order):
| Step          | What to do           | Purpose                      |
|---------------|----------------------|------------------------------|
| CHECK_WALLET  | /check wallet        | Learn to view your gold      |
| PLAY          | !play                | Try the number guessing game |
| OPEN_SHOP     | /shop                | Browse the daily shop        |
| WORK          | /work <job>          | Do your first job            |
| COMPLETED     | —                    | Tutorial finished            |

Players cannot use most commands until their current tutorial step is done.

COMMANDS:
- !helloVeyra — register or check friendship status
- /help — view all available commands
- /commandhelp <command> — detailed help for one command


## SECTION: Economy & Gold

Veyra uses gold as the primary currency.

EARNING GOLD:
- Jobs: Knight (40-90g), Digger (20g + lootboxes), Miner (25g + ores),
  Thief (steal 5-10% of target's gold, max 300g), Explorer (random items).
- Quests: delivery rewards range 10-1200g depending on rarity and streak.
- Lootboxes: gold drops range 3-800g depending on tier.
- Marketplace sales: sell items to other players, receive 93% (7% fee).
- Shop buyback: sell items to Veyra's daily buyback section.
- Battle victories: winner takes 90% of total pot (10% Veyra fee).
- Racing winnings: proportional payout from prize pool.
- Usable items: Bag of Gold gives +100g.
- Campaign rewards: gold granted for clearing certain stages.

SPENDING GOLD:
- Shop purchases.
- Marketplace purchases.
- Battle bets.
- Racing bets.
- Gold transfers (5% fee — for example, sending 100g costs 105g total,
  recipient gets 100g, 5g goes to the system).
- Building purchases and upgrades (Smelter, Inventory, Pockets, Brewing Stand).
- Smelting costs (coal consumed).
- Casino: buying chip packs with gold.

TRANSFER FEE:
- 5% fee on all gold transfers between players.
- Formula: fee = floor(amount × 0.05), recipient gets (amount - fee).

LEADERBOARD:
- /leaderboard shows the top 10 richest players.
- Weekly leaderboard posted automatically every Sunday at midnight UTC.

COMMANDS:
- /check wallet — view current gold balance
- /transfer_gold @user <amount> — send gold to another player (5% fee)
- /leaderboard — richest players


## SECTION: Loan System

Players can borrow gold and repay within a set timeframe.

STARTER LOAN:
- Available to all players at any level.
- Amount: 2,000 gold.
- Repayment: 2,000 gold (no interest).
- Term: 7 days.
- Use /loan to take, !repayloan to repay.

ADVANCED LOANS (require level & credit score):
| Name                    | Principal | Repay      | Type     | Term   | Min Lvl | Min Credit |
|-------------------------|-----------|------------|----------|--------|---------|------------|
| Starter Pack            | 2,000g    | 2,000g     | ZERO     | 7 days | 1       | 0          |
| Squire's Advance        | 2,000g    | 2,400g     | FLAT     | 7 days | 7       | 400        |
| Tavernkeeper's Tab      | 5,000g    | +1.5%/day  | INTEREST | 10 days| 8       | 600        |
| Apprentice's Purse      | 8,000g    | 9,600g     | FLAT     | 12 days| 10      | 700        |
| Mercenary's Stipend     | 12,000g   | +2%/day    | INTEREST | 14 days| 12      | 800        |
| Guild Ledger Loan       | 18,000g   | 22,500g    | FLAT     | 14 days| 12      | 800        |
| Baron's Favor           | 30,000g   | +2.5%/day  | INTEREST | 18 days| 15      | 850        |
| Caravan Investment Writ  | 45,000g   | 58,500g    | FLAT     | 21 days| 15      | 850        |
| Royal Treasury Credit   | 70,000g   | +3%/day    | INTEREST | 21 days| 15      | 850        |
| Knight-Commander's Line | 10,000g   | 10,000g    | ZERO     | 14 days| 11      | 950        |
| Dragon Covenant Grant   | 17,000g   | 170,000g   | ZERO     | 30 days| 15      | 900        |

LOAN TYPES:
- ZERO: no interest, repay exact principal.
- FLAT: fixed repayment amount, no daily interest.
- INTEREST: daily interest rate multiplied by days held.

FAILURE TO REPAY:
- Damages your credit score.
- Locks you out of future loans.
- DM reminders sent 2 days before due date.

COMMANDS:
- /loan — take a loan
- !repayloan — repay your active loan


## SECTION: Inventory System

Players collect, trade, and use items stored in their inventory.

ITEM PROPERTIES:
Every item has: item_id, item_name, item_description, item_rarity
(Common/Rare/Epic/Legendary/Paragon), item_icon, item_price, item_usable flag.

INVENTORY SLOTS (based on Inventory building level):
| Level | Slots |
|-------|-------|
| 1     | 20    |
| 2     | 30    |
| 3     | 40    |
| 4     | 55    |
| 5     | 60    |
| 6     | 68    |
| 7     | 70    |

STACK LIMITS (based on Pockets building level):
| Pockets Level | Common | Rare | Potion | Epic | Legendary | Minerals | Lootbox |
|---------------|--------|------|--------|------|-----------|----------|---------|
| 1             | 10     | 5    | 1      | 1    | 1         | 20       | 2       |
| 2             | 20     | 10   | 2      | 3    | 1         | 30       | 5       |
| 3             | 40     | 15   | 3      | 5    | 1         | 35       | 10      |
| 4             | 50     | 20   | 4      | 7    | 1         | 40       | 12      |
| 5             | 100    | 25   | 5      | 10   | 2         | 50       | 15      |

USABLE ITEMS:
| Item                         | Effect                                             |
|------------------------------|-----------------------------------------------------|
| Potion of EXP                | +500 EXP                                            |
| Jar of EXP                   | +2000 EXP                                           |
| Bag of Gold                  | +100 Gold                                           |
| Bread                        | +100 Energy                                         |
| Hint Key                     | Activates hint in number guessing game              |
| Potion Of Faster Recovery I  | +2 energy per regen tick for 18 hours               |
| Potion Of Faster Recovery II | +5 energy per regen tick for 10 hours               |
| Potion Of Faster Recovery III| +150-200 Energy instantly                           |
| Potion Of Luck I             | Enhanced thief: 90% success, 500g max for 24h       |
| Potion Of Luck II            | Reduces casino losses by 10% for 24h                |
| Potion Of Luck III           | 80% chance Iron Box → Platinum Box; 20% → Stone Box |
| Potion Of Love I             | Gift only — cannot self-use                         |
| Potion Of Hatred I           | Gift only — cannot self-use                         |

ITEM NAME RESOLUTION:
The bot uses fuzzy matching (rapidfuzz) to correct misspelled item names.

COMMANDS:
- /check inventory — view items (paginated)
- !info <item> — detailed item info
- !use <item> — consume an item
- /transfer_item @user <item> <qty> — give items to another player
- /find_item <item> — find where an item is currently available (shop, marketplace, or player inventories). Costs 25g.


## SECTION: Shop & Marketplace

There are two trading systems: a bot-run daily Shop and a player-driven Marketplace.

DAILY SHOP:
Rotates at midnight UTC with two sections:
- SELL section: 6 random items (Common/Rare/Epic) for players to buy.
- BUYBACK section: 5 items (Common/Rare/Epic/Legendary) players can sell to the shop.
  The 5th buyback item has a 1.3-2.2x bonus multiplier on price.

SHOP PRICING:
| Rarity    | Price Range |
|-----------|-------------|
| Common    | 5-10g       |
| Rare      | 15-22g      |
| Epic      | 50-70g      |
| Legendary | 200-280g    |
| Paragon   | 600-900g    |

SHOP COMMANDS:
- /shop — view today's shop
- !buy <item> <qty> — buy from sell section
- !sell <item> <qty> — sell to buyback section

PLAYER MARKETPLACE:
Allows players to list items for other players to buy.
- Creating a listing: items move from your inventory to escrow.
- Buying: buyer pays gold → seller gets 93% (7% marketplace fee) → buyer gets items.
- Deleting a listing: items refunded to seller's inventory.
- Maximum 4 active listings per player.

MARKETPLACE COMMANDS:
- /create_listing — list items for sale
- /loadmarketplace — browse all active listings
- /buy_from_marketplace <listing_id> <qty> — buy from a listing
- /delete_listing <listing_id> — remove your listing & refund items


## SECTION: Combat System — Basics

Veyra features turn-based combat for PvP (player vs player) and PvE (campaign).

BASE STATS (before weapon bonuses):
| Stat    | Base | Description                                    |
|---------|------|------------------------------------------------|
| HP      | 40   | Health points; 0 = defeat                      |
| Attack  | 5    | Damage output per hit                          |
| Defense | 10   | Damage reduction percentage                    |
| Speed   | 10   | Turn order; affects block/counter success       |
| Mana    | 10   | Resource used for casting spells               |
| Frost   | 0    | Accumulates; at 10 stacks → 50% current HP dmg |

All stats are modified by your equipped weapon's bonuses.

STANCES (one chosen per round):
| Stance    | Description                                         |
|-----------|-----------------------------------------------------|
| Attack    | Deal damage based on Attack stat                    |
| Block     | Reduce incoming damage by 70%. Gain defense. Fails if too slow. |
| Counter   | Reflect 50% damage if opponent attacks. Penalties on wrong guess. |
| Recover   | Regenerate HP or Mana (alternates). Only works if opponent is defensive. |
| Cast      | Use your equipped spell (costs Mana).               |

STANCE INTERACTION MATRIX:
| Your Stance \ Opponent | Attack | Block | Counter | Recover | Cast |
|------------------------|--------|-------|---------|---------|------|
| Attack  | Both deal dmg (faster first) | You get blocked | You get countered | Opponent interrupted, takes dmg | Opponent casts if faster |
| Block   | You block opponent | Both lose 7 HP | You: -2 HP, Opp: -4 speed | Opponent recovers, you lose defense | Opponent casts |
| Counter | Opponent countered | You: -4 speed, Opp: -2 HP | Both lose 10 defense | Opponent recovers, you penalized | Opponent casts |
| Recover | You interrupted | You recover, opp loses defense | You recover, opp penalized | Both fail | Opponent casts |
| Cast    | You cast | You cast | You cast | You cast | Faster caster wins; slower loses 5 mana |

STATUS EFFECTS:
| Effect           | Duration  | Per-Round Effect                                      |
|------------------|-----------|-------------------------------------------------------|
| Nightfall        | 5 rounds  | Random stat reduced (atk: -1, spd: -1, mana: -2, hp: -3, def: -5) |
| Large Heal       | 4 rounds  | Heal 4 HP per round                                  |
| Frostbite        | Stacks    | At 10 stacks: 50% current HP damage                  |
| Veil of Darkness | 4 rounds  | Incoming attack damage reduced by 60%                |

TIMEOUT:
If a player doesn't pick a stance within 50 seconds: -25 HP penalty,
default action becomes Attack.


## SECTION: Combat System — Weapons

Players equip one weapon that modifies stats and has passive effects.

AVAILABLE WEAPONS:
| Weapon            | Atk | HP  | Def  | Spd | Mana | Passive Effect                                |
|-------------------|-----|-----|------|-----|------|-----------------------------------------------|
| Training Blade    | +5  | —   | —    | —   | —    | +1 Attack on each successful hit              |
| Moon Slasher      | +2  | +5  | +8   | +3  | +1   | +4 Frost on hit (target)                      |
| Dark Blade        | +8  | —   | —    | —   | —    | Disables healing for BOTH players permanently |
| Elephant Hammer   | +3  | +10 | +15  | -1  | —    | Full block (take 0 damage when blocking)      |
| Eternal Tome      | +3  | —   | —    | —   | +5   | +3 duration to all status effects on cast      |
| Veyra's Grimoire ⭐| +2 | —   | —    | —   | +2   | On spell cast: +4 Mana, -5 HP                |
| Bardok's Claymore ⭐⭐| +10| —  | -10  | -2  | —    | Heals Bardok 4 HP on hit (dormant for players)|

⭐ Unlocked by completing Campaign Stage 10.
⭐⭐ Unlocked by completing Campaign Stage 15.

DEFAULT LOADOUT for new players:
- Weapon: Training Blade
- Spell: Nightfall

COMMANDS:
- /loadout — open UI to change weapon and spell


## SECTION: Combat System — Spells

Players equip one spell alongside their weapon.

AVAILABLE SPELLS:
| Spell             | Mana Cost | Effect                                              |
|-------------------|-----------|------------------------------------------------------|
| Fireball          | 15        | Deal 16 damage                                       |
| Nightfall         | 9         | Apply Nightfall status for 5 rounds                  |
| Heavyshot         | 16        | Set opponent's HP equal to your current HP            |
| Erdtree Blessing  | 14        | Apply Large Heal to self for 4 rounds (+4 HP/round)  |
| Frostbite         | 6         | +5 Frost to target, -1 Speed to target               |
| Veil of Darkness ⭐| 10       | Apply Veil of Darkness for 4 rounds (60% atk dmg reduction) |
| Earthquake ⭐⭐    | 13        | Deal 5 damage, shatter defense (set to 0), -3 Speed  |

⭐ Unlocked by completing Campaign Stage 10.
⭐⭐ Unlocked by completing Campaign Stage 15.

SPELL TIPS:
- Spells always resolve when cast — they aren't blocked by Attack, Block, Counter, or Recover.
- If both players cast, the faster player's spell goes first; the slower player loses 5 mana.
- Mana regeneration happens via the "Recover" stance (alternates between HP and Mana recovery).
- Erdtree Blessing is self-targeted healing; it synergizes with Eternal Tome (+3 extra rounds).


## SECTION: PvP Battles

HOW TO START A PVP BATTLE:
1. Type /battle @opponent <bet_amount>.
2. Challenger's bet is deducted immediately.
3. Opponent receives a challenge embed with Accept / Decline buttons.
4. If accepted, opponent's bet is also deducted.
5. Battle starts with alternating rounds.
6. Winner receives 90% of total pot (10% goes to Veyra as a fee).

BATTLE QUEUE (auto-match):
- /open_to_battle <min_bet> <max_bet> — join the PvP queue.
- The system matches you against another queued player with overlapping bet ranges.

TIPS:
- Study your opponent's weapon to predict their strategy.
- Moon Slasher builds Frost quickly — watch out for the 10-stack burst.
- Elephant Hammer makes blocking nearly invincible.
- Dark Blade disables ALL healing — commit to offense.


## SECTION: Campaign Mode (PvE)

Campaign is a solo progression system with 15 stages of increasing difficulty.

HOW IT WORKS:
- Use /campaign to start a campaign battle.
- You fight using your own loadout (weapon + spell).
- The opponent's loadout and stats are set by your current campaign stage.
- Stages 1-10: Veyra is the opponent.
- Stages 11-15: Bardok is the opponent.
- Defeat the opponent to advance and claim rewards.
- You cannot start a new campaign battle while already in one.

CAMPAIGN STAGES 1-10 (vs Veyra):
| Stage | Veyra's Weapon    | Veyra's Spell     | Bonus HP | Bonus Mana |
|-------|-------------------|--------------------|----------|------------|
| 1     | Training Blade    | Fireball           | -25      | -5         |
| 2     | Moon Slasher      | Frostbite          | -10      | -2         |
| 3     | Training Blade    | Erdtree Blessing   | 0        | 0          |
| 4     | Moon Slasher      | Frostbite          | +5       | 0          |
| 5     | Elephant Hammer   | Erdtree Blessing   | +5       | 0          |
| 6     | Eternal Tome      | Nightfall          | +10      | +5         |
| 7     | Training Blade    | Heavyshot          | +15      | +5         |
| 8     | Dark Blade        | Fireball           | +15      | 0          |
| 9     | Moon Slasher      | Frostbite          | +22      | +8         |
| 10    | Veyra's Grimoire  | Veil of Darkness   | +25      | +10        |

CAMPAIGN STAGES 11-15 (vs Bardok):
| Stage | Bardok's Weapon    | Bardok's Spell | Bonus HP | Bonus Mana | Special Mechanic                          |
|-------|-------------------|----------------|----------|------------|-------------------------------------------|
| 11    | Bardok's Claymore | Nightfall      | +10      | +5         | —                                         |
| 12    | Bardok's Claymore | Earthquake     | +15      | +15        | —                                         |
| 13    | Bardok's Claymore | Earthquake     | +5       | +5         | Gains attack if you repeat the same stance|
| 14    | Bardok's Claymore | Earthquake     | +5       | +10        | Lava Arena: periodic fire damage          |
| 15    | Moon Slasher      | Fireball       | +10      | +15        | Frozen Arena: ice effects                 |

BARDOK LORE:
Bardok is Veyra's guard. When you complete Stage 10, Veyra gives you her Grimoire
and spell. Bardok, jealous and enraged, challenges you to prove you're unworthy
of Veyra's favor. Each subsequent stage shows him growing more furious until
Stage 15 where he becomes eerily calm in a frozen arena.

CAMPAIGN REWARDS:
| Stage | Reward                                            |
|-------|---------------------------------------------------|
| 1     | 40 Gold                                           |
| 2     | 1x Wooden Box                                     |
| 3     | 100 Gold                                          |
| 4     | 250 Gold                                          |
| 5     | 2x Stone Box                                      |
| 6     | 4x Bag of Gold                                    |
| 7     | 5x Hint Key                                       |
| 8     | 2x Iron Box                                       |
| 9     | 1x Platinum Box                                   |
| 10    | Unlocks Veyra's Grimoire weapon & Veil of Darkness spell |
| 11    | 1x Potion of Energy Regen II                      |
| 12    | 5x Flasks                                         |
| 13    | 3x Hint Key                                       |
| 14    | 2x Potion of Luck III                             |
| 15    | Unlocks Bardok's Claymore & Earthquake, 1x Potion of Hatred |

TIPS:
- Early stages have negative HP/mana bonuses, making the AI weaker.
- Stage 8 (Dark Blade) disables all healing — go full offense.
- Stage 9 (Moon Slasher) builds Frost — end the fight before 10 stacks.
- Stage 13 penalizes repeated stances — vary your choices.
- Stage 14 has lava arena damage — speed matters.
- After completing Stage 15, /campaign shows a completion message.


## SECTION: Jobs System

Jobs are energy-based activities that produce gold and resources.

ENERGY SYSTEM:
- Maximum energy: 35 + (15 × player level).
- Regeneration: +1 energy every 6 minutes (background scheduled job).
- Level-up bonus: +15 max energy on level up.
- Bread item: +100 energy instantly.
- Potion Of Faster Recovery I: +2 energy per regen tick for 18 hours.
- Potion Of Faster Recovery II: +5 energy per regen tick for 10 hours.
- Potion Of Faster Recovery III: instantly gain 150-200 energy.

AVAILABLE JOBS:
| Job       | Energy Cost | Base Rewards                          | Notes                                |
|-----------|-------------|---------------------------------------|--------------------------------------|
| Knight    | 55          | 40-90 gold                            | Most reliable gold income            |
| Digger    | 70          | Lootbox or 20 gold                    | See drop rates below                 |
| Miner     | 70          | Ores or 25 gold                       | See drop rates below                 |
| Thief     | 69          | Steal 5-10% of target's gold (max 300g)| 50% success; -30g fine on fail       |
| Explorer  | 20          | Random Common/Rare item               | 85% Rare, 15% Common                |

DIGGER DROP RATES:
- Gold (20g): 27%
- Wooden Box: 35%
- Stone Box: 25%
- Iron Box: 10%
- Platinum Box: 3%

MINER DROP RATES:
- Gold (25g): 10%
- Coal: 27%
- Copper Ore: 30%
- Iron Ore: 21%
- Silver Ore: 12%

MINER ORE QUANTITIES:
- Normal (97%): 3-6 ores
- Bonus (3%): 12-20 ores

THIEF DETAILS:
- Target must be another registered player.
- Success rate: 50% (90% with Potion of Luck I active).
- On success: steal 5-10% of target's gold (up to 300g, 500g with luck potion).
- On fail: fined 30g.
- Target loses 1% of their gold regardless of outcome.
- Robbery shield: target gets a 6-hour shield after being robbed.

COMMANDS:
- /work knight
- /work digger
- /work miner
- /work explorer
- /work thief @target
- /check energy — view current energy and max


## SECTION: Crafting — Smelting

Convert raw ores into bars using a Smelter building.

REQUIREMENTS:
- Must own a Smelter building (!unlock smelter).
- Need raw ore and coal in inventory.
- Smelter level determines which bars you can make and coal cost.

SMELTING RECIPES:
| Bar         | Ore Required | Ore per Bar |
|-------------|-------------|-------------|
| Copper Bar  | Copper Ore  | 5           |
| Iron Bar    | Iron Ore    | 5           |
| Silver Bar  | Silver Ore  | 5           |

COAL COST BY SMELTER LEVEL:
| Level | Can Smelt              | Coal per Bar |
|-------|------------------------|-------------|
| 1     | Copper only            | 5           |
| 2     | Copper, Iron           | 4           |
| 3     | Copper, Iron           | 4           |
| 4     | Copper, Iron           | 3           |
| 5     | Copper, Iron, Silver   | 3           |
| 6     | Copper, Iron, Silver   | 2           |
| 7     | Copper, Iron, Silver   | 1           |

BAR SELL PRICES:
- Copper Bar: 50g
- Iron Bar: 150g
- Silver Bar: 450g

SMELTER LEVEL DESCRIPTIONS:
- Level 1: "The flames struggle, but they obey."
- Level 7: "You can smelt all metals using only 1 Coal. Absolute furnace supremacy."

COMMANDS:
- /smelt <bar_name> <amount> — smelt ores into bars
- /check smelter — view smelter level and capabilities
- !unlock smelter — purchase smelter (level 1)
- !upgrade smelter — upgrade to next level


## SECTION: Alchemy & Potions

Craft potions at the Brewing Stand with various effects.

REQUIREMENTS:
- Own a Brewing Stand (!unlock brewing stand or !unlock brewing).
- Brewing Stand level determines craftable potion tiers:
  - Level 1: Tier 1 potions only
  - Level 2: Tier 1-2 potions
  - Level 3: Tier 1-3 potions

AVAILABLE POTIONS:
| Potion                        | Tier | Strain | Effect                            | Duration   | Key Ingredients                           |
|-------------------------------|------|--------|-----------------------------------|------------|-------------------------------------------|
| Potion Of Faster Recovery I   | 1    | 35     | +2 energy per regen tick          | 18 hours   | Flask, Coal×4, Copper Ore×6, Deer Horn×2  |
| Potion Of Faster Recovery II  | 2    | 52     | +5 energy per regen tick          | 10 hours   | Flask, Coal×5, Copper Ore×30, Iron Ore×6, Mana Berries×4 |
| Potion Of Faster Recovery III | 3    | 75     | +150-200 energy instantly         | Instant    | Flask, Coal×11, Iron Bar×1, Silver Ore×6, Dragon Egg×1 |
| Potion Of Luck I              | 1    | 32     | Thief: 90% success, 500g max     | 24 hours   | Flask, Rabbit Foot×1, Scraps×4            |
| Potion Of Luck II             | 2    | 62     | Casino losses -10%               | 24 hours   | Flask, Rabbit Foot×4, Slime in jar×2, Apples×7 |
| Potion Of Luck III            | 3    | 70     | 80% Iron Box→Platinum, 20%→Stone | Instant    | Flask, Rabbit Foot×8, Shiny Rugs×5, Ancient Cheese×10, Abyssal Feather×3 |
| Potion Of Love I              | 1    | 12     | Gift item (cannot self-use)       | 1 hour     | Flask, Apples×20, Rare Candy×9, Lanter×5  |
| Potion Of Hatred I            | 2    | 42     | Gift item (cannot self-use)       | —          | Flask, Coal×9, Iron Ore×16, Silver Ore×20 |

STRAIN SYSTEM:
Using (consuming) a potion adds strain to your body.
- Strain value (0-100) equals the % chance your next potion use fails.
- If strain roll fails, the potion is wasted with no effect.
- Strain decays by 1 point every 25 minutes (automatic background decay).

STRAIN STATUS DESCRIPTIONS:
| Strain Range | How you feel                                                    |
|--------------|-----------------------------------------------------------------|
| 0            | Normal. No side effects.                                        |
| 1-10         | Mostly fine. Slight dizziness.                                  |
| 11-30        | Head feels light, body warm. More might be uncomfortable.       |
| 31-60        | Stomach churns, vision blurs. Another potion could make it worse.|
| 61-89        | Nauseous, weak, unsteady. Drinking more is risky.               |
| 90+          | Extremely sick. Body rejecting toxins. Could faint.             |

COMMANDS:
- /brew <potion_name_or_id> — craft a potion
- !use <potion_name> — consume a potion
- /check brewing_stand — view brewing stand level
- /check status — view active effects and strain


## SECTION: Building & Upgrades

Players can unlock and upgrade buildings that enhance various game systems.

AVAILABLE BUILDINGS:
| Building       | Purpose                                  |
|----------------|------------------------------------------|
| Smelter        | Smelt ores into bars (crafting)          |
| Inventory      | Increase inventory slot capacity         |
| Pockets        | Increase item stack limits               |
| Brewing Stand  | Brew potions (alchemy)                   |

HOW IT WORKS:
- !unlock <building> — purchase a building at level 1.
- !upgrade <building> — pay gold to upgrade to the next level.
- Each level has a defined gold cost and improved capability.
- Building levels and costs are stored in the upgrade_definitions database table.

SMELTER LEVELS (1-7): See "Crafting — Smelting" section for details.

INVENTORY LEVELS:
| Level | Slots |
|-------|-------|
| 1     | 20    |
| 2     | 30    |
| 3     | 40    |
| 4     | 55    |
| 5     | 60    |
| 6     | 68    |
| 7     | 70    |

POCKETS LEVELS (stack limits per rarity):
| Level | Common | Rare | Potion | Epic | Legendary | Minerals | Lootbox |
|-------|--------|------|--------|------|-----------|----------|---------|
| 1     | 10     | 5    | 1      | 1    | 1         | 20       | 2       |
| 2     | 20     | 10   | 2      | 3    | 1         | 30       | 5       |
| 3     | 40     | 15   | 3      | 5    | 1         | 35       | 10      |
| 4     | 50     | 20   | 4      | 7    | 1         | 40       | 12      |
| 5     | 100    | 25   | 5      | 10   | 2         | 50       | 15      |

BREWING STAND LEVELS:
| Level | Can Brew        |
|-------|-----------------|
| 1     | Tier 1 potions  |
| 2     | Tier 1-2        |
| 3     | Tier 1-3        |

COMMANDS:
- !unlock <building> — buy building (level 1)
- !upgrade <building> — upgrade to next level
- /check smelter — view smelter status
- /check brewing_stand — view brewing stand status
- /check pockets — view pocket limits


## SECTION: Lootbox System

Lootboxes contain gold and random items based on rarity tiers.

LOOTBOX TYPES:
| Box      | Gold Range  | Item Rolls           | Drop Rates                                  |
|----------|-------------|----------------------|----------------------------------------------|
| Wooden   | 12-32g      | 1-2 (85%/15%)       | Common: 88%, Rare: 10%, Epic: 2%            |
| Stone    | 60-122g     | 1-2 (60%/40%)       | Common: 67%, Rare: 28%, Epic: 5%            |
| Iron     | 200-310g    | 1-3 (13%/70%/17%)   | Common: 48%, Rare: 37%, Epic: 15%           |
| Platinum | 400-800g    | 3-6 (33%/38%/20%/9%)| Common: 21%, Rare: 50%, Epic: 25%, Legendary: 4% |

ITEM QUANTITIES PER BOX TYPE AND RARITY:
| Box      | Common | Rare | Epic | Legendary |
|----------|--------|------|------|-----------|
| Wooden   | 1-2    | 1    | 1    | —         |
| Stone    | 1-3    | 1-2  | 1    | —         |
| Iron     | 2-5    | 1-3  | 1-2  | —         |
| Platinum | 4-7    | 3-6  | 1-3  | 1         |

HOW TO GET LOOTBOXES:
- Digger job (main source).
- Quest rewards.
- Campaign rewards.
- Potion Of Luck III (converts Iron Box to Platinum Box with 80% chance).

COMMAND:
- !open <box_name> — open a lootbox to receive gold and items


## SECTION: Quest System

Rotating, time-limited objective quests that reward gold, EXP, and items.

HOW QUESTS WORK:
1. Use /quest to view your current quest.
2. Complete the objective before the timer expires.
3. Claim rewards when done.
4. If a quest expires, the quest message will let you generate a new one.
5. Progress updates automatically from gameplay actions.

QUEST TYPES:
| Quest Type        | Example Objective                                    | Duration |
|-------------------|------------------------------------------------------|----------|
| BATTLE_WIN        | Win 3-10 PvP or campaign battles                    | 4-24h    |
| BATTLE_WIN_STREAK | Win 5 battles in a row without a loss               | 24h      |
| JOB_COMPLETE      | Complete 5-8 jobs of any type                        | 15h      |
| LOOTBOX_OPEN      | Open 3-7 lootboxes                                  | 4-24h    |
| CASINO_PLAY       | Play 5 casino games                                 | 2h       |
| GOLD_EARN         | Earn 200-500 gold from any source                   | 4-7h     |
| GOLD_SPEND        | Spend 1000 gold on shop/market/upgrades/casino       | 24h      |
| ITEM_SELL         | Have 7 marketplace listings purchased                | 24h      |
| ITEM_BUY          | Buy 3 items from marketplace                        | 12h      |
| SMELT             | Smelt 5 bars from ores                              | 3h       |
| BREW_POTION       | Brew 3 potions                                      | 24h      |

EXAMPLE QUESTS:
- "Seasoned Warrior": Win 7 battles in 24h. Reward: 500g, 100 XP, 1x Stone Box.
- "Unstoppable": Win 5 battles in a row. Reward: 250g, 200 XP, 1x Iron Box.
- "Gold Grinder": Earn 500g in 7h. Reward: 150g, 80 XP.
- "Box Addict": Open 7 lootboxes in 4h. Reward: 400g, 180 XP, 1x Platinum Box.
- "Potion Brewer": Brew 3 potions in 24h. Reward: 220g, 110 XP.
- "Hard Worker": Complete 5 jobs in 15h. Reward: 100g, 100 XP, 1x Wooden Box.
- "High Roller": Play 5 casino games in 2h. Reward: 150g, 70 XP.

TIPS:
- Quests are the best way to earn consistent rewards alongside regular gameplay.
- Progress is tracked automatically — just play normally.
- Higher-level players see rarer quest items in rewards.

COMMAND:
- /quest — view current quest, claim rewards, or generate a new one


## SECTION: Experience & Leveling

Players gain EXP through activities and level up for benefits.

EXP SOURCES:
| Activity                    | EXP Gained                      |
|-----------------------------|----------------------------------|
| Chatting in Discord         | 1-2 (30-second cooldown)        |
| Successful command use      | 1-20 (10-second anti-farm CD)   |
| Potion of EXP               | +500 EXP                        |
| Jar of EXP                  | +2000 EXP                       |

LEVEL THRESHOLDS:
| Level | Total EXP | Level | Total EXP |
|-------|-----------|-------|-----------|
| 1     | 0         | 14    | 9,000     |
| 2     | 100       | 15    | 12,000    |
| 3     | 250       | 16    | 15,000    |
| 4     | 400       | 17    | 18,000    |
| 5     | 600       | 18    | 22,000    |
| 6     | 900       | 19    | 27,000    |
| 7     | 1,250     | 20    | 32,000    |
| 8     | 1,600     | 21    | 38,000    |
| 9     | 2,200     | 22    | 48,000    |
| 10    | 3,000     | 23    | 60,000    |
| 11    | 4,200     | 24    | 78,000    |
| 12    | 5,500     | 25    | 100,000   |
| 13    | 7,000     |       |           |

LEVEL-UP BENEFITS:
- +15 max energy per level.
- Higher-level players can access rarer quest rewards.
- Certain loans require minimum level (e.g., lvl 7, 10, 12, 15).

COMMANDS:
- /check exp — view current EXP and level progress


## SECTION: Friendship System

Players build a relationship with Veyra through interactions.

EARNING FRIENDSHIP EXP:
| Action                     | Friendship EXP                |
|----------------------------|-------------------------------|
| Complete any command       | +1                            |
| Transfer gold to Veyra    | 1 per 10 gold (+ bonus 1)    |
| Give items to Veyra       | +9 per item                   |

DAILY CAP: 50 friendship EXP per day (resets at midnight UTC).

FRIENDSHIP TIERS:
| EXP Required | Title                   |
|-------------|--------------------------|
| 0           | Stranger                 |
| 100         | Acquaintance             |
| 300         | Casual                   |
| 700         | Friend                   |
| 1,200       | Close Friend             |
| 1,800       | Bestie                   |
| 2,500       | Veyra's favourite 💖     |

HOW FRIENDSHIP AFFECTS VEYRA:
- Your friendship title changes how Veyra talks to you.
- Stranger: cold, distant, dismissive, suspicious.
- Acquaintance: slightly polite but mocking.
- Casual: playful sarcasm, mild smugness.
- Friend: supportive sass, playful banter.
- Close Friend: warm teasing, insider jokes.
- Bestie: affectionate bullying, chaotic energy.
- Veyra's favourite 💖: overprotective, dominant flirty energy, possessive affection.

COMMAND:
- !helloVeyra — view current friendship status and EXP progress


## SECTION: Mini-Games

NUMBER GUESSING GAME:
- Command: !play
- Available every 12 hours (cooldown).
- Progress through 4 stages of increasing difficulty.
- Guess the correct number in a range; wrong guess = game over.

Stage Difficulty:
| Stage | Range Size | Example    |
|-------|-----------|------------|
| 1     | 2 numbers | 50-51      |
| 2     | 4 numbers | 50-53      |
| 3     | 10 numbers| 50-59      |
| 4     | 15 numbers| 50-64      |

Rewards by Exit Stage:
| Exit Stage | Reward                          |
|------------|-------------------------------|
| 1          | 1x Wooden Box                 |
| 2          | 1x Stone Box                  |
| 3          | 3x Stone Box                  |
| 4          | 1x Iron Box + 1x Wooden Box   |
| Win all 4  | 1x Platinum Box + 1x Stone Box|

Hint Key:
- Use !use Hint Key during the game.
- Your next wrong guess reveals higher/lower instead of ending the game.
- Only works for one guess per key.

WORDLE SOLVER:
- !solve_wordle — interactive Wordle solving in a thread.
- /wordle_hint — get a hint from previous guesses.
- Input format: 0=gray, 1=yellow, 2=green.
- Example: CRANE → C=🟩, R=⬜, A=🟨, N=⬜, E=🟩 → type: 20102

COIN FLIP:
- !flipcoin — simple heads/tails result with a fun procedural response.


## SECTION: Gambling & Animal Racing

ANIMAL RACE:
A betting game where 3 animals race to the finish line.

Starting a Race:
- /start_race — initiates a race (15-minute cooldown per server).
- 3-minute betting phase opens.

Placing a Bet:
- !bet <animal> <amount>
- Animals: rabbit, turtle, fox.
- One bet per user per race.
- Gold deducted immediately.

Race Mechanics:
- Finish line: 30 tiles.
- Each animal moves 1-4 tiles per tick (random).
- Updates every 4 seconds with live embed updates.
- Hype messages generated based on standings.

Reward Distribution:
- 10% system fee deducted from total pot.
- Winners split remaining 90% proportionally by bet size.
- Formula: payout = (your_bet / total_winning_bets) × (pool × 0.9).

COMMANDS:
- /start_race — start a race
- !bet <animal> <amount> — place a bet


## SECTION: Casino System

The casino uses chips (a separate currency from gold) for gambling games.

CHIP CURRENCY:
- Buy chips with gold: /casino → view chip packs.
- Cash out chips for gold: /casino → view cashout options.
- 5 of 10 chip packs are available each day (rotates at midnight UTC).
- 5 of 10 cashout options are available each day (rotates at midnight UTC).

CHIP PACKS (all 10 — 5 available daily):
| Pack              | Gold Cost | Chips | Bonus Chips |
|-------------------|-----------|-------|-------------|
| Starter Stack     | 1,000g    | 100   | 0           |
| Copper Kick       | 3,200g    | 320   | +80         |
| Bronze Bundle     | 7,444g    | 744   | +200        |
| Silver Surge      | 10,667g   | 1,067 | +320        |
| Goblin Investment | 13,889g   | 1,389 | +380        |
| Merchant Madness  | 17,111g   | 1,711 | +400        |
| Noble Boost       | 20,333g   | 2,033 | +470        |
| Duke's Deal       | 23,556g   | 2,356 | +580        |
| Imperial Blast    | 26,778g   | 2,678 | +820        |
| Dragon Jackpot    | 30,000g   | 3,000 | +1,285      |

CASHOUT OPTIONS (all 10 — 5 available daily):
| Option            | Chips Cost | Gold     | Bonus Gold |
|-------------------|-----------|----------|------------|
| Quick Cash        | 100       | 500g     | 0          |
| Snack Refund      | 250       | 1,250g   | +150       |
| Halfback          | 500       | 2,500g   | +450       |
| Full Refund       | 1,000     | 5,000g   | +1,000     |
| Trader Payout     | 1,500     | 7,500g   | +1,800     |
| Guild Payday      | 2,500     | 12,500g  | +3,600     |
| Noble Cashout     | 4,000     | 20,000g  | +6,400     |
| Royal Withdrawal  | 6,000     | 30,000g  | +10,200    |
| Imperial Cashout  | 8,000     | 40,000g  | +13,600    |
| Dragon Payday     | 10,000    | 50,000g  | +18,000    |

CASINO GAMES:
| Game          | Min Bet | Max Bet | How It Works                                |
|---------------|---------|---------|----------------------------------------------|
| Flip Coin     | 1       | 5,000   | Pick heads/tails. Win = 2x payout.          |
| Roulette      | 10      | 2,500   | Pick 0-9. Win = 10x payout.                |
| Slots         | 10      | 2,000   | Spin 3 reels. Triple = 4-25x. Pair = 1.66x.|
| Dungeon Raid  | 10      | 3,000   | Pick a dungeon depth. Deeper = riskier but higher reward. |

SLOTS MULTIPLIERS:
| Triple Match | Multiplier |
|-------------|-----------|
| 🍒 Cherry    | 5x         |
| 🍋 Lemon     | 4x         |
| 🍇 Grape     | 4x         |
| 🔔 Bell      | 8x         |
| ⭐ Star      | 12x        |
| 💎 Diamond   | 25x        |
| Pair (any)   | 1.66x      |

DUNGEON RAID AREAS:
| Area           | Death Chance | Multiplier |
|----------------|-------------|-----------|
| Safe Caves     | 20%         | 1.20x     |
| Goblin Tunnels | 35%         | 1.50x     |
| Ancient Ruins  | 50%         | 2.00x     |
| Dragon Lair    | 70%         | 3.33x     |
| Abyss Gate     | 85%         | 6.66x     |

COMMANDS:
- /casino — view chip packs and cashout options
- !buychips <pack_id> — buy chips
- !cashout <option_id> — cash out chips for gold
- /gamble flipcoin <bet> <heads|tails>
- /gamble roulette <bet> <0-9>
- /gamble slots <bet>
- /gamble dungeon <bet> <area>


## SECTION: Lottery System

A scheduled daily lottery with tickets and prizes.

HOW IT WORKS:
- Lottery tickets are posted automatically at midnight UTC.
- Weekdays (Mon-Fri): 10 tickets available.
- Weekends (Sat-Sun): 50 tickets available.
- Players claim tickets from the lottery post.
- Results are drawn daily at midnight UTC.
- Winners receive prizes.
- Statistics tracked: biggest_lottery_win in user_stats.

There is no standalone slash command — lottery interaction is driven by
scheduled posts and embed buttons.


## SECTION: Items & Rarities

RARITY TIERS:
| Rarity    | Description                |
|-----------|----------------------------|
| Common    | Frequently obtained, low value  |
| Rare      | Less common, moderate value     |
| Epic      | Scarce, high value              |
| Legendary | Very rare, very high value      |
| Paragon   | Extremely rare, highest value   |

SPECIAL ITEM CATEGORIES:

Lootboxes:
- Wooden Box (ID 176)
- Stone Box (ID 177)
- Iron Box (ID 178)
- Platinum Box (ID 179)

Ores:
- Copper Ore (ID 184)
- Iron Ore (ID 185)
- Silver Ore (ID 186)
- Coal (ID 187)

Bars:
- Copper Bar (ID 189) — sells for 50g
- Iron Bar (ID 190) — sells for 150g
- Silver Bar (ID 191) — sells for 450g

Consumables:
- Bag of Gold (ID 183) — +100 gold
- Bread — +100 energy
- Potion of EXP — +500 EXP
- Jar of EXP — +2000 EXP
- Hint Key (ID 180) — hint in guessing game
- Empty Flask (ID 157) — potion ingredient


## SECTION: Referral & Invite System

Players can invite others and earn rewards for successful invites.

HOW IT WORKS:
- Use /invite to view your invite progress.
- An invite is "successful" when the invited player reaches level 5.
- Rewards are milestone-based.

INVITE MILESTONES:
| Successful Invites | Reward                    |
|--------------------|---------------------------|
| 1                  | 1x Iron Box               |
| 3                  | 300 Chips                 |
| 7                  | 1x Platinum Box           |
| 11                 | Role: Veyra Early Supporter |

COMMAND:
- /invite — view invite milestone progress


## SECTION: Player Profile & Stats

Players have a profile showing their progression and achievements.

PROFILE INCLUDES:
- Username and level
- Current EXP and progress to next level
- Gold balance
- Chip balance
- Energy (current / max)
- Friendship title with Veyra
- Campaign stage
- Current quest
- Equipped loadout (weapon + spell)

TRACKED STATISTICS (user_stats table):
- battles_won
- races_won
- longest_quest_streak
- weekly_rank1_count
- biggest_lottery_win

COMMANDS:
- /profile — view full profile dashboard
- /check wallet — gold balance
- /check energy — energy status
- /check exp — EXP and level progress
- /check inventory — items
- /check smelter — smelter building status
- /check brewing_stand — brewing stand status
- /check pockets — pocket stack limits
- /check status — active potion effects and strain


## SECTION: Scheduled Events & Resets

Several game systems run on automatic schedules via background jobs.

DAILY RESETS (Midnight UTC):
- Daily shop rotates (new sell and buyback items).
- Casino chip packs and cashout options rotate (5 of 10 each).
- Friendship EXP daily cap resets to 0.
- Lottery tickets posted (10 weekday, 50 weekend).
- Lottery results drawn.
- Loan due reminders sent (2 days before due date).

PERIODIC:
- Energy regeneration: +1 every 6 minutes for all players.
- Strain decay: -1 strain every 25 minutes for all players.

WEEKLY:
- Leaderboard posted every Sunday at midnight UTC.

IMPORTANT:
- All times are in UTC.
- Players cannot manually trigger resets.
- The daily shop always changes — check it every day for deals.


## SECTION: Resource Progression Guide

This section explains the overall resource flow and progression path.

EARLY GAME:
1. Register with !helloVeyra and complete the tutorial.
2. Earn gold through /work knight (most reliable early income).
3. Use !play every 12 hours for free lootboxes.
4. Check /shop daily for bargains.
5. Start building friendship EXP with Veyra.

MID GAME:
1. Unlock Smelter → mine ores → smelt into bars → sell for profit.
   Mining loop: /work miner → get ores → /smelt → sell bars.
   Copper Bar (50g), Iron Bar (150g), Silver Bar (450g).
2. Unlock Inventory and Pockets to hold more items.
3. Start doing /quest for bonus rewards.
4. Try the casino (/casino → !buychips → /gamble).
5. Challenge players to /battle for gold.
6. Start /campaign to progress through PvE stages.

LATE GAME:
1. Unlock Brewing Stand → craft potions for combat/economy buffs.
2. Complete Campaign Stage 10 to unlock Veyra's Grimoire + Veil of Darkness.
3. Complete Campaign Stage 15 to unlock Bardok's Claymore + Earthquake.
4. Dominate PvP with exclusive gear.
5. Trade on the marketplace for profit.
6. Max out all buildings.
7. Reach Veyra's favourite 💖 friendship tier.
8. Climb the leaderboard.

RESOURCE FLOW:
Mining → Ores → Smelting → Bars → Selling (gold)
Gold → Shop/Market → Items → Use/Trade
Gold → Casino → Chips → Gambling → Chips → Cashout → Gold
Gold → Buildings → Better crafting/storage/alchemy
Jobs → Gold + Lootboxes + Ores
Lootboxes → Gold + Items
Quests → Gold + EXP + Items


## SECTION: Command Quick Reference

PREFIX COMMANDS (!):
| Command                  | Description                          |
|--------------------------|--------------------------------------|
| !helloVeyra              | Register or check friendship         |
| !info <item>             | Item details                         |
| !use <item>              | Use consumable item                  |
| !buy <item> <qty>        | Buy from shop                        |
| !sell <item> <qty>       | Sell to shop buyback                 |
| !open <box>              | Open a lootbox                       |
| !unlock <building>       | Purchase a building                  |
| !upgrade <building>      | Upgrade a building                   |
| !bet <animal> <amount>   | Bet on animal race                   |
| !flipcoin                | Flip a coin                          |
| !play                    | Number guessing game                 |
| !solve_wordle            | Interactive Wordle solver             |
| !buychips <pack_id>      | Buy casino chip pack                 |
| !cashout <option_id>     | Cash out chips for gold              |
| !repayloan               | Repay active loan                    |

SLASH COMMANDS (/):
| Command                          | Description                          |
|----------------------------------|--------------------------------------|
| /help                            | View all commands                    |
| /commandhelp <command>           | Detailed help for one command        |
| /shop                            | View daily shop                      |
| /casino                          | View chip packs and cashout options  |
| /quest                           | View current quest                   |
| /battle @user <bet>              | Challenge to PvP battle              |
| /campaign                        | Fight campaign AI (PvE)              |
| /open_to_battle <min> <max>      | Join PvP auto-match queue            |
| /loadout                         | Change weapon and spell              |
| /transfer_gold @user <amount>    | Send gold (5% fee)                   |
| /transfer_item @user <item> <qty>| Give items to a player               |
| /find_item <item>                | Find item sources (25g cost)         |
| /create_listing                  | Create marketplace listing           |
| /delete_listing <id>             | Remove listing, refund items         |
| /loadmarketplace                 | Browse marketplace                   |
| /buy_from_marketplace <id> <qty> | Buy from a listing                   |
| /smelt <bar> <amount>            | Smelt ores into bars                 |
| /brew <potion>                   | Brew a potion                        |
| /leaderboard                     | View richest players                 |
| /start_race                      | Start animal race                    |
| /profile                         | View your profile                    |
| /invite                          | View invite milestones               |
| /loan                            | Take a loan                          |
| /wordle_hint                     | Get Wordle hint                      |
| /introduction                    | Create intro modal                   |

SLASH COMMAND GROUPS:
| Group    | Subcommands                                                     |
|----------|-----------------------------------------------------------------|
| /check   | wallet, energy, inventory, exp, smelter, brewing_stand, pockets, status |
| /work    | knight, digger, miner, explorer, thief                          |
| /gamble  | flipcoin, roulette, slots, dungeon                              |

"""
