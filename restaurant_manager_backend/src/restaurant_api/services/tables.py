from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import TableRepository


class TableService:
    def __init__(self, repository: TableRepository) -> None: self.repository = repository
    async def create(self, data, restaurant_id):
        if not data.get("name", "").strip(): raise DomainError("Table name is required", 422)
        if data.get("capacity") is not None and data["capacity"] <= 0: raise DomainError("Table capacity must be positive", 422)
        return await self.repository.create(data, restaurant_id)
    async def list(self, restaurant_id, page):
        if page < 1: raise DomainError("Page must be positive", 422)
        return await self.repository.list(restaurant_id, page)
    async def get(self, table_id): return await self.repository.get(table_id)
    async def delete(self, table_id): return await self.repository.delete(table_id)
    async def reset(self, table_id): return await self.repository.reset(table_id)
    async def search(self, restaurant_id, name): return await self.repository.search(restaurant_id, name.strip())
