import argparse
import json
import os

import pandas as pd
import joblib

from src.config import DATA_RAW, DATA_PROCESSED, ARTIFACTS
from src.demo_data import make_demo_data
from src.collect_news import collect_tavily_news, collect_exa_news
from src.collect_events import collect_apify_events
from src.clean_data import clean_news, clean_events
from src.feature_engineering import build_daily_features
from src.modeling import add_demo_target, walk_forward_evaluate
from src.trading_metrics import calculate_trading_metrics
from src.visualize import make_charts
from src.reporting import write_reports
from src.data_quality import summarize_coverage, validate_returns_frame


def load_collected_data():
    news_path = DATA_RAW / "tavily_economic_news.csv"
    events_path = DATA_RAW / "economic_calendar.csv"

    if not news_path.exists():
        raise FileNotFoundError(f"News CSV not found: {news_path}")

    if not events_path.exists():
        raise FileNotFoundError(f"Calendar CSV not found: {events_path}")

    news = pd.read_csv(news_path)
    events = pd.read_csv(events_path)

    # Validate the source columns.
    required_news = {"published_at", "title", "content", "url"}
    required_events = {"date", "name", "title", "impact"}

    missing_news = required_news - set(news.columns)
    missing_events = required_events - set(events.columns)

    if missing_news:
        raise ValueError(f"News CSV missing columns: {sorted(missing_news)}")

    if missing_events:
        raise ValueError(
            f"Calendar CSV missing columns: {sorted(missing_events)}"
        )

    # Prepare news data.
    news["published_at"] = pd.to_datetime(
        news["published_at"], utc=True, errors="coerce"
    )
    news = news.dropna(subset=["published_at"])

    if "source" not in news.columns:
        news["source"] = "TAVILY"

    if "is_synthetic" not in news.columns:
        news["is_synthetic"] = False

    # Map calendar columns to the names expected by clean_events().
    events["event_time"] = pd.to_datetime(
        events["time_utc"].fillna(events["date"])
        if "time_utc" in events.columns
        else events["date"],
        utc=True,
        errors="coerce",
    )

    events["event_name"] = events["name"].fillna("").astype(str)
    events["forecast"] = (
        events["consensus"]
        if "consensus" in events.columns
        else pd.NA
    )
    events["importance"] = events["impact"].fillna("").astype(str)
    events["source"] = "FINANCE_CALENDAR"
    events["is_synthetic"] = False

    # Convert textual actuals and forecasts only when they are numeric.
    # Missing or textual values remain missing; they are not replaced with zero.
    events["actual"] = pd.to_numeric(
        events["actual"] if "actual" in events.columns else pd.Series(
            pd.NA, index=events.index
        ),
        errors="coerce",
    )
    events["forecast"] = pd.to_numeric(
        events["forecast"], errors="coerce"
    )

    return news, events


def main(mode):
    demo = mode == "demo"
    collected = mode == "collected"

    if demo:
        news, events = make_demo_data(180)

        (DATA_RAW / "demo_news.json").write_text(
            news.to_json(orient="records", date_format="iso", indent=2),
            encoding="utf-8",
        )
        (DATA_RAW / "demo_events.json").write_text(
            events.to_json(orient="records", date_format="iso", indent=2),
            encoding="utf-8",
        )

    elif collected:
        print("Using existing local news and economic-calendar CSV files.")
        news, events = load_collected_data()

    else:
        query = os.getenv(
            "NEWS_QUERY",
            "macroeconomic outlook CPI Federal Reserve employment inflation",
        )
        days = int(os.getenv("NEWS_DAYS", "180"))
        parts = []

        if os.getenv("TAVILY_API_KEY"):
            parts.append(collect_tavily_news(query, days))

        if os.getenv("EXA_API_KEY"):
            parts.append(collect_exa_news(query, days))

        if not parts:
            raise RuntimeError(
                "Live mode requires TAVILY_API_KEY and/or EXA_API_KEY in .env"
            )

        news = pd.concat(parts, ignore_index=True).drop_duplicates(
            subset=["url", "title"]
        )

        events, raw_events = collect_apify_events()

        if raw_events:
            (DATA_RAW / "apify_events_raw.json").write_text(
                json.dumps(raw_events, indent=2, default=str),
                encoding="utf-8",
            )

        (DATA_RAW / "live_news.json").write_text(
            news.to_json(orient="records", date_format="iso", indent=2),
            encoding="utf-8",
        )

    news = clean_news(news)
    events = clean_events(events)

    news.to_csv(DATA_PROCESSED / "news_clean.csv", index=False)
    events.to_csv(DATA_PROCESSED / "events_clean.csv", index=False)

    features = build_daily_features(news, events)

    if features.empty:
        raise RuntimeError(
            "No usable daily features. Check the source fields and timestamps."
        )

    features.to_csv(DATA_PROCESSED / "daily_features.csv", index=False)

    coverage = summarize_coverage(news, events, features)
    (DATA_PROCESSED / "data_coverage.json").write_text(
        json.dumps(coverage, indent=2, default=str),
        encoding="utf-8",
    )

    print(f"News rows: {len(news)}")
    print(f"Calendar rows: {len(events)}")
    print(f"Daily feature rows: {len(features)}")

    if collected:
        print("\nCollected-data mode completed.")
        print("No target or trading returns were fabricated.")
        print("Model and trading performance metrics were not calculated.")
        print(f"Coverage diagnostics: {DATA_PROCESSED / 'data_coverage.json'}")
        print(f"Feature dataset: {DATA_PROCESSED / 'daily_features.csv'}")
        print("Note: verify source coverage and event timestamps before modeling.")
        return

    if demo:
        data = add_demo_target(features)
    else:
        path = DATA_RAW / "strategy_returns.csv"

        if not path.exists():
            raise RuntimeError(
                "Live collection completed, but data/raw/strategy_returns.csv "
                "is missing. Genuine dated target values and strategy returns "
                "are required for valid model and trading evaluation."
            )

        ret = validate_returns_frame(pd.read_csv(path))
        features["date"] = pd.to_datetime(features["date"], utc=True)
        data = features.merge(
            ret[["date", "target_next_day", "strategy_return"]],
            on="date",
            how="inner",
        )
        data["demo_strategy_return"] = data["strategy_return"]
        data["target_is_synthetic"] = False

    min_train = min(60, max(30, len(data) // 2))

    predictions, model_metrics, model = walk_forward_evaluate(
        data, min_train_size=min_train
    )

    predictions.to_csv(
        DATA_PROCESSED / "model_predictions.csv", index=False
    )

    if model is not None:
        joblib.dump(model, ARTIFACTS / "baseline_model.joblib")

    trading_metrics = calculate_trading_metrics(
        predictions["demo_strategy_return"]
    )

    make_charts(features, predictions)
    write_reports(model_metrics, trading_metrics, len(features), demo)

    print(f"Pipeline completed. Mode={'DEMO (synthetic)' if demo else 'LIVE'}")
    print(f"Feature rows: {len(features)}")
    print(f"Out-of-sample predictions: {len(predictions)}")
    print(f"Model metrics: {model_metrics}")
    print(f"Trading metrics: {trading_metrics}")
    print(f"Coverage diagnostics: {DATA_PROCESSED / 'data_coverage.json'}")
    print(f"Outputs: {DATA_PROCESSED}, {ARTIFACTS}, reports/")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="CWT Economic Sentiment Agent"
    )
    parser.add_argument(
        "--mode",
        choices=["demo", "live", "collected"],
        default="demo",
    )
    main(parser.parse_args().mode)