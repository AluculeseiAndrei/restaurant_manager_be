from fastapi import APIRouter, Depends, Query

from restaurant_api.api.dependencies import get_menu_service, require_owner_for_admin, require_menu_owner
from restaurant_api.schemas.domains import MenuProductCreate, mongo_payload
from restaurant_api.services.menus import MenuService


router = APIRouter(tags=["menu"])


@router.post("/restaurants/{admin_id}/menu", status_code=201)
async def add_menu_product(request: MenuProductCreate, admin_id: str, service: MenuService = Depends(get_menu_service), _: dict = Depends(require_owner_for_admin)):
    return await service.add(mongo_payload(request), admin_id)


@router.get("/restaurants/{admin_id}/menu")
async def get_menu_products(admin_id: str, page: int = 1, food_type: str | None = None, sort: str = Query("name"), direction: str = Query("asc"), service: MenuService = Depends(get_menu_service)):
    return await service.list(admin_id, page, food_type, sort, direction)


@router.delete("/menu-products/{product_id}")
async def delete_menu_product(product_id: str, service: MenuService = Depends(get_menu_service), _: dict = Depends(require_menu_owner)):
    await service.delete(product_id)
    return {"Message": "Product deleted successfully"}


@router.patch("/menu-products/{product_id}")
async def update_menu_product(product_id: str, request: MenuProductCreate, service: MenuService = Depends(get_menu_service), _: dict = Depends(require_menu_owner)):
    await service.update(product_id, mongo_payload(request))
    return {"message": "Product updated successfully"}


@router.get("/restaurants/{admin_id}/menu/search")
async def search_menu_product(admin_id: str, product_name: str, food_type: str | None = None, sort: str = Query("name"), direction: str = Query("asc"), service: MenuService = Depends(get_menu_service)):
    return await service.search(admin_id, product_name, food_type, sort, direction)
