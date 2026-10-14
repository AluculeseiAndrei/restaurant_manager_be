from fastapi import APIRouter, Depends, HTTPException

from restaurant_api.core.database import get_async_database_client


router = APIRouter(tags=["health"])


@router.get("/health/live")
async def health_check() -> dict[str, str]:
    return {"status": "ok"}


@router.get("/health/ready")
async def readiness() -> dict[str, str]:
    try:
        await get_async_database_client().ping()
    except Exception as exc:
        raise HTTPException(status_code=503, detail="Database unavailable") from exc
    return {"status": "ready", "database": "ok"}
