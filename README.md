# Enterprise Multi-Agent AI Analyst

A local-first analytics assistant that turns a business question into a governed SQL query, executes it against PostgreSQL, computes descriptive statistics, retrieves metric definitions, and returns a cited narrative report.

## What is included

- **Supervisor workflow:** LangGraph routes a question through SQL planning, read-only query execution, statistical analysis, retrieval, and report composition.
- **Data access:** PostgreSQL via SQLAlchemy. The SQL guard allows a single `SELECT` statement and rejects writes and multiple statements.
- **Knowledge retrieval:** a small local TF-IDF index over metric definitions and data dictionary files; retrieved passages appear in the report.
- **API:** FastAPI endpoints for health, schema discovery, and analysis.
- **UI:** Streamlit chat-style analyst interface with result table, SQL, and report.
- **MCP:** a separate MCP server exposing schema discovery and analysis as tools.
- **Demo mode:** starts without an LLM key. It uses deterministic examples so the entire stack can be explored locally.

## Quick start (Docker)

Docker Compose starts three containers: the app API, the Streamlit UI, and PostgreSQL. PostgreSQL creates the `analyst` database and loads the sample orders from `data/orders.csv` automatically the first time its data volume is initialized. You do not need to install PostgreSQL separately.

1. Install Docker Desktop and make sure its engine is running. On Windows this requires the WSL 2/virtualization feature to be enabled.
2. Copy `.env.example` to `.env` and optionally add an OpenAI API key. The `.env` file is read by the API; it is excluded from the Docker image.
3. From this project folder, run `docker compose up --build`.
4. Open Streamlit at `http://localhost:8501` and API docs at `http://localhost:8000/docs`.

The web ports are bound to localhost. PostgreSQL is reachable by the other containers but is not published on a host port. Stop the stack with `docker compose down`; the database volume is kept. Use `docker compose down -v` only if you intentionally want to erase the persisted database and initialize it again.

PostgreSQL is seeded with sample order data on first startup. Try: “How did monthly revenue change?” or “Which region has the most orders?”

## Run without Docker (Windows-friendly)

This mode uses Python and a local SQLite file, so it does not require Docker, WSL, or administrator privileges. Requires Python 3.11+:

```bash
py -3.11 -m venv .venv
Copy-Item .env.example .env
.venv\Scripts\python.exe -m pip install -r requirements.txt
.venv\Scripts\python.exe scripts/seed_db.py
.venv\Scripts\python.exe -m uvicorn app.api.main:app --reload
```

Run the last command in one PowerShell window. In a second window, change to this project directory and run `.venv\Scripts\python.exe -m streamlit run app/ui/streamlit_app.py`. Both services read `.env` from the project directory. To use PostgreSQL locally instead, change `DATABASE_URL` in `.env` to a PostgreSQL connection string.

## Architecture

```text
Question → Supervisor (LangGraph)
          ├─ SQL planner → SQL guard → PostgreSQL → result rows
          ├─ Statistics worker → summary, trend and outlier signals
          ├─ RAG worker → metric definitions and data dictionary citations
          └─ Report worker → answer, caveats, SQL and evidence
```

The demo SQL planner is deterministic and deliberately limited. Set `OPENAI_API_KEY` and `LLM_MODEL` to enable model-assisted planning and report writing. SQL is still validated before execution. Use least-privilege, read-only database credentials in any shared deployment; this starter does not implement user authentication or row-level security.

## Project layout

```text
app/analytics/     LangGraph workflow, agents, SQL and statistics
app/api/           FastAPI service
app/mcp_server/    MCP tool server
app/retrieval/     Local RAG index
app/ui/            Streamlit application
data/              Seed CSV and knowledge base
db/                PostgreSQL initialization schema
scripts/           Database seeding utility
```

## API

- `GET /health` — liveness and database connectivity
- `GET /schema` — available tables and columns
- `POST /analyze` — body: `{"question":"How did monthly revenue change?"}`

## Safety and limits

The SQL guard rejects non-SELECT statements, comments, and multiple statements. It does not replace database permissions or a SQL parser. Before connecting production data, replace demo credentials, enforce a read-only DB role, add authentication/authorization, and review privacy and retention requirements. Results are capped at 500 rows.

## Next steps

1. Add authentication and per-tenant data access.
2. Replace TF-IDF retrieval with a managed vector store for a large knowledge base.
3. Add query audit logging, timeouts, and human approval for costly queries.
4. Add evaluation cases for SQL correctness and groundedness.
5. Add tracing and deployment manifests for your target environment.
