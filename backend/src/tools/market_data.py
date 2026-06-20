import httpx
import statistics
from bs4 import BeautifulSoup
from src.models import MarketData

HEADERS = {"User-Agent": "SokoIQ/1.0 (student research project)"}

AFX_BASE_URL = "https://afx.kwayisi.org/nse/{ticker}/"


def compute_returns(ticker: str, prices: list[float]) -> MarketData:
    if not prices or len(prices) < 2:
        return MarketData(ticker=ticker)

    latest = prices[-1]
    start_30d = prices[max(0, len(prices) - 22)]
    start_90d = prices[max(0, len(prices) - 66)]

    return_30d = ((latest - start_30d) / start_30d) * 100
    return_90d = ((latest - start_90d) / start_90d) * 100

    recent = prices[-22:]
    daily_returns = [(recent[i] - recent[i-1]) / recent[i-1] for i in range(1, len(recent))]
    volatility = statistics.stdev(daily_returns) * 100 if len(daily_returns) > 1 else None

    trend: str
    if return_30d > 2.0:
        trend = "bullish"
    elif return_30d < -2.0:
        trend = "bearish"
    else:
        trend = "neutral"

    return MarketData(
        ticker=ticker,
        current_price_kes=latest,
        return_30d_pct=round(return_30d, 2),
        return_90d_pct=round(return_90d, 2),
        volatility_30d=round(volatility, 3) if volatility is not None else None,
        trend=trend,
        data_source="african-markets.com",
    )


def parse_afx_html(ticker: str, html: str) -> MarketData:
    soup = BeautifulSoup(html, "html.parser")
    tables = soup.find_all("table")

    current_price: float | None = None
    history_table = next((t for t in tables if "Close" in t.get_text()), None)
    if history_table:
        for row in history_table.find_all("tr")[1:]:
            cells = [c.get_text(strip=True) for c in row.find_all(["td", "th"])]
            if len(cells) >= 3 and cells[2]:
                try:
                    current_price = float(cells[2].replace(",", ""))
                    break
                except ValueError:
                    continue

    return_30d: float | None = None
    return_90d: float | None = None
    perf_table = next((t for t in tables if "4WK" in t.get_text()), None)
    if perf_table:
        rows = perf_table.find_all("tr")
        if len(rows) >= 2:
            cells = [c.get_text(strip=True) for c in rows[1].find_all(["td", "th"])]
            if len(cells) >= 2:
                try:
                    return_30d = float(cells[1].rstrip("%"))
                except ValueError:
                    pass
            if len(cells) >= 3:
                try:
                    return_90d = float(cells[2].rstrip("%"))
                except ValueError:
                    pass

    if return_30d is not None:
        trend = "bullish" if return_30d > 2.0 else "bearish" if return_30d < -2.0 else "neutral"
    else:
        trend = "neutral"

    return MarketData(
        ticker=ticker,
        current_price_kes=current_price,
        return_30d_pct=round(return_30d, 2) if return_30d is not None else None,
        return_90d_pct=round(return_90d, 2) if return_90d is not None else None,
        trend=trend,
        data_source="afx.kwayisi.org",
    )


async def fetch_market_data(ticker: str) -> MarketData:
    url = AFX_BASE_URL.format(ticker=ticker)
    try:
        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
        return parse_afx_html(ticker, r.text)
    except httpx.HTTPStatusError as e:
        return MarketData(ticker=ticker, data_source=f"HTTP {e.response.status_code}")
    except httpx.TransportError as e:
        return MarketData(ticker=ticker, data_source=f"network error: {str(e)[:100]}")
    except Exception as e:
        return MarketData(ticker=ticker, data_source=f"error: {str(e)[:100]}")
