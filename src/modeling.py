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

    These targets are not real market returns and cannot demonstrate
    trading profitability.
    """
    rng = np.random.default_rng(seed)
    df = features.copy()

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

    Each prediction is generated using a model trained only on
    earlier observations.

    IMPORTANT:
    This function cannot independently guarantee that the input
    features were available at prediction time. That must be ensured
    during feature construction and dataset alignment.
    """
    if min_train_size < 1:
        raise ValueError("min_train_size must be at least 1.")

    if data is None or data.empty:
        raise ValueError("Input data is empty.")

    df = data.copy()

    required_columns = {"date", "target_next_day"}
    missing_columns = required_columns - set(df.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    df["date"] = pd.to_datetime(
        df["date"],
        utc=True,
        errors="coerce",
    )

    df["target_next_day"] = pd.to_numeric(
        df["target_next_day"],
        errors="coerce",
    )

    df = (
        df.dropna(subset=["date", "target_next_day"])
        .sort_values("date")
        .reset_index(drop=True)
    )

    # Require one observation per UTC calendar date.
    utc_dates = df["date"].dt.floor("D")

    if utc_dates.duplicated().any():
        raise ValueError(
            "Input data must contain one row per UTC date."
        )

    missing_features = set(FEATURE_COLUMNS) - set(df.columns)

    if missing_features:
        raise ValueError(
            f"Missing model features: {sorted(missing_features)}"
        )

    if len(df) <= min_train_size + 5:
        raise ValueError(
            f"Need more than {min_train_size + 5} usable rows; "
            f"got {len(df)}."
        )

    # Convert feature columns to numeric values.
    X = df[FEATURE_COLUMNS].copy()

    for column in FEATURE_COLUMNS:
        X[column] = pd.to_numeric(
            X[column],
            errors="coerce",
        )

    X = (
        X.replace([np.inf, -np.inf], np.nan)
        .fillna(0.0)
        .astype(float)
    )

    y = df["target_next_day"].astype(float)

    rows = []
    last_model = None

    # Expanding-window evaluation:
    # train on rows before i, then predict row i.
    for i in range(min_train_size, len(df)):
        model = RandomForestRegressor(
            n_estimators=120,
            max_depth=4,
            min_samples_leaf=4,
            random_state=42,
            n_jobs=-1,
        )

        model.fit(
            X.iloc[:i],
            y.iloc[:i],
        )

        predicted = float(
            model.predict(X.iloc[[i]])[0]
        )

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
                predictions["actual"],
                predictions["predicted"],
            )
        ),
        "rmse": float(
            np.sqrt(
                mean_squared_error(
                    predictions["actual"],
                    predictions["predicted"],
                )
            )
        ),
        "r2": float(
            r2_score(
                predictions["actual"],
                predictions["predicted"],
            )
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
    Compare prediction-threshold strategies using supplied returns.

    Positive prediction: long.
    Negative prediction: short.
    Predictions within the threshold: no position.

    Returns are not generated by this function.
    Transaction costs and slippage are not included.
    """
    if predictions is None or predictions.empty:
        raise ValueError("Predictions are empty.")

    if "predicted" not in predictions.columns:
        raise ValueError(
            "Predictions must contain a 'predicted' column."
        )

    if "strategy_return" in predictions.columns:
        return_column = "strategy_return"

    elif "demo_strategy_return" in predictions.columns:
        return_column = "demo_strategy_return"

    else:
        raise ValueError(
            "No return column available. Supply genuine aligned "
            "returns for real evaluation. Synthetic returns are "
            "for demonstration only."
        )

    df = predictions[
        ["predicted", return_column]
    ].copy()

    df["predicted"] = pd.to_numeric(
        df["predicted"],
        errors="coerce",
    )

    df[return_column] = pd.to_numeric(
        df[return_column],
        errors="coerce",
    )

    df = (
        df.replace([np.inf, -np.inf], np.nan)
        .dropna()
    )

    if df.empty:
        raise ValueError(
            "No valid prediction/return observations remain."
        )

    results = []

    for threshold in thresholds:
        if not np.isfinite(threshold) or threshold < 0:
            raise ValueError(
                "Thresholds must be finite and non-negative."
            )

        position = np.where(
            df["predicted"] > threshold,
            1.0,
            np.where(
                df["predicted"] < -threshold,
                -1.0,
                0.0,
            ),
        )

        period_returns = (
            position * df[return_column].to_numpy()
        )

        active = period_returns[position != 0]
        total = len(period_returns)

        results.append({
            "threshold": float(threshold),
            "observations": total,
            "trades": int(np.count_nonzero(position)),
            "win_rate": (
                float(np.mean(active > 0))
                if len(active)
                else np.nan
            ),
            "mean_return_per_period": float(
                np.mean(period_returns)
            ),
            "cumulative_return": float(
                np.prod(1 + period_returns) - 1
            ),
            "return_source": return_column,
        })

    return pd.DataFrame(results)