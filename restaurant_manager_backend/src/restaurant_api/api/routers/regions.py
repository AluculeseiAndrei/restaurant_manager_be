from fastapi import APIRouter, Depends

from restaurant_api.repositories.regions import JsonRegionRepository


router = APIRouter(prefix="/locations", tags=["locations"])


def get_region_repository() -> JsonRegionRepository:
    return JsonRegionRepository()


@router.get("/counties")
async def get_counties(repository: JsonRegionRepository = Depends(get_region_repository)) -> list[str]:
    return repository.counties()


@router.get("/{county}/cities")
async def get_cities(county: str, repository: JsonRegionRepository = Depends(get_region_repository)) -> list[str]:
    return repository.cities(county)
