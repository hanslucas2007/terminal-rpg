"""
inventory.py - the bag the player carries, plus the inventory menu.

Data format: a dictionary of  item name -> how many, e.g. {"Health Potion": 3, "Wolf Pelt": 2}.
That is already JSON-friendly, so saving it is just  inventory.to_dict().
"""
import ui
from item import Consumable, Equipment, get_item


class Inventory:
    def __init__(self):
        self.items = {}

    def add(self, name, amount=1):
        if amount <= 0:
            return   # ignore nonsense amounts, so the bag never holds "x0" items
        self.items[name] = self.items.get(name, 0) + amount

    def count(self, name):
        return self.items.get(name, 0)

    def has(self, name, amount=1):
        return self.count(name) >= amount

    def remove(self, name, amount=1):
        """Remove items. Returns False (and changes nothing) if there are not enough."""
        if not self.has(name, amount):
            return False
        self.items[name] -= amount
        if self.items[name] == 0:
            del self.items[name]
        return True

    def entries(self):
        """List of (Item object, quantity) sorted by name."""
        return [(get_item(name), qty) for name, qty in sorted(self.items.items())]

    def is_empty(self):
        return len(self.items) == 0

    def to_dict(self):
        return dict(self.items)

    @classmethod
    def from_dict(cls, data):
        inventory = cls()
        for name, qty in (data or {}).items():
            # ignore corrupted data: unknown items or bad quantities
            if get_item(name) is not None and isinstance(qty, int) and qty > 0:
                inventory.items[name] = qty
        return inventory


def inventory_menu(player):
    """Let the player look at, use or equip items."""
    while True:
        ui.header("Inventory", ui.YELLOW)
        print(f"Gold: {ui.gold_text(player.gold)}")
        print(f"Weapon: {player.weapon or 'none'}   Armor: {player.armor or 'none'}")
        entries = player.inventory.entries()
        if not entries:
            ui.info("\nYour bag is empty.")
            return
        print()
        for number, (item, qty) in enumerate(entries, start=1):
            print(f" {number}) {item.name} x{qty}  [{item.category}] - {item.detail()}")
        print(" 0) Back")
        choice = ui.ask_int("Choose an item to use/equip: ", 0, len(entries))
        if choice == 0:
            return

        item = entries[choice - 1][0]
        if isinstance(item, Consumable):
            can_use, reason = item.can_use(player)
            if not can_use:
                ui.warn(reason)
                continue
            player.inventory.remove(item.name)
            ui.ok(item.use(player))
        elif isinstance(item, Equipment):
            player.equip(item)
            ui.ok(f"You equipped the {item.name}.")
        else:
            ui.info(f"{item.name}: {item.description}")
