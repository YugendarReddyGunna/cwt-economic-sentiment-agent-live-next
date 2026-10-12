# Strategy Evaluation Report

## Evaluation Setup

- Underlying: S&P 500 index
- Out-of-sample observations: 62
- Evaluation: Walk-forward predictions
- Transaction costs and slippage: Not included
- Position size: One unit per active session

## Strategy Comparison

```text
                 strategy  total_sessions  active_sessions  win_rate  mean_active_return  cumulative_return  sharpe_ratio  sortino_ratio  max_drawdown  transaction_costs_included
                Long-only              62               38  0.368421           -0.000831          -0.031829     -1.620843      -2.212932     -0.043332                       False
               Long-short              62               62  0.403226           -0.001535          -0.092116     -3.590186      -4.289701     -0.111213                       False
 Threshold-0.2%-long-only              62               14  0.428571           -0.000283          -0.004364     -0.277196      -0.420900     -0.015203                       False
Threshold-0.2%-long-short              62               19  0.421053           -0.001288          -0.024851     -1.325995      -1.743179     -0.034600                       False
```

## Metric Definitions

- **Win rate:** Percentage of active positions with positive returns.
- **Mean active return:** Average return during active positions.
- **Cumulative return:** Compounded return across evaluated sessions.
- **Sharpe ratio:** Annualized mean return divided by return volatility.
- **Sortino ratio:** Annualized mean return divided by downside deviation.
- **Maximum drawdown:** Largest peak-to-trough decline in the equity curve.

## Important Limitations

- These strategies use historical index returns, not actual trading-account P&L.
- Transaction costs, slippage, taxes, and market impact are excluded.
- The out-of-sample evaluation period is small, so results are preliminary.
- Feature availability timestamps must be checked to prevent look-ahead bias.
- Long-short returns assume short positions can be executed at the corresponding index return in reverse; actual costs and constraints are not modeled.
- Results do not establish that any strategy will be profitable in live trading.
