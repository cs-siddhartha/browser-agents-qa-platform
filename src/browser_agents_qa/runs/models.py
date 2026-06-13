from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class RunStatus(StrEnum):
    """Identify the current lifecycle state of an agentic test run."""

    PENDING = "pending"
    PLANNING = "planning"
    PLANNED = "planned"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


class ExecutionLayer(StrEnum):
    """Identify the preferred interaction layer for a planned step."""

    EXTRACTION = "extraction"
    PLAYWRIGHT = "playwright"
    ACCESSIBILITY = "accessibility"
    VISION = "vision"
    ASSERTION = "assertion"


class PlanStep(BaseModel):
    """Describe one bounded action in an agent-generated execution plan."""

    model_config = ConfigDict(extra="forbid")

    instruction: str = Field(min_length=1, max_length=1_000)
    expected_outcome: str = Field(min_length=1, max_length=1_000)
    preferred_layer: ExecutionLayer


class ExecutionPlan(BaseModel):
    """Represent the structured plan consumed by execution graph nodes."""

    model_config = ConfigDict(extra="forbid")

    summary: str = Field(min_length=1, max_length=1_000)
    steps: list[PlanStep] = Field(min_length=1, max_length=200)


class AgenticRunCreate(BaseModel):
    """Request execution of one stored agentic test case."""

    model_config = ConfigDict(extra="forbid")

    test_case_id: UUID


class AgenticRun(BaseModel):
    """Represent an agentic test execution tracked by the platform."""

    model_config = ConfigDict(extra="forbid")

    id: UUID
    test_case_id: UUID
    status: RunStatus
    created_at: datetime
    planned_at: datetime | None = None
    started_at: datetime | None = None
    completed_at: datetime | None = None
    plan: ExecutionPlan | None = None
    error: str | None = None
