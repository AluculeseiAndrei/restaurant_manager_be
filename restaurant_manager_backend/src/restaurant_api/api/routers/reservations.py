from fastapi import APIRouter, Depends

from restaurant_api.api.dependencies import get_reservation_service, require_reservation_creator, require_table_staff
from restaurant_api.schemas.domains import ReservationCreate, ReservationUpdate, mongo_payload
from restaurant_api.services.reservations import ReservationService


router = APIRouter(tags=["reservations"])


@router.post("/tables/{table_id}/reservations", status_code=201)
async def create_reservation(table_id: str, request: ReservationCreate, service: ReservationService = Depends(get_reservation_service), actor: dict = Depends(require_reservation_creator)):
    data = mongo_payload(request)
    data["clientId"] = actor["id"]
    return await service.create(table_id, data)


@router.get("/tables/{table_id}/reservations")
async def get_reservations(table_id: str, service: ReservationService = Depends(get_reservation_service), _: dict = Depends(require_table_staff)):
    return await service.for_table(table_id)


@router.patch("/tables/{table_id}/reservations/{reservation_id}")
async def update_reservation(table_id: str, reservation_id: str, request: ReservationUpdate, service: ReservationService = Depends(get_reservation_service), _: dict = Depends(require_table_staff)):
    await service.update(table_id, reservation_id, mongo_payload(request))
    return {"message": "Reservation updated successfully"}


@router.delete("/tables/{table_id}/reservations/{reservation_id}")
async def delete_reservation(table_id: str, reservation_id: str, service: ReservationService = Depends(get_reservation_service), _: dict = Depends(require_table_staff)):
    await service.delete(table_id, reservation_id)
    return {"message": "Reservation cancelled successfully"}
