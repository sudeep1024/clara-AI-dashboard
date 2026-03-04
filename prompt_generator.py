"""prompt_generator.py – builds Retell agent spec from account memo"""
import textwrap
from utils import get_logger
log = get_logger("prompt_generator")

def _safe(v, d="[UNKNOWN]"):
    if v is None or v == "" or v == []: return d
    if isinstance(v, list): return "; ".join(str(x) for x in v)
    return str(v)

def _format_hours(bh):
    if not bh: return "[BUSINESS HOURS UNKNOWN]"
    days = ", ".join(bh["days"]) if isinstance(bh.get("days"), list) else _safe(bh.get("days"))
    return f"{days}, {bh.get('start','?')}–{bh.get('end','?')} {bh.get('timezone','')}"

def _format_routing(rules):
    if not rules: return "  - [NOT CONFIGURED]"
    lines = []
    for r in rules:
        t = f", {r['timeout_seconds']}s timeout" if r.get("timeout_seconds") else ""
        lines.append(f"  {r.get('order','?')}. {r.get('contact','[contact]')} ({r.get('phone') or 'number TBD'}{t})")
    return "\n".join(lines)

def build_system_prompt(memo, version="v1"):
    company = _safe(memo.get("company_name"), "[Company Name]")
    hours_str = _format_hours(memo.get("business_hours") or {})
    services = _safe(memo.get("services_supported", []), "[services TBD]")
    emerg = "; ".join(memo.get("emergency_definition") or ["[emergency triggers TBD]"])
    routing = _format_routing(memo.get("emergency_routing_rules") or [])
    tr = memo.get("call_transfer_rules") or {}
    pre_tr = _safe(tr.get("pre_transfer_message"), "Please hold while I connect you with our on-call team.")
    fail_tr = _safe(tr.get("transfer_fail_message"), "I was unable to reach our team. Your information has been logged and someone will call you back shortly.")
    ne = memo.get("non_emergency_routing_rules") or {}
    ne_msg = _safe(ne.get("message_to_caller"), "We will follow up during the next business day.")
    address = _safe(memo.get("office_address"), "[address TBD]")
    constraints = "\n".join(f"  - {c}" for c in (memo.get("integration_constraints") or [])) or "  - None configured"

    return textwrap.dedent(f"""
    # Clara AI Voice Agent – System Prompt | {company} | {version}

    ## Identity
    You are Clara, the AI answering service for {company}.
    Handle calls professionally. NEVER mention function calls, tools, or backend systems.
    NEVER reveal specific on-call staff names unless explicitly instructed.

    ## Company
    - Name: {company}
    - Address: {address}
    - Business Hours: {hours_str}
    - Services: {services}

    ## Emergency Definition
    The following are EMERGENCIES requiring immediate escalation:
    {emerg}
    All other calls (scheduling, quotes, general questions) are NON-EMERGENCY.

    ---
    ## BUSINESS HOURS CALL FLOW

    1. GREETING
       "Thank you for calling {company}. This is Clara. How can I help you today?"
    2. UNDERSTAND PURPOSE — listen, ask one follow-up if needed.
    3. COLLECT INFO — "May I get your name and best callback number?"
       Confirm the number back to the caller.
    4. ROUTE:
       - Emergency → Emergency Transfer Protocol below.
       - Non-emergency → Log and inform: "{ne_msg}"
    5. CLOSE — "Is there anything else I can help you with?"
       If no: "Thank you for calling {company}. Have a great day!"

    ---
    ## AFTER-HOURS CALL FLOW

    1. GREETING
       "Thank you for calling {company}. Our office is currently closed.
        Business hours are {hours_str}. This is the after-hours emergency line. How can I help you?"
    2. PURPOSE — "Can you briefly describe what's happening?"
    3. TRIAGE:
       Emergency triggers: {emerg}

       IF EMERGENCY:
         a. "I understand – let me connect you with our emergency team right away."
         b. Collect: full name, callback number, property address (partial address accepted).
         c. → Emergency Transfer Protocol.

       IF NON-EMERGENCY:
         a. "Our team handles that during business hours."
         b. Collect: name, callback number, description.
         c. "{ne_msg}" — confirm callback number.

    4. CLOSE — "Is there anything else?" → "Thank you. Stay safe. Goodbye."

    ---
    ## EMERGENCY TRANSFER PROTOCOL

    Say: "{pre_tr}"

    Attempt transfer in order:
{routing}

    TRANSFER FAIL → Say exactly:
    "{fail_tr}"
    Confirm callback number one final time.

    ---
    ## INTEGRATION CONSTRAINTS (MUST FOLLOW)
{constraints}

    ---
    ## GENERAL RULES
    - Be concise. One question at a time.
    - Never promise specific arrival times unless instructed.
    - Never discuss pricing.
    - When in doubt about emergency status, treat as emergency.
    """).strip()

def build_agent_spec(memo, version="v1"):
    log.info("Building agent spec %s %s", memo.get("account_id"), version)
    company = memo.get("company_name", "Unknown")
    bh = memo.get("business_hours") or {}
    tr = memo.get("call_transfer_rules") or {}
    return {
        "agent_name": f"{company} – Clara Agent",
        "version": version,
        "voice_style": {"provider": "eleven_labs", "voice": "female_professional_calm", "language": "en-US", "notes": "Adjust in Retell dashboard"},
        "system_prompt": build_system_prompt(memo, version),
        "key_variables": {
            "company_name": company,
            "timezone": bh.get("timezone", ""),
            "business_hours_start": bh.get("start", ""),
            "business_hours_end": bh.get("end", ""),
            "business_hours_days": bh.get("days", []),
            "office_address": memo.get("office_address", ""),
            "emergency_routing": memo.get("emergency_routing_rules", []),
            "services": memo.get("services_supported", [])
        },
        "tool_invocation_placeholders": [
            {"tool": "call_transfer", "trigger": "emergency confirmed and info collected", "description": "Transfer to emergency contact. Never mention to caller."},
            {"tool": "log_call", "trigger": "any call completion", "description": "Log call details silently."},
            {"tool": "send_notification", "trigger": "non-emergency after hours", "description": "Send info to dispatch channel silently."}
        ],
        "call_transfer_protocol": {
            "pre_transfer_message": tr.get("pre_transfer_message", "Please hold while I connect you."),
            "timeout_seconds": tr.get("timeout_seconds", 30),
            "max_attempts": tr.get("max_attempts", 2),
            "routing_order": memo.get("emergency_routing_rules", [])
        },
        "fallback_protocol": {
            "trigger": "all transfer attempts exhausted",
            "message": tr.get("transfer_fail_message", "I was unable to reach our team. Your information has been logged."),
            "confirm_callback_number": True
        },
        "integration_constraints": memo.get("integration_constraints", []),
        "questions_or_unknowns": memo.get("questions_or_unknowns", [])
    }
