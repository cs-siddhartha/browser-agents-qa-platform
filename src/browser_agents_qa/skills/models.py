from pydantic import BaseModel, ConfigDict, Field

from browser_agents_qa.runs.models import ExecutionLayer


class SkillValueDefinition(BaseModel):
    """Define a skill input or output value for planners and handlers."""

    model_config = ConfigDict(extra="forbid")

    type: str = Field(min_length=1, max_length=100)
    description: str = Field(min_length=1, max_length=1_000)
    required: bool = True


class SkillCost(BaseModel):
    """Describe the expected model cost of invoking a skill once."""

    model_config = ConfigDict(extra="forbid")

    llm_calls: int = Field(default=0, ge=0)
    vision_calls: int = Field(default=0, ge=0)


class SkillDefinition(BaseModel):
    """Represent one validated capability available to the agent planner."""

    model_config = ConfigDict(extra="forbid")

    name: str = Field(pattern=r"^[a-z][a-z0-9_]*$", max_length=100)
    version: int = Field(ge=1)
    description: str = Field(min_length=1, max_length=1_000)
    prompt: str = Field(min_length=1, max_length=500)
    handler: str = Field(pattern=r"^[a-z][a-z0-9_.]*$", max_length=200)
    layer: ExecutionLayer
    inputs: dict[str, SkillValueDefinition] = Field(default_factory=dict)
    outputs: dict[str, SkillValueDefinition] = Field(default_factory=dict)
    preconditions: list[str] = Field(default_factory=list, max_length=50)
    fallbacks: list[str] = Field(default_factory=list, max_length=20)
    retries: int = Field(default=0, ge=0, le=10)
    cost: SkillCost = Field(default_factory=SkillCost)
    instructions: str = Field(min_length=1)
