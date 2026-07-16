# Changelog

All notable changes to AEGON are documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/), and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

---

## [Unreleased]

### Planned
- Real-time RTSP stream integration for Vision Intelligence.
- Kubernetes Helm chart for production deployment.
- Executive Copilot RAG integration with LLM.

---

## [7.0.0] — 2026-07-16

### Added
- Complete repository overhaul aligned to enterprise open-source standards (Palantir, Stripe, Microsoft quality tier).
- Structured `docs/` folder with Architecture, SystemDesign, Frontend, Backend, API, Database, Security, Deployment, and VisionIntelligence documentation.
- GitHub community health files: `CODE_OF_CONDUCT.md`, `SECURITY.md`, `SUPPORT.md`, `ROADMAP.md`.
- GitHub Issue Templates: Bug Report, Feature Request, Question.
- Pull Request Template with architectural scope and Definition of Done checklist.
- `CODEOWNERS` file enforcing review policies per module layer.
- CI/CD workflows: `ci.yml`, `codeql.yml`, `release.yml`, `docs.yml`.

### Changed
- `README.md` completely rewritten with professional architecture-first structure.
- `CONTRIBUTING.md` rewritten with strict architectural rules, branch naming, commit conventions, and DoD.
- `backend/.env.example` and `frontend/.env.example` standardized with documentation.

### Security
- All `.env` files sanitized. Real project credentials replaced with typed placeholders.
- `DATABASE_URL` fail-fast startup validation introduced in FastAPI lifespan manager.

---

## [6.5.0] — 2026-06-20

### Added
- Enterprise Vision Intelligence module with animated AI processing pipeline.
- Defect heatmap overlays on asset views.
- Digital Twin live telemetry animations.
- Multi-source image acquisition: upload, USB camera, RTSP/IP, mobile.
- Model metadata tracking: model version, inference latency, confidence score.
- Historical degradation trend charts.
- One-click maintenance ticket creation from detected defects.
- Enterprise operational metrics: processing time, queue status, GPU/inference status.

---

## [5.0.0] — 2026-05-01

### Added
- Supabase PostgreSQL migration from local SQLite.
- Database configuration refactored to single `DATABASE_URL` environment variable.
- Alembic migrations aligned to Supabase connection pooler settings.
- `asyncpg` driver validated at application startup.

### Changed
- Removed dynamic PostgreSQL connection string construction.
- Settings updated from `SUPABASE_DB_PASSWORD` + `SQLALCHEMY_DATABASE_URI` to `DATABASE_URL`.

---

## [4.0.0] — 2026-04-01

### Added
- Analytics module with MTTR, MTBF, and downtime metrics.
- Finance module with ROI tracking.
- Inventory module with EOQ and stock trend charts.
- Procurement module with vendor ranking.

---

## [3.0.0] — 2026-03-01

### Added
- Maintenance Intelligence module with predictive failure scoring.
- Asset health score (0–100) computed from telemetry.
- Celery + RabbitMQ integration for background task processing.

---

## [2.0.0] — 2026-02-01

### Added
- Asset Registry module with full CRUD and audit trail.
- Digital Twin module with real-time telemetry visualization.
- Redis caching for KPI dashboards.

---

## [1.0.0] — 2026-01-15

### Added
- Initial FastAPI backend with Clean Architecture foundation.
- Repository Pattern and Service Layer.
- Dependency Injection container.
- React 19 frontend scaffold with TanStack Router and TanStack Query.
- Executive Dashboard with basic KPI cards.
