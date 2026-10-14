from datetime import datetime

from pydantic import BaseModel, Field


class RevenuePeriod(BaseModel):
    start: datetime
    end: datetime


class RevenueResponse(BaseModel):
    restaurant_id: str = Field(alias="restaurantId")
    period: RevenuePeriod
    currency: str
    total_revenue: str = Field(alias="totalRevenue")

    model_config = {"populate_by_name": True}
