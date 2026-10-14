from typing import Any

from restaurant_api.repositories.table_maps import TableMapRepository


class TableMapService:
    def __init__(self, repository: TableMapRepository) -> None:
        self.repository = repository

    async def get(self, restaurant_id: str): return await self.repository.get(restaurant_id)
    async def update(self, restaurant_id: str, data: dict[str, Any]): return await self.repository.update(restaurant_id, data)
