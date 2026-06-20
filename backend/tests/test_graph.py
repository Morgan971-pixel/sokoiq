from datetime import datetime, timezone
from unittest.mock import AsyncMock, patch

from src.graph import run_research_pipeline
from src.models import FilingData, InvestmentBrief, MarketData, NewsData, NewsItem


def _make_brief(ticker: str, company_name: str) -> InvestmentBrief:
    return InvestmentBrief(
        ticker=ticker,
        company_name=company_name,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        recommendation="BUY",
        confidence=0.82,
        thesis="Strong growth.",
        financials_summary="Revenue grew.",
        market_summary="30d return positive.",
        news_summary="Positive sentiment.",
        key_risks=["competition"],
    )


def _make_articles(n: int = 3) -> list[NewsItem]:
    return [
        NewsItem(headline=f"Headline {i}", url=f"http://ex.com/{i}",
                 source="Test Source", sentiment="neutral")
        for i in range(n)
    ]


async def test_pipeline_returns_brief():
    with patch("src.graph.fetch_filing", new_callable=AsyncMock) as mock_filing, \
         patch("src.graph.fetch_market_data", new_callable=AsyncMock) as mock_market, \
         patch("src.graph.fetch_news", new_callable=AsyncMock) as mock_news, \
         patch("src.graph._synthesize_brief", new_callable=AsyncMock) as mock_synth:

        mock_filing.return_value = FilingData(
            ticker="SCOM", company_name="Safaricom PLC", period="FY2024",
            revenue_growth_pct=11.0, profit_growth_pct=8.0,
            raw_excerpt="Revenue grew 11%."
        )
        mock_market.return_value = MarketData(
            ticker="SCOM", current_price_kes=36.50,
            return_30d_pct=4.2, trend="bullish"
        )
        mock_news.return_value = NewsData(
            ticker="SCOM", company_name="Safaricom PLC",
            overall_sentiment="positive", articles=_make_articles(3)
        )
        mock_synth.return_value = _make_brief("SCOM", "Safaricom PLC")

        steps = []
        brief = None
        async for event in run_research_pipeline("SCOM", "Safaricom PLC"):
            if event.get("type") == "step":
                steps.append(event["data"])
            elif event.get("type") == "brief":
                brief = event["data"]

        assert len(steps) == 8
        assert brief is not None
        assert brief["ticker"] == "SCOM"
        assert brief["recommendation"] in {"BUY", "HOLD", "SELL", "NEUTRAL"}


async def test_pipeline_streams_named_agents():
    with patch("src.graph.fetch_filing", new_callable=AsyncMock) as mock_filing, \
         patch("src.graph.fetch_market_data", new_callable=AsyncMock) as mock_market, \
         patch("src.graph.fetch_news", new_callable=AsyncMock) as mock_news, \
         patch("src.graph._synthesize_brief", new_callable=AsyncMock) as mock_synth:

        mock_filing.return_value = FilingData(
            ticker="EQTY", company_name="Equity Group", period="FY2024",
            revenue_growth_pct=7.0
        )
        mock_market.return_value = MarketData(ticker="EQTY")
        mock_news.return_value = NewsData(
            ticker="EQTY", company_name="Equity Group",
            articles=_make_articles(3)
        )
        mock_synth.return_value = _make_brief("EQTY", "Equity Group Holdings")

        agent_names = set()
        async for event in run_research_pipeline("EQTY", "Equity Group Holdings"):
            if event.get("type") == "step":
                agent_names.add(event["data"]["agent"])

        assert "filing_analyst" in agent_names
        assert "market_analyst" in agent_names
        assert "news_analyst" in agent_names
        assert "memo_writer" in agent_names


async def test_pipeline_handles_synthesis_error_gracefully():
    with patch("src.graph.fetch_filing", new_callable=AsyncMock) as mock_filing, \
         patch("src.graph.fetch_market_data", new_callable=AsyncMock) as mock_market, \
         patch("src.graph.fetch_news", new_callable=AsyncMock) as mock_news, \
         patch("src.graph._synthesize_brief", new_callable=AsyncMock) as mock_synth:

        mock_filing.return_value = FilingData(
            ticker="KCB", company_name="KCB Group", period="FY2024",
            revenue_growth_pct=5.0
        )
        mock_market.return_value = MarketData(ticker="KCB")
        mock_news.return_value = NewsData(
            ticker="KCB", company_name="KCB Group",
            articles=_make_articles(3)
        )
        mock_synth.side_effect = Exception("LLM timeout")

        statuses = []
        async for event in run_research_pipeline("KCB", "KCB Group PLC"):
            if event.get("type") == "step" and event["data"]["agent"] == "memo_writer":
                statuses.append(event["data"]["status"])

        assert "error" in statuses


async def test_filing_agent_retries_when_no_financials():
    """When revenue_growth_pct is None, filing agent emits a retry step and calls fetch_filing_broad."""
    with patch("src.graph.fetch_filing", new_callable=AsyncMock) as mock_f, \
         patch("src.graph.fetch_filing_broad", new_callable=AsyncMock) as mock_fb, \
         patch("src.graph.fetch_market_data", new_callable=AsyncMock) as mock_m, \
         patch("src.graph.fetch_news", new_callable=AsyncMock) as mock_n, \
         patch("src.graph._synthesize_brief", new_callable=AsyncMock) as mock_s:

        mock_f.return_value = FilingData(
            ticker="SCOM", company_name="Safaricom PLC", period="Unknown"
        )
        mock_fb.return_value = FilingData(
            ticker="SCOM", company_name="Safaricom PLC", period="FY2024",
            revenue_growth_pct=11.0
        )
        mock_m.return_value = MarketData(ticker="SCOM", current_price_kes=32.65, trend="bullish")
        mock_n.return_value = NewsData(
            ticker="SCOM", company_name="Safaricom PLC",
            overall_sentiment="neutral", articles=_make_articles(3)
        )
        mock_s.return_value = _make_brief("SCOM", "Safaricom PLC")

        steps = []
        async for event in run_research_pipeline("SCOM", "Safaricom PLC"):
            if event["type"] == "step":
                steps.append(event["data"])

        assert mock_fb.called
        assert len(steps) == 9
        messages = [s["message"] for s in steps]
        assert any("retry" in m.lower() or "broader" in m.lower() for m in messages)


async def test_filing_agent_does_not_retry_when_data_sufficient():
    """fetch_filing_broad is never called when first fetch returns financials."""
    with patch("src.graph.fetch_filing", new_callable=AsyncMock) as mock_f, \
         patch("src.graph.fetch_filing_broad", new_callable=AsyncMock) as mock_fb, \
         patch("src.graph.fetch_market_data", new_callable=AsyncMock) as mock_m, \
         patch("src.graph.fetch_news", new_callable=AsyncMock) as mock_n, \
         patch("src.graph._synthesize_brief", new_callable=AsyncMock) as mock_s:

        mock_f.return_value = FilingData(
            ticker="SCOM", company_name="Safaricom PLC", period="FY2024",
            revenue_growth_pct=11.0
        )
        mock_m.return_value = MarketData(ticker="SCOM")
        mock_n.return_value = NewsData(
            ticker="SCOM", company_name="Safaricom PLC",
            articles=_make_articles(3)
        )
        mock_s.return_value = _make_brief("SCOM", "Safaricom PLC")

        steps = []
        async for event in run_research_pipeline("SCOM", "Safaricom PLC"):
            if event["type"] == "step":
                steps.append(event["data"])

        assert not mock_fb.called
        assert len(steps) == 8


async def test_news_agent_retries_when_too_few_articles():
    """When article count < 3, news agent emits a retry step and calls fetch_news_broad."""
    with patch("src.graph.fetch_filing", new_callable=AsyncMock) as mock_f, \
         patch("src.graph.fetch_market_data", new_callable=AsyncMock) as mock_m, \
         patch("src.graph.fetch_news", new_callable=AsyncMock) as mock_n, \
         patch("src.graph.fetch_news_broad", new_callable=AsyncMock) as mock_nb, \
         patch("src.graph._synthesize_brief", new_callable=AsyncMock) as mock_s:

        mock_f.return_value = FilingData(
            ticker="SCOM", company_name="Safaricom PLC", period="FY2024",
            revenue_growth_pct=11.0
        )
        mock_m.return_value = MarketData(ticker="SCOM")
        mock_n.return_value = NewsData(
            ticker="SCOM", company_name="Safaricom PLC",
            overall_sentiment="neutral", articles=_make_articles(1)
        )
        mock_nb.return_value = NewsData(
            ticker="SCOM", company_name="Safaricom PLC",
            overall_sentiment="positive", articles=_make_articles(5)
        )
        mock_s.return_value = _make_brief("SCOM", "Safaricom PLC")

        steps = []
        async for event in run_research_pipeline("SCOM", "Safaricom PLC"):
            if event["type"] == "step":
                steps.append(event["data"])

        assert mock_nb.called
        assert len(steps) == 9
        messages = [s["message"] for s in steps]
        assert any("retry" in m.lower() or "broader" in m.lower() for m in messages)
