# System Architecture

## Architectural Principles
AEGON adheres to strict architectural boundaries:
1. **Clean Architecture & DDD:** The backend is organized into Domain-Driven layers. Repositories only access the database; Services contain business logic; Routers handle HTTP translation.
2. **Strict Component Boundaries:** Analytics modules only consume Business Services, ML only consumes Feature Pipelines, and AI strictly consumes Analytics and ML outputs.
3. **Async-First:** The backend API and database layer use asyncio and async SQLAlchemy to handle high concurrency efficiently.
4. **Strong Typing:** Pydantic is used throughout the API layer for robust data validation, and TypeScript ensures type safety on the frontend.

## Frontend Architecture
- **Framework:** React 19 + TypeScript
- **Routing:** TanStack Router (File-based routing)
- **State Management:** TanStack Query for remote state, Context API for auth/local state
- **Styling:** TailwindCSS with a bespoke design system
- **Build Tool:** Vite + Nitro (Cloudflare targeting)

## Backend Architecture
- **Framework:** FastAPI
- **Database:** PostgreSQL with asyncpg driver
- **ORM:** SQLAlchemy 2.0 (Async Declarative mapping)
- **Migrations:** Alembic
- **Caching:** Redis (accessed via async redis client)
- **Security:** JWT-based authentication, PBKDF2/Bcrypt password hashing, Role-Based Access Control (RBAC).

## High-Level Component Interaction
1. **Client Request:** The user interacts with the React frontend.
2. **API Gateway:** FastAPI receives the request and validates the JWT and schema using Pydantic.
3. **Service Layer:** The API router delegates to the appropriate Service class (e.g., `MaintenanceService`), which applies business rules.
4. **Repository Layer:** The Service requests data via the Repository (e.g., `MaintenanceRepository`), which executes async SQL against PostgreSQL.
5. **Caching Layer:** Frequently accessed data (like Asset Health Scores) may be retrieved directly from Redis to bypass the database.
