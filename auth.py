"""
auth.py - register and login.

We NEVER store the real password. We store:
    salt          = random text, different for every account
    password_hash = a scrambled version of (password + salt)
When logging in we scramble what the user typed with the same salt and compare.
If the scrambled results match, the password was right.
"""
import hashlib
import hmac
import os
import re
from getpass import getpass

import ui

USERNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,16}$")
MIN_PASSWORD_LENGTH = 4
MAX_LOGIN_ATTEMPTS = 3


def hash_password(password, salt):
    """Scramble the password with PBKDF2 (a standard, slow-on-purpose hashing method)."""
    return hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000).hex()


def read_password(prompt):
    """getpass hides what you type. Some editors can't hide it, so fall back to input()."""
    try:
        return getpass(prompt)
    except Exception:
        return input(prompt)


def register(db):
    """Create a new account. Returns the username, or None if the player cancelled."""
    ui.header("Create Account")
    ui.info("Username: 3-16 letters, numbers or underscores. Press Enter on an empty line to cancel.")
    while True:
        username = ui.ask("Choose a username: ")
        if username == "":
            return None
        if not USERNAME_PATTERN.match(username):
            ui.warn("Invalid username. Use 3-16 letters, numbers or underscores.")
            continue
        username = username.lower()
        if db.get_account(username):
            ui.warn("That username is already taken.")
            continue
        break

    while True:
        password = read_password("Choose a password (min 4 characters): ")
        if len(password) < MIN_PASSWORD_LENGTH:
            ui.warn(f"Password must be at least {MIN_PASSWORD_LENGTH} characters.")
            continue
        if password != read_password("Type the password again: "):
            ui.warn("Passwords did not match. Try again.")
            continue
        break

    salt = os.urandom(16).hex()
    db.create_account(username, salt, hash_password(password, salt))
    ui.ok(f"Account '{username}' created!")
    return username


def login(db):
    """Log in an existing account. Returns the username, or None if it failed/cancelled."""
    ui.header("Login")
    username = ui.ask("Username (Enter to cancel): ").lower()
    if username == "":
        return None
    account = db.get_account(username)
    if account is None:
        ui.bad("No account with that username.")
        return None

    for attempt in range(1, MAX_LOGIN_ATTEMPTS + 1):
        password = read_password("Password: ")
        attempt_hash = hash_password(password, account["salt"])
        # compare_digest is a safe way to compare two hashes
        if hmac.compare_digest(attempt_hash, account["password_hash"]):
            ui.ok(f"Welcome back, {username}!")
            return username
        ui.bad(f"Wrong password. ({attempt}/{MAX_LOGIN_ATTEMPTS})")
    ui.bad("Too many failed attempts.")
    return None
