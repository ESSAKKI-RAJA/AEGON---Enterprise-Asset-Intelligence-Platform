# Production Readiness Checklist

Before promoting AEGON to the production environment, ensure all items on this checklist have been verified and signed off.

## 1. Code Quality & Testing
- [x] All automated Unit Tests pass (`pytest`).
- [x] All automated End-to-End (E2E) Acceptance Tests pass (`playwright`).
- [x] TypeScript compiler passes with zero strict errors (`tsc --noEmit`).
- [x] Linter passes with no critical warnings (`eslint .`).
- [x] Code formatting is unified across the codebase (`prettier --check .`).

## 2. Security
- [x] Secret Keys are rotated and removed from source control.
- [x] CORS policies are restricted to specific, known origins.
- [x] All dependencies are scanned for vulnerabilities (`npm audit`).
- [x] Role-Based Access Control (RBAC) rules are strictly enforced on all sensitive API endpoints.
- [x] Passwords are hashed using PBKDF2/Bcrypt with a strong salt.

## 3. Performance & Reliability
- [x] Frontend assets build successfully in production mode (`npm run build`).
- [x] Redis caching is configured and connected for high-volume endpoints.
- [x] Database connection pooling is configured (e.g., PgBouncer or SQLAlchemy connection pool settings).
- [x] Uvicorn workers are scaled appropriately for the CPU architecture.

## 4. Observability
- [x] Application logs are aggregated and formatted (e.g., structured JSON logs).
- [x] Health check endpoints (`/health`) are active and monitored.
- [x] Sentry or similar error tracking is configured for both Frontend and Backend.

## 5. Deployment
- [x] Database migrations (`alembic`) execute cleanly against the target schema.
- [x] Docker images build and pass vulnerability scanning.
- [x] Deployment pipelines (CI/CD) execute cleanly without manual intervention.
