import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from src.config import ARTIFACTS

def make_charts(features, predictions):
    paths = []
    if not features.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pd.to_datetime(features.date), features.sentiment_7d_mean, label="7-day mean sentiment")
        ax.axhline(0, linewidth=1)
        ax.set(title="Macroeconomic News Sentiment (Lexicon Baseline)", xlabel="Date (UTC)", ylabel="Score")
        ax.legend(); fig.tight_layout()
        p = ARTIFACTS / "sentiment_timeline.png"; fig.savefig(p, dpi=150); plt.close(fig); paths.append(str(p))
    if not predictions.empty:
        fig, ax = plt.subplots(figsize=(10, 4))
        ax.plot(pd.to_datetime(predictions.date), predictions.actual, label="Actual target")
        ax.plot(pd.to_datetime(predictions.date), predictions.predicted, label="Walk-forward prediction")
        ax.set(title="Out-of-Sample Walk-Forward Predictions", xlabel="Date (UTC)", ylabel="Target")
        ax.legend(); fig.tight_layout()
        p = ARTIFACTS / "walk_forward_predictions.png"; fig.savefig(p, dpi=150); plt.close(fig); paths.append(str(p))
    return paths
