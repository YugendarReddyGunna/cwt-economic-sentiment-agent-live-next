from pathlib import Path
import json
import os
from dotenv import load_dotenv

ROOT = Path(__file__).resolve().parents[1]
load_dotenv(ROOT / ".env")
DATA_RAW = ROOT / "data" / "raw"
DATA_PROCESSED = ROOT / "data" / "processed"
ARTIFACTS = ROOT / "artifacts"
REPORTS = ROOT / "reports"
for folder in (DATA_RAW, DATA_PROCESSED, ARTIFACTS, REPORTS):
    folder.mkdir(parents=True, exist_ok=True)

def actor_input():
    try:
        value = json.loads(os.getenv("APIFY_ACTOR_INPUT_JSON", "{}") or "{}")
    except json.JSONDecodeError as exc:
        raise ValueError("APIFY_ACTOR_INPUT_JSON must be valid JSON") from exc
    if not isinstance(value, dict):
        raise ValueError("APIFY_ACTOR_INPUT_JSON must be a JSON object")
    return value
