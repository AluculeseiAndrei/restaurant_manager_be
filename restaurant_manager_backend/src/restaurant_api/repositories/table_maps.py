from datetime import datetime, timezone
from typing import Any

from restaurant_api.core.exceptions import DomainError
from restaurant_api.repositories.restaurant import object_id, public_document


class TableMapRepository:
    def __init__(self, database) -> None: self.users, self.maps = database["user"], database["floorPlans"]

    async def get(self, restaurant_id: str) -> dict[str, Any]:
        user = await self.users.find_one({"_id": object_id(restaurant_id, "restaurant ID"), "role": "admin"})
        if not user: raise DomainError("Admin not found", 404)
        table_map = await self.maps.find_one({"restaurantId": restaurant_id})
        if not table_map: raise DomainError("Table map not found", 404)
        result = public_document(table_map) or {}; result["id"] = result.pop("_id", ""); return result

    async def update(self, restaurant_id: str, data: dict[str, Any]) -> dict[str, Any]:
        if not await self.users.find_one({"_id": object_id(restaurant_id, "restaurant ID"), "role": "admin"}): raise DomainError("Admin not found", 404)
        now = datetime.now(timezone.utc); current = await self.maps.find_one({"restaurantId": restaurant_id}, {"version": 1, "createdAt": 1})
        elements = [{**element, "id": str(element["id"])} for element in data.get("elements", [])]
        payload = {**data, "elements": elements, "restaurantId": restaurant_id, "version": (current or {}).get("version", 0) + 1, "updatedAt": now, "createdAt": (current or {}).get("createdAt", now)}
        await self.maps.update_one({"restaurantId": restaurant_id}, {"$set": payload}, upsert=True)
        return await self.get(restaurant_id)
