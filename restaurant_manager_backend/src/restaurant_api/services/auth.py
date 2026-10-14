from restaurant_api.core.config import Settings
from restaurant_api.core.exceptions import DomainError
from restaurant_api.core.security import create_access_token, verify_password
from restaurant_api.interfaces.repositories.user_repository import UserRepository


class AuthenticationService:
    def __init__(self, users: UserRepository, settings: Settings) -> None:
        self._users = users
        self._settings = settings

    async def login(self, username: str, password: str) -> dict[str, str]:
        user = await self._users.find_by_email(username)
        if user is None or not verify_password(password, user.get("password", "")):
            raise DomainError("Wrong username or password", 401)
        token = create_access_token(str(user["_id"]), self._settings)
        return {"Authentication successful": token}
