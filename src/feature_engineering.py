import numpy as np
import pandas as pd

from src.sentiment_analysis import add_sentiment


# Use a cutoff before the US stock market closes.
MARKET_TIMEZONE = "America/New_York"
PREDICTION_CUTOFF = "15:45"


def _prepare_timestamps(df, column):
    """Convert a timestamp column to UTC-aware datetimes."""
    df[column] = pd.to_datetime(
        df[column],
        utc=True,
        errors="coerce",
    )
    return df


def _prepare_daily_features(df, timestamp_column):
    """
    Assign records to US Eastern calendar dates.

    Records after the prediction cutoff are excluded.
    Output dates are represented as UTC midnight so that
    existing date-based dataset alignment remains compatible.
    """
    df = _prepare_timestamps(df, timestamp_column)
    df = df.dropna(subset=[timestamp_column]).copy()

    eastern = df[timestamp_column].dt.tz_convert(
        MARKET_TIMEZONE
    )

    df["_session_date"] = eastern.dt.strftime("%Y-%m-%d")
    df["_local_time"] = eastern.dt.strftime("%H:%M")

    # Retain information available by the prediction cutoff.
    df = df[
        df["_local_time"] <= PREDICTION_CUTOFF
    ].copy()

    return df


def build_daily_features(news, events):
    """
    Build daily economic-news and calendar features.

    Information published or occurring after 15:45 US Eastern
    time is excluded from that day's feature calculations.

    Economic surprises are retained for descriptive analysis
    only. Their release availability is not independently
    verified, and they are not model input features.
    """

    # --------------------------------------------------
    # 1. Process news
    # --------------------------------------------------
    if news is not None and not news.empty:
        n = add_sentiment(news.copy())

        n = _prepare_daily_features(
            n,
            "published_at",
        )

        n = n.dropna(subset=["sentiment"])

        dn = n.groupby("_session_date").agg(
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

        dn.index = pd.to_datetime(
            dn.index,
            utc=True,
        )
        dn.index.name = "date"

    else:
        dn = pd.DataFrame(
            columns=[
                "news_count",
                "sentiment_mean",
                "sentiment_std",
                "sentiment_positive_share",
                "sentiment_negative_share",
            ],
            index=pd.DatetimeIndex(
                [],
                name="date",
                tz="UTC",
            ),
        )

    # --------------------------------------------------
    # 2. Process economic events
    # --------------------------------------------------
    if events is not None and not events.empty:
        e = events.copy()

        e = _prepare_daily_features(
            e,
            "event_time",
        )

        if "event_name" not in e.columns:
            e["event_name"] = ""

        if "importance" not in e.columns:
            e["importance"] = ""

        if "actual" not in e.columns:
            e["actual"] = np.nan

        if "forecast" not in e.columns:
            e["forecast"] = np.nan

        e["actual"] = pd.to_numeric(
            e["actual"],
            errors="coerce",
        )

        e["forecast"] = pd.to_numeric(
            e["forecast"],
            errors="coerce",
        )

        e["actual_minus_forecast"] = (
            e["actual"] - e["forecast"]
        )

        de = e.groupby("_session_date").agg(
            event_count=("event_name", "size"),
            event_surprise_mean=(
                "actual_minus_forecast",
                "mean",
            ),
            high_impact_event_count=(
                "importance",
                lambda x: int(
                    x.astype(str)
                    .str.contains(
                        "high",
                        case=False,
                        na=False,
                    )
                    .sum()
                ),
            ),
        )

        de.index = pd.to_datetime(
            de.index,
            utc=True,
        )
        de.index.name = "date"

    else:
        de = pd.DataFrame(
            columns=[
                "event_count",
                "event_surprise_mean",
                "high_impact_event_count",
            ],
            index=pd.DatetimeIndex(
                [],
                name="date",
                tz="UTC",
            ),
        )

    # --------------------------------------------------
    # 3. Combine daily features
    # --------------------------------------------------
    dates = list(dn.index) + list(de.index)

    if not dates:
        return pd.DataFrame()

    idx = pd.date_range(
        start=min(dates),
        end=max(dates),
        freq="D",
        tz="UTC",
        name="date",
    )

    out = dn.join(de, how="outer").reindex(idx)

    # --------------------------------------------------
    # 4. Fill count columns
    # --------------------------------------------------
    count_columns = [
        "news_count",
        "event_count",
        "high_impact_event_count",
    ]

    for column in count_columns:
        out[column] = (
            out[column]
            .fillna(0)
            .astype(int)
        )

    # --------------------------------------------------
    # 5. Fill missing sentiment statistics
    # --------------------------------------------------
    sentiment_columns = [
        "sentiment_mean",
        "sentiment_std",
        "sentiment_positive_share",
        "sentiment_negative_share",
    ]

    for column in sentiment_columns:
        out[column] = out[column].fillna(0.0)

    # Do not replace missing event surprises with zero.
    # Missing data does not mean the surprise was zero.

    # --------------------------------------------------
    # 6. Calculate rolling features
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

    # --------------------------------------------------
    # 7. Final cleanup
    # --------------------------------------------------
    out = out.replace(
        [np.inf, -np.inf],
        np.nan,
    )

    return out.reset_index()