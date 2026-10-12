from pathlib import Path

import pandas as pd

from sentiment_analysis import add_sentiment

ROOT = Path(__file__).resolve().parents[1]

CALENDAR_FILE = ROOT / "data" / "raw" / "economic_calendar.csv"
NEWS_FILE = ROOT / "data" / "raw" / "tavily_economic_news.csv"
OUTPUT_DIR = ROOT / "data" / "processed"


def main():
    # Check that both source files exist.
    for file_path in (CALENDAR_FILE, NEWS_FILE):
        if not file_path.exists():
            raise FileNotFoundError(f"Missing input file: {file_path}")

    calendar = pd.read_csv(CALENDAR_FILE)
    news = pd.read_csv(NEWS_FILE)

    # Normalize calendar dates.
    calendar["date"] = pd.to_datetime(
        calendar["date"], errors="coerce", utc=True
    ).dt.strftime("%Y-%m-%d")

    # Normalize news publication dates.
    news["published_at"] = pd.to_datetime(
        news["published_at"], errors="coerce", utc=True
    )
    news["date"] = news["published_at"].dt.strftime("%Y-%m-%d")

    # Use the sentiment functions already present in your project.
    scored_news = add_sentiment(news)

    if "sentiment" not in scored_news.columns:
        raise ValueError(
            "The sentiment function did not create a 'sentiment' column."
        )

    scored_news["sentiment"] = pd.to_numeric(
        scored_news["sentiment"], errors="coerce"
    )

    # Summarize news by publication date.
    daily_news = (
        scored_news.dropna(subset=["date"])
        .groupby("date")
        .agg(
            news_article_count=("title", "count"),
            average_news_sentiment=("sentiment", "mean"),
            positive_articles=(
                "sentiment", lambda s: int((s > 0).sum())
            ),
            negative_articles=(
                "sentiment", lambda s: int((s < 0).sum())
            ),
        )
        .reset_index()
    )

    # Summarize calendar events by date.
    calendar["impact"] = (
        calendar["impact"].fillna("").astype(str).str.lower()
    )

    daily_calendar = (
        calendar.dropna(subset=["date"])
        .groupby("date")
        .agg(
            economic_event_count=("title", "count"),
            high_impact_event_count=(
                "impact",
                lambda s: int(
                    s.isin(["high", "3", "high impact"]).sum()
                ),
            ),
            events_with_actual=("actual", lambda s: int(s.notna().sum())),
        )
        .reset_index()
    )

    # Combine the two daily datasets.
    combined = pd.merge(
        daily_calendar,
        daily_news,
        on="date",
        how="outer",
    ).sort_values("date")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    output_file = OUTPUT_DIR / "daily_macro_features.csv"
    combined.to_csv(output_file, index=False)

    print("\nDaily macro dataset created successfully.")
    print("Calendar events:", len(calendar))
    print("News articles:", len(scored_news))
    print("Combined daily rows:", len(combined))
    print("Saved to:", output_file)
    print("\nPreview:")
    print(combined.head(10).to_string(index=False))


if __name__ == "__main__":
    main()