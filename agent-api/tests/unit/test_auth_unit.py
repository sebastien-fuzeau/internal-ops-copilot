import time

import jwt
import pytest
from fastapi import FastAPI
from httpx import ASGITransport, AsyncClient

from internal_ops_copilot.app.config import get_settings
from internal_ops_copilot.app.factory import create_app


@pytest.mark.asyncio
async def test_auth_missing_api_key() -> None:
    app: FastAPI = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/v1/ping")
        assert r.status_code == 401


@pytest.mark.asyncio
async def test_auth_invalid_api_key() -> None:
    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/v1/ping", headers={"X-API-Key": "nope"})
        assert r.status_code == 403


@pytest.mark.asyncio
async def test_auth_valid_api_key_only() -> None:
    settings = get_settings()
    key = next(iter(settings.api_key_set()))

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/v1/ping", headers={settings.auth_api_key_header: key})
        assert r.status_code == 200
        assert r.json()["status"] == "ok"


@pytest.mark.asyncio
async def test_auth_valid_api_key_and_jwt() -> None:
    settings = get_settings()
    key = next(iter(settings.api_key_set()))

    now = int(time.time())
    token = jwt.encode(
        {
            "sub": "user-123",
            "iss": settings.jwt_issuer,
            "aud": settings.jwt_audience,
            "iat": now,
            "exp": now + 60,
        },
        settings.jwt_secret,
        algorithm=settings.jwt_alg,
    )

    app = create_app()
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get(
            "/v1/ping",
            headers={
                settings.auth_api_key_header: key,
                "Authorization": f"Bearer {token}",
            },
        )
        assert r.status_code == 200
