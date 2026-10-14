from fastapi import APIRouter, Depends, status

from restaurant_api.api.dependencies import get_client_service, require_client
from restaurant_api.schemas.domains import ClientCreate, ClientLocationUpdate, ReviewCreate, mongo_payload
from restaurant_api.services.clients import ClientService


router = APIRouter(tags=["clients"])


@router.get("/restaurants/{restaurant_id}/reviews")
async def get_reviews(restaurant_id: str, service: ClientService = Depends(get_client_service)):
    return await service.reviews_for(restaurant_id)


@router.get("/restaurants")
async def get_restaurants(county: str | None = None, location: str | None = None, name: str | None = None, service: ClientService = Depends(get_client_service)):
    return await service.restaurants(county, location, name)


@router.post("/restaurants/{restaurant_id}/reviews", status_code=status.HTTP_201_CREATED)
async def post_review(restaurant_id: str, request: ReviewCreate, service: ClientService = Depends(get_client_service), client: dict = Depends(require_client)):
    data = mongo_payload(request)
    data["restaurant_id"] = restaurant_id
    data["client_id"] = client["id"]
    return await service.add_review(data)


@router.post("/clients", status_code=status.HTTP_201_CREATED)
async def create_client(request: ClientCreate, service: ClientService = Depends(get_client_service)):
    return {"User id": await service.create(mongo_payload(request))}


@router.patch("/clients/{client_id}/location")
async def update_client_location(client_id: str, request: ClientLocationUpdate, service: ClientService = Depends(get_client_service), client: dict = Depends(require_client)):
    if client_id != client["id"]:
        from fastapi import HTTPException
        raise HTTPException(status_code=403, detail="You can update only your own location")
    data = mongo_payload(request)
    data["client_id"] = client_id
    return await service.update_location(data)
