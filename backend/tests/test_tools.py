import pytest
from src.tools.nse_filings import parse_filing_text, NSE_FILING_URLS


def test_parse_filing_text_extracts_revenue():
    sample = """
    Revenue for the year ended 31 December 2024 grew by 11% to KES 340 billion.
    Profit before tax increased by 8% year on year.
    Key risks: competition from new entrants, regulatory changes.
    The Board remains confident in long-term growth prospects.
    """
    result = parse_filing_text("SCOM", "Safaricom PLC", sample)
    assert result.ticker == "SCOM"
    assert result.raw_excerpt != ""
    assert result.revenue_growth_pct == 11.0
    assert result.profit_growth_pct == 8.0
    assert len(result.key_risks) >= 1


def test_filing_urls_has_all_companies():
    from src.models import COMPANIES
    for company in COMPANIES:
        assert company.ticker in NSE_FILING_URLS, \
            f"Missing filing URL for {company.ticker}"


def test_parse_filing_text_empty_gracefully():
    result = parse_filing_text("SCOM", "Safaricom PLC", "")
    assert result.ticker == "SCOM"
    assert result.raw_excerpt == ""


from src.tools.market_data import compute_returns


def test_compute_returns_positive_trend():
    prices = [100.0, 102.0, 105.0, 103.0, 108.0]
    result = compute_returns("SCOM", prices)
    assert result.return_30d_pct is not None
    assert result.trend in {"bullish", "bearish", "neutral"}


def test_compute_returns_empty_list():
    result = compute_returns("SCOM", [])
    assert result.return_30d_pct is None
    assert result.trend == "neutral"


def test_compute_returns_declining():
    prices = [100.0, 98.0, 95.0, 92.0, 90.0]
    result = compute_returns("SCOM", prices)
    assert result.trend == "bearish"
