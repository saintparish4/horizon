"""Unit tests for the routing math. No database required."""

import math
from datetime import UTC, datetime, timedelta

import pytest

from horizon.models import Execution, ExecutionStatus
from horizon.services import router


def _execution(**kwargs) -> Execution:
    defaults = dict(task="t", status=ExecutionStatus.SUCCESS, quality_score=None)
    return Execution(**{**defaults, **kwargs})


class TestOutcomeValue:
    def test_success_without_feedback_scores_one(self):
        assert router._outcome_value(_execution(status=ExecutionStatus.SUCCESS)) == 1.0

    @pytest.mark.parametrize("status", [ExecutionStatus.FAILURE, ExecutionStatus.TIMEOUT])
    def test_non_success_without_feedback_scores_zero(self, status):
        assert router._outcome_value(_execution(status=status)) == 0.0

    def test_explicit_quality_overrides_status(self):
        # A "successful" call can still be a bad answer; feedback wins.
        e = _execution(status=ExecutionStatus.SUCCESS, quality_score=0.2)
        assert router._outcome_value(e) == 0.2

    def test_quality_is_clamped(self):
        assert router._outcome_value(_execution(quality_score=1.7)) == 1.0
        assert router._outcome_value(_execution(quality_score=-0.5)) == 0.0


class TestRecencyWeight:
    def test_now_is_full_weight(self):
        now = datetime.now(UTC)
        assert router._recency_weight(now, now) == pytest.approx(1.0)

    def test_one_halflife_halves_the_weight(self):
        now = datetime.now(UTC)
        old = now - timedelta(days=router.EVIDENCE_HALFLIFE_DAYS)
        assert router._recency_weight(old, now) == pytest.approx(0.5)

    def test_weight_decays_monotonically(self):
        now = datetime.now(UTC)
        weights = [router._recency_weight(now - timedelta(days=d), now) for d in (0, 10, 30, 90)]
        assert weights == sorted(weights, reverse=True)

    def test_future_timestamps_do_not_exceed_full_weight(self):
        now = datetime.now(UTC)
        future = now + timedelta(days=5)
        assert router._recency_weight(future, now) == pytest.approx(1.0)


class TestCosine:
    def test_identical_vectors(self):
        assert router._cosine([1.0, 0.0], [1.0, 0.0]) == pytest.approx(1.0)

    def test_orthogonal_vectors(self):
        assert router._cosine([1.0, 0.0], [0.0, 1.0]) == pytest.approx(0.0)

    def test_opposite_vectors(self):
        assert router._cosine([1.0, 0.0], [-1.0, 0.0]) == pytest.approx(-1.0)

    def test_magnitude_invariant(self):
        assert router._cosine([3.0, 4.0], [6.0, 8.0]) == pytest.approx(1.0)

    def test_zero_vector_is_safe(self):
        assert router._cosine([0.0, 0.0], [1.0, 1.0]) == 0.0

    def test_mismatched_dimensions_raise(self):
        with pytest.raises(ValueError):
            router._cosine([1.0, 0.0], [1.0, 0.0, 0.0])


class TestCostScoring:
    def _candidates(self, *costs):
        from horizon.models import Agent

        return {
            i: router.Candidate(agent=Agent(name=f"a{i}", endpoint="x", cost_per_call_usd=c))
            for i, c in enumerate(costs)
        }

    def test_penalty_is_normalized_to_the_most_expensive(self):
        cands = self._candidates(0.0, 0.5, 1.0)
        router._score_cost(cands)
        assert [c.cost_penalty for c in cands.values()] == [0.0, 0.5, 1.0]

    def test_all_free_agents_incur_no_penalty(self):
        cands = self._candidates(0.0, 0.0)
        router._score_cost(cands)
        assert all(c.cost_penalty == 0.0 for c in cands.values())


class TestWeights:
    def test_weights_are_a_convex_combination(self):
        # Evidence and capability must sum to 1 so `score` stays comparable to
        # the 0-1 confidence scale; cost is a separate penalty.
        assert router.W_EVIDENCE + router.W_CAPABILITY + router.W_COST == pytest.approx(1.0)

    def test_evidence_outweighs_capability(self):
        # What actually worked beats what an agent claims it can do.
        assert router.W_EVIDENCE > router.W_CAPABILITY

    def test_confidence_saturation_is_reachable(self):
        # Support should approach 1.0 within a realistic number of executions.
        support = 1 - math.exp(-20 / router.CONFIDENCE_SATURATION)
        assert support > 0.95


class TestPosterior:
    """The Beta posterior is what makes exploration possible — pin its shape."""

    def _cand(self, wins: float, losses: float) -> router.Candidate:
        from horizon.models import Agent

        c = router.Candidate(agent=Agent(name="a", endpoint="e"))
        c.wins, c.losses = wins, losses
        return c

    def test_untried_agent_sits_on_the_uniform_prior(self):
        c = self._cand(0, 0)
        assert c.evidence_mean == pytest.approx(0.5)
        assert c.support == 0.0

    def test_untried_agent_outranks_a_known_mediocre_one(self):
        # The exact failure this design exists to prevent: without optimism the
        # first adequate agent locks in and better ones are never discovered.
        untried = self._cand(0, 0)
        mediocre = self._cand(10.4, 9.6)  # ~52% over 20 observations
        assert mediocre.evidence_mean < 0.55
        assert untried.evidence > mediocre.evidence

    def test_untried_agent_does_not_outrank_a_known_good_one(self):
        # Exploration must stop on its own once evidence is strong.
        untried = self._cand(0, 0)
        proven = self._cand(27.9, 2.1)  # ~93% over 30 observations
        assert untried.evidence < proven.evidence

    def test_uncertainty_shrinks_as_evidence_accumulates(self):
        sds = [self._cand(0.9 * n, 0.1 * n).evidence_sd for n in (1, 5, 20, 100)]
        assert sds == sorted(sds, reverse=True)

    def test_bound_converges_on_the_mean(self):
        c = self._cand(90, 10)
        assert c.evidence - c.evidence_mean < 0.05

    def test_bound_never_exceeds_one(self):
        assert self._cand(1000, 0).evidence <= 1.0

    def test_partial_credit_splits_across_the_posterior(self):
        # quality_score=0.7 should read as 70% of a win, not a coin flip.
        c = self._cand(0.7, 0.3)
        assert c.evidence_mean == pytest.approx(1.7 / 3.0)

    def test_failures_pull_the_mean_down(self):
        assert self._cand(2, 8).evidence_mean < 0.5
        assert self._cand(8, 2).evidence_mean > 0.5
