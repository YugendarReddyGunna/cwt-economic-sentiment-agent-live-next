# Macro Outlook

**Data period:** 2026-04-28 to 2026-10-12

## Executive Summary

The collected dataset contains 131 economic-calendar events
and 20 news-article observations.

The rule-based news sentiment score is classified as **Neutral or mixed**.
This is a descriptive indicator, not a validated market forecast or trading signal.

## Economic Calendar

- Total calendar events: 131
- High-impact events: 61
- Calendar source: Finance Calendar API

## News Sentiment

- Articles represented in daily features: 20
- Mean daily sentiment score: -0.0223

The sentiment method uses a simple keyword lexicon. It may miss context,
negation, and the difference between inflation concerns and positive economic
growth. Results should therefore be interpreted cautiously.

## Research Limitations

- The news sample contains only the articles actually collected; it is not
  a complete archive of all macroeconomic news.
- Missing actual, forecast, and prior values have not been fabricated.
- No verified strategy-return dataset has been supplied yet.
- Sharpe ratio, Sortino ratio, maximum drawdown, and predictive performance
  must not be claimed without suitable return data and out-of-sample testing.

## Next Research Steps

1. Expand and verify historical news coverage.
2. Validate event timestamps and economic-calendar values.
3. Join macro features to market outcomes without look-ahead leakage.
4. Run walk-forward validation using genuine historical returns.
