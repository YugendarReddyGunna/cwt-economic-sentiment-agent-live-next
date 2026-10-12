from pathlib import Path

import numpy as np
import pandas as pd


# Project paths
ROOT = Path(__file__).resolve().parents[1]

INPUT = ROOT / "data" / "processed" / "walk_forward_predictions.csv"
OUTPUT = ROOT / "data" / "processed" / "strategy_comparison.csv"
REPORT = ROOT / "reports" / "strategy_evaluation.md"


def calculate_metrics(actual_returns, positions):
    """Calculate performance metrics for a trading strategy."""

    actual_returns = np.asarray(actual_returns, dtype=float)
    positions = np.asarray(positions, dtype=float)

    # Strategy return for each session
    strategy_returns = positions * actual_returns

    # Exclude sessions when the strategy holds no position
    active_mask = positions != 0
    active_returns = strategy_returns[active_mask]

    total_sessions = len(strategy_returns)
    active_sessions = len(active_returns)

    # Cumulative return across all evaluated sessions
    equity = np.cumprod(1 + strategy_returns)
    cumulative_return = equity[-1] - 1 if total_sessions else 0.0

    # Maximum drawdown
    if total_sessions:
        equity_with_initial = np.concatenate(([1.0], equity))
        running_peak = np.maximum.accumulate(equity_with_initial)
        drawdowns = equity_with_initial / running_peak - 1
        max_drawdown = float(np.min(drawdowns))
    else:
        max_drawdown = 0.0

    # Annualized Sharpe ratio
    if (
        total_sessions > 1
        and np.std(strategy_returns, ddof=1) > 0
    ):
        sharpe_ratio = (
            np.mean(strategy_returns)
            / np.std(strategy_returns, ddof=1)
            * np.sqrt(252)
        )
    else:
        sharpe_ratio = np.nan

    # Annualized Sortino ratio
    downside_returns = np.minimum(strategy_returns, 0)
    downside_deviation = np.sqrt(np.mean(downside_returns**2))

    if total_sessions and downside_deviation > 0:
        sortino_ratio = (
            np.mean(strategy_returns)
            / downside_deviation
            * np.sqrt(252)
        )
    else:
        sortino_ratio = np.nan

    # Win rate considers only sessions with an active position
    if active_sessions:
        win_rate = float(np.mean(active_returns > 0))
        mean_active_return = float(np.mean(active_returns))
    else:
        win_rate = np.nan
        mean_active_return = np.nan

    return {
        "total_sessions": total_sessions,
        "active_sessions": active_sessions,
        "win_rate": win_rate,
        "mean_active_return": mean_active_return,
        "cumulative_return": cumulative_return,
        "sharpe_ratio": sharpe_ratio,
        "sortino_ratio": sortino_ratio,
        "max_drawdown": max_drawdown,
        "transaction_costs_included": False,
    }


def main():
    # Check whether the input file exists
    if not INPUT.exists():
        raise FileNotFoundError(
            f"Input file not found: {INPUT}\n"
            "Run the walk-forward model evaluation first."
        )

    # Load out-of-sample predictions
    data = pd.read_csv(INPUT)

    required_columns = {
        "date",
        "actual_return",
        "model_prediction",
    }

    missing_columns = required_columns - set(data.columns)

    if missing_columns:
        raise ValueError(
            f"Missing required columns: {sorted(missing_columns)}"
        )

    # Clean and sort the data
    data["date"] = pd.to_datetime(data["date"], errors="coerce")
    data["actual_return"] = pd.to_numeric(
        data["actual_return"], errors="coerce"
    )
    data["model_prediction"] = pd.to_numeric(
        data["model_prediction"], errors="coerce"
    )

    data = data.replace([np.inf, -np.inf], np.nan)
    data = data.dropna(
        subset=["date", "actual_return", "model_prediction"]
    )
    data = data.sort_values("date").reset_index(drop=True)

    if data.empty:
        raise ValueError("No valid out-of-sample predictions were found.")

    actual_returns = data["actual_return"].to_numpy(dtype=float)
    predictions = data["model_prediction"].to_numpy(dtype=float)

    # Define the strategies
    strategies = {
        "Long-only": np.where(predictions > 0, 1, 0),

        "Long-short": np.where(
            predictions > 0,
            1,
            np.where(predictions < 0, -1, 0),
        ),

        "Threshold-0.2%-long-only": np.where(
            predictions > 0.002, 1, 0
        ),

        "Threshold-0.2%-long-short": np.where(
            predictions > 0.002,
            1,
            np.where(predictions < -0.002, -1, 0),
        ),
    }

    # Evaluate every strategy
    results = []

    for strategy_name, positions in strategies.items():
        metrics = calculate_metrics(actual_returns, positions)
        metrics["strategy"] = strategy_name
        results.append(metrics)

    comparison = pd.DataFrame(results)

    # Arrange columns for readability
    column_order = [
        "strategy",
        "total_sessions",
        "active_sessions",
        "win_rate",
        "mean_active_return",
        "cumulative_return",
        "sharpe_ratio",
        "sortino_ratio",
        "max_drawdown",
        "transaction_costs_included",
    ]

    comparison = comparison[column_order]

    # Save the comparison CSV
    OUTPUT.parent.mkdir(parents=True, exist_ok=True)
    comparison.to_csv(OUTPUT, index=False)

    # Format the table without requiring the tabulate package
    report_table = comparison.to_string(
        index=False,
        float_format=lambda value: f"{value:.6f}",
    )

    # Create the evaluation report
    REPORT.parent.mkdir(parents=True, exist_ok=True)

    report = (
        "# Strategy Evaluation Report\n\n"
        "## Evaluation Setup\n\n"
        "- Underlying: S&P 500 index\n"
        f"- Out-of-sample observations: {len(data)}\n"
        "- Evaluation: Walk-forward predictions\n"
        "- Transaction costs and slippage: Not included\n"
        "- Position size: One unit per active session\n\n"
        "## Strategy Comparison\n\n"
        "```text\n"
        f"{report_table}\n"
        "```\n\n"
        "## Metric Definitions\n\n"
        "- **Win rate:** Percentage of active positions with positive returns.\n"
        "- **Mean active return:** Average return during active positions.\n"
        "- **Cumulative return:** Compounded return across evaluated sessions.\n"
        "- **Sharpe ratio:** Annualized mean return divided by return volatility.\n"
        "- **Sortino ratio:** Annualized mean return divided by downside deviation.\n"
        "- **Maximum drawdown:** Largest peak-to-trough decline in the equity curve.\n\n"
        "## Important Limitations\n\n"
        "- These strategies use historical index returns, not actual trading-account P&L.\n"
        "- Transaction costs, slippage, taxes, and market impact are excluded.\n"
        "- The out-of-sample evaluation period is small, so results are preliminary.\n"
        "- Feature availability timestamps must be checked to prevent look-ahead bias.\n"
        "- Long-short returns assume short positions can be executed at the corresponding index return in reverse; actual costs and constraints are not modeled.\n"
        "- Results do not establish that any strategy will be profitable in live trading.\n"
    )

    REPORT.write_text(report, encoding="utf-8")

    # Display results
    print("\nStrategy evaluation completed successfully.")
    print(f"Input predictions: {INPUT}")
    print(f"Comparison CSV: {OUTPUT}")
    print(f"Evaluation report: {REPORT}")

    print("\nStrategy comparison:")
    print(report_table)


if __name__ == "__main__":
    main()