# Security Policy

At AEGON, security is foundational. This document outlines our security policies, how to report vulnerabilities, and our architectural security posture.

## Supported Versions

We provide security updates for the current major release and the immediately preceding major release.

| Version | Supported          |
| ------- | ------------------ |
| 7.x.x   | :white_check_mark: |
| 6.x.x   | :white_check_mark: |
| < 6.0   | :x:                |

## Reporting a Vulnerability

If you discover a security vulnerability in the AEGON platform, we ask that you report it immediately. 

**Please do not report security vulnerabilities through public GitHub issues.**

Instead, report them privately via email to `security@aegon-enterprise.example.com`. 

### Disclosure Process

1. **Acknowledge**: We will acknowledge receipt of your vulnerability report within 48 hours.
2. **Investigate**: Our engineering team will investigate the issue and confirm the vulnerability.
3. **Mitigate**: We will develop and test a patch to resolve the issue.
4. **Disclose**: Once the patch is released and users have been notified, we will publicly acknowledge your contribution (if desired).

## Architectural Security Posture

AEGON enforces strict security paradigms cross-cuttingly across all layers of the architecture.

### Authentication & Authorization
- **JWT (JSON Web Tokens)**: All API access requires a valid RS256 JWT, signed and verified against the `SUPABASE_JWKS_URL`.
- **RBAC & ABAC**: Role-Based Access Control and Attribute-Based Access Control are enforced natively within the FastAPI dependency injection graph.
- **Supabase Row Level Security (RLS)**: The database layer utilizes RLS to ensure that users can only interact with rows they are authorized to access, providing a defense-in-depth layer below the API.

### Secrets Handling
- **No Hardcoded Secrets**: Under no circumstances should secrets (e.g., `DATABASE_URL`, `SUPABASE_SECRET_KEY`) be hardcoded or committed to version control.
- **Environment Variables**: All configuration must be ingested via environment variables parsed strictly by `pydantic-settings`. 

### Dependency Management
- All dependencies are strictly pinned in `package-lock.json` and `requirements.txt`/`pyproject.toml`.
- We utilize automated dependabot workflows and regular audits to ensure vulnerabilities in downstream packages are remediated promptly.

### Security Headers & Network
- The FastAPI layer is configured with robust middleware implementing secure CORS policies, rate limiting, and standard security headers (HSTS, X-Content-Type-Options, etc.).
