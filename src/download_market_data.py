import yfinance as yf
import pandas as pd
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]

OUTPUT = ROOT / "data" / "raw" / "market_prices.csv"
FEATURES_PATH = ROOT / "data" / "processed" / "daily_features.csv"
ALIGNED_PATH = ROOT / "data" / "processed" / "aligned_model_dataset.csv"


def download_market_prices():
    """Download S&P 500 prices and calculate next-observation returns."""

    OUTPUT.parent.mkdir(parents=True, exist_ok=True)

    print("Downloading S&P 500 historical prices...")

    prices = yf.download(
        "^GSPC",
        period="6mo",
        interval="1d",
        auto_adjust=True,
        progress=False,
    )

    if prices.empty:
        raise RuntimeError(
            "No market data returned. Check your internet connection "
            "and try again later."
        )

    # Handle both single-level and multi-level column indexes.
    if isinstance(prices.columns, pd.MultiIndex):
        prices.columns = prices.columns.get_level_values(0)

    prices = prices.reset_index()

    required = {"Date", "Close"}

    if not required.issubset(prices.columns):
        raise ValueError(
            f"Unexpected columns returned: {list(prices.columns)}"
        )

    prices = prices[["Date", "Close"]].copy()

    prices["Date"] = pd.to_datetime(
        prices["Date"],
        utc=True,
        errors="coerce",
    )

    prices["Close"] = pd.to_numeric(
        prices["Close"],
        errors="coerce",
    )

    prices = (
        prices.dropna(subset=["Date", "Close"])
        .sort_values("Date")
        .drop_duplicates(subset=["Date"])
        .reset_index(drop=True)
    )

    # Close-to-next-available-trading-day close return.
    prices["next_day_return"] = (
        prices["Close"].shift(-1) / prices["Close"] - 1
    )

    prices.to_csv(OUTPUT, index=False)

    print(f"Saved market prices: {OUTPUT}")
    print(f"Price observations: {len(prices)}")
    print(f"First date: {prices['Date'].min()}")
    print(f"Last date: {prices['Date'].max()}")
    print("\nMarket price preview:")
    print(prices.head().to_string(index=False))


def create_aligned_dataset():
    """
    Align previous trading-date features with market returns.

    date:
        Date associated with the target market return.

    feature_date:
        Previous available trading date supplying the features.

    next_day_return:
        Return from the target date's close to the next available
        trading date's close.
    """

    if not FEATURES_PATH.exists():
        raise FileNotFoundError(
            f"Feature dataset not found: {FEATURES_PATH}"
        )

    if not OUTPUT.exists():
        raise FileNotFoundError(
            f"Market price dataset not found: {OUTPUT}"
        )

    features = pd.read_csv(FEATURES_PATH)
    prices = pd.read_csv(OUTPUT)

    # Validate required columns.
    if "date" not in features.columns:
        raise ValueError(
            "Feature dataset must contain a 'date' column."
        )

    required_price_columns = {"Date", "next_day_return"}

    if not required_price_columns.issubset(prices.columns):
        raise ValueError(
            "Market prices must contain 'Date' and "
            "'next_day_return' columns."
        )

    # Normalize feature dates.
    features["date"] = pd.to_datetime(
        features["date"],
        utc=True,
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    features = features.dropna(subset=["date"])

    if features["date"].duplicated().any():
        raise ValueError(
            "Duplicate feature dates found in daily_features.csv."
        )

    # Normalize market dates and returns.
    prices["Date"] = pd.to_datetime(
        prices["Date"],
        utc=True,
        errors="coerce",
    ).dt.strftime("%Y-%m-%d")

    prices["next_day_return"] = pd.to_numeric(
        prices["next_day_return"],
        errors="coerce",
    )

    prices = (
        prices.dropna(subset=["Date"])
        .sort_values("Date")
        .drop_duplicates(subset=["Date"])
        .reset_index(drop=True)
    )

    # Rename the target date and create the preceding trading date.
    prices = prices.rename(columns={"Date": "date"})

    prices["feature_date"] = prices["date"].shift(1)

    # Remove rows without a previous trading date or target return.
    prices = prices.dropna(
        subset=["feature_date", "next_day_return"]
    ).copy()

    # Rename the feature date before merging so there are no
    # duplicate date columns.
    features = features.rename(
        columns={"date": "feature_date"}
    )

    # Match each target return to features from the preceding
    # available trading date.
    aligned = prices.merge(
        features,
        on="feature_date",
        how="inner",
        validate="many_to_one",
    )

    aligned = (
        aligned.dropna(
            subset=["date", "feature_date", "next_day_return"]
        )
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Validate unique target dates.
    if aligned["date"].duplicated().any():
        raise ValueError(
            "Aligned dataset contains duplicate target dates."
        )

    # Verify feature dates precede target dates.
    target_dates = pd.to_datetime(
        aligned["date"],
        errors="coerce",
    )

    feature_dates = pd.to_datetime(
        aligned["feature_date"],
        errors="coerce",
    )

    if target_dates.isna().any() or feature_dates.isna().any():
        raise ValueError(
            "Invalid dates found in the aligned dataset."
        )

    if not (feature_dates < target_dates).all():
        raise ValueError(
            "Timing validation failed: feature dates must precede "
            "target dates."
        )

    # Save the aligned dataset.
    ALIGNED_PATH.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    aligned.to_csv(
        ALIGNED_PATH,
        index=False,
    )

    print("\nAligned modeling dataset created successfully.")
    print(f"Rows: {len(aligned)}")
    print(f"First target date: {aligned['date'].min()}")
    print(f"Last target date: {aligned['date'].max()}")
    print(f"Saved: {ALIGNED_PATH}")

    print("\nAligned dataset preview:")
    print(
        aligned[
            ["date", "feature_date", "next_day_return"]
        ].head().to_string(index=False)
    )

    print("\nTarget return summary:")
    print(aligned["next_day_return"].describe())


def main():
    """Download market data and create the aligned dataset."""

    download_market_prices()
    create_aligned_dataset()


if __name__ == "__main__":
    main()