<div align="center">

# Frontend

React + TypeScript + Vite

![React](https://img.shields.io/badge/React-19-61DAFB?logo=react&logoColor=white)
![TypeScript](https://img.shields.io/badge/TypeScript-5.x-3178C6?logo=typescript&logoColor=white)
![Vite](https://img.shields.io/badge/Vite-latest-646CFF?logo=vite&logoColor=white)
![Tests](https://img.shields.io/badge/tests-18%20passed-brightgreen?logo=vitest&logoColor=white)
![ESLint](https://img.shields.io/badge/ESLint-passed-brightgreen?logo=eslint&logoColor=white)
![Prettier](https://img.shields.io/badge/Prettier-passed-brightgreen?logo=prettier&logoColor=white)

</div>

---

## Prerequisites

- [Node.js](https://nodejs.org/) 20+

## Setup

```sh
make install   # npm install
```

## Development

```sh
make dev       # vite dev server → http://localhost:5173
```

The frontend proxies API calls to the backend at `http://localhost:8000`
by default. Override with:

```sh
VITE_API_BASE_URL=http://localhost:8000 npm run dev
```

## Build

```sh
make build     # tsc + vite build → dist/
```

## Testing

```sh
make test            # vitest run (single pass)
make test-watch      # vitest in watch mode
```

Tests use `@testing-library/react` with `jsdom`. Files:

| File                    | Coverage                                     |
| ---------------------- | -------------------------------------------- |
| `api.test.ts`          | Fetch mocking, BookingError, request shaping |
| `ErrorBoundary.test.tsx`| Error catching, fallback render               |
| `App.test.tsx`         | Slot rendering, booking flow, error states    |

## Code Quality

```sh
make lint           # eslint
make format         # prettier --write
make format-check   # prettier --check
```

Pre-commit hooks: `eslint`, `prettier`, `vitest`.

## Architecture

```
src/
├── main.tsx           # Root + ErrorBoundary wrapper
├── App.tsx            # Slot selection + booking UI
├── api.ts             # API client (fetch wrapper, BookingError)
├── ErrorBoundary.tsx  # Global error boundary
└── App.css            # Styles
```

| Component       | Responsibility                                            |
| --------------- | -------------------------------------------------------- |
| `main.tsx`      | Mounts app, wraps with `ErrorBoundary` + `StrictMode`   |
| `App.tsx`       | State management, slot fetching, booking flow            |
| `api.ts`        | Typed fetch wrapper, `AbortController`, error handling  |
| `ErrorBoundary` | Catches render errors, shows fallback UI                 |