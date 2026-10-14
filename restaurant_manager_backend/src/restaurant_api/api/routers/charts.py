from datetime import datetime, timedelta, timezone
from decimal import Decimal

from fastapi import APIRouter, Depends, HTTPException, Query

from restaurant_api.api.dependencies import get_async_database, require_staff_for_admin, require_staff_for_restaurant, require_staff_for_user_id
from restaurant_api.core.config import get_settings
from restaurant_api.schemas.reports import RevenueResponse

router = APIRouter(prefix="/reports", tags=["sales reports"])
restaurant_reports_router = APIRouter(prefix="/restaurants", tags=["sales reports"])
employee_router = APIRouter(prefix="/reports/employees", tags=["employee sales reports"])


def _dates(period: str, start_date: str | None, end_date: str | None):
    now = datetime.now(timezone.utc)
    if period == "today": return now.replace(hour=0, minute=0, second=0, microsecond=0), now
    if period == "month": return now.replace(day=1, hour=0, minute=0, second=0, microsecond=0), now
    if period == "range":
        if not start_date or not end_date: raise HTTPException(422, "start_date and end_date are required")
        try: start, end = datetime.fromisoformat(start_date), datetime.fromisoformat(end_date)
        except ValueError as exc: raise HTTPException(422, "Invalid date format") from exc
        if start.tzinfo is None: start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None: end = end.replace(tzinfo=timezone.utc)
        if start >= end: raise HTTPException(422, "start_date must be before end_date")
        return start, end
    raise HTTPException(422, "period must be today, month, or range")


async def _revenue(database, restaurant_id: str, start: datetime, end: datetime) -> int:
    pipeline = [{"$match": {"adminId": restaurant_id, "timeStamp": {"$gte": start, "$lt": end}, "lineTotalCents": {"$exists": True}}}, {"$group": {"_id": None, "total": {"$sum": "$lineTotalCents"}}}]
    cursor = await database["productHistory"].aggregate(pipeline)
    rows = await cursor.to_list()
    return int(rows[0]["total"]) if rows else 0


async def _quantity(database, restaurant_id: str, start: datetime, end: datetime) -> int:
    cursor = await database["productHistory"].aggregate([{"$match": {"adminId": restaurant_id, "timeStamp": {"$gte": start, "$lt": end}}}, {"$group": {"_id": None, "total": {"$sum": "$qty"}}}])
    rows = await cursor.to_list()
    return int(rows[0]["total"]) if rows else 0


@router.get("/sales/{admin_id}")
async def sales_report(admin_id: str, period: str = Query("summary"), start_date: str | None = None, end_date: str | None = None, database=Depends(get_async_database), _: dict = Depends(require_staff_for_admin)):
    if period in {"summary", "transactions"}:
        start, end = _dates("range", start_date, end_date)
    else:
        start, end = _dates("month" if period in {"month", "monthly"} else "today", start_date, end_date)
    if period == "transactions":
        return await database["productHistory"].find({"adminId": admin_id, "timeStamp": {"$gte": start, "$lt": end}}, {"_id": 0}).to_list()
    return {"restaurantId": admin_id, "start": start, "end": end, "quantity": sum(r.get("qty", 0) for r in await database["productHistory"].find({"adminId": admin_id, "timeStamp": {"$gte": start, "$lt": end}}).to_list())}


@restaurant_reports_router.get("/{restaurant_id}/reports/revenue", response_model=RevenueResponse, response_model_by_alias=True)
async def revenue_report(restaurant_id: str, period: str = Query("month"), start_date: str | None = None, end_date: str | None = None, database=Depends(get_async_database), _: dict = Depends(require_staff_for_restaurant)):
    start, end = _dates(period, start_date, end_date)
    cents = await _revenue(database, restaurant_id, start, end)
    return {"restaurant_id": restaurant_id, "period": {"start": start, "end": end}, "currency": get_settings().default_currency, "total_revenue": f"{Decimal(cents) / Decimal(100):.2f}"}


@employee_router.get("/{user_id}/daily")
async def employee_daily_sales(user_id: str, database=Depends(get_async_database), _: dict = Depends(require_staff_for_user_id)):
    now = datetime.now(timezone.utc); start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    return [{"day": day, "totalSum": await _quantity(database, user_id, start.replace(day=day), start.replace(day=day) + timedelta(days=1))} for day in range(1, now.day + 1)]


@employee_router.get("/{user_id}/monthly")
async def employee_monthly_sales(user_id: str, database=Depends(get_async_database), _: dict = Depends(require_staff_for_user_id)):
    now = datetime.now(timezone.utc); year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)
    values = []
    for month in range(1, now.month + 1):
        start = year.replace(month=month)
        end = year.replace(month=month + 1) if month < 12 else year.replace(year=year.year + 1)
        values.append({"month": month, "totalSum": await _quantity(database, user_id, start, end)})
    return values
