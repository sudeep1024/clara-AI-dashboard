"""differ.py – generates structured changelog between v1 and v2"""
import json
from datetime import datetime, timezone
from utils import get_logger, save_json, changelog_dir
log = get_logger("differ")

def _deep_diff(old, new, path=""):
    changes = []
    if isinstance(old, dict) and isinstance(new, dict):
        for key in sorted(set(old.keys()) | set(new.keys())):
            cp = f"{path}.{key}" if path else key
            if key not in old: changes.append({"path":cp,"type":"added","old":None,"new":new[key]})
            elif key not in new: changes.append({"path":cp,"type":"removed","old":old[key],"new":None})
            else: changes.extend(_deep_diff(old[key], new[key], cp))
    elif isinstance(old, list) and isinstance(new, list):
        if json.dumps(old,sort_keys=True) != json.dumps(new,sort_keys=True):
            changes.append({"path":path,"type":"modified","old":old,"new":new})
    else:
        if old != new: changes.append({"path":path,"type":"modified","old":old,"new":new})
    return changes

def generate_changelog(account_id, v1_memo, v2_memo, v1_spec, v2_spec):
    log.info("Generating changelog for %s", account_id)
    memo_changes = _deep_diff(v1_memo, v2_memo, "memo")
    spec_changes = _deep_diff(
        {k:v for k,v in v1_spec.items() if k != "system_prompt"},
        {k:v for k,v in v2_spec.items() if k != "system_prompt"}, "spec")
    prompt_changed = v1_spec.get("system_prompt") != v2_spec.get("system_prompt")

    changelog = {
        "account_id": account_id,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "summary": {
            "memo_fields_changed": len(memo_changes),
            "spec_fields_changed": len(spec_changes),
            "system_prompt_changed": prompt_changed,
            "total_changes": len(memo_changes) + len(spec_changes) + (1 if prompt_changed else 0)
        },
        "memo_changes": memo_changes, "spec_changes": spec_changes,
        "system_prompt_changed": prompt_changed
    }
    cdir = changelog_dir()
    save_json(changelog, cdir / f"{account_id}_changelog.json")

    md_lines = [f"# Changelog: {account_id}", "", f"**Generated:** {changelog['generated_at']}",
                f"**Total changes:** {changelog['summary']['total_changes']}", "", "---", "",
                f"## Memo Changes ({len(memo_changes)})", ""]
    for c in memo_changes:
        md_lines.append(f"### `{c['path']}` — *{c['type']}*")
        if c["type"] == "added": md_lines.append(f"- Added: `{json.dumps(c['new'])}`")
        elif c["type"] == "removed": md_lines.append(f"- Removed: `{json.dumps(c['old'])}`")
        else: md_lines += [f"- Before: `{json.dumps(c['old'])}`", f"- After:  `{json.dumps(c['new'])}`"]
        md_lines.append("")
    if not memo_changes: md_lines.append("_No memo changes._\n")
    md_lines += [f"## Spec Changes ({len(spec_changes)})", ""]
    for c in spec_changes:
        md_lines.append(f"### `{c['path']}` — *{c['type']}*")
        if c["type"] == "added": md_lines.append(f"- Added: `{json.dumps(c['new'])}`")
        elif c["type"] == "removed": md_lines.append(f"- Removed: `{json.dumps(c['old'])}`")
        else: md_lines += [f"- Before: `{json.dumps(c['old'])}`", f"- After:  `{json.dumps(c['new'])}`"]
        md_lines.append("")
    if not spec_changes: md_lines.append("_No spec changes._\n")
    if prompt_changed:
        md_lines += ["## System Prompt", "", "Prompt **regenerated** from updated memo. See `v2/agent_spec.json`.", ""]
    with open(cdir / f"{account_id}_changes.md", "w") as f: f.write("\n".join(md_lines))
    log.info("Saved changelog → %s", cdir / f"{account_id}_changes.md")
    return changelog
