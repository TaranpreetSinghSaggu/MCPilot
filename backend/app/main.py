from fastapi import FastAPI


app = FastAPI(
    title="MCPilot",
    description="Agentic Analytics Platform powered by MCP",
    version="0.1.0",
)


@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "service": "mcpilot",
    }