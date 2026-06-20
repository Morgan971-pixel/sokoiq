"""
Realistic demo data for all 5 NSE companies.
Used when network tools return empty results or for offline demos.
"""
from src.models import FilingData, MarketData, NewsData, NewsItem

DEMO_FILINGS: dict[str, FilingData] = {
    "SCOM": FilingData(
        ticker="SCOM",
        company_name="Safaricom PLC",
        period="FY2024",
        revenue_growth_pct=11.2,
        profit_growth_pct=8.4,
        key_risks=[
            "Intensifying competition from Airtel and Telkom Kenya",
            "Regulatory scrutiny on M-Pesa transaction fees",
            "Macroeconomic headwinds reducing consumer spending",
        ],
        management_commentary=(
            "The Board remains confident in the long-term growth trajectory of M-Pesa "
            "and our enterprise segment. We have invested KES 28 billion in network "
            "infrastructure and expect this to underpin revenue growth in FY2025."
        ),
        raw_excerpt=(
            "Revenue for the year ended 31 March 2024 grew by 11.2% to KES 340.1 billion. "
            "Profit before tax increased by 8.4% year-on-year to KES 74.3 billion. "
            "M-Pesa revenue grew 16.3% driven by merchant and international transfers."
        ),
        source_url="https://www.safaricom.co.ke/investor-relations/annual-reports",
    ),
    "EQTY": FilingData(
        ticker="EQTY",
        company_name="Equity Group Holdings",
        period="FY2023",
        revenue_growth_pct=14.1,
        profit_growth_pct=12.3,
        key_risks=[
            "Non-performing loans rising across the DRC and South Sudan subsidiaries",
            "Currency depreciation in subsidiary markets (Uganda, Rwanda, DRC)",
            "Regulatory capital requirements tightening in Kenya",
        ],
        management_commentary=(
            "Our pan-African diversification strategy continues to deliver. "
            "The DRC subsidiary now contributes 18% of group profits. "
            "We are targeting 20% loan book growth in FY2024 while maintaining NPL below 8%."
        ),
        raw_excerpt=(
            "Net interest income grew 14.1% to KES 82.4 billion. "
            "Profit after tax rose 12.3% to KES 46.1 billion. "
            "The loan book expanded 19% to KES 890 billion across 7 African countries."
        ),
        source_url="https://www.equitygroupholdings.com/investor-relations",
    ),
    "KCB": FilingData(
        ticker="KCB",
        company_name="KCB Group PLC",
        period="FY2023",
        revenue_growth_pct=9.0,
        profit_growth_pct=6.8,
        key_risks=[
            "NPL ratio elevated at 18.5% due to National Bank of Kenya integration",
            "KCB Bank Rwanda and Tanzania subsidiaries operating below cost of capital",
            "Kenya government borrowing crowding out private sector credit",
        ],
        management_commentary=(
            "The integration of NBK is largely complete and we expect cost synergies "
            "of KES 3 billion in FY2024. Our digital platform KCB Mobi now has 9 million users."
        ),
        raw_excerpt=(
            "Total income grew 9.0% to KES 71.2 billion. "
            "Profit after tax increased 6.8% to KES 22.4 billion. "
            "NPL ratio improved slightly to 18.5% from 19.1% in prior year."
        ),
        source_url="https://ke.kcbgroup.com/investor-centre",
    ),
    "EABL": FilingData(
        ticker="EABL",
        company_name="East African Breweries",
        period="FY2024",
        revenue_growth_pct=-4.2,
        profit_growth_pct=-18.6,
        key_risks=[
            "Illicit alcohol trade capturing low-income consumer segment",
            "KES depreciation driving up imported raw material costs (malt, hops)",
            "Excise duty increases reducing volume demand",
            "Uganda Breweries margin compression",
        ],
        management_commentary=(
            "The operating environment in FY2024 was exceptionally challenging. "
            "We are accelerating our premiumisation strategy and cost reduction program "
            "to rebuild margins in FY2025."
        ),
        raw_excerpt=(
            "Net revenue declined 4.2% to KES 104.7 billion impacted by consumer down-trading. "
            "Operating profit fell 18.6% to KES 14.2 billion. "
            "Volume declined 7% due to illicit trade and consumer affordability pressures."
        ),
        source_url="https://www.eabl.com/investors",
    ),
    "KEGN": FilingData(
        ticker="KEGN",
        company_name="KenGen PLC",
        period="FY2024",
        revenue_growth_pct=6.3,
        profit_growth_pct=5.1,
        key_risks=[
            "Delayed KPLC payments creating liquidity constraints",
            "Geothermal drilling capex exceeding budget",
            "Hydrological risk — drought reducing hydro generation",
        ],
        management_commentary=(
            "KenGen generated 8,264 GWh in FY2024, up 4% from prior year. "
            "Our 83 MW Olkaria VI geothermal project is on track for commissioning in FY2026. "
            "We continue to advocate for timely settlement of KPLC receivables."
        ),
        raw_excerpt=(
            "Revenue grew 6.3% to KES 28.4 billion driven by higher tariffs. "
            "Profit before tax rose 5.1% to KES 9.8 billion. "
            "Geothermal now accounts for 73% of total installed capacity."
        ),
        source_url="https://www.kengen.co.ke/investor-relations",
    ),
}

DEMO_MARKETS: dict[str, MarketData] = {
    "SCOM": MarketData(
        ticker="SCOM",
        current_price_kes=36.50,
        return_30d_pct=4.2,
        return_90d_pct=9.1,
        volatility_30d=1.243,
        trend="bullish",
        data_source="demo",
    ),
    "EQTY": MarketData(
        ticker="EQTY",
        current_price_kes=54.30,
        return_30d_pct=6.8,
        return_90d_pct=14.3,
        volatility_30d=1.891,
        trend="bullish",
        data_source="demo",
    ),
    "KCB": MarketData(
        ticker="KCB",
        current_price_kes=38.20,
        return_30d_pct=1.1,
        return_90d_pct=-2.4,
        volatility_30d=1.105,
        trend="neutral",
        data_source="demo",
    ),
    "EABL": MarketData(
        ticker="EABL",
        current_price_kes=105.00,
        return_30d_pct=-8.3,
        return_90d_pct=-19.7,
        volatility_30d=2.341,
        trend="bearish",
        data_source="demo",
    ),
    "KEGN": MarketData(
        ticker="KEGN",
        current_price_kes=4.80,
        return_30d_pct=2.1,
        return_90d_pct=5.4,
        volatility_30d=0.987,
        trend="neutral",
        data_source="demo",
    ),
}

DEMO_NEWS: dict[str, NewsData] = {
    "SCOM": NewsData(
        ticker="SCOM",
        company_name="Safaricom PLC",
        articles=[
            NewsItem(headline="Safaricom M-Pesa revenue surges 16% on merchant growth", url="https://businessdailyafrica.com/demo", source="Business Daily", sentiment="positive"),
            NewsItem(headline="Safaricom expands Ethiopia operations, adds 4 million subscribers", url="https://businessdailyafrica.com/demo2", source="Business Daily", sentiment="positive"),
            NewsItem(headline="Safaricom faces regulatory review over M-Pesa fees", url="https://businessdailyafrica.com/demo3", source="Business Daily", sentiment="negative"),
        ],
        overall_sentiment="positive",
        sentiment_drivers=["M-Pesa surges 16% on merchant growth", "Ethiopia subscriber growth"],
    ),
    "EQTY": NewsData(
        ticker="EQTY",
        company_name="Equity Group Holdings",
        articles=[
            NewsItem(headline="Equity Group profit rises 12% on strong DRC growth", url="https://businessdailyafrica.com/demo", source="Business Daily", sentiment="positive"),
            NewsItem(headline="Equity Bank wins best bank in East Africa award", url="https://businessdailyafrica.com/demo2", source="Business Daily", sentiment="positive"),
        ],
        overall_sentiment="positive",
        sentiment_drivers=["DRC subsidiary profit growth", "Regional expansion award"],
    ),
    "KCB": NewsData(
        ticker="KCB",
        company_name="KCB Group PLC",
        articles=[
            NewsItem(headline="KCB Group completes National Bank integration, targets synergies", url="https://businessdailyafrica.com/demo", source="Business Daily", sentiment="positive"),
            NewsItem(headline="KCB NPL ratio improves but remains elevated at 18.5%", url="https://businessdailyafrica.com/demo2", source="Business Daily", sentiment="negative"),
        ],
        overall_sentiment="neutral",
        sentiment_drivers=["NBK integration complete", "NPL ratio still elevated"],
    ),
    "EABL": NewsData(
        ticker="EABL",
        company_name="East African Breweries",
        articles=[
            NewsItem(headline="EABL profit falls 19% as illicit alcohol erodes volumes", url="https://businessdailyafrica.com/demo", source="Business Daily", sentiment="negative"),
            NewsItem(headline="East African Breweries loses market share to cheaper alternatives", url="https://businessdailyafrica.com/demo2", source="Business Daily", sentiment="negative"),
            NewsItem(headline="EABL launches premiumisation drive to rebuild margins", url="https://businessdailyafrica.com/demo3", source="Business Daily", sentiment="positive"),
        ],
        overall_sentiment="negative",
        sentiment_drivers=["Profit falls 19%", "Market share loss to illicit alcohol"],
    ),
    "KEGN": NewsData(
        ticker="KEGN",
        company_name="KenGen PLC",
        articles=[
            NewsItem(headline="KenGen Olkaria VI geothermal plant on track for 2026", url="https://businessdailyafrica.com/demo", source="Business Daily", sentiment="positive"),
            NewsItem(headline="KenGen awaits KPLC payment for KES 12 billion receivables", url="https://businessdailyafrica.com/demo2", source="Business Daily", sentiment="negative"),
        ],
        overall_sentiment="neutral",
        sentiment_drivers=["Geothermal expansion on track", "KPLC payment delays"],
    ),
}
