"""
Routing behaviour against a live database.

These are the tests that matter most: they assert the product's central claim,
that routing improves as execution history accumulates.
"""

from horizon.models import ExecutionStatus
from tests.conftest import requires_db

pytestmark = requires_db

CODE_TASK = "review this pull request for security vulnerabilities in the auth handler"
SIMILAR_CODE_TASK = "review this pull request for security vulnerabilities in the login handler"
PROSE_TASK = "summarize the quarterly earnings call transcript into three bullet points"


async def _register(client, headers, name, description, capabilities, cost=0.0):
    resp = await client.post(
        "/v1/agents",
        json={
            "name": name,
            "endpoint": f"https://example.com/{name}",
            "description": description,
            "capabilities": capabilities,
            "cost_per_call_usd": cost,
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text
    return resp.json()["id"]


async def _record(client, headers, agent_id, task, status, quality=None):
    resp = await client.post(
        "/v1/executions",
        json={
            "agent_id": agent_id,
            "task": task,
            "status": status,
            "quality_score": quality,
            "latency_ms": 100,
        },
        headers=headers,
    )
    assert resp.status_code == 201, resp.text


class TestRoutingBasics:
    async def test_routing_with_no_agents_is_422(self, client, org):
        resp = await client.post("/v1/route", json={"task": CODE_TASK}, headers=org["headers"])
        assert resp.status_code == 422

    async def test_single_agent_is_selected(self, client, org):
        agent_id = await _register(client, org["headers"], "solo", "does everything", ["general"])
        resp = await client.post("/v1/route", json={"task": CODE_TASK}, headers=org["headers"])
        assert resp.status_code == 200
        assert resp.json()["selected_agent"]["id"] == agent_id

    async def test_decision_includes_a_full_audit_trail(self, client, org):
        await _register(client, org["headers"], "a", "reviews code", ["code_review"])
        await _register(client, org["headers"], "b", "writes prose", ["summarize"])

        resp = await client.post("/v1/route", json={"task": CODE_TASK}, headers=org["headers"])
        reason = resp.json()["reason"]
        # Every candidate considered must be reported, not just the winner.
        assert len(reason["considered"]) == 2
        assert reason["weights"]["evidence"] == 0.6
        for entry in reason["considered"]:
            assert {"agent_name", "score", "evidence", "capability", "sample_size"} <= entry.keys()

    async def test_disabled_agents_are_not_routed_to(self, client, org):
        good = await _register(client, org["headers"], "good", "reviews code", ["code_review"])
        bad = await _register(client, org["headers"], "bad", "reviews code", ["code_review"])

        await client.delete(f"/v1/agents/{bad}", headers=org["headers"])
        resp = await client.post("/v1/route", json={"task": CODE_TASK}, headers=org["headers"])
        assert resp.json()["selected_agent"]["id"] == good

    async def test_required_capabilities_filter_candidates(self, client, org):
        await _register(client, org["headers"], "coder", "x", ["code_review"])
        summarizer = await _register(client, org["headers"], "writer", "x", ["summarize"])

        resp = await client.post(
            "/v1/route",
            json={"task": PROSE_TASK, "required_capabilities": ["summarize"]},
            headers=org["headers"],
        )
        assert resp.json()["selected_agent"]["id"] == summarizer


class TestLearning:
    """The core claim: outcomes change future routing."""

    async def test_routing_shifts_to_the_agent_that_actually_succeeds(self, client, org):
        # Both agents declare the same capabilities, so capability similarity
        # cannot break the tie — only execution history can.
        good = await _register(
            client, org["headers"], "good", "handles code review", ["code_review"]
        )
        bad = await _register(client, org["headers"], "bad", "handles code review", ["code_review"])

        for _ in range(5):
            await _record(client, org["headers"], good, CODE_TASK, ExecutionStatus.SUCCESS)
            await _record(client, org["headers"], bad, CODE_TASK, ExecutionStatus.FAILURE)

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        body = resp.json()
        assert body["selected_agent"]["id"] == good

        winner = next(c for c in body["reason"]["considered"] if c["agent_id"] == good)
        loser = next(c for c in body["reason"]["considered"] if c["agent_id"] == bad)
        assert winner["evidence"] > loser["evidence"]
        assert winner["sample_size"] == 5

    async def test_confidence_rises_with_evidence(self, client, org):
        good = await _register(
            client, org["headers"], "good", "handles code review", ["code_review"]
        )
        await _register(client, org["headers"], "bad", "handles code review", ["code_review"])

        first = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        cold_confidence = first.json()["confidence"]

        for _ in range(10):
            await _record(client, org["headers"], good, CODE_TASK, ExecutionStatus.SUCCESS)

        warm = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        assert warm.json()["confidence"] > cold_confidence

    async def test_explicit_quality_feedback_outranks_bare_success(self, client, org):
        praised = await _register(
            client, org["headers"], "praised", "handles code review", ["code_review"]
        )
        panned = await _register(
            client, org["headers"], "panned", "handles code review", ["code_review"]
        )

        # Both "succeed"; only the feedback distinguishes them.
        for _ in range(5):
            await _record(
                client, org["headers"], praised, CODE_TASK, ExecutionStatus.SUCCESS, quality=0.95
            )
            await _record(
                client, org["headers"], panned, CODE_TASK, ExecutionStatus.SUCCESS, quality=0.10
            )

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        assert resp.json()["selected_agent"]["id"] == praised

    async def test_evidence_is_scoped_to_similar_tasks(self, client, org):
        # An agent that is great at prose should not win a code task on the
        # strength of its prose history.
        coder = await _register(client, org["headers"], "coder", "handles work", ["general"])
        writer = await _register(client, org["headers"], "writer", "handles work", ["general"])

        for _ in range(8):
            await _record(client, org["headers"], writer, PROSE_TASK, ExecutionStatus.SUCCESS)
        for _ in range(3):
            await _record(client, org["headers"], coder, CODE_TASK, ExecutionStatus.SUCCESS)

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        body = resp.json()
        assert body["selected_agent"]["id"] == coder
        writer_entry = next(c for c in body["reason"]["considered"] if c["agent_id"] == writer)
        # The prose history is too dissimilar to count toward a code task.
        assert writer_entry["sample_size"] == 0

    async def test_execution_history_is_tenant_scoped(self, client, org):
        other = await client.post(
            "/v1/organizations", json={"name": "Other", "email": "other-routing@example.com"}
        )
        other_headers = {"Authorization": f"Bearer {other.json()['api_key']}"}

        mine = await _register(
            client, org["headers"], "shared-name", "handles code review", ["code_review"]
        )
        theirs = await _register(
            client, other_headers, "shared-name", "handles code review", ["code_review"]
        )

        for _ in range(5):
            await _record(client, org["headers"], mine, CODE_TASK, ExecutionStatus.SUCCESS)

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=other_headers
        )
        entry = next(c for c in resp.json()["reason"]["considered"] if c["agent_id"] == theirs)
        # Our history must be invisible to them: their posterior is untouched,
        # still sitting on the uniform prior.
        assert entry["sample_size"] == 0
        assert entry["evidence_mean"] == 0.5


class TestCostAwareness:
    async def test_cost_breaks_ties_between_equal_agents(self, client, org):
        cheap = await _register(
            client, org["headers"], "cheap", "handles code review", ["code_review"], cost=0.001
        )
        pricey = await _register(
            client, org["headers"], "pricey", "handles code review", ["code_review"], cost=0.100
        )

        for _ in range(5):
            await _record(client, org["headers"], cheap, CODE_TASK, ExecutionStatus.SUCCESS)
            await _record(client, org["headers"], pricey, CODE_TASK, ExecutionStatus.SUCCESS)

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        assert resp.json()["selected_agent"]["id"] == cheap

    async def test_quality_still_beats_cost(self, client, org):
        # Cost is a tie-breaker, not an override: a cheap agent that fails
        # must not win over an expensive one that works.
        cheap = await _register(
            client, org["headers"], "cheap", "handles code review", ["code_review"], cost=0.001
        )
        pricey = await _register(
            client, org["headers"], "pricey", "handles code review", ["code_review"], cost=0.100
        )

        for _ in range(6):
            await _record(client, org["headers"], cheap, CODE_TASK, ExecutionStatus.FAILURE)
            await _record(client, org["headers"], pricey, CODE_TASK, ExecutionStatus.SUCCESS)

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        assert resp.json()["selected_agent"]["id"] == pricey


class TestExploration:
    """
    Regression guard for the bug this router was originally shipped with:
    pure argmax on the observed mean, which made a better agent undiscoverable
    once any incumbent had history.
    """

    async def test_an_unproven_agent_is_tried_over_a_mediocre_incumbent(self, client, org):
        incumbent = await _register(
            client, org["headers"], "incumbent", "handles code review", ["code_review"]
        )
        challenger = await _register(
            client, org["headers"], "challenger", "handles code review", ["code_review"]
        )

        # Give the incumbent a long, mediocre track record and the challenger none.
        for i in range(20):
            await _record(
                client,
                org["headers"],
                incumbent,
                CODE_TASK,
                ExecutionStatus.SUCCESS if i % 2 else ExecutionStatus.FAILURE,
            )

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        body = resp.json()
        assert body["selected_agent"]["id"] == challenger
        assert body["reason"]["exploring"] is True

    async def test_a_proven_agent_is_not_displaced_by_an_unproven_one(self, client, org):
        proven = await _register(
            client, org["headers"], "proven", "handles code review", ["code_review"]
        )
        for _ in range(25):
            await _record(client, org["headers"], proven, CODE_TASK, ExecutionStatus.SUCCESS)

        # A newcomer arrives after the incumbent is well established.
        await _register(client, org["headers"], "newcomer", "handles code review", ["code_review"])

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        body = resp.json()
        assert body["selected_agent"]["id"] == proven
        assert body["reason"]["exploring"] is False

    async def test_exploration_reports_both_the_bound_and_the_mean(self, client, org):
        agent_id = await _register(
            client, org["headers"], "solo", "handles code review", ["code_review"]
        )
        for _ in range(6):
            await _record(client, org["headers"], agent_id, CODE_TASK, ExecutionStatus.SUCCESS)

        resp = await client.post(
            "/v1/route", json={"task": SIMILAR_CODE_TASK}, headers=org["headers"]
        )
        entry = resp.json()["reason"]["considered"][0]
        # The audit trail must expose what was optimism and what was observed.
        assert entry["evidence"] >= entry["evidence_mean"]
        assert entry["evidence_sd"] > 0
        assert entry["evidence_mean"] > 0.5
