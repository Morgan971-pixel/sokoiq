import httpx
from bs4 import BeautifulSoup
from src.models import NewsData, NewsItem

HEADERS = {"User-Agent": "SokoIQ/1.0 (student research project)"}

POSITIVE_WORDS = {
    "growth", "profit", "dividend", "strong", "record", "increased", "surged",
    "beat", "exceeded", "expansion", "acquisition", "positive", "rise", "gain"
}
NEGATIVE_WORDS = {
    "loss", "losses", "decline", "warning", "dropped", "fell", "negative", "concern",
    "risk", "penalty", "fine", "lawsuit", "suspended", "struggle", "deficit"
}

COMPANY_SEARCH_TERMS = {
    "SCOM": "Safaricom",
    "EQTY": "Equity Group",
    "KCB": "KCB Group",
    "EABL": "East African Breweries",
    "KEGN": "KenGen",
}


def classify_sentiment(headline: str) -> str:
    words = set(headline.lower().split())
    pos = len(words & POSITIVE_WORDS)
    neg = len(words & NEGATIVE_WORDS)
    if pos > neg:
        return "positive"
    if neg > pos:
        return "negative"
    return "neutral"


def build_news_data(
    ticker: str, company_name: str, articles: list[NewsItem]
) -> NewsData:
    if not articles:
        return NewsData(ticker=ticker, company_name=company_name)
    sentiments = [a.sentiment for a in articles]
    pos = sentiments.count("positive")
    neg = sentiments.count("negative")
    overall = "positive" if pos > neg else "negative" if neg > pos else "neutral"
    drivers = list({a.headline[:60] for a in articles[:3]})
    return NewsData(
        ticker=ticker,
        company_name=company_name,
        articles=articles,
        overall_sentiment=overall,
        sentiment_drivers=drivers,
    )


def _extract_base_url(url: str) -> str:
    parts = url.split("/")
    return "/".join(parts[:3])


async def fetch_news(ticker: str) -> NewsData:
    company_name = COMPANY_SEARCH_TERMS.get(ticker, ticker)
    articles: list[NewsItem] = []
    sources = [
        (
            f"https://www.businessdailyafrica.com/bd/search?q={company_name.replace(' ', '+')}",
            "Business Daily Africa",
        ),
        (
            f"https://www.reuters.com/search/news?blob={company_name.replace(' ', '+')}",
            "Reuters",
        ),
    ]
    for url, source_name in sources:
        base_url = _extract_base_url(url)
        try:
            async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
                r = await client.get(url, follow_redirects=True)
                r.raise_for_status()
            soup = BeautifulSoup(r.text, "lxml")
            headlines = soup.find_all("h3") + soup.find_all("h2")
            for h in headlines[:5]:
                text = h.get_text(strip=True)
                if company_name.split()[0].lower() in text.lower() and len(text) > 20:
                    link_tag = h.find("a")
                    href = link_tag.get("href", "") if link_tag else ""
                    if href.startswith("/"):
                        href = base_url + href
                    elif not href:
                        href = url
                    articles.append(
                        NewsItem(
                            headline=text[:200],
                            url=href,
                            source=source_name,
                            sentiment=classify_sentiment(text),
                        )
                    )
        except (httpx.HTTPStatusError, httpx.TransportError):
            continue
        except Exception:
            continue
    return build_news_data(ticker, company_name, articles[:8])
