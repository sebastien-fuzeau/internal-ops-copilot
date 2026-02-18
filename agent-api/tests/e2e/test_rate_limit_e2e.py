import httpx
import pytest

from internal_ops_copilot.app.config import get_settings
from internal_ops_copilot.app.factory import create_app


@pytest.mark.asyncio
async def test_rate_limit_e2e() -> None:
    settings = get_settings()
    key = next(iter(settings.api_key_set()))

    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        # max 10 par défaut
        for _ in range(settings.rate_limit_max_requests):
            r = await client.get("/v1/ping", headers={settings.auth_api_key_header: key})
            assert r.status_code == 200

        r = await client.get("/v1/ping", headers={settings.auth_api_key_header: key})
        assert r.status_code == 429
