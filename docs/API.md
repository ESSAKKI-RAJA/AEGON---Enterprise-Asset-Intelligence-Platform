# API Design Standards

The AEGON API Gateway provides a RESTful interface to the enterprise platform. 

## Base URL and Versioning

All API routes are mounted under a versioned prefix:
`/api/v1/...`

Future breaking changes will be deployed under `/api/v2/`, allowing legacy clients to migrate seamlessly.

## OpenAPI (Swagger) Documentation

Because the backend is built with FastAPI and strictly typed Pydantic models, interactive API documentation is auto-generated and guaranteed to be accurate.

In local development, visit:
`http://localhost:8000/docs`

## REST Guidelines

We adhere strictly to RESTful paradigms for routing and HTTP verbs.

- `GET /assets` - Retrieve a collection of assets.
- `GET /assets/{id}` - Retrieve a specific asset.
- `POST /assets` - Create a new asset.
- `PUT /assets/{id}` - Fully update an asset.
- `PATCH /assets/{id}` - Partially update an asset.
- `DELETE /assets/{id}` - Soft-delete an asset.

### Pagination

Any collection endpoint returning potentially large datasets MUST implement pagination.
- We utilize limit/offset or cursor-based pagination depending on the entity size.
- Example: `GET /assets?limit=50&offset=100`

### Error Handling

The API will never return raw internal server exceptions (HTML traces).
All errors are caught by global exception handlers and serialized into a standard JSON format:

```json
{
  "error": {
    "code": "ASSET_NOT_FOUND",
    "message": "The requested asset UUID does not exist.",
    "details": null
  }
}
```
Standard HTTP status codes are strictly enforced (e.g., `400` Bad Request, `401` Unauthorized, `403` Forbidden, `404` Not Found, `422` Unprocessable Entity).
