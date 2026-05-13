import numpy as np
import pandas as pd

TRADING_DAYS = 252
RISK_FREE_RATE = 0.02  # annual


def sharpe_ratio(returns: pd.Series) -> float:
    excess = returns.mean() * TRADING_DAYS - RISK_FREE_RATE
    vol = returns.std() * np.sqrt(TRADING_DAYS)
    return excess / vol if vol != 0 else np.nan


def max_drawdown(returns: pd.Series) -> float:
    cumulative = (1 + returns).cumprod()
    rolling_max = cumulative.cummax()
    drawdown = (cumulative - rolling_max) / rolling_max
    return drawdown.min()


def annualized_return(returns: pd.Series) -> float:
    return returns.mean() * TRADING_DAYS


def annualized_volatility(returns: pd.Series) -> float:
    return returns.std() * np.sqrt(TRADING_DAYS)


def sector_summary(df: pd.DataFrame) -> pd.DataFrame:
    grouped = df.groupby("sector")["daily_return"]
    summary = pd.DataFrame({
        "annualized_return": grouped.mean() * TRADING_DAYS,
        "annualized_volatility": grouped.std() * np.sqrt(TRADING_DAYS),
        "max_drawdown": grouped.apply(max_drawdown),
    })
    vol = summary["annualized_volatility"]
    summary["sharpe_ratio"] = (summary["annualized_return"] - RISK_FREE_RATE) / vol.where(vol != 0)
    return summary.reset_index().sort_values("sharpe_ratio", ascending=False)
