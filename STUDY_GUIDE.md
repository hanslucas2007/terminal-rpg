# Study Guide (for Midterm 2)

Read this next to the code. Each section matches one of the "Key Logic" topics.

## 1. How the game is designed (the big picture)
Think of the game as a team where each file has one job:

- `main.py` shows the menu and starts everything.
- `game.py` is the "manager": it repeats **draw the map -> ask for a command -> react**.
- Other files are specialists the manager calls: `combat.py` (fights), `npc.py` (talking),
  `shop.py` (buying), `quest.py` (goals), `map.py` (the world), `player.py` (the hero).
- `database.py` and `auth.py` handle saving and accounts.
- `ui.py` is used by everyone to print colors and to ask for input safely.

Typical flow: `main()` -> register/login -> `Game.run()` loop -> `handle(command)` ->
`move()` -> bumps into NPC (`npc.interact`) or steps on grass (`random_encounter` -> `battle`).

## 2. How data is stored and restored in TinyDB
TinyDB is a tiny database that keeps everything in one text file, `rpg_save.json`.

**Format = JSON.** JSON can only hold simple things: numbers, text, True/False, None,
lists and dictionaries. It cannot hold a Python object like `Player` or `Fireball()`.
So we convert:

- **Save:** `player.to_dict()` builds a dictionary of simple values (skills become a list of
  *names*, the inventory is `{"Health Potion": 3}`, quests are `{"status", "step", "progress"}`).
  Then `db.save_game(username, data)` stores it with `upsert` (insert if new, replace if it exists).
- **Restore:** `db.load_game(username)` returns the dictionary and `Player.from_dict(data)`
  rebuilds the object. Skill names go through `create_skill(name)` to become real skill objects again.
  `from_dict` uses `.get(key, default)` so a missing value doesn't crash the game.

Two tables: `accounts` (username, salt, password_hash) and `saves` (username, data).
`Query().username == name` is how TinyDB searches a table.

## 3. How class inheritance works
A child class (`class Goblin(Monster)`) automatically gets everything its parent has, and can
**override** (replace) methods to behave differently.

- `Monster` has HP, `take_damage()`, `take_turn()`. `Goblin`, `Wolf`, `Orc`... change `take_turn()`
  (Goblin crits, Wolf bites twice, Orc charges then smashes). `Boss(Monster)` -> `ShadowDragon(Boss)`.
- `Skill` has `cooldown`, `is_ready()`, `use()`. Each child (`Fireball`, `Heal`...) writes its own `use()`.
- Also used for items (`Item -> Consumable -> Potion`, `Item -> Equipment -> Weapon/Armor`) and NPCs.
- **Polymorphism:** `combat.py` just calls `monster.take_turn(player)` or `skill.use(...)`
  without caring which child it is. Python runs the right version automatically.
- `super().__init__()` calls the parent's setup code first (see `Orc.__init__`).

## 4. How register and login work (`auth.py`)
- We never store the real password. On register we make a random **salt**, then store
  `hash_password(password, salt)`, a one-way scramble.
- On login we scramble what the user typed using the *stored* salt and compare with the stored hash.
  Same result = correct password. `hmac.compare_digest` does the comparison safely.
- Username rules are checked with a regular expression; duplicates are rejected via `db.get_account`.

## 5. How quest status is tracked (`quest.py`)
Each quest is a list of steps done in order. Only three values are saved per quest:
`status` (not_started / active / completed), `step` (index of the current step), `progress` (kills so far).

Events call into the quest log:
- Kill a monster -> `quests.on_kill(name)`; talk to an NPC -> `quests.on_talk(npc_id)`;
  bag changes -> `quests.refresh()` (for "collect" steps).
- If the event matches the current step, `_finish_step()` moves `step_index` forward; after the last step,
  `_complete()` pays gold/XP/items and sets `status = "completed"`.
- Game rules read that state: the cave gate opens when main quest `step >= 2`;
  the dragon's lair opens when `step == 4`; killing the Shadow Dragon completes the quest and wins the game.

## 6. Other things a test might ask
- **Cooldowns:** using a skill sets `current_cooldown = cooldown`; `tick()` lowers it by 1 each turn.
- **Level up:** `gain_xp()` loops `while xp >= xp_needed`, so one big reward can give several levels.
- **Maps:** a list of strings; `grid[y][x]` is a tile; `is_walkable()` allows only `. , F`.
  NPC letters are found in the text and replaced with floor.
- **Input validation:** `ui.ask_int` keeps asking (try/except ValueError + range check) until valid.
- **Death:** `player.respawn()` restores HP and removes half the gold; you wake up in Eldoria.
