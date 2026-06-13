from datetime import UTC, datetime

from langgraph.graph import END, START, StateGraph

from browser_agents_qa.planning.planners import Planner
from browser_agents_qa.runs.models import AgenticRun, RunStatus
from browser_agents_qa.runs.state import AgentExecutionState
from browser_agents_qa.test_cases.models import AgenticTestCase


class PlanningWorkflow:
    """Run the NLP planning stage as the first LangGraph execution workflow."""

    def __init__(self, planner: Planner) -> None:
        """Compile a reusable planning graph around the configured planner."""

        graph = StateGraph(AgentExecutionState)

        # Converts the test-case intent into graph state that later browser
        # execution nodes can consume without parsing unstructured model text.
        async def create_plan(state: AgentExecutionState) -> dict[str, object]:
            """Generate and attach a structured execution plan."""

            plan = await planner.create_plan(state["test_case"])
            return {
                "current_node": "planner",
                "plan": plan,
                "status": RunStatus.PLANNED,
            }

        graph.add_node("planner", create_plan)
        graph.add_edge(START, "planner")
        graph.add_edge("planner", END)
        self._graph = graph.compile()

    async def execute(
        self,
        run: AgenticRun,
        test_case: AgenticTestCase,
    ) -> AgenticRun:
        """Plan one pending run and return its updated lifecycle state."""

        planned_at = datetime.now(UTC)
        initial_state: AgentExecutionState = {
            "run_id": run.id,
            "test_case": test_case,
            "status": RunStatus.PLANNING,
            "current_node": None,
            "plan": None,
            "observations": [],
            "evidence": [],
            "errors": [],
            "step_count": 0,
            "estimated_cost_usd": 0,
        }

        try:
            result = await self._graph.ainvoke(initial_state)
            return run.model_copy(
                update={
                    "status": result["status"],
                    "planned_at": planned_at,
                    "plan": result["plan"],
                    "error": None,
                }
            )
        except Exception as error:
            return run.model_copy(
                update={
                    "status": RunStatus.FAILED,
                    "planned_at": planned_at,
                    "completed_at": datetime.now(UTC),
                    "error": str(error),
                }
            )
