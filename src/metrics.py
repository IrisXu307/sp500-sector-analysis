import numpy as np
import pandas as pd

TRADING_DAYS = 252
RISK_FREE_RATE = 0.02  # annual


def sharpe_ratio(returns: pd.Series) -> float:
    excess = returns.mean() * TRADING_DAYS - RISK_FREE_RATE
    vol = returns.std() * np.sqrt(TRADING_DAYS)
    return round(excess / vol, 4) if vol != 0 else np.nan


def max_drawdown(returns: pd.Series) -> float:
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    return round(drawdown.min(), 4)


def annualized_return(returns: pd.Series) -> float:
    return round(returns.mean() * TRADING_DAYS, 4)


def annualized_volatility(returns: pd.Series) -> float:
    return round(returns.std() * np.sqrt(TRADING_DAYS), 4)


def sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    """Compute risk-return metrics for each sector."""
    records = []
    for sector, group in df.groupby("sector"):
        r = group["daily_return"]
        records.append({
            "sector": sector,
            "annualized_return": annualized_return(r),
            "annualized_volatility": annualized_volatility(r),
            "sharpe_ratio": sharpe_ratio(r),
            "max_drawdown": max_drawdown(r),
        })
    return pd.DataFrame(records).sort_values("sharpe_ratio", ascending=False)
