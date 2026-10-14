from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import ClientRepository


class ClientService:
    def __init__(self, repository: ClientRepository) -> None:
        self.repository = repository

    async def create(self, data: dict) -> str:
        if not data.get("username") or not data.get("password"):
            raise DomainError("Email and password are required", 422)
        return await self.repository.create(data)

    async def restaurants(self, county=None, location=None, name=None):
        return await self.repository.restaurants(county, location, name)

    async def reviews_for(self, restaurant_id: str):
        return await self.repository.reviews_for(restaurant_id)

    async def add_review(self, data: dict):
        rating = data.get("rating")
        if rating is None or not 1 <= rating <= 5:
            raise DomainError("Rating must be between 1 and 5", 422)
        if not data.get("recension", "").strip():
            raise DomainError("Review text is required", 422)
        return await self.repository.add_review(data)

    async def update_location(self, data: dict):
        if not data.get("location") or not data.get("county"):
            raise DomainError("Location and county are required", 422)
        return await self.repository.update_location(data)
