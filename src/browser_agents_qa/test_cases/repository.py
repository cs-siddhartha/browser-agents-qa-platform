from asyncio import Lock
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from browser_agents_qa.test_cases.models import AgenticTestCase, AgenticTestCaseCreate

class TestCaseRepository(Protocol):
    """Specify the persistence operations required by test-case workflows."""

    async def create(self, test_case: AgenticTestCaseCreate) -> AgenticTestCase:
        """Store and return a new agentic test case."""

        ...

    async def get(self, test_case_id: UUID) -> AgenticTestCase | None:
        """Return a stored test case, or None when it does not exist."""

        ...


# temporary
class InMemoryTestCaseRepository:
    """Store agentic test cases in process memory."""


    def __init__(self) -> None:
        """Create an empty in-memory test-case repository."""

        self._test_cases: dict[UUID, AgenticTestCase] = {}
        self._lock = Lock()

    async def create(self, test_case: AgenticTestCaseCreate) -> AgenticTestCase:
        """Store and return a new agentic test case."""

        stored_test_case = AgenticTestCase(
            **test_case.model_dump(),
            id=uuid4(),
            created_at=datetime.now(UTC),
        )

        async with self._lock:
            self._test_cases[stored_test_case.id] = stored_test_case.model_copy(deep=True)

        return stored_test_case

    async def get(self, test_case_id: UUID) -> AgenticTestCase | None:
        """Return a stored test case, or None when it does not exist."""

        async with self._lock:
            test_case = self._test_cases.get(test_case_id)

        return test_case.model_copy(deep=True) if test_case is not None else None
