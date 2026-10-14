from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import ProductRepository


class ProductService:
    def __init__(self, repository: ProductRepository) -> None: self.repository = repository
    async def add(self, data, employee_id):
        if data.get("qty", 0) <= 0: raise DomainError("Quantity must be positive", 422)
        if data.get("price", 0) < 0: raise DomainError("Price cannot be negative", 422)
        return await self.repository.add(data, employee_id)
    async def delete(self, product_id): return await self.repository.delete(product_id)
