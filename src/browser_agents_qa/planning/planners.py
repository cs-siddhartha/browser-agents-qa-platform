from typing import Protocol

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from browser_agents_qa.runs.models import ExecutionLayer, ExecutionPlan, PlanStep
from browser_agents_qa.test_cases.models import AgenticTestCase


class Planner(Protocol):
    """Define how natural-language test intent becomes a structured plan."""

    async def create_plan(self, test_case: AgenticTestCase) -> ExecutionPlan:
        """Create a bounded execution plan for one agentic test case."""

        ...


class DeterministicPlanner:
    """Create a local baseline plan without requiring an LLM provider."""

    async def create_plan(self, test_case: AgenticTestCase) -> ExecutionPlan:
        """Convert preconditions, objective, and assertions into ordered steps."""

        steps = [
            PlanStep(
                instruction=f"Verify precondition: {precondition}",
                expected_outcome="The precondition is satisfied before browser execution.",
                preferred_layer=ExecutionLayer.EXTRACTION,
            )
            for precondition in test_case.preconditions
        ]
        steps.append(
            PlanStep(
                instruction=test_case.objective,
                expected_outcome="The requested browser workflow is completed.",
                preferred_layer=ExecutionLayer.PLAYWRIGHT,
            )
        )
        steps.extend(
            PlanStep(
                instruction=f"Verify assertion: {assertion}",
                expected_outcome=assertion,
                preferred_layer=ExecutionLayer.ASSERTION,
            )
            for assertion in test_case.assertions
        )

        return ExecutionPlan(
            summary=f"Execute agentic test case: {test_case.name}",
            steps=steps[: test_case.constraints.max_steps],
        )


class LangChainPlanner:
    """Use a LangChain chat model to produce the platform planning schema."""

    def __init__(self, model: BaseChatModel) -> None:
        """Configure the planner with a provider-specific LangChain chat model."""

        self._planner = (
            ChatPromptTemplate.from_messages(
                [
                    (
                        "system",
                        "You plan browser QA workflows. Return a concise, bounded plan. "
                        "Prefer extraction, then Playwright, accessibility, and vision. "
                        "Use assertion steps for expected outcomes.",
                    ),
                    (
                        "human",
                        "Name: {name}\n"
                        "Objective: {objective}\n"
                        "Preconditions: {preconditions}\n"
                        "Assertions: {assertions}\n"
                        "Maximum steps: {max_steps}\n"
                        "Allowed domains: {allowed_domains}",
                    ),
                ]
            )
            | model.with_structured_output(ExecutionPlan)
        )

    async def create_plan(self, test_case: AgenticTestCase) -> ExecutionPlan:
        """Generate a validated execution plan from natural-language intent."""

        result = await self._planner.ainvoke(
            {
                "name": test_case.name,
                "objective": test_case.objective,
                "preconditions": test_case.preconditions,
                "assertions": test_case.assertions,
                "max_steps": test_case.constraints.max_steps,
                "allowed_domains": test_case.constraints.allowed_domains,
            }
        )
        return ExecutionPlan.model_validate(result)
