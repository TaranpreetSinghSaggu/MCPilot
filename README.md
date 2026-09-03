# MCPilot

MCPilot is an AI-powered DevOps intelligence platform that combines LLM reasoning, Model Context Protocol (MCP), structured tool execution, PostgreSQL, GitHub integration, and a modern web interface.

## Demo

**Live Demo:** [Open MCPilot](https://frontend-two-blond-33.vercel.app/chat)

MCPilot provides two primary experiences:

- **AI Assistant** — ask natural-language questions about repositories, builds, deployments, incidents, issues, and supported GitHub resources.
- **Operations Dashboard** — explore structured operational data through filters and statistics.

The public demo may take longer to respond on the first request after inactivity because the deployment can experience cold starts.

## Overview

MCPilot demonstrates how an AI agent can answer practical DevOps questions using structured tools and real application data.

A user asks a question in natural language, the agent determines the required capability, invokes the appropriate tool through MCP against PostgreSQL or GitHub, and feeds the structured result back to the LLM to generate the final response.

Each request also produces a structured execution trace, making the system more than a basic LLM chatbot.

## Key Features

- Natural-language DevOps assistant
- MCP-based structured tool execution
- GitHub integration through MCP
- PostgreSQL-backed DevOps data
- Credential-aware LLM provider routing and fallback
- Structured request-level execution traces
- Operations dashboard
- Conversation history for follow-up questions
- FastAPI REST API
- Separate frontend, backend, and MCP server architecture

## End-to-End Request Flow

```text
User question
    -> Vue frontend
    -> FastAPI
    -> Agent
    -> LLM provider
    -> Tool decision
    -> MCP client
    -> MCP server
    -> Selected MCP tool
    -> PostgreSQL or GitHub
    -> Tool result
    -> LLM
    -> Final answer and trace
    -> Vue frontend
```

The frontend sends the question and bounded conversation history to the backend. The agent obtains the available MCP tools, asks the selected provider to reason over the question, invokes any requested tools, and sends the tool result back to the provider before returning the answer and trace.

The browser does not directly access MCP, PostgreSQL, or GitHub. The backend owns service-to-service communication and credentials.

## MCP Integration

MCP keeps tool discovery and execution separate from the LLM provider and the browser. The backend MCP client connects to the MCP server, which exposes structured read-oriented capabilities backed by application services and the GitHub integration.

The currently exposed tools include:

- `search_repositories`
- `search_issues`
- `search_builds`
- `get_slowest_builds`
- `search_deployments`
- `get_deployment_stats`
- `search_incidents`
- `get_incident_stats`
- `github_get_repository`
- `github_get_issues`
- `github_get_pull_requests`

The MCP server supports Streamable HTTP for the production transport. A separate stdio entry point is available for local MCP development and testing.

### Why MCP?

MCPilot uses Model Context Protocol to create a clear boundary between LLM reasoning and application capabilities.

Instead of giving the browser or LLM direct access to databases and external APIs, capabilities are exposed as structured MCP tools. This provides a consistent tool interface, separates reasoning from execution, centralizes access to external systems, and makes tool execution easier to observe and extend.

## Example Queries

```text
Which repositories use Python?

Which repositories belong to the Platform team?

Show me the failed deployments.

What are the slowest builds?

Show me active incidents.

What is the description of octocat/Hello-World?

List the open issues in octocat/Hello-World.

Show me the pull requests for octocat/Hello-World.
```

The agent determines the required capability, invokes the appropriate MCP tool, and uses the returned structured data to generate the final response.

## LLM Routing and Fallback

The provider abstraction supports Gemini, Groq, and OpenAI. The configured primary provider is attempted first, followed by credentialed fallback providers in the router's configured order.

```text
Primary provider
    -> provider failure
    -> next credentialed fallback
    -> successful answer or next fallback
```

The primary provider must have credentials. Fallback providers remain available when their credentials are present.

Provider failures are recorded in the trace. Fallback is performed at the provider level, so a transient failure from the primary model does not necessarily fail the entire agent request.

If all configured providers fail, the agent returns an error rather than producing an unsupported response.

## GitHub Integration

GitHub access is server-side and is exposed through the MCP layer. The browser does not call GitHub directly and does not receive GitHub credentials.

The current integration supports:

- Repository details
- Repository issues
- Repository pull requests

The GitHub adapter communicates with the GitHub API through HTTPX, while MCP exposes the supported operations to the agent.

A public repository such as `octocat/Hello-World` can be used for testing or demonstration or any available github repository.

## Operations Dashboard

The Operations view displays persisted backend data for:

- **Repositories** — filtering by language, team, and visibility
- **Builds** — status filtering and slowest-build results
- **Deployments** — filtering and deployment statistics
- **Incidents** — filtering and incident statistics
- **Issues** — filtering by repository, priority, status, and assignee

The dashboard consumes FastAPI endpoints rather than maintaining a duplicate dataset in the frontend.

## Observability and Tracing

Agent execution records request-scoped events such as:

- `agent.request.started`
- `llm.provider.started`
- `mcp.tool.started`
- `mcp.tool.completed`
- `llm.provider.completed`
- `llm.provider.selected`
- `agent.response.completed`

Events include fields such as timestamp, status, provider, tool name, duration, and safe error information.

This provides visibility into provider selection, MCP tool execution, fallback behavior, failures, and execution timing for each assistant response.

## API

The FastAPI backend exposes these important endpoints:

| Method | Endpoint | Purpose |
| --- | --- | --- |
| GET | `/health` | Service health response |
| GET | `/api/agent/readiness` | Verify MCP connectivity and tool discovery |
| GET | `/api/repositories` | Search persisted repositories |
| GET | `/api/issues` | Search persisted issues |
| GET | `/api/builds` | Search build runs |
| GET | `/api/builds/slowest` | Return slowest build runs |
| GET | `/api/deployments` | Search deployments |
| GET | `/api/deployments/stats` | Return deployment statistics |
| GET | `/api/incidents` | Search incidents |
| GET | `/api/incidents/stats` | Return incident statistics |
| POST | `/api/agent/chat` | Ask the DevOps assistant a question |

## Technology Stack

### Frontend

- Vue 3
- TypeScript
- Vite
- Tailwind CSS
- Marked
- DOMPurify

### Backend

- Python 3.10
- FastAPI
- SQLAlchemy
- Alembic
- Pydantic
- Uvicorn

### AI / MCP

- Gemini
- Groq
- OpenAI
- MCP Python SDK

### Data / Integrations

- PostgreSQL
- psycopg
- GitHub API through HTTPX

### Testing

- Pytest
- Vitest
- Vue Test Utils
- jsdom

## Local Development

### Requirements

- Python 3.10
- Node.js and npm
- PostgreSQL, or Docker Desktop for local PostgreSQL

Create and activate a Python environment from the repository root:

```powershell
py -3.10 -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -e ".[dev]"
```

Copy `.env.example` to `.env` and supply the required configuration through environment variables.

Start local PostgreSQL:

```bash
docker compose up -d postgres
```

Apply migrations and optionally load local seed data:

```bash
alembic upgrade head
python -m scripts.seed_data
```

Start FastAPI:

```bash
uvicorn backend.app.main:app --reload --host 127.0.0.1 --port 8000
```

Start the Streamable HTTP MCP server in a second terminal:

```bash
python -m backend.app.mcp.server
```

For local stdio MCP development/testing:

```bash
python -m backend.app.mcp.stdio_server
```

Start the frontend:

```bash
cd frontend
npm install
npm run dev
```

## Environment Configuration

Credentials and service configuration are supplied through environment variables.

Main backend variables include:

```text
APP_ENV
LLM_PRIMARY
GEMINI_API_KEY
GROQ_API_KEY
OPENAI_API_KEY
DATABASE_URL
MCP_SERVER_URL
CORS_ORIGINS
GITHUB_API_URL
GITHUB_TOKEN
```

The frontend uses public configuration variables such as:

```text
VITE_API_BASE_URL
VITE_API_PROXY_TARGET
```

`VITE_*` values are exposed to the browser, so LLM, database, GitHub, and MCP credentials must remain server-side.

Never commit `.env`, API keys, GitHub tokens, passwords, or database connection strings.

## Testing

Backend tests cover database services, MCP tools, agent behavior, tool schemas, and GitHub client/adapter behavior.

Frontend tests cover API requests, routing, shared components, chat behavior, trace rendering, and Operations dashboard behavior.

Run backend checks from the repository root:

```bash
python -m pip check
pytest -v
```

Run frontend checks from `frontend`:

```bash
npm run typecheck
npm run lint
npm run test -- --run
npm run build
```

## Engineering Highlights

- Clear frontend/backend separation
- Agent orchestration around structured tool calls
- MCP as an explicit tool boundary
- Provider abstraction with credential-aware fallback
- PostgreSQL persistence with Alembic migrations
- Server-side GitHub integration
- Request-scoped structured tracing
- API response validation in the frontend service layer
- Environment-based configuration for service endpoints and credentials

## Limitations

The demo deployment uses infrastructure that may scale services down after periods of inactivity, so the first request after inactivity can take longer.

## License

MIT License
