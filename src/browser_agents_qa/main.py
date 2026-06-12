from fastapi import FastAPI

from browser_agents_qa.api.router import api_router
from browser_agents_qa.config import get_settings


# Build the application in one place so tests and future deployment entrypoints
# create the API with the same routes, metadata, and configuration.
def create_app() -> FastAPI:
    """Create and configure the Browser Agents QA HTTP application."""

    settings = get_settings()
    application = FastAPI(
        title=settings.app_name,
        version="0.1.0",
    )
    application.include_router(api_router, prefix=settings.api_prefix)
    return application


app = create_app()
