r"""
monster.py - all enemies, built with INHERITANCE.

                    Monster          (stats + the default way to attack)
      /     /      |       \          \
   Slime Goblin  Wolf   Skeleton  Orc      Boss      (each changes take_turn)
                                             |
                                        ShadowDragon

take_turn(player) is where monsters behave differently:
    Slime    = sometimes wobbles and does nothing
    Goblin   = 20% chance of a sneaky double-damage stab
    Wolf     = bites twice per turn (but weaker bites)
    Skeleton = high defense, normal attacks
    Orc      = charges for one turn, then smashes for triple damage
    Dragon   = fire breath every 3rd turn, enrages below half HP
"""
import random


class Monster:
    name = "Monster"
    max_hp = 20
    attack = 5
    defense = 0
    xp_reward = 10
    gold_range = (1, 5)
    drops = []            # list of (item name, chance from 0 to 1)
    is_boss = False

    def __init__(self):
        self.hp = self.max_hp
        self.poison_damage = 0
        self.poison_turns = 0

    def is_alive(self):
        return self.hp > 0

    def take_damage(self, amount):
        """Lower HP (never below 0) and return the damage actually dealt."""
        dealt = min(amount, self.hp)
        self.hp -= dealt
        return dealt

    def apply_poison(self, damage, turns):
        self.poison_damage = damage
        self.poison_turns = turns

    def process_effects(self):
        """Poison hurts the monster at the start of its turn. Returns a message or None."""
        if self.poison_turns > 0:
            self.poison_turns -= 1
            dealt = self.take_damage(self.poison_damage)
            return f"The poison burns {self.name} for {dealt} damage."
        return None

    def basic_hit(self, player, multiplier=1.0, bonus=0):
        damage = int((self.attack + bonus + random.randint(-2, 2)) * multiplier) - player.defense
        return player.take_damage(max(1, damage))

    def take_turn(self, player):
        """Default behavior: one normal attack. Returns a list of messages."""
        dealt = self.basic_hit(player)
        return [f"{self.name} attacks you for {dealt} damage."]

    def roll_gold(self):
        return random.randint(*self.gold_range)

    def roll_drops(self):
        return [name for name, chance in self.drops if random.random() < chance]


class Slime(Monster):
    name = "Slime"
    max_hp = 22
    attack = 5
    defense = 0
    xp_reward = 12
    gold_range = (3, 8)
    drops = [("Slime Jelly", 0.6), ("Health Potion", 0.08)]

    def take_turn(self, player):
        if random.random() < 0.3:
            return ["The Slime jiggles around harmlessly."]
        return super().take_turn(player)


class Goblin(Monster):
    name = "Goblin"
    max_hp = 32
    attack = 8
    defense = 1
    xp_reward = 20
    gold_range = (5, 12)
    drops = [("Goblin Ear", 0.5), ("Health Potion", 0.15)]

    def take_turn(self, player):
        if random.random() < 0.2:
            dealt = self.basic_hit(player, multiplier=2)
            return [f"The Goblin stabs you from the shadows for {dealt} damage!"]
        return super().take_turn(player)


class Wolf(Monster):
    name = "Wolf"
    max_hp = 38
    attack = 10
    defense = 2
    xp_reward = 28
    gold_range = (4, 10)
    drops = [("Wolf Pelt", 1.0)]

    def take_turn(self, player):
        first = self.basic_hit(player, multiplier=0.7)
        second = self.basic_hit(player, multiplier=0.7)
        return [f"The Wolf bites you twice for {first} and {second} damage."]


class Skeleton(Monster):
    name = "Skeleton"
    max_hp = 55
    attack = 13
    defense = 5
    xp_reward = 45
    gold_range = (10, 20)
    drops = [("Bone Fragment", 0.5), ("Dragon Sigil", 1.0), ("Greater Health Potion", 0.1)]


class Orc(Monster):
    name = "Orc"
    max_hp = 75
    attack = 17
    defense = 6
    xp_reward = 70
    gold_range = (15, 30)
    drops = [("Orc Tusk", 0.5), ("Greater Health Potion", 0.25)]

    def __init__(self):
        super().__init__()
        self.charging = False

    def take_turn(self, player):
        if self.charging:
            self.charging = False
            dealt = self.basic_hit(player, multiplier=3)
            return [f"The Orc SMASHES you with its club for {dealt} damage!"]
        self.charging = True
        return ["The Orc raises its club high... it is charging a heavy attack!"]


class Boss(Monster):
    """A boss is a monster that cannot be escaped from and keeps count of its turns."""
    is_boss = True

    def __init__(self):
        super().__init__()
        self.turn_count = 0


class ShadowDragon(Boss):
    name = "Shadow Dragon"
    max_hp = 120
    attack = 26
    defense = 8
    xp_reward = 500
    gold_range = (250, 350)
    drops = [("Greater Health Potion", 1.0)]
    breath_damage = 38

    def __init__(self):
        super().__init__()
        self.enraged = False

    def take_turn(self, player):
        self.turn_count += 1
        messages = []
        if not self.enraged and self.hp < self.max_hp // 2:
            self.enraged = True
            self.attack += 6
            messages.append("The Shadow Dragon roars in fury! It is ENRAGED!")
        if self.turn_count % 3 == 0:
            dealt = player.take_damage(self.breath_damage)   # fire breath ignores defense
            messages.append(f"The Shadow Dragon unleashes a wave of black fire for {dealt} damage!")
        else:
            dealt = self.basic_hit(player)
            messages.append(f"The Shadow Dragon rakes you with its claws for {dealt} damage.")
        return messages


MONSTER_CLASSES = {cls.name: cls for cls in [Slime, Goblin, Wolf, Skeleton, Orc, ShadowDragon]}


def create_monster(name):
    return MONSTER_CLASSES[name]()
