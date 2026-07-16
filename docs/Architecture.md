# Architecture Overview

AEGON is an Enterprise Asset Intelligence Platform built to handle the complexities of modern industrial and physical asset ecosystems. The architecture strictly adheres to Clean Architecture and Domain-Driven Design (DDD) principles.

## Core Architectural Rules

1. **Separation of Concerns**: The platform is strictly divided into Presentation (Frontend), Gateway (API), Domain (Services), and Infrastructure (Repositories).
2. **Deterministic UI**: The frontend must never hold business logic. It exists solely to capture user intent and visualize data.
3. **Database Isolation**: The database schema and connection pools are managed entirely within the Infrastructure layer. The API and Domain layers have no direct knowledge of SQL or connection drivers.
4. **Asynchronous by Default**: All I/O bound operations, including database queries, external API calls, and file operations, utilize Python's `async/await` paradigms.
5. **Event-Driven Offloading**: Any computational workload exceeding 300ms (e.g., PDF generation, heavy ML inference) is offloaded to an asynchronous task queue (Celery/RabbitMQ).

## Layer Definitions

### 1. Presentation Layer (Frontend)
Built with React 19 and TypeScript. The frontend communicates exclusively over HTTP/REST with the API Gateway. It maintains minimal local state and relies heavily on server state caching (TanStack Query). See [Frontend Design](Frontend.md) for details.

### 2. API Gateway (FastAPI)
The FastAPI application acts as the entry point for all external requests. It is responsible for:
- Route definitions and path parameters.
- Input validation via Pydantic.
- Enforcing security paradigms (JWT, RBAC).
- Injecting dependencies from the Domain layer.

### 3. Domain Layer (Services)
The Service Layer houses the core business logic of the AEGON platform. It defines the rules for asset maintenance, inventory tracking, predictive analytics, and computer vision workflows. Services are agnostic to the transport layer (HTTP) and the data storage mechanism (SQL).

### 4. Infrastructure Layer (Repositories & AI)
The Infrastructure layer provides implementations for interfaces defined by the Domain layer. This includes:
- SQLAlchemy repositories that execute raw SQL or ORM queries.
- Redis cache clients.
- External API integrations (e.g., Supabase Auth).
- Machine learning pipelines (OpenCV, Scikit-learn).

## Data Flow Pipeline

1. **Client Request**: A client makes an HTTP request to the FastAPI application.
2. **Validation & Security**: The API Gateway validates the request schema and verifies the JWT against Supabase Auth.
3. **Dependency Injection**: The routing function receives the necessary Service objects via the DI container.
4. **Business Logic Execution**: The Service object executes its internal logic. If data is needed, it calls methods on injected Repository objects.
5. **Data Access**: Repositories query the Supabase PostgreSQL database asynchronously and map the raw data back to Pydantic domain models.
6. **Response**: The Service returns the domain models to the API Gateway, which serializes them back to the client.

For a deeper dive into the system layout, refer to the [System Design](SystemDesign.md) document.
