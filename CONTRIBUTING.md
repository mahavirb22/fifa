# Contributing to MatchDay Command Center

## Project Layout

```
backend/         Python FastAPI backend
  app/           Application source
  tests/         Test suite
frontend/        React + TypeScript frontend
  src/           Application source
  src/test/      Test setup and type declarations
docs/            Architecture documentation
```

## Development Setup

### Prerequisites

- Python 3.11+
- Node.js 20+
- (Optional) Google Cloud SDK for Gemini integration

### Backend

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
pip install pytest pytest-cov mypy ruff

# Run locally
uvicorn app.main:app --reload
```

### Frontend

```bash
cd frontend
npm install
npm run dev
```

### Pre-commit Hooks

```bash
pip install pre-commit
pre-commit install
```

## Quality Gates

These gates are **non-negotiable** — all must pass before merging.

| Gate | Backend | Frontend |
|------|---------|----------|
| **Lint** | `ruff check app/ tests/` | `npm run lint` (ESLint + jsx-a11y) |
| **Format** | `ruff format --check app/ tests/` | `npm run format:check` (Prettier) |
| **Types** | `mypy app/` (strict mode) | `npx tsc --noEmit` (strict mode) |
| **Tests** | `pytest --cov-fail-under=90` | `npm run test:coverage` (90%+ threshold) |
| **Build** | — | `npm run build` |
| **Accessibility** | — | axe assertion in every component test |

## Coding Conventions

These are stated as rules, not suggestions:

1. **Fully type-annotated**: Every function has return-type annotations. No `any` in TypeScript (except `.d.ts`).
2. **Docstrings on public interfaces**: Module, class, and public function docstrings follow PEP 257.
3. **No secrets in code**: Use Application Default Credentials. No API keys.
4. **Accessibility is part of the definition of done**: Every component test includes an `expect(await axe(container)).toHaveNoViolations()` assertion.
5. **Enums over strings**: Finite value sets use `str, Enum` (Python) or union types (TypeScript).
6. **Bounded inputs**: Every numeric Pydantic field has `ge` and `le` constraints.
7. **Pure domain logic**: Domain modules have zero I/O imports.
8. **Small functions**: Max McCabe complexity of 10.

## Submission Workflow

1. Create a feature branch from `main`
2. Make changes following conventions above
3. Run all quality gates locally
4. Open a pull request
5. CI must pass all 4 jobs before merge
