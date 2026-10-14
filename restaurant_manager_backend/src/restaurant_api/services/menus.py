from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import MenuRepository


class MenuService:
    def __init__(self, repository: MenuRepository) -> None:
        self.repository = repository

    async def add(self, data, restaurant_id):
        if not data.get("name", "").strip(): raise DomainError("Product name is required", 422)
        if data.get("price", 0) <= 0: raise DomainError("Product price must be positive", 422)
        data = {**data, "name": data["name"].strip().lower()}
        return await self.repository.add(data, restaurant_id)

    async def list(self, restaurant_id, page, food_type=None, sort="name", direction="asc"):
        if page < 1: raise DomainError("Page must be positive", 422)
        return await self.repository.list(restaurant_id, page, food_type, sort, direction)

    async def delete(self, product_id):
        return await self.repository.delete(product_id)

    async def update(self, product_id, data):
        if data.get("price", 1) <= 0: raise DomainError("Product price must be positive", 422)
        return await self.repository.update(product_id, {**data, "name": data["name"].strip().lower()})

    async def search(self, restaurant_id, name, food_type=None, sort="name", direction="asc"):
        return await self.repository.search(restaurant_id, name.strip(), food_type, sort, direction)
