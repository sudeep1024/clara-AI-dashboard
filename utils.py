"""utils.py"""
import json, logging, re, sys
from datetime import datetime, timezone
from pathlib import Path
from config import OUTPUTS_DIR, CHANGELOG_DIR, DEMO_DIR, ONBOARD_DIR

# aliases for compatibility
OUTPUT_DIR = OUTPUTS_DIR
CHLOG_DIR = CHANGELOG_DIR

LOG_FORMAT = "%(asctime)s | %(levelname)-8s | %(name)s | %(message)s"
def get_logger(name):
    logger = logging.getLogger(name)
    if not logger.handlers:
        h = logging.StreamHandler(sys.stdout)
        h.setFormatter(logging.Formatter(LOG_FORMAT))
        logger.addHandler(h)
    logger.setLevel(logging.INFO)
    return logger

def account_dir(account_id, version="v1"):
    path = OUTPUTS_DIR / account_id / version
    path.mkdir(parents=True, exist_ok=True)
    return path

def changelog_dir():
    CHANGELOG_DIR.mkdir(parents=True, exist_ok=True)
    return CHANGELOG_DIR

def load_json(path):
    with open(path, "r", encoding="utf-8") as f: return json.load(f)

def save_json(data, path):
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as f: json.dump(data, f, indent=2, ensure_ascii=False)

def read_transcript(path):
    with open(path, "r", encoding="utf-8") as f: return f.read()

def infer_account_id(filename):
    m = re.match(r"(ACC-\d+)", filename, re.IGNORECASE)
    return m.group(1).upper() if m else Path(filename).stem.split("_")[0].upper()

def utcnow():
    return datetime.now(timezone.utc).isoformat()

def extract_json_block(text):
    text = re.sub(r"```(?:json)?\s*", "", text).replace("```", "")
    start = text.find("{")
    if start == -1: start = text.find("[")
    if start == -1: raise ValueError("No JSON found")
    depth = 0; opener = text[start]; closer = "}" if opener == "{" else "]"
    for i, ch in enumerate(text[start:], start=start):
        if ch == opener: depth += 1
        elif ch == closer:
            depth -= 1
            if depth == 0: return json.loads(text[start:i+1])
    raise ValueError("Could not parse JSON")
