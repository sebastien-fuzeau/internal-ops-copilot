from __future__ import annotations

from fastapi import APIRouter

router = APIRouter()


@router.get("/healthz", tags=["health"])
def healthz() -> dict:
    return {"status": "ok"}


@router.get("/readyz", tags=["health"])
def readyz() -> dict:
    # Plus tard: checks DB/redis/etc.
    return {"status": "ready"}
