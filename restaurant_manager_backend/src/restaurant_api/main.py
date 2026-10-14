from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from restaurant_api.api.errors import register_exception_handlers
from restaurant_api.api.routers import (auth, charts, clients, employees, food_types, health, menu, products, regions,
                                         reservations, table_maps, tables, uploads, users)
from restaurant_api.core.config import get_settings
from restaurant_api.core.database import get_async_database_client


@asynccontextmanager
async def lifespan(_: FastAPI):
    await get_async_database_client().ensure_indexes()
    yield
    await get_async_database_client().close()
    get_async_database_client.cache_clear()


def create_app() -> FastAPI:
    settings = get_settings()
    app = FastAPI(title=settings.app_name, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=settings.allowed_origins,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    register_exception_handlers(app)
    api_prefix = "/api/v1"
    app.include_router(health.router, prefix=api_prefix)
    app.include_router(auth.router, prefix=api_prefix)
    app.include_router(users.router, prefix=api_prefix)
    app.include_router(regions.router, prefix=api_prefix)
    app.include_router(clients.router, prefix=api_prefix)
    app.include_router(tables.router, prefix=api_prefix)
    app.include_router(menu.router, prefix=api_prefix)
    app.include_router(products.router, prefix=api_prefix)
    app.include_router(reservations.router, prefix=api_prefix)
    app.include_router(food_types.router, prefix=api_prefix)
    app.include_router(table_maps.router, prefix=api_prefix)
    app.include_router(employees.router, prefix=api_prefix)
    app.include_router(charts.router, prefix=api_prefix)
    app.include_router(charts.restaurant_reports_router, prefix=api_prefix)
    app.include_router(charts.employee_router, prefix=api_prefix)
    app.include_router(uploads.router, prefix=api_prefix)
    return app


app = create_app()
