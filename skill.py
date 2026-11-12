r"""
skill.py - skills the player can learn, built with INHERITANCE.

                 Skill   (shared stuff: name, cooldown, "is it ready?")
          /       |        |        \
   PowerStrike  Heal  PoisonSting  Fireball   (each overrides use() with its own effect)

COOLDOWN = how many turns you must wait before using the skill again.
Using a skill sets current_cooldown to its cooldown; every new turn it goes down by 1.
The save file only stores skill NAMES; create_skill(name) rebuilds the object.
"""
import random


class Skill:
    name = "Skill"
    description = ""
    cooldown = 1          # turns to wait after using it
    cost = 0              # gold the trainer charges
    level_required = 1

    def __init__(self):
        self.current_cooldown = 0

    def is_ready(self):
        return self.current_cooldown == 0

    def start_cooldown(self):
        self.current_cooldown = self.cooldown

    def tick(self):
        """Called at the start of each player turn."""
        if self.current_cooldown > 0:
            self.current_cooldown -= 1

    def use(self, user, target):
        """Do the skill's effect and return a message. Every child class overrides this."""
        raise NotImplementedError("Each skill decides its own effect.")


class PowerStrike(Skill):
    name = "Power Strike"
    description = "A mighty blow: 1.8x your Attack (enemy Defense still applies)."
    cooldown = 2
    cost = 25
    level_required = 1

    def use(self, user, target):
        damage = max(1, int(user.attack * 1.8) + random.randint(0, 3) - target.defense)
        dealt = target.take_damage(damage)
        return f"You swing with all your might! Power Strike hits {target.name} for {dealt} damage."


class Heal(Skill):
    name = "Heal"
    description = "Restore 30 HP plus 5 per level."
    cooldown = 4
    cost = 40
    level_required = 2

    def use(self, user, target):
        healed = user.heal(30 + 5 * user.level)
        return f"A warm light surrounds you. You recover {healed} HP."


class PoisonSting(Skill):
    name = "Poison Sting"
    description = "Poison the enemy: 6 damage per turn for 4 turns (ignores Defense)."
    cooldown = 3
    cost = 60
    level_required = 3

    def use(self, user, target):
        target.apply_poison(6, 4)
        return f"You coat your blade in venom. {target.name} is poisoned!"


class Fireball(Skill):
    name = "Fireball"
    description = "Magic fire: 22 damage plus 5 per level (ignores Defense)."
    cooldown = 3
    cost = 100
    level_required = 4

    def use(self, user, target):
        damage = 22 + 5 * user.level + random.randint(0, 6)
        dealt = target.take_damage(damage)
        return f"A fireball explodes on {target.name} for {dealt} damage!"


SKILL_CLASSES = {cls.name: cls for cls in [PowerStrike, Heal, PoisonSting, Fireball]}


def create_skill(name):
    """Build a fresh skill from its name. Returns None if the name is unknown."""
    skill_class = SKILL_CLASSES.get(name)
    return skill_class() if skill_class else None
