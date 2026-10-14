from typing import Any

from pydantic import BaseModel, EmailStr, Field


class UserCreate(BaseModel):
    username: EmailStr
    password: str = Field(min_length=8)
    company_name: str | None = None
    company_address: str | None = None
    company_phone: str | None = None
    location: str | None = None
    county: str | None = None


class UserResponse(BaseModel):
    id: str
    email: EmailStr
    role: str
    name: str | None = None
    phone_number: str | None = None
    company_name: str | None = None
    company_address: str | None = None
    company_phone: str | None = None
    location: str | None = None
    total_amount: float | None = None
    image_url: str | None = None


class UserIdResponse(BaseModel):
    user_id: str = Field(alias="User id")

    model_config = {"populate_by_name": True}


def serialize_user(document: dict[str, Any]) -> UserResponse:
    return UserResponse(
        id=str(document["_id"]),
        email=document["email"],
        role=document.get("role", ""),
        name=document.get("name"),
        phone_number=document.get("phoneNumber"),
        company_name=document.get("companyName"),
        company_address=document.get("companyAddress"),
        company_phone=document.get("companyPhone"),
        location=document.get("location"),
        total_amount=document.get("totalAmount"),
        image_url=document.get("imageUrl"),
    )
