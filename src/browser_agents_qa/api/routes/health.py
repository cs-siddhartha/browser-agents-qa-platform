from typing import Literal

from fastapi import APIRouter
from pydantic import BaseModel

router = APIRouter()


# Publish a typed response model so infrastructure clients receive a small,
# versioned readiness contract instead of depending on an unstructured payload.
class HealthResponse(BaseModel):
    """Defines a stable readiness payload for operators and deployment probes."""

    status: Literal["ok"]


# Keep health checks dependency-free so infrastructure can verify that the API
# process is responsive even before external platform services are configured.
@router.get("/health", response_model=HealthResponse)
def health() -> HealthResponse:
    """Report whether the API process can accept requests."""

    return HealthResponse(status="ok")
