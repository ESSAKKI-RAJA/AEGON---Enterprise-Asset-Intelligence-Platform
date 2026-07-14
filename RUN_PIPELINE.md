# AEGON Run Pipeline

Welcome to the AEGON evaluation guide. This document contains everything necessary to start, test, and evaluate the AEGON repository.

## Repository Overview
AEGON is a comprehensive, production-ready AI-powered enterprise asset management and preventive operations platform. It features a robust Python/FastAPI backend with Machine Learning capabilities, and a modern React/TanStack frontend.

## Architecture Summary
- **Frontend**: React 19, Vite, TanStack Router/Query, TailwindCSS 4, Shadcn UI.
- **Backend**: Python 3.12, FastAPI, SQLAlchemy (PostgreSQL), Alembic for migrations.
- **ML/AI Layer**: Built-in pipelines for predictive maintenance.
- **Infrastructure**: Docker, Kubernetes (manifests provided), Redis caching.

## Database Migration
Ensure PostgreSQL is running. To initialize the database:
```bash
cd backend
python -m venv venv
venv\Scripts\activate
alembic upgrade head
```

## Redis Startup
Redis is recommended for caching and background tasks. You can run it via Docker:
```bash
docker run -d --name aegon-redis -p 6379:6379 redis:7
```

## Backend Startup
From the project root:
```bash
cd backend
venv\Scripts\activate
uvicorn app.main:app --reload --host 127.0.0.1 --port 8000
```
- **Swagger URL**: `http://127.0.0.1:8000/docs`

## Frontend Startup
From the project root:
```bash
cd frontend
npm install
npm run dev
```
- **Application URL**: `http://127.0.0.1:5173`

## Demo Credentials
- **Admin**: `admin@aegon.com` / `admin123`
- **Operator**: `operator@aegon.com` / `operator123`

## Validation Commands
To verify project health, you can run the following validation commands:
```bash
# Frontend
cd frontend
npm run lint
npx tsc --noEmit
npm run build

# Backend
cd backend
python -m pytest
```

## Project Structure
- `backend/` - FastAPI application, database schemas, ML pipelines.
- `frontend/` - React components, pages, TanStack router configuration.
- `docs/` - Extensive technical documentation.
- `scripts/` - Automation scripts for easy setup and running.
- `k8s/` (in backend) - Kubernetes deployment files.

## Future Roadmap
- Integration with external IoT sensors for real-time asset telemetry.
- Advanced ML models for predictive failure analysis.
- Expanded RBAC and audit logging.

## Expected Output
When running the full stack, you should see a modern, dynamic dashboard allowing you to manage assets, view analytics, and trigger ML predictions seamlessly.
