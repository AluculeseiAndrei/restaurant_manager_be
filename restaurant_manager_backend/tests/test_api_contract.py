import inspect
import os

os.environ.setdefault("MONGO_URI", "mongodb://localhost:27017")
os.environ.setdefault("JWT_SECRET_KEY", "test-secret")

from restaurant_api.main import app
from restaurant_api.repositories.restaurant import money_to_cents, public_document


def test_required_routes_are_documented():
    paths = app.openapi()["paths"]
    assert "/api/v1/health/live" in paths
    assert "/api/v1/health/ready" in paths
    assert "/api/v1/restaurants/{restaurant_id}/reports/revenue" in paths


def test_money_conversion_is_decimal_safe():
    assert money_to_cents("10.005") == 1001
    assert money_to_cents("12.50") == 1250


def test_public_documents_remove_secrets():
    result = public_document({"_id": "abc", "password": "secret", "code": 1234, "email": "a@example.com"})
    assert result == {"_id": "abc", "email": "a@example.com"}


def test_business_route_handlers_are_async():
    for route in app.routes:
        if route.path.startswith("/api/v1") and route.path not in {"/api/v1/health/live", "/api/v1/health/ready"}:
            assert inspect.iscoroutinefunction(route.endpoint), route.path
