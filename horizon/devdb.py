"""
Zero-dependency local Postgres for development and tests.

`pgserver` ships a self-contained PostgreSQL 16 build with pgvector, so a
contributor needs neither Docker nor a system Postgres to run the real stack.
Production points DATABASE_URL at a managed instance instead; nothing else in
the codebase imports this module.
"""

import pathlib
import sys

DEFAULT_DATA_DIR = pathlib.Path.home() / ".horizon" / "pgdata"
DB_NAME = "horizon"


def start(data_dir: pathlib.Path | None = None) -> str:
    """Start (or reuse) a local server and return an asyncpg URL for `horizon`."""
    import pgserver

    data_dir = data_dir or DEFAULT_DATA_DIR
    data_dir.mkdir(parents=True, exist_ok=True)

    # cleanup_mode=None leaves the server running after this process exits,
    # so `make db` behaves like `docker compose up -d` rather than dying
    # the moment the command returns.
    server = pgserver.get_server(str(data_dir), cleanup_mode=None)
    existing = server.psql(f"SELECT 1 FROM pg_database WHERE datname = '{DB_NAME}'")
    if "1 row" not in existing:
        server.psql(f"CREATE DATABASE {DB_NAME}")
    # psql() always attaches to the bootstrap database, so switch with a
    # meta-command: the extension has to live in the target database.
    server.psql(f"\\connect {DB_NAME}\nCREATE EXTENSION IF NOT EXISTS vector;")

    return f"postgresql+asyncpg://postgres@/{DB_NAME}?host={data_dir}"


if __name__ == "__main__":
    url = start()
    print(url)
    print(f"\nAdd to .env:\n  DATABASE_URL={url}", file=sys.stderr)
