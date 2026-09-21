"""End-to-end API tests against a live PostgreSQL + pgvector."""

import pytest

from tests.conftest import requires_db

pytestmark = requires_db


class TestAuth:
    async def test_signup_returns_a_usable_key(self, client, org):
        resp = await client.get("/v1/organizations/me", headers=org["headers"])
        assert resp.status_code == 200
        assert resp.json()["plan"] == "free"

    async def test_signup_key_is_shown_once_and_looks_right(self, org):
        assert org["api_key"].startswith("hzn_live_")

    async def test_duplicate_email_is_rejected(self, client, org):
        resp = await client.post(
            "/v1/organizations", json={"name": "Acme 2", "email": "acme@example.com"}
        )
        assert resp.status_code == 409

    async def test_missing_key_is_401(self, client):
        assert (await client.get("/v1/organizations/me")).status_code == 401

    async def test_invalid_key_is_401(self, client):
        resp = await client.get(
            "/v1/organizations/me", headers={"Authorization": "Bearer hzn_live_nope"}
        )
        assert resp.status_code == 401

    async def test_x_api_key_header_also_works(self, client, org):
        resp = await client.get("/v1/organizations/me", headers={"X-API-Key": org["api_key"]})
        assert resp.status_code == 200

    async def test_plaintext_key_is_not_stored(self, client, org, db):
        from sqlalchemy import select

        from horizon.models import APIKey

        keys = (await db.execute(select(APIKey))).scalars().all()
        assert len(keys) == 1
        assert keys[0].key_hash != org["api_key"]
        assert org["api_key"] not in keys[0].key_hash


class TestMemories:
    async def test_store_then_search_finds_it(self, client, org):
        content = "The customer prefers dark mode and compact spacing"
        create = await client.post(
            "/v1/memories", json={"content": content}, headers=org["headers"]
        )
        assert create.status_code == 201
        assert create.json()["created"] is True

        search = await client.post(
            "/v1/memories/search",
            json={"query": "customer prefers dark mode compact", "min_similarity": 0.3},
            headers=org["headers"],
        )
        assert search.status_code == 200
        hits = search.json()["hits"]
        assert len(hits) == 1
        assert hits[0]["memory"]["content"] == content
        assert hits[0]["similarity"] > 0.3

    async def test_near_duplicate_is_deduped(self, client, org):
        payload = {"content": "The deploy pipeline runs on GitHub Actions"}
        first = await client.post("/v1/memories", json=payload, headers=org["headers"])
        second = await client.post("/v1/memories", json=payload, headers=org["headers"])

        assert first.json()["created"] is True
        assert second.json()["created"] is False
        assert second.json()["memory"]["id"] == first.json()["memory"]["id"]

    async def test_dedupe_can_be_disabled(self, client, org):
        payload = {"content": "Repeated note", "dedupe": False}
        a = await client.post("/v1/memories", json=payload, headers=org["headers"])
        b = await client.post("/v1/memories", json=payload, headers=org["headers"])
        assert a.json()["memory"]["id"] != b.json()["memory"]["id"]

    async def test_search_respects_collection_isolation(self, client, org):
        await client.post(
            "/v1/memories",
            json={"content": "agent alpha config detail", "collection": "alpha"},
            headers=org["headers"],
        )
        resp = await client.post(
            "/v1/memories/search",
            json={
                "query": "agent alpha config detail",
                "collection": "beta",
                "min_similarity": 0.1,
            },
            headers=org["headers"],
        )
        assert resp.json()["hits"] == []

    async def test_tag_filter_narrows_search(self, client, org):
        # Exercises the PG array overlap operator, which the generic
        # sqlalchemy.ARRAY type cannot express.
        await client.post(
            "/v1/memories",
            json={"content": "deployment runbook for the api service", "tags": ["ops"]},
            headers=org["headers"],
        )
        await client.post(
            "/v1/memories",
            json={"content": "deployment runbook for the web service", "tags": ["docs"]},
            headers=org["headers"],
        )

        base = {"query": "deployment runbook service", "min_similarity": 0.2}
        both = await client.post("/v1/memories/search", json=base, headers=org["headers"])
        assert len(both.json()["hits"]) == 2

        ops = await client.post(
            "/v1/memories/search", json={**base, "tags": ["ops"]}, headers=org["headers"]
        )
        hits = ops.json()["hits"]
        assert len(hits) == 1
        assert hits[0]["memory"]["tags"] == ["ops"]

    async def test_update_reembeds_content(self, client, org):
        created = await client.post(
            "/v1/memories", json={"content": "original wording here"}, headers=org["headers"]
        )
        mid = created.json()["memory"]["id"]

        await client.patch(
            f"/v1/memories/{mid}",
            json={"content": "completely different subject matter entirely"},
            headers=org["headers"],
        )
        # The new text must be findable; the old must not.
        found = await client.post(
            "/v1/memories/search",
            json={"query": "completely different subject matter entirely", "min_similarity": 0.5},
            headers=org["headers"],
        )
        assert len(found.json()["hits"]) == 1

        stale = await client.post(
            "/v1/memories/search",
            json={"query": "original wording here", "min_similarity": 0.5},
            headers=org["headers"],
        )
        assert stale.json()["hits"] == []

    async def test_delete_removes_the_memory(self, client, org):
        created = await client.post(
            "/v1/memories", json={"content": "temporary note"}, headers=org["headers"]
        )
        mid = created.json()["memory"]["id"]
        assert (
            await client.delete(f"/v1/memories/{mid}", headers=org["headers"])
        ).status_code == 204
        assert (await client.get(f"/v1/memories/{mid}", headers=org["headers"])).status_code == 404


class TestTenantIsolation:
    @pytest.fixture
    async def other_org(self, client):
        resp = await client.post(
            "/v1/organizations", json={"name": "Other", "email": "other@example.com"}
        )
        body = resp.json()
        return {"headers": {"Authorization": f"Bearer {body['api_key']}"}}

    async def test_search_never_crosses_tenants(self, client, org, other_org):
        await client.post(
            "/v1/memories",
            json={"content": "acme confidential revenue projection"},
            headers=org["headers"],
        )
        resp = await client.post(
            "/v1/memories/search",
            json={"query": "acme confidential revenue projection", "min_similarity": 0.1},
            headers=other_org["headers"],
        )
        assert resp.json()["hits"] == []

    async def test_direct_id_fetch_never_crosses_tenants(self, client, org, other_org):
        created = await client.post(
            "/v1/memories", json={"content": "acme secret"}, headers=org["headers"]
        )
        mid = created.json()["memory"]["id"]
        # Knowing the UUID must not be enough.
        resp = await client.get(f"/v1/memories/{mid}", headers=other_org["headers"])
        assert resp.status_code == 404

    async def test_delete_never_crosses_tenants(self, client, org, other_org):
        created = await client.post(
            "/v1/memories", json={"content": "acme secret"}, headers=org["headers"]
        )
        mid = created.json()["memory"]["id"]
        assert (
            await client.delete(f"/v1/memories/{mid}", headers=other_org["headers"])
        ).status_code == 404
        assert (await client.get(f"/v1/memories/{mid}", headers=org["headers"])).status_code == 200
