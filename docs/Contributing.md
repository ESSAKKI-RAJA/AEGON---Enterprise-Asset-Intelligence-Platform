# Local Development Setup

This guide details how to configure your local machine to contribute to the AEGON platform.

## Prerequisites

- **Python**: 3.12 or higher.
- **Node.js**: 20 or higher.
- **Docker**: For running local instances of Redis and RabbitMQ.
- **Git**: For version control.

## 1. Local Infrastructure

While you can connect to a hosted Supabase instance for the database, you will need Redis and RabbitMQ running locally for the caching and background worker tiers.

```bash
# Start Redis
docker run -d -p 6379:6379 --name aegon-redis redis:7-alpine

# Start RabbitMQ
docker run -d -p 5672:5672 -p 15672:15672 --name aegon-rabbitmq rabbitmq:3-management-alpine
```

## 2. Backend Setup

The backend is built with FastAPI and requires a virtual environment.

```bash
cd backend
python -m venv venv

# Activate on Windows
venv\Scripts\activate
# Activate on Unix/MacOS
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
# If pyproject.toml is configured, you may use poetry or pip install -e .
```

### Database Configuration

Copy the example environment variables:
```bash
cp .env.example .env
```
Ensure your `DATABASE_URL` is pointed at your development Supabase instance.

Run database migrations to ensure your local schema is up to date:
```bash
alembic upgrade head
```

### Running the Server

```bash
uvicorn app.main:app --reload --port 8000
```
The API documentation will be available at `http://localhost:8000/docs`.

## 3. Frontend Setup

The frontend is a React application built with Vite.

```bash
cd frontend
npm install

# Configure environment variables
cp .env.example .env
```

Start the development server:
```bash
npm run dev
```

## 4. Running Tests

Before submitting a pull request, you must ensure all tests pass.

```bash
# Backend Tests
cd backend
pytest

# Frontend Tests
cd frontend
npm run test
```

Please refer to the root `CONTRIBUTING.md` for our workflow and architectural rules.
