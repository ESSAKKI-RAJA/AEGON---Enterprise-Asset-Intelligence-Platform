# AEGON Project Rules

These rules dictate the strict architectural boundaries that Antigravity must follow when building the AEGON platform.

## Global Architectural Rules

1. **DO NOT rewrite existing architecture.**
2. **DO NOT replace existing modules.**
3. **DO NOT duplicate business logic.**
4. **DO NOT introduce new architectural patterns.**
5. **Repositories ONLY access the database.**
6. **Business Services contain ALL business rules.**
7. **Analytics ONLY consumes Business Services.**
8. **ML ONLY consumes Feature Pipelines and Business Services.**
9. **AI ONLY consumes Analytics, ML outputs, and Business Services.**
10. **Executive Copilot ONLY consumes AI Gateway, RAG, and approved tools.**
11. **API Layer ONLY exposes Services and Gateways.**
12. **Frontend ONLY communicates with the API Layer.**
13. **Security is cross-cutting and applies to every layer.**
14. **Cloud and Infrastructure must support the architecture, never modify it.**
15. **Every new component must follow SOLID principles, Clean Architecture, Domain-Driven Design (DDD), async-first programming, strong typing with Pydantic, and comprehensive unit/integration testing.**

## Module-Specific Boundaries

- **Business Intelligence**: Read-only. Never access repositories. Generate executive dashboards, dynamic KPIs, advanced analytics, and reporting.
- **Enterprise Machine Learning**: Never know SQL or FastAPI. Operates purely on Feature Pipelines → Training → Prediction → Monitoring. Exposes `PredictionDTO`.
- **Enterprise AI Engine**: AI reasons, it does not predict. It consumes Analytics, Predictions, and Business Rules. Exposes recommendations with priority and confidence.
- **Executive Copilot**: Never hallucinates. Always uses RAG + AI Engine + Business Services. Always cites sources.
- **Enterprise API Platform**: Rest, GraphQL, WebSockets. Only exposes services. Never exposes repositories.
- **Enterprise Frontend**: Role-based UI. Never talks to repositories.
- **Enterprise Security**: JWT, RBAC, ABAC. Must be cross-cutting.
- **Enterprise Cloud Platform**: Kubernetes, Terraform. Deploys architecture, does not change it.

---

# AEGON Enterprise Development Blueprint

## Mission
Build **AEGON** as an **Enterprise Asset Intelligence Platform**, not as a CRUD application.
Every implementation decision must maximize:
* Business Value, Enterprise Readiness, Python-first Intelligence, Cloud Native Architecture, AI-driven Decision Support, Cybersecurity, Scalability, Maintainability.

## 1. WHAT TO BUILD
Phase 1: Dashboard, Assets, Maintenance, Inventory, Procurement, Finance, Analytics.
Nothing else.

## 2. BUILD ORDER
Never randomly jump between modules.
Dashboard -> Assets -> Maintenance -> Inventory -> Procurement -> Finance -> Analytics.
Reason: Everything depends on Assets. Analytics depends on everything.

## 3. WHAT TO BUILD INSIDE EVERY MODULE
Every module follows exactly this hierarchy:
Overview -> KPIs -> AI Insights -> Visual Analytics -> Operational Data -> Actions -> History -> Reports.
No exceptions.

## 4. HOW TO BUILD
Never build page-by-page. Always build vertically:
UI -> Backend API -> Database -> Python Analytics -> Charts -> Reports.
Only after Dashboard is production ready, move to Assets.

## 5. TECHNOLOGY DISTRIBUTION
Frontend 20%, Backend 80%.
Approximate effort: React 20%, FastAPI 35%, AI/ML 25%, Database 10%, Cloud 10%. Python must dominate.

## 6. FRONTEND
Purpose: Visualization only. Never calculate. Never predict. Never optimize. Never forecast.
React should: fetch, display, filter, search, visualize. Nothing more.
Use: React, TypeScript, Tailwind, TanStack Router, TanStack Query, Recharts, Framer Motion (very little), Lucide Icons.

## 7. BACKEND
Everything intelligent happens here.
Use: FastAPI, Pydantic, SQLAlchemy, Alembic, Async, Dependency Injection, Repository Pattern, Service Layer.
Never put business logic inside routes.

## 8. DATABASE
Use Supabase PostgreSQL.
Structure: Users, Departments, Assets, Asset History, Maintenance, Inventory, Procurement, Finance, Analytics, Audit Logs.
Every table: UUID, created_at, updated_at, created_by, updated_by, deleted_at, deleted_by, version, audit_id.
Soft delete only.

## 9. CLOUD
Use Supabase for Database, Storage, Realtime, Authentication (later), RLS, Backups, Policies, Storage Buckets.
Never use Supabase only as SQL.

## 10. REDIS
Use for Caching, Dashboard KPIs, Analytics Cache, Sessions, Queues, Notifications.
Don't cache everything. Cache expensive things.

## 11. CELERY
Anything longer than 300 ms -> Background.
Examples: Prediction, Forecast, PDF, Excel, Import, Bulk Upload, Analytics, Report Generation.

## 12. AI
Never create AI for marketing. Every AI feature must solve work.
- Dashboard: Executive Insights
- Assets: Health Score
- Maintenance: Failure Prediction
- Inventory: Demand Forecast
- Procurement: Vendor Ranking
- Finance: Budget Forecast
- Analytics: Trend Prediction

## 13. AI MODELS
Keep it realistic. Use Scikit Learn, XGBoost, Prophet, SHAP, Pandas, NumPy.
Avoid unnecessary deep learning unless the problem requires it.

## 14. EVERY AI RESPONSE
Must include: Prediction, Confidence, Reason, Data Used, Recommended Action.
Example:
Failure Risk: 78% | Confidence: 91% | Reason: High utilization, Overdue maintenance, Temperature anomaly | Recommendation: Schedule inspection within 7 days.

## 15. ANALYTICS
Every module contains analytics:
- Assets: Health Trend, Cost Trend, Age Trend
- Maintenance: MTTR, MTBF, Downtime, Failure Rate
- Inventory: Stock Trend, EOQ, Forecast
- Finance: ROI, Budget, Variance
Analytics module combines everything.

## 16. CYBERSECURITY
Every endpoint: Validate, Authorize, Audit, Log, Protect.
Features: RBAC, JWT, Rate Limit, Audit Trail, Immutable Logs, Soft Delete, Secure Headers, Input Validation, CORS, Encryption, Secrets.

## 17. REPORTING
Every module exports PDF, Excel, CSV. Reports generated in Python. Not React.

## 18. DESIGN
Target Microsoft, Palantir, Datadog, Power BI, SAP, Azure Portal, ServiceNow.
Enterprise: Minimal, Professional, Calm, Data First.

## 19. PERFORMANCE
Always: Pagination, Filtering, Lazy Loading, Virtual Tables, Caching, Background Jobs, Compression.

## 20. CODE QUALITY
Folder Structure:
Frontend: components/, features/, hooks/, services/, routes/, types/, utils/
Backend: api/, core/, services/, repositories/, models/, schemas/, ai/, analytics/, security/, workers/, utils/

## 21. WHAT NOT TO DO
Don't: Overuse animations, Overuse gradients, Put business logic in React, Hardcode values, Duplicate components, Mix services, Mix analytics into UI, Build fake AI, Create unnecessary pages, Add features without purpose.

## 23. DEVELOPMENT PROCESS
Business Requirement -> UX Flow -> Database Design -> API Contract -> Python Service -> AI/Analytics Logic -> Frontend UI -> Testing -> Documentation.

## 24. ANTIGRAVITY EXECUTION RULES
1. Think domain-first, not page-first.
2. Implement complete workflows, not isolated screens.
3. Keep React presentational; keep Python intelligent.
4. Build reusable services before reusable components.
5. Every module must expose measurable business KPIs.
6. Every AI output must be explainable and actionable.
7. Every database change must be migration-driven and auditable.
8. Every feature must improve an enterprise decision, reduce operational effort, or increase trust.
9. Maintain production-quality code even during rapid iteration.
10. Continuously validate with linting, type checks, tests, and builds after each completed module.

> **Build AEGON like a Fortune 500 enterprise platform that happens to use AI—not like an AI demo that happens to manage assets. Every module must be cloud-native, Python-first, analytics-driven, secure by design, and connected through real business workflows.**
