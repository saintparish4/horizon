"""Request/response models for the agent registry and routing API."""

import uuid
from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field, model_validator

from horizon.models.agent import ExecutionStatus, Protocol


class AgentCreate(BaseModel):
    name: str = Field(min_length=1, max_length=128)
    endpoint: str = Field(min_length=1, max_length=1024)
    description: str = ""
    protocol: Protocol = Protocol.REST
    capabilities: list[str] = Field(default_factory=list)
    cost_per_call_usd: float = Field(default=0.0, ge=0.0)
    timeout_seconds: float = Field(default=30.0, gt=0.0)
    config: dict[str, Any] = Field(default_factory=dict)


class AgentOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    name: str
    description: str
    endpoint: str
    protocol: str
    capabilities: list[str]
    cost_per_call_usd: float
    enabled: bool
    created_at: datetime


class RouteRequest(BaseModel):
    task: str = Field(min_length=1)
    allowed_agent_ids: list[uuid.UUID] = Field(default_factory=list)
    required_capabilities: list[str] = Field(default_factory=list)
    min_similarity: float | None = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description=(
            "How alike a past task must be to count as evidence. Defaults to the "
            "server's EVIDENCE_MIN_SIMILARITY. Raise it for tightly-templated "
            "workloads; lower it for free-form ones, where nothing would qualify."
        ),
    )


class RouteResponse(BaseModel):
    decision_id: uuid.UUID = Field(
        description="Pass this back to POST /v1/executions to link the outcome to this decision."
    )
    selected_agent: AgentOut | None
    confidence: float
    reason: dict[str, Any]


class ExecutionCreate(BaseModel):
    """
    Reported by the caller after it runs an agent.

    Send `decision_id` whenever the agent came from `/v1/route`. The server then
    reads the task, its embedding and the routing reason from its own record, so
    the outcome is auditable, costs no second embedding call, and records whether
    the recommendation was followed. `task` is the fallback for executions that
    were never routed here.
    """

    agent_id: uuid.UUID
    decision_id: uuid.UUID | None = Field(
        default=None, description="The `decision_id` returned by POST /v1/route."
    )
    task: str | None = Field(
        default=None,
        min_length=1,
        description="Ignored when `decision_id` is set; the stored task is used instead.",
    )
    status: ExecutionStatus
    latency_ms: int = Field(default=0, ge=0)
    cost_usd: float = Field(default=0.0, ge=0.0)
    quality_score: float | None = Field(default=None, ge=0.0, le=1.0)
    routing_reason: dict[str, Any] = Field(
        default_factory=dict,
        description="Ignored when `decision_id` is set; the stored reason is used instead.",
    )
    error: str | None = None

    @model_validator(mode="after")
    def _needs_a_task_or_a_decision(self) -> "ExecutionCreate":
        if self.decision_id is None and not self.task:
            raise ValueError("Provide `decision_id`, or `task` if the call was not routed here.")
        return self


class ExecutionOut(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: uuid.UUID
    agent_id: uuid.UUID
    decision_id: uuid.UUID | None
    followed: bool | None = Field(
        description="Whether the caller ran the recommended agent. None if unlinked."
    )
    task: str
    status: str
    latency_ms: int
    cost_usd: float
    quality_score: float | None
    created_at: datetime
