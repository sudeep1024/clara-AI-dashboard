"""
config.py — Central configuration for the Clara Pipeline.
Reads from environment variables; see .env.example for all options.
"""

import os
from pathlib import Path

# ── Paths ─────────────────────────────────────────────────────────────────────
BASE_DIR      = Path(__file__).parent.parent
DATA_DIR      = BASE_DIR / "data"
DEMO_DIR      = DATA_DIR / "demo"
ONBOARD_DIR   = DATA_DIR / "onboarding"
OUTPUTS_DIR   = BASE_DIR / "outputs" / "accounts"
CHANGELOG_DIR = BASE_DIR / "changelog"

# Create required directories on import
for _d in [OUTPUTS_DIR, CHANGELOG_DIR]:
    _d.mkdir(parents=True, exist_ok=True)

# ── LLM Provider ──────────────────────────────────────────────────────────────
# Options: "groq" (free tier, recommended) | "ollama" (local, fully offline)
LLM_PROVIDER  = os.getenv("LLM_PROVIDER", "groq")

# Groq — free at https://console.groq.com (no credit card required)
GROQ_API_KEY  = os.getenv("GROQ_API_KEY", "")
GROQ_MODEL    = os.getenv("GROQ_MODEL", "llama-3.1-8b-instant")
GROQ_BASE_URL = "https://api.groq.com/openai/v1"

# Ollama local (fallback) — run `ollama pull llama3` first
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL    = os.getenv("OLLAMA_MODEL", "llama3")

# ── Task Tracker ──────────────────────────────────────────────────────────────
TASK_TRACKER = os.getenv("TASK_TRACKER", "local")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN", "")
GITHUB_REPO  = os.getenv("GITHUB_REPO", "")

# ── Retell ────────────────────────────────────────────────────────────────────
RETELL_API_KEY  = os.getenv("RETELL_API_KEY", "")
RETELL_BASE_URL = "https://api.retellai.com"

# ── Pipeline Settings ─────────────────────────────────────────────────────────
LOG_LEVEL = os.getenv("LOG_LEVEL", "INFO")
DRY_RUN   = os.getenv("DRY_RUN", "false").lower() == "true"
