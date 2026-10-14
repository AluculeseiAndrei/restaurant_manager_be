from typing import Any

from restaurant_api.core.exceptions import DomainError
from restaurant_api.core.security import hash_password
from restaurant_api.repositories.restaurant import object_id, public_document


class AsyncEmployeeRepository:
    def __init__(self, database) -> None:
        self.employers, self.users = database["employers"], database["user"]

    async def create(self, data: dict[str, Any]) -> dict[str, Any]:
        if not await self.users.find_one({"_id": object_id(data["user_id"], "user ID"), "role": "admin"}): raise DomainError("The restaurant owner does not exist", 404)
        if await self.users.find_one({"email": data["email"]}): raise DomainError("The email is already used", 409)
        password = hash_password(data["password"])
        employee = {"name": data["name"], "email": data["email"], "password": password, "role": data["role"], "salary": data["salary"], "birthdate": data["birthdate"], "userId": data["user_id"], "description": data.get("description")}
        employee["_id"] = (await self.employers.insert_one(employee)).inserted_id
        await self.users.insert_one({"email": data["email"], "password": password, "role": "waiter", "income": 0, "adminId": data["user_id"]})
        return public_document(employee) or {}

    async def list(self, user_id):
        items = [public_document(i) or {} for i in await self.employers.find({"userId": user_id}).to_list()]
        if not items: raise DomainError("Employees not found", 404)
        return items

    async def get(self, user_id, employee_id):
        item = await self.employers.find_one({"_id": object_id(employee_id, "employee ID"), "userId": user_id})
        if not item: raise DomainError("Employee not found", 404)
        return public_document(item) or {}

    async def delete(self, user_id, employee_id):
        item = await self.employers.find_one({"_id": object_id(employee_id, "employee ID"), "userId": user_id})
        if not item: raise DomainError("Employee not found", 404)
        await self.employers.delete_one({"_id": item["_id"]}); await self.users.delete_one({"email": item["email"], "adminId": user_id})

    async def update(self, user_id, employee_id, data):
        employee = await self.employers.find_one({"_id": object_id(employee_id, "employee ID"), "userId": user_id})
        if not employee: raise DomainError("Employee not found", 404)

        new_email = data.get("email", employee["email"])
        if new_email != employee["email"] and await self.users.find_one({"email": new_email}):
            raise DomainError("The email is already used", 409)

        user_updates: dict[str, Any] = {}
        if new_email != employee["email"]:
            user_updates["email"] = new_email
        if "password" in data:
            password = hash_password(data["password"])
            data["password"] = password
            user_updates["password"] = password

        await self.employers.update_one({"_id": employee["_id"]}, {"$set": data})
        if user_updates:
            await self.users.update_one({"email": employee["email"], "adminId": user_id}, {"$set": user_updates})

    async def income(self, user_id, employee_id, value):
        result = await self.employers.update_one({"_id": object_id(employee_id, "employee ID"), "userId": user_id}, {"$inc": {"income": value}})
        if not result.matched_count: raise DomainError("Employee not found", 404)

    async def by_email(self, email):
        item = await self.employers.find_one({"email": email})
        if not item: raise DomainError("Employee not found", 404)
        return [public_document(item) or {}]
