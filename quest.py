"""
quest.py - quests and how their progress is tracked.

A Quest is a list of QuestSteps done in order. Each step has a KIND:
    "talk"    -> talk to an NPC (target = npc id)
    "kill"    -> defeat monsters (target = monster name, amount = how many)
    "collect" -> have items in your bag (target = item name, amount = how many)

What we SAVE for each quest is just three small values (this is the "quest status"):
    status      -> "not_started", "active" or "completed"
    step_index  -> which step we are on (0 = first step)
    progress    -> how many kills/items so far on the current step
The quest text itself never changes, so it is rebuilt from code on every launch,
and the saved status is loaded on top of it.
"""

NOT_STARTED = "not_started"
ACTIVE = "active"
COMPLETED = "completed"


class QuestStep:
    def __init__(self, description, kind, target, amount=1, consume=None):
        self.description = description
        self.kind = kind
        self.target = target
        self.amount = amount
        self.consume = consume   # (item name, quantity) removed from the bag when the step ends


class Quest:
    def __init__(self, quest_id, title, steps, reward_gold=0, reward_xp=0,
                 reward_items=None, is_main=False):
        self.quest_id = quest_id
        self.title = title
        self.steps = steps
        self.reward_gold = reward_gold
        self.reward_xp = reward_xp
        self.reward_items = reward_items or []   # list of (item name, quantity)
        self.is_main = is_main
        self.status = NOT_STARTED
        self.step_index = 0
        self.progress = 0

    # ----- reading the state -----
    def current_step(self):
        if self.status == ACTIVE:
            return self.steps[self.step_index]
        return None

    def objective_text(self):
        step = self.current_step()
        if step is None:
            return ""
        if step.amount > 1:
            return f"{step.description} ({self.progress}/{step.amount})"
        return step.description

    # ----- changing the state (each returns a list of messages to print) -----
    def start(self, player):
        self.status = ACTIVE
        self.step_index = 0
        self.progress = 0
        messages = [f"Quest started: {self.title}", f"Objective: {self.objective_text()}"]
        return messages + self.refresh(player)

    def refresh(self, player):
        """Check 'collect' steps against the bag. Call this whenever the bag changes."""
        step = self.current_step()
        if step is not None and step.kind == "collect":
            have = player.inventory.count(step.target)
            self.progress = min(have, step.amount)
            if have >= step.amount:
                return self._finish_step(player)
        return []

    def on_kill(self, monster_name, player):
        step = self.current_step()
        if step is None or step.kind != "kill" or step.target != monster_name:
            return []
        self.progress += 1
        if self.progress >= step.amount:
            return self._finish_step(player)
        return [f"{self.title}: {self.objective_text()}"]

    def on_talk(self, npc_id, player):
        step = self.current_step()
        if step is None or step.kind != "talk" or step.target != npc_id:
            return []
        return self._finish_step(player)

    def _finish_step(self, player):
        step = self.steps[self.step_index]
        messages = [f"Step complete: {step.description}"]
        if step.consume:
            player.inventory.remove(*step.consume)
        self.step_index += 1
        self.progress = 0
        if self.step_index >= len(self.steps):
            return messages + self._complete(player)
        messages.append(f"New objective: {self.objective_text()}")
        return messages + self.refresh(player)   # the next step might already be done

    def _complete(self, player):
        self.status = COMPLETED
        messages = [f"*** QUEST COMPLETE: {self.title} ***"]
        if self.reward_gold:
            player.gold += self.reward_gold
            messages.append(f"Reward: {self.reward_gold} gold")
        for name, qty in self.reward_items:
            player.inventory.add(name, qty)
            messages.append(f"Reward: {name} x{qty}")
        if self.reward_xp:
            messages.append(f"Reward: {self.reward_xp} XP")
            messages += player.gain_xp(self.reward_xp)
        return messages

    # ----- saving / loading -----
    def to_dict(self):
        return {"status": self.status, "step": self.step_index, "progress": self.progress}

    def load(self, data):
        status = data.get("status", NOT_STARTED)
        step = data.get("step", 0)
        if status not in (NOT_STARTED, ACTIVE, COMPLETED) or not isinstance(step, int):
            return   # damaged data: keep the quest as "not started"
        if status == COMPLETED:
            step = len(self.steps)            # a finished quest has passed every step
        elif not 0 <= step < len(self.steps):
            return
        self.status = status
        self.step_index = step
        progress = data.get("progress", 0)
        self.progress = progress if isinstance(progress, int) and progress >= 0 else 0


def build_quests():
    """Create fresh (not started) copies of every quest in the game."""
    main = Quest(
        "main", "The Shadow Dragon",
        [
            QuestStep("Speak to Captain Bram on the forest road", "talk", "bram"),
            QuestStep("Defeat a Goblin in Whispering Forest", "kill", "Goblin"),
            QuestStep("Find the Dragon Sigil in the Ashen Caverns (Skeletons carry it)",
                      "collect", "Dragon Sigil", 1),
            QuestStep("Bring the Dragon Sigil to Elder Maren", "talk", "maren",
                      consume=("Dragon Sigil", 1)),
            QuestStep("Defeat the Shadow Dragon in the depths of the cavern", "kill", "Shadow Dragon"),
        ],
        reward_gold=500, reward_xp=500, is_main=True)

    slime = Quest(
        "slime", "Slime Trouble",
        [
            QuestStep("Defeat 2 Slimes in the forest", "kill", "Slime", 2),
            QuestStep("Return to Lila the Healer", "talk", "lila"),
        ],
        reward_gold=60, reward_xp=50, reward_items=[("Health Potion", 2)])

    pelts = Quest(
        "pelts", "Pelts for Torg",
        [
            QuestStep("Collect a Wolf Pelt", "collect", "Wolf Pelt"),
            QuestStep("Bring the pelt to Torg the Blacksmith", "talk", "torg",
                      consume=("Wolf Pelt", 1)),
        ],
        reward_gold=80, reward_xp=70, reward_items=[("Leather Armor", 1)])

    return [main, slime, pelts]


class QuestLog:
    """Holds all quests of one player and passes game events to them."""

    def __init__(self):
        self.quests = {quest.quest_id: quest for quest in build_quests()}

    def get(self, quest_id):
        return self.quests[quest_id]

    @property
    def main(self):
        return self.quests["main"]

    def on_kill(self, monster_name, player):
        messages = []
        for quest in self.quests.values():
            messages += quest.on_kill(monster_name, player)
        return messages

    def on_talk(self, npc_id, player):
        messages = []
        for quest in self.quests.values():
            messages += quest.on_talk(npc_id, player)
        return messages

    def refresh(self, player):
        messages = []
        for quest in self.quests.values():
            messages += quest.refresh(player)
        return messages

    def to_dict(self):
        return {quest_id: quest.to_dict() for quest_id, quest in self.quests.items()}

    @classmethod
    def from_dict(cls, data):
        log = cls()
        for quest_id, quest_data in (data or {}).items():
            if quest_id in log.quests and isinstance(quest_data, dict):
                log.quests[quest_id].load(quest_data)
        return log
