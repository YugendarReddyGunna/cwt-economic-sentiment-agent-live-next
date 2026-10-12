import pandas as pd

NEWS_COLS = [
    "published_at",
    "title",
    "content",
    "url",
    "source",
    "is_synthetic",
]

EVENT_COLS = [
    "event_time",
    "event_name",
    "actual",
    "forecast",
    "importance",
    "source",
    "is_synthetic",
]


def clean_news(news):
    if news is None or news.empty:
        return pd.DataFrame(columns=NEWS_COLS)

    df = news.copy()

    for column in NEWS_COLS:
        if column not in df.columns:
            df[column] = False if column == "is_synthetic" else ""

    df["published_at"] = pd.to_datetime(
        df["published_at"],
        errors="coerce",
        utc=True,
    )

    for column in ["title", "content", "url", "source"]:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    df["is_synthetic"] = (
        df["is_synthetic"]
        .fillna(False)
        .astype(bool)
    )

    df = df.dropna(subset=["published_at"])

    df = df[
        (df["title"] != "")
        | (df["content"] != "")
    ]

    return (
        df.drop_duplicates(
            subset=["published_at", "title", "url"]
        )
        .sort_values("published_at")
        [NEWS_COLS]
        .reset_index(drop=True)
    )


def clean_events(events):
    if events is None or events.empty:
        return pd.DataFrame(
            columns=EVENT_COLS + ["actual_minus_forecast"]
        )

    df = events.copy()

    for column in EVENT_COLS:
        if column not in df.columns:
            df[column] = False if column == "is_synthetic" else ""

    # Normalize timestamps to UTC.
    df["event_time"] = pd.to_datetime(
        df["event_time"],
        errors="coerce",
        utc=True,
    )

    # Preserve original values for auditing.
    df["actual_raw"] = df["actual"]
    df["forecast_raw"] = df["forecast"]

    # Convert numeric values without inventing missing figures.
    df["actual"] = pd.to_numeric(
        df["actual"],
        errors="coerce",
    )

    df["forecast"] = pd.to_numeric(
        df["forecast"],
        errors="coerce",
    )

    # Normalize text columns.
    for column in ["event_name", "importance", "source"]:
        df[column] = (
            df[column]
            .fillna("")
            .astype(str)
            .str.strip()
        )

    # Restore missing source labels for original calendar records.
    # Existing APIFY labels remain unchanged.
    df.loc[
        df["source"] == "",
        "source",
    ] = "FINANCE_CALENDAR"

    df["is_synthetic"] = (
        df["is_synthetic"]
        .fillna(False)
        .astype(bool)
    )

    # Remove only records with invalid timestamps or missing names.
    df = df.dropna(subset=["event_time"])
    df = df[df["event_name"] != ""]

    # Deduplicate within each source. Identical events from different
    # sources are retained so source coverage is not silently lost.
    df = df.drop_duplicates(
        subset=["event_time", "event_name", "source"]
    )

    df = df.sort_values("event_time")

    # Calculate surprises only when both values are numeric.
    df["actual_minus_forecast"] = (
        df["actual"] - df["forecast"]
    )

    return df.reset_index(drop=True)