from httpx import AsyncClient, ASGITransport
from src.api import app


async def test_health_check():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/health")
    assert r.status_code == 200
    assert r.json()["status"] == "ok"


async def test_list_companies_returns_five():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/companies")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 5
    tickers = [c["ticker"] for c in data]
    assert "SCOM" in tickers
    assert "EQTY" in tickers


async def test_list_companies_shape():
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        r = await client.get("/companies")
    data = r.json()
    for company in data:
        assert "ticker" in company
        assert "company_name" in company
