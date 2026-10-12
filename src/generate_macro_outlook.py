from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]

FEATURE_FILE = ROOT / "data" / "processed" / "daily_macro_features.csv"
CALENDAR_FILE = ROOT / "data" / "raw" / "economic_calendar.csv"
OUTPUT_FILE = ROOT / "reports" / "macro_outlook.md"


def main():
    if not FEATURE_FILE.exists():
        raise FileNotFoundError(f"Missing dataset: {FEATURE_FILE}")

    features = pd.read_csv(FEATURE_FILE)
    calendar = pd.read_csv(CALENDAR_FILE)

    features["date"] = pd.to_datetime(features["date"], errors="coerce")
    calendar["date"] = pd.to_datetime(calendar["date"], errors="coerce")

    news_count = features["news_article_count"].fillna(0).sum()

    valid_sentiment = features["average_news_sentiment"].dropna()

    if len(valid_sentiment):
        overall_sentiment = valid_sentiment.mean()
    else:
        overall_sentiment = None

    event_count = len(calendar)
    high_impact = (
        calendar["impact"].astype(str).str.lower()
        .isin(["high", "3", "high impact"]).sum()
    )

    latest_date = features["date"].max()
    earliest_date = features["date"].min()

    if overall_sentiment is None:
        sentiment_label = "Insufficient sentiment data"
    elif overall_sentiment > 0.05:
        sentiment_label = "Positive"
    elif overall_sentiment < -0.05:
        sentiment_label = "Negative"
    else:
        sentiment_label = "Neutral or mixed"

    report = f"""# Macro Outlook

**Data period:** {earliest_date.date()} to {latest_date.date()}

## Executive Summary

The collected dataset contains {event_count} economic-calendar events
and {int(news_count)} news-article observations.

The rule-based news sentiment score is classified as **{sentiment_label}**.
This is a descriptive indicator, not a validated market forecast or trading signal.

## Economic Calendar

- Total calendar events: {event_count}
- High-impact events: {int(high_impact)}
- Calendar source: Finance Calendar API

## News Sentiment

- Articles represented in daily features: {int(news_count)}
- Mean daily sentiment score: {
        f"{overall_sentiment:.4f}" if overall_sentiment is not None else "Unavailable"
    }

The sentiment method uses a simple keyword lexicon. It may miss context,
negation, and the difference between inflation concerns and positive economic
growth. Results should therefore be interpreted cautiously.

## Research Limitations

- The news sample contains only the articles actually collected; it is not
  a complete archive of all macroeconomic news.
- Missing actual, forecast, and prior values have not been fabricated.
- No verified strategy-return dataset has been supplied yet.
- Sharpe ratio, Sortino ratio, maximum drawdown, and predictive performance
  must not be claimed without suitable return data and out-of-sample testing.

## Next Research Steps

1. Expand and verify historical news coverage.
2. Validate event timestamps and economic-calendar values.
3. Join macro features to market outcomes without look-ahead leakage.
4. Run walk-forward validation using genuine historical returns.
"""

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_FILE.write_text(report, encoding="utf-8")

    print("Macro outlook created.")
    print("Saved to:", OUTPUT_FILE)
    print("\n", report)


if __name__ == "__main__":
    main()