import logging

from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi import HTTPException
from fastapi.responses import JSONResponse

from restaurant_api.core.exceptions import DomainError

logger = logging.getLogger("restaurant_api")


def register_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(DomainError)
    async def handle_domain_error(_: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"message": error.message})

    @app.exception_handler(RequestValidationError)
    async def handle_validation_error(_: Request, error: RequestValidationError) -> JSONResponse:
        return JSONResponse(status_code=422, content={"message": "Request validation failed", "errors": error.errors()})

    @app.exception_handler(HTTPException)
    async def handle_http_error(_: Request, error: HTTPException) -> JSONResponse:
        return JSONResponse(status_code=error.status_code, content={"message": error.detail})

    @app.exception_handler(Exception)
    async def handle_unexpected_error(request: Request, error: Exception) -> JSONResponse:
        logger.exception("Unhandled exception for %s %s", request.method, request.url.path, exc_info=error)
        return JSONResponse(status_code=500, content={"message": "Internal server error"})
