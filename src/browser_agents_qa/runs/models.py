from datetime import datetime
from enum import StrEnum
from uuid import UUID

from pydantic import BaseModel, ConfigDict


class RunStatus(StrEnum):
    """Identify the current lifecycle state of an agentic test run."""

    PENDING = "pending"
    PLANNING = "planning"
    RUNNING = "running"
    PASSED = "passed"
    FAILED = "failed"
    BLOCKED = "blocked"
    CANCELLED = "cancelled"


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
    started_at: datetime | None = None
    completed_at: datetime | None = None
