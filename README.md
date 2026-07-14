<p align="center">
  <img src="docs/aegon-logo.svg" alt="AEGON" width="80" />
</p>

# AEGON

<p align="center"><strong>Enterprise Intelligence Platform for Asset-Centric Operations</strong></p>
<p align="center"><em>Enterprise Evaluation Edition (v5.0.0)</em></p>

<p align="center">
  <a href="#executive-summary"><img src="https://img.shields.io/badge/Status-Enterprise_Evaluation-blue?style=for-the-badge" alt="Status" /></a>
  <a href="#machine-learning"><img src="https://img.shields.io/badge/Intelligence-ML_%2B_AI-indigo?style=for-the-badge" alt="AI" /></a>
  <a href="#technical-stack"><img src="https://img.shields.io/badge/Architecture-Python_First-yellow?style=for-the-badge" alt="Architecture" /></a>
</p>

---

## Executive Summary

AEGON is a comprehensive **Enterprise Intelligence Platform** designed to solve complex operational challenges in asset-intensive industries (Manufacturing, Energy, Logistics, Utilities). 

While traditional Enterprise Asset Management (EAM) and ERP systems function as reactive systems of record, AEGON operates as a **proactive system of intelligence**. It bridges the gap between raw machine data, maintenance operations, procurement, and executive financial planning.

By combining Machine Learning, Business Analytics, and a Digital Twin architecture, AEGON transforms siloed operational data into **Decision Intelligence**—delivering executive-level visibility and actionable, AI-driven recommendations across the enterprise.

This repository is an **Enterprise Evaluation Edition**, built to demonstrate production-grade software engineering, advanced system architecture, and enterprise UX to technical leaders, product managers, and academic reviewers.

---

## Why AEGON Exists

Large enterprises face critical operational blind spots:

1. **Reactive Maintenance:** Equipment fails unexpectedly because maintenance is schedule-based, not condition-based, leading to millions in unplanned downtime.
2. **Disconnected Systems:** Procurement, inventory, maintenance, and finance operate in silos. A delayed part delivery doesn't automatically trigger a financial risk warning or maintenance schedule adjustment.
3. **Data Overload, Intelligence Deficit:** Sensors generate terabytes of telemetry, but operators lack the tooling to translate that data into prioritized actions.
4. **Poor Executive Visibility:** C-suite leaders rely on stale, aggregated reports rather than real-time operational truth.

**AEGON solves this** by centralizing the data, applying predictive models (to forecast failure and demand), and surfacing the insights through role-specific, action-oriented interfaces.

---

## Vision

AEGON is not just an Asset Management System; it is an **Enterprise Intelligence Platform**. 

Our vision is to move organizations along the maturity curve:
*From **Descriptive** (What happened?)*  
*To **Predictive** (What will happen?)*  
*To **Prescriptive** (What should we do?)*  
*Towards **Autonomous Operations** (The system optimizes itself).*

By leveraging a Digital Twin core, AEGON acts as the connective tissue for the enterprise—providing a unified operating picture that augments human decision-making at every level, from the shop floor to the boardroom.

---

## Product Philosophy

- **Business-First Engineering:** Every feature is tied to a measurable business KPI (e.g., reducing MTTR, optimizing EOQ, improving ROI).
- **Executive-First UX:** Complex data is distilled into clear, high-density, action-oriented dashboards. No fluff, no marketing metrics—just operational truth.
- **Human-Centered AI:** AI does not replace operators; it augments them. Every AI recommendation includes the underlying reasoning, confidence score, and data lineage (Explainable AI).
- **Enterprise Scalability:** Built on a decoupled, asynchronous, cloud-native architecture ready for massive scale.

---

## Enterprise Architecture

AEGON employs a decoupled, asynchronous, Clean Architecture, ensuring that business logic, ML pipelines, and data access remain strictly isolated.

```text
┌─────────────────────────────────────────────────────────────────────────┐
│                           FRONTEND LAYER (React 19)                     │
│  State: TanStack Query & Zustand | Routing: TanStack Router | UI: Tailwind │
├─────────────────────────────────────────────────────────────────────────┤
│                           API LAYER (FastAPI)                           │
│  RESTful & WebSockets | Pydantic Validation | Rate Limiting & Audit     │
├──────────────┬──────────────┬────────────────────────┬──────────────────┤
│   BUSINESS   │   ANALYTICS  │       ML ENGINE        │    AI COPILOT    │
│   SERVICES   │  KPI Engine  │ Predictive Maintenance │  NLP Interface   │
│ (DDD logic)  │ Trends & ROI │    Forecasting (EOQ)   │ Decision Support │
├──────────────┴──────────────┴────────────────────────┴──────────────────┤
│                          REPOSITORY LAYER                               │
│            SQLAlchemy 2.0 (Async) | Unit of Work Pattern                │
├─────────────────────────────────────────────────────────────────────────┤
│                          INFRASTRUCTURE LAYER                           │
│ PostgreSQL (Supabase) | Redis (Caching) | Celery/RabbitMQ (Workers)     │
└─────────────────────────────────────────────────────────────────────────┘
```

- **Frontend:** Pure presentation. It visualizes data and captures intent, entirely decoupled from business logic.
- **API:** A thin routing and validation layer. 
- **Services:** The core of the application where all domain rules live.
- **Background Workers:** Any operation taking >300ms (analytics aggregations, PDF generation, ML batch predictions) is offloaded to Celery.

---

## Technical Stack

| Component | Technology | Version | Purpose | Advantages / Tradeoffs |
|-----------|------------|---------|---------|------------------------|
| **Frontend UI** | React | 19.0 | Client-side rendering & component architecture | Unmatched ecosystem; requires disciplined state management. |
| **Data Fetching** | TanStack Query | 5.0 | Async state management & caching | Eliminates useEffect data fetching; steep learning curve. |
| **Styling** | Tailwind CSS | 4.0 | Utility-first styling & design tokens | Rapid iteration, consistent design system; dense markup. |
| **Backend** | FastAPI | 0.115 | High-performance async API | Python-native, auto-docs, fast; requires strict async hygiene. |
| **ORM** | SQLAlchemy | 2.0 | Asynchronous database interactions | Enterprise standard, powerful; complex relationship eager-loading. |
| **Database** | PostgreSQL | 15+ | Relational, ACID-compliant data store | Proven reliability, JSONB support; requires strict migrations. |
| **Cache & Queue** | Redis | 7.0 | KPI caching, session store, Celery broker | Blazing fast in-memory ops; volatile data requires persistence strategy. |
| **Workers** | Celery | 5.4 | Background job processing | Distributed task execution; adds infrastructure complexity. |

---

## Platform Modules

### Executive Dashboard
- **Objective:** Provide a real-time, top-down view of enterprise health and financial exposure.
- **Implementation:** Aggregates data across all modules via Redis-cached analytics endpoints. Features Recharts visualizations and AI-curated intelligence feeds.
- **KPIs:** Overall Asset Health, Financial Variance, Risk Exposure.

### Asset Registry
- **Objective:** Manage the full lifecycle and depreciation of physical and IT assets.
- **Implementation:** Hierarchical data models, soft-deletes, full audit trails (who changed what and when).
- **KPIs:** Total Value, Depreciation Rate, Utilization.

### Maintenance Intelligence
- **Objective:** Shift from reactive to predictive maintenance.
- **Implementation:** Work orders are generated and ranked dynamically based on ML failure risk scores rather than static schedules.
- **KPIs:** Mean Time To Repair (MTTR), Mean Time Between Failures (MTBF), Schedule Compliance.

### Inventory Optimization
- **Objective:** Ensure parts are available precisely when needed without overstocking.
- **Implementation:** Algorithms calculate Economic Order Quantity (EOQ) and dynamic reorder points based on historical consumption and lead times.
- **KPIs:** Stock Turnover, Stockout Risk, Holding Costs.

### Finance Intelligence
- **Objective:** Track CAPEX/OPEX and departmental budget variances in real-time.
- **Implementation:** Financial transaction ledgers tied directly to maintenance and procurement events.
- **KPIs:** Budget Variance, Maintenance Spend, ROI.

### Procurement
- **Objective:** Manage supplier relationships and track purchase orders.
- **Implementation:** Vendor ranking based on delivery performance and defect rates.
- **KPIs:** On-Time Delivery Rate, Spend per Vendor, Delivery Risk.

---

## Machine Learning & Advanced Analytics

AEGON is built Python-first to natively integrate data science and machine learning.

### Machine Learning
- **Predictive Maintenance:** Uses Scikit-learn and XGBoost to classify the probability of asset failure within the next 30 days based on usage telemetry and maintenance history.
- **Demand Forecasting:** Uses Prophet for time-series forecasting to predict future inventory demand and optimize EOQ.
- **Explainability:** Employs SHAP (SHapley Additive exPlanations) so operators understand *why* a machine is flagged for failure (e.g., "Temperature Anomaly: +15%").

### Business Analytics
- **Dynamic KPI Engine:** Computes complex aggregations (ROI, MTBF) dynamically and caches them in Redis for sub-50ms dashboard loads.
- **Cost Optimization:** Identifies systemic financial inefficiencies across facilities.

### Enterprise AI
- **Decision Support:** Generates prescriptive recommendations (e.g., "Expedite bearing delivery due to 89% failure probability on Asset X").
- **AEGON Copilot:** An interactive, context-aware interface allowing users to query enterprise data naturally.

### Digital Twin
- **Operational Awareness:** A real-time, digital representation of physical assets, allowing for simulation, health monitoring, and scenario analysis before physical execution.

---

## Enterprise Authentication Roadmap

> [!NOTE]
> **This repository intentionally ships WITHOUT authentication.**

The **Enterprise Evaluation Edition** is designed to allow reviewers, recruiters, and technical leaders to immediately evaluate the platform's business capabilities, architecture, and UX without the friction of account creation.

For production deployments, the platform is architected to integrate with enterprise Identity Providers (IdPs):

- **Clerk:** (Primary SaaS identity) SSO, B2B Organizations, RBAC.
- **Azure Active Directory (Entra ID):** Enterprise SAML/OIDC.
- **Okta / Auth0:** Workforce identity federation.
- **SCIM:** Automated user provisioning and de-provisioning.
- **Fine-Grained Authorization:** Attribute-Based Access Control (ABAC) ensuring users only see data within their organizational department.

*Authentication is infrastructure; this evaluation edition focuses on the product and intelligence.*

---

## Business Value

Deploying AEGON yields significant enterprise ROI:
- **Reduced Downtime:** Predictive alerts catch failures before they cascade.
- **Lower Maintenance Costs:** Eliminates unnecessary scheduled maintenance.
- **Optimized Capital Allocation:** Data-driven repair vs. replace decisions.
- **Operational Resilience:** Real-time visibility prevents localized issues from becoming systemic failures.

---

## Quick Start (Evaluation Mode)

Experience the platform locally in minutes.

### Prerequisites
- Node.js v20+
- Python 3.12+
- PostgreSQL 15+ (SQLite is used by default for zero-config evaluation)

### 1. Backend API
```bash
cd backend
python -m venv venv
# Windows: venv\Scripts\activate | macOS/Linux: source venv/bin/activate
pip install -r requirements.txt
alembic upgrade head
uvicorn app.main:app --reload --port 8000
```
*(Runs on http://127.0.0.1:8000)*

### 2. Frontend Application
```bash
cd frontend
npm install
npm run dev
```
*(Runs on http://127.0.0.1:5173)*

No login required. The application will open directly to the Executive Dashboard as the Enterprise Evaluation User.

---

## Future Vision & Roadmap

- **IoT Telemetry Streaming:** Integration with Apache Kafka for real-time edge sensor ingestion.
- **Generative AI & RAG:** Integrating Large Language Models with the corporate knowledge base (manuals, SOPs) for instant troubleshooting.
- **Graph Intelligence:** Mapping complex dependencies between assets, parts, and financial impact.
- **Autonomous Execution:** Shifting from human-in-the-loop to human-on-the-loop for routine procurement and scheduling.

---

## License

This software is released as an Enterprise Evaluation Portfolio piece. See [LICENSE](LICENSE) for details.

<p align="center">
  <em>Designed for decision intelligence. Built for the enterprise.</em>
</p>
