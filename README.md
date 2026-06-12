# Browser Agents QA

A project for an agent-first QA automation platform.

## Local development

Install the project:

```bash
UV_CACHE_DIR=.uv-cache uv sync
```

Run the API:

```bash
UV_CACHE_DIR=.uv-cache uv run uvicorn browser_agents_qa.main:app --reload
```

Run checks:

```bash
UV_CACHE_DIR=.uv-cache uv run ruff check .
```
