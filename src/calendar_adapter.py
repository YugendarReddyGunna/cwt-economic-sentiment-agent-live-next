import re
import pandas as pd


def extract_numeric_value(value):
    """
    Extract a numeric value from a string when it has one clear number.

    Returns None for missing, ambiguous, or non-numeric values.
    """
    if pd.isna(value):
        return None

    text = str(value).strip()

    if not text or text.lower() in {
        "nan",
        "none",
        "no formal consensus",
        "no formal consensus published",
    }:
        return None

    # Remove thousands separators: 172,000 -> 172000
    text = text.replace(",", "")

    # Extract numbers, including decimals and signed values.
    numbers = re.findall(r"[-+]?\d*\.?\d+", text)

    # Multiple numbers may represent ranges, rates, or different measures.
    # Do not guess which number is appropriate.
    if len(numbers) != 1:
        return None

    try:
        return float(numbers[0])
    except ValueError:
        return None


def adapt_calendar(events: pd.DataFrame) -> pd.DataFrame:
    """Convert calendar CSV records into the feature pipeline schema."""

    required = {"date", "title", "impact", "actual", "consensus"}
    missing = required - set(events.columns)

    if missing:
        raise ValueError(
            f"Calendar data is missing columns: {sorted(missing)}"
        )

    result = pd.DataFrame(index=events.index)

    result["event_time"] = pd.to_datetime(
        events["date"],
        errors="coerce",
        utc=True,
    )

    result["event_name"] = (
        events["title"].fillna("").astype(str).str.strip()
    )

    result["importance"] = (
        events["impact"].fillna("").astype(str).str.strip()
    )

    # Preserve the original values for audit and troubleshooting.
    result["actual_raw"] = events["actual"]
    result["forecast_raw"] = events["consensus"]

    result["actual"] = events["actual"].apply(
        extract_numeric_value
    )

    result["forecast"] = events["consensus"].apply(
        extract_numeric_value
    )

    # Do not calculate a surprise unless both values are available.
    result["actual_minus_forecast"] = (
        result["actual"] - result["forecast"]
    )

    result["source"] = "FINANCE_CALENDAR"
    result["is_synthetic"] = False

    return result