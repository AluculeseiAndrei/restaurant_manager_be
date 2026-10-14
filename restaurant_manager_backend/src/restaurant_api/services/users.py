from restaurant_api.core.exceptions import DomainError
from restaurant_api.core.security import hash_password
from restaurant_api.interfaces.repositories.user_repository import UserRepository


class UserService:
    def __init__(self, users: UserRepository) -> None:
        self._users = users

    async def create_user(self, data: dict) -> str:
        if await self._users.find_by_email(data["username"]):
            raise DomainError("User already exists", 409)
        document = {
            "email": data["username"],
            "password": hash_password(data["password"]),
            "role": "admin",
            "companyName": data.get("company_name"),
            "companyAddress": data.get("company_address"),
            "companyPhone": data.get("company_phone"),
            "location": data.get("location"),
            "county": data.get("county"),
        }
        return await self._users.create(document)
