from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import ReservationRepository


class ReservationService:
    def __init__(self, repository: ReservationRepository) -> None: self.repository = repository
    async def create(self, table_id, data):
        if data.get("guests") is not None and data["guests"] <= 0: raise DomainError("Guests must be positive", 422)
        if data.get("start_time") and data.get("end_time") and data["start_time"] >= data["end_time"]:
            raise DomainError("Reservation end time must be after start time", 422)
        return await self.repository.create(table_id, data)
    async def for_table(self, table_id): return await self.repository.for_table(table_id)
    async def update(self, table_id, reservation_id, data):
        if data.get("guests") is not None and data["guests"] <= 0: raise DomainError("Guests must be positive", 422)
        if data.get("start_time") and data.get("end_time") and data["start_time"] >= data["end_time"]: raise DomainError("Reservation end time must be after start time", 422)
        return await self.repository.update(table_id, reservation_id, data)
    async def delete(self, table_id, reservation_id): return await self.repository.delete(table_id, reservation_id)
