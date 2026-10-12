# Walk-Forward Market Model Evaluation

## Dataset
- Input: `data/processed/aligned_model_dataset.csv`
- Total aligned observations: 123
- Out-of-sample predictions: 63
- First test date: 2026-07-13
- Last test date: 2026-10-08
- Target: next-observation S&P 500 index return

## Predictive metrics

| Metric | Random Forest | Mean-return baseline |
|---|---:|---:|
| MAE | 0.00551213 | 0.00561917 |
| RMSE | 0.00685281 | 0.00690337 |

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
