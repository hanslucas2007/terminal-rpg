# Eldoria RPG: The Shadow Dragon

A terminal RPG in Python with TinyDB saving and colorama colors.

## Run it
```
uv add colorama tinydb
uv run main.py        # or: python main.py
```
Register an account, log in, and play. Your progress is saved to `rpg_save.json`,
so you can quit (`X`) and log back in later to continue.

## Controls
`W A S D` move (you can type several, like `ddd`) | `I` inventory | `C` character sheet |
`K` skills | `J` quest journal | `V` save | `H` help | `X` save and exit.
Walk into a letter (E S H G W) to talk to that character. Tall grass `,` can hide monsters.

## Files
| File | Job |
|---|---|
| main.py | Entry point: title menu, register/login, starts the game |
| game.py | Main loop: draws the map, reads commands, moving, portals, boss, saving |
| auth.py | Register and login (salted password hashing) |
| database.py | The only file that talks to TinyDB |
| player.py | The hero: stats, leveling, to_dict / from_dict |
| monster.py | Monster base class + Slime, Goblin, Wolf, Skeleton, Orc, Boss, ShadowDragon |
| skill.py | Skill base class + PowerStrike, Heal, PoisonSting, Fireball |
| combat.py | Turn-based battle loop and rewards |
| item.py | Item classes (Potion, Weapon, Armor, Material, QuestItem) and the item list |
| inventory.py | The bag + inventory menu |
| quest.py | Quest, QuestStep, QuestLog (main quest + 2 side quests) |
| npc.py | 5 NPCs, each with their own dialogue and job |
| shop.py | Buying and selling |
| map.py | The 2 maps (text layouts), drawing, walkable checks, portals |
| ui.py | Colors, bars, safe input helpers (input validation) |
| story.py | Intro, ending and help text |
