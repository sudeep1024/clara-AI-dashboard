"""
pipeline_b.py – Onboarding Call → Updated Retell Agent (v2)

Loads the existing v1 memo, applies onboarding updates, produces v2 + changelog.

Usage:
  python pipeline_b.py <path/to/onboarding_transcript.txt> [--account-id ACC-001]
  python pipeline_b.py --all
"""

import argparse
import copy
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))

from config import ONBD_DIR, OUTPUT_DIR
from differ import generate_changelog
from extractor import extract_memo
from prompt_generator import build_agent_spec
from utils import (
    account_dir, get_logger, infer_account_id,
    load_json, read_transcript, save_json, utcnow
)

log = get_logger("pipeline_b")


# ─────────────────────────────────────────────────────────────────────────────
def _deep_merge(base: dict, updates: dict) -> dict:
    """
    Merge `updates` into `base`.
    - Scalars: update always wins (unless update is None/empty and base has a value).
    - Lists: update always replaces base (onboarding confirms).
    - Dicts: recursive merge.
    - questions_or_unknowns: union and deduplicate.
    - Resolved unknowns are removed from questions_or_unknowns.
    """
    result = copy.deepcopy(base)

    for key, new_val in updates.items():
        old_val = result.get(key)

        # Special: questions_or_unknowns → union
        if key == "questions_or_unknowns":
            merged = list(set((old_val or []) + (new_val or [])))
            result[key] = merged
            continue

        # Skip if update value is None/empty and base already has something
        if new_val is None or new_val == "" or new_val == []:
            continue

        if isinstance(new_val, dict) and isinstance(old_val, dict):
            result[key] = _deep_merge(old_val, new_val)
        else:
            result[key] = new_val

    # Remove questions that were answered by the update
    if result.get("questions_or_unknowns"):
        resolved = []
        for q in result["questions_or_unknowns"]:
            # If the question mentioned a field that now has a value, consider it resolved
            q_lower = q.lower()
            is_resolved = False
            for check_key in ["timezone", "address", "phone", "routing", "hours", "emergency"]:
                if check_key in q_lower:
                    # Check if the relevant field is now populated
                    if check_key == "timezone" and (result.get("business_hours") or {}).get("timezone"):
                        is_resolved = True; break
                    if check_key == "address" and result.get("office_address"):
                        is_resolved = True; break
                    if check_key in ["phone", "routing"] and result.get("emergency_routing_rules"):
                        is_resolved = True; break
            if not is_resolved:
                resolved.append(q)
        result["questions_or_unknowns"] = resolved

    return result


# ─────────────────────────────────────────────────────────────────────────────
def run_onboarding(transcript_path: Path, account_id: str | None = None) -> dict:
    """
    Process a single onboarding transcript → v2 memo + spec + changelog.
    Requires v1 outputs to already exist (run pipeline_a first).
    """
    account_id = account_id or infer_account_id(transcript_path.name)
    log.info("▶  Pipeline B | account=%s | file=%s", account_id, transcript_path.name)

    # 1. Load v1 outputs
    v1_dir = OUTPUT_DIR / account_id / "v1"
    if not (v1_dir / "account_memo.json").exists():
        raise FileNotFoundError(
            f"v1 memo not found for {account_id}. Run Pipeline A first.\n"
            f"Expected: {v1_dir / 'account_memo.json'}"
        )
    v1_memo = load_json(v1_dir / "account_memo.json")
    v1_spec = load_json(v1_dir / "agent_spec.json")
    log.info("   Loaded v1 memo from %s", v1_dir)

    # 2. Extract onboarding updates via LLM
    transcript = read_transcript(transcript_path)
    log.info("   Extracting onboarding updates via LLM...")
    onboarding_data = extract_memo(transcript, account_id)

    # 3. Merge v1 + onboarding → v2 memo
    v2_memo = _deep_merge(v1_memo, onboarding_data)
    v2_memo["_pipeline"] = "B"
    v2_memo["_source_file"] = transcript_path.name
    v2_memo["_onboarding_extracted_at"] = utcnow()
    v2_memo["_version"] = "v2"
    v2_memo["_previous_version"] = "v1"

    # 4. Build v2 Agent Spec
    log.info("   Generating v2 Retell agent spec...")
    v2_spec = build_agent_spec(v2_memo, version="v2")

    # 5. Save v2 outputs
    out = account_dir(account_id, "v2")
    save_json(v2_memo, out / "account_memo.json")
    save_json(v2_spec, out / "agent_spec.json")
    log.info("   ✓ Saved v2 outputs → %s", out)

    # 6. Generate changelog
    log.info("   Generating changelog v1 → v2...")
    changelog = generate_changelog(account_id, v1_memo, v2_memo, v1_spec, v2_spec)
    log.info("   ✓ Changelog: %d total changes", changelog["summary"]["total_changes"])

    return {
        "account_id": account_id,
        "status": "ok",
        "output_dir": str(out),
        "changes": changelog["summary"]["total_changes"]
    }


def run_all() -> list[dict]:
    files = sorted(ONBD_DIR.glob("*.txt"))
    if not files:
        log.warning("No .txt files found in %s", ONBD_DIR)
        return []
    results = []
    for f in files:
        try:
            r = run_onboarding(f)
            results.append(r)
        except Exception as exc:
            log.error("FAILED %s: %s", f.name, exc)
            results.append({"account_id": infer_account_id(f.name), "status": "error", "error": str(exc)})
    return results


# ─────────────────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Pipeline B: Onboarding → v2 Agent")
    parser.add_argument("transcript", nargs="?", help="Path to a single onboarding transcript")
    parser.add_argument("--account-id", help="Override inferred account_id")
    parser.add_argument("--all", action="store_true", help="Process all onboarding transcripts")
    args = parser.parse_args()

    if args.all:
        results = run_all()
        for r in results:
            status = "✓" if r["status"] == "ok" else "✗"
            extra = f"  ({r.get('changes')} changes)" if r.get("changes") is not None else f"  ERROR: {r.get('error')}"
            print(f"  {status} {r['account_id']}{extra}")
    elif args.transcript:
        result = run_onboarding(Path(args.transcript), args.account_id)
        print(f"Done → {result['output_dir']}  ({result['changes']} changes)")
    else:
        parser.print_help()
        sys.exit(1)
