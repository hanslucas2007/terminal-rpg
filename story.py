"""
story.py - the big blocks of story text, kept apart so game logic stays clean.
"""

TITLE_ART = r"""
  _____ _      _                  _        ___  ___   ___
 | ____| |  __| | ___  _ __ _  __| | __ _ | _ \| _ \ / __|
 |  _| | | / _` |/ _ \| '__| |/ _` |/ _` ||   /|  _/| (_ |
 |_____|_| \__,_|\___/|_|  |_|\__,_|\__,_||_|_\|_|   \___|
        T H E   S H A D O W   D R A G O N
"""

INTRO = [
    "For a thousand years, the village of Eldoria slept in peace.",
    "Beneath the Ashen Caverns, a Shadow Dragon slept too - bound by an ancient seal.",
    "But the seal is cracking. Goblins pour from the forest, wolves hunt on the roads,",
    "and the dead rise from their tombs in the caves.",
    "",
    "You arrive in Eldoria with a worn sword, a few coins and two red potions.",
    "The villagers look at you with a strange mixture of fear... and hope.",
    "Perhaps the Elder, Maren, knows why you were drawn here.",
]

VICTORY = [
    "The Shadow Dragon lets out one final, thunderous roar... and crumbles into ash.",
    "The cavern shakes, then falls silent. Light pours in through the cracks in the stone.",
    "",
    "When you step out of the Ashen Caverns, the whole village of Eldoria is waiting.",
    "They cheer your name. The seal is no more - and neither is the danger.",
    "",
    "*** CONGRATULATIONS! YOU HAVE SAVED ELDORIA! ***",
    "                THE END",
]

HELP = """
Movement:  W = up   A = left   S = down   D = right   (you can type several, like 'ddd')
Walk into a character (letter) to talk to them.
Walk into ',' (tall grass) and monsters may attack!

I = Inventory    C = Character sheet    K = Skills    J = Quest journal
V = Save game    H = Help               X = Save and exit
"""
