"""
Synthetic workload for the routing benchmark.

The world is deliberately unkind to naive routing: agents over-claim in their
declared capabilities, exactly as real agent registries do. An agent that says
it handles four task families but is only good at one will win capability-based
routing and lose evidence-based routing. That gap is what the benchmark
measures.
"""

import random
from dataclasses import dataclass, field

TaskFamily = str


@dataclass(frozen=True)
class Family:
    """
    One kind of work, and the ways a user might ask for it.

    `phrasings[0]` is canonical: it is what the agents' self-descriptions are
    built from, and the only phrasing used in template mode. The rest are
    paraphrases that mean the same thing in different words, which is the
    harder test — under paraphrasing, lexical overlap stops being a usable
    proxy for "same kind of task" and only a real semantic model can tell.
    """

    name: TaskFamily
    phrasings: tuple[str, ...]
    slot_a: tuple[str, ...]
    slot_b: tuple[str, ...]
    slot_c: tuple[str, ...]

    @property
    def template(self) -> str:
        """The canonical phrasing, used for agent capability text."""
        return self.phrasings[0]

    def render(self, rng: random.Random, *, paraphrase: bool = False) -> str:
        phrasing = rng.choice(self.phrasings) if paraphrase else self.template
        return phrasing.format(
            a=rng.choice(self.slot_a), b=rng.choice(self.slot_b), c=rng.choice(self.slot_c)
        )


FAMILIES: tuple[Family, ...] = (
    Family(
        "code_review",
        (
            "review this {a} pull request for {b} defects in the {c} module",
            "audit the {c} module of this {a} changeset for {b} problems",
            "go over the diff touching {c} and flag anything {b} before we merge this {a} change",
            "does this {a} patch to {c} introduce {b} issues anywhere",
        ),
        ("python", "go", "rust"),
        ("security", "performance", "concurrency"),
        ("auth", "billing", "search"),
    ),
    Family(
        "sql_generation",
        (
            "write a sql query joining the {a} table with the {b} table filtered by {c}",
            "i need the {a} records matched up against {b}, narrowed down by {c}",
            "pull every row where {a} lines up with {b}, restricted to a given {c}",
            "give me a select statement bringing {a} and {b} together, limited by {c}",
        ),
        ("orders", "users", "events"),
        ("invoices", "sessions", "accounts"),
        ("region", "status", "date"),
    ),
    Family(
        "summarization",
        (
            "summarize this {a} document into a short {b} covering the {c} points",
            "condense the {a} writeup down to a {b} that hits the {c} items",
            "i need a {b} of this {a} material, focused on whatever is {c}",
            "shorten this {a} text into a {b} and keep only the {c} parts",
        ),
        ("earnings", "research", "incident"),
        ("brief", "abstract", "digest"),
        ("key", "risk", "action"),
    ),
    Family(
        "translation",
        (
            "translate this {a} passage from english into {b} preserving {c} tone",
            "render this {a} copy in {b}, keeping the register {c}",
            "put this english {a} text into {b} without losing the {c} feel",
            "i need a {b} version of this {a} content, tone stays {c}",
        ),
        ("marketing", "legal", "technical"),
        ("japanese", "german", "spanish"),
        ("formal", "casual", "neutral"),
    ),
)

FAMILY_BY_NAME = {f.name: f for f in FAMILIES}


@dataclass(frozen=True)
class AgentSpec:
    name: str
    # Ground truth the router cannot see: P(success) per family.
    competence: dict[TaskFamily, float]
    # What the agent claims. Deliberately broader than the truth.
    declared: tuple[TaskFamily, ...]
    cost_per_call_usd: float
    description: str = field(default="")

    def capability_text(self) -> str:
        """Self-description, phrased in the vocabulary of what it claims."""
        claims = " ".join(
            FAMILY_BY_NAME[f].template.format(a="", b="", c="") for f in self.declared
        )
        return f"{self.name} {claims}"


AGENTS: tuple[AgentSpec, ...] = (
    AgentSpec(
        "alpha",
        {"code_review": 0.93, "sql_generation": 0.30, "summarization": 0.22, "translation": 0.18},
        declared=("code_review", "sql_generation"),  # over-claims sql
        cost_per_call_usd=0.012,
    ),
    AgentSpec(
        "beta",
        {"code_review": 0.28, "sql_generation": 0.91, "summarization": 0.25, "translation": 0.20},
        declared=("sql_generation",),
        cost_per_call_usd=0.009,
    ),
    AgentSpec(
        "gamma",
        {"code_review": 0.20, "sql_generation": 0.24, "summarization": 0.89, "translation": 0.35},
        declared=("summarization", "translation"),  # over-claims translation
        cost_per_call_usd=0.011,
    ),
    AgentSpec(
        "delta",
        {"code_review": 0.19, "sql_generation": 0.21, "summarization": 0.33, "translation": 0.92},
        declared=("translation",),
        cost_per_call_usd=0.010,
    ),
    AgentSpec(
        "omni",
        # The generalist: never bad, never good. Claims everything.
        {"code_review": 0.52, "sql_generation": 0.55, "summarization": 0.53, "translation": 0.51},
        declared=("code_review", "sql_generation", "summarization", "translation"),
        cost_per_call_usd=0.006,
    ),
)

AGENT_BY_NAME = {a.name: a for a in AGENTS}


def best_possible(family: TaskFamily) -> float:
    """Oracle ceiling: the competence of the genuinely best agent."""
    return max(a.competence[family] for a in AGENTS)


def sample_outcome(agent: AgentSpec, family: TaskFamily, rng: random.Random) -> bool:
    return rng.random() < agent.competence[family]
