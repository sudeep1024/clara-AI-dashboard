"""
task_tracker.py — Create and update task-tracker items per account.

Supports:
  • "local"  — writes a task.json + appends to tasks_log.md (always available)
  • "github" — creates a GitHub Issue via REST API (requires GITHUB_TOKEN + GITHUB_REPO)

The local backend is always the fallback.
"""

import json
import logging
import urllib.error
import urllib.request
from datetime import datetime, timezone
from typing import Any, Dict, Optional

import config
import storage

logger = logging.getLogger(__name__)


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


# ─── Local backend ────────────────────────────────────────────────────────────

def _local_create(account_id: str, title: str, body: str) -> Dict[str, Any]:
    task = {
        "account_id": account_id,
        "title":      title,
        "body":       body,
        "status":     "open",
        "created_at": _now(),
        "backend":    "local",
    }
    storage.save_task(account_id, task)

    # Also append to a global tasks log
    log_path = config.BASE_DIR / "tasks_log.md"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n## [{_now()}] {title}\n")
        f.write(f"**Account:** {account_id}\n\n")
        f.write(f"{body}\n\n---\n")
    logger.info("Local task created for %s", account_id)
    return task


def _local_update(account_id: str, update_body: str) -> None:
    task = storage.load_memo.__module__  # just to use storage import
    task_path = config.OUTPUTS_DIR / account_id / "task.json"
    if task_path.exists():
        existing = json.loads(task_path.read_text())
        existing["last_updated"] = _now()
        existing["updates"]      = existing.get("updates", []) + [{"at": _now(), "body": update_body}]
        task_path.write_text(json.dumps(existing, indent=2))
    log_path = config.BASE_DIR / "tasks_log.md"
    with log_path.open("a", encoding="utf-8") as f:
        f.write(f"\n### Update [{_now()}] — {account_id}\n{update_body}\n\n---\n")


# ─── GitHub backend ───────────────────────────────────────────────────────────

def _github_create(account_id: str, title: str, body: str) -> Optional[Dict[str, Any]]:
    if not config.GITHUB_TOKEN or not config.GITHUB_REPO:
        logger.warning("GitHub token/repo not set — falling back to local tracker.")
        return None

    url     = f"https://api.github.com/repos/{config.GITHUB_REPO}/issues"
    payload = json.dumps({"title": title, "body": body, "labels": ["clara-onboarding"]}).encode()
    headers = {
        "Authorization": f"token {config.GITHUB_TOKEN}",
        "Accept":        "application/vnd.github.v3+json",
        "Content-Type":  "application/json",
    }
    req = urllib.request.Request(url, data=payload, headers=headers, method="POST")
    try:
        with urllib.request.urlopen(req, timeout=15) as resp:
            issue = json.loads(resp.read())
        logger.info("GitHub issue #%s created for %s", issue.get("number"), account_id)
        return issue
    except urllib.error.HTTPError as exc:
        logger.error("GitHub API error: %s %s", exc.code, exc.read().decode())
        return None


# ─── Public API ───────────────────────────────────────────────────────────────

def create_task(account_id: str, company_name: str, version: str, memo: Dict[str, Any]) -> Dict[str, Any]:
    """Create a task tracker item for a newly processed account."""
    unknowns  = memo.get("questions_or_unknowns") or []
    services  = ", ".join(memo.get("services_supported") or []) or "Unknown"
    bh        = memo.get("business_hours") or {}
    hours_str = f"{bh.get('days','?')} {bh.get('start','?')}–{bh.get('end','?')} {bh.get('timezone','')}"

    title = f"[Clara] {company_name} — {version.upper()} agent generated ({account_id})"
    body  = f"""**Account ID:** {account_id}
**Company:** {company_name}
**Version:** {version}
**Business Hours:** {hours_str}
**Services:** {services}

**Open Questions / Unknowns:**
{"".join(f"- {u}\\n" for u in unknowns) if unknowns else "None — all fields resolved."}

**Next Steps:**
- [ ] Review generated agent spec
- [ ] Confirm transfer numbers
- [ ] Import spec into Retell UI
- [ ] Schedule test call
"""

    result = None
    if config.TASK_TRACKER == "github":
        result = _github_create(account_id, title, body)

    if result is None:
        result = _local_create(account_id, title, body)

    return result


def update_task(account_id: str, version: str, changes_count: int) -> None:
    """Append an update to an existing task when onboarding completes."""
    msg = f"Onboarding complete — {version} generated with {changes_count} field change(s)."
    _local_update(account_id, msg)
