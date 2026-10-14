import random

from fastapi import APIRouter, Depends, HTTPException

from restaurant_api.api.dependencies import get_authentication_service
from restaurant_api.schemas.auth import LoginRequest, LoginResponse, PasswordResetConfirm, PasswordResetRequest
from restaurant_api.services.auth import AuthenticationService
from restaurant_api.core.database import get_async_database
from restaurant_api.core.security import hash_password


router = APIRouter(prefix="/auth", tags=["authentication"])


@router.post("/login", response_model=LoginResponse)
async def login(request: LoginRequest, service: AuthenticationService = Depends(get_authentication_service)):
    return await service.login(request.username, request.password)


@router.post("/password-reset/request")
async def forgot_password(request: PasswordResetRequest, database=Depends(get_async_database)):
    user = await database["user"].find_one({"email": request.email})
    if not user: raise HTTPException(status_code=404, detail="User not found")
    code = random.randint(1000, 9999)
    await database["user"].update_one({"_id": user["_id"]}, {"$set": {"code": code}})
    return {"message": "Password reset code generated"}


@router.post("/password-reset/confirm")
async def reset_password(request: PasswordResetConfirm, database=Depends(get_async_database)):
    user = await database["user"].find_one({"email": request.email})
    if not user: raise HTTPException(status_code=404, detail="User not found")
    if user.get("code") != request.code: raise HTTPException(status_code=401, detail="Wrong code")
    await database["user"].update_one({"_id": user["_id"]}, {"$set": {"password": hash_password(request.password)}, "$unset": {"code": ""}})
    return {"message": "Password reset successful"}
