"""
ui.py - how the game LOOKS (colors, bars) and how it READS input safely.

Color meanings used everywhere in the game, so the player learns them:
    RED      = damage, monsters, danger
    GREEN    = healing, success, HP
    YELLOW   = gold, warnings
    CYAN     = NPC speech
    MAGENTA  = quests
    WHITE    = normal text
Only plain ASCII characters are used so it works in any terminal.
"""
import os
import time

from colorama import Fore, Style, init

init()  # makes colors work on Windows too

RED = Fore.RED
GREEN = Fore.GREEN
YELLOW = Fore.YELLOW
BLUE = Fore.BLUE
MAGENTA = Fore.MAGENTA
CYAN = Fore.CYAN
WHITE = Fore.WHITE
GREY = Style.DIM + Fore.WHITE


def paint(text, color, bold=False):
    """Wrap text in a color code. RESET_ALL turns the color off afterwards."""
    prefix = (Style.BRIGHT if bold else "") + color
    return f"{prefix}{text}{Style.RESET_ALL}"


# ---------- Printing helpers ----------
def ok(message):
    print(paint(message, GREEN))


def bad(message):
    print(paint(message, RED))


def warn(message):
    print(paint(message, YELLOW))


def info(message):
    print(message)


def quest_msg(message):
    print(paint(message, MAGENTA, True))


def npc_say(name, line):
    print(paint(f"{name}: ", CYAN, True) + paint(f'"{line}"', CYAN))


def gold_text(amount):
    return paint(f"{amount} gold", YELLOW, True)


def header(title, color=CYAN):
    line = "=" * (len(title) + 6)
    print()
    print(paint(line, color, True))
    print(paint(f"   {title}", color, True))
    print(paint(line, color, True))


def bar(current, maximum, width=20, color=None):
    """Draw a progress bar like [=========-----------]."""
    maximum = max(1, maximum)
    current = max(0, min(current, maximum))
    filled = int(width * current / maximum)
    if color is None:
        ratio = current / maximum
        color = GREEN if ratio > 0.5 else YELLOW if ratio > 0.25 else RED
    return "[" + paint("=" * filled, color) + paint("-" * (width - filled), GREY) + "]"


def slow_print(text, delay=0.012):
    """Typewriter effect for the story intro (the delay is tiny so it stays quick)."""
    for char in text:
        print(char, end="", flush=True)
        time.sleep(delay)
    print()


def clear():
    os.system("cls" if os.name == "nt" else "clear")


# ---------- Input helpers (all input validation lives here) ----------
def ask(prompt):
    return input(paint(prompt, CYAN)).strip()


def ask_int(prompt, low, high, default=None):
    """Keep asking until the player types a whole number between low and high."""
    while True:
        raw = ask(prompt)
        if raw == "" and default is not None:
            return default
        try:
            value = int(raw)
        except ValueError:
            warn("Please type a number.")
            continue
        if low <= value <= high:
            return value
        warn(f"Please choose a number between {low} and {high}.")


def ask_yes_no(prompt):
    while True:
        raw = ask(prompt + " (y/n): ").lower()
        if raw in ("y", "yes"):
            return True
        if raw in ("n", "no"):
            return False
        warn("Please answer y or n.")


def pause():
    input(paint("\n[Press Enter to continue]", GREY))
