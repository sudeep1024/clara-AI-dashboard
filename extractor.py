"""
extractor.py – Calls an LLM to extract a structured Account Memo from a transcript.

Supports:
  - Google Gemini (free tier: 1,500 req/day, gemini-1.5-flash)
  - Groq       (free tier, llama3-8b-8192)
  - Ollama     (local, no cost)
"""

import json
import os
import sys
import textwrap
from pathlib import Path

from config import (
    LLM_PROVIDER, GEMINI_API_KEY, GEMINI_MODEL,
    GROQ_API_KEY, GROQ_MODEL,
    OLLAMA_BASE_URL, OLLAMA_MODEL,
    LLM_TEMPERATURE, LLM_MAX_TOKENS
)
from utils import extract_json_block, get_logger

log = get_logger("extractor")

# ─────────────────────────────────────────────────────────────────────────────
EXTRACTION_PROMPT = textwrap.dedent("""
You are an expert operations analyst for a voice AI company.
Your job is to extract structured configuration data from a call transcript.

Rules:
- Extract ONLY what is explicitly stated.
- Do NOT invent, guess, or infer any values that are not stated.
- If a field is missing or unclear, use null and add an entry to questions_or_unknowns.
- Return ONLY valid JSON matching the schema below. No explanation, no markdown fences.

Schema:
{
  "account_id": "string",
  "company_name": "string",
  "business_hours": {
    "days": ["Monday","Tuesday",...],
    "start": "HH:MM (24h)",
    "end": "HH:MM (24h)",
    "timezone": "IANA tz string e.g. America/Denver",
    "notes": "string or null"
  },
  "office_address": "string or null",
  "services_supported": ["list of services"],
  "emergency_definition": ["list of emergency trigger descriptions"],
  "emergency_routing_rules": [
    {
      "order": 1,
      "contact": "description (no personal names if instructed)",
      "phone": "number or null",
      "timeout_seconds": integer or null
    }
  ],
  "non_emergency_routing_rules": {
    "action": "collect_info | transfer | voicemail",
    "collect_fields": ["name","phone","description",...],
    "notify_method": "email | none",
    "notify_target": "string or null",
    "message_to_caller": "string or null"
  },
  "call_transfer_rules": {
    "pre_transfer_message": "string",
    "timeout_seconds": integer or null,
    "max_attempts": integer or null,
    "transfer_fail_message": "string"
  },
  "integration_constraints": ["list of constraint strings"],
  "after_hours_flow_summary": "paragraph summarising after-hours call flow",
  "office_hours_flow_summary": "paragraph summarising business-hours call flow",
  "questions_or_unknowns": ["list of open questions or missing fields"],
  "notes": "any important short notes"
}

Transcript:
{transcript}

Account ID hint (may appear in the transcript or filename): {account_id}

Return only the JSON object.
""").strip()


# ─────────────────────────────────────────────────────────────────────────────
def _call_gemini(prompt: str) -> str:
    import google.generativeai as genai  # pip install google-generativeai
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel(GEMINI_MODEL)
    resp = model.generate_content(
        prompt,
        generation_config={"temperature": LLM_TEMPERATURE, "max_output_tokens": LLM_MAX_TOKENS}
    )
    return resp.text


def _call_groq(prompt: str) -> str:
    from groq import Groq  # pip install groq
    client = Groq(api_key=GROQ_API_KEY)
    resp = client.chat.completions.create(
        model=GROQ_MODEL,
        messages=[{"role": "user", "content": prompt}],
        temperature=LLM_TEMPERATURE,
        max_tokens=LLM_MAX_TOKENS,
    )
    return resp.choices[0].message.content


def _call_ollama(prompt: str) -> str:
    import urllib.request
    payload = json.dumps({
        "model": OLLAMA_MODEL,
        "prompt": prompt,
        "stream": False,
        "options": {"temperature": LLM_TEMPERATURE}
    }).encode()
    req = urllib.request.Request(
        f"{OLLAMA_BASE_URL}/api/generate",
        data=payload,
        headers={"Content-Type": "application/json"},
        method="POST"
    )
    with urllib.request.urlopen(req, timeout=120) as r:
        return json.loads(r.read())["response"]


def _llm_call(prompt: str) -> str:
    provider = LLM_PROVIDER.lower()
    log.info("LLM call via provider=%s", provider)
    if provider == "gemini":
        return _call_gemini(prompt)
    elif provider == "groq":
        return _call_groq(prompt)
    elif provider == "ollama":
        return _call_ollama(prompt)
    else:
        raise ValueError(f"Unknown LLM_PROVIDER: {provider}")


# ─────────────────────────────────────────────────────────────────────────────
def extract_memo(transcript: str, account_id: str) -> dict:
    """
    Extract a structured Account Memo JSON from a transcript string.
    Returns a Python dict matching the schema.
    """
    prompt = EXTRACTION_PROMPT.format(transcript=transcript, account_id=account_id)
    raw = _llm_call(prompt)
    log.debug("Raw LLM output (first 500 chars): %s", raw[:500])
    memo = extract_json_block(raw)

    # Ensure account_id is set
    if not memo.get("account_id"):
        memo["account_id"] = account_id

    return memo
