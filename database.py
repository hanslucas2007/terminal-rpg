"""
database.py - the ONLY file that talks to TinyDB.

TinyDB stores everything in one JSON file (rpg_save.json). JSON is plain text made of
dictionaries, lists, strings, numbers, true/false and null. That is why the Player
turns itself into a dictionary (to_dict) before saving: TinyDB can't store Python
objects like a Player or a Skill, only simple data.

Two "tables" (like two sheets in a spreadsheet):
    accounts -> {"username", "salt", "password_hash"}
    saves    -> {"username", "data": {...the whole player...}}
"""
from tinydb import Query, TinyDB


class Database:
    def __init__(self, path="rpg_save.json"):
        self.db = TinyDB(path, indent=2)
        self.accounts = self.db.table("accounts")
        self.saves = self.db.table("saves")

    # ----- accounts -----
    def get_account(self, username):
        """Return the account dictionary, or None if it does not exist."""
        row = Query()
        return self.accounts.get(row.username == username)

    def create_account(self, username, salt, password_hash):
        self.accounts.insert({"username": username, "salt": salt, "password_hash": password_hash})

    # ----- game saves -----
    def save_game(self, username, data):
        """Insert the save, or replace it if this user already has one (upsert)."""
        row = Query()
        self.saves.upsert({"username": username, "data": data}, row.username == username)

    def load_game(self, username):
        """Return the saved player dictionary, or None if this user never saved."""
        row = Query()
        record = self.saves.get(row.username == username)
        return record["data"] if record else None

    def close(self):
        self.db.close()
