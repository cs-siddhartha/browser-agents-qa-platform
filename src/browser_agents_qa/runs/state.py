from typing import TypedDict
from uuid import UUID

from browser_agents_qa.runs.models import ExecutionPlan, RunStatus
from browser_agents_qa.test_cases.models import AgenticTestCase


class AgentExecutionState(TypedDict):
    """Hold the complete state of one agentic test execution graph."""

    run_id: UUID
    test_case: AgenticTestCase
    status: RunStatus
    current_node: str | None
    plan: ExecutionPlan | None
    observations: list[str]
    evidence: list[dict[str, object]]
    errors: list[str]
    step_count: int
    estimated_cost_usd: float
