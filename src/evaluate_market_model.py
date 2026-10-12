from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error

ROOT = Path(__file__).resolve().parents[1]
INPUT = ROOT / "data" / "processed" / "aligned_model_dataset.csv"
OUTPUT = ROOT / "data" / "processed" / "walk_forward_predictions.csv"
REPORT = ROOT / "reports" / "market_model_evaluation.md"

FEATURES = [
    "news_count",
    "sentiment_mean",
    "sentiment_std",
    "sentiment_positive_share",
    "sentiment_negative_share",
    "event_count",
    "high_impact_event_count",
    "sentiment_3d_mean",
    "sentiment_7d_mean",
    "sentiment_change_1d",
    "news_count_7d",
]

def main():
    if not INPUT.exists():
        raise FileNotFoundError(f"Dataset not found: {INPUT}")

    df = pd.read_csv(INPUT)
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")
    df["next_day_return"] = pd.to_numeric(
        df["next_day_return"], errors="coerce"
    )

    df = (
        df.dropna(subset=["date", "next_day_return"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    missing = set(FEATURES) - set(df.columns)
    if missing:
        raise ValueError(f"Missing features: {sorted(missing)}")

    X = (
        df[FEATURES]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .astype(float)
    )
    y = df["next_day_return"].astype(float)

    min_train = 60
    if len(df) <= min_train + 5:
        raise ValueError(
            f"Need more than {min_train + 5} rows; found {len(df)}."
        )

    results = []

    for i in range(min_train, len(df)):
        X_train, y_train = X.iloc[:i], y.iloc[:i]
        X_test, y_test = X.iloc[[i]], y.iloc[i]

        # Baseline: predict the average return observed in the training set.
        baseline_prediction = float(y_train.mean())

        model = RandomForestRegressor(
            n_estimators=200,
            max_depth=3,
            min_samples_leaf=5,
            random_state=42,
            n_jobs=-1,
        )
        model.fit(X_train, y_train)
        prediction = float(model.predict(X_test)[0])

        results.append({
            "date": df.loc[i, "date"],
            "actual_return": float(y_test),
            "model_prediction": prediction,
            "baseline_prediction": baseline_prediction,
        })

    pred = pd.DataFrame(results)
    pred.to_csv(OUTPUT, index=False)

    model_mae = mean_absolute_error(
        pred["actual_return"], pred["model_prediction"]
    )
    baseline_mae = mean_absolute_error(
        pred["actual_return"], pred["baseline_prediction"]
    )
    model_rmse = np.sqrt(mean_squared_error(
        pred["actual_return"], pred["model_prediction"]
    ))
    baseline_rmse = np.sqrt(mean_squared_error(
        pred["actual_return"], pred["baseline_prediction"]
    ))

    REPORT.parent.mkdir(parents=True, exist_ok=True)

    report = f"""# Walk-Forward Market Model Evaluation

## Dataset
- Input: `data/processed/aligned_model_dataset.csv`
- Total aligned observations: {len(df)}
- Out-of-sample predictions: {len(pred)}
- First test date: {pred['date'].min().date()}
- Last test date: {pred['date'].max().date()}
- Target: next-observation S&P 500 index return

## Predictive metrics

| Metric | Random Forest | Mean-return baseline |
|---|---:|---:|
| MAE | {model_mae:.8f} | {baseline_mae:.8f} |
| RMSE | {model_rmse:.8f} | {baseline_rmse:.8f} |

## Limitations
- This is a small historical sample.
- The evaluation target is an index return, not strategy P&L.
- The event-surprise feature was excluded from the model because its
  availability and release-time alignment have not been verified.
- Features must be checked for publication-time alignment before results are
  interpreted as a valid real-time forecast.
- Transaction costs, slippage, and executable trading rules have not been
  included.
- Predictive error does not establish profitability.

These results are a preliminary research evaluation, not investment advice
or evidence of a profitable trading strategy.
"""

    REPORT.write_text(report, encoding="utf-8")

    print("Walk-forward evaluation completed.")
    print(f"Out-of-sample predictions: {len(pred)}")
    print(f"Random Forest MAE: {model_mae:.8f}")
    print(f"Baseline MAE: {baseline_mae:.8f}")
    print(f"Random Forest RMSE: {model_rmse:.8f}")
    print(f"Baseline RMSE: {baseline_rmse:.8f}")
    print(f"Predictions saved to: {OUTPUT}")
    print(f"Report saved to: {REPORT}")

if __name__ == "__main__":
    main()