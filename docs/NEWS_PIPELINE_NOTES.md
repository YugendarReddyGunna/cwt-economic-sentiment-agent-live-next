# News pipeline notes

The Tavily adapter now normalizes publication dates to UTC, deduplicates by URL, and retains missing timestamps as `NaT` so they can be audited. `audit_news_coverage()` produces explicit coverage diagnostics.

Important: Tavily Search is a search/discovery API, not a guaranteed complete archive of every news item across all 180 days. Do not infer no-news days from absent results. Check result timestamps, source URLs, and coverage before joining to model features. API authentication is not tested without a private key. Keep `.env` out of source control.
