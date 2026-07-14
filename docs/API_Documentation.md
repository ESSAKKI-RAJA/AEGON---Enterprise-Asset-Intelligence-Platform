# API Documentation

## Overview
The AEGON API is built with FastAPI and follows RESTful principles, providing a comprehensive interface for managing enterprise assets, maintenance, procurement, and advanced AI-driven analytics.

## Base URL
`/api/v1`

## Authentication
All protected endpoints require a Bearer token sent in the `Authorization` header.
- **Format:** `Authorization: Bearer <JWT_TOKEN>`

## Core Modules

### 1. Auth (`/auth`)
- `POST /auth/login` - Authenticate user and issue JWT.
- `POST /auth/refresh` - Refresh an expired access token.
- `GET /auth/me` - Retrieve current user profile.

### 2. Assets (`/assets`)
- `GET /assets` - List all assets with pagination and filtering.
- `GET /assets/{id}` - Retrieve details for a specific asset.
- `POST /assets` - Create a new asset registry entry.
- `PUT /assets/{id}` - Update asset details.

### 3. Maintenance (`/maintenance`)
- `GET /maintenance/plans` - Retrieve preventative maintenance schedules.
- `GET /maintenance/work-orders` - List active and historical work orders.
- `POST /maintenance/work-orders` - Create a new work order.

### 4. AI & Analytics (`/ai`, `/analytics`)
- `GET /ai/recommendations` - Retrieve prioritized AI-driven operational recommendations.
- `GET /ai/health-scores` - Fetch real-time predictive health scores for critical assets.
- `GET /analytics/dashboards/executive` - Retrieve high-level KPIs and financial roll-ups for executive dashboards.

## Standardized Responses
Every endpoint returns a standardized standard JSON structure:
```json
{
  "success": true,
  "message": "Operation successful",
  "data": { ... },
  "meta": { "page": 1, "total": 100 }
}
```

## Error Handling
Errors return standard HTTP status codes (e.g., 400, 401, 403, 404, 500) and a structured payload:
```json
{
  "success": false,
  "message": "Detailed error message",
  "error_code": "RESOURCE_NOT_FOUND"
}
```
