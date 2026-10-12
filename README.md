# CWT Economic Sentiment Agent

A Python research prototype that combines macroeconomic news sentiment,
economic calendar events, historical market data, machine learning,
walk-forward evaluation, and an interactive Streamlit dashboard.

The project explores whether macroeconomic sentiment features contain
useful information for forecasting subsequent market returns.

**Important:** This is a research prototype, not a validated trading
system. Preliminary results do not establish predictive power or
profitability in live trading.

## Features

- Economic news collection using Tavily, with optional Exa integration.
- Economic calendar event collection through configurable Apify actors.
- Data cleaning and timestamp normalization.
- Daily sentiment and macroeconomic feature engineering.
- Historical S&P 500 price integration.
- Chronological walk-forward model evaluation.
- Comparison of baseline predictions and model predictions.
- Experimental trading strategy comparisons.
- Performance metrics including MAE, RMSE, Sharpe ratio, Sortino ratio,
  and maximum drawdown.
- Streamlit dashboard for exploring project outputs.
- Automated tests for selected pipeline components.

## Project Structure

```text
.
├── dashboard/
│   └── app.py
├── data/
│   ├── raw/
│   └── processed/
├── docs/
├── reports/
│   ├── evaluation_report.md
│   ├── macro_outlook.md
│   ├── market_model_evaluation.md
│   └── strategy_evaluation.md
├── src/
│   ├── clean_data.py
│   ├── collect_calendar.py
│   ├── collect_events.py
│   ├── collect_news.py
│   ├── feature_engineering.py
│   ├── modeling.py
│   ├── sentiment_analysis.py
│   ├── evaluate_market_model.py
│   ├── evaluate_strategies.py
│   └── visualize.py
├── tests/
├── main.py
├── requirements.txt
├── .env.example
└── README.md
