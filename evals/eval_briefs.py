"""
Run the research pipeline against all 5 NSE companies and save the outputs.

Usage:
    cd sokoiq
    source backend/venv/bin/activate
    python evals/eval_briefs.py           # live mode (requires API credits + network)
    python evals/eval_briefs.py --demo    # demo mode (no network, no API credits needed)

Outputs:
    evals/eval_results.json  — raw brief JSON for all companies
    evals/eval_summary.txt   — human-readable summary for rubric scoring
"""
import asyncio
import json
import pathlib
import sys

sys.path.insert(0, str(pathlib.Path(__file__).parent.parent / "backend"))

DEMO_MODE = "--demo" in sys.argv

from src.graph import run_research_pipeline
from src.models import COMPANIES

EVALS_DIR = pathlib.Path(__file__).parent


async def run_evals() -> list[dict]:
    results = []
    failed = []

    for company in COMPANIES:
        print(f"\n{'='*60}")
        print(f"  {company.ticker}  {company.company_name}")
        print(f"{'='*60}")

        brief = None
        try:
            async for event in run_research_pipeline(
                company.ticker, company.company_name, demo=DEMO_MODE
            ):
                if event["type"] == "step":
                    d = event["data"]
                    icon = {"running": "...", "done": "OK ", "error": "ERR"}[d["status"]]
                    print(f"  [{icon}] {d['agent']}: {d['message']}")
                elif event["type"] == "brief":
                    brief = event["data"]
        except Exception as exc:
            print(f"  [ERR] pipeline exception: {exc}")

        if brief:
            results.append(brief)
            rec = brief["recommendation"]
            conf = brief["confidence"]
            print(f"\n  RESULT: {rec}  (confidence {conf:.0%})")
            print(f"  Thesis: {brief['thesis'][:120]}...")
        else:
            failed.append(company.ticker)
            print(f"\n  FAILED: no brief generated")

    results_path = EVALS_DIR / "eval_results.json"
    with open(results_path, "w") as f:
        json.dump(results, f, indent=2)

    summary_path = EVALS_DIR / "eval_summary.txt"
    with open(summary_path, "w") as f:
        f.write("SokoIQ Eval Summary\n")
        f.write("=" * 60 + "\n\n")
        for b in results:
            f.write(f"{b['ticker']}  {b['company_name']}\n")
            f.write(f"  Recommendation : {b['recommendation']}  (confidence {b['confidence']:.0%})\n")
            f.write(f"  Thesis         : {b['thesis']}\n")
            f.write(f"  Financials     : {b['financials_summary']}\n")
            f.write(f"  Market         : {b['market_summary']}\n")
            f.write(f"  News           : {b['news_summary']}\n")
            f.write(f"  Key risks      : {'; '.join(b['key_risks'])}\n")
            f.write(f"  Citations      : {'; '.join(b['citations'])}\n")
            f.write("\n")
        if failed:
            f.write(f"FAILED tickers: {', '.join(failed)}\n")

    print(f"\n{'='*60}")
    print(f"Saved {len(results)}/5 briefs to {results_path}")
    print(f"Summary written to {summary_path}")
    if failed:
        print(f"Failed: {', '.join(failed)}")

    return results


if __name__ == "__main__":
    mode = "DEMO" if DEMO_MODE else "LIVE"
    print(f"SokoIQ Eval  [{mode} MODE]")
    asyncio.run(run_evals())
