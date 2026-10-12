import pandas as pd
from src.clean_data import clean_news, clean_events
from src.feature_engineering import build_daily_features
from src.sentiment_analysis import score_sentiment
from src.trading_metrics import calculate_trading_metrics

def test_sentiment_direction():
    assert score_sentiment("growth improved") > 0
    assert score_sentiment("recession risks increased") < 0
    assert score_sentiment("") == 0

def test_clean_news_drops_bad_timestamp():
    raw = pd.DataFrame([
        {"published_at": "2026-01-01T12:00:00Z", "title": "Growth improved", "content": "Good", "url": "x", "source": "test"},
        {"published_at": "bad-date", "title": "bad row", "content": "x", "url": "y", "source": "test"},
    ])
    result = clean_news(raw)
    assert len(result) == 1
    assert str(result.iloc[0]["published_at"].tz) == "UTC"

def test_features_include_event_surprise():
    news = clean_news(pd.DataFrame([{"published_at":"2026-01-01T12:00:00Z","title":"Growth improved","content":"Strong","url":"x","source":"test","is_synthetic":False}]))
    events = clean_events(pd.DataFrame([{"event_time":"2026-01-01T13:30:00Z","event_name":"CPI","actual":3.0,"forecast":2.5,"importance":"high","source":"test","is_synthetic":False}]))
    features = build_daily_features(news, events)
    assert len(features) == 1
    assert features.iloc[0]["event_count"] == 1
    assert features.iloc[0]["event_surprise_mean"] == 0.5

def test_metrics_return_required_fields():
    result = calculate_trading_metrics([0.01, -0.02, 0.015, -0.005])
    assert result["observations"] == 4
    assert result["max_drawdown"] <= 0

def test_returns_validator_rejects_duplicate_dates():
    import pytest
    from src.data_quality import validate_returns_frame
    frame = pd.DataFrame({"date": ["2026-01-01", "2026-01-01"],
                          "target_next_day": [0.01, 0.02], "strategy_return": [0.01, -0.01]})
    with pytest.raises(ValueError, match="one row per UTC date"):
        validate_returns_frame(frame)

def test_coverage_reports_missing_calendar_days():
    from src.data_quality import summarize_coverage
    news = pd.DataFrame({"published_at": pd.to_datetime(["2026-01-01T00:00:00Z", "2026-01-03T00:00:00Z"])})
    events = pd.DataFrame({"event_time": pd.to_datetime([], utc=True)})
    features = pd.DataFrame({"date": pd.to_datetime(["2026-01-01T00:00:00Z", "2026-01-03T00:00:00Z"])})
    report = summarize_coverage(news, events, features)
    assert report["daily_features"]["missing_calendar_days"] == 1
