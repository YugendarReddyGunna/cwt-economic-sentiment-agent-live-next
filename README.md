CWT Economic Sentiment Agent

A Python-based research prototype that combines macroeconomic news sentiment, economic calendar events, historical market data, and machine learning to explore relationships between macroeconomic conditions and subsequent market returns.

The project includes data collection, preprocessing, feature engineering, SQLite database integration, walk-forward model evaluation, experimental trading-strategy comparisons, reports, visualizations, and an interactive Streamlit dashboard.

Disclaimer: This is an experimental research prototype, not a validated trading system. Demo-mode targets are synthetic, and preliminary evaluation results do not establish predictive power or profitability in live trading.

Features

Economic news collection: Collect economic news using Tavily, with optional Exa integration.

Economic calendar collection: Retrieve economic events using configurable Apify actors.

Data cleaning: Normalize timestamps, clean source records, and prepare datasets for analysis.

Feature engineering: Generate daily news-sentiment and macroeconomic features.

Sentiment analysis: Calculate baseline sentiment scores using a keyword-based lexicon.

Historical market data: Integrate historical S&P 500 index prices for experimental return prediction.

SQLite database: Store collected economic calendar data, news records, and processed datasets locally.

Database integration: Join daily macroeconomic feature datasets by date.

Machine learning: Train and evaluate a model for subsequent market-return prediction.

Walk-forward validation: Evaluate predictions chronologically using an expanding training window.

Baseline comparison: Compare model predictions with a baseline forecasting approach.

Strategy evaluation: Compare multiple experimental trading strategies using out-of-sample predictions.

Performance metrics: Calculate MAE, RMSE, Sharpe ratio, Sortino ratio, and maximum drawdown.

Macro outlook: Generate a descriptive summary of available economic-calendar data and news sentiment.

Visualization: Generate sentiment timelines and walk-forward prediction charts.

Interactive dashboard: Explore available project outputs using Streamlit.

Automated testing: Run tests for selected data-processing and feature-engineering components.

Project Structure

cwt-economic-sentiment-agent-live-next/
├── dashboard/
│ └── app.py
├── data/
│ ├── raw/
│ └── processed/
├── docs/
│ └── NEWS_PIPELINE_NOTES.md
├── reports/
│ ├── evaluation_report.md
│ ├── macro_outlook.md
│ ├── market_model_evaluation.md
│ └── strategy_evaluation.md
├── src/
│ ├── database.py
│ ├── clean_data.py
│ ├── collect_calendar.py
│ ├── collect_events.py
│ ├── collect_news.py
│ ├── config.py
│ ├── data_quality.py
│ ├── feature_engineering.py
│ ├── generate_macro_outlook.py
│ ├── modeling.py
│ ├── sentiment_analysis.py
│ ├── download_market_data.py
│ ├── evaluate_market_model.py
│ ├── evaluate_strategies.py
│ ├── trading_metrics.py
│ └── visualize.py
├── tests/
├── artifacts/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── SUBMISSION_CHECKLIST.md
├── LIVE_DATA_GUIDE.md
└── README.md

Note: This structure summarizes the main project components. Generated data files and other supporting modules may be omitted for readability.

Technology Stack

Component

Technologies

Programming language

Python

Data processing

Pandas, NumPy

Machine learning

Scikit-learn

News collection

Tavily, optional Exa integration

Economic calendar collection

Apify

Database

SQLite

Market data

Historical S&P 500 index prices

Visualization

Matplotlib

Interactive dashboard

Streamlit

Testing

Pytest

Version control

Git, GitHub

Prerequisites

Install the following before running the project:

Python 3.10 or a compatible version supported by the project dependencies

Git

A terminal or IDE such as Visual Studio Code

API credentials are required for live data collection. Demo mode can be used to test the software workflow without relying on genuine market forecasts.

Setup and Installation

1. Clone the repository

git clone https://github.com/YugendarReddyGunna/cwt-economic-sentiment-agent-live-next.git
cd cwt-economic-sentiment-agent-live-next

2. Create and activate a virtual environment

python -m venv .venv
.\.venv\Scripts\Activate.ps1

On macOS or Linux:

source .venv/bin/activate

3. Install dependencies

python -m pip install --upgrade pip
python -m pip install -r requirements.txt

4. Configure environment variables

Create a local .env file using .env.example as a reference. Add the API keys and configuration values required by the data providers you intend to use. Do not replace example placeholders with real credentials in .env.example.

Security requirements:

Never commit .env files or API tokens to GitHub.

Keep .env.example limited to variable names and non-sensitive example values.

Do not include credentials in reports, screenshots, or logs.

Share credentials with an evaluator only through an approved secure channel.

Review git status and git diff before committing.

Consult LIVE_DATA_GUIDE.md for live-data configuration details.

Running the Project

1. Display available pipeline modes

python main.py --help

The available modes are:

demo: Run the synthetic demonstration pipeline.

live: Run the configured live-data pipeline.

collected: Process locally collected datasets.

2. Run the demo pipeline

python main.py --mode demo

Demo mode exercises the pipeline using synthetic data. It demonstrates software execution and workflow integration; it does not demonstrate genuine forecasting performance.

3. Process collected data

python main.py --mode collected

This mode processes datasets available locally. Its output depends on which files are present and their quality, coverage, and timestamp integrity.

4. Run the live pipeline

python main.py --mode live

Live execution depends on valid provider credentials, correct configuration, compatible provider schemas, API quotas, and external data-source availability. Verify the actor input/output schema and field mappings before relying on collected records.

5. Import datasets into SQLite

python src/database.py

This command imports the configured CSV datasets into the local database:

data/macro_economics.db

The database integration creates tables for economic-calendar records, news, processed features, and the aligned model dataset. It also creates joined_macro_dataset, which joins daily feature tables by date.

The SQLite database is generated locally and should remain untracked unless the submission instructions explicitly require it. Do not commit a local database containing sensitive information.

6. Generate the macro outlook

python src/generate_macro_outlook.py

The generated report is saved to:

reports/macro_outlook.md

The report summarizes the available calendar data and news sentiment. Conclusions depend on source coverage, completeness, and data quality.

7. Run market-model evaluation

python src/evaluate_market_model.py

This evaluates the configured market-return model using walk-forward predictions and generates the corresponding evaluation report.

8. Run strategy evaluation

python src/evaluate_strategies.py

This compares the configured experimental strategies using out-of-sample predictions. The resulting metrics are exploratory and should not be interpreted as verified trading-account P&L.

9. Launch the dashboard

python -m streamlit run dashboard/app.py

The dashboard provides an interactive interface for exploring available project outputs.

10. Run the tests

python -m pytest -q

The tests cover selected pipeline components. A passing test suite does not independently establish model validity or trading profitability.

Data Pipeline

The project follows this general workflow:

Data collection: Retrieve economic-calendar events and economic news from configured sources.

Data cleaning: Normalize records, timestamps, and relevant numeric fields.

Feature engineering: Aggregate available news sentiment and macroeconomic event information into daily features.

Database storage: Import available datasets into SQLite and join daily feature tables by date.

Market-data integration: Align macroeconomic features with historical market data.

Model training: Fit the configured machine-learning model on historical observations.

Walk-forward evaluation: Generate predictions using chronological training and evaluation windows.

Strategy comparison: Evaluate experimental strategies using out-of-sample predictions.

Reporting and visualization: Produce evaluation reports, macro outlook summaries, and charts.

Model Evaluation

The project includes a walk-forward evaluation workflow designed to preserve chronological ordering between training and testing observations.

The market-model evaluation reports:

Mean Absolute Error (MAE)

Root Mean Squared Error (RMSE)

Comparison with a baseline predictor

Number of out-of-sample predictions

Evaluation-period details

Walk-forward evaluation is preferable to random splitting for time-dependent prediction tasks because it helps preserve the temporal order of observations. However, chronological splitting alone does not eliminate look-ahead bias. Feature availability timestamps, event release times, and the timing of market observations must also be verified.

Previously recorded collected-data results

A previously recorded evaluation produced 63 out-of-sample predictions:

Metric

Model

Baseline

MAE

0.005512

0.005619

RMSE

0.006853

0.006903

These figures show only a small improvement over the baseline on a limited sample. They do not establish robust predictive performance or trading profitability. They describe a previously recorded run and may change when the evaluation is rerun. Confirm the current report files before presenting these numbers as the latest results.

The model predicts subsequent market returns; the strategy evaluation applies trading rules to those predictions. This is not the same as training and validating a separate model for each strategy's expected trading-account P&L or win probability.

Experimental Trading Strategy Evaluation

The project compares four strategy variations:

Long-only

Long-short

Threshold-0.2%-long-only

Threshold-0.2%-long-short

The evaluation reports:

Metric

Description

Win rate

Fraction of active positions with positive returns

Mean active return

Average return during active positions

Cumulative return

Compounded return over the evaluation period

Sharpe ratio

Annualized mean return relative to return volatility

Sortino ratio

Annualized mean return relative to downside deviation

Maximum drawdown

Largest peak-to-trough decline in the equity curve

The current strategy evaluation uses historical index returns rather than actual trading-account P&L. Transaction costs, slippage, taxes, market impact, financing costs, borrow availability, and realistic execution constraints are not fully modeled.

The resulting metrics are preliminary research outputs, not evidence that a strategy will be profitable in live markets. Metrics based on a small sample can be unstable and sensitive to assumptions.

Reports and Outputs

The project generates reports under reports/:

File

Purpose

evaluation_report.md

Demonstration-pipeline evaluation and synthetic-data disclosures

market_model_evaluation.md

Walk-forward market-return prediction results

strategy_evaluation.md

Comparison of experimental trading strategies

macro_outlook.md

Descriptive summary of available macroeconomic data

Depending on the pipeline mode, processed datasets may be saved under data/processed/, and generated visualizations may be saved under artifacts/. Generated results can change when the pipeline is rerun.

Limitations

This project is an experimental research prototype and has several limitations:

Limited news coverage: The collected news sample may not represent all relevant macroeconomic news.

Incomplete event values: Some calendar events may not contain actual, forecast, or previous values.

Timestamp alignment: Event release times and news publication times require validation against the prediction timestamp.

Look-ahead bias: Every feature must be checked to ensure that it would have been available when a prediction was made.

Synthetic demonstration targets: Demo-mode predictive and trading metrics do not establish real-world predictive performance.

Small evaluation sample: Limited out-of-sample observations make the results preliminary.

Execution assumptions: Transaction costs, slippage, taxes, market impact, and realistic trading constraints are not fully modeled.

Strategy-specific forecasting: The current strategy comparison evaluates trading rules based on market-return predictions; it does not establish validated forecasts of strategy-specific trading-account P&L.

No profitability guarantee: Historical or experimental results do not establish future trading performance.

The project should not be used to make live trading decisions without further validation, verified point-in-time features, and realistic execution modeling.

Testing

Run the automated tests with:

python -m pytest -q

The previously recorded test run completed with 9 passing tests. Rerun the tests after code changes to verify the current state of the project. Passing tests validate only the cases covered by the suite.

Security

Keep API credentials in local environment configuration.

Never publish access tokens or secrets in source code.

Do not commit local .env files.

Keep .env.example free of real secrets.

Review Git changes before committing.

Share required credentials and actor configuration with the evaluator only through a secure, approved channel.

Future Improvements

Potential improvements include:

Expanding and validating historical economic-news coverage.

Verifying economic-calendar schemas and release timestamps.

Auditing all features for look-ahead bias and point-in-time availability.

Improving database relationships between raw event records, news records, and daily features.

Evaluating the model on larger, genuinely timestamped historical datasets.

Incorporating transaction costs and realistic execution assumptions.

Improving financial sentiment analysis beyond a basic keyword lexicon.

Evaluating strategy-specific expected returns or win probabilities.

Adding tests for data quality, timestamp alignment, and database integrity.

Reporting uncertainty and sensitivity analyses alongside performance metrics.

Repository

GitHub: https://github.com/YugendarReddyGunna/cwt-economic-sentiment-agent-live-next

Disclaimer

This repository is intended for educational and experimental research purposes only. It does not provide financial advice, and its results should not be interpreted as a recommendation to buy, sell, or short any financial instrument.
