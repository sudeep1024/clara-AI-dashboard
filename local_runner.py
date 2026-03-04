"""
local_runner.py — Zero-cost, zero-API-key pipeline runner.

Uses a rule-based extractor to parse transcripts and generate all outputs.
This is the demonstration mode that works without any external services.

Usage:
  python local_runner.py           # process all 10 transcripts
  python local_runner.py --account account_001  # single account
"""

import argparse
import json
import logging
import re
import sys
from pathlib import Path

# Add scripts dir to path
sys.path.insert(0, str(Path(__file__).parent))

import config
import agent_generator
import versioning
import storage
import task_tracker

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s  %(levelname)-8s  %(message)s",
)
logger = logging.getLogger("local_runner")


# ─── Rule-based extractor ─────────────────────────────────────────────────────

COMPANY_PATTERNS = [
    r"(?:for|at|—)\s+([A-Z][A-Za-z\s&]+(?:Services|Solutions|Systems|HVAC|Safety|Protection|Security))",
    r"TRANSCRIPT — ([A-Z][A-Za-z\s&]+)",
]

def _extract_company_name(text: str) -> str | None:
    for pattern in COMPANY_PATTERNS:
        m = re.search(pattern, text)
        if m:
            return m.group(1).strip()
    return None


def _extract_business_hours(text: str) -> dict:
    bh = {"days": None, "start": None, "end": None, "timezone": None}

    days_pattern = r"(Monday\s+through\s+(?:Friday|Saturday|Sunday))"
    m = re.search(days_pattern, text, re.IGNORECASE)
    if m:
        bh["days"] = m.group(1).replace("  ", " ").strip()

    time_pattern = r"(\d{1,2}(?:am|pm))\s+(?:to|through)\s+(\d{1,2}(?::\d{2})?(?:am|pm))"
    m = re.search(time_pattern, text, re.IGNORECASE)
    if m:
        bh["start"] = m.group(1).upper()
        bh["end"]   = m.group(2).upper()

    tz_map = {
        "Central": "America/Chicago",
        "Eastern": "America/New_York",
        "Mountain": "America/Phoenix",
        "Pacific": "America/Los_Angeles",
    }
    for label, tz in tz_map.items():
        if re.search(label + r"\s+time", text, re.IGNORECASE):
            bh["timezone"] = tz
            break

    return bh


def _extract_address(text: str) -> str | None:
    addr_pattern = r"\d{3,5}\s+[A-Z][A-Za-z\s]+(?:Road|Avenue|Boulevard|Street|Ave|Blvd|Rd|St|Way|Drive|Dr|Lane|Ln)[,\s]+[A-Za-z\s]+,?\s+[A-Z]{2}\s+\d{5}"
    m = re.search(addr_pattern, text)
    if m:
        return m.group(0).strip()
    return None


def _extract_services(text: str) -> list:
    service_keywords = [
        "sprinkler installation", "sprinkler repair", "sprinkler service",
        "fire alarm installation", "fire alarm monitoring", "fire suppression",
        "fire extinguisher", "HVAC repair", "HVAC maintenance", "chiller service",
        "boiler service", "rooftop unit", "alarm monitoring", "burglar alarm",
        "access control", "CCTV", "backflow preventer", "annual inspection",
        "annual certification", "kitchen hood suppression", "emergency lighting",
        "exit sign inspection", "preventive maintenance", "new installs",
    ]
    found = []
    for svc in service_keywords:
        if re.search(re.escape(svc), text, re.IGNORECASE):
            found.append(svc.title())
    return found


def _extract_emergencies(text: str) -> list:
    emerg_patterns = [
        r"active\s+(?:sprinkler\s+)?(?:water\s+)?discharge",
        r"fire\s+alarm\s+(?:signal|activation|triggered)",
        r"smoke\s+smell",
        r"flooding\s+(?:from|inside)",
        r"fire\s+panel\s+fault",
        r"carbon\s+monoxide",
        r"server\s+room\s+overheating",
        r"walk-in\s+cooler\s+(?:or\s+freezer\s+)?failure",
        r"complete\s+cooling\s+failure",
        r"boiler\s+failure",
        r"gas\s+smell",
        r"break-?in\s+in\s+progress",
        r"panel\s+is\s+offline",
        r"extinguisher\s+(?:failed|failure)",
        r"post-discharge",
    ]
    found = []
    for p in emerg_patterns:
        m = re.search(p, text, re.IGNORECASE)
        if m:
            found.append(m.group(0).strip().capitalize())
    return list(dict.fromkeys(found))  # deduplicate preserving order


def _extract_phone(text: str, label_hint: str = "") -> str | None:
    """Find first phone number near an optional label."""
    pattern = r"\b(\d{3}-\d{3}-\d{4})\b"
    if label_hint:
        search_area = text[max(0, text.lower().find(label_hint.lower()) - 20):][:200]
        m = re.search(pattern, search_area)
        if m:
            return m.group(1)
    m = re.search(pattern, text)
    return m.group(1) if m else None


def _extract_routing(text: str) -> dict:
    routing = {"primary_contact": None, "contact_order": [], "fallback": None}

    # Find primary and contacts by "first" / "dispatch" / "on-call" keywords
    first_match = re.search(
        r"(?:first|First)[,\s]+(?:try\s+)?([A-Za-z\s']+?)(?:\s*—\s*|\s*,\s*|\s+that\s+)",
        text
    )
    if first_match:
        routing["primary_contact"] = first_match.group(1).strip()

    phones = re.findall(r"\b\d{3}-\d{3}-\d{4}\b", text)
    routing["contact_order"] = phones[:3] if phones else []

    fallback_match = re.search(
        r"(?:all\s+(?:three|fail)|all\s+else\s+fails?|if\s+all\s+fail)[,\s:]+([^.]+\.).*?",
        text, re.IGNORECASE
    )
    if fallback_match:
        routing["fallback"] = fallback_match.group(1).strip()

    return routing


def _extract_transfer_rules(text: str) -> dict:
    rules = {"timeout_seconds": None, "retries": None, "message_on_fail": None}

    timeout_m = re.search(r"(\d{1,3})\s*second", text, re.IGNORECASE)
    if timeout_m:
        rules["timeout_seconds"] = int(timeout_m.group(1))

    msg_m = re.search(
        r'"(I was unable to[^"]+)"',
        text
    )
    if msg_m:
        rules["message_on_fail"] = msg_m.group(1)

    rules["retries"] = 1

    return rules


def _build_flow_summaries(memo: dict) -> tuple:
    """Generate plain-English summaries of the two call flows."""
    company = memo.get("company_name") or "the company"
    bh      = memo.get("business_hours") or {}
    days    = bh.get("days") or "business days"
    start   = bh.get("start") or "opening time"
    end     = bh.get("end") or "closing time"
    tz      = bh.get("timezone") or "local time"
    timeout = (memo.get("call_transfer_rules") or {}).get("timeout_seconds") or 30

    office_summary = (
        f"During business hours ({days}, {start}–{end} {tz}), Clara greets the caller, "
        f"asks for their reason for calling, collects name and callback number, then attempts "
        f"to transfer within {timeout} seconds. If transfer fails, the caller is assured a "
        f"callback and the interaction is logged."
    )
    after_summary = (
        f"After hours, Clara identifies whether the call is an emergency. "
        f"For emergencies, she collects name, number, and address immediately, then attempts "
        f"transfer in order per the escalation chain. If all transfers fail, she assures the caller "
        f"that the on-call team has been alerted and will respond promptly. "
        f"For non-emergencies, she collects name and number and confirms a follow-up during "
        f"business hours ({days} starting {start} {tz})."
    )
    return office_summary, after_summary


def _extract_constraints(text: str) -> list:
    constraint_patterns = [
        r"[Nn]ever\s+create\s+[a-z\s]+(?:job|work\s+order)[^.]+\.",
        r"[Nn]ever\s+quote\s+prices[^.]+\.",
        r"[Nn]ever\s+promise\s+[^.]+\.",
        r"[Nn]ever\s+give\s+out\s+[^.]+\.",
        r"[Nn]ever\s+confirm\s+[^.]+\.",
        r"[Nn]ever\s+create\s+anything[^.]+\.",
        r"[Dd]on't\s+create\s+[^.]+\.",
        r"[Dd]on't\s+promise\s+[^.]+\.",
        r"[Dd]on't\s+tell\s+customers[^.]+\.",
    ]
    found = []
    for p in constraint_patterns:
        for m in re.finditer(p, text, re.IGNORECASE):
            sentence = m.group(0).strip().rstrip(".")
            if sentence and sentence not in found:
                found.append(sentence)
    return found[:6]


def _extract_unknowns(text: str, memo: dict) -> list:
    unknowns = []
    if not memo.get("business_hours", {}).get("timezone"):
        unknowns.append("Timezone not confirmed")
    if not memo.get("emergency_routing_rules", {}).get("contact_order"):
        unknowns.append("Emergency contact phone numbers not provided")
    if not memo.get("call_transfer_rules", {}).get("timeout_seconds"):
        unknowns.append("Transfer timeout not specified")
    if not memo.get("office_address"):
        unknowns.append("Office address not mentioned")
    return unknowns


def rule_based_extract(transcript: str, account_id: str) -> dict:
    """Pure rule-based extraction — no LLM, no API calls, zero cost."""
    memo = {
        "account_id":               account_id,
        "company_name":             _extract_company_name(transcript),
        "business_hours":           _extract_business_hours(transcript),
        "office_address":           _extract_address(transcript),
        "services_supported":       _extract_services(transcript),
        "emergency_definition":     _extract_emergencies(transcript),
        "emergency_routing_rules":  _extract_routing(transcript),
        "non_emergency_routing_rules": "Collect name, callback number, and brief description. Confirm follow-up next business day.",
        "call_transfer_rules":      _extract_transfer_rules(transcript),
        "integration_constraints":  _extract_constraints(transcript),
        "after_hours_flow_summary": None,
        "office_hours_flow_summary": None,
        "questions_or_unknowns":    [],
        "notes":                    None,
    }
    memo["questions_or_unknowns"] = _extract_unknowns(transcript, memo)
    office_sum, after_sum = _build_flow_summaries(memo)
    memo["office_hours_flow_summary"] = office_sum
    memo["after_hours_flow_summary"]  = after_sum
    return memo


# ─── Pipeline logic ───────────────────────────────────────────────────────────

def process_demo(account_id: str, transcript_path: Path) -> dict:
    logger.info("═══ [Pipeline A] %s — %s", account_id, transcript_path.name)
    transcript = transcript_path.read_text(encoding="utf-8")
    memo       = rule_based_extract(transcript, account_id)
    storage.save_memo(account_id, memo, "v1")
    spec = agent_generator.generate_agent_spec(memo, "v1")
    storage.save_agent_spec(account_id, spec, "v1")
    company = memo.get("company_name") or account_id
    task_tracker.create_task(account_id, company, "v1", memo)
    logger.info("  ✓ v1 generated for %s", company)
    return {"account_id": account_id, "company": company, "status": "ok", "version": "v1"}


def process_onboarding(account_id: str, transcript_path: Path) -> dict:
    logger.info("═══ [Pipeline B] %s — %s", account_id, transcript_path.name)
    v1_memo = storage.load_memo(account_id, "v1")
    if not v1_memo:
        raise FileNotFoundError(f"v1 memo missing for {account_id}. Run Pipeline A first.")
    transcript = transcript_path.read_text(encoding="utf-8")
    delta      = rule_based_extract(transcript, account_id)
    delta.pop("account_id", None)
    v2_memo    = versioning.apply_delta(v1_memo, delta)
    diff       = versioning.compute_diff(v1_memo, v2_memo)
    storage.save_memo(account_id, v2_memo, "v2")
    spec_v2    = agent_generator.generate_agent_spec(v2_memo, "v2")
    storage.save_agent_spec(account_id, spec_v2, "v2")
    company    = v2_memo.get("company_name") or account_id
    changes_md, changes_json = versioning.generate_changelog(account_id, company, v1_memo, v2_memo, diff)
    storage.save_changelog(account_id, changes_md, changes_json)
    task_tracker.update_task(account_id, "v2", len(diff))
    logger.info("  ✓ v2 generated for %s (%d changes)", company, len(diff))
    return {"account_id": account_id, "company": company, "status": "ok", "version": "v2", "changes": len(diff)}


def run_all() -> dict:
    results_a, results_b = [], []

    demo_files = sorted(config.DEMO_DIR.glob("demo_*_transcript.txt"))
    for f in demo_files:
        num        = f.stem.split("_")[1]
        account_id = f"account_{num}"
        try:
            results_a.append(process_demo(account_id, f))
        except Exception as e:
            logger.error("Pipeline A failed %s: %s", account_id, e)
            results_a.append({"account_id": account_id, "status": "error", "error": str(e)})

    ob_files = sorted(config.ONBOARD_DIR.glob("onboarding_*_transcript.txt"))
    for f in ob_files:
        num        = f.stem.split("_")[1]
        account_id = f"account_{num}"
        try:
            results_b.append(process_onboarding(account_id, f))
        except Exception as e:
            logger.error("Pipeline B failed %s: %s", account_id, e)
            results_b.append({"account_id": account_id, "status": "error", "error": str(e)})

    # Summary
    print("\n" + "═"*65)
    print("  BATCH RUN COMPLETE")
    print("═"*65)
    for r in results_a + results_b:
        icon = "✓" if r["status"] == "ok" else "✗"
        ver  = r.get("version", "?")
        chg  = f" [{r['changes']} changes]" if "changes" in r else ""
        print(f"  {icon}  {r['account_id']:<20}  {r.get('company',''):<32}  {ver}{chg}")
    print("═"*65)

    return {"pipeline_a": results_a, "pipeline_b": results_b}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--account", help="Single account_id to process (both pipelines)")
    args = parser.parse_args()

    if args.account:
        aid = args.account
        num = aid.split("_")[-1]
        df  = config.DEMO_DIR / f"demo_{num}_transcript.txt"
        of  = config.ONBOARD_DIR / f"onboarding_{num}_transcript.txt"
        if df.exists():
            process_demo(aid, df)
        if of.exists():
            process_onboarding(aid, of)
    else:
        run_all()
