from fastapi import APIRouter, Depends

from restaurant_api.api.dependencies import get_product_service, require_product_staff, require_table_staff
from restaurant_api.api.dependencies import get_current_user
from restaurant_api.schemas.domains import ProductCreate, mongo_payload
from restaurant_api.services.products import ProductService


router = APIRouter(prefix="/tables", tags=["ordered products"])


@router.post("/{table_id}/products", status_code=201)
async def add_product(request: ProductCreate, table_id: str, service: ProductService = Depends(get_product_service), user: dict = Depends(require_table_staff)):
    data = mongo_payload(request)
    data["table_id"] = table_id
    return await service.add(data, user["id"])


@router.delete("/products/{product_id}")
async def delete_product(product_id: str, service: ProductService = Depends(get_product_service), _: dict = Depends(require_product_staff)):
    await service.delete(product_id)
    return {"message": "Product deleted successfully"}
