import numpy as np
import pandas as pd


def adapt_calendar(events: pd.DataFrame) -> pd.DataFrame:
    """Convert the collected calendar CSV into the feature pipeline schema."""

    required = {"date", "title", "impact", "actual", "consensus"}
    missing = required - set(events.columns)

    if missing:
        raise ValueError(
            f"Calendar data is missing columns: {sorted(missing)}"
        )

    result = pd.DataFrame(index=events.index)

    result["event_time"] = pd.to_datetime(
        events["date"], errors="coerce", utc=True
    )

    result["event_name"] = events["title"].fillna("").astype(str)
    result["importance"] = events["impact"].fillna("").astype(str)

    actual = pd.to_numeric(events["actual"], errors="coerce")
    forecast = pd.to_numeric(events["consensus"], errors="coerce")

    result["actual"] = actual
    result["forecast"] = forecast
    result["actual_minus_forecast"] = actual - forecast

    result.loc[
        actual.isna() | forecast.isna(),
        "actual_minus_forecast"
    ] = np.nan

    result["source"] = "FINANCE_CALENDAR"
    result["is_synthetic"] = False

    return result