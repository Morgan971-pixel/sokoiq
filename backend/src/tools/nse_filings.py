import httpx
import pdfplumber
import tempfile
import pathlib
import re
from src.models import FilingData

NSE_FILING_URLS: dict[str, str] = {
    "SCOM": "https://www.nse.co.ke/wp-content/uploads/2024/03/Safaricom-PLC-Investor-Briefing-H1FY2024.pdf",
    "EQTY": "https://www.nse.co.ke/wp-content/uploads/2024/04/Equity-Group-2023-Annual-Report.pdf",
    "KCB":  "https://www.nse.co.ke/wp-content/uploads/2024/04/KCB-2023-Annual-Report.pdf",
    "EABL": "https://www.nse.co.ke/wp-content/uploads/2024/04/EABL-2023-Annual-Report.pdf",
    "KEGN": "https://www.nse.co.ke/wp-content/uploads/2024/04/KenGen-Annual-Report-2023.pdf",
}

HEADERS = {
    "User-Agent": "SokoIQ/1.0 Research Platform (student project)"
}


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


async def fetch_filing(ticker: str, company_name: str) -> FilingData:
    url = NSE_FILING_URLS.get(ticker)
    if not url:
        return FilingData(
            ticker=ticker,
            company_name=company_name,
            period="Unknown",
            raw_excerpt=f"No filing URL configured for {ticker}",
        )
    tmp_path: str | None = None
    try:
        async with httpx.AsyncClient(timeout=30, headers=HEADERS) as client:
            response = await client.get(url, follow_redirects=True)
            response.raise_for_status()
            with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
                f.write(response.content)
                tmp_path = f.name
        text = ""
        with pdfplumber.open(tmp_path) as pdf:
            for page in pdf.pages[:20]:
                text += (page.extract_text() or "") + "\n"
        return parse_filing_text(ticker, company_name, text)
    except httpx.HTTPStatusError as e:
        raw_excerpt = f"HTTP {e.response.status_code} fetching filing for {ticker}"
    except httpx.TransportError as e:
        raw_excerpt = f"Network error fetching filing: {str(e)[:200]}"
    except Exception as e:
        raw_excerpt = f"Parse error: {str(e)[:200]}"
    finally:
        if tmp_path:
            pathlib.Path(tmp_path).unlink(missing_ok=True)
    return FilingData(
        ticker=ticker,
        company_name=company_name,
        period="Unknown",
        raw_excerpt=raw_excerpt,
    )
