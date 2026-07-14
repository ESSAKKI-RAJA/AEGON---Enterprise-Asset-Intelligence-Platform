# AEGON Enterprise Architecture

AEGON is an Enterprise Asset Intelligence Platform built with a Python-first, cloud-native architecture.

## Core Technologies
- **Frontend:** React, TypeScript, Vite, Tailwind CSS, TanStack (Router, Query)
- **Backend:** FastAPI, Pydantic
- **Database:** Supabase PostgreSQL (via SQLAlchemy 2.0 Async)
- **Caching & Queues:** Redis (via redis-py)
- **Background Processing:** Celery (Workers, Beat)
- **Infrastructure:** Supabase Storage, Realtime

## Architectural Layers (Backend)
1. **API Layer (`app/api`):** Exposes routes. Only uses Services. No database logic.
2. **Service Layer (`app/services`):** Contains all business logic. Retrieves Repositories from `UnitOfWork`.
3. **Repository Layer (`app/repositories`):** Abstraction over Database. All raw SQL or aggregation happens here. Inherits from `BaseRepository`.
4. **Data Layer (`app/models`):** SQLAlchemy ORM models. All models inherit from `AuditableBase` (includes SoftDelete, Tracking, Versioning).
5. **Infrastructure (`app/core`):** Redis Caching (`CacheHook`), Celery Configuration (`celery_app.py`), Centralized Exceptions (`exceptions.py`), Structured Logging (`structlog`), and Dependency Injection (`container.py`).

## Key Principles
- **Strict Boundaries:** APIs never talk to Repositories. Services never execute raw SQL.
- **Enterprise Observability:** Every endpoint is logged via `structlog`. Entities contain `audit_id`.
- **Performance:** `lazy="selectin"` for eager loading. Redis caching for Analytics endpoints.
- **Background Async:** Any task >300ms (like Analytics recalculation, Report generation) is processed in Celery.
