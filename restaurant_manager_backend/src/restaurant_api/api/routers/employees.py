from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr, Field

from restaurant_api.api.dependencies import get_async_database, get_employee_service, require_owner_for_user_id
from restaurant_api.core.config import get_settings
from restaurant_api.repositories.restaurant import object_id
from restaurant_api.services.employees import EmployeeService
from restaurant_api.schemas.domains import IncomeAdjustment


class EmployeeCreate(BaseModel):
    name: str; email: EmailStr; password: str = Field(min_length=8); role: str = "waiter"; salary: float; birthdate: str; description: str | None = None
class EmployeeUpdate(BaseModel):
    name: str
    email: EmailStr
    password: str | None = Field(default=None, min_length=8)
    role: str
    salary: float = Field(ge=0)
    description: str | None = None
    birthdate: str

router = APIRouter(tags=["employees"])

@router.post("/restaurants/{user_id}/employees", status_code=201)
async def create_employee(user_id: str, request: EmployeeCreate, service: EmployeeService = Depends(get_employee_service), _: dict = Depends(require_owner_for_user_id)):
    data = request.model_dump(); data["user_id"] = user_id
    return await service.create(data)

@router.get("/restaurants/{user_id}/employees")
async def get_employees(user_id: str, service: EmployeeService = Depends(get_employee_service), _: dict = Depends(require_owner_for_user_id)): return await service.list(user_id)

@router.get("/restaurants/{user_id}/employees/{employee_id}")
async def get_employee(user_id: str, employee_id: str, service: EmployeeService = Depends(get_employee_service), _: dict = Depends(require_owner_for_user_id)): return await service.get(user_id, employee_id)

@router.delete("/restaurants/{user_id}/employees/{employee_id}")
async def delete_employee(user_id: str, employee_id: str, service: EmployeeService = Depends(get_employee_service), _: dict = Depends(require_owner_for_user_id)):
    await service.delete(user_id, employee_id); return {"message": "Employee deleted successfully"}

@router.patch("/restaurants/{user_id}/employees/{employee_id}")
async def update_employee(user_id: str, employee_id: str, request: EmployeeUpdate, service: EmployeeService = Depends(get_employee_service), _: dict = Depends(require_owner_for_user_id)):
    await service.update(user_id, employee_id, request.model_dump(exclude_none=True)); return {"message": "Employee updated successfully"}

@router.get("/restaurants/{user_id}/employees/{employee_id}/reports")
async def employee_report(user_id: str, employee_id: str, period: str = Query("range"), start_date: str | None = None, end_date: str | None = None, group_by: str = Query("daily"), database=Depends(get_async_database), _: dict = Depends(require_owner_for_user_id)):
    if group_by not in {"daily", "monthly"}:
        raise HTTPException(422, "group_by must be daily or monthly")
    now = datetime.now(timezone.utc)
    if period == "month":
        start, end = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0), now
    elif period == "year":
        start, end = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0), now
    elif period == "range":
        if not start_date or not end_date:
            raise HTTPException(422, "start_date and end_date are required")
        try:
            start, end = datetime.fromisoformat(start_date), datetime.fromisoformat(end_date)
        except ValueError as exc:
            raise HTTPException(422, "Invalid date format") from exc
        if start.tzinfo is None: start = start.replace(tzinfo=timezone.utc)
        if end.tzinfo is None: end = end.replace(tzinfo=timezone.utc)
        if start >= end: raise HTTPException(422, "start_date must be before end_date")
    else:
        raise HTTPException(422, "period must be month, year, or range")

    employee = await database["employers"].find_one({"_id": object_id(employee_id, "employee ID"), "userId": user_id})
    if not employee: raise HTTPException(404, "Employee not found")
    account = await database["user"].find_one({"email": employee["email"], "adminId": user_id})
    if not account: raise HTTPException(404, "Employee account not found")

    rows = await database["productHistory"].find({"adminId": user_id, "userId": {"$in": [employee_id, str(account["_id"])]}, "timeStamp": {"$gte": start, "$lt": end}}, {"_id": 0}).to_list()
    buckets: dict[str, dict[str, int | str]] = {}
    for row in rows:
        stamp = row.get("timeStamp")
        if not isinstance(stamp, datetime): continue
        stamp = stamp.astimezone(timezone.utc)
        bucket_start = stamp.replace(day=1, hour=0, minute=0, second=0, microsecond=0) if group_by == "monthly" else stamp.replace(hour=0, minute=0, second=0, microsecond=0)
        key = bucket_start.isoformat()
        bucket = buckets.setdefault(key, {"date": key, "quantity": 0, "revenueCents": 0})
        bucket["quantity"] = int(bucket["quantity"]) + int(row.get("qty", 0))
        bucket["revenueCents"] = int(bucket["revenueCents"]) + int(row.get("lineTotalCents", 0))
    series = [{"date": value["date"], "quantity": value["quantity"], "revenue": round(int(value["revenueCents"]) / 100, 2)} for _, value in sorted(buckets.items())]
    return {"employeeId": employee_id, "employeeName": employee["name"], "period": {"start": start, "end": end}, "currency": get_settings().default_currency, "quantity": sum(int(row.get("qty", 0)) for row in rows), "revenue": round(sum(int(row.get("lineTotalCents", 0)) for row in rows) / 100, 2), "series": series}

@router.post("/restaurants/{user_id}/employees/{employee_id}/income")
async def add_income(user_id: str, employee_id: str, request: IncomeAdjustment, service: EmployeeService = Depends(get_employee_service), _: dict = Depends(require_owner_for_user_id)):
    await service.income(user_id, employee_id, request.amount); return {"message": "Income added successfully"}

@router.get("/employees/by-email/{email}")
async def get_employee_by_email(email: str, service: EmployeeService = Depends(get_employee_service)): return await service.by_email(email)
