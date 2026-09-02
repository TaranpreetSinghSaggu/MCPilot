# MCPilot frontend

Vue 3 + TypeScript + Vite + Tailwind frontend for the MCPilot FastAPI service.

## Local development

1. Start the FastAPI application on `http://localhost:8000`.
2. From this directory, install dependencies and start Vite:

   ```text
   npm install
   npm run dev
   ```

The Vite development proxy forwards `/api` and `/health` to the local backend.
Set `VITE_API_BASE_URL` when the frontend must call a separately hosted API.
Only public API configuration belongs in frontend environment variables; LLM,
database, GitHub, and MCP credentials remain server-side.

The primary experience is `/chat`. Assistant responses retain their real,
request-scoped execution trace in the contextual panel, and `/operations`
provides concise live data with suggested questions that return to chat.

## Verification

```text
npm run typecheck
npm run lint
npm run test -- --run
npm run build
```
