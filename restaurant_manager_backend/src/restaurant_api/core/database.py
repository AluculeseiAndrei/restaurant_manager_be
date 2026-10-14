from collections.abc import AsyncGenerator
from functools import lru_cache

from pymongo import AsyncMongoClient

from restaurant_api.core.config import Settings, get_settings


class AsyncDatabaseClient:
    """Owns the asynchronous MongoDB client lifecycle."""

    def __init__(self, settings: Settings) -> None:
        self._client = AsyncMongoClient(settings.mongo_uri)
        self.database = self._client[settings.mongo_database]

    async def close(self) -> None:
        await self._client.close()

    async def ping(self) -> None:
        await self._client.admin.command("ping")

    async def ensure_indexes(self) -> None:
        await self.database["user"].create_index("email", unique=True)
        await self.database["employers"].create_index([("userId", 1), ("email", 1)])
        await self.database["table"].create_index("userId")
        await self.database["menu"].create_index([("adminId", 1), ("deleted", 1)])
        await self.database["productHistory"].create_index([("adminId", 1), ("timeStamp", 1)])
        await self.database["floorPlans"].create_index("restaurantId", unique=True)


@lru_cache
def get_async_database_client() -> AsyncDatabaseClient:
    return AsyncDatabaseClient(get_settings())


async def get_async_database() -> AsyncGenerator:
    yield get_async_database_client().database
