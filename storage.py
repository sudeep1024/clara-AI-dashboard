"""
storage.py — Read and write all pipeline artefacts.

Directory layout (all relative to OUTPUTS_DIR):
  outputs/accounts/<account_id>/
    v1/
      memo.json
      agent_spec.json
    v2/
      memo.json
      agent_spec.json
    changelog/
      changes.md
      changes.json
    task.json          ← task-tracker record
"""

import json
import logging
from pathlib import Path
from typing import Any, Dict, Optional

import config

logger = logging.getLogger(__name__)


def _account_dir(account_id: str) -> Path:
    p = config.OUTPUTS_DIR / account_id
    p.mkdir(parents=True, exist_ok=True)
    return p


def _version_dir(account_id: str, version: str) -> Path:
    p = _account_dir(account_id) / version
    p.mkdir(parents=True, exist_ok=True)
    return p


def _changelog_dir(account_id: str) -> Path:
    p = _account_dir(account_id) / "changelog"
    p.mkdir(parents=True, exist_ok=True)
    return p


# ─── Write ────────────────────────────────────────────────────────────────────

def save_memo(account_id: str, memo: Dict[str, Any], version: str) -> Path:
    path = _version_dir(account_id, version) / "memo.json"
    path.write_text(json.dumps(memo, indent=2), encoding="utf-8")
    logger.info("Saved memo  → %s", path)
    return path


def save_agent_spec(account_id: str, spec: Dict[str, Any], version: str) -> Path:
    path = _version_dir(account_id, version) / "agent_spec.json"
    path.write_text(json.dumps(spec, indent=2), encoding="utf-8")
    logger.info("Saved spec  → %s", path)
    return path


def save_changelog(account_id: str, changes_md: str, changes_json: Dict[str, Any]) -> None:
    d = _changelog_dir(account_id)
    (d / "changes.md").write_text(changes_md, encoding="utf-8")
    (d / "changes.json").write_text(json.dumps(changes_json, indent=2), encoding="utf-8")
    logger.info("Saved changelog → %s", d)


def save_task(account_id: str, task: Dict[str, Any]) -> Path:
    path = _account_dir(account_id) / "task.json"
    path.write_text(json.dumps(task, indent=2), encoding="utf-8")
    logger.info("Saved task  → %s", path)
    return path


# ─── Read ─────────────────────────────────────────────────────────────────────

def load_memo(account_id: str, version: str) -> Optional[Dict[str, Any]]:
    path = _version_dir(account_id, version) / "memo.json"
    if not path.exists():
        logger.warning("Memo not found: %s", path)
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def load_agent_spec(account_id: str, version: str) -> Optional[Dict[str, Any]]:
    path = _version_dir(account_id, version) / "agent_spec.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def list_accounts() -> list:
    if not config.OUTPUTS_DIR.exists():
        return []
    return sorted(p.name for p in config.OUTPUTS_DIR.iterdir() if p.is_dir())
