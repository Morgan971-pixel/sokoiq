import pytest
from pydantic import ValidationError
from src.models import FilingData, InvestmentBrief, MarketData


def test_filing_data_defaults_to_empty_lists():
    data = FilingData(ticker="SCOM", company_name="Safaricom PLC", period="FY2024")
    assert data.key_risks == []
    assert data.raw_excerpt == ""
    assert data.revenue_growth_pct is None


def test_filing_data_accepts_full_payload():
    data = FilingData(
        ticker="SCOM",
        company_name="Safaricom PLC",
        period="FY2024",
        revenue_growth_pct=11.0,
        profit_growth_pct=8.0,
        key_risks=["competition", "regulation"],
        management_commentary="Strong growth in M-Pesa.",
        raw_excerpt="Revenue grew 11% year-on-year.",
        source_url="https://nse.co.ke/filings/SCOM_AR2024.pdf",
    )
    assert data.ticker == "SCOM"
    assert len(data.key_risks) == 2


def test_investment_brief_rejects_invalid_recommendation():
    with pytest.raises(ValidationError):
        InvestmentBrief(
            ticker="SCOM",
            company_name="Safaricom PLC",
            generated_at="2026-06-18T12:00:00Z",
            recommendation="STRONG_BUY",
            confidence=0.78,
            thesis="thesis",
            financials_summary="fin",
            market_summary="mkt",
            news_summary="news",
        )


def test_investment_brief_rejects_out_of_range_confidence():
    with pytest.raises(ValidationError):
        InvestmentBrief(
            ticker="SCOM",
            company_name="Safaricom PLC",
            generated_at="2026-06-18T12:00:00Z",
            recommendation="BUY",
            confidence=1.5,
            thesis="thesis",
            financials_summary="fin",
            market_summary="mkt",
            news_summary="news",
        )


def test_market_data_rejects_invalid_trend():
    with pytest.raises(ValidationError):
        MarketData(ticker="SCOM", trend="sideways")
