import numpy as np
import pandas as pd

POS = [
    "economic activity improved as employment remained strong",
    "business confidence rose after stronger demand",
    "inflation eased and markets welcomed softer data",
    "growth outlook improved as consumer spending increased",
]
NEG = [
    "economic activity weakened as demand slowed",
    "inflation pressures increased and markets turned cautious",
    "employment growth slowed amid recession concerns",
    "business confidence fell after weaker manufacturing data",
]
NEU = [
    "officials are scheduled to discuss the economic outlook",
    "the report summarizes recent economic conditions",
    "analysts await the next release of economic indicators",
]

def make_demo_data(days=180, seed=17):
    """Synthetic records test the pipeline only; they are not market observations."""
    rng = np.random.default_rng(seed)
    dates = pd.date_range(end=pd.Timestamp.now(tz="UTC").normalize(), periods=days, freq="D")
    news_rows, event_rows = [], []
    event_names = ["CPI Release", "FOMC Announcement", "Employment Report", "Retail Sales"]
    for date in dates:
        for _ in range(int(rng.integers(1, 5))):
            bucket = int(rng.integers(0, 3))
            text = (POS if bucket == 0 else NEG if bucket == 1 else NEU)[int(rng.integers(0, len(POS if bucket < 2 else NEU)))]
            news_rows.append({
                "published_at": (date + pd.Timedelta(hours=int(rng.integers(8, 22)))).isoformat(),
                "title": text.title(), "content": text,
                "url": "https://example.invalid/synthetic-demo",
                "source": "SYNTHETIC_DEMO", "is_synthetic": True,
            })
        if rng.random() < 0.14:
            event_rows.append({
                "event_time": (date + pd.Timedelta(hours=13, minutes=30)).isoformat(),
                "event_name": event_names[int(rng.integers(0, len(event_names)))],
                "actual": float(rng.normal(2.5, 0.7)),
                "forecast": float(rng.normal(2.5, 0.7)),
                "importance": "medium", "source": "SYNTHETIC_DEMO", "is_synthetic": True,
            })
    return pd.DataFrame(news_rows), pd.DataFrame(event_rows)
