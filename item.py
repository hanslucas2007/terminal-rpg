r"""
item.py - every item in the game, built with INHERITANCE.

                         Item
        /------------/-----|-----\-------------\
   Consumable      Equipment  Material      QuestItem
       |           /      \
     Potion     Weapon   Armor

A child class gets everything from its parent for free and only adds what is different.
Items never change, so we create each one once and keep them in the ITEMS dictionary.
The save file only stores item NAMES; get_item(name) turns a name back into an item.
"""


class Item:
    category = "Item"
    sellable = True

    def __init__(self, name, description, price):
        self.name = name
        self.description = description
        self.price = price

    @property
    def sell_price(self):
        return self.price // 2 if self.sellable else 0

    def detail(self):
        """Short text shown in menus. Children override this."""
        return self.description


class Consumable(Item):
    category = "Consumable"

    def can_use(self, player):
        return True, ""

    def use(self, player):
        raise NotImplementedError("Each consumable decides what 'use' does.")


class Potion(Consumable):
    def __init__(self, name, description, price, heal_amount):
        super().__init__(name, description, price)
        self.heal_amount = heal_amount

    def can_use(self, player):
        if player.hp >= player.max_hp:
            return False, "You are already at full HP."
        return True, ""

    def use(self, player):
        healed = player.heal(self.heal_amount)
        return f"You drink the {self.name} and recover {healed} HP."

    def detail(self):
        return f"Restores {self.heal_amount} HP"


class Equipment(Item):
    category = "Equipment"
    slot = ""


class Weapon(Equipment):
    category = "Weapon"
    slot = "weapon"

    def __init__(self, name, description, price, attack_bonus):
        super().__init__(name, description, price)
        self.attack_bonus = attack_bonus

    def detail(self):
        return f"+{self.attack_bonus} Attack"


class Armor(Equipment):
    category = "Armor"
    slot = "armor"

    def __init__(self, name, description, price, defense_bonus):
        super().__init__(name, description, price)
        self.defense_bonus = defense_bonus

    def detail(self):
        return f"+{self.defense_bonus} Defense"


class Material(Item):
    """Loot dropped by monsters. Useless in battle, but you can sell it."""
    category = "Material"

    def detail(self):
        return f"{self.description} (sells for {self.sell_price} gold)"


class QuestItem(Item):
    """Important story items. They cannot be sold."""
    category = "Quest Item"
    sellable = False


ITEMS = {item.name: item for item in [
    Potion("Health Potion", "A red potion.", 20, 40),
    Potion("Greater Health Potion", "A glowing red potion.", 50, 80),
    Weapon("Iron Sword", "A plain but sturdy sword.", 60, 4),
    Weapon("Steel Sword", "A sharp, well-balanced blade.", 150, 8),
    Armor("Leather Armor", "Light armor made of hide.", 50, 2),
    Armor("Chain Mail", "Heavy rings of linked steel.", 140, 5),
    Material("Slime Jelly", "Sticky green goo.", 10),
    Material("Goblin Ear", "A pointy green ear.", 12),
    Material("Wolf Pelt", "A thick grey pelt.", 24),
    Material("Bone Fragment", "A brittle piece of bone.", 16),
    Material("Orc Tusk", "A heavy yellowed tusk.", 30),
    QuestItem("Dragon Sigil", "An ancient emblem. It hums with power.", 0),
]}


def get_item(name):
    """Return the Item with this name, or None if the name is unknown."""
    return ITEMS.get(name)
