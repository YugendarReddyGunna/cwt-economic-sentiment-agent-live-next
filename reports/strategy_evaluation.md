# Strategy Evaluation Report

## Evaluation Setup

- Underlying: S&P 500 index
- Out-of-sample observations: 54
- Evaluation: Walk-forward predictions
- Transaction costs and slippage: Not included
- Position size: One unit per active session

## Strategy Comparison

```text
                 strategy  total_sessions  active_sessions  win_rate  mean_active_return  cumulative_return  sharpe_ratio  sortino_ratio  max_drawdown  transaction_costs_included
                Long-only              54               30  0.633333            0.003429           0.107232      5.111437      11.501655     -0.015161                       False
               Long-short              54               54  0.685185            0.002814           0.162620      6.983643      14.753347     -0.015161                       False
 Threshold-0.2%-long-only              54               25  0.600000            0.003483           0.090190      5.180221      15.698769     -0.013735                       False
Threshold-0.2%-long-short              54               33  0.575758            0.002359           0.080128      4.386533      11.162380     -0.013735                       False
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
