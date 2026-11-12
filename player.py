"""
player.py - the hero: stats, progression, and saving/loading.

to_dict()   turns the Player into plain data (numbers, text, lists, dicts) for TinyDB.
from_dict() does the reverse: builds a Player object back from that data.
"""
import ui
from inventory import Inventory
from item import get_item
from quest import QuestLog
from skill import create_skill


class Player:
    def __init__(self, name):
        self.name = name
        self.level = 1
        self.xp = 0
        self.max_hp = 60
        self.hp = 60
        self.base_attack = 8
        self.base_defense = 2
        self.gold = 200
        self.inventory = Inventory()
        self.inventory.add("Health Potion", 2)
        self.skills = []                 # list of Skill objects
        self.quests = QuestLog()
        self.weapon = None               # name of the equipped weapon
        self.armor = None                # name of the equipped armor
        self.map_key = "eldoria"
        self.x = None                    # None means "use the map's starting spot"
        self.y = None
        self.game_won = False

    # ----- stats -----
    @property
    def attack(self):
        weapon = get_item(self.weapon) if self.weapon else None
        return self.base_attack + (weapon.attack_bonus if weapon else 0)

    @property
    def defense(self):
        armor = get_item(self.armor) if self.armor else None
        return self.base_defense + (armor.defense_bonus if armor else 0)

    @property
    def xp_needed(self):
        return 10 + 10 * (self.level - 1)

    # ----- changing the player -----
    def take_damage(self, amount):
        dealt = min(amount, self.hp)
        self.hp -= dealt
        return dealt

    def heal(self, amount):
        healed = min(amount, self.max_hp - self.hp)
        self.hp += healed
        return healed

    def is_alive(self):
        return self.hp > 0

    def gain_xp(self, amount):
        """Add XP, level up as many times as needed. Returns messages to print."""
        messages = []
        self.xp += amount
        while self.xp >= self.xp_needed:
            self.xp -= self.xp_needed
            self.level += 1
            self.max_hp += 12
            self.base_attack += 2
            self.base_defense += 1
            self.hp = self.max_hp
            messages.append(f"LEVEL UP! You are now level {self.level}! (+12 HP, +2 Attack, +1 Defense)")
        return messages

    def spend_gold(self, amount):
        if self.gold < amount:
            return False
        self.gold -= amount
        return True

    def has_skill(self, skill_name):
        return any(skill.name == skill_name for skill in self.skills)

    def learn_skill(self, skill):
        self.skills.append(skill)

    def equip(self, item):
        """Put on a weapon/armor. The old one goes back into the bag."""
        old_name = getattr(self, item.slot)
        self.inventory.remove(item.name)
        setattr(self, item.slot, item.name)
        if old_name:
            self.inventory.add(old_name)

    def respawn(self):
        """After dying: back to full HP, but lose half your gold."""
        self.hp = self.max_hp
        lost = self.gold // 2
        self.gold -= lost
        return lost

    # ----- showing progress -----
    def show_status(self):
        ui.header(f"{self.name} - Level {self.level}", ui.GREEN)
        print(f"HP:      {ui.bar(self.hp, self.max_hp)} {self.hp}/{self.max_hp}")
        print(f"XP:      {ui.bar(self.xp, self.xp_needed, color=ui.BLUE)} {self.xp}/{self.xp_needed}")
        print(f"Gold:    {ui.gold_text(self.gold)}")
        print(f"Attack:  {self.attack}  (base {self.base_attack})")
        print(f"Defense: {self.defense}  (base {self.base_defense})")
        print(f"Weapon:  {self.weapon or 'none'}")
        print(f"Armor:   {self.armor or 'none'}")
        if self.inventory.is_empty():
            print("Items:   (empty)")
        else:
            bag = ", ".join(f"{item.name} x{qty}" for item, qty in self.inventory.entries())
            print(f"Items:   {bag}")
        if self.skills:
            print("Skills:  " + ", ".join(skill.name for skill in self.skills))
        else:
            print("Skills:  (none learned yet - visit Oswin the Hermit)")
        main = self.quests.main
        if main.status == "completed":
            print("Main quest: COMPLETE")
        elif main.status == "active":
            print(f"Main quest: {main.objective_text()}")
        else:
            print("Main quest: not started (talk to Elder Maren)")

    def show_skills(self):
        ui.header("Skills", ui.MAGENTA)
        if not self.skills:
            ui.info("You have not learned any skills yet. Oswin the Hermit can teach you.")
            return
        for skill in self.skills:
            print(f"- {ui.paint(skill.name, ui.MAGENTA, True)} (cooldown {skill.cooldown} turns): "
                  f"{skill.description}")

    # ----- saving / loading -----
    def to_dict(self):
        return {
            "name": self.name,
            "level": self.level,
            "xp": self.xp,
            "hp": self.hp,
            "max_hp": self.max_hp,
            "base_attack": self.base_attack,
            "base_defense": self.base_defense,
            "gold": self.gold,
            "inventory": self.inventory.to_dict(),
            "skills": [skill.name for skill in self.skills],
            "quests": self.quests.to_dict(),
            "weapon": self.weapon,
            "armor": self.armor,
            "map": self.map_key,
            "x": self.x,
            "y": self.y,
            "game_won": self.game_won,
        }

    @classmethod
    def from_dict(cls, data):
        player = cls(data.get("name", "Hero"))
        player.level = data.get("level", 1)
        player.xp = data.get("xp", 0)
        player.max_hp = data.get("max_hp", 60)
        player.hp = min(data.get("hp", player.max_hp), player.max_hp)
        player.base_attack = data.get("base_attack", 8)
        player.base_defense = data.get("base_defense", 2)
        player.gold = data.get("gold", 0)
        player.inventory = Inventory.from_dict(data.get("inventory"))
        player.skills = [s for s in (create_skill(n) for n in data.get("skills", [])) if s]
        player.quests = QuestLog.from_dict(data.get("quests"))
        player.weapon = data.get("weapon") if get_item(data.get("weapon") or "") else None
        player.armor = data.get("armor") if get_item(data.get("armor") or "") else None
        player.map_key = data.get("map", "eldoria")
        player.x = data.get("x")
        player.y = data.get("y")
        player.game_won = data.get("game_won", False)
        return player
