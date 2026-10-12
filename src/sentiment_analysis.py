import re

POSITIVE = {"improved", "strong", "stronger", "growth", "rose", "welcomed", "eased", "softer", "recovery", "positive", "beat", "surged", "resilient", "optimistic", "expansion"}
NEGATIVE = {"weakened", "weaker", "slowed", "slowdown", "inflation", "pressures", "cautious", "fell", "declined", "decline", "recession", "negative", "missed", "contraction", "risk", "risks", "uncertainty"}

def score_sentiment(text):
    """Transparent toy lexicon; not a validated financial sentiment model."""
    tokens = re.findall(r"[a-zA-Z]+", (text or "").lower())
    if not tokens: return 0.0
    return float((sum(t in POSITIVE for t in tokens) - sum(t in NEGATIVE for t in tokens)) / len(tokens))

def add_sentiment(news):
    df = news.copy()
    df["text_for_sentiment"] = (df["title"].fillna("").astype(str) + ". " + df["content"].fillna("").astype(str)).str.strip()
    df["sentiment"] = df["text_for_sentiment"].map(score_sentiment)
    return df
