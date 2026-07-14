# Known Limitations

While AEGON is a highly capable Enterprise Asset Intelligence Platform, certain design constraints and known limitations exist in the current version (v1.0).

## 1. Offline Mode
- The current application relies on real-time data from the backend. Complete offline functionality for field engineers (e.g., executing work orders without network connectivity) is not fully supported. TanStack Query will cache previous states, but mutations require a connection.

## 2. Multi-Tenancy
- AEGON is currently designed as a single-tenant enterprise deployment. While departments and locations exist to logically separate data, true database-level tenant isolation (Row-Level Security or separate schemas) is not natively implemented for SaaS distribution.

## 3. Real-Time WebSockets
- While the architecture supports WebSockets, not all dashboard elements currently utilize them. Metrics and AI health scores rely on polling or TanStack Query invalidations.

## 4. Third-Party Integrations
- Out-of-the-box integrations with legacy ERP systems (SAP, Oracle) require custom ETL pipelines. The `Enterprise API Platform` exposes endpoints, but a dedicated integration middleware is needed to sync data automatically.
