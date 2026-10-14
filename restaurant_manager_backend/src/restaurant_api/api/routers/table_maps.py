from fastapi import APIRouter, Depends

from restaurant_api.api.dependencies import require_owner
from restaurant_api.core.database import get_async_database
from restaurant_api.core.security import get_current_user_id
from restaurant_api.repositories.table_maps import TableMapRepository
from restaurant_api.schemas.table_maps import FloorPlanResponse, FloorPlanUpdate
from restaurant_api.services.table_maps import TableMapService


router = APIRouter(prefix="/restaurants", tags=["floor plans"])


async def get_floor_plan_service(database=Depends(get_async_database)) -> TableMapService:
    return TableMapService(TableMapRepository(database))


@router.put("/{restaurant_id}/floor-plan", response_model=FloorPlanResponse)
async def update_floor_plan(restaurant_id: str, request: FloorPlanUpdate, service: TableMapService = Depends(get_floor_plan_service), _: dict = Depends(require_owner)):
    return await service.update(restaurant_id, request.model_dump(by_alias=True))


@router.get("/{restaurant_id}/floor-plan", response_model=FloorPlanResponse)
async def get_floor_plan(restaurant_id: str, service: TableMapService = Depends(get_floor_plan_service), _: dict = Depends(require_owner)):
    return await service.get(restaurant_id)
