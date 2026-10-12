"""Data quality checks for macro/news data and time-series targets."""
from __future__ import annotations
import pandas as pd


def summarize_coverage(news: pd.DataFrame, events: pd.DataFrame, features: pd.DataFrame) -> dict:
    """Return transparent coverage diagnostics; does not imply a complete 180-day archive."""
    def date_span(frame, column):
        if frame is None or frame.empty or column not in frame:
            return {"rows": 0, "start_utc": None, "end_utc": None, "distinct_days": 0}
        ts = pd.to_datetime(frame[column], errors="coerce", utc=True).dropna()
        if ts.empty:
            return {"rows": int(len(frame)), "start_utc": None, "end_utc": None, "distinct_days": 0}
        days = ts.dt.floor("D")
        return {"rows": int(len(frame)), "start_utc": ts.min().isoformat(),
                "end_utc": ts.max().isoformat(), "distinct_days": int(days.nunique())}

    coverage = {
        "news": date_span(news, "published_at"),
        "economic_events": date_span(events, "event_time"),
        "daily_features": date_span(features, "date"),
    }
    if features is not None and not features.empty and "date" in features:
        dates = pd.to_datetime(features["date"], errors="coerce", utc=True).dropna().dt.floor("D").drop_duplicates().sort_values()
        expected = pd.date_range(dates.min(), dates.max(), freq="D", tz="UTC") if not dates.empty else pd.DatetimeIndex([], tz="UTC")
        coverage["daily_features"]["calendar_days_in_span"] = int(len(expected))
        coverage["daily_features"]["missing_calendar_days"] = int(len(expected.difference(pd.DatetimeIndex(dates))))
        coverage["daily_features"]["span_days"] = int((dates.max() - dates.min()).days + 1) if not dates.empty else 0
    return coverage


def validate_returns_frame(frame: pd.DataFrame) -> pd.DataFrame:
    """Validate genuine outcome file schema and basic integrity before modelling."""
    required = {"date", "target_next_day", "strategy_return"}
    missing = required - set(frame.columns)
    if missing:
        raise ValueError(f"strategy_returns.csv missing required columns: {', '.join(sorted(missing))}")
    result = frame.copy()
    result["date"] = pd.to_datetime(result["date"], errors="coerce", utc=True)
    if result["date"].isna().any():
        raise ValueError("strategy_returns.csv contains invalid dates")
    if result["date"].duplicated().any():
        raise ValueError("strategy_returns.csv must contain at most one row per UTC date")
    for col in ("target_next_day", "strategy_return"):
        result[col] = pd.to_numeric(result[col], errors="coerce")
        if result[col].isna().any():
            raise ValueError(f"strategy_returns.csv contains missing/non-numeric values in {col}")
    if not result["target_next_day"].map(lambda x: pd.notna(x) and abs(float(x)) < float("inf")).all():
        raise ValueError("target_next_day contains non-finite values")
    if not result["strategy_return"].map(lambda x: pd.notna(x) and abs(float(x)) < float("inf")).all():
        raise ValueError("strategy_return contains non-finite values")
    return result.sort_values("date").reset_index(drop=True)
