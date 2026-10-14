from fastapi import APIRouter, Depends

from restaurant_api.api.dependencies import get_food_type_service
from restaurant_api.schemas.domains import FoodTypeCreate, mongo_payload
from restaurant_api.services.food_types import FoodTypeService


router = APIRouter(prefix="/food-types", tags=["food types"])


@router.post("")
async def create_food_type(request: FoodTypeCreate, service: FoodTypeService = Depends(get_food_type_service)):
    return await service.create(mongo_payload(request))


@router.get("")
async def get_food_types(service: FoodTypeService = Depends(get_food_type_service)):
    return await service.list()
