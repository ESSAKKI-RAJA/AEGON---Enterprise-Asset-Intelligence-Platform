# Deployment Guide

## Prerequisites
- **Node.js**: v20 or higher
- **Python**: 3.12 or higher
- **PostgreSQL**: 15 or higher
- **Redis**: 7.x (optional but recommended for caching)
- **Docker**: For containerized deployment

## 1. Local / Development Deployment

### Frontend
1. Navigate to the project root.
2. Install dependencies: `npm install`
3. Start the dev server: `npm run dev`
4. The application will be accessible at `http://localhost:8080` (or `http://localhost:5173`).

### Backend
1. Navigate to `backend/`.
2. Create virtual environment: `python -m venv venv`
3. Activate: `venv\Scripts\activate` (Windows) or `source venv/bin/activate` (Mac/Linux)
4. Install dependencies: `pip install -r requirements.txt`
5. Run migrations: `alembic upgrade head`
6. Start the server: `uvicorn app.main:app --reload --port 8000`

## 2. Docker Compose (Production)

A `docker-compose.prod.yml` file is provided for full-stack deployment.

1. Create a `.env` file at the root containing the necessary environment variables (Database URL, JWT Secret, etc.).
2. Build and start the containers:
   ```bash
   docker-compose -f docker-compose.prod.yml up -d --build
   ```
3. The platform is now running and routing traffic via the built-in Nginx/Traefik proxy (if configured), or directly exposing port 80/443.

## 3. Kubernetes Deployment

Helm charts and Kubernetes manifests are located in `backend/k8s`.

1. Apply ConfigMaps and Secrets:
   ```bash
   kubectl apply -f backend/k8s/secrets.yaml
   ```
2. Deploy the database and Redis instances.
3. Deploy the backend and frontend:
   ```bash
   kubectl apply -f backend/k8s/backend-deployment.yaml
   ```
4. Expose the services via Ingress rules.
