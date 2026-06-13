from typing import Protocol

from langchain_core.language_models import BaseChatModel
from langchain_core.prompts import ChatPromptTemplate

from browser_agents_qa.runs.models import ExecutionPlan, PlanStep
from browser_agents_qa.skills.catalogue import SkillCatalogue
from browser_agents_qa.test_cases.models import AgenticTestCase


class Planner(Protocol):
    """Define how natural-language test intent becomes a structured plan."""

    async def create_plan(self, test_case: AgenticTestCase) -> ExecutionPlan:
        """Create a bounded execution plan for one agentic test case."""

        ...


class DeterministicPlanner:
    """Create a local baseline plan without requiring an LLM provider."""

    def __init__(self, catalogue: SkillCatalogue) -> None:
        """Configure deterministic planning against validated catalogue skills."""

        self._catalogue = catalogue

    async def create_plan(self, test_case: AgenticTestCase) -> ExecutionPlan:
        """Convert preconditions, objective, and assertions into ordered steps."""

        gateway_skill = self._catalogue.get("verify_gateway_access")
        extraction_skill = self._catalogue.get("extract_page_content")
        browser_skill = self._catalogue.get("perform_browser_action")
        assertion_skill = self._catalogue.get("assert_outcome")

        steps = [
            PlanStep(
                id="verify_gateway_access",
                skill=gateway_skill.name,
                instruction="Verify gateway access for the allowed test domains.",
                arguments={"domains": test_case.constraints.allowed_domains},
                expected_outcome="The target application is accessible for execution.",
                preferred_layer=gateway_skill.layer,
            )
        ]
        steps.extend(
            PlanStep(
                id=f"verify_precondition_{index}",
                skill=extraction_skill.name,
                instruction=f"Verify precondition: {precondition}",
                arguments={"objective": precondition},
                expected_outcome="The precondition is satisfied before browser execution.",
                preferred_layer=extraction_skill.layer,
                depends_on=["verify_gateway_access"],
            )
            for index, precondition in enumerate(test_case.preconditions, start=1)
        )
        browser_dependencies = [step.id for step in steps]
        steps.append(
            PlanStep(
                id="perform_objective",
                skill=browser_skill.name,
                instruction=test_case.objective,
                arguments={
                    "instruction": test_case.objective,
                    "expected_outcome": "The requested browser workflow is completed.",
                },
                expected_outcome="The requested browser workflow is completed.",
                preferred_layer=browser_skill.layer,
                depends_on=browser_dependencies,
            )
        )
        steps.extend(
            PlanStep(
                id=f"assert_outcome_{index}",
                skill=assertion_skill.name,
                instruction=f"Verify assertion: {assertion}",
                arguments={"assertion": assertion},
                expected_outcome=assertion,
                preferred_layer=assertion_skill.layer,
                depends_on=["perform_objective"],
            )
            for index, assertion in enumerate(test_case.assertions, start=1)
        )

        return ExecutionPlan(
            summary=f"Execute agentic test case: {test_case.name}",
            steps=steps,
        )


class LangChainPlanner:
    """Use a LangChain chat model to produce the platform planning schema."""

    def __init__(self, model: BaseChatModel, catalogue: SkillCatalogue) -> None:
        """Configure the planner with a provider-specific LangChain chat model."""

        self._catalogue = catalogue
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
                        "Allowed domains: {allowed_domains}\n"
                        "Available skills:\n{skills}\n"
                        "Use only listed skill names and make dependencies explicit.",
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
                "skills": self._catalogue.planner_context(),
            }
        )
        plan = ExecutionPlan.model_validate(result)
        for step in plan.steps:
            skill = self._catalogue.get(step.skill)
            if step.preferred_layer is not skill.layer:
                raise ValueError(
                    f"Plan step '{step.id}' uses layer '{step.preferred_layer}' "
                    f"but skill '{step.skill}' requires '{skill.layer}'."
                )
        return plan
