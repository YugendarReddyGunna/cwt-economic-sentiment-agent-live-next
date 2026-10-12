import os
import requests
import pandas as pd
from src.config import actor_input

COLUMNS = ["event_time", "event_name", "actual", "forecast", "importance", "source", "is_synthetic"]

def normalize_event_records(records):
    """Best-effort mapping. Verify these field names against your selected Apify actor."""
    rows = []
    for item in records:
        rows.append({
            "event_time": item.get("event_time") or item.get("date") or item.get("datetime") or item.get("timestamp"),
            "event_name": item.get("event_name") or item.get("event") or item.get("title") or item.get("name", ""),
            "actual": item.get("actual") or item.get("actual_value"),
            "forecast": item.get("forecast") or item.get("forecast_value") or item.get("consensus"),
            "importance": item.get("importance") or item.get("impact", ""),
            "source": "APIFY", "is_synthetic": False,
        })
    return pd.DataFrame(rows, columns=COLUMNS)

def collect_apify_events():
    token, actor_id = os.getenv("APIFY_API_TOKEN"), os.getenv("APIFY_ACTOR_ID")
    if not token or not actor_id:
        return pd.DataFrame(columns=COLUMNS), []
    url = f"https://api.apify.com/v2/acts/{actor_id}/run-sync-get-dataset-items"
    response = requests.post(url, headers={"Authorization": f"Bearer {token}"},
                             params={"format": "json", "clean": "true"},
                             json=actor_input(), timeout=180)
    response.raise_for_status()
    raw = response.json()
    if not isinstance(raw, list):
        raise ValueError("Expected Apify dataset items to be a JSON list")
    return normalize_event_records(raw), raw
