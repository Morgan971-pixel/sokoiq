import json
import re
from datetime import datetime, timezone
from typing import AsyncGenerator
from anthropic import AsyncAnthropic
from src.config import settings
from src.models import FilingData, MarketData, NewsData, InvestmentBrief, AgentStep
from src.tools.nse_filings import fetch_filing
from src.tools.market_data import fetch_market_data
from src.tools.news_fetcher import fetch_news


def _synthesize_brief_local(
    ticker: str,
    company_name: str,
    filing: FilingData,
    market: MarketData,
    news: NewsData,
) -> InvestmentBrief:
    """Rule-based brief synthesis — no API required. Used in demo mode."""
    rev = filing.revenue_growth_pct or 0.0
    pft = filing.profit_growth_pct or 0.0
    ret30 = market.return_30d_pct or 0.0
    sent = news.overall_sentiment

    if rev > 8 and pft > 5 and ret30 > 2 and sent == "positive":
        recommendation, confidence = "BUY", 0.78
    elif rev < 0 or (sent == "negative" and ret30 < -5):
        recommendation, confidence = "SELL", 0.72
    elif rev > 4 and ret30 > 0:
        recommendation, confidence = "HOLD", 0.61
    else:
        recommendation, confidence = "NEUTRAL", 0.50

    thesis = (
        f"{company_name} ({ticker}) shows {filing.period} revenue growth of {rev:.1f}% "
        f"and profit growth of {pft:.1f}%. The share trades at KES {market.current_price_kes} "
        f"with a 30-day return of {ret30:+.1f}%, reflecting a {market.trend} trend. "
        f"News sentiment is {sent}. "
        f"Based on these signals, a {recommendation} recommendation is warranted "
        f"with {confidence:.0%} confidence."
    )

    return InvestmentBrief(
        ticker=ticker,
        company_name=company_name,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        recommendation=recommendation,
        confidence=confidence,
        thesis=thesis,
        financials_summary=(
            f"Revenue grew {rev:.1f}% and profit grew {pft:.1f}% in {filing.period}. "
            f"{filing.raw_excerpt[:200]}"
        ),
        market_summary=(
            f"Current price KES {market.current_price_kes}. "
            f"30-day return {ret30:+.1f}%, 90-day return {market.return_90d_pct or 0:+.1f}%. "
            f"Trend: {market.trend}."
        ),
        news_summary=(
            f"Overall sentiment {sent} based on {len(news.articles)} articles. "
            f"Key drivers: {'; '.join(news.sentiment_drivers[:2]) or 'no data'}."
        ),
        key_risks=filing.key_risks[:3] or ["Insufficient data for risk assessment"],
        citations=[filing.source_url] if filing.source_url else [],
    )


def _get_client() -> AsyncAnthropic:
    if not settings.anthropic_api_key:
        raise RuntimeError("ANTHROPIC_API_KEY is not set in environment")
    return AsyncAnthropic(api_key=settings.anthropic_api_key)


async def _synthesize_brief(
    ticker: str,
    company_name: str,
    filing: FilingData,
    market: MarketData,
    news: NewsData,
) -> InvestmentBrief:
    source_url = filing.source_url or "N/A"
    commentary = filing.management_commentary[:300]
    if len(filing.management_commentary) > 300:
        commentary += "..."

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
  "citations": ["<source url>"]
}}

FILING DATA:
Period: {filing.period}
Revenue growth: {filing.revenue_growth_pct}%
Profit growth: {filing.profit_growth_pct}%
Key risks from filing: {filing.key_risks}
Management commentary: {commentary}
Source URL: {source_url}

MARKET DATA:
Current price: KES {market.current_price_kes}
30-day return: {market.return_30d_pct}%
90-day return: {market.return_90d_pct}%
Trend: {market.trend}

NEWS SENTIMENT:
Overall: {news.overall_sentiment}
Drivers: {news.sentiment_drivers}

Respond with JSON only. No markdown. No explanation."""

    client = _get_client()
    response = await client.messages.create(
        model="claude-haiku-3-5-20251001",
        max_tokens=1024,
        messages=[{"role": "user", "content": prompt}],
    )
    raw = response.content[0].text.strip()
    cleaned = re.sub(r"^```(?:json)?\s*|\s*```$", "", raw, flags=re.MULTILINE).strip()
    try:
        data = json.loads(cleaned)
    except json.JSONDecodeError as exc:
        raise ValueError(
            f"LLM returned invalid JSON: {exc}. Raw response: {raw[:400]!r}"
        ) from exc
    return InvestmentBrief(
        ticker=ticker,
        company_name=company_name,
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        **data,
    )


async def run_research_pipeline(
    ticker: str, company_name: str, demo: bool = False
) -> AsyncGenerator[dict, None]:
    if demo:
        from src.demo_data import DEMO_FILINGS, DEMO_MARKETS, DEMO_NEWS

        async def _fetch_filing(t: str, c: str) -> FilingData:
            return DEMO_FILINGS.get(t) or FilingData(ticker=t, company_name=c, period="Unknown")

        async def _fetch_market(t: str) -> MarketData:
            return DEMO_MARKETS.get(t) or MarketData(ticker=t)

        async def _fetch_news(t: str) -> NewsData:
            return DEMO_NEWS.get(t) or NewsData(ticker=t, company_name=company_name)
    else:
        async def _fetch_filing(t: str, c: str) -> FilingData:
            return await fetch_filing(t, c)

        async def _fetch_market(t: str) -> MarketData:
            return await fetch_market_data(t)

        async def _fetch_news(t: str) -> NewsData:
            return await fetch_news(t)

    yield {"type": "step", "data": AgentStep(
        agent="filing_analyst", status="running",
        message=f"Fetching NSE filings for {company_name}..."
    ).model_dump()}

    filing = await _fetch_filing(ticker, company_name)

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

    market = await _fetch_market(ticker)

    yield {"type": "step", "data": AgentStep(
        agent="market_analyst", status="done",
        message=f"Market trend: {market.trend} | 30d return: {market.return_30d_pct}%",
        data={"trend": market.trend, "return_30d_pct": market.return_30d_pct}
    ).model_dump()}

    yield {"type": "step", "data": AgentStep(
        agent="news_analyst", status="running",
        message=f"Fetching news and sentiment for {company_name}..."
    ).model_dump()}

    news = await _fetch_news(ticker)

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
        if demo:
            brief = _synthesize_brief_local(ticker, company_name, filing, market, news)
        else:
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
