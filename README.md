# SokoIQ

AI-powered equity research platform for the Nairobi Securities Exchange. A 4-agent LangGraph pipeline fetches real-time financial data, runs sentiment analysis, and synthesizes investment briefs via Claude Haiku, delivered to a Next.js UI over WebSocket.

## Architecture

```
Browser (Next.js)
    |  WebSocket  |
FastAPI + uvicorn
    |
LangGraph pipeline
    |           |           |
Filing Agent  Market Agent  News Agent
    |               |           |
Google News    afx.kwayisi.org  Google News
RSS (financials)  (NSE prices)   RSS (sentiment)
    |
Memo Writer (Claude Haiku)
    |
InvestmentBrief
```

**Four agents run sequentially, each yielding a step event before and after its work:**

| Agent | Data source | Output |
|---|---|---|
| Filing Analyst | Google News RSS (financial headlines) | Revenue/profit growth %, reporting period |
| Market Analyst | afx.kwayisi.org (live NSE prices) | Current price KES, 30d/90d returns, trend |
| News Analyst | Google News RSS (sentiment search) | Article sentiment, overall tone |
| Memo Writer | Claude Haiku | BUY/HOLD/SELL/NEUTRAL brief with thesis |

**Covered companies:** Safaricom (SCOM), Equity Group (EQTY), KCB Group (KCB), East African Breweries (EABL), KenGen (KEGN)

## Stack

- **Backend:** Python 3.11, FastAPI, LangGraph, Anthropic SDK, httpx, BeautifulSoup4
- **Frontend:** Next.js 14 (App Router), React 18, TypeScript, Tailwind CSS
- **Transport:** WebSocket (FastAPI native), JSON event frames
- **Testing:** pytest, asyncio mode=auto (54 tests)

## Running locally

### Prerequisites

- Python 3.11+
- Node 18+
- Anthropic API key

### Backend

```bash
cd sokoiq/backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create sokoiq/.env
echo "ANTHROPIC_API_KEY=your_key_here" > ../.env

uvicorn src.api:app --port 8000 --reload
```

### Frontend

```bash
cd sokoiq/frontend
npm install
npm run dev
```

Open `http://localhost:3000`, click a company, then **Run Research**.

### Demo mode (no API key needed)

Add `?demo=true` to any research URL:

```
http://localhost:3000/research/SCOM?demo=true
```

Demo mode uses hardcoded data and rule-based brief synthesis. No network calls, no API credits.

You can also run the eval harness in demo mode:

```bash
cd sokoiq
source backend/venv/bin/activate
python evals/eval_briefs.py --demo
```

### Tests

```bash
cd sokoiq/backend
source venv/bin/activate
pytest
```

54 tests covering models, tools (filing/market/news parsers as pure functions), graph pipeline, API endpoints, agent retry logic, and SQLite persistence.

### Brief history

After running live research (not demo mode), briefs are stored in `sokoiq/backend/sokoiq.db`. View all past briefs at:

```
http://localhost:3000/history
```

History is also available via the REST API:

```bash
curl http://localhost:8000/history
curl "http://localhost:8000/history?ticker=SCOM"
```

## Project structure

```
sokoiq/
  backend/
    src/
      api.py            FastAPI app, WebSocket endpoint
      graph.py          LangGraph pipeline (async generator)
      config.py         pydantic-settings, reads sokoiq/.env
      models.py         Pydantic models: FilingData, MarketData, NewsData, InvestmentBrief
      demo_data.py      Hardcoded data for demo mode
      ws_manager.py     ConnectionManager for WebSocket rooms
      db.py             SQLite persistence: save and query InvestmentBriefs
      tools/
        nse_filings.py  Google News RSS financial extraction
        market_data.py  afx.kwayisi.org HTML parser
        news_fetcher.py Google News RSS sentiment parser
    tests/              54 pytest tests
  frontend/
    app/
      layout.tsx                Root layout with nav bar (Companies + History)
      page.tsx                  Company grid (fetches /companies)
      research/[ticker]/        Research page, WebSocket client
      history/page.tsx          History page: past briefs list
    components/
      AgentFeed.tsx             Streaming step log with status icons
      BriefPanel.tsx            Brief display: recommendation badge, 3-column layout
    lib/
      ws.ts                     createResearchSocket() factory
      types.ts                  TypeScript discriminated unions for WsEvent
      api.ts                    getCompanies() and getHistory() REST clients
  evals/
    eval_briefs.py              Runs all 5 companies, saves JSON + summary
  .env                          ANTHROPIC_API_KEY (gitignored)
```

## Data sources

| Source | What | Why |
|---|---|---|
| Google News RSS | Financial metrics, news sentiment | Free, no auth, 100 articles per search, structured XML |
| afx.kwayisi.org | NSE live prices, 4-week/3-month returns | Free, server-rendered HTML, all 5 tickers confirmed |

Financial metrics (revenue growth, profit growth) are extracted from news headlines using regex with bidirectional pattern matching. For live mode with a valid API key, Claude synthesizes the final brief from all three data inputs.

## Backtest baseline

Snapshot captured 2026-06-20 using live data (afx.kwayisi.org prices, Google News RSS financials and sentiment). Recommendations from rule-based synthesis; LLM synthesis requires a valid API key.

| Ticker | Company | Rec | Confidence | Price (KES) | 30d Return | Sentiment | 30d Outcome |
|--------|---------|-----|-----------|-------------|-----------|-----------|-------------|
| SCOM | Safaricom PLC | HOLD | 61% | 32.65 | +6.87% | neutral | TBD 2026-07-20 |
| EQTY | Equity Group Holdings | HOLD | 61% | 80.00 | +6.31% | positive | TBD 2026-07-20 |
| KCB | KCB Group PLC | NEUTRAL | 50% | 73.25 | +9.74% | positive | TBD 2026-07-20 |
| EABL | East African Breweries | HOLD | 61% | 273.25 | +11.40% | neutral | TBD 2026-07-20 |
| KEGN | KenGen PLC | NEUTRAL | 50% | 9.12 | -0.65% | neutral | TBD 2026-07-20 |

Check afx.kwayisi.org on 2026-07-20, fill in the 30d Outcome column, and compute whether recommendations aligned with price direction.
