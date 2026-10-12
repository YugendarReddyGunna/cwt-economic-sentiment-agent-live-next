# CWT Economic Sentiment Agent

A Python-based research prototype that combines macroeconomic news sentiment, economic calendar events, historical market data, and machine learning to explore relationships between macroeconomic conditions and subsequent market returns.

The project includes data collection, preprocessing, feature engineering, SQLite database integration, walk-forward model evaluation, experimental trading strategy comparisons, and an interactive Streamlit dashboard.

> **Disclaimer:** This is an experimental research prototype, not a validated trading system. Demo-mode targets are synthetic, and preliminary evaluation results do not establish predictive power or profitability in live trading.

## Features

- **Economic News Collection:** Collect economic news using Tavily, with optional Exa integration.
- **Economic Calendar Collection:** Retrieve economic events using configurable Apify actors.
- **Data Cleaning:** Normalize timestamps, clean source records, and prepare datasets for analysis.
- **Feature Engineering:** Generate daily news sentiment and macroeconomic features.
- **Sentiment Analysis:** Calculate baseline sentiment scores using a keyword-based lexicon.
- **Historical Market Data:** Integrate historical S&P 500 index prices for experimental return prediction.
- **SQLite Database:** Store collected economic calendar data, news records, and processed datasets in a local SQLite database.
- **Database Integration:** Join daily macroeconomic feature datasets by date.
- **Machine Learning:** Train and evaluate a model for subsequent market-return prediction.
- **Walk-Forward Validation:** Evaluate model predictions chronologically using an expanding training window.
- **Baseline Comparison:** Compare model predictions with a baseline forecasting approach.
- **Strategy Evaluation:** Compare multiple experimental trading strategies using out-of-sample predictions.
- **Performance Metrics:** Calculate MAE, RMSE, Sharpe ratio, Sortino ratio, and maximum drawdown.
- **Macro Outlook:** Generate a descriptive summary of available economic calendar and news sentiment data.
- **Visualization:** Generate sentiment timelines and walk-forward prediction charts.
- **Interactive Dashboard:** Explore project outputs using Streamlit.
- **Automated Testing:** Run tests for selected data-processing and feature-engineering components.

## Project Structure

```text
cwt-economic-sentiment-agent-live-next/
│
├── dashboard/
│   └── app.py
│
├── data/
│   ├── raw/
│   └── processed/
│
├── docs/
│   └── NEWS_PIPELINE_NOTES.md
│
├── reports/
│   ├── evaluation_report.md
│   ├── macro_outlook.md
│   ├── market_model_evaluation.md
│   └── strategy_evaluation.md
│
├── src/
│   ├── database.py
│   ├── clean_data.py
│   ├── collect_calendar.py
│   ├── collect_events.py
│   ├── collect_news.py
│   ├── config.py
│   ├── data_quality.py
│   ├── feature_engineering.py
│   ├── generate_macro_outlook.py
│   ├── modeling.py
│   ├── sentiment_analysis.py
│   ├── download_market_data.py
│   ├── evaluate_market_model.py
│   ├── evaluate_strategies.py
│   ├── trading_metrics.py
│   └── visualize.py
│
├── tests/
│
├── artifacts/
├── main.py
├── requirements.txt
├── .env.example
├── .gitignore
├── SUBMISSION_CHECKLIST.md
├── LIVE_DATA_GUIDE.md
└── README.md
```

*Note: This structure summarizes the main project components. Some generated data files and other supporting modules are omitted for readability.*

## Technology Stack

| Component | Technologies |
|---|---|
| Programming language | Python |
| Data processing | Pandas, NumPy |
| Machine learning | Scikit-learn |
| News collection | Tavily, optional Exa integration |
| Economic calendar collection | Apify |
| Database | SQLite |
| Market data | Historical S&P 500 index prices |
| Visualization | Matplotlib |
| Interactive dashboard | Streamlit |
| Testing | Pytest |
| Version control | Git, GitHub |

## Prerequisites

Before running the project, install:

- Python 3.10 or a compatible version supported by the project dependencies
- Git
- A terminal or IDE such as Visual Studio Code

API credentials are required for live data collection. The demo pipeline can be used to test the project without relying on genuine market forecasts.

## Setup and Installation

### 1. Clone the repository

```bash
git clone https://github.com/YugendarReddyGunna/cwt-economic-sentiment-agent-live-next.git
```

Navigate into the project directory:

```bash
cd cwt-economic-sentiment-agent-live-next
```

### 2. Create a virtual environment

```bash
python -m venv .venv
```

Activate the environment on Windows PowerShell:

```powershell
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file using `.env.example` as a reference.

Add the API keys and configuration values required by the selected data collection providers.

**Security requirements:**

- Never commit `.env` files or API tokens to GitHub.
- Keep `.env.example` limited to variable names and non-sensitive example values.
- Share credentials with the evaluator only through an approved secure channel.
- Do not include credentials in reports, screenshots, or logs.

Consult `LIVE_DATA_GUIDE.md` for the project's live data configuration instructions.

## Running the Project

### 1. Display available pipeline modes

```bash
python main.py --help
```

The available modes are:

- `demo`: Run the synthetic demonstration pipeline.
- `live`: Run the configured live-data pipeline.
- `collected`: Process locally collected datasets.

### 2. Run the demo pipeline

```bash
python main.py --mode demo
```

The demo mode exercises the pipeline using synthetic data. It is intended to demonstrate software execution and workflow integration, not genuine forecasting performance.

### 3. Process collected data

```bash
python main.py --mode collected
```

This mode processes the datasets available locally. Its results depend on the data files present in the project.

### 4. Run the live pipeline

```bash
python main.py --mode live
```

Live execution depends on the project's configuration, valid provider credentials, and the availability of external data sources.

Review the configuration and expected API usage before running this mode.

### 5. Import datasets into SQLite

```bash
python src/database.py
```

This command imports the configured CSV datasets into a local SQLite database at:

```text
data/macro_economics.db
```

The database integration creates tables for economic calendar records, news, processed features, and the aligned model dataset. It also creates `joined_macro_dataset`, which joins daily feature tables by date.

The SQLite database is generated locally and should not be committed unless explicitly required by the submission instructions.

### 6. Generate the macro outlook

```bash
python src/generate_macro_outlook.py
```

The generated report is saved to:

```text
reports/macro_outlook.md
```

The report summarizes the available calendar data and news sentiment. Its conclusions depend on source coverage and data quality.

### 7. Run model evaluation

```bash
python src/evaluate_market_model.py
```

This evaluates the configured market-return model using walk-forward predictions and generates the corresponding evaluation report.

### 8. Run strategy evaluation

```bash
python src/evaluate_strategies.py
```

This compares the configured experimental strategies using out-of-sample predictions.

### 9. Launch the dashboard

```bash
python -m streamlit run dashboard/app.py
```

The dashboard provides an interactive interface for exploring available project outputs.

### 10. Run the tests

```bash
python -m pytest -q
```

The tests cover selected pipeline components. A passing test suite does not independently establish model validity or trading profitability.

## Data Pipeline

The project follows this general workflow:

1. **Data collection:** Retrieve economic calendar events and economic news from configured sources.
2. **Data cleaning:** Normalize records, timestamps, and relevant numeric fields.
3. **Feature engineering:** Aggregate available news sentiment and macroeconomic event information into daily features.
4. **Database storage:** Import available datasets into SQLite and join daily feature tables by date.
5. **Market data integration:** Align macroeconomic features with historical market data.
6. **Model training:** Fit the configured machine learning model on historical observations.
7. **Walk-forward evaluation:** Generate predictions using chronological training and evaluation windows.
8. **Strategy comparison:** Evaluate experimental strategies using out-of-sample predictions.
9. **Reporting and visualization:** Produce evaluation reports, macro outlook summaries, and charts.

## Model Evaluation

The project includes a walk-forward evaluation workflow designed to preserve chronological ordering between training and testing observations.

The market-model evaluation reports:

- Mean Absolute Error (MAE)
- Root Mean Squared Error (RMSE)
- Comparison with a baseline predictor
- Number of out-of-sample predictions
- Evaluation-period details

Walk-forward evaluation is preferable to random splitting for time-dependent prediction tasks because it helps preserve the temporal order of observations.

However, chronological splitting alone does not eliminate look-ahead bias. Feature availability timestamps, event release times, and the timing of market observations must also be verified.

## Experimental Trading Strategy Evaluation

The project compares four strategy variations:

1. Long-only
2. Long-short
3. Threshold-0.2%-long-only
4. Threshold-0.2%-long-short

The evaluation reports:

| Metric | Description |
|---|---|
| Win rate | Fraction of active positions with positive returns |
| Mean active return | Average return during active positions |
| Cumulative return | Compounded return over the evaluation period |
| Sharpe ratio | Annualized mean return relative to return volatility |
| Sortino ratio | Annualized mean return relative to downside deviation |
| Maximum drawdown | Largest peak-to-trough decline in the equity curve |

The current strategy evaluation uses historical index returns rather than actual trading-account P&L. Transaction costs, slippage, taxes, market impact, and realistic execution constraints are not included.

The resulting metrics are preliminary research outputs, not evidence that a strategy will be profitable in live markets.

## Reports and Outputs

The project generates reports under `reports/`:

| File | Purpose |
|---|---|
| `evaluation_report.md` | Demonstration pipeline evaluation and synthetic-data disclosures |
| `market_model_evaluation.md` | Walk-forward market-return prediction results |
| `strategy_evaluation.md` | Comparison of experimental trading strategies |
| `macro_outlook.md` | Descriptive summary of available macroeconomic data |

Depending on the pipeline mode, processed datasets are saved under `data/processed/`, and generated visualizations are saved under `artifacts/`.

Generated results can change when the pipeline is rerun.

## Limitations

This project is an experimental research prototype and has several limitations:

- **Limited news coverage:** The collected news sample may not represent the full set of relevant macroeconomic news.
- **Incomplete event values:** Some calendar events may not contain actual, forecast, or previous values.
- **Timestamp alignment:** Event release times and news publication times require validation against the prediction timestamp.
- **Look-ahead bias:** Every feature must be checked to ensure that it would have been available when a prediction was made.
- **Synthetic demonstration targets:** Demo-mode predictive and trading metrics do not establish real-world predictive performance.
- **Small evaluation sample:** Limited out-of-sample observations make the results preliminary.
- **Execution assumptions:** Transaction costs, slippage, taxes, market impact, and realistic trading constraints are not fully modeled.
- **Strategy-specific forecasting:** The current strategy comparison evaluates trading rules based on market-return predictions; it does not establish validated forecasts of strategy-specific trading-account P&L.
- **No profitability guarantee:** Historical or experimental results do not establish future trading performance.

The project should not be used to make live trading decisions without further validation and realistic execution modeling.

## Testing

Run the automated tests with:

```bash
python -m pytest -q
```

The latest recorded test run completed with **9 passing tests**. Rerun the tests after making code changes to verify the current state of the project.

## Security

- Keep API credentials in local environment configuration.
- Never publish access tokens or secrets in source code.
- Do not commit local `.env` files.
- Review Git changes before committing.
- Share required credentials and actor configuration with the evaluator only through a secure, approved channel.

## Future Improvements

Potential improvements include:

- Expanding and validating historical economic news coverage.
- Verifying economic-calendar schemas and release timestamps.
- Auditing all features for look-ahead bias.
- Improving database relationships between raw event records, news records, and daily features.
- Evaluating the model on larger, genuinely timestamped historical datasets.
- Incorporating transaction costs and realistic execution assumptions.
- Improving financial sentiment analysis beyond a basic keyword lexicon.
- Evaluating strategy-specific expected returns or win probabilities.
- Adding additional tests for data quality, timestamp alignment, and database integrity.

## Repository

**GitHub:**  
https://github.com/YugendarReddyGunna/cwt-economic-sentiment-agent-live-next

## Disclaimer

This repository is intended for educational and experimental research purposes only. It does not provide financial advice, and its results should not be interpreted as a recommendation to buy, sell, or short any financial instrument.
