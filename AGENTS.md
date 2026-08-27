# AGENTS.md

Project conventions for AI agents working on this codebase.

## Stack

- **Backend**: Python 3.13, FastAPI, SQLAlchemy 2.0 (async), asyncpg, Pydantic V2
- **Frontend**: React 19, TypeScript, Vite
- **Database**: PostgreSQL 16
- **Tooling**: uv, ruff, mypy (strict), pytest, vitest, pre-commit

## Architecture

### Backend (src/ layout)

```
src/app/
├── api/v1/endpoints/   HTTP handlers only — no business logic
├── services/           Business logic — orchestrates repositories
├── repositories/       Database queries only — no business rules
├── models/             SQLAlchemy ORM models
├── schemas/            Pydantic V2 request/response models
├── core/               database.py, exceptions.py
└── settings.py         Pydantic Settings (env config)
```

**Flow**: endpoint → service → repository → model

- Endpoints use `Annotated` dependencies (`DbDep = Annotated[AsyncSession, Depends(get_db)]`)
- Exceptions live in `core/exceptions.py`, not in services
- Schemas use `to_camel` alias generation for JSON field names
- Datetimes serialize as UTC with `Z` suffix
- `get_db` commits after yield, rolls back on error

### Frontend

- `api.ts` — typed fetch client, `BookingError` extends `Error`
- `App.tsx` — state management with `useCallback`/`useMemo`
- `ErrorBoundary.tsx` — wraps the app
- `AbortController` on all fetch calls
- `aria-live` regions for status messages

## Code Style

### Python
- ruff: `["E", "F", "I", "N", "W", "UP", "B", "SIM"]`
- Line length: 88
- mypy strict mode with `pydantic.mypy` plugin
- No `# type: ignore` without justification
- TypedDict for service return types

### TypeScript
- ESLint flat config with React + hooks plugins
- Prettier (double quotes, trailing commas, 80 char width)
- Strict mode enabled
- No `any` — use proper types

### CSS
- Status colors: success `#176b56`, error `#c0392b`, info `#3b7ea1`
- Icons from `lucide-react` with `aria-hidden="true"`

## Testing

### Backend
- **Unit** (`tests/unit/`): pure logic, no DB, no Docker needed
- **Integration** (`tests/integration/`): real PostgreSQL via `docker compose up -d db`
- Use `@pytest.mark.parametrize` for multi-case tests
- Concurrency tests use `asyncio.gather`
- Coverage threshold: 85% (enforced via `--cov-fail-under`)

### Frontend
- Vitest + `@testing-library/react` + jsdom
- Mock `fetch` with `vi.stubGlobal("fetch", fn)`
- Test files: `*.test.ts(x)` next to source

## Commands

```sh
# Backend (from backend/)
make install      # uv sync + pre-commit
make dev          # uvicorn --reload
make test         # pytest with coverage
make test-unit    # no Docker needed
make test-integration  # needs docker compose up -d db
make check        # ruff + mypy

# Frontend (from frontend/)
make install      # npm install
make dev          # vite dev server
make test         # vitest run
make lint         # eslint
make format       # prettier --write
```

## Pre-commit Hooks

Runs on every commit: ruff, ruff-format, mypy, uv lock check, eslint, prettier, vitest.

## Git Conventions

- Atomic commits, one logical change per commit
- Conventional commit prefixes: `feat:`, `fix:`, `chore:`, `test:`, `docs:`, `ci:`, `refactor:`
- Keep commit messages concise — one line summary, optional body

## Database

- Init scripts in `db/init/` (numbered: schema, migrations, seed)
- Schema split from seed so tests can apply schema without seed data
- `IF NOT EXISTS` on all DDL for idempotency
- Double-booking prevention: `SELECT FOR UPDATE SKIP LOCKED` + unique constraint