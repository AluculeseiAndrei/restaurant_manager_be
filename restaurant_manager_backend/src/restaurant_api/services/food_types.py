from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import FoodTypeRepository


class FoodTypeService:
    def __init__(self, repository: FoodTypeRepository) -> None: self.repository = repository
    async def create(self, data):
        if not data.get("type_name", "").strip(): raise DomainError("Food type is required", 422)
        return await self.repository.create({"type_name": data["type_name"].strip().lower()})
    async def list(self): return await self.repository.list()
