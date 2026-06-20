from pydantic import BaseModel, Field
from typing import Literal
from datetime import datetime


class CompanyTicker(BaseModel):
    ticker: str
    company_name: str


COMPANIES: list[CompanyTicker] = [
    CompanyTicker(ticker="SCOM", company_name="Safaricom PLC"),
    CompanyTicker(ticker="EQTY", company_name="Equity Group Holdings"),
    CompanyTicker(ticker="KCB", company_name="KCB Group PLC"),
    CompanyTicker(ticker="EABL", company_name="East African Breweries"),
    CompanyTicker(ticker="KEGN", company_name="KenGen PLC"),
]

TICKER_MAP = {c.ticker: c.company_name for c in COMPANIES}


class FilingData(BaseModel):
    ticker: str
    company_name: str
    period: str
    revenue_growth_pct: float | None = None
    profit_growth_pct: float | None = None
    key_risks: list[str] = Field(default_factory=list)
    management_commentary: str = ""
    raw_excerpt: str = ""
    source_url: str = ""


class MarketData(BaseModel):
    ticker: str
    current_price_kes: float | None = None
    return_30d_pct: float | None = None
    return_90d_pct: float | None = None
    volatility_30d: float | None = None
    trend: Literal["bullish", "bearish", "neutral"] = "neutral"
    data_source: str = ""


class NewsItem(BaseModel):
    headline: str
    url: str
    source: str
    sentiment: Literal["positive", "negative", "neutral"] = "neutral"


class NewsData(BaseModel):
    ticker: str
    company_name: str
    articles: list[NewsItem] = Field(default_factory=list)
    overall_sentiment: Literal["positive", "negative", "neutral"] = "neutral"
    sentiment_drivers: list[str] = Field(default_factory=list)


class InvestmentBrief(BaseModel):
    ticker: str
    company_name: str
    generated_at: str
    recommendation: Literal["BUY", "HOLD", "SELL", "NEUTRAL"]
    confidence: float = Field(ge=0.0, le=1.0)
    thesis: str
    financials_summary: str
    market_summary: str
    news_summary: str
    key_risks: list[str] = Field(default_factory=list)
    citations: list[str] = Field(default_factory=list)


class AgentStep(BaseModel):
    agent: str
    status: Literal["running", "done", "error"]
    message: str
    data: dict = Field(default_factory=dict)
