from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from browser_agents_qa.api.dependencies import (
    get_planning_workflow,
    get_run_repository,
    get_test_case_repository,
)
from browser_agents_qa.planning.workflow import PlanningWorkflow
from browser_agents_qa.runs.models import AgenticRun, AgenticRunCreate, RunStatus
from browser_agents_qa.runs.repository import RunRepository
from browser_agents_qa.test_cases.repository import TestCaseRepository

router = APIRouter(prefix="/runs")
RunRepositoryDependency = Annotated[RunRepository, Depends(get_run_repository)]
PlanningWorkflowDependency = Annotated[
    PlanningWorkflow,
    Depends(get_planning_workflow),
]
TestCaseRepositoryDependency = Annotated[
    TestCaseRepository,
    Depends(get_test_case_repository),
]


@router.post("", response_model=AgenticRun, status_code=status.HTTP_201_CREATED)
async def create_run(
    run_request: AgenticRunCreate,
    run_repository: RunRepositoryDependency,
    test_case_repository: TestCaseRepositoryDependency,
) -> AgenticRun:
    """Create a pending run for an existing agentic test case."""

    test_case = await test_case_repository.get(run_request.test_case_id)
    if test_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agentic test case not found.",
        )

    return await run_repository.create(run_request.test_case_id)


# Starts only the planning DAG, leaving browser execution for the next stage.
@router.post("/{run_id}/plan", response_model=AgenticRun)
async def plan_run(
    run_id: UUID,
    run_repository: RunRepositoryDependency,
    test_case_repository: TestCaseRepositoryDependency,
    planning_workflow: PlanningWorkflowDependency,
) -> AgenticRun:
    """Generate and persist the execution plan for one pending run."""

    run = await run_repository.get(run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agentic test run not found.",
        )
    if run.status is not RunStatus.PENDING:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Only pending runs can be planned.",
        )

    test_case = await test_case_repository.get(run.test_case_id)
    if test_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agentic test case not found.",
        )

    planned_run = await planning_workflow.execute(run, test_case)
    return await run_repository.update(planned_run)


@router.get("/{run_id}", response_model=AgenticRun)
async def get_run(
    run_id: UUID,
    run_repository: RunRepositoryDependency,
) -> AgenticRun:
    """Return one agentic test run by its identifier."""

    run = await run_repository.get(run_id)
    if run is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agentic test run not found.",
        )

    return run
