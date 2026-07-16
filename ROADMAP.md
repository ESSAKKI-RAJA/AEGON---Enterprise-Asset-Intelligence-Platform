# AEGON Roadmap

This document outlines the planned development trajectory of the AEGON Enterprise Asset Intelligence Platform. Items are organized by delivery horizon. All timelines are indicative and subject to change based on priorities and community feedback.

---

## Near Term (Q3 2026)

- **Kubernetes Helm Charts**: Production-ready Helm charts for deploying all AEGON services (API, Workers, Frontend proxy) to any Kubernetes cluster.
- **Celery Worker Hardening**: Dead-letter queues, task retry policies with exponential backoff, and observability dashboards for the RabbitMQ broker.
- **Asset Import Pipeline**: Bulk asset creation via CSV/Excel upload, processed asynchronously by Celery workers.
- **Notification System**: Email and in-app notifications triggered by critical AI alerts (e.g., asset failure predictions, critical defect detection).
- **OpenAPI Client SDK**: Auto-generated TypeScript and Python SDK from the FastAPI OpenAPI schema.

---

## Mid Term (Q4 2026 — Q1 2027)

- **Real Computer Vision Integration**: Connect the Enterprise Vision Intelligence module to live RTSP streams using production-grade OpenCV pipelines and GPU-accelerated YOLO inference.
- **Predictive Maintenance (ML)**: Ship the trained XGBoost failure prediction model using historical maintenance and telemetry data. Confidence scores and SHAP explanations will surface in the Maintenance module.
- **Demand Forecasting (Prophet)**: Inventory demand forecasting using Prophet for time-series modelling, driving automated reorder-point recommendations.
- **Multi-Tenant Architecture**: Full data isolation per tenant via PostgreSQL RLS policies and tenant-scoped API tokens.
- **GraphQL Gateway**: Expose a GraphQL interface alongside REST for flexible client querying of analytical and asset data.

---

## Long Term (2027)

- **Executive Copilot (RAG + LLM)**: Ship the Retrieval-Augmented Generation engine that allows executives to ask natural language questions grounded in live enterprise data (asset history, maintenance logs, financial records).
- **IoT Device Registry**: First-class support for registering, authenticating, and managing IoT edge devices that stream telemetry into the Digital Twin module.
- **Digital Twin Simulation**: Physics-informed simulation layer that can model asset degradation under hypothetical load conditions before applying changes to production assets.
- **Enterprise SSO**: SAML 2.0 and OIDC integration for enterprise identity providers (Okta, Azure AD, Google Workspace).
- **Mobile Application**: React Native companion app for field technicians to capture images, receive maintenance assignments, and update asset status in real time.

---

## Future Capabilities

- **Federated Learning**: Train ML models on distributed edge data without centralizing sensitive telemetry — particularly relevant for regulated industries.
- **Digital Thread**: Complete lifecycle traceability linking procurement orders, installation records, maintenance events, and decommissioning — forming an unbroken audit trail per asset.
- **Third-Party ERP Integrations**: Native connectors to SAP, Oracle ERP, and Maximo to enable bidirectional data flow with existing enterprise systems.
