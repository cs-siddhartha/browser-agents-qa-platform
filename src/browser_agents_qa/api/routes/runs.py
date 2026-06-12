from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from browser_agents_qa.api.dependencies import (
    get_run_repository,
    get_test_case_repository,
)
from browser_agents_qa.runs.models import AgenticRun, AgenticRunCreate
from browser_agents_qa.runs.repository import RunRepository
from browser_agents_qa.test_cases.repository import TestCaseRepository

router = APIRouter(prefix="/runs")
RunRepositoryDependency = Annotated[RunRepository, Depends(get_run_repository)]
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
