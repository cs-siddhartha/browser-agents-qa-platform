from fastapi import APIRouter

from browser_agents_qa.api.routes.test_cases import router as test_cases_router

api_router = APIRouter()
api_router.include_router(test_cases_router, tags=["test-cases"])
