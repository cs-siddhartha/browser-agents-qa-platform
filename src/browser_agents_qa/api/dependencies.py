from browser_agents_qa.runs.repository import InMemoryRunRepository, RunRepository
from browser_agents_qa.test_cases.repository import (
    InMemoryTestCaseRepository,
    TestCaseRepository,
)

run_repository = InMemoryRunRepository()
test_case_repository = InMemoryTestCaseRepository()


def get_run_repository() -> RunRepository:
    """Return the configured execution-run repository."""

    return run_repository


def get_test_case_repository() -> TestCaseRepository:
    """Return the configured test-case repository."""

    return test_case_repository
