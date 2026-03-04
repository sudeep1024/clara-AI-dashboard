"""
pipeline_a.py – Demo Call → Preliminary Retell Agent (v1)

Usage:
  python pipeline_a.py <path/to/transcript.txt> [--account-id ACC-001]
  python pipeline_a.py --all   (processes all files in data/transcripts/demo/)
"""

import argparse
import sys
from pathlib import Path

# Allow running from scripts/ dir
sys.path.insert(0, str(Path(__file__).parent))

from config import DEMO_DIR
from extractor import extract_memo
from prompt_generator import build_agent_spec
from utils import (
    account_dir, get_logger, infer_account_id,
    read_transcript, save_json, utcnow
)

log = get_logger("pipeline_a")


def run_demo(transcript_path: Path, account_id: str | None = None) -> dict:
    """
    Process a single demo transcript → v1 memo + agent spec.
    Returns a result summary dict.
    """
    account_id = account_id or infer_account_id(transcript_path.name)
    log.info("▶  Pipeline A | account=%s | file=%s", account_id, transcript_path.name)

    # 1. Read transcript
    transcript = read_transcript(transcript_path)

    # 2. Extract Account Memo
    log.info("   Extracting account memo via LLM...")
    memo = extract_memo(transcript, account_id)
    memo["_pipeline"] = "A"
    memo["_source_file"] = transcript_path.name
    memo["_extracted_at"] = utcnow()
    memo["_version"] = "v1"

    # 3. Build Agent Spec
    log.info("   Generating Retell agent spec...")
    spec = build_agent_spec(memo, version="v1")

    # 4. Save outputs
    out = account_dir(account_id, "v1")
    save_json(memo, out / "account_memo.json")
    save_json(spec, out / "agent_spec.json")
    log.info("   ✓ Saved v1 outputs → %s", out)

    return {"account_id": account_id, "status": "ok", "output_dir": str(out)}


def run_all() -> list[dict]:
    """Process every demo transcript found in DEMO_DIR."""
    files = sorted(DEMO_DIR.glob("*.txt"))
    if not files:
        log.warning("No .txt files found in %s", DEMO_DIR)
        return []
    results = []
    for f in files:
        try:
            r = run_demo(f)
            results.append(r)
        except Exception as exc:
            log.error("FAILED %s: %s", f.name, exc)
            results.append({"account_id": infer_account_id(f.name), "status": "error", "error": str(exc)})
    return results


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline A: Demo → v1 Agent")
    parser.add_argument("transcript", nargs="?", help="Path to a single transcript file")
    parser.add_argument("--account-id", help="Override inferred account_id")
    parser.add_argument("--all", action="store_true", help="Process all demo transcripts")
    args = parser.parse_args()

    if args.all:
        results = run_all()
        for r in results:
            status = "✓" if r["status"] == "ok" else "✗"
            print(f"  {status} {r['account_id']} → {r.get('output_dir', r.get('error'))}")
    elif args.transcript:
        result = run_demo(Path(args.transcript), args.account_id)
        print(f"Done → {result['output_dir']}")
    else:
        parser.print_help()
        sys.exit(1)
