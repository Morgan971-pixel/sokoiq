import json
from datetime import datetime
from typing import AsyncGenerator
from anthropic import AsyncAnthropic
from src.config import settings
from src.models import FilingData, MarketData, NewsData, InvestmentBrief, AgentStep
from src.tools.nse_filings import fetch_filing
from src.tools.market_data import fetch_market_data
from src.tools.news_fetcher import fetch_news

client = AsyncAnthropic(api_key=settings.anthropic_api_key)


async def _synthesize_brief(
    ticker: str,
    company_name: str,
    filing: FilingData,
    market: MarketData,
    news: NewsData,
) -> InvestmentBrief:
    prompt = f"""You are an equity research analyst. Based on the following data for {company_name} ({ticker}),
write a structured investment brief. Respond ONLY with valid JSON matching this schema exactly:
{{
  "recommendation": "BUY" | "HOLD" | "SELL" | "NEUTRAL",
  "confidence": <float 0.0-1.0>,
  "thesis": "<one paragraph investment thesis>",
  "financials_summary": "<2-3 sentences on financial performance>",
  "market_summary": "<2-3 sentences on price performance>",
  "news_summary": "<2-3 sentences on recent news and sentiment>",
  "key_risks": ["<risk 1>", "<risk 2>", "<risk 3>"],
  "citations": ["{filing.source_url}"]
}}

FILING DATA:
Period: {filing.period}
Revenue growth: {filing.revenue_growth_pct}%
Profit growth: {filing.profit_growth_pct}%
Key risks from filing: {filing.key_risks}
Management commentary: {filing.management_commentary[:300]}

MARKET DATA:
Current price: KES {market.current_price_kes}
30-day return: {market.return_30d_pct}%
90-day return: {market.return_90d_pct}%
Trend: {market.trend}

NEWS SENTIMENT:
Overall: {news.overall_sentiment}
Drivers: {news.sentiment_drivers}

Respond with JSON only. No markdown. No explanation."""

    response = await client.messages.create(
        model="claude-haiku-3-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    data = json.loads(raw)
    return InvestmentBrief(
        ticker=ticker,
        company_name=company_name,
        generated_at=datetime.utcnow().isoformat() + "Z",
        **data,
    )


async def run_research_pipeline(
    ticker: str, company_name: str
) -> AsyncGenerator[dict, None]:
    yield {"type": "step", "data": AgentStep(
        agent="filing_analyst", status="running",
        message=f"Fetching NSE filings for {company_name}..."
    ).model_dump()}

    filing = await fetch_filing(ticker, company_name)

    yield {"type": "step", "data": AgentStep(
        agent="filing_analyst", status="done",
        message=f"Extracted filing data for {filing.period}",
        data={"revenue_growth_pct": filing.revenue_growth_pct,
              "profit_growth_pct": filing.profit_growth_pct}
    ).model_dump()}

    yield {"type": "step", "data": AgentStep(
        agent="market_analyst", status="running",
        message=f"Fetching market data for {ticker}..."
    ).model_dump()}

    market = await fetch_market_data(ticker)

    yield {"type": "step", "data": AgentStep(
        agent="market_analyst", status="done",
        message=f"Market trend: {market.trend} | 30d return: {market.return_30d_pct}%",
        data={"trend": market.trend, "return_30d_pct": market.return_30d_pct}
    ).model_dump()}

    yield {"type": "step", "data": AgentStep(
        agent="news_analyst", status="running",
        message=f"Fetching news and sentiment for {company_name}..."
    ).model_dump()}

    news = await fetch_news(ticker)

    yield {"type": "step", "data": AgentStep(
        agent="news_analyst", status="done",
        message=f"Sentiment: {news.overall_sentiment} across {len(news.articles)} articles",
        data={"overall_sentiment": news.overall_sentiment,
              "article_count": len(news.articles)}
    ).model_dump()}

    yield {"type": "step", "data": AgentStep(
        agent="memo_writer", status="running",
        message="Synthesizing investment brief..."
    ).model_dump()}

    try:
        brief = await _synthesize_brief(ticker, company_name, filing, market, news)
        yield {"type": "step", "data": AgentStep(
            agent="memo_writer", status="done",
            message=f"Brief complete: {brief.recommendation} (confidence: {brief.confidence:.0%})"
        ).model_dump()}
        yield {"type": "brief", "data": brief.model_dump()}
    except Exception as e:
        yield {"type": "step", "data": AgentStep(
            agent="memo_writer", status="error",
            message=f"Synthesis failed: {str(e)[:200]}"
        ).model_dump()}
