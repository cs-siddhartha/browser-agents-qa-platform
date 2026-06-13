from asyncio import Lock
from datetime import UTC, datetime
from typing import Protocol
from uuid import UUID, uuid4

from browser_agents_qa.runs.models import AgenticRun, RunStatus


class RunRepository(Protocol):
    """Specify persistence operations required by execution-run workflows."""

    async def create(self, test_case_id: UUID) -> AgenticRun:
        """Create a pending run for one test case."""

        ...

    async def get(self, run_id: UUID) -> AgenticRun | None:
        """Return a run, or None when it does not exist."""

        ...

    async def update(self, run: AgenticRun) -> AgenticRun:
        """Persist and return the current state of an existing run."""

        ...


class InMemoryRunRepository:
    """Store agentic test runs in process memory."""

    def __init__(self) -> None:
        """Create an empty in-memory run repository."""

        self._runs: dict[UUID, AgenticRun] = {}
        self._lock = Lock()

    async def create(self, test_case_id: UUID) -> AgenticRun:
        """Create and store a pending run for one test case."""

        run = AgenticRun(
            id=uuid4(),
            test_case_id=test_case_id,
            status=RunStatus.PENDING,
            created_at=datetime.now(UTC),
        )

        async with self._lock:
            self._runs[run.id] = run.model_copy(deep=True)

        return run

    async def get(self, run_id: UUID) -> AgenticRun | None:
        """Return a run, or None when it does not exist."""

        async with self._lock:
            run = self._runs.get(run_id)

        return run.model_copy(deep=True) if run is not None else None

    async def update(self, run: AgenticRun) -> AgenticRun:
        """Persist and return the current state of an existing run."""

        async with self._lock:
            if run.id not in self._runs:
                raise KeyError(run.id)
            self._runs[run.id] = run.model_copy(deep=True)

        return run
