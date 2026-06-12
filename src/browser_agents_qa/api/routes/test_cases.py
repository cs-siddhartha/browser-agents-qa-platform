from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, HTTPException, status

from browser_agents_qa.api.dependencies import get_test_case_repository
from browser_agents_qa.test_cases.models import AgenticTestCase, AgenticTestCaseCreate
from browser_agents_qa.test_cases.repository import TestCaseRepository

router = APIRouter(prefix="/test-cases")
RepositoryDependency = Annotated[TestCaseRepository, Depends(get_test_case_repository)]


@router.post("", response_model=AgenticTestCase, status_code=status.HTTP_201_CREATED)
async def create_test_case(
    test_case: AgenticTestCaseCreate,
    repository: RepositoryDependency,
) -> AgenticTestCase:
    """Create and return an agentic test case."""

    return await repository.create(test_case)


@router.get("/{test_case_id}", response_model=AgenticTestCase)
async def get_test_case(
    test_case_id: UUID,
    repository: RepositoryDependency,
) -> AgenticTestCase:
    """Return one agentic test case by its identifier."""

    test_case = await repository.get(test_case_id)
    if test_case is None:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Agentic test case not found.",
        )

    return test_case
