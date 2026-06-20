from src.models import (
    CompanyTicker, FilingData, MarketData, NewsData, InvestmentBrief
)


def test_filing_data_has_required_fields():
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
    assert len(data.key_risks) > 0


def test_investment_brief_confidence_range():
    from src.models import InvestmentBrief
    brief = InvestmentBrief(
        ticker="SCOM",
        company_name="Safaricom PLC",
        generated_at="2026-06-18T12:00:00Z",
        recommendation="BUY",
        confidence=0.78,
        thesis="Strong M-Pesa growth drives revenue.",
        financials_summary="Revenue grew 11%.",
        market_summary="30-day return +4.2%.",
        news_summary="Positive sentiment across 8 articles.",
        key_risks=["regulation"],
        citations=["https://nse.co.ke/filings/SCOM.pdf"],
    )
    assert 0.0 <= brief.confidence <= 1.0
    assert brief.recommendation in {"BUY", "HOLD", "SELL", "NEUTRAL"}
