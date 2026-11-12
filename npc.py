r"""
npc.py - the five townsfolk, built with INHERITANCE.

                         NPC        (shared: name, symbol, talking, quest hooks)
        /         /        |         \          \
 ElderMaren   Blacksmith  Healer   Captain   Hermit   (each: own dialogue + own extras)

Talking to an NPC runs interact(), which always does the same 4 steps:
    1. say the dialogue   2. maybe offer a quest   3. tell the quests "you talked to X"
    4. open the NPC's extra menu (shop, healing, skill training...)
Children override the steps that make them different.
"""
import ui
from quest import ACTIVE, COMPLETED, NOT_STARTED
from shop import Shop
from skill import SKILL_CLASSES, create_skill


class NPC:
    def __init__(self, npc_id, name, symbol, map_key):
        self.npc_id = npc_id      # used by quests: "talk to maren"
        self.name = name
        self.symbol = symbol      # the letter shown on the map
        self.map_key = map_key    # which map this NPC lives on

    def dialogue(self, player):
        """List of lines the NPC says. Children override this."""
        return ["..."]

    def offer_quest(self, player):
        """Children that give quests override this."""

    def extra_menu(self, player):
        """Children with a shop/service override this."""

    def interact(self, player):
        ui.header(self.name)
        for line in self.dialogue(player):
            ui.npc_say(self.name, line)
        self.offer_quest(player)
        for message in player.quests.on_talk(self.npc_id, player):
            ui.quest_msg(message)
        self.extra_menu(player)

    def offer_side_quest(self, player, quest_id, question):
        """Shared helper: ask the player to accept a side quest."""
        quest = player.quests.get(quest_id)
        if quest.status != NOT_STARTED:
            return
        if ui.ask_yes_no(question):
            for message in quest.start(player):
                ui.quest_msg(message)
        else:
            ui.npc_say(self.name, "No worries. Come back if you change your mind.")


class ElderMaren(NPC):
    def dialogue(self, player):
        main = player.quests.main
        if main.status == NOT_STARTED:
            return ["Traveler! The gods must have sent you. Eldoria is in grave danger.",
                    "A Shadow Dragon sleeps beneath the Ashen Caverns, and its seal is failing.",
                    "Will you stand against it?"]
        if main.status == COMPLETED:
            return ["Hero of Eldoria! Children now play at being you.",
                    "The village will never forget what you did."]
        lines = {
            0: ["Find Captain Bram on the forest road, east across the river. He will test you."],
            1: ["The goblins are the dragon's scouts. Defeat one and Bram will open the cave gate."],
            2: ["The Ashen Caverns are crawling with undead. Skeletons guard an ancient Dragon Sigil.",
                "Bring it to me - only the sigil can break the seal on the dragon's chamber."],
            3: ["The Dragon Sigil! You actually found it!",
                "Hold still... there. The seal on the dragon's chamber is broken."],
            4: ["The way is open. Go deep into the caverns and end this, hero.",
                "Drink a potion before you walk in. You will need it."],
        }
        return lines[main.step_index]

    def offer_quest(self, player):
        main = player.quests.main
        if main.status == NOT_STARTED and ui.ask_yes_no("Accept the main quest?"):
            for message in main.start(player):
                ui.quest_msg(message)


class Blacksmith(NPC):
    def __init__(self, *args):
        super().__init__(*args)
        self.shop = Shop("Torg's Forge", ["Iron Sword", "Steel Sword", "Leather Armor", "Chain Mail"])

    def dialogue(self, player):
        pelts = player.quests.get("pelts")
        if pelts.status == NOT_STARTED:
            return ["Hmph. Another adventurer. Don't touch the swords unless you're buying.",
                    "...Actually, I'm short on wolf pelts. The leather straps don't make themselves."]
        if pelts.status == ACTIVE and pelts.step_index == 0:
            return ["One wolf pelt. Wolves roam the tall grass in the forest. Get moving."]
        if pelts.status == ACTIVE:
            return ["A fine pelt! The wolves left you in one piece, I see.",
                    "Here, take this armor as thanks. I made it myself."]
        return ["Steel doesn't lie, friend. Buy the best and you'll live longer."]

    def offer_quest(self, player):
        self.offer_side_quest(player, "pelts", "Help Torg? (side quest: collect a Wolf Pelt)")

    def extra_menu(self, player):
        if ui.ask_yes_no("Browse Torg's weapons and armor?"):
            self.shop.open(player)


class Healer(NPC):
    HEAL_PRICE = 10

    def __init__(self, *args):
        super().__init__(*args)
        self.shop = Shop("Lila's Remedies", ["Health Potion", "Greater Health Potion"])

    def dialogue(self, player):
        slime = player.quests.get("slime")
        if slime.status == NOT_STARTED:
            return ["Oh, hello dear. Mind the mud on the floor - those slimes keep oozing into my garden.",
                    "I would pay someone to clear them out..."]
        if slime.status == ACTIVE and slime.step_index == 0:
            return ["Two slimes, remember? They like the tall grass in the forest."]
        if slime.status == ACTIVE:
            return ["You did it! My herbs are safe again. Thank you, dear!"]
        return ["Stay safe out there. My door is always open if you need healing."]

    def offer_quest(self, player):
        self.offer_side_quest(player, "slime", "Help Lila? (side quest: defeat 2 Slimes)")

    def extra_menu(self, player):
        while True:
            print(f"\n 1) Heal me ({self.HEAL_PRICE} gold)   2) Shop   0) Leave")
            choice = ui.ask_int("Choose: ", 0, 2)
            if choice == 0:
                return
            if choice == 2:
                self.shop.open(player)
            elif player.hp >= player.max_hp:
                ui.warn("You are already at full HP.")
            elif not player.spend_gold(self.HEAL_PRICE):
                ui.warn("You cannot afford that.")
            else:
                player.hp = player.max_hp
                ui.ok("Lila's gentle magic restores you to full health.")


class Captain(NPC):
    def dialogue(self, player):
        main = player.quests.main
        if main.status == NOT_STARTED:
            return ["Halt. The forest road is no place for travelers.",
                    "If you want to help, speak to Elder Maren in the village."]
        if main.status == COMPLETED:
            return ["The dragon is dead... I never thought I would see the day. Well fought."]
        if main.step_index == 0:
            return ["Maren sent you? Hah. We'll see about that.",
                    "Prove yourself: defeat a goblin in this forest. Then I'll open the gate to the caverns."]
        if main.step_index == 1:
            return ["Find a goblin in the tall grass and take it down. The gate stays shut until then."]
        return ["The gate to the Ashen Caverns is open. The portal '>' is at the end of the road.",
                "Watch out for skeletons, and for orcs that charge up their blows."]


class Hermit(NPC):
    def dialogue(self, player):
        if player.skills:
            return ["Ahh, you carry the spark now. Skills are not magic, child - they are habits.",
                    "Master them and use them wisely, for they need time to recover."]
        return ["Shhh... the trees are whispering about you.",
                "I have lived alone for forty years, and I have learned a few tricks.",
                "For a little gold, I could teach you."]

    def extra_menu(self, player):
        skill_names = list(SKILL_CLASSES)
        while True:
            print()
            for number, name in enumerate(skill_names, start=1):
                skill = SKILL_CLASSES[name]
                status = "(learned)" if player.has_skill(name) else f"{skill.cost} gold, level {skill.level_required}"
                print(f" {number}) {name:<14} {status}")
                print(f"      {skill.description}  Cooldown: {skill.cooldown}")
            print(" 0) Leave")
            choice = ui.ask_int("Learn which skill? ", 0, len(skill_names))
            if choice == 0:
                return
            skill = create_skill(skill_names[choice - 1])
            if player.has_skill(skill.name):
                ui.warn("You already know that skill.")
            elif player.level < skill.level_required:
                ui.warn(f"You must be level {skill.level_required} to learn {skill.name}.")
            elif not player.spend_gold(skill.cost):
                ui.warn("You cannot afford that.")
            else:
                player.learn_skill(skill)
                ui.ok(f"You learned {skill.name}!")


def create_npcs():
    """All NPCs in the game. The symbol must match a letter in the map layouts."""
    return [
        ElderMaren("maren", "Elder Maren", "E", "eldoria"),
        Blacksmith("torg", "Torg the Blacksmith", "S", "eldoria"),
        Healer("lila", "Lila the Healer", "H", "eldoria"),
        Captain("bram", "Captain Bram", "G", "eldoria"),
        Hermit("oswin", "Oswin the Hermit", "W", "eldoria"),
    ]
