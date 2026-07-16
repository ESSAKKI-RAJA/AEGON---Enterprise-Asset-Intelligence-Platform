# Contributing to AEGON

First, thank you for your interest in contributing to the AEGON Enterprise Platform. 

As a core enterprise system, AEGON adheres to strict engineering standards. This document outlines our development workflow, architectural constraints, and definition of done. Please review it thoroughly before opening a pull request.

## Development Workflow

1. **Fork and Clone**: Fork the repository and clone it to your local machine.
2. **Branching**: Create a feature branch from `main`. We enforce the following branch naming conventions:
   - `feat/<issue-id>-short-description`
   - `fix/<issue-id>-short-description`
   - `docs/<issue-id>-short-description`
   - `chore/<issue-id>-short-description`
3. **Commit Messages**: We strictly follow [Conventional Commits](https://www.conventionalcommits.org/). This allows us to automate changelog generation and semantic versioning.
   - Example: `feat(vision): integrate YOLO object detection pipeline`
4. **Pull Requests**: Submit your PR against the `main` branch. Ensure you use the provided Pull Request Template. 

## Architectural Rules

AEGON enforces Clean Architecture and Domain-Driven Design (DDD). Your PR will be rejected if it violates these boundaries.

1. **Strict Layering**: 
   - **Frontend**: Data visualization only. Never calculate, predict, or execute business logic in React components.
   - **API Layer**: Exposes services and gateways. Never put business logic in FastAPI routes.
   - **Service Layer**: Contains ALL business rules.
   - **Repositories**: Exclusively access the database (SQLAlchemy). Repositories must never import from the Service layer.
2. **Async-First**: All database interactions, file I/O, and external API calls must utilize asynchronous Python constructs (`async`/`await`).
3. **Long-Running Tasks**: Any computational task taking longer than 300ms (e.g., PDF generation, ML inference) must be delegated to a Celery background worker.

## Code Style

### Backend (Python)
- **Formatting**: We use `black` and `ruff`. Code must be fully formatted before pushing.
- **Typing**: Strict type hinting is required. We validate types using `mypy`.
- **Validation**: Use Pydantic v2 for all data validation and transfer objects (DTOs).

### Frontend (React/TypeScript)
- **Formatting**: We use `prettier` and `eslint`. 
- **State**: Use TanStack Query for server state. React Context or zustand should be reserved strictly for local UI state.
- **Styling**: TailwindCSS v4 via utility classes. Avoid inline styles.

## Testing Rules

Untested code is considered broken code. 

- **Backend**: We use `pytest`. You must provide unit tests for all new services and repositories, and integration tests for new API routes.
- **Frontend**: Tests are written using Vitest and React Testing Library. Components must have covering tests for rendering and interactions.

## Review Checklist and Definition of Done

Before submitting a Pull Request, ensure you meet the Definition of Done:
- [ ] Code successfully builds locally without warnings.
- [ ] Code adheres strictly to the defined Architecture Rules.
- [ ] Unit and integration tests are written and passing.
- [ ] No hardcoded configuration values or secrets are present.
- [ ] Documentation (Markdown files, OpenAPI specs, docstrings) has been updated.
- [ ] Commit history is clean and follows Conventional Commits.

## Issue Tracking

If you find a bug or want to propose a feature, please use the appropriate Issue Template in `.github/ISSUE_TEMPLATE/`.
