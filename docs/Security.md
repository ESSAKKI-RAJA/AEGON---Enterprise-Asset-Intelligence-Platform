# Security Architecture

Security within AEGON is not an afterthought; it is a cross-cutting concern woven into the very fabric of the architecture.

## 1. Authentication (Identity)

All authentication is handled externally by Supabase Auth (GoTrue), allowing us to offload password hashing, OAuth integrations, and MFA to a dedicated, battle-tested service.

- Upon successful login, the client receives an RS256-signed JSON Web Token (JWT).
- The FastAPI gateway validates this token on every protected request by cryptographically verifying the signature against the public JWKS (JSON Web Key Set) exposed by Supabase.
- This ensures the API remains stateless while guaranteeing identity.

## 2. Authorization (Access Control)

### Role-Based Access Control (RBAC)
User roles (e.g., `Admin`, `Technician`, `Executive`) are embedded within the JWT claims or queried rapidly from the database. FastAPI dependencies enforce these roles at the route level.

### Row Level Security (RLS)
As a defense-in-depth measure, Supabase PostgreSQL is configured with Row Level Security policies.
- Even if the API tier were compromised, the database enforces that a user can only query or mutate rows belonging to their assigned tenant/department.
- The `DATABASE_URL` used by the application backend bypasses RLS (via the `service_role` equivalent connection), meaning the API layer MUST explicitly enforce tenant boundaries before executing queries.

## 3. Secret Management

- **No Hardcoding**: Under zero circumstances are secrets committed to the repository.
- **Environment Ingestion**: The FastAPI configuration relies on `pydantic-settings`, which strictly parses `.env` files or system environment variables. If a required secret (e.g., `DATABASE_URL`) is missing, the application will fail-fast and refuse to boot.
- **Production Secrets**: In production, secrets are injected via Kubernetes Secrets, HashiCorp Vault, or AWS Secrets Manager.

## 4. Network and Middleware Security

- **CORS**: Cross-Origin Resource Sharing is strictly limited to authorized frontend domains.
- **Rate Limiting**: Applied to sensitive endpoints (e.g., authentication routes, heavy analytical queries) to prevent DDoS attacks.
- **Headers**: Standard security headers (HSTS, X-Content-Type-Options) are enforced via FastAPI middleware.
