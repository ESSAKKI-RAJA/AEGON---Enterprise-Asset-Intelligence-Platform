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
