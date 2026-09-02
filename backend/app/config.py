import os

from dotenv import load_dotenv


load_dotenv()


LLM_PRIMARY = os.getenv("LLM_PRIMARY", "gemini")
APP_ENV = os.getenv("APP_ENV", "development").lower()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DATABASE_URL = os.getenv("DATABASE_URL")
MCP_SERVER_URL = os.getenv("MCP_SERVER_URL")

if not MCP_SERVER_URL:
    if APP_ENV == "production":
        raise RuntimeError(
            "MCP_SERVER_URL must be configured in production."
        )
    MCP_SERVER_URL = "http://localhost:8001/mcp"

MCP_HOST = os.getenv("MCP_HOST", "127.0.0.1")

try:
    MCP_PORT = int(os.getenv("MCP_PORT", "8001"))
except ValueError as exc:
    raise RuntimeError("MCP_PORT must be an integer") from exc

CORS_ORIGINS = os.getenv(
    "CORS_ORIGINS",
    "http://localhost:5173",
)


provider_keys = {
    "gemini": GEMINI_API_KEY,
    "openai": OPENAI_API_KEY,
    "groq": GROQ_API_KEY,
}

if LLM_PRIMARY not in provider_keys:
    supported_providers = ", ".join(provider_keys)
    raise RuntimeError(
        f"LLM_PRIMARY must be one of: {supported_providers}"
    )

if not provider_keys[LLM_PRIMARY]:
    raise RuntimeError(
        f"{LLM_PRIMARY.upper()} provider credentials are not configured."
    )




if not DATABASE_URL:
    raise RuntimeError("DATABASE_URL is not configured.")

GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_API_URL = os.getenv(
    "GITHUB_API_URL",
    "https://api.github.com",
)
