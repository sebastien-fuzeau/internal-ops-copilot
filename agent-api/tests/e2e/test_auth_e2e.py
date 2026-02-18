import httpx
import pytest

from internal_ops_copilot.app.config import get_settings
from internal_ops_copilot.app.factory import create_app


@pytest.mark.asyncio
async def test_openapi_has_security_schemes() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/openapi.json")
        assert r.status_code == 200
        spec = r.json()
        schemes = spec.get("components", {}).get("securitySchemes", {})
        # au moins apiKey présent; bearer peut dépendre du wiring
        assert any(v.get("type") == "apiKey" for v in schemes.values())


@pytest.mark.asyncio
async def test_v1_ping_requires_api_key_e2e() -> None:
    settings = get_settings()
    key = next(iter(settings.api_key_set()))

    app = create_app()
    transport = httpx.ASGITransport(app=app)
    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r1 = await client.get("/v1/ping")
        assert r1.status_code == 401

        r2 = await client.get("/v1/ping", headers={settings.auth_api_key_header: key})
        assert r2.status_code == 200
