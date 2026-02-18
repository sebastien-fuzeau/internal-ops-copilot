import httpx
import pytest

from internal_ops_copilot.app.factory import create_app


@pytest.mark.asyncio
async def test_v1_ping_e2e() -> None:
    app = create_app()
    transport = httpx.ASGITransport(app=app)

    async with httpx.AsyncClient(transport=transport, base_url="http://test") as client:
        r = await client.get("/v1/ping")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
