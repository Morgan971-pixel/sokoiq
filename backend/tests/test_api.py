from unittest.mock import patch

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


async def test_history_returns_empty_list():
    with patch("src.api.get_briefs", return_value=[]):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/history")
    assert r.status_code == 200
    assert r.json() == []


async def test_history_returns_brief_rows():
    mock_rows = [
        {
            "id": "abc-123",
            "ticker": "SCOM",
            "company_name": "Safaricom PLC",
            "recommendation": "BUY",
            "confidence": 0.78,
            "thesis": "Strong growth.",
            "generated_at": "2026-06-20T10:00:00Z",
        }
    ]
    with patch("src.api.get_briefs", return_value=mock_rows):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            r = await client.get("/history")
    assert r.status_code == 200
    data = r.json()
    assert len(data) == 1
    assert data[0]["ticker"] == "SCOM"
    assert data[0]["recommendation"] == "BUY"


async def test_history_passes_ticker_filter():
    with patch("src.api.get_briefs", return_value=[]) as mock_gb:
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
            await client.get("/history?ticker=EQTY")
    mock_gb.assert_called_once_with(ticker="EQTY")
