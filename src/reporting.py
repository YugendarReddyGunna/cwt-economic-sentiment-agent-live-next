from datetime import datetime, timezone
from pathlib import Path
import math
from src.config import REPORTS

def fmt(x):
    try:
        return f"{float(x):.4f}" if x is not None and math.isfinite(float(x)) else "N/A"
    except (TypeError, ValueError):
        return "N/A"

def write_reports(model_metrics, trading_metrics, row_count, demo_mode):
    stamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M UTC")
    label = "SYNTHETIC DEMO DATA — NOT REAL TRADING RESULTS" if demo_mode else "Live collection; verify source coverage and target validity"
    text = f"""# Model Evaluation Report

Generated: {stamp}  
Data status: **{label}**

## Dataset and validation
- Daily feature rows: {row_count}
- Out-of-sample predictions: {model_metrics.get('n_oos', 0)}
- Validation: expanding-window walk-forward, one-step-ahead
- Demo target: synthetic and illustrative

## Predictive metrics
- MAE: {fmt(model_metrics.get('mae'))}
- RMSE: {fmt(model_metrics.get('rmse'))}
- R-squared: {fmt(model_metrics.get('r2'))}

## Trading risk metrics
- Return observations: {trading_metrics.get('observations', 0)}
- Sharpe ratio: {fmt(trading_metrics.get('sharpe_ratio'))}
- Sortino ratio: {fmt(trading_metrics.get('sortino_ratio'))}
- Maximum drawdown: {fmt(trading_metrics.get('max_drawdown'))}

## Limitations
{'Synthetic data only: metrics test software execution, not real forecasting skill or trading profitability.' if demo_mode else 'Audit the source data, target construction, publication timestamps, and returns before interpreting results.'}
- The sentiment score is a starter lexicon, not a finance-validated model.
- Trading metrics are meaningful only for a defined strategy and genuine returns.
- Include transaction costs, slippage, and execution assumptions in a real evaluation.
- Audit feature availability timestamps to avoid look-ahead bias.
"""
    (REPORTS / "evaluation_report.md").write_text(text, encoding="utf-8")
    macro = f"""# Macroeconomic Outlook Summary

Generated: {stamp}

Data status: **{label}**

This is a descriptive summary of pipeline records, not investment advice. Event counts depend on source coverage. Actual-minus-forecast is meaningful only when values use comparable units and event definitions. In demo mode, source records are synthetic. Validate publication times, source reliability, event coverage, and sentiment quality before making substantive conclusions.
"""
    (REPORTS / "macro_outlook.md").write_text(macro, encoding="utf-8")
