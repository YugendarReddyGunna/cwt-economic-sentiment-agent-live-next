import pandas as pd
from src.collect_news import COLUMNS, _normalize_records, audit_news_coverage, collect_exa_news

def test_normalization_parses_dates_deduplicates_and_keeps_real_source_flag():
    frame = _normalize_records([
        {"published_date":"2026-10-10T12:00:00Z","title":"CPI","url":"https://example.com/a","content":"Inflation"},
        {"published_date":"2026-10-10T12:00:00Z","title":"CPI duplicate","url":"https://example.com/a","content":"Duplicate"},
        {"title":"No date","url":"https://example.com/b"},
    ], "TAVILY")
    assert list(frame.columns) == COLUMNS
    assert len(frame) == 2
    assert str(frame.loc[0, "published_at"].tz) == "UTC"
    assert frame["is_synthetic"].eq(False).all()
    assert frame["published_at"].isna().sum() == 1

def test_audit_reports_missing_timestamps():
    frame = _normalize_records([
        {"published_date":"2026-10-10T12:00:00Z","url":"https://example.com/a"},
        {"url":"https://example.com/b"},
    ], "TAVILY")
    stats = audit_news_coverage(frame, days=180, as_of="2026-10-12T00:00:00Z")
    assert stats["rows"] == 2
    assert stats["missing_timestamp_rows"] == 1
    assert "not a complete historical archive" in stats["coverage_note"]

def test_exa_without_key_returns_empty_schema(monkeypatch):
    monkeypatch.delenv("EXA_API_KEY", raising=False)
    frame = collect_exa_news("macro news", days=30)
    assert list(frame.columns) == COLUMNS
    assert frame.empty
