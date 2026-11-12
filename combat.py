"""
combat.py - turn-based battles.

One round of battle:
    1. skill cooldowns tick down            4. monster takes poison damage (if poisoned)
    2. the player chooses a move            5. the monster takes its turn
    3. if the monster died -> victory       6. if the player died -> defeat
battle() returns "win", "lose" or "fled".
"""
import random

import ui
from item import Consumable, get_item


def show_battle_status(player, monster):
    poison = ui.paint(f"  (poisoned {monster.poison_turns})", ui.GREEN) if monster.poison_turns else ""
    print()
    print(f"{ui.paint(monster.name, ui.RED, True):<22} HP {ui.bar(monster.hp, monster.max_hp)} "
          f"{monster.hp}/{monster.max_hp}{poison}")
    print(f"{ui.paint(player.name, ui.GREEN, True):<22} HP {ui.bar(player.hp, player.max_hp)} "
          f"{player.hp}/{player.max_hp}")


def attack_move(player, monster):
    damage = max(1, player.attack + random.randint(-2, 3) - monster.defense)
    if random.random() < 0.1:
        damage *= 2
        ui.warn("Critical hit!")
    dealt = monster.take_damage(damage)
    ui.info(f"You strike the {monster.name} for {ui.paint(dealt, ui.RED, True)} damage.")


def skill_move(player, monster):
    """Returns True if a skill was used (the turn is spent)."""
    if not player.skills:
        ui.warn("You don't know any skills yet. Visit Oswin the Hermit!")
        return False
    print()
    for number, skill in enumerate(player.skills, start=1):
        status = ui.paint("ready", ui.GREEN) if skill.is_ready() \
            else ui.paint(f"cooldown {skill.current_cooldown}", ui.RED)
        print(f" {number}) {skill.name:<14} [{status}] {skill.description}")
    print(" 0) Back")
    choice = ui.ask_int("Use which skill? ", 0, len(player.skills))
    if choice == 0:
        return False
    skill = player.skills[choice - 1]
    if not skill.is_ready():
        ui.warn(f"{skill.name} is still on cooldown for {skill.current_cooldown} more turn(s).")
        return False
    ui.info(ui.paint(skill.use(player, monster), ui.MAGENTA, True))
    skill.start_cooldown()
    return True


def item_move(player):
    """Returns True if an item was used (the turn is spent)."""
    usable = [(item, qty) for item, qty in player.inventory.entries() if isinstance(item, Consumable)]
    if not usable:
        ui.warn("You have no usable items.")
        return False
    print()
    for number, (item, qty) in enumerate(usable, start=1):
        print(f" {number}) {item.name} x{qty} - {item.detail()}")
    print(" 0) Back")
    choice = ui.ask_int("Use which item? ", 0, len(usable))
    if choice == 0:
        return False
    item = usable[choice - 1][0]
    can_use, reason = item.can_use(player)
    if not can_use:
        ui.warn(reason)
        return False
    if not player.inventory.remove(item.name):
        return False   # safety: never use an item the player does not have
    ui.ok(item.use(player))
    return True


def player_turn(player, monster):
    """Keep asking until the player does something. Returns 'acted' or 'fled'."""
    while True:
        print("\n 1) Attack   2) Skill   3) Item   4) Run")
        choice = ui.ask_int("Your move: ", 1, 4)
        if choice == 1:
            attack_move(player, monster)
            return "acted"
        if choice == 2 and skill_move(player, monster):
            return "acted"
        if choice == 3 and item_move(player):
            return "acted"
        if choice == 4:
            if monster.is_boss:
                ui.warn(f"You cannot run from the {monster.name}!")
            elif random.random() < 0.5:
                ui.ok("You got away safely!")
                return "fled"
            else:
                ui.bad("You failed to escape!")
                return "acted"


def give_rewards(player, monster):
    """XP, gold, item drops, and tell the quests that a monster died."""
    gold = monster.roll_gold()
    player.gold += gold
    ui.ok(f"You defeated the {monster.name}!")
    print(f"Gained {ui.paint(str(monster.xp_reward) + ' XP', ui.BLUE, True)} and {ui.gold_text(gold)}.")
    for name in monster.roll_drops():
        item = get_item(name)
        if not item.sellable and player.inventory.has(name):
            continue   # never drop a second copy of a quest item
        player.inventory.add(name)
        print(f"The {monster.name} dropped: {ui.paint(name, ui.YELLOW, True)}")
    for message in player.gain_xp(monster.xp_reward):
        ui.ok(message)
    for message in player.quests.on_kill(monster.name, player) + player.quests.refresh(player):
        ui.quest_msg(message)


def battle(player, monster):
    ui.header(f"BATTLE: {monster.name}", ui.RED)
    for skill in player.skills:
        skill.current_cooldown = 0   # skills start every fight ready
    first_turn = True
    while True:
        if not first_turn:
            for skill in player.skills:
                skill.tick()
        first_turn = False

        show_battle_status(player, monster)
        if player_turn(player, monster) == "fled":
            return "fled"
        if not monster.is_alive():
            give_rewards(player, monster)
            return "win"

        poison_message = monster.process_effects()
        if poison_message:
            ui.info(ui.paint(poison_message, ui.GREEN))
            if not monster.is_alive():
                give_rewards(player, monster)
                return "win"

        for message in monster.take_turn(player):
            ui.info(ui.paint(message, ui.RED))
        if not player.is_alive():
            ui.bad("You collapse to the ground...")
            return "lose"
