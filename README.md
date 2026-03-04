# Clara AI Pipeline

> **Automated Demo → Onboarding → Retell Agent Configuration Pipeline**  
> Converts service trade business calls into production-ready AI voice agent configs.

---

## Architecture & Data Flow

```
Demo Transcript (.txt)
        │
        ▼
  [pipeline_a.py]
        │
        ├─ LLM Extraction (Gemini / Groq / Ollama)
        │         └─ account_memo.json  (v1)
        │
        └─ Prompt Generator
                  └─ agent_spec.json   (v1)

Onboarding Transcript (.txt)
        │
        ▼
  [pipeline_b.py]
        │
        ├─ Load v1 memo
        ├─ LLM Extraction (onboarding updates)
        ├─ Deep-merge v1 + updates
        │         └─ account_memo.json  (v2)
        │
        ├─ Prompt Generator
        │         └─ agent_spec.json   (v2)
        │
        └─ Differ
                  ├─ {account_id}_changelog.json
                  └─ {account_id}_changes.md
```

**Orchestration**: n8n (self-hosted via Docker) exposes two webhook endpoints — one for demo calls (Pipeline A) and one for onboarding calls (Pipeline B) — and optionally logs run status to Google Sheets.

---

## Outputs Per Account

```
outputs/accounts/{account_id}/
  v1/
    account_memo.json     ← structured data extracted from demo call
    agent_spec.json       ← Retell agent draft (system prompt, voice, transfer rules)
  v2/
    account_memo.json     ← updated memo after onboarding
    agent_spec.json       ← updated Retell agent spec
changelog/
  {account_id}_changelog.json   ← structured field diff (v1→v2)
  {account_id}_changes.md       ← human-readable changelog
```

---

## Quick Start

### 1. Clone and configure

```bash
git clone <your-repo-url>
cd clara-pipeline
cp .env.example .env
# Edit .env — add your GEMINI_API_KEY (free from aistudio.google.com)
```

### 2. Install Python dependencies

```bash
pip install -r requirements.txt
```

### 3. Run on the sample dataset (no API key needed)

The repo includes 5 demo + 5 onboarding transcripts in `data/transcripts/`.
To generate all outputs using the pre-extracted data (no LLM call):

```bash
cd scripts
python generate_sample_outputs.py
```

### 4. Run with live LLM extraction (requires API key in .env)

```bash
cd scripts

# Single file
python pipeline_a.py ../data/transcripts/demo/ACC-001_demo.txt

# All demo calls
python pipeline_a.py --all

# Single onboarding (requires v1 to exist first)
python pipeline_b.py ../data/transcripts/onboarding/ACC-001_onboarding.txt

# All onboarding calls
python pipeline_b.py --all

# Full batch (A then B)
python batch_run.py
```

### 5. Run with n8n orchestration

```bash
docker-compose up -d
# Open http://localhost:5678 (admin / claraadmin)
# Import workflows/clara_pipeline_n8n.json via Settings → Import Workflow
```

---

## LLM Provider Options (All Zero-Cost)

| Provider | Setup | Limits | How to enable |
|---|---|---|---|
| **Google Gemini** *(default)* | Get free API key at aistudio.google.com | 1,500 req/day, 1M tokens/day | Set `LLM_PROVIDER=gemini` + `GEMINI_API_KEY` |
| **Groq** | Free account at console.groq.com | ~14,400 req/day | Set `LLM_PROVIDER=groq` + `GROQ_API_KEY` |
| **Ollama** *(fully local)* | Install Ollama + pull llama3 | Unlimited | Set `LLM_PROVIDER=ollama` |

No API key is needed to run `generate_sample_outputs.py` — it uses pre-extracted data.

---

## Plugging In Your Dataset

1. Place demo transcripts in `data/transcripts/demo/` named `{ACCOUNT_ID}_demo.txt`
2. Place onboarding transcripts in `data/transcripts/onboarding/` named `{ACCOUNT_ID}_onboarding.txt`
3. Account IDs must match between the two (e.g., `ACC-006_demo.txt` + `ACC-006_onboarding.txt`)
4. Run `python batch_run.py` from the `scripts/` directory

The pipeline infers `account_id` from the filename prefix. You can override with `--account-id`.

---

## Retell Setup Instructions

### If Retell free tier allows programmatic agent creation:
1. Create account at retell.ai
2. Obtain API key from dashboard
3. Use the `agent_spec.json` output as your payload to `POST /v1/create-agent`
4. Map fields: `system_prompt` → agent prompt; `voice_style` → voice config

### If Retell API requires paid plan (mock integration):
1. Log into Retell dashboard
2. Create a new agent manually
3. Copy the `system_prompt` field from `agent_spec.json` → paste into the agent prompt field
4. Set voice to closest match of `voice_style.voice`
5. Configure call transfer numbers from `call_transfer_protocol.routing_order`

The `agent_spec.json` is designed to be a complete, self-contained spec that maps 1:1 to Retell's configuration fields.

---

## Task Tracker (Google Sheets)

Set `GOOGLE_SHEET_ID` in `.env` to your sheet ID. The n8n workflow will log each pipeline run as a row with: `account_id`, `v1_status`, `v2_status`, `timestamp`, `changes_count`.

Alternatively, use Airtable or Supabase free tier — swap out the Google Sheets node in the n8n workflow.

---

## Dashboard

Open `dashboard/index.html` in your browser for a visual view of all accounts, their v1/v2 status, and field-level changelog. No server required — it's a static HTML file.

For a live dashboard reading real outputs, run a minimal server:
```bash
cd outputs && python -m http.server 8080
```
Then update the dashboard's data fetching to `GET /accounts/{id}/v1/account_memo.json`.

---

## File Structure

```
clara-pipeline/
├── README.md
├── docker-compose.yml
├── .env.example
├── requirements.txt
├── scripts/
│   ├── config.py               ← env vars and paths
│   ├── utils.py                ← file I/O, logging
│   ├── extractor.py            ← LLM extraction (Gemini/Groq/Ollama)
│   ├── prompt_generator.py     ← Retell agent spec builder
│   ├── differ.py               ← v1→v2 changelog generator
│   ├── pipeline_a.py           ← demo → v1
│   ├── pipeline_b.py           ← onboarding → v2
│   ├── batch_run.py            ← end-to-end batch runner
│   └── generate_sample_outputs.py  ← no-LLM demo runner
├── data/transcripts/
│   ├── demo/                   ← 5 demo call transcripts
│   └── onboarding/             ← 5 onboarding call transcripts
├── outputs/accounts/
│   └── {account_id}/v1 + v2/  ← account_memo.json + agent_spec.json
├── changelog/                  ← per-account changelog files
├── workflows/
│   └── clara_pipeline_n8n.json ← importable n8n workflow
└── dashboard/
    └── index.html              ← static diff viewer + account cards
```

---

## Known Limitations

- **No Retell API integration**: Retell's free tier doesn't expose programmatic agent creation. The pipeline produces a complete `agent_spec.json` that maps 1:1 to Retell's fields, with clear manual import instructions.
- **No audio transcription**: Pipeline assumes transcripts as input (`.txt`). To add audio support, prepend a Whisper local transcription step (via `openai-whisper` package — runs locally, free).
- **Deep-merge conflicts**: If an onboarding transcript explicitly contradicts v1 with different data, the onboarding value wins. Conflicts are not flagged separately — this could be improved.
- **List diffing**: List fields show full before/after rather than element-level diffs. Acceptable for this data size.

---

## What I'd Improve with Production Access

1. **Whisper transcription step** — add a pre-processing node that accepts `.mp3`/`.mp4` and transcribes via `openai-whisper` locally before passing to the LLM extractor.
2. **Retell API integration** — once on a paid plan, add a final step that calls `POST /v1/create-agent` and stores the Retell `agent_id` back into the memo.
3. **Conflict detection** — during the merge step, flag fields where the onboarding value explicitly contradicts v1 and require human sign-off.
4. **Fine-tuned extraction prompt** — after 20+ accounts, fine-tune or few-shot the extraction with real examples to reduce `questions_or_unknowns`.
5. **Slack/email notifications** — notify the ops team when v1 or v2 is generated, with a summary link to the dashboard.
6. **Supabase storage** — replace flat JSON files with Supabase (free tier) for queryable storage and real-time dashboard updates.
