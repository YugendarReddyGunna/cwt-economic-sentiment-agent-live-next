# Walk-Forward Market Model Evaluation

## Dataset
- Input: `data/processed/aligned_model_dataset.csv`
- Total aligned observations: 114
- Out-of-sample predictions: 54
- First test date: 2026-07-24
- Last test date: 2026-10-08
- Target: next-observation S&P 500 index return

## Predictive metrics

| Metric | Random Forest | Mean-return baseline |
|---|---:|---:|
| MAE | 0.00533540 | 0.00563526 |
| RMSE | 0.00659327 | 0.00691073 |

## Limitations
- This is a small historical sample.
- The evaluation target is an index return, not strategy P&L.
- The event-surprise feature was excluded because all its values are missing.
- Features must be checked for publication-time alignment before results are
  interpreted as a valid real-time forecast.
- Transaction costs, slippage, and executable trading rules have not been
  included.
- Predictive error does not establish profitability.

These results are a preliminary research evaluation, not investment advice
or evidence of a profitable trading strategy.
