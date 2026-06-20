import xml.etree.ElementTree as ET

import httpx
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
        return NewsData(ticker=ticker, company_name=company_name, overall_sentiment="neutral")
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


GOOGLE_NEWS_RSS = (
    "https://news.google.com/rss/search?q={query}"
    "&hl=en-KE&gl=KE&ceid=KE:en"
)

COMPANY_SEARCH_QUERIES = {
    "SCOM": "Safaricom+Kenya",
    "EQTY": "Equity+Group+Kenya",
    "KCB": "KCB+Group+Kenya",
    "EABL": "East+African+Breweries",
    "KEGN": "KenGen+Kenya",
}


def parse_rss_feed(ticker: str, company_name: str, xml_text: str) -> NewsData:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return NewsData(ticker=ticker, company_name=company_name, overall_sentiment="neutral")

    articles: list[NewsItem] = []
    for item in root.iter("item"):
        title_el = item.find("title")
        link_el = item.find("link")
        source_el = item.find("source")

        headline = (title_el.text or "").strip() if title_el is not None else ""
        url = (link_el.text or "").strip() if link_el is not None else ""
        source = (source_el.text or "").strip() if source_el is not None else "Google News"

        if not headline:
            continue

        articles.append(NewsItem(
            headline=headline[:200],
            url=url,
            source=source,
            sentiment=classify_sentiment(headline),
        ))

    return build_news_data(ticker, company_name, articles[:15])


async def fetch_news_broad(ticker: str) -> NewsData:
    """Broader search fallback — drops the Kenya geo-restriction."""
    company_name = COMPANY_SEARCH_TERMS.get(ticker, ticker)
    query = COMPANY_SEARCH_QUERIES.get(ticker, company_name.replace(" ", "+"))
    url = f"https://news.google.com/rss/search?q={query}"
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
        return parse_rss_feed(ticker, company_name, r.text)
    except (httpx.HTTPStatusError, httpx.TransportError):
        return NewsData(ticker=ticker, company_name=company_name, overall_sentiment="neutral")
    except Exception:
        return NewsData(ticker=ticker, company_name=company_name, overall_sentiment="neutral")


async def fetch_news(ticker: str) -> NewsData:
    company_name = COMPANY_SEARCH_TERMS.get(ticker, ticker)
    query = COMPANY_SEARCH_QUERIES.get(ticker, company_name.replace(" ", "+"))
    url = GOOGLE_NEWS_RSS.format(query=query)
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
        return parse_rss_feed(ticker, company_name, r.text)
    except (httpx.HTTPStatusError, httpx.TransportError):
        return NewsData(ticker=ticker, company_name=company_name, overall_sentiment="neutral")
    except Exception:
        return NewsData(ticker=ticker, company_name=company_name, overall_sentiment="neutral")
