"""
batch_runner.py — Run the full end-to-end pipeline on all 10 files.

Execution order:
  1. Pipeline A on all 5 demo transcripts    (generates v1 for each account)
  2. Pipeline B on all 5 onboarding transcripts (generates v2 for each account)
  3. Print a summary table

Usage:
  python batch_runner.py
  python batch_runner.py --pipeline a    # only Pipeline A
  python batch_runner.py --pipeline b    # only Pipeline B
"""

import argparse
import json
import logging
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Dict, Any

import config
import pipeline_a
import pipeline_b

logging.basicConfig(
    level=getattr(logging, config.LOG_LEVEL),
    format="%(asctime)s  %(levelname)-8s  %(name)s  %(message)s",
)
logger = logging.getLogger("batch_runner")


def _print_summary(results: List[Dict[str, Any]], label: str) -> None:
    """Pretty-print a summary table of pipeline results."""
    print(f"\n{'═'*60}")
    print(f"  {label} — Results")
    print(f"{'═'*60}")
    ok      = sum(1 for r in results if r.get("status") == "ok")
    skipped = sum(1 for r in results if r.get("status") == "skipped")
    errors  = sum(1 for r in results if r.get("status") == "error")

    for r in results:
        status = r.get("status", "?")
        icon   = {"ok": "✓", "skipped": "⚠", "error": "✗"}.get(status, "?")
        extra  = ""
        if r.get("changes_count") is not None:
            extra = f"  [{r['changes_count']} changes]"
        if r.get("error"):
            extra = f"  ERROR: {r['error'][:60]}"
        print(f"  {icon}  {r.get('account_id','?'):<20}  {r.get('company_name',''):<30}{extra}")

    print(f"{'─'*60}")
    print(f"  Total: {len(results)}  |  OK: {ok}  |  Skipped: {skipped}  |  Errors: {errors}")
    print(f"{'═'*60}\n")


def run_full_batch() -> Dict[str, Any]:
    """Run Pipeline A then Pipeline B across all accounts."""
    started = datetime.now(timezone.utc).isoformat()
    t0      = time.time()

    logger.info("▶ Starting full batch run")

    # ── Pipeline A ──────────────────────────────────────────────────────────
    logger.info("── Pipeline A: Demo → v1 ──")
    a_results = pipeline_a.run_all()
    _print_summary(a_results, "Pipeline A (Demo → v1)")

    # ── Pipeline B ──────────────────────────────────────────────────────────
    logger.info("── Pipeline B: Onboarding → v2 ──")
    b_results = pipeline_b.run_all()
    _print_summary(b_results, "Pipeline B (Onboarding → v2)")

    elapsed = round(time.time() - t0, 1)
    summary = {
        "started_at":       started,
        "elapsed_seconds":  elapsed,
        "pipeline_a":       a_results,
        "pipeline_b":       b_results,
        "totals": {
            "a_ok":     sum(1 for r in a_results if r.get("status") == "ok"),
            "a_errors": sum(1 for r in a_results if r.get("status") == "error"),
            "b_ok":     sum(1 for r in b_results if r.get("status") == "ok"),
            "b_errors": sum(1 for r in b_results if r.get("status") == "error"),
        },
    }

    # Save batch summary
    out = config.BASE_DIR / "batch_summary.json"
    out.write_text(json.dumps(summary, indent=2), encoding="utf-8")
    logger.info("Batch summary saved to %s", out)
    logger.info("Full batch complete in %ss ✓", elapsed)
    return summary


# ─── CLI ─────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Batch runner for Clara Pipeline")
    parser.add_argument(
        "--pipeline",
        choices=["a", "b", "all"],
        default="all",
        help="Which pipeline(s) to run (default: all)",
    )
    args = parser.parse_args()

    if args.pipeline == "a":
        results = pipeline_a.run_all()
        _print_summary(results, "Pipeline A")
    elif args.pipeline == "b":
        results = pipeline_b.run_all()
        _print_summary(results, "Pipeline B")
    else:
        summary = run_full_batch()
        print(json.dumps(summary["totals"], indent=2))
