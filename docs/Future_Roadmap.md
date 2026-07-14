# Future Roadmap

The AEGON platform is continuously evolving. The following features and architectural improvements are planned for future releases.

## Q3 2026 - Mobile & Field Operations
- **Native Field App:** A React Native port of the frontend targeted at maintenance engineers on iOS and Android devices, featuring barcode scanning, offline mode, and push notifications.
- **Geospatial Asset Tracking:** Integration with GIS for real-time tracking of mobile assets across large campus environments.

## Q4 2026 - Advanced AI & Digital Twins
- **Digital Twin Integration:** 3D rendering of complex assets and buildings, overlaying live sensor telemetry and health scores directly onto the models.
- **Generative AI Copilot v2:** Upgrading the Executive Copilot to interact directly with the database via natural language to SQL (NL2SQL) for ad-hoc custom reporting.

## Q1 2027 - Enterprise Integrations & IoT
- **IoT Edge Gateway:** Direct ingestion from industrial IoT sensors (MQTT) into a time-series database (TimescaleDB or InfluxDB), bypassing the standard REST API for massive high-frequency data streams.
- **Native SAP/Oracle Connectors:** Pre-built, bidirectional synchronization plugins for enterprise ERPs.

## Ongoing Architectural Refinements
- **GraphQL Federation:** Transitioning complex analytical read operations to a GraphQL endpoint to allow the frontend to specify exactly what nested relational data it needs, further reducing over-fetching.
- **Event-Driven Architecture (Kafka):** Shifting from synchronous HTTP inter-service communication to asynchronous event streams for audit logging and AI retraining pipelines.
