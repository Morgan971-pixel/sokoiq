import xml.etree.ElementTree as ET
import re

import httpx
from src.models import FilingData

NSE_FILING_URLS: dict[str, str] = {
    "SCOM": "https://www.nse.co.ke/wp-content/uploads/2024/03/Safaricom-PLC-Investor-Briefing-H1FY2024.pdf",
    "EQTY": "https://www.nse.co.ke/wp-content/uploads/2024/04/Equity-Group-2023-Annual-Report.pdf",
    "KCB":  "https://www.nse.co.ke/wp-content/uploads/2024/04/KCB-2023-Annual-Report.pdf",
    "EABL": "https://www.nse.co.ke/wp-content/uploads/2024/04/EABL-2023-Annual-Report.pdf",
    "KEGN": "https://www.nse.co.ke/wp-content/uploads/2024/04/KenGen-Annual-Report-2023.pdf",
}

GOOGLE_NEWS_FINANCIALS_RSS = (
    "https://news.google.com/rss/search?q={query}+results+revenue+profit"
    "&hl=en-KE&gl=KE&ceid=KE:en"
)

COMPANY_FINANCIAL_QUERIES = {
    "SCOM": "Safaricom+PLC+annual+results",
    "EQTY": "Equity+Group+Holdings+annual+results",
    "KCB":  "KCB+Group+annual+results",
    "EABL": "East+African+Breweries+annual+results",
    "KEGN": "KenGen+annual+results",
}

COMPANY_BROAD_QUERIES = {
    "SCOM": "Safaricom+PLC+results",
    "EQTY": "Equity+Group+Holdings+results",
    "KCB":  "KCB+Group+results",
    "EABL": "East+African+Breweries+results",
    "KEGN": "KenGen+results",
}

HEADERS = {
    "User-Agent": "SokoIQ/1.0 Research Platform (student project)"
}


def _extract_pct(text: str, keyword: str) -> float | None:
    # "11% revenue growth" — number precedes keyword within 50 chars
    m = re.search(rf'(\d+\.?\d*)\s*%[^.;{{}}\n]{{0,50}}{keyword}', text, re.IGNORECASE)
    if m:
        return float(m.group(1))
    # "revenue grew by 11%" — number follows keyword within 100 chars
    m = re.search(rf'{keyword}[^.{{}}]{{0,100}}(\d+\.?\d*)\s*%', text, re.IGNORECASE)
    return float(m.group(1)) if m else None


def _extract_period(text: str) -> str:
    m = re.search(r'(FY\s?\d{4}|H[12]\s?FY?\s?\d{4}|\b20\d{2}\b)', text, re.IGNORECASE)
    return m.group(1).replace(" ", "") if m else "Unknown"


def extract_financials_from_rss(ticker: str, company_name: str, xml_text: str) -> FilingData:
    try:
        root = ET.fromstring(xml_text)
    except ET.ParseError:
        return FilingData(ticker=ticker, company_name=company_name, period="Unknown")

    combined = ""
    source_url = ""
    for item in root.iter("item"):
        title = (item.findtext("title") or "").strip()
        desc = (item.findtext("description") or "").strip()
        link = (item.findtext("link") or "").strip()
        combined += f" {title} {desc}"
        if not source_url and link:
            source_url = link

    rev = _extract_pct(combined, "revenue")
    pft = _extract_pct(combined, "profit")
    period = _extract_period(combined)

    return FilingData(
        ticker=ticker,
        company_name=company_name,
        period=period,
        revenue_growth_pct=rev,
        profit_growth_pct=pft,
        raw_excerpt=combined[:1500].strip(),
        source_url=source_url,
    )


def parse_filing_text(ticker: str, company_name: str, text: str) -> FilingData:
    if not text.strip():
        return FilingData(ticker=ticker, company_name=company_name, period="Unknown")

    revenue_match = re.search(
        r"revenue[^.]*?(\d+\.?\d*)\s*%", text, re.IGNORECASE
    )
    profit_match = re.search(
        r"profit[^.]*?(\d+\.?\d*)\s*%", text, re.IGNORECASE
    )

    risks = []
    risk_section = re.search(
        r"(key risks?|principal risks?)[:\s]+(.*?)(?:\n\n|\Z)",
        text, re.IGNORECASE | re.DOTALL
    )
    if risk_section:
        raw_risks = risk_section.group(2)
        risks = [r.strip() for r in re.split(r"[,;\n]", raw_risks) if r.strip()][:5]

    commentary_match = re.search(
        r"(board|management|chief executive)[^.]*\.(.*?\.)",
        text, re.IGNORECASE | re.DOTALL
    )

    excerpt = text[:1500].strip()

    return FilingData(
        ticker=ticker,
        company_name=company_name,
        period="FY2024",
        revenue_growth_pct=float(revenue_match.group(1)) if revenue_match else None,
        profit_growth_pct=float(profit_match.group(1)) if profit_match else None,
        key_risks=risks,
        management_commentary=commentary_match.group(2).strip() if commentary_match else "",
        raw_excerpt=excerpt,
        source_url=NSE_FILING_URLS.get(ticker, ""),
    )


async def fetch_filing_broad(ticker: str, company_name: str) -> FilingData:
    """Broader query fallback — drops the +revenue+profit requirement."""
    query = COMPANY_BROAD_QUERIES.get(ticker, company_name.replace(" ", "+") + "+results")
    url = GOOGLE_NEWS_FINANCIALS_RSS.format(query=query)
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
        return extract_financials_from_rss(ticker, company_name, r.text)
    except (httpx.HTTPStatusError, httpx.TransportError):
        return FilingData(ticker=ticker, company_name=company_name, period="Unknown")
    except Exception:
        return FilingData(ticker=ticker, company_name=company_name, period="Unknown")


async def fetch_filing(ticker: str, company_name: str) -> FilingData:
    query = COMPANY_FINANCIAL_QUERIES.get(ticker, company_name.replace(" ", "+"))
    url = GOOGLE_NEWS_FINANCIALS_RSS.format(query=query)
    try:
        async with httpx.AsyncClient(timeout=15, headers=HEADERS) as client:
            r = await client.get(url, follow_redirects=True)
            r.raise_for_status()
        return extract_financials_from_rss(ticker, company_name, r.text)
    except (httpx.HTTPStatusError, httpx.TransportError):
        return FilingData(ticker=ticker, company_name=company_name, period="Unknown")
    except Exception:
        return FilingData(ticker=ticker, company_name=company_name, period="Unknown")
