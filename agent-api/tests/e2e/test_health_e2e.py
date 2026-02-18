import httpx

from internal_ops_copilot.app.factory import create_app


def test_healthz_e2e() -> None:
    app = create_app()

    transport = httpx.ASGITransport(app=app)
    with httpx.Client(transport=transport, base_url="http://test") as client:
        r = client.get("/healthz")
        assert r.status_code == 200
        assert r.json()["status"] == "ok"
