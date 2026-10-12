# CWT Economic Sentiment Agent

A reproducible Python research prototype for collecting macroeconomic news/events, creating time-based sentiment features, evaluating a baseline model with chronological walk-forward validation, and visualizing results.

**Important:** The default demo uses synthetic data only to test the software pipeline. Demo results are not real market data, do not prove predictive power, and must not be represented as trading performance.

## Setup (Windows PowerShell)

```powershell
py -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
Copy-Item .env.example .env
```

Edit `.env` locally; never commit it.

## Run

```powershell
python main.py --mode demo
pytest -q
streamlit run dashboard/app.py
```

Live collection (Tavily news and optional Apify events):

```powershell
python main.py --mode live
```

Live mode requires provider credentials in `.env`. Apify actor input/output schemas differ by actor; configure `APIFY_ACTOR_ID` and `APIFY_ACTOR_INPUT_JSON`, then verify the field mapping in `src/collect_events.py`. Optional Exa collection is supported.

## Project modules

- `src/collect_news.py`: Tavily and optional Exa search
- `src/collect_events.py`: Apify actor invocation
- `src/clean_data.py`: timestamp and field normalization
- `src/sentiment_analysis.py`: transparent starter lexicon (not finance-validated)
- `src/feature_engineering.py`: daily features and rolling sentiment
- `src/modeling.py`: expanding-window walk-forward baseline
- `src/trading_metrics.py`: Sharpe, Sortino, maximum drawdown
- `dashboard/app.py`: Streamlit dashboard

## Critical methodology notes

- Do not use information published after a prediction timestamp. Audit availability timestamps to avoid look-ahead bias.
- A news sentiment score is not the same as a market signal.
- The demo target and return series are synthetic and only test code execution.
- Live mode requires `data/raw/strategy_returns.csv` with `date,target_next_day,strategy_return` before evaluating a real target. Use genuine, timestamped strategy outcomes; do not invent P&L.
- A credible strategy evaluation needs transaction costs, slippage, execution assumptions, a fixed strategy definition, and sufficient genuine historical returns.
- API providers' plans, quotas, and schemas may change; confirm current provider documentation and permissions.
