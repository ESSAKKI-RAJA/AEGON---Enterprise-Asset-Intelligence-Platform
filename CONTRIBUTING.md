# Contributing to AEGON

Thank you for your interest in contributing to the AEGON Enterprise Asset Intelligence Platform.

## Development Setup

1. Fork and clone the repository
2. Set up the backend: `cd backend && python -m venv venv && pip install -r requirements.txt`
3. Set up the frontend: `cd frontend && npm install`
4. Copy environment files: `cp backend/.env.example backend/.env` and `cp frontend/.env.example frontend/.env`
5. Start the backend: `uvicorn app.main:app --reload`
6. Start the frontend: `npm run dev`

## Code Standards

### Frontend
- TypeScript strict mode
- ESLint + Prettier formatting
- Components in `src/components/` organized by domain
- All API calls through `src/services/` or `src/lib/api.ts`
- State management via TanStack Query (server state) and Zustand (UI state)

### Backend
- Python 3.12+ with type hints
- FastAPI async endpoints
- Pydantic v2 schemas for validation
- SQLAlchemy 2.0 async ORM
- Repository pattern for data access
- Service layer for business logic

## Pull Request Process

1. Create a feature branch from `main`
2. Ensure `npx tsc --noEmit` passes
3. Ensure `npm run lint` passes with no errors
4. Ensure `pytest` passes
5. Update documentation if needed
6. Submit a PR with a clear description

## Architecture Rules

- **Frontend** is presentational only — no business logic
- **Services** contain all business rules
- **Repositories** only access the database
- **ML/AI** operates through dedicated pipelines, never inline
- **Security** is cross-cutting — every endpoint validates, authorizes, and audits
