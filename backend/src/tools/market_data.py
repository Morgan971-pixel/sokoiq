import httpx
import statistics
from bs4 import BeautifulSoup
from src.models import MarketData

HEADERS = {"User-Agent": "SokoIQ/1.0 (student research project)"}

NSE_TICKERS = {
    "SCOM": "safaricom",
    "EQTY": "equity-group-holdings",
    "KCB": "kcb-group",
    "EABL": "east-african-breweries",
    "KEGN": "kengen",
}


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


async def fetch_market_data(ticker: str) -> MarketData:
    slug = NSE_TICKERS.get(ticker, ticker.lower())
    url = f"https://www.african-markets.com/en/stock-markets/nse/listed-companies/{slug}"
    try:
        async with httpx.AsyncClient(timeout=20, headers=HEADERS) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
        soup = BeautifulSoup(r.text, "lxml")
        prices = []
        price_tags = soup.find_all("td", class_=lambda c: c and "price" in c.lower())
        for tag in price_tags:
            try:
                prices.append(float(tag.text.strip().replace(",", "")))
            except ValueError:
                continue
        if not prices:
            price_td = soup.find(
                "td",
                string=lambda s: s and s.strip().replace(".", "").replace(",", "").isdigit()
            )
            if price_td:
                prices = [float(price_td.text.strip().replace(",", ""))]
        if prices:
            return compute_returns(ticker, prices)
        return MarketData(ticker=ticker, data_source="african-markets.com (no data parsed)")
    except httpx.HTTPStatusError as e:
        return MarketData(ticker=ticker, data_source=f"HTTP {e.response.status_code}")
    except httpx.TransportError as e:
        return MarketData(ticker=ticker, data_source=f"network error: {str(e)[:100]}")
    except Exception as e:
        return MarketData(ticker=ticker, data_source=f"error: {str(e)[:100]}")
