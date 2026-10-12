from pathlib import Path
import pandas as pd
import streamlit as st

ROOT = Path(__file__).resolve().parents[1]
FEATURES = ROOT / "data" / "processed" / "daily_features.csv"
PREDICTIONS = ROOT / "data" / "processed" / "model_predictions.csv"
REPORT = ROOT / "reports" / "evaluation_report.md"

st.set_page_config(page_title="CWT Economic Sentiment Agent", layout="wide")
st.title("CWT Economic Sentiment Agent")
st.caption("Research prototype. Synthetic demo metrics are not real trading performance.")
if not FEATURES.exists():
    st.warning("Run `python main.py --mode demo` from the project root first.")
    st.stop()
features = pd.read_csv(FEATURES, parse_dates=["date"])
news_path = ROOT / "data" / "processed" / "news_clean.csv"
synthetic = False
if news_path.exists():
    sources = pd.read_csv(news_path)["source"].astype(str)
    synthetic = sources.eq("SYNTHETIC_DEMO").any()
if synthetic:
    st.error("SYNTHETIC DEMO DATA — not real market results.")
a, b, c = st.columns(3)
a.metric("Daily rows", len(features))
b.metric("Mean sentiment", f"{features.sentiment_mean.mean():.4f}")
c.metric("Event records", int(features.event_count.sum()))
st.subheader("News sentiment")
st.line_chart(features.set_index("date")[["sentiment_mean", "sentiment_7d_mean"]])
st.subheader("Economic events")
st.bar_chart(features.set_index("date")[["event_count", "high_impact_event_count"]])
if PREDICTIONS.exists():
    pred = pd.read_csv(PREDICTIONS, parse_dates=["date"])
    st.subheader("Walk-forward predictions")
    st.line_chart(pred.set_index("date")[["actual", "predicted"]])
    st.dataframe(pred.tail(20), use_container_width=True)
if REPORT.exists():
    st.subheader("Evaluation report")
    st.markdown(REPORT.read_text(encoding="utf-8"))
