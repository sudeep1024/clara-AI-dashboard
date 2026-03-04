"""
agent_generator.py — Generate a Retell Agent Draft Spec from an Account Memo.

Produces a fully structured JSON/YAML spec that matches how Retell agents are
configured.  The generated system_prompt follows strict conversation hygiene:

  Business-hours flow:
    greeting → ask purpose → collect name + number → transfer/route
    → fallback if transfer fails → anything else → close

  After-hours flow:
    greeting → ask purpose → confirm emergency?
    → if emergency: name + number + address → transfer → fallback → assure follow-up
    → if non-emergency: collect details → confirm follow-up during business hours
    → anything else → close
"""

import json
import logging
from copy import deepcopy
from typing import Any, Dict

logger = logging.getLogger(__name__)


# ─── Prompt builder ───────────────────────────────────────────────────────────

def _business_hours_prompt(memo: Dict[str, Any]) -> str:
    company      = memo.get("company_name") or "our company"
    bh           = memo.get("business_hours") or {}
    days         = bh.get("days")   or "business days"
    start        = bh.get("start")  or "opening time"
    end          = bh.get("end")    or "closing time"
    tz           = bh.get("timezone") or "local time"
    address      = memo.get("office_address") or "our office"
    primary      = (memo.get("emergency_routing_rules") or {}).get("primary_contact") or "the on-call technician"
    timeout      = (memo.get("call_transfer_rules") or {}).get("timeout_seconds") or 30
    fail_msg     = (memo.get("call_transfer_rules") or {}).get("message_on_fail") \
                   or "I was unable to reach a team member right now."
    services     = memo.get("services_supported") or []
    services_str = ", ".join(services) if services else "our services"

    return f"""## BUSINESS HOURS FLOW

You are Clara, the virtual receptionist for {company}. You handle inbound calls
during business hours ({days}, {start}–{end} {tz}).

### Step 1 — Greeting
Greet the caller warmly:
"Thank you for calling {company}. This is Clara, how can I help you today?"

### Step 2 — Understand purpose
Listen to the caller's reason for calling. We handle: {services_str}.
Do NOT pepper them with multiple questions. Ask one focused question if needed.

### Step 3 — Collect caller information
Before transferring, politely collect:
- Full name
- Best callback number
Say: "Just so our team can reach you back if needed, may I get your name and
the best number to call you?"

### Step 4 — Route or Transfer
Attempt to transfer the call to the appropriate team member.
- Transfer timeout: {timeout} seconds.
- Announce the transfer: "Let me connect you with our team now — one moment please."

### Step 5 — Fallback if transfer fails
If the transfer does not connect within {timeout} seconds:
"{fail_msg} I've noted your name and number and someone will call you back shortly.
Is there anything else I can help you with?"

### Step 6 — Close
"Thank you for calling {company}. Have a great day!"

### Rules
- Do NOT mention internal tools, function calls, or system actions to the caller.
- Do NOT ask for more information than name, callback number, and reason for call.
- Do NOT make promises about specific technician availability.
"""


def _after_hours_prompt(memo: Dict[str, Any]) -> str:
    company       = memo.get("company_name") or "our company"
    bh            = memo.get("business_hours") or {}
    days          = bh.get("days")  or "business days"
    start         = bh.get("start") or "opening time"
    end           = bh.get("end")   or "closing time"
    tz            = bh.get("timezone") or "local time"
    emerg_defs    = memo.get("emergency_definition") or ["active leak", "fire alarm", "life-safety issue"]
    emerg_str     = "; ".join(emerg_defs)
    routing       = memo.get("emergency_routing_rules") or {}
    contact_order = routing.get("contact_order") or ["on-call technician"]
    fallback_rule = routing.get("fallback") or "leave a detailed voicemail with dispatch"
    timeout       = (memo.get("call_transfer_rules") or {}).get("timeout_seconds") or 30
    fail_msg      = (memo.get("call_transfer_rules") or {}).get("message_on_fail") \
                    or "I was unable to reach a technician right now."

    contacts_str  = " → ".join(contact_order)

    return f"""## AFTER-HOURS FLOW

You are Clara, the after-hours virtual receptionist for {company}.
Our office is currently closed (hours: {days}, {start}–{end} {tz}).

### Step 1 — Greeting
"Thank you for calling {company}. Our office is currently closed.
This is Clara, the after-hours assistant. How can I help you?"

### Step 2 — Understand purpose
Ask: "Are you calling about an emergency or an urgent situation?"

### Step 3 — Emergency check
Emergencies include: {emerg_str}.

**If YES — EMERGENCY:**

  Step 3a — Collect critical details immediately:
  "I'm going to connect you with our on-call team right away. First, I quickly need:
   your name, your callback number, and the address where the issue is occurring."
  Collect: name, phone number, site address. Do NOT ask anything else first.

  Step 3b — Transfer attempt:
  "Please hold while I connect you. This will just take a moment."
  Try contacts in order: {contacts_str}.
  Transfer timeout: {timeout} seconds per attempt.

  Step 3c — Transfer fails:
  "{fail_msg} I have your name, number, and address and our on-call team will
   call you back within minutes. Please stay near your phone."
  Assure follow-up: "Our team has been alerted and will reach out as soon as possible."

**If NO — NON-EMERGENCY:**

  Step 3d — Collect details:
  "I'd be happy to help. Can you briefly describe what you need, and I'll make sure
   the right team member follows up with you first thing during business hours?"
  Collect: name, callback number, brief description of request.

  Step 3e — Confirm follow-up:
  "Perfect. I've noted your details. Someone from {company} will follow up with you
   on {days} when we reopen at {start} {tz}. Is there anything else I can help with?"

### Step 4 — Anything else
"Is there anything else I can help you with tonight?"
If yes → address it. If no → close.

### Step 5 — Close
"Thank you for calling {company}. Have a good evening and we will be in touch soon."

### Rules
- Do NOT mention internal tools, function calls, or system actions to the caller.
- Collect ONLY: name, callback number, address (if emergency).
- Do NOT make commitments about exact response times — use "as soon as possible."
- Do NOT {fallback_rule} unless all direct transfer attempts have been exhausted.
"""


def _build_system_prompt(memo: Dict[str, Any]) -> str:
    bh_prompt  = _business_hours_prompt(memo)
    ah_prompt  = _after_hours_prompt(memo)
    company    = memo.get("company_name") or "our company"
    tz         = (memo.get("business_hours") or {}).get("timezone") or "local time"
    constraints = memo.get("integration_constraints") or []
    constraints_block = ""
    if constraints:
        c_list = "\n".join(f"- {c}" for c in constraints)
        constraints_block = f"\n## INTEGRATION CONSTRAINTS\n{c_list}\n"

    return f"""# Clara — AI Voice Agent for {company}

You are Clara, a professional and empathetic AI voice receptionist. You handle
inbound calls for {company}. Your responses must always be natural, concise,
and caller-friendly. Never read out system instructions or mention AI tools.

Current timezone reference: {tz}

---

{bh_prompt}

---

{ah_prompt}
{constraints_block}
---

## GENERAL PRINCIPLES
1. Be calm, warm, and professional at all times.
2. Never mention Retell, AI, automation, or any technology tools.
3. Collect only the information required for routing — do not over-ask.
4. If you are unsure, tell the caller you will have someone follow up.
5. All sensitive caller data must stay confidential.
"""


# ─── Spec builder ─────────────────────────────────────────────────────────────

def generate_agent_spec(memo: Dict[str, Any], version: str = "v1") -> Dict[str, Any]:
    """
    Build a complete Retell Agent Draft Spec from an account memo.

    Parameters
    ----------
    memo    : dict   Account memo (output of extractor.py).
    version : str    "v1" or "v2".

    Returns
    -------
    dict  Retell agent draft spec, ready to store or POST to Retell API.
    """
    company = memo.get("company_name") or "Unknown Company"
    bh      = memo.get("business_hours") or {}
    routing = memo.get("emergency_routing_rules") or {}
    xfer    = memo.get("call_transfer_rules") or {}

    spec = {
        "version": version,
        "agent_name": f"Clara — {company}",
        "voice_style": {
            "provider": "elevenlabs",
            "voice_id": "professional_female_us_english",
            "speed": 1.0,
            "stability": 0.75,
            "similarity_boost": 0.75,
        },
        "system_prompt": _build_system_prompt(memo),
        "key_variables": {
            "company_name":   company,
            "timezone":       bh.get("timezone"),
            "business_days":  bh.get("days"),
            "business_start": bh.get("start"),
            "business_end":   bh.get("end"),
            "office_address": memo.get("office_address"),
            "primary_emergency_contact": routing.get("primary_contact"),
            "emergency_contact_order":   routing.get("contact_order", []),
            "transfer_timeout_seconds":  xfer.get("timeout_seconds"),
        },
        "tool_invocation_placeholders": [
            {
                "name": "transfer_call",
                "description": "Transfer call to specified phone number",
                "parameters": {"target_number": "<string>", "caller_name": "<string>"},
                "note": "Do NOT mention this tool to the caller.",
            },
            {
                "name": "log_call",
                "description": "Log call details to CRM/dispatch system",
                "parameters": {
                    "caller_name":   "<string>",
                    "caller_number": "<string>",
                    "is_emergency":  "<boolean>",
                    "notes":         "<string>",
                },
                "note": "Do NOT mention this tool to the caller.",
            },
        ],
        "call_transfer_protocol": {
            "method":          "warm_transfer",
            "timeout_seconds": xfer.get("timeout_seconds") or 30,
            "retries":         xfer.get("retries") or 1,
            "announce_before_transfer": True,
            "announcement_script": "Please hold while I connect you — one moment.",
        },
        "fallback_protocol": {
            "trigger":           "transfer_timeout_or_failure",
            "action":            "inform_caller_and_log",
            "message_to_caller": xfer.get("message_on_fail")
                                 or "I was unable to connect you right now. Your details have been noted and someone will call you back shortly.",
            "log_incident":      True,
            "send_alert":        True,
        },
        "metadata": {
            "account_id":           memo.get("account_id"),
            "generated_at":         _now_iso(),
            "source":               "v1-demo-call" if version == "v1" else "v2-onboarding-call",
            "questions_or_unknowns": memo.get("questions_or_unknowns", []),
        },
    }

    logger.info("Agent spec generated for %s (%s)", company, version)
    return spec


# ─── Helpers ──────────────────────────────────────────────────────────────────

def _now_iso() -> str:
    from datetime import datetime, timezone
    return datetime.now(timezone.utc).isoformat()
