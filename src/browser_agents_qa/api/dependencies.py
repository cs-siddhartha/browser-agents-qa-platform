from browser_agents_qa.test_cases.repository import (
    InMemoryTestCaseRepository,
    TestCaseRepository,
)

test_case_repository = InMemoryTestCaseRepository()


def get_test_case_repository() -> TestCaseRepository:
    """Return the configured test-case repository."""

    return test_case_repository
