"""
Integration test fixtures.

These run against a real PostgreSQL with pgvector (via `pgserver`, no Docker
required) and a deterministic offline embedding provider, so the full stack —
SQL, vector search, HNSW indexes, routing — is exercised without a network call.
"""

import os
import pathlib
import subprocess
import tempfile

import pytest
import pytest_asyncio

# Point the app at the test database before anything imports settings.
_TMP = pathlib.Path(tempfile.gettempdir()) / "horizon-test-pgdata"


def _bootstrap_database() -> str:
    from horizon import devdb

    return devdb.start(_TMP)


try:
    os.environ["DATABASE_URL"] = _bootstrap_database()
    os.environ.setdefault("API_KEY_PEPPER", "test-pepper")
    _DB_AVAILABLE = True
    _DB_SKIP_REASON = ""
except Exception as exc:  # pragma: no cover - environment dependent
    # Skipping keeps `make test` usable on a machine where pgserver cannot
    # start. In CI that silence is dangerous — a green run that tested nothing
    # looks identical to a real one — so HORIZON_REQUIRE_DB turns it into a hard
    # failure. CI sets it; see .github/workflows/ci.yml.
    if os.environ.get("HORIZON_REQUIRE_DB"):
        raise RuntimeError(
            f"HORIZON_REQUIRE_DB is set but no test database could start: {exc}"
        ) from exc
    _DB_AVAILABLE = False
    _DB_SKIP_REASON = f"no test database: {exc}"


requires_db = pytest.mark.skipif(not _DB_AVAILABLE, reason=_DB_SKIP_REASON)


@pytest.fixture(scope="session", autouse=True)
def _migrate() -> None:
    if not _DB_AVAILABLE:
        return
    subprocess.run(
        [".venv/bin/alembic", "upgrade", "head"],
        check=True,
        capture_output=True,
        env={**os.environ},
    )


@pytest.fixture(autouse=True)
def _offline_embeddings():
    """Swap in deterministic embeddings for every test, then restore."""
    from horizon.services.embeddings import DeterministicEmbeddings, set_embeddings

    set_embeddings(DeterministicEmbeddings())
    yield
    set_embeddings(None)


@pytest_asyncio.fixture
async def db():
    if not _DB_AVAILABLE:
        pytest.skip(_DB_SKIP_REASON)

    from sqlalchemy import text

    from horizon.config.database import SessionLocal

    async with SessionLocal() as session:
        # Truncate rather than recreate: keeps the HNSW indexes in place so
        # tests hit the same query plans production does.
        await session.execute(
            text(
                "TRUNCATE organizations, api_keys, memories, agents, "
                "routing_decisions, executions CASCADE"
            )
        )
        await session.commit()
        yield session


@pytest_asyncio.fixture
async def client(db):
    import httpx

    from horizon.main import app

    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as c:
        yield c


@pytest_asyncio.fixture
async def org(client):
    """A signed-up organization with an auth header ready to use."""
    resp = await client.post(
        "/v1/organizations", json={"name": "Acme", "email": "acme@example.com"}
    )
    assert resp.status_code == 201, resp.text
    body = resp.json()
    return {
        "id": body["org_id"],
        "api_key": body["api_key"],
        "headers": {"Authorization": f"Bearer {body['api_key']}"},
    }
