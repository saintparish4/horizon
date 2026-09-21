"""API key generation, hashing, and lookup.

Keys are never stored in plaintext. We hash with SHA-256 over a server-side
pepper; a leaked database dump does not yield usable credentials.

SHA-256 rather than bcrypt/argon2 is deliberate: these are 256-bit random
tokens, not user-chosen passwords, so there is no dictionary to attack and the
hash must stay fast enough to run on every request.
"""

import hashlib
import secrets

KEY_PREFIX_LIVE = "hzn_live_"
KEY_PREFIX_TEST = "hzn_test_"
PREFIX_DISPLAY_LEN = 16


def generate_key(live: bool = True) -> str:
    prefix = KEY_PREFIX_LIVE if live else KEY_PREFIX_TEST
    return f"{prefix}{secrets.token_urlsafe(32)}"


def hash_key(plaintext: str, pepper: str) -> str:
    return hashlib.sha256(f"{pepper}:{plaintext}".encode()).hexdigest()


def display_prefix(plaintext: str) -> str:
    return plaintext[:PREFIX_DISPLAY_LEN]
