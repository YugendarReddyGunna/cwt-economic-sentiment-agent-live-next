"""News collection adapters with explicit date validation and deduplication.

Tavily search is a discovery interface, not a guaranteed complete historical archive.
Results are saved with source publication timestamps when supplied; missing/invalid dates
are retained as NaT and flagged by the caller rather than silently assigned today's date.
"""
import os
import requests
import pandas as pd
from datetime import datetime, timedelta, timezone

TAVILY_URL = "https://api.tavily.com/search"
EXA_URL = "https://api.exa.ai/search"
COLUMNS = ["published_at", "title", "content", "url", "source", "is_synthetic"]

def _normalize_records(records, source):
    rows = []
    for item in records or []:
        published = item.get("published_date") or item.get("publishedDate") or item.get("date")
        rows.append({
            "published_at": published,
            "title": str(item.get("title") or "").strip(),
            "content": str(item.get("content") or item.get("text") or "").strip(),
            "url": str(item.get("url") or "").strip(),
            "source": source,
            "is_synthetic": False,
        })
    frame = pd.DataFrame(rows, columns=COLUMNS)
    if frame.empty:
        return frame
    # Parse timestamps as UTC; invalid/missing values remain NaT and are auditable.
    frame["published_at"] = pd.to_datetime(frame["published_at"], utc=True, errors="coerce")
    frame = frame.drop_duplicates(subset=["url"], keep="first")
    frame = frame[frame["url"].ne("")]
    return frame.reset_index(drop=True)

def collect_tavily_news(query, days=180):
    key = os.getenv("TAVILY_API_KEY")
    if not key:
        raise RuntimeError("TAVILY_API_KEY is missing from local .env")
    days = int(days)
    if days < 1:
        raise ValueError("days must be >= 1")
    end_date = datetime.now(timezone.utc).date()
    start_date = end_date - timedelta(days=days)
    response = requests.post(
        TAVILY_URL,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        json={
            "query": query, "topic": "news", "search_depth": "advanced",
            "max_results": 20, "start_date": start_date.isoformat(),
            "end_date": end_date.isoformat(), "include_answer": False,
            "include_raw_content": False,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Unexpected Tavily response: expected a JSON object")
    return _normalize_records(payload.get("results", []), "TAVILY")

def collect_exa_news(query, days=180):
    key = os.getenv("EXA_API_KEY")
    if not key:
        return pd.DataFrame(columns=COLUMNS)
    days = int(days)
    if days < 1:
        raise ValueError("days must be >= 1")
    start = (datetime.now(timezone.utc) - timedelta(days=days)).date().isoformat()
    response = requests.post(
        EXA_URL,
        headers={"x-api-key": key, "Content-Type": "application/json"},
        json={
            "query": query, "type": "auto", "numResults": 50,
            "startPublishedDate": start,
            "contents": {"text": {"maxCharacters": 2000}},
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()
    if not isinstance(payload, dict):
        raise ValueError("Unexpected Exa response: expected a JSON object")
    return _normalize_records(payload.get("results", []), "EXA")

def audit_news_coverage(frame, days=180, as_of=None):
    """Return auditable coverage stats; never imply that search results are complete."""
    as_of = pd.Timestamp(as_of or datetime.now(timezone.utc)).tz_convert("UTC").normalize()
    start = as_of - pd.Timedelta(days=int(days))
    if frame is None or frame.empty:
        return {
            "requested_days": int(days), "rows": 0, "unique_days": 0,
            "missing_timestamp_rows": 0, "out_of_window_rows": 0,
            "coverage_note": "No results; this is not evidence of zero news.",
        }
    dates = pd.to_datetime(frame["published_at"], utc=True, errors="coerce")
    valid = dates.notna()
    in_window = valid & dates.ge(start) & dates.le(as_of + pd.Timedelta(days=1))
    unique_days = int(dates[in_window].dt.floor("D").nunique())
    return {
        "requested_days": int(days),
        "rows": int(len(frame)),
        "unique_days": unique_days,
        "missing_timestamp_rows": int((~valid).sum()),
        "out_of_window_rows": int((valid & ~in_window).sum()),
        "coverage_note": "Search results are not a complete historical archive; verify source coverage before modeling.",
    }
