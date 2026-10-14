from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from fastapi.responses import Response

from restaurant_api.api.dependencies import get_async_database, get_current_user, require_menu_owner
from restaurant_api.repositories.images import MongoImageStorage
from restaurant_api.repositories.restaurant import object_id


router = APIRouter(prefix="/media", tags=["media"])
MAX_IMAGE_SIZE = 10 * 1024 * 1024
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}


def get_image_storage(database=Depends(get_async_database)) -> MongoImageStorage:
    return MongoImageStorage(database)


async def save_upload(file: UploadFile, storage: MongoImageStorage, metadata: dict) -> str:
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Unsupported image type")
    content = await file.read()
    if not content or len(content) > MAX_IMAGE_SIZE:
        raise HTTPException(status_code=413, detail="Image must be between 1 byte and 10 MB")
    return await storage.save(content, file.filename or "image", file.content_type, metadata)


@router.post("/users/{email}/profile-image")
async def upload_profile_image(email: str, file: UploadFile = File(...), database=Depends(get_async_database), storage: MongoImageStorage = Depends(get_image_storage), user: dict = Depends(get_current_user)):
    if email.lower() != user.get("email", "").lower():
        raise HTTPException(status_code=403, detail="You can update only your own profile image")
    user = await database["user"].find_one({"email": email})
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    old_image_id = user.get("imageId")
    image_id = await save_upload(file, storage, {"resourceType": "profile", "resourceId": str(user["_id"]), "restaurantId": user.get("restaurant_id"), "uploaderId": user["id"]})
    await database["user"].update_one({"_id": user["_id"]}, {"$set": {"imageId": image_id, "imageUrl": f"/api/v1/media/images/{image_id}"}})
    if old_image_id: await storage.delete(old_image_id)
    return {"image_id": image_id, "url": f"/api/v1/media/images/{image_id}"}


@router.put("/menu-products/{product_id}/image")
async def upload_product_image(product_id: str, file: UploadFile = File(...), database=Depends(get_async_database), storage: MongoImageStorage = Depends(get_image_storage), _: dict = Depends(require_menu_owner)):
    product = await database["menu"].find_one({"_id": object_id(product_id, "product ID")})
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    old_image_id = product.get("imageId")
    image_id = await save_upload(file, storage, {"resourceType": "menu", "resourceId": product_id, "restaurantId": product.get("adminId")})
    await database["menu"].update_one({"_id": product["_id"]}, {"$set": {"imageId": image_id, "imageUrl": f"/api/v1/media/images/{image_id}"}})
    if old_image_id: await storage.delete(old_image_id)
    return {"image_id": image_id, "url": f"/api/v1/media/images/{image_id}"}


@router.get("/images/{image_id}")
async def get_image(image_id: str, storage: MongoImageStorage = Depends(get_image_storage)):
    content, content_type = await storage.read(image_id)
    return Response(content=content, media_type=content_type)


@router.delete("/images/{image_id}", status_code=204)
async def delete_image(image_id: str, storage: MongoImageStorage = Depends(get_image_storage), user: dict = Depends(get_current_user)):
    metadata = await storage.metadata(image_id)
    if metadata.get("resourceType") == "profile" and metadata.get("resourceId") != user.get("id"):
        raise HTTPException(status_code=403, detail="You cannot delete this image")
    if metadata.get("resourceType") == "menu" and (user.get("role") != "admin" or metadata.get("restaurantId") != user.get("id")):
        raise HTTPException(status_code=403, detail="Restaurant owner access required")
    await storage.delete(image_id)
