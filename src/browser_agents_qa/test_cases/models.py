from datetime import datetime
from typing import Annotated
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, StringConstraints

AllowedDomain = Annotated[
    str,
    StringConstraints(
        min_length=1,
        max_length=253,
        pattern=r"^(localhost|(?:\*\.)?(?:[A-Za-z0-9-]+\.)*[A-Za-z0-9-]+)$",
    ),
]


# Keep execution limits explicit in every agentic test case so the future agent
# runtime can enforce bounded browser steps, model spend, and navigation scope.
class AgenticTestConstraints(BaseModel):
    """Define the execution boundaries for an agentic test case."""

    model_config = ConfigDict(extra="forbid")

    max_steps: int = Field(default=25, ge=1, le=200)
    max_cost_usd: float = Field(default=0.20, ge=0, le=100)
    allowed_domains: list[AllowedDomain] = Field(min_length=1, max_length=100)
    require_approval_for_destructive_actions: bool = True


# for fields supplied by the user, such as name, objective, and assertions.
class AgenticTestCaseCreate(BaseModel):
    """Describe the intent and expected outcomes of a new agentic test case."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(min_length=1, max_length=200)
    objective: str = Field(min_length=1, max_length=5_000)
    preconditions: list[str] = Field(default_factory=list, max_length=100)
    constraints: AgenticTestConstraints
    assertions: list[str] = Field(min_length=1, max_length=100)


# Expose platform-managed metadata alongside the authored test definition so
# API consumers can address and audit a stored test case consistently.
class AgenticTestCase(AgenticTestCaseCreate):
    """Represent a stored agentic test case returned by the platform."""

    id: UUID
    created_at: datetime
