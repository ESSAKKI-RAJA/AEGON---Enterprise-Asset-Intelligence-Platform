# Backend Architecture

The AEGON backend is an asynchronous, high-performance API built with FastAPI and Python 3.12. It serves as the intelligent core of the enterprise platform.

## Technology Stack

- **Framework**: FastAPI
- **Validation**: Pydantic v2
- **ORM**: SQLAlchemy 2.0 (with `asyncpg` driver)
- **Migrations**: Alembic
- **Dependency Injection**: `dependency-injector`
- **Background Tasks**: Celery
- **Testing**: Pytest (with `pytest-asyncio`)

## Architectural Constraints

### 1. The Repository Pattern
To maintain strict database isolation, all database queries (SQLAlchemy operations) must be contained within a Repository class (`app.repositories.*`).
- Repositories must NOT contain business logic.
- Repositories must NOT import from `app.services.*`.
- Repositories expose clean, asynchronous methods (e.g., `get_asset_by_id`, `create_maintenance_ticket`).

### 2. The Service Layer
The Service Layer (`app.services.*`) is the heart of AEGON. It contains all business rules, orchestration, and domain logic.
- Services consume Repositories via Dependency Injection.
- Services must NEVER execute raw SQL or use SQLAlchemy session objects directly.
- Services return Pydantic models (DTOs) or domain entities, never SQLAlchemy ORM models.

### 3. API Routes (Controllers)
FastAPI routes (`app.api.v1.*`) act strictly as HTTP gateways.
- They depend on the DI container to resolve the required Service.
- They parse incoming HTTP requests, pass data to the Service, and serialize the response.
- **Rule**: Never write `if` statements containing business logic inside a router.

## Dependency Injection

We utilize the `dependency-injector` library to manage the lifecycle of our components. 
- The container is configured in `app/core/container.py`.
- Repositories and Services are wired together at startup.
- This allows for seamless mocking of Repositories during unit testing of Services.

## Asynchronous Paradigms

AEGON is an `async-first` codebase. 
- You must use `async def` for all API endpoints, services, and repository methods.
- Blocking operations (e.g., synchronous file reads, heavy CPU loops) must be executed in a thread pool (`asyncio.to_thread`) or offloaded to Celery to avoid blocking the main event loop.

## Security & Validation

- **Pydantic**: All incoming and outgoing data must be validated against Pydantic models. We use strong typing (`UUID`, `EmailStr`, etc.).
- **Authentication**: JWT verification is implemented as a FastAPI dependency. It is applied cross-cuttingly to protected routes.
