import argparse
import json
import os
import re

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


def extract_numeric_value(value):
    """Extract one unambiguous numeric value; otherwise return NaN."""
    if pd.isna(value):
        return float("nan")

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "no formal consensus",
        "no formal consensus published",
    }:
        return float("nan")

    # Do not interpret ranges or multiple economic measures arbitrarily.
    numbers = re.findall(
        r"[-+]?\d*\.?\d+",
        text.replace(",", ""),
    )

    if len(numbers) != 1:
        return float("nan")

    try:
        return float(numbers[0])
    except ValueError:
        return float("nan")


def load_collected_data():
    """Load local news and combine the existing and Apify calendars."""
    news_path = DATA_RAW / "tavily_economic_news.csv"
    events_path = DATA_RAW / "economic_calendar.csv"
    apify_path = DATA_RAW / "apify_economic_calendar.csv"

    if not news_path.exists():
        raise FileNotFoundError(f"News CSV not found: {news_path}")

    if not events_path.exists():
        raise FileNotFoundError(f"Calendar CSV not found: {events_path}")

    news = pd.read_csv(news_path)
    events = pd.read_csv(events_path)

    # Validate news columns.
    required_news = {
        "published_at",
        "title",
        "content",
        "url",
    }

    missing_news = required_news - set(news.columns)

    if missing_news:
        raise ValueError(
            f"News CSV missing columns: {sorted(missing_news)}"
        )

    # Validate the existing calendar.
    required_events = {
        "date",
        "name",
        "title",
        "impact",
    }

    missing_events = required_events - set(events.columns)

    if missing_events:
        raise ValueError(
            f"Calendar CSV missing columns: {sorted(missing_events)}"
        )

    # Load and normalize the Apify calendar if the file exists.
    if apify_path.exists():
        apify = pd.read_csv(apify_path)

        required_apify = {
            "datetimeISO",
            "title",
            "actual",
            "forecast",
            "previous",
            "impact",
            "currency",
        }

        missing_apify = required_apify - set(apify.columns)

        if missing_apify:
            raise ValueError(
                f"Apify CSV missing columns: {sorted(missing_apify)}"
            )

        apify_timestamps = pd.to_datetime(
            apify["datetimeISO"],
            utc=True,
            errors="coerce",
        )

        apify_events = pd.DataFrame({
            "date": apify_timestamps,
            "time_utc": apify_timestamps,
            "name": apify["title"].fillna("").astype(str),
            "title": apify["title"].fillna("").astype(str),
            "impact": apify["impact"].fillna("").astype(str),
            "actual": apify["actual"],
            "consensus": apify["forecast"],
            "prior": apify["previous"],
            "currency": apify["currency"],
            "source": "APIFY",
            "is_synthetic": False,
        })

        # Preserve both CSV files; combine their rows in memory.
        events = pd.concat(
            [events, apify_events],
            ignore_index=True,
            sort=False,
        )

        print(f"Apify events loaded: {len(apify_events)}")

    else:
        print("Apify calendar not found; using the existing calendar.")

    # Normalize news timestamps.
    news["published_at"] = pd.to_datetime(
        news["published_at"],
        utc=True,
        errors="coerce",
    )

    news = news.dropna(subset=["published_at"]).copy()

    if "source" not in news.columns:
        news["source"] = "TAVILY"

    if "is_synthetic" not in news.columns:
        news["is_synthetic"] = False

    # Normalize event timestamps. Parse time_utc and date separately so
    # missing OR malformed times reliably fall back to the event date.
    if "time_utc" in events.columns:
        parsed_time = pd.to_datetime(
            events["time_utc"],
            utc=True,
            errors="coerce",
        )
    else:
        parsed_time = pd.Series(
            pd.NaT,
            index=events.index,
            dtype="datetime64[ns, UTC]",
        )

    parsed_date = pd.to_datetime(
        events["date"],
        utc=True,
        errors="coerce",
    )

    events["event_time"] = parsed_time.fillna(parsed_date)

    events["event_name"] = (
        events["name"].fillna("").astype(str).str.strip()
    )

    # Preserve raw actual and forecast values for audit purposes.
    events["actual_raw"] = (
        events["actual"].copy()
        if "actual" in events.columns
        else pd.Series(pd.NA, index=events.index)
    )

    events["forecast_raw"] = (
        events["consensus"].copy()
        if "consensus" in events.columns
        else pd.Series(pd.NA, index=events.index)
    )

    # Extract simple numeric values where unambiguous.
    events["actual"] = events["actual_raw"].apply(
        extract_numeric_value
    )

    events["forecast"] = events["forecast_raw"].apply(
        extract_numeric_value
    )

    events["importance"] = (
        events["impact"].fillna("").astype(str)
    )

    if "source" not in events.columns:
        events["source"] = "FINANCE_CALENDAR"

    if "is_synthetic" not in events.columns:
        events["is_synthetic"] = False

    # Remove records only if both the timestamp and date were invalid.
    invalid_timestamps = int(events["event_time"].isna().sum())

    if invalid_timestamps:
        print(
            f"Warning: {invalid_timestamps} events have invalid timestamps "
            "after trying both time_utc and date."
        )

    events = events.dropna(subset=["event_time"]).copy()

    print(f"News records loaded: {len(news)}")
    print(f"Calendar records loaded: {len(events)}")

    return news, events


def main(mode):
    demo = mode == "demo"
    collected = mode == "collected"

    if demo:
        news, events = make_demo_data(180)

        (DATA_RAW / "demo_news.json").write_text(
            news.to_json(
                orient="records",
                date_format="iso",
                indent=2,
            ),
            encoding="utf-8",
        )

        (DATA_RAW / "demo_events.json").write_text(
            events.to_json(
                orient="records",
                date_format="iso",
                indent=2,
            ),
            encoding="utf-8",
        )

    elif collected:
        print("Loading existing news and economic-calendar CSV files.")
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
                "Live mode requires TAVILY_API_KEY and/or EXA_API_KEY "
                "in .env"
            )

        news = pd.concat(
            parts,
            ignore_index=True,
        ).drop_duplicates(
            subset=["url", "title"]
        )

        events, raw_events = collect_apify_events()

        if raw_events:
            (DATA_RAW / "apify_events_raw.json").write_text(
                json.dumps(
                    raw_events,
                    indent=2,
                    default=str,
                ),
                encoding="utf-8",
            )

        (DATA_RAW / "live_news.json").write_text(
            news.to_json(
                orient="records",
                date_format="iso",
                indent=2,
            ),
            encoding="utf-8",
        )

    # Clean data.
    news = clean_news(news)
    events = clean_events(events)

    news.to_csv(
        DATA_PROCESSED / "news_clean.csv",
        index=False,
    )

    events.to_csv(
        DATA_PROCESSED / "events_clean.csv",
        index=False,
    )

    # Build daily features.
    features = build_daily_features(news, events)

    if features.empty:
        raise RuntimeError(
            "No usable daily features. Check the source fields "
            "and timestamps."
        )

    features.to_csv(
        DATA_PROCESSED / "daily_features.csv",
        index=False,
    )

    # Save data coverage diagnostics.
    coverage = summarize_coverage(
        news,
        events,
        features,
    )

    (DATA_PROCESSED / "data_coverage.json").write_text(
        json.dumps(
            coverage,
            indent=2,
            default=str,
        ),
        encoding="utf-8",
    )

    print(f"News rows: {len(news)}")
    print(f"Calendar rows: {len(events)}")
    print(f"Daily feature rows: {len(features)}")

    if "event_surprise_mean" in features.columns:
        valid_surprises = int(
            features["event_surprise_mean"].notna().sum()
        )

        print(
            f"Days with numeric event surprises: "
            f"{valid_surprises}/{len(features)}"
        )

    if collected:
        print("\nCollected-data mode completed.")
        print("No target or trading returns were fabricated.")
        print("Model and trading performance metrics were not calculated.")

        print(
            f"Coverage diagnostics: "
            f"{DATA_PROCESSED / 'data_coverage.json'}"
        )

        print(
            f"Feature dataset: "
            f"{DATA_PROCESSED / 'daily_features.csv'}"
        )

        print(
            "Note: verify source coverage and event timestamps before modeling."
        )

        return

    if demo:
        data = add_demo_target(features)

    else:
        path = DATA_RAW / "strategy_returns.csv"

        if not path.exists():
            raise RuntimeError(
                "Live collection completed, but "
                "data/raw/strategy_returns.csv is missing. "
                "Genuine dated target values and strategy returns "
                "are required for valid model and trading evaluation."
            )

        ret = validate_returns_frame(
            pd.read_csv(path)
        )

        features["date"] = pd.to_datetime(
            features["date"],
            utc=True,
        )

        data = features.merge(
            ret[["date", "target_next_day", "strategy_return"]],
            on="date",
            how="inner",
        )

        data["demo_strategy_return"] = data["strategy_return"]
        data["target_is_synthetic"] = False

    min_train = min(
        60,
        max(30, len(data) // 2),
    )

    predictions, model_metrics, model = walk_forward_evaluate(
        data,
        min_train_size=min_train,
    )

    predictions.to_csv(
        DATA_PROCESSED / "model_predictions.csv",
        index=False,
    )

    if model is not None:
        joblib.dump(
            model,
            ARTIFACTS / "baseline_model.joblib",
        )

    trading_metrics = calculate_trading_metrics(
        predictions["demo_strategy_return"]
    )

    make_charts(
        features,
        predictions,
    )

    write_reports(
        model_metrics,
        trading_metrics,
        len(features),
        demo,
    )

    print(
        f"Pipeline completed. "
        f"Mode={'DEMO (synthetic)' if demo else 'LIVE'}"
    )

    print(f"Feature rows: {len(features)}")
    print(f"Out-of-sample predictions: {len(predictions)}")
    print(f"Model metrics: {model_metrics}")
    print(f"Trading metrics: {trading_metrics}")

    print(
        f"Coverage diagnostics: "
        f"{DATA_PROCESSED / 'data_coverage.json'}"
    )

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