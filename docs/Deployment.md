# Deployment Guide

AEGON is designed to be cloud-native and infrastructure-agnostic, easily deployable to any environment supporting containerized workloads.

## Containerization

The repository contains `Dockerfiles` for both the frontend and backend services.

- **Backend (`python:3.12-slim`)**: The FastAPI application is bundled with Uvicorn. For production, multiple Uvicorn workers should be managed via Gunicorn or through Kubernetes replica sets.
- **Worker (`python:3.12-slim`)**: A separate container instance running the Celery worker process.
- **Frontend (`node:20-alpine`)**: The React application is built via Vite and served using Nginx for high-throughput static asset delivery.

## Kubernetes (EKS/AKS/GKE)

For enterprise deployments, Kubernetes is the recommended orchestration platform.

- **Helm Charts**: (Coming Soon) Infrastructure configurations, including horizontal pod autoscalers (HPA) and resource limits, will be defined via Helm.
- **Stateful Sets**: While the application pods are strictly stateless, databases (if not using hosted Supabase), Redis, and RabbitMQ can be deployed as StatefulSets, though managed cloud variants (Elasticache, Amazon MQ) are highly recommended.

## Infrastructure as Code (Terraform)

All underlying cloud resources should be provisioned via Terraform to guarantee reproducible environments. This includes:
- IAM Roles and Policies
- VPC Networking and Subnets
- Managed PostgreSQL (Supabase) configurations
- Kubernetes cluster provisioning

## Continuous Integration and Delivery (CI/CD)

Deployments are automated through GitHub Actions.

1. **Pull Requests**: Code is linted (`ruff`, `eslint`), type-checked (`mypy`, `tsc`), and tested (`pytest`, `vitest`).
2. **Merge to Main**: Triggers a container build. Images are tagged with the Git SHA and pushed to the container registry.
3. **Deployment**: An ArgoCD (GitOps) controller detects the new image tag in the deployment repository and seamlessly rolls out the new pods to the cluster without downtime.
