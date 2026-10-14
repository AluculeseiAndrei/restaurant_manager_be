from datetime import datetime
from typing import Any

from pydantic import BaseModel, Field


class ClientCreate(BaseModel):
    client_name: str = Field(alias="clientName")
    username: str
    password: str = Field(min_length=8)
    location: str
    county: str
    phone_number: str = Field(alias="phoneNumber")
    model_config = {"populate_by_name": True}


class ClientLocationUpdate(BaseModel):
    client_id: str = Field(alias="clientId")
    location: str
    county: str
    model_config = {"populate_by_name": True}


class ReviewCreate(BaseModel):
    client_id: str = Field(alias="clientId")
    restaurant_id: str = Field(alias="restaurantId")
    recension: str
    rating: float
    model_config = {"populate_by_name": True}


class TableCreate(BaseModel):
    name: str
    capacity: int | None = None


class MenuProductCreate(BaseModel):
    name: str
    type: str
    price: float
    description: str


class ProductCreate(BaseModel):
    menu_product_id: str = Field(alias="menuProductId")
    name: str
    price: float
    qty: int = Field(gt=0)
    table_id: str = Field(alias="table_id")
    model_config = {"populate_by_name": True}


class ReservationCreate(BaseModel):
    reservation_name: str | None = Field(default=None, alias="reservationName")
    start_time: datetime | None = Field(default=None, alias="startTime")
    end_time: datetime | None = Field(default=None, alias="endTime")
    guests: int | None = None
    special_requests: str | None = Field(default=None, alias="specialRequests")
    model_config = {"populate_by_name": True}


class ReservationUpdate(ReservationCreate):
    pass


class FoodTypeCreate(BaseModel):
    type_name: str = Field(alias="typeName")
    model_config = {"populate_by_name": True}


class MessageResponse(BaseModel):
    message: str


class IncomeAdjustment(BaseModel):
    amount: float


def mongo_payload(model: BaseModel) -> dict[str, Any]:
    return model.model_dump(by_alias=False, exclude_none=True)
