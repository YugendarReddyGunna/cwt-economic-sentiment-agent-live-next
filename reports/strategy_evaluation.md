# Strategy Evaluation Report

## Evaluation Setup

- Underlying: S&P 500 index
- Out-of-sample observations: 63
- Evaluation: Walk-forward predictions
- Transaction costs and slippage: Not included
- Position size: One unit per active session

## Strategy Comparison

```text
                 strategy  total_sessions  active_sessions  win_rate  mean_active_return  cumulative_return  sharpe_ratio  sortino_ratio  max_drawdown  transaction_costs_included
                Long-only              63               33  0.545455            0.002732           0.093260      4.143312      10.142833     -0.017051                       False
               Long-short              63               63  0.587302            0.002225           0.148758      5.380087      11.989727     -0.025757                       False
 Threshold-0.2%-long-only              63               23  0.565217            0.002745           0.064443      3.431424       8.055126     -0.015148                       False
Threshold-0.2%-long-short              63               28  0.535714            0.001711           0.048288      2.467897       5.002714     -0.023871                       False
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
