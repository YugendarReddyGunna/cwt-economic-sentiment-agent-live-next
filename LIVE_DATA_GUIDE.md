# Live data and evaluation setup

## Provider credentials
1. Copy `.env.example` to `.env`.
2. Add your own Tavily API key.
3. Optional: add an Exa API key.
4. For economic calendar events, add an Apify API token, actor ID, and JSON input accepted by that specific actor.
5. Never send tokens in chat, put them in screenshots, or commit `.env` to GitHub.

## Provider-specific configuration
Apify Actors have different input and output schemas. The normalizer checks common names such as `event_time`, `date`, `datetime`, `event_name`, `title`, `actual`, and `forecast`. Verify and adjust the mapping for your selected actor.

Tavily and Exa search results are not guaranteed to form a complete 180-day archive. Measure final dataset coverage and report gaps.

## Genuine trading data requirement
To run a real evaluation, place `data/raw/strategy_returns.csv` with columns `date`, `target_next_day`, and `strategy_return`. `date` should be UTC; `target_next_day` must be defined before training and aligned to the correct horizon; `strategy_return` must be a genuine decimal return (0.01 means +1%), ideally net of fees and slippage.

Do not generate these fields from synthetic data and describe them as actual performance. Document the instrument, strategy rules, return interval, source, fees, slippage, and execution assumptions. Verify that features for each date were available before the target return period begins.

## Validation checklist
- [ ] Inspect source URLs and publication timestamps.
- [ ] Verify data spans the required dates and report gaps.
- [ ] Deduplicate news and events.
- [ ] Check time zone and daylight-saving assumptions.
- [ ] Confirm actual and forecast values share units.
- [ ] Review target definition and feature/label alignment.
- [ ] Include costs/slippage and fixed strategy rules.
- [ ] Compare against a naive baseline.
- [ ] Report out-of-sample metrics, not training metrics.
