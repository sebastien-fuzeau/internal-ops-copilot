from __future__ import annotations

from fastapi import APIRouter, Depends

from internal_ops_copilot.web.deps.auth import AuthContext, require_auth

router = APIRouter(prefix="/v1", tags=["meta"])


@router.get("/ping")
def ping(_: AuthContext = Depends(require_auth)) -> dict:
    return {"status": "ok"}
