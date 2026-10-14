from typing import Any

from bson import ObjectId

from restaurant_api.core.exceptions import DomainError


class AsyncMongoUserRepository:
    def __init__(self, collection) -> None: self._collection = collection

    async def find_by_email(self, email: str) -> dict[str, Any] | None:
        return await self._collection.find_one({"email": email})

    async def find_by_id(self, user_id: str) -> dict[str, Any] | None:
        if not ObjectId.is_valid(user_id): return None
        return await self._collection.find_one({"_id": ObjectId(user_id)})

    async def create(self, document: dict[str, Any]) -> str:
        result = await self._collection.insert_one(document)
        return str(result.inserted_id)

    async def find_all(self) -> list[dict[str, Any]]:
        return await self._collection.find().to_list()

    async def delete(self, user_id: str) -> None:
        if not ObjectId.is_valid(user_id): raise DomainError("User not found", 404)
        result = await self._collection.delete_one({"_id": ObjectId(user_id)})
        if not result.deleted_count: raise DomainError("User not found", 404)

    async def admin_id_for_user(self, user_id: str) -> str:
        user = await self.find_by_id(user_id)
        if user is None: raise DomainError("User not found", 404)
        employer = await self._collection.database["employers"].find_one({"email": user["email"]})
        if employer is None: raise DomainError("Admin not found", 404)
        return employer["userId"]

    async def employee_for_user(self, user: dict[str, Any]) -> dict[str, Any] | None:
        return await self._collection.database["employers"].find_one({"email": user.get("email")})
