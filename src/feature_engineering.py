import numpy as np
import pandas as pd

from src.sentiment_analysis import add_sentiment


def build_daily_features(news, events):
    """
    Build daily features from economic news and calendar events.

    Missing economic surprises remain NaN rather than being treated as zero.
    """

    # --------------------------------------------------
    # 1. Process news data
    # --------------------------------------------------
    if news is not None and not news.empty:
        n = add_sentiment(news.copy())

        n["date"] = (
            pd.to_datetime(n["published_at"], utc=True, errors="coerce")
            .dt.floor("D")
        )

        n = n.dropna(subset=["date", "sentiment"])

        dn = n.groupby("date").agg(
            news_count=("sentiment", "size"),
            sentiment_mean=("sentiment", "mean"),
            sentiment_std=("sentiment", "std"),
            sentiment_positive_share=(
                "sentiment",
                lambda x: float((x > 0).mean()),
            ),
            sentiment_negative_share=(
                "sentiment",
                lambda x: float((x < 0).mean()),
            ),
        )

    else:
        dn = pd.DataFrame(
            columns=[
                "news_count",
                "sentiment_mean",
                "sentiment_std",
                "sentiment_positive_share",
                "sentiment_negative_share",
            ],
            index=pd.DatetimeIndex([], name="date", tz="UTC"),
        )

    # --------------------------------------------------
    # 2. Process economic calendar events
    # --------------------------------------------------
    if events is not None and not events.empty:
        e = events.copy()

        e["event_time"] = pd.to_datetime(
            e["event_time"],
            utc=True,
            errors="coerce",
        )

        e = e.dropna(subset=["event_time"])

        e["date"] = e["event_time"].dt.floor("D")

        # Create the surprise column if it is missing.
        if "actual_minus_forecast" not in e.columns:
            e["actual_minus_forecast"] = np.nan

        e["actual_minus_forecast"] = pd.to_numeric(
            e["actual_minus_forecast"],
            errors="coerce",
        )

        # Count events without converting missing surprises to zero.
        de = e.groupby("date").agg(
            event_count=("event_name", "size"),
            event_surprise_mean=("actual_minus_forecast", "mean"),
            high_impact_event_count=(
                "importance",
                lambda x: int(
                    x.astype(str)
                    .str.contains("high", case=False, na=False)
                    .sum()
                ),
            ),
        )

    else:
        de = pd.DataFrame(
            columns=[
                "event_count",
                "event_surprise_mean",
                "high_impact_event_count",
            ],
            index=pd.DatetimeIndex([], name="date", tz="UTC"),
        )

    # --------------------------------------------------
    # 3. Combine news and event data
    # --------------------------------------------------
    dates = list(dn.index) + list(de.index)

    if not dates:
        return pd.DataFrame()

    start_date = min(dates)
    end_date = max(dates)

    idx = pd.date_range(
        start=start_date,
        end=end_date,
        freq="D",
        tz="UTC",
        name="date",
    )

    out = dn.join(de, how="outer").reindex(idx)

    # Missing counts mean no recorded items for that date.
    count_columns = [
        "news_count",
        "event_count",
        "high_impact_event_count",
    ]

    for column in count_columns:
        out[column] = out[column].fillna(0)

    # Missing news sentiment is set to neutral for feature construction.
    # This is a modeling convention, not proof that sentiment was neutral.
    sentiment_columns = [
        "sentiment_mean",
        "sentiment_std",
        "sentiment_positive_share",
        "sentiment_negative_share",
    ]

    for column in sentiment_columns:
        out[column] = out[column].fillna(0.0)

    # --------------------------------------------------
    # 4. Create rolling sentiment features
    # --------------------------------------------------
    out["sentiment_3d_mean"] = (
        out["sentiment_mean"]
        .rolling(window=3, min_periods=1)
        .mean()
    )

    out["sentiment_7d_mean"] = (
        out["sentiment_mean"]
        .rolling(window=7, min_periods=1)
        .mean()
    )

    out["sentiment_change_1d"] = (
        out["sentiment_mean"]
        .diff()
        .fillna(0.0)
    )

    out["news_count_7d"] = (
        out["news_count"]
        .rolling(window=7, min_periods=1)
        .sum()
    )

    # Do not replace missing economic surprises with zero.
    out = out.replace([np.inf, -np.inf], np.nan)

    # Return date as a regular column.
    return out.reset_index()