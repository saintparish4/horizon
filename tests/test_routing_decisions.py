"""
Decisions are recorded server-side and outcomes link back to them.

The point of this table is trust: with real traffic you need to tell a followed
recommendation from an override, and the audit trail has to be the server's own
record rather than whatever the client chose to echo back.
"""

import pytest

from horizon.models import ExecutionStatus, RoutingDecision
from tests.conftest import requires_db

pytestmark = requires_db

CODE_TASK = "review this pull request for security vulnerabilities in the auth handler"
SIMILAR_TASK = "review this pull request for security vulnerabilities in the login handler"


async def _register(client, headers, name):
    resp = await client.post(
        "/v1/agents",
        json={
            "name": name,
            "endpoint": f"https://example.com/{name}",
            "description": "handles code review",
            "capabilities": ["code_review"],
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _route(client, headers, task=CODE_TASK, **extra):
    resp = await client.post("/v1/route", json={"task": task, **extra}, headers=headers)
    assert resp.status_code == 200, resp.text
    return resp.json()


class TestDecisionIsRecorded:
    async def test_route_returns_a_decision_id(self, client, org):
        await _register(client, org["headers"], "solo")
        body = await _route(client, org["headers"])
        assert body["decision_id"]

    async def test_the_decision_row_matches_what_the_caller_was_told(self, client, org, db):
        from sqlalchemy import select

        agent_id = await _register(client, org["headers"], "solo")
        body = await _route(client, org["headers"])

        row = (
            await db.execute(
                select(RoutingDecision).where(RoutingDecision.id == body["decision_id"])
            )
        ).scalar_one()
        assert str(row.selected_agent_id) == agent_id
        assert row.task == CODE_TASK
        assert row.confidence == pytest.approx(body["confidence"])
        assert row.exploring == body["reason"]["exploring"]
        # The stored embedding is what makes the second embed unnecessary.
        assert row.task_embedding is not None

    async def test_no_decision_is_stored_when_nothing_is_eligible(self, client, org, db):
        from sqlalchemy import func, select

        resp = await client.post("/v1/route", json={"task": CODE_TASK}, headers=org["headers"])
        assert resp.status_code == 422
        count = await db.scalar(select(func.count()).select_from(RoutingDecision))
        assert count == 0


class TestExecutionLinking:
    async def test_following_the_recommendation_records_followed_true(self, client, org):
        agent_id = await _register(client, org["headers"], "solo")
        decision = await _route(client, org["headers"])

        resp = await client.post(
            "/v1/executions",
            json={
                "agent_id": agent_id,
                "decision_id": decision["decision_id"],
                "status": ExecutionStatus.SUCCESS,
            },
            headers=org["headers"],
        )
        assert resp.status_code == 201, resp.text
        body = resp.json()
        assert body["followed"] is True
        assert body["decision_id"] == decision["decision_id"]
        # The task came from the stored decision, not from the request.
        assert body["task"] == CODE_TASK

    async def test_overriding_the_recommendation_records_followed_false(self, client, org):
        await _register(client, org["headers"], "recommended")
        other = await _register(client, org["headers"], "other")
        decision = await _route(client, org["headers"])
        # Force the override to be a genuine one.
        picked = decision["selected_agent"]["id"]
        override = other if other != picked else await _register(client, org["headers"], "third")

        resp = await client.post(
            "/v1/executions",
            json={
                "agent_id": override,
                "decision_id": decision["decision_id"],
                "status": ExecutionStatus.SUCCESS,
            },
            headers=org["headers"],
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["followed"] is False

    async def test_an_unlinked_execution_reports_followed_as_unknown(self, client, org):
        agent_id = await _register(client, org["headers"], "solo")
        resp = await client.post(
            "/v1/executions",
            json={"agent_id": agent_id, "task": CODE_TASK, "status": ExecutionStatus.SUCCESS},
            headers=org["headers"],
        )
        assert resp.status_code == 201, resp.text
        assert resp.json()["followed"] is None
        assert resp.json()["decision_id"] is None

    async def test_the_stored_reason_wins_over_whatever_the_client_sends(self, client, org, db):
        from sqlalchemy import select

        from horizon.models import Execution

        agent_id = await _register(client, org["headers"], "solo")
        decision = await _route(client, org["headers"])

        resp = await client.post(
            "/v1/executions",
            json={
                "agent_id": agent_id,
                "decision_id": decision["decision_id"],
                "status": ExecutionStatus.SUCCESS,
                "routing_reason": {"forged": "by the client"},
            },
            headers=org["headers"],
        )
        row = (
            await db.execute(select(Execution).where(Execution.id == resp.json()["id"]))
        ).scalar_one()
        assert "forged" not in row.routing_reason
        assert row.routing_reason["selected_agent_id"] == decision["selected_agent"]["id"]

    async def test_a_report_with_neither_task_nor_decision_is_rejected(self, client, org):
        agent_id = await _register(client, org["headers"], "solo")
        resp = await client.post(
            "/v1/executions",
            json={"agent_id": agent_id, "status": ExecutionStatus.SUCCESS},
            headers=org["headers"],
        )
        assert resp.status_code == 422


class TestTenantIsolation:
    async def test_a_decision_id_never_crosses_tenants(self, client, org):
        await _register(client, org["headers"], "mine")
        decision = await _route(client, org["headers"])

        other = await client.post(
            "/v1/organizations", json={"name": "Other", "email": "other-decisions@example.com"}
        )
        other_headers = {"Authorization": f"Bearer {other.json()['api_key']}"}
        their_agent = await _register(client, other_headers, "theirs")

        resp = await client.post(
            "/v1/executions",
            json={
                "agent_id": their_agent,
                "decision_id": decision["decision_id"],
                "status": ExecutionStatus.SUCCESS,
            },
            headers=other_headers,
        )
        # 404, not 403: confirming the row exists would itself leak.
        assert resp.status_code == 404


class TestEmbeddingReuse:
    async def test_linking_a_decision_costs_no_second_embedding(self, client, org):
        """The whole reason to store the vector: reporting an outcome is free."""
        from horizon.services.embeddings import DeterministicEmbeddings, set_embeddings

        class Counting(DeterministicEmbeddings):
            calls = 0

            async def embed_one(self, text: str) -> list[float]:
                Counting.calls += 1
                return await super().embed_one(text)

        set_embeddings(Counting())
        agent_id = await _register(client, org["headers"], "solo")

        Counting.calls = 0
        decision = await _route(client, org["headers"])
        assert Counting.calls == 1, "routing embeds the task once"

        await client.post(
            "/v1/executions",
            json={
                "agent_id": agent_id,
                "decision_id": decision["decision_id"],
                "status": ExecutionStatus.SUCCESS,
            },
            headers=org["headers"],
        )
        assert Counting.calls == 1, "reporting the outcome must reuse the stored embedding"

        await client.post(
            "/v1/executions",
            json={"agent_id": agent_id, "task": CODE_TASK, "status": ExecutionStatus.SUCCESS},
            headers=org["headers"],
        )
        assert Counting.calls == 2, "an unlinked report still has to embed"


class TestMinSimilarityOverride:
    async def test_raising_min_similarity_discards_loose_evidence(self, client, org):
        agent_id = await _register(client, org["headers"], "solo")
        for _ in range(3):
            await client.post(
                "/v1/executions",
                json={
                    "agent_id": agent_id,
                    "task": CODE_TASK,
                    "status": ExecutionStatus.SUCCESS,
                },
                headers=org["headers"],
            )

        loose = await _route(client, org["headers"], task=SIMILAR_TASK)
        strict = await _route(
            client,
            org["headers"],
            task=SIMILAR_TASK,
            min_similarity=0.99,
        )
        assert loose["reason"]["considered"][0]["sample_size"] > 0
        assert strict["reason"]["considered"][0]["sample_size"] == 0
