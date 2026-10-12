from pathlib import Path

import pandas as pd

from feature_engineering import build_daily_features
from calendar_adapter import adapt_calendar

ROOT = Path(__file__).resolve().parents[1]

NEWS_FILE = ROOT / "data" / "raw" / "tavily_economic_news.csv"
CALENDAR_FILE = ROOT / "data" / "raw" / "economic_calendar.csv"
OUTPUT_FILE = ROOT / "data" / "processed" / "model_features.csv"


def main():
    # Verify input files.
    for path in (NEWS_FILE, CALENDAR_FILE):
        if not path.exists():
            raise FileNotFoundError(f"Missing input file: {path}")

    news = pd.read_csv(NEWS_FILE)
    calendar_raw = pd.read_csv(CALENDAR_FILE)

    # Normalize the calendar schema.
    events = adapt_calendar(calendar_raw)

    # Keep US events relevant to the assessment.
    event_names = events["event_name"].fillna("").str.lower()

    us_relevant = (
    event_names.str.startswith("us ")
    | event_names.str.contains(
        r"\b(?:fomc|federal reserve)\b",
        regex=True,
    )
)

    events = events.loc[us_relevant].copy()

    # Avoid look-ahead leakage: realized surprises are not predictive
    # features until release timestamps and availability are verified.
    events["actual_minus_forecast"] = float("nan")

    # Build daily features from the original news and filtered events.
    features = build_daily_features(news, events)

    if features.empty:
        raise ValueError("No daily features were generated.")

    # Keep dates consistently represented as YYYY-MM-DD.
    features["date"] = pd.to_datetime(
        features["date"], utc=True, errors="coerce"
    ).dt.strftime("%Y-%m-%d")

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    features.to_csv(OUTPUT_FILE, index=False)

    print("Model features created successfully.")
    print("News articles:", len(news))
    print("Relevant calendar events:", len(events))
    print("Feature rows:", len(features))
    print("Feature columns:", features.columns.tolist())
    print("Saved to:", OUTPUT_FILE)
    print("\nPreview:")
    print(features.head(5).to_string(index=False))


if __name__ == "__main__":
    main()