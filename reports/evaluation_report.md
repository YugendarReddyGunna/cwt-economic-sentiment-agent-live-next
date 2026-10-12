# Model Evaluation Report

Generated: 2026-10-12 08:38 UTC  
Data status: **SYNTHETIC DEMO DATA — NOT REAL TRADING RESULTS**

## Dataset and validation
- Daily feature rows: 180
- Out-of-sample predictions: 120
- Validation: expanding-window walk-forward, one-step-ahead
- Demo target: synthetic and illustrative

## Predictive metrics
- MAE: 0.0255
- RMSE: 0.0317
- R-squared: 0.6268

## Trading risk metrics
- Return observations: 120
- Sharpe ratio: 0.3571
- Sortino ratio: 0.5075
- Maximum drawdown: -0.4261

## Limitations
Synthetic data only: metrics test software execution, not real forecasting skill or trading profitability.
- The sentiment score is a starter lexicon, not a finance-validated model.
- Trading metrics are meaningful only for a defined strategy and genuine returns.
- Include transaction costs, slippage, and execution assumptions in a real evaluation.
- Audit feature availability timestamps to avoid look-ahead bias.
