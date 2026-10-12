import yfinance as yf
import pandas as pd
from pathlib import Path

OUTPUT = Path("data/raw/market_prices.csv")
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
prices["Date"] = pd.to_datetime(prices["Date"], utc=True)
prices["Close"] = pd.to_numeric(prices["Close"], errors="coerce")
prices = prices.dropna(subset=["Date", "Close"])
prices = prices.sort_values("Date").drop_duplicates("Date")

# Next-observation return: useful as a preliminary target,
# but not yet a complete executable trading strategy.
prices["next_day_return"] = prices["Close"].shift(-1) / prices["Close"] - 1

prices.to_csv(OUTPUT, index=False)

print(f"Saved: {OUTPUT}")
print(f"Price observations: {len(prices)}")
print(f"First date: {prices['Date'].min()}")
print(f"Last date: {prices['Date'].max()}")
print("\nPreview:")
print(prices.head().to_string(index=False))
# Align market returns with the existing macro feature dataset.
FEATURES_PATH = Path("data/processed/daily_features.csv")
ALIGNED_PATH = Path("data/processed/aligned_model_dataset.csv")

if not FEATURES_PATH.exists():
    raise FileNotFoundError(
        f"Macro features not found: {FEATURES_PATH}"
    )

features = pd.read_csv(FEATURES_PATH)
prices = pd.read_csv(OUTPUT)

features["date"] = pd.to_datetime(
    features["date"], utc=True, errors="coerce"
).dt.strftime("%Y-%m-%d")

prices["Date"] = pd.to_datetime(
    prices["Date"], utc=True, errors="coerce"
).dt.strftime("%Y-%m-%d")

prices["next_day_return"] = pd.to_numeric(
    prices["next_day_return"], errors="coerce"
)

aligned = features.merge(
    prices[["Date", "next_day_return"]],
    left_on="date",
    right_on="Date",
    how="inner",
)

aligned = aligned.drop(columns=["Date"])
aligned = aligned.dropna(subset=["next_day_return"])
aligned = aligned.sort_values("date").reset_index(drop=True)

aligned.to_csv(ALIGNED_PATH, index=False)

print("\nAligned modeling dataset created.")
print(f"Rows: {len(aligned)}")
print(f"Date range: {aligned['date'].min()} to {aligned['date'].max()}")
print(f"Saved: {ALIGNED_PATH}")
print("\nTarget summary:")
print(aligned["next_day_return"].describe())
