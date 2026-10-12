import numpy as np
import pandas as pd

def calculate_trading_metrics(returns, periods_per_year=252, risk_free_rate_annual=0.0):
    """Input periodic decimal returns, ideally net of fees/slippage."""
    r = pd.Series(returns, dtype="float64").replace([np.inf, -np.inf], np.nan).dropna()
    if r.empty:
        return {"observations": 0, "sharpe_ratio": np.nan, "sortino_ratio": np.nan, "max_drawdown": np.nan}
    excess = r - risk_free_rate_annual / periods_per_year
    std = excess.std(ddof=1)
    sharpe = float(np.sqrt(periods_per_year) * excess.mean() / std) if pd.notna(std) and std > 0 else np.nan
    downside = np.minimum(excess.to_numpy(), 0.0)
    downside_dev = float(np.sqrt(np.mean(np.square(downside))))
    sortino = float(np.sqrt(periods_per_year) * excess.mean() / downside_dev) if downside_dev > 0 else np.nan
    equity = (1 + r).cumprod()
    drawdown = equity / equity.cummax() - 1
    return {"observations": int(len(r)), "sharpe_ratio": sharpe, "sortino_ratio": sortino, "max_drawdown": float(drawdown.min())}
