from fastapi import FastAPI

from backend.app.api.router import router as api_router


app = FastAPI(
    title="MCPilot",
    description="Agentic Analytics Platform powered by MCP",
    version="0.1.0",
)


app.include_router(api_router)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "mcpilot",
    }