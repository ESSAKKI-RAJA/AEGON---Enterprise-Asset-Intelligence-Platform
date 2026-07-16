# Database Architecture

The primary relational data store for AEGON is PostgreSQL, currently hosted and managed via Supabase.

## Supabase Integration

While Supabase provides excellent frontend libraries for rapid prototyping, **AEGON utilizes Supabase strictly as a robust PostgreSQL hosting provider and authentication provider.** 

- We do NOT query the database directly from the React frontend.
- All database interactions flow through the FastAPI Backend -> SQLAlchemy Repositories -> Supabase PostgreSQL.
- This ensures that our business logic, validation, and analytics engines remain in the Python domain, preserving Clean Architecture.

## Connection Management

Because FastAPI is asynchronous and operates using a worker pool, connection management to PostgreSQL requires careful configuration to avoid exhausting the database connection limits.

### Direct Connection vs. Session Pooler

- **Direct Connection (Port 5432)**: Used for local development and environments supporting persistent IPv6 connections.
- **Session Pooler (Port 6543)**: Used in production, serverless deployments, or K8s environments where connection thrashing is common. Supabase provides a built-in PgBouncer pooler to multiplex connections efficiently.

AEGON's SQLAlchemy `create_async_engine` is configured with `pool_size`, `max_overflow`, and `pool_pre_ping=True` to handle connection drops gracefully.

## Migrations

All schema changes are managed declaratively via **Alembic**.

1. Modifying a SQLAlchemy model in `app/models/` requires generating a new migration:
   ```bash
   alembic revision --autogenerate -m "Description of change"
   ```
2. Migrations must be reviewed manually to ensure no accidental data destruction.
3. Migrations are executed via `alembic upgrade head` before the application starts.

## Soft Deletion and Auditing

Data integrity and compliance are paramount.
- Records are rarely hard-deleted. Instead, tables implement a `deleted_at` timestamp.
- Critical tables (Assets, Maintenance, Finance) utilize an `audit_id` and a `version` column to track historical changes, feeding directly into the Analytics and ML pipelines.
