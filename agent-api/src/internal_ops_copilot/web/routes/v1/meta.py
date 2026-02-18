from __future__ import annotations

from fastapi import APIRouter

router = APIRouter(prefix="/v1", tags=["meta"])


@router.get("/ping")
def ping() -> dict:
    return {"status": "ok"}
