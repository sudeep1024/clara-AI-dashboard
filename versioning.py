"""
versioning.py — Version management, memo patching, and changelog generation.

Responsibilities:
  • Merge an onboarding delta into an existing v1 memo to produce v2.
  • Detect which fields changed, were added, or were removed.
  • Produce both a human-readable changes.md and a machine-readable changes.json.
  • Never silently overwrite fields — every change is logged with reason.
"""

import json
import logging
from copy import deepcopy
from datetime import datetime, timezone
from typing import Any, Dict, List, Tuple

logger = logging.getLogger(__name__)


# ─── Merge logic ─────────────────────────────────────────────────────────────

def _flatten(d: Any, prefix: str = "") -> Dict[str, Any]:
    """Flatten a nested dict to dot-notation keys for diffing."""
    items: Dict[str, Any] = {}
    if isinstance(d, dict):
        for k, v in d.items():
            full = f"{prefix}.{k}" if prefix else k
            items.update(_flatten(v, full))
    elif isinstance(d, list):
        items[prefix] = json.dumps(d, sort_keys=True)
    else:
        items[prefix] = d
    return items


def compute_diff(v1: Dict[str, Any], v2: Dict[str, Any]) -> List[Dict[str, Any]]:
    """
    Compare two memo dicts and return a list of change records.

    Each record: {"field": str, "old": Any, "new": Any, "action": str}
    action is one of: "updated" | "added" | "removed" | "cleared"
    """
    flat1 = _flatten(v1)
    flat2 = _flatten(v2)
    all_keys = set(flat1) | set(flat2)

    changes: List[Dict[str, Any]] = []
    for key in sorted(all_keys):
        old = flat1.get(key)
        new = flat2.get(key)
        if old == new:
            continue

        if old is None and new is not None:
            action = "added"
        elif old is not None and new is None:
            action = "removed"
        elif new in (None, "null", "[]", "{}"):
            action = "cleared"
        else:
            action = "updated"

        changes.append({"field": key, "old": old, "new": new, "action": action})

    return changes


def apply_delta(v1_memo: Dict[str, Any], delta: Dict[str, Any]) -> Dict[str, Any]:
    """
    Deep-merge *delta* onto a copy of *v1_memo*, returning the v2 memo.

    Rules:
      • Scalar fields: delta value wins.
      • List fields: delta value replaces entirely (not appended).
      • Dict fields: recursive merge.
      • account_id is ALWAYS preserved from v1.
    """
    v2 = deepcopy(v1_memo)
    _deep_merge(v2, delta)
    # Always keep original account_id
    v2["account_id"] = v1_memo.get("account_id")
    return v2


def _deep_merge(base: Dict[str, Any], override: Dict[str, Any]) -> None:
    """In-place recursive merge of override into base."""
    for key, val in override.items():
        if key == "account_id":
            continue  # protected field
        if isinstance(val, dict) and isinstance(base.get(key), dict):
            _deep_merge(base[key], val)
        elif val is not None:
            base[key] = val


# ─── Changelog generation ────────────────────────────────────────────────────

def generate_changelog(
    account_id: str,
    company_name: str,
    v1_memo: Dict[str, Any],
    v2_memo: Dict[str, Any],
    diff: List[Dict[str, Any]],
) -> Tuple[str, Dict[str, Any]]:
    """
    Produce (changes_md, changes_json) for a v1 → v2 transition.

    Returns
    -------
    changes_md   : str   Human-readable Markdown changelog.
    changes_json : dict  Machine-readable changelog with full diff.
    """
    now = datetime.now(timezone.utc).isoformat()

    # ── Markdown ──
    lines = [
        f"# Changelog — {company_name} ({account_id})",
        f"",
        f"**Generated:** {now}  ",
        f"**Transition:** v1 (demo-derived) → v2 (onboarding-confirmed)  ",
        f"**Total changes:** {len(diff)}",
        "",
        "---",
        "",
        "## Changes",
        "",
    ]

    if not diff:
        lines.append("_No fields were modified during onboarding._")
    else:
        for ch in diff:
            emoji = {"updated": "✏️", "added": "➕", "removed": "➖", "cleared": "🗑️"}.get(ch["action"], "•")
            lines.append(f"### {emoji} `{ch['field']}`")
            lines.append(f"- **Action:** {ch['action']}")
            if ch["old"] is not None:
                lines.append(f"- **Before (v1):** `{ch['old']}`")
            if ch["new"] is not None:
                lines.append(f"- **After (v2):**  `{ch['new']}`")
            lines.append("")

    lines += [
        "---",
        "",
        "## Fields Still Unknown",
        "",
    ]
    unknowns = v2_memo.get("questions_or_unknowns") or []
    if unknowns:
        for u in unknowns:
            lines.append(f"- {u}")
    else:
        lines.append("_All fields resolved._")

    changes_md = "\n".join(lines)

    # ── JSON ──
    changes_json = {
        "account_id":    account_id,
        "company_name":  company_name,
        "generated_at":  now,
        "transition":    "v1 → v2",
        "total_changes": len(diff),
        "diff":          diff,
        "unknowns_remaining": unknowns,
    }

    return changes_md, changes_json
