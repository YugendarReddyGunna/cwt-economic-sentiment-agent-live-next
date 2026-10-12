import numpy as np
import pandas as pd

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


FEATURE_COLUMNS = [
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


def add_demo_target(features, seed=23):
    """
    Create synthetic targets for testing the software pipeline only.
    These are not real market returns or evidence of trading profitability.
    """
    rng = np.random.default_rng(seed)
    df = features.copy()

    # Avoid using event_surprise_mean because it is missing in the
    # currently collected dataset.
    signal = (
        0.25 * df["sentiment_3d_mean"].fillna(0).to_numpy()
        + 0.15 * df["sentiment_change_1d"].fillna(0).to_numpy()
    )

    df["target_next_day"] = (
        signal + rng.normal(0, 0.025, len(df))
    )

    df["demo_strategy_return"] = (
        df["target_next_day"] + rng.normal(0, 0.01, len(df))
    )

    df["target_is_synthetic"] = True
    return df


def walk_forward_evaluate(data, min_train_size=60):
    """
    Chronological expanding-window evaluation.

    The model trains only on observations before the prediction date.
    """
    df = data.copy()
    df["date"] = pd.to_datetime(df["date"], utc=True, errors="coerce")

    df = (
        df.dropna(subset=["date", "target_next_day"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    missing_features = set(FEATURE_COLUMNS) - set(df.columns)
    if missing_features:
        raise ValueError(
            f"Missing model features: {sorted(missing_features)}"
        )

    if len(df) <= min_train_size + 5:
        raise ValueError(
            f"Need more than {min_train_size + 5} usable rows; got {len(df)}."
        )

    X = (
        df[FEATURE_COLUMNS]
        .replace([np.inf, -np.inf], np.nan)
        .fillna(0)
        .astype(float)
    )
    y = pd.to_numeric(df["target_next_day"], errors="coerce")

    valid = y.notna()
    df = df.loc[valid].reset_index(drop=True)
    X = X.loc[valid].reset_index(drop=True)
    y = y.loc[valid].reset_index(drop=True)

    if len(df) <= min_train_size + 5:
        raise ValueError(
            f"Not enough usable targets after cleaning: {len(df)}."
        )

    rows = []
    last_model = None

    for i in range(min_train_size, len(df)):
        model = RandomForestRegressor(
            n_estimators=120,
            max_depth=4,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(X.iloc[:i], y.iloc[:i])
        predicted = float(model.predict(X.iloc[[i]])[0])

        row = {
            "date": df.loc[i, "date"],
            "actual": float(y.iloc[i]),
            "predicted": predicted,
            "target_is_synthetic": bool(
                df.loc[i, "target_is_synthetic"]
            ) if "target_is_synthetic" in df.columns else False,
        }

        if "demo_strategy_return" in df.columns:
            row["demo_strategy_return"] = float(
                df.loc[i, "demo_strategy_return"]
            )
        elif "strategy_return" in df.columns:
            row["strategy_return"] = float(
                df.loc[i, "strategy_return"]
            )

        rows.append(row)
        last_model = model

    predictions = pd.DataFrame(rows)

    metrics = {
        "n_oos": len(predictions),
        "mae": float(
            mean_absolute_error(
                predictions["actual"], predictions["predicted"]
            )
        ),
        "rmse": float(
            np.sqrt(
                mean_squared_error(
                    predictions["actual"], predictions["predicted"]
                )
            )
        ),
        "r2": float(
            r2_score(predictions["actual"], predictions["predicted"])
        ) if len(predictions) > 1 else float("nan"),
        "synthetic_targets": bool(
            predictions["target_is_synthetic"].all()
        ),
    }

    return predictions, metrics, last_model


def evaluate_strategy_permutations(
    predictions,
    thresholds=(0.0, 0.005, 0.01),
):
    """
    Compare prediction-threshold rules using an existing return series.

    This function does not create returns. It requires an observed return
    column and should be used only with appropriately aligned out-of-sample
    predictions and returns.

    Positive prediction: long.
    Negative prediction: short.
    Small predictions: stay out, depending on the threshold.
    """
    if "predicted" not in predictions.columns:
        raise ValueError("Predictions must contain a 'predicted' column.")

    if "strategy_return" in predictions.columns:
        return_column = "strategy_return"
    elif "demo_strategy_return" in predictions.columns:
        return_column = "demo_strategy_return"
    else:
        raise ValueError(
            "No return column available. Supply genuine aligned returns "
            "for real evaluation; synthetic returns are for demonstration only."
        )

    df = predictions[["predicted", return_column]].copy()
    df = df.replace([np.inf, -np.inf], np.nan).dropna()

    results = []

    for threshold in thresholds:
        position = np.where(
            df["predicted"] > threshold,
            1.0,
            np.where(df["predicted"] < -threshold, -1.0, 0.0),
        )

        strategy_returns = position * df[return_column].to_numpy()
        active = strategy_returns[position != 0]
        total = len(strategy_returns)

        results.append({
            "threshold": float(threshold),
            "observations": total,
            "trades": int(np.count_nonzero(position)),
            "win_rate": (
                float(np.mean(active > 0)) if len(active) else np.nan
            ),
            "mean_return_per_period": (
                float(np.mean(strategy_returns)) if total else np.nan
            ),
            "cumulative_return": (
                float(np.prod(1 + strategy_returns) - 1)
                if total else np.nan
            ),
            "return_source": return_column,
        })

    return pd.DataFrame(results)