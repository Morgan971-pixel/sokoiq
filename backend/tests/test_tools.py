import pytest
from src.models import COMPANIES
from src.tools.nse_filings import parse_filing_text, NSE_FILING_URLS, extract_financials_from_rss
from src.tools.market_data import compute_returns, parse_afx_html
from src.tools.news_fetcher import classify_sentiment, build_news_data, parse_rss_feed


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
    for company in COMPANIES:
        assert company.ticker in NSE_FILING_URLS, \
            f"Missing filing URL for {company.ticker}"


def test_parse_filing_text_empty_gracefully():
    result = parse_filing_text("SCOM", "Safaricom PLC", "")
    assert result.ticker == "SCOM"
    assert result.raw_excerpt == ""


FINANCIAL_NEWS_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Safaricom results - Google News</title>
    <item>
      <title>Safaricom reports 11% revenue growth to KES 340 billion for FY2024</title>
      <link>https://businessdailyafrica.com/article/safaricom-fy2024</link>
      <source>Business Daily Africa</source>
      <description>Safaricom PLC recorded profit before tax growth of 8% year on year.</description>
    </item>
    <item>
      <title>Safaricom faces regulatory pressure over M-Pesa dominance in FY2024</title>
      <link>https://reuters.com/article/safaricom</link>
      <source>Reuters</source>
      <description>Competition risk and regulatory scrutiny remain key concerns.</description>
    </item>
  </channel>
</rss>"""


def test_extract_financials_revenue_pct():
    result = extract_financials_from_rss("SCOM", "Safaricom PLC", FINANCIAL_NEWS_RSS)
    assert result.revenue_growth_pct == 11.0


def test_extract_financials_profit_pct():
    result = extract_financials_from_rss("SCOM", "Safaricom PLC", FINANCIAL_NEWS_RSS)
    assert result.profit_growth_pct == 8.0


def test_extract_financials_period_detected():
    result = extract_financials_from_rss("SCOM", "Safaricom PLC", FINANCIAL_NEWS_RSS)
    assert "2024" in result.period


def test_extract_financials_source_url_set():
    result = extract_financials_from_rss("SCOM", "Safaricom PLC", FINANCIAL_NEWS_RSS)
    assert result.source_url != ""


def test_extract_financials_empty_rss():
    empty = '<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>'
    result = extract_financials_from_rss("SCOM", "Safaricom PLC", empty)
    assert result.ticker == "SCOM"
    assert result.revenue_growth_pct is None
    assert result.profit_growth_pct is None


def test_extract_financials_malformed_xml():
    result = extract_financials_from_rss("SCOM", "Safaricom PLC", "not xml <<<")
    assert result.ticker == "SCOM"
    assert result.revenue_growth_pct is None


def test_compute_returns_positive_trend():
    prices = [100.0, 102.0, 105.0, 103.0, 108.0]
    result = compute_returns("SCOM", prices)
    assert result.trend == "bullish"
    assert result.return_30d_pct == pytest.approx(8.0, abs=0.1)
    assert result.current_price_kes == 108.0


def test_compute_returns_empty_list():
    result = compute_returns("SCOM", [])
    assert result.return_30d_pct is None
    assert result.trend == "neutral"
    assert result.current_price_kes is None


def test_compute_returns_declining():
    prices = [100.0, 98.0, 95.0, 92.0, 90.0]
    result = compute_returns("SCOM", prices)
    assert result.trend == "bearish"
    assert result.return_30d_pct == pytest.approx(-10.0, abs=0.1)


SAMPLE_AFX_HTML = """
<html><body>
<table>
  <tr><th>Last Trading Results</th></tr>
  <tr><td>Day's Low Price</td><td>32.20</td></tr>
  <tr><td>Day's High Price</td><td>32.80</td></tr>
</table>
<table>
  <tr><th>1WK</th><th>4WK</th><th>3MO</th></tr>
  <tr><td>+4.82%</td><td>+6.87%</td><td>+7.76%</td></tr>
</table>
<table>
  <tr><th>Date</th><th>Volume</th><th>Close</th><th>Change</th><th>Change%</th></tr>
  <tr><td>2026-06-19</td><td>3,924,397</td><td>32.65</td><td>+0.65</td><td>+2.03%</td></tr>
  <tr><td>2026-06-18</td><td>8,879,487</td><td>32.00</td><td>+0.10</td><td>+0.31%</td></tr>
  <tr><td>2026-06-17</td><td>27,036,284</td><td>31.90</td><td>+0.15</td><td>+0.47%</td></tr>
</table>
</body></html>
"""

BEARISH_AFX_HTML = SAMPLE_AFX_HTML.replace("+6.87%", "-8.50%")


def test_parse_afx_current_price():
    result = parse_afx_html("SCOM", SAMPLE_AFX_HTML)
    assert result.current_price_kes == 32.65


def test_parse_afx_30d_return():
    result = parse_afx_html("SCOM", SAMPLE_AFX_HTML)
    assert result.return_30d_pct == pytest.approx(6.87)


def test_parse_afx_90d_return():
    result = parse_afx_html("SCOM", SAMPLE_AFX_HTML)
    assert result.return_90d_pct == pytest.approx(7.76)


def test_parse_afx_bullish_trend():
    result = parse_afx_html("SCOM", SAMPLE_AFX_HTML)
    assert result.trend == "bullish"


def test_parse_afx_bearish_trend():
    result = parse_afx_html("SCOM", BEARISH_AFX_HTML)
    assert result.trend == "bearish"


def test_parse_afx_empty_html():
    result = parse_afx_html("SCOM", "<html><body></body></html>")
    assert result.ticker == "SCOM"
    assert result.current_price_kes is None
    assert result.trend == "neutral"


def test_classify_sentiment_positive():
    assert classify_sentiment("Company reports strong profit growth") == "positive"


def test_classify_sentiment_negative():
    assert classify_sentiment("Company issues profit warning amid losses") == "negative"


def test_classify_sentiment_neutral():
    assert classify_sentiment("Company holds annual general meeting") == "neutral"


def test_classify_sentiment_tied_returns_neutral():
    assert classify_sentiment("strong loss") == "neutral"


def test_build_news_data_no_articles():
    result = build_news_data("SCOM", "Safaricom PLC", [])
    assert result.overall_sentiment == "neutral"
    assert result.articles == []


SAMPLE_RSS = """<?xml version="1.0" encoding="UTF-8"?>
<rss version="2.0">
  <channel>
    <title>Safaricom Kenya - Google News</title>
    <item>
      <title>Safaricom profit surges on strong M-Pesa growth</title>
      <link>https://news.google.com/article/1</link>
      <source url="https://businessdailyafrica.com">Business Daily Africa</source>
    </item>
    <item>
      <title>Safaricom faces regulatory warning over data practices</title>
      <link>https://news.google.com/article/2</link>
      <source url="https://reuters.com">Reuters</source>
    </item>
    <item>
      <title>Safaricom holds annual general meeting in Nairobi</title>
      <link>https://news.google.com/article/3</link>
      <source url="https://standardmedia.co.ke">The Standard</source>
    </item>
  </channel>
</rss>"""


def test_parse_rss_extracts_correct_article_count():
    result = parse_rss_feed("SCOM", "Safaricom PLC", SAMPLE_RSS)
    assert len(result.articles) == 3


def test_parse_rss_extracts_headline_and_source():
    result = parse_rss_feed("SCOM", "Safaricom PLC", SAMPLE_RSS)
    assert result.articles[0].headline == "Safaricom profit surges on strong M-Pesa growth"
    assert result.articles[0].source == "Business Daily Africa"


def test_parse_rss_sentiment_per_article():
    result = parse_rss_feed("SCOM", "Safaricom PLC", SAMPLE_RSS)
    assert result.articles[0].sentiment == "positive"
    assert result.articles[1].sentiment == "negative"
    assert result.articles[2].sentiment == "neutral"


def test_parse_rss_overall_sentiment():
    result = parse_rss_feed("SCOM", "Safaricom PLC", SAMPLE_RSS)
    assert result.overall_sentiment == "neutral"


def test_parse_rss_empty_feed():
    empty = '<?xml version="1.0"?><rss version="2.0"><channel></channel></rss>'
    result = parse_rss_feed("SCOM", "Safaricom PLC", empty)
    assert result.overall_sentiment == "neutral"
    assert result.articles == []


def test_parse_rss_malformed_xml_returns_neutral():
    result = parse_rss_feed("SCOM", "Safaricom PLC", "not xml at all <<<")
    assert result.overall_sentiment == "neutral"
    assert result.articles == []
