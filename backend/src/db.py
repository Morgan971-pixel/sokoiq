import json
import sqlite3
import uuid
from pathlib import Path

from src.models import InvestmentBrief

_DEFAULT_DB_PATH = Path(__file__).parent.parent / "sokoiq.db"


def init_db(db_path: Path = _DEFAULT_DB_PATH) -> None:
    with sqlite3.connect(db_path) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS briefs (
                id           TEXT PRIMARY KEY,
                ticker       TEXT NOT NULL,
                company_name TEXT NOT NULL,
                recommendation TEXT NOT NULL,
                confidence   REAL NOT NULL,
                thesis       TEXT NOT NULL,
                generated_at TEXT NOT NULL,
                raw_json     TEXT NOT NULL
            )
        """)
        conn.commit()


def save_brief(brief: InvestmentBrief, db_path: Path = _DEFAULT_DB_PATH) -> str:
    brief_id = str(uuid.uuid4())
    with sqlite3.connect(db_path) as conn:
        conn.execute(
            """INSERT INTO briefs
               (id, ticker, company_name, recommendation, confidence, thesis, generated_at, raw_json)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                brief_id,
                brief.ticker,
                brief.company_name,
                brief.recommendation,
                brief.confidence,
                brief.thesis,
                brief.generated_at,
                json.dumps(brief.model_dump()),
            ),
        )
        conn.commit()
    return brief_id


def get_briefs(ticker: str | None = None, db_path: Path = _DEFAULT_DB_PATH) -> list[dict]:
    if not db_path.exists():
        return []
    with sqlite3.connect(db_path) as conn:
        conn.row_factory = sqlite3.Row
        if ticker:
            rows = conn.execute(
                "SELECT id, ticker, company_name, recommendation, confidence, thesis, generated_at"
                " FROM briefs WHERE ticker = ? ORDER BY generated_at DESC",
                (ticker,),
            ).fetchall()
        else:
            rows = conn.execute(
                "SELECT id, ticker, company_name, recommendation, confidence, thesis, generated_at"
                " FROM briefs ORDER BY generated_at DESC"
            ).fetchall()
    return [dict(r) for r in rows]
