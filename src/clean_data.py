import pandas as pd

NEWS_COLS = ["published_at", "title", "content", "url", "source", "is_synthetic"]
EVENT_COLS = ["event_time", "event_name", "actual", "forecast", "importance", "source", "is_synthetic"]

def clean_news(news):
    if news is None or news.empty:
        return pd.DataFrame(columns=NEWS_COLS)
    df = news.copy()
    for c in NEWS_COLS:
        if c not in df: df[c] = False if c == "is_synthetic" else ""
    df["published_at"] = pd.to_datetime(df["published_at"], errors="coerce", utc=True)
    for c in ["title", "content", "url", "source"]:
        df[c] = df[c].fillna("").astype(str).str.strip()
    df["is_synthetic"] = df["is_synthetic"].fillna(False).astype(bool)
    df = df.dropna(subset=["published_at"])
    df = df[(df.title != "") | (df.content != "")]
    return df.drop_duplicates(subset=["published_at", "title", "url"]).sort_values("published_at")[NEWS_COLS].reset_index(drop=True)

def clean_events(events):
    if events is None or events.empty:
        return pd.DataFrame(columns=EVENT_COLS + ["actual_minus_forecast"])
    df = events.copy()
    for c in EVENT_COLS:
        if c not in df: df[c] = False if c == "is_synthetic" else ""
    df["event_time"] = pd.to_datetime(df["event_time"], errors="coerce", utc=True)
    for c in ["actual", "forecast"]: df[c] = pd.to_numeric(df[c], errors="coerce")
    for c in ["event_name", "importance", "source"]:
        df[c] = df[c].fillna("").astype(str).str.strip()
    df["is_synthetic"] = df["is_synthetic"].fillna(False).astype(bool)
    df = df.dropna(subset=["event_time"])
    df = df[df.event_name != ""].drop_duplicates(subset=["event_time", "event_name"]).sort_values("event_time")
    df["actual_minus_forecast"] = df["actual"] - df["forecast"]
    return df.reset_index(drop=True)
