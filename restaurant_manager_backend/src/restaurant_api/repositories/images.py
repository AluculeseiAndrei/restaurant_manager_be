from bson import ObjectId
from gridfs import AsyncGridFSBucket

from restaurant_api.core.exceptions import DomainError


class MongoImageStorage:
    def __init__(self, database) -> None:
        self._bucket = AsyncGridFSBucket(database, bucket_name="images")

    async def save(self, content: bytes, filename: str, content_type: str, metadata: dict | None = None) -> str:
        image_metadata = {"contentType": content_type, **(metadata or {})}
        image_id = await self._bucket.upload_from_stream(filename, content, metadata=image_metadata)
        return str(image_id)

    async def read(self, image_id: str) -> tuple[bytes, str]:
        if not ObjectId.is_valid(image_id):
            raise DomainError("Image not found", 404)
        try:
            stream = await self._bucket.open_download_stream(ObjectId(image_id))
            return await stream.read(), stream.metadata.get("contentType", "application/octet-stream")
        except Exception as exc:
            raise DomainError("Image not found", 404) from exc

    async def delete(self, image_id: str) -> None:
        if ObjectId.is_valid(image_id):
            try:
                await self._bucket.delete(ObjectId(image_id))
            except Exception:
                pass

    async def metadata(self, image_id: str) -> dict:
        if not ObjectId.is_valid(image_id): raise DomainError("Image not found", 404)
        try:
            stream = await self._bucket.open_download_stream(ObjectId(image_id))
            return stream.metadata or {}
        except Exception as exc:
            raise DomainError("Image not found", 404) from exc
