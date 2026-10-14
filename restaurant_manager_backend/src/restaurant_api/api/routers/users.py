from fastapi import APIRouter, Depends, HTTPException, status

from restaurant_api.api.dependencies import get_user_repository, get_user_service
from restaurant_api.api.dependencies import get_current_user
from restaurant_api.repositories.users import AsyncMongoUserRepository
from restaurant_api.schemas.users import UserCreate, UserIdResponse, UserResponse, serialize_user
from restaurant_api.services.users import UserService


router = APIRouter(prefix="/users", tags=["users"])


@router.post("", response_model=UserIdResponse, status_code=status.HTTP_201_CREATED)
async def create_user(request: UserCreate, service: UserService = Depends(get_user_service)):
    return {"User id": await service.create_user(request.model_dump())}


@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: str,
    current_user: dict = Depends(get_current_user),
    repository: AsyncMongoUserRepository = Depends(get_user_repository),
):
    if user_id != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="You cannot access this user")
    user = await repository.find_by_id(user_id)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    return serialize_user(user)


@router.get("", response_model=list[UserResponse])
async def get_all_users(current_user: dict = Depends(get_current_user), repository: AsyncMongoUserRepository = Depends(get_user_repository)):
    if current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="Restaurant owner access required")
    return [serialize_user(user) for user in await repository.find_all()]


@router.get("/availability/{email}")
async def verify_user(email: str, repository: AsyncMongoUserRepository = Depends(get_user_repository)):
    if await repository.find_by_email(email):
        raise HTTPException(status_code=409, detail="User with this email already exists")
    return {"message": "You can create a user with this email"}


@router.get("/by-email/{email}")
async def get_user_by_email(email: str, current_user: dict = Depends(get_current_user), repository: AsyncMongoUserRepository = Depends(get_user_repository)):
    user = await repository.find_by_email(email)
    if user is None:
        raise HTTPException(status_code=404, detail="User not found")
    if user["_id"] != current_user.get("_id") and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="You cannot access this user")
    return serialize_user(user)


@router.delete("/{user_id}")
async def delete_user(user_id: str, current_user: dict = Depends(get_current_user), repository: AsyncMongoUserRepository = Depends(get_user_repository)):
    if user_id != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="You cannot delete this user")
    await repository.delete(user_id)
    return {"message": "User deleted successfully"}


@router.get("/{user_id}/administrator")
async def get_user_admin(user_id: str, current_user: dict = Depends(get_current_user), repository: AsyncMongoUserRepository = Depends(get_user_repository)):
    if user_id != current_user["id"] and current_user.get("role") != "admin":
        raise HTTPException(status_code=403, detail="You cannot access this user")
    return {"id": await repository.admin_id_for_user(user_id)}
