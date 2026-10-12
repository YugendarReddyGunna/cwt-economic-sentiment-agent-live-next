import time
from datetime import date, timedelta
from pathlib import Path

import pandas as pd
import requests

API_URL = "https://www.financecalendar.com/wp-json/fc/v1/calendar"

PROJECT_ROOT = Path(__file__).resolve().parents[1]
OUTPUT_FILE = PROJECT_ROOT / "data" / "raw" / "economic_calendar.csv"


def fetch_calendar(start_date, end_date):
    """Fetch calendar events for a date range of at most 92 days."""
    response = requests.get(
        API_URL,
        params={
            "from": start_date.isoformat(),
            "to": end_date.isoformat(),
            "limit": 500,
        },
        timeout=60,
    )
    response.raise_for_status()
    payload = response.json()

    # Support common JSON response structures.
    if isinstance(payload, list):
        events = payload
    elif isinstance(payload, dict):
        events = payload.get("events", payload.get("data", []))
    else:
        raise ValueError("Unexpected API response format")

    if not isinstance(events, list):
        raise ValueError("Calendar events were not returned as a list")

    return events


def collect_calendar(days=180):
    end_date = date.today()
    start_date = end_date - timedelta(days=days - 1)

    all_events = []
    window_start = start_date

    while window_start <= end_date:
        window_end = min(
            window_start + timedelta(days=91),
            end_date,
        )

        print(f"Fetching {window_start} to {window_end}...")

        events = fetch_calendar(window_start, window_end)
        all_events.extend(events)

        print(f"Events returned: {len(events)}")

        window_start = window_end + timedelta(days=1)
        time.sleep(1)

    if not all_events:
        raise RuntimeError(
            "No calendar events returned. Check the API response."
        )

    df = pd.DataFrame(all_events)

    # Remove duplicates if the API returns overlapping events.
    df = df.drop_duplicates()

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(OUTPUT_FILE, index=False)

    print("\nCalendar collection completed.")
    print(f"Total events: {len(df)}")
    print(f"Saved to: {OUTPUT_FILE}")
    print("Columns:", ", ".join(df.columns))


if __name__ == "__main__":
    collect_calendar(days=180)