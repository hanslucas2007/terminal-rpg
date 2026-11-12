"""
shop.py - buying and selling. A Shop is just a name plus a list of item names it stocks.
"""
import ui
from item import get_item


class Shop:
    def __init__(self, name, stock):
        self.name = name
        self.stock = stock   # list of item names for sale

    def open(self, player):
        while True:
            ui.header(self.name, ui.YELLOW)
            print(f"Your gold: {ui.gold_text(player.gold)}")
            print(" 1) Buy")
            print(" 2) Sell")
            print(" 0) Leave")
            choice = ui.ask_int("Choose: ", 0, 2)
            if choice == 0:
                return
            if choice == 1:
                self._buy(player)
            else:
                self._sell(player)

    def _buy(self, player):
        items = [get_item(name) for name in self.stock]
        print()
        for number, item in enumerate(items, start=1):
            print(f" {number}) {item.name:<22} {ui.gold_text(item.price):<22} {item.detail()}")
        print(" 0) Back")
        choice = ui.ask_int("Buy which item? ", 0, len(items))
        if choice == 0:
            return
        item = items[choice - 1]
        max_affordable = player.gold // item.price
        if max_affordable == 0:
            ui.warn(f"You cannot afford the {item.name}.")
            return
        quantity = ui.ask_int(f"How many? (1-{min(99, max_affordable)}, Enter = 1): ",
                              1, min(99, max_affordable), default=1)
        player.spend_gold(item.price * quantity)
        player.inventory.add(item.name, quantity)
        ui.ok(f"You bought {quantity}x {item.name} for {item.price * quantity} gold.")
        for message in player.quests.refresh(player):
            ui.quest_msg(message)

    def _sell(self, player):
        entries = [(item, qty) for item, qty in player.inventory.entries() if item.sellable]
        if not entries:
            ui.warn("You have nothing to sell.")
            return
        print()
        for number, (item, qty) in enumerate(entries, start=1):
            print(f" {number}) {item.name} x{qty} - sells for {ui.gold_text(item.sell_price)} each")
        print(" 0) Back")
        choice = ui.ask_int("Sell which item? ", 0, len(entries))
        if choice == 0:
            return
        item, owned = entries[choice - 1]
        quantity = ui.ask_int(f"How many? (1-{owned}, Enter = 1): ", 1, owned, default=1)
        player.inventory.remove(item.name, quantity)
        player.gold += item.sell_price * quantity
        ui.ok(f"You sold {quantity}x {item.name} for {item.sell_price * quantity} gold.")
