# MCPilot

MCPilot is an AI engineering portfolio project that answers DevOps questions using live application data, MCP tools, and configurable LLM providers.

## Architecture

- FastAPI REST API: `backend.app.main:app`
- PostgreSQL with SQLAlchemy and Alembic
- Streamable HTTP MCP server at `/mcp` for production
- `stdio_server.py` as the local/development MCP entry point
- Vue 3, TypeScript, Vite, and Tailwind frontend
- Gemini, Groq, and OpenAI providers with ordered fallback
- GitHub read operations exposed through MCP tools

## Requirements

- Python 3.10
- Node.js and npm
- PostgreSQL, or Docker Desktop for local PostgreSQL

## Backend setup

From the repository root:

```text
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and set the required values. The selected `LLM_PRIMARY` provider must have credentials. Other providers are optional fallbacks and are used when their credentials are present.

## PostgreSQL and migrations

Start the local database with:

```text
docker compose up -d postgres
```

The Compose defaults are for local development only. Production must provide its own database name, user, and password through environment configuration.

Apply migrations with:

```text
alembic upgrade head
```

Optional local seed data can be loaded with:

```text
python -m scripts.seed_data
```

## Environment variables

Backend variables belong in the server environment or root `.env` file:

```text
LLM_PRIMARY=gemini
APP_ENV=development
GEMINI_API_KEY=
GROQ_API_KEY=
OPENAI_API_KEY=
DATABASE_URL=postgresql+psycopg://mcpilot:mcpilot@localhost:5432/mcpilot
MCP_SERVER_URL=http://localhost:8001/mcp
MCP_HOST=127.0.0.1
MCP_PORT=8001
CORS_ORIGINS=http://localhost:5173
GITHUB_API_URL=https://api.github.com
GITHUB_TOKEN=
```

`MCP_SERVER_URL=http://localhost:8001/mcp` is only the local-development default. Set `APP_ENV=production` and explicitly set `MCP_SERVER_URL` to the deployed MCP service URL in production; the backend refuses to start in production when it is missing. Do not put LLM, database, GitHub, or MCP credentials in frontend `VITE_*` variables.

## Run the services locally

Start FastAPI:

```text
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the production-style Streamable HTTP MCP server in a second terminal:

```text
python -m backend.app.mcp.server
```

The local MCP client connects to `http://localhost:8001/mcp` by default. `backend/app/mcp/stdio_server.py` remains available for local MCP development and testing:

```text
python -m backend.app.mcp.stdio_server
```

Start the frontend in a third terminal:

```text
cd frontend
npm install
npm run dev
```

For a separately hosted backend, set the public frontend variable `VITE_API_BASE_URL`. The Vite development proxy uses `VITE_API_PROXY_TARGET` when `VITE_API_BASE_URL` is empty.

## LLM fallback and GitHub

The router tries `LLM_PRIMARY` first, followed by credentialed fallback providers. A provider failure is recorded in the request trace, and the next configured provider is attempted. No provider is used without its credentials.

GitHub repository, issue, and pull-request reads are available through the MCP server and use the server-side `GITHUB_TOKEN` and `GITHUB_API_URL` configuration.

## Verification

Backend:

```text
python -m pip check
pytest -v
```

Frontend:

```text
cd frontend
npm run typecheck
npm run lint
npm run test -- --run
npm run build
```

## Production deployment

Run the FastAPI application and Streamable HTTP MCP server as separate processes or services. Set `APP_ENV=production`, production `DATABASE_URL`, `MCP_SERVER_URL`, `MCP_HOST`, `MCP_PORT`, `CORS_ORIGINS`, and the credentials for the selected LLM provider. Run `alembic upgrade head` against the production database before serving traffic. Build the frontend with `npm run build` and configure its public API base URL without exposing server credentials.
