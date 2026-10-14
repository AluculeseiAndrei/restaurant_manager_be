# Dream Deluxe Restaurant API

Dream Deluxe is a restaurant-management backend built with FastAPI, asynchronous PyMongo, MongoDB, JWT authentication, and MongoDB GridFS for images.

## Current stage

The project is at a functional staging/internal-demo stage. It has been migrated from Flask to FastAPI and is organized around routers, services, repositories, interfaces, schemas, and core infrastructure.

Implemented:

- FastAPI application with `/api/v1` versioned routes.
- Asynchronous MongoDB access through one `AsyncMongoClient`.
- JWT login and role-aware authorization dependencies.
- Owner, waiter, and client access boundaries for restaurant operations.
- Explicit service classes, one service per file, with business validation.
- Global handling for domain, HTTP, validation, and unexpected errors.
- Restaurant, menu, table, order, reservation, employee, review, and floor-plan workflows.
- Revenue reporting using integer cents and decimal-string API output.
- MongoDB GridFS image storage with protected uploads and public reads.
- Live and MongoDB readiness health endpoints.
- Startup index creation and Docker Compose development environment.
- OpenAPI contract in [openapi.json](openapi.json).

The project is not yet a final production release. It still needs a complete integration/security test suite, production secret management, monitoring, rate limiting, formal deployment configuration, and a secure production password-reset workflow.

## Architecture

```text
HTTP request -> router -> service -> repository -> MongoDB
                         |
                         -> DomainError -> global error handler
```

- `api/routers`: HTTP concerns, dependency injection, and response contracts.
- `services`: business rules, validation, use cases, and orchestration.
- `repositories`: asynchronous persistence and MongoDB-specific queries.
- `interfaces`: repository and infrastructure contracts.
- `schemas`: Pydantic request and response models.
- `core`: configuration, security, database lifecycle, and exceptions.

## Roles and access

- `admin`: restaurant owner; manages the restaurant, menus, employees, floor plan, media, and reports.
- `waiter`: works only with tables and orders belonging to the assigned restaurant.
- `client`: can discover restaurants and menus publicly; authenticated clients can create reviews, reservations, and update their location.

## Running locally

Create `.env` from `.env.example` and set real values for `MONGO_URI` and `JWT_SECRET_KEY`.

```bash
pip install -r requirements.txt
uvicorn restaurant_api.main:app --app-dir src --reload
```

Documentation is available at `/docs`, `/redoc`, and `/openapi.json`.

## Running with Docker

```bash
docker compose up --build
```

The API runs at `http://localhost:8000`. The Compose configuration is for local development and must not be used unchanged in production.

## Testing

```bash
pip install -r requirements-dev.txt
pytest -q
```

## Future improvements

1. Add full integration tests for owner/waiter/client isolation, GridFS, revenue, and failure scenarios.
2. Complete production password reset with expiring one-time tokens, email delivery, rate limiting, and non-enumerating responses.
3. Add structured logging, metrics, tracing, alerting, and request correlation IDs.
4. Move secrets to a managed secret store and configure strict production CORS.
5. Add MongoDB backup/restore procedures, migration tooling, and deployment health checks.
6. Replace remaining floating-point operational money fields with Decimal128 or integer cents throughout the domain.
7. Add pagination, filtering, sorting, and consistent response models to all collection endpoints.
8. Add geospatial restaurant search using latitude/longitude and a MongoDB `2dsphere` index.
9. Add transaction boundaries for multi-document order, bill, employee-income, and sales-history updates.
10. Build the React/Tailwind frontend using [FRONTEND_AGENT_README.md](FRONTEND_AGENT_README.md) and [openapi.json](openapi.json).
