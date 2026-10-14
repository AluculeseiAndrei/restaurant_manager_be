from fastapi import APIRouter, Depends, status

from restaurant_api.api.dependencies import get_table_service, require_staff_for_admin, require_staff_for_user_id, require_table_staff
from restaurant_api.core.security import get_current_user_id
from restaurant_api.schemas.domains import TableCreate, mongo_payload
from restaurant_api.services.tables import TableService


router = APIRouter(tags=["tables"])


@router.post("/restaurants/{user_id}/tables", status_code=status.HTTP_201_CREATED)
async def create_table(request: TableCreate, user_id: str, service: TableService = Depends(get_table_service), _: dict = Depends(require_staff_for_user_id)):
    return {"Table id": await service.create(mongo_payload(request), user_id)}


@router.get("/restaurants/{user_id}/tables")
async def get_tables(user_id: str, page: int = 1, service: TableService = Depends(get_table_service), _: dict = Depends(require_staff_for_user_id)):
    return await service.list(user_id, page)


@router.get("/tables/{table_id}")
async def get_table(table_id: str, service: TableService = Depends(get_table_service), _: dict = Depends(require_table_staff)):
    return await service.get(table_id)


@router.delete("/tables/{table_id}")
async def delete_table(table_id: str, service: TableService = Depends(get_table_service), _: dict = Depends(require_table_staff)):
    await service.delete(table_id)
    return {"message": "Table and associated products deleted successfully"}


@router.post("/tables/{table_id}/reset")
async def reset_table(table_id: str, service: TableService = Depends(get_table_service), _: dict = Depends(require_table_staff)):
    await service.reset(table_id)
    return {"Message": "The table was reset successfully"}


@router.get("/restaurants/{admin_id}/tables/search")
async def search_tables(admin_id: str, table_name: str = "", service: TableService = Depends(get_table_service), _: dict = Depends(require_staff_for_admin)):
    return await service.search(admin_id, table_name)
