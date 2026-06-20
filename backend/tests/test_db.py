import sqlite3
from datetime import datetime, timezone
from src.db import get_briefs, init_db, save_brief
from src.models import InvestmentBrief


def _brief(ticker: str = "SCOM", rec: str = "BUY") -> InvestmentBrief:
    return InvestmentBrief(
        ticker=ticker,
        company_name="Safaricom PLC",
        generated_at=datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        recommendation=rec,
        confidence=0.78,
        thesis="Strong growth.",
        financials_summary="Revenue up 11%.",
        market_summary="Price up 6%.",
        news_summary="Positive sentiment.",
        key_risks=["competition"],
        citations=[],
    )


def test_init_db_creates_briefs_table(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    with sqlite3.connect(db) as conn:
        tables = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table'"
        ).fetchall()
    assert any(t[0] == "briefs" for t in tables)


def test_init_db_is_idempotent(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    init_db(db)  # second call must not raise


def test_save_brief_returns_uuid(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    brief_id = save_brief(_brief(), db_path=db)
    assert isinstance(brief_id, str)
    assert len(brief_id) == 36  # UUID4


def test_get_briefs_returns_all(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    save_brief(_brief("SCOM"), db_path=db)
    save_brief(_brief("EQTY"), db_path=db)
    results = get_briefs(db_path=db)
    assert len(results) == 2


def test_get_briefs_filters_by_ticker(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    save_brief(_brief("SCOM"), db_path=db)
    save_brief(_brief("EQTY"), db_path=db)
    results = get_briefs(ticker="SCOM", db_path=db)
    assert len(results) == 1
    assert results[0]["ticker"] == "SCOM"


def test_get_briefs_empty_db(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    assert get_briefs(db_path=db) == []


def test_get_briefs_row_has_expected_fields(tmp_path):
    db = tmp_path / "test.db"
    init_db(db)
    save_brief(_brief(), db_path=db)
    row = get_briefs(db_path=db)[0]
    for field in ("id", "ticker", "company_name", "recommendation", "confidence", "thesis", "generated_at"):
        assert field in row
