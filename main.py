"""
main.py - the entry point. Run the game with:  uv run main.py   (or: python main.py)

Flow:  title screen -> register / login -> (new game: story intro) -> Game.run()
"""
import auth
import story
import ui
from database import Database
from game import Game
from player import Player


def start_game(db, username):
    saved = db.load_game(username)
    if saved:
        player = Player.from_dict(saved)
        ui.ok(f"Loading your saved game... Welcome back, {player.name} (level {player.level}).")
        ui.pause()
    else:
        player = Player(username)
        ui.clear()
        print()
        for line in story.INTRO:
            ui.slow_print(ui.paint(line, ui.CYAN), 0.005)
        ui.pause()
        ui.info(story.HELP)
        ui.pause()
    game = Game(db, username, player)
    try:
        game.run()
    except (KeyboardInterrupt, EOFError):
        game.save()                 # never lose progress if the window is closed
        print("\nGame saved. Goodbye!")
        raise SystemExit


def main():
    db = Database()
    try:
        while True:
            ui.clear()
            print(ui.paint(story.TITLE_ART, ui.YELLOW, True))
            print(" 1) Register\n 2) Login\n 0) Quit")
            choice = ui.ask_int("Choose: ", 0, 2)
            if choice == 0:
                break
            username = auth.register(db) if choice == 1 else auth.login(db)
            if username:
                start_game(db, username)
            else:
                ui.pause()
    except (KeyboardInterrupt, EOFError):
        print("\nGoodbye!")
    finally:
        db.close()


if __name__ == "__main__":
    main()
