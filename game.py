"""
game.py - the main game loop: draw the map, read a command, react.

Everything the player does passes through Game.handle(). The Game object owns the
current player, the maps and the NPCs, and saves progress to the database.
"""
import random

import story
import ui
from combat import battle
from inventory import inventory_menu
from map import build_maps
from monster import ShadowDragon, create_monster
from npc import create_npcs
from quest import ACTIVE, COMPLETED, NOT_STARTED

DIRECTIONS = {"w": (0, -1), "s": (0, 1), "a": (-1, 0), "d": (1, 0)}


class Game:
    def __init__(self, db, username, player):
        self.db = db
        self.username = username
        self.player = player
        self.maps = build_maps()
        self.npcs = create_npcs()
        self.running = True
        self.notice = ""          # one line of feedback shown under the map

        # fix a bad/missing saved position (new game, or a damaged save file)
        if player.map_key not in self.maps:
            player.map_key = "eldoria"
        if player.x is None or player.y is None or not self.current_map.is_walkable(player.x, player.y):
            player.x, player.y = self.current_map.spawn

    @property
    def current_map(self):
        return self.maps[self.player.map_key]

    # ---------- saving ----------
    def save(self):
        self.db.save_game(self.username, self.player.to_dict())

    # ---------- main loop ----------
    def run(self):
        if self.player.game_won:
            self.notice = "You already saved Eldoria! Feel free to keep exploring."
        while self.running:
            self.draw()
            command = ui.ask("\nCommand (H = help): ").lower()
            self.handle(command)
        self.save()

    def draw(self):
        p = self.player
        ui.clear()
        print(f"{ui.paint(p.name, ui.GREEN, True)}  Lv {p.level}  HP {ui.bar(p.hp, p.max_hp, 15)} "
              f"{p.hp}/{p.max_hp}  XP {p.xp}/{p.xp_needed}  {ui.gold_text(p.gold)}")
        print(ui.paint(f"-- {self.current_map.title} --", ui.CYAN, True))
        print(self.current_map.render(p.x, p.y, self.npcs))
        print(f"{ui.paint('@', ui.YELLOW, True)} you   "
              f"{ui.paint('E S H G W', ui.CYAN, True)} people   "
              f"{ui.paint(',', ui.GREEN)} tall grass (monsters)   "
              f"{ui.paint('> <', ui.MAGENTA, True)} portal   "
              f"{ui.paint('F', ui.YELLOW)} campfire")
        main = p.quests.main
        if main.status == ACTIVE:
            print(ui.paint(f"Quest: {main.objective_text()}", ui.MAGENTA))
        elif main.status != COMPLETED:
            print(ui.paint("Quest: talk to Elder Maren (E) in the village", ui.MAGENTA))
        if self.notice:
            print(ui.paint(self.notice, ui.YELLOW))
            self.notice = ""

    def handle(self, command):
        if command == "":
            return
        if all(char in DIRECTIONS for char in command):
            for char in command:            # 'ddd' walks right three times
                if self.move(char):         # stop early if something happened
                    break
            return
        actions = {
            "i": lambda: inventory_menu(self.player),
            "c": self.player.show_status,
            "k": self.player.show_skills,
            "j": self.show_journal,
            "h": lambda: ui.info(story.HELP),
        }
        if command in actions:
            actions[command]()
            ui.pause()
        elif command == "v":
            self.save()
            self.notice = "Game saved."
        elif command == "x":
            self.running = False
            ui.ok("Progress saved. Farewell, hero!")
        else:
            self.notice = "Unknown command. Type H for help."

    # ---------- moving ----------
    def move(self, key):
        """Try to step one tile. Returns True if something happened that should stop 'dddd'."""
        dx, dy = DIRECTIONS[key]
        p = self.player
        new_x, new_y = p.x + dx, p.y + dy
        game_map = self.current_map

        npc = game_map.npc_at(new_x, new_y, self.npcs)
        if npc:
            npc.interact(p)
            ui.pause()
            self.save()
            return True

        tile = game_map.tile(new_x, new_y)
        if tile in game_map.portals:
            self.use_portal(tile)
            return True
        if tile == "D":
            self.enter_lair()
            return True
        if not game_map.is_walkable(new_x, new_y):
            self.notice = "Something blocks your way."
            return True

        p.x, p.y = new_x, new_y
        if tile == "F":
            p.hp = p.max_hp
            self.notice = "You rest by the campfire and recover all your HP."
            self.save()
            return True
        if tile == "," and random.random() < game_map.encounter_rate:
            self.random_encounter()
            return True
        return False

    def cave_is_open(self):
        main = self.player.quests.main
        return main.status == COMPLETED or (main.status == ACTIVE and main.step_index >= 2)

    def use_portal(self, tile):
        destination, (x, y) = self.current_map.portals[tile]
        if destination == "cavern" and not self.cave_is_open():
            self.notice = "The cave gate is sealed. Captain Bram guards it - speak to him (and prove yourself)."
            return
        p = self.player
        p.map_key, p.x, p.y = destination, x, y
        self.notice = f"You travel to {self.current_map.title}."
        self.save()

    # ---------- fights ----------
    def random_encounter(self):
        monster = create_monster(random.choice(self.current_map.monster_pool))
        ui.bad(f"\nA wild {monster.name} appears!")
        ui.pause()
        result = battle(self.player, monster)
        if result == "lose":
            self.handle_defeat()
        else:
            ui.pause()
        self.save()

    def enter_lair(self):
        main = self.player.quests.main
        if main.status == COMPLETED:
            self.notice = "The dragon's lair is empty now. Only ashes remain."
            return
        if not (main.status == ACTIVE and main.step_index == 4):
            self.notice = "A magical seal blocks the lair. Elder Maren may know how to break it."
            return
        ui.warn("\nThe Shadow Dragon coils in the dark. You cannot flee from this fight!")
        if not ui.ask_yes_no("Heal up first if you need to. Enter the lair now?"):
            return
        result = battle(self.player, ShadowDragon())
        if result == "win":
            self.victory()
        elif result == "lose":
            self.handle_defeat()
        self.save()

    def handle_defeat(self):
        lost = self.player.respawn()
        p = self.player
        p.map_key = "eldoria"
        p.x, p.y = self.current_map.spawn
        ui.bad(f"\nYou wake up in Eldoria. You lost {lost} gold in the retreat.")
        ui.pause()

    def victory(self):
        self.player.game_won = True
        ui.clear()
        print()
        for line in story.VICTORY:
            ui.slow_print(ui.paint(line, ui.YELLOW, True), 0.01)
        ui.pause()
        self.running = False

    # ---------- quest journal ----------
    def show_journal(self):
        ui.header("Quest Journal", ui.MAGENTA)
        self.player.quests.refresh(self.player)
        for quest in self.player.quests.quests.values():
            kind = "MAIN" if quest.is_main else "SIDE"
            if quest.status == COMPLETED:
                state = ui.paint("completed", ui.GREEN)
            elif quest.status == ACTIVE:
                state = ui.paint("in progress", ui.YELLOW)
            else:
                state = ui.paint("not started", ui.GREY)
            print(f"\n[{kind}] {ui.paint(quest.title, ui.MAGENTA, True)} - {state}")
            if quest.status == ACTIVE:
                print(f"   Step {quest.step_index + 1}/{len(quest.steps)}: {quest.objective_text()}")
            elif quest.status == NOT_STARTED:
                hint = "Talk to Elder Maren in the village." if quest.is_main \
                    else "Someone in the village may need help..."
                print(f"   {hint}")
