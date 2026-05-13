import numpy as np
import pandas as pd
import pytest

from src.metrics import (
    TRADING_DAYS,
    annualized_return,
    annualized_volatility,
    max_drawdown,
    sector_summary,
    sharpe_ratio,
)


def test_annualized_return():
    r = pd.Series([0.001] * 10)
    assert annualized_return(r) == pytest.approx(0.001 * TRADING_DAYS)


def test_annualized_volatility():
    r = pd.Series([0.01, -0.01] * 5)
    assert annualized_volatility(r) == pytest.approx(r.std() * np.sqrt(TRADING_DAYS))


def test_sharpe_positive():
    r = pd.Series([0.005] * 100)
    assert sharpe_ratio(r) > 0


def test_sharpe_zero_volatility():
    r = pd.Series([0.0] * 10)
    assert np.isnan(sharpe_ratio(r))


def test_max_drawdown_negative():
    r = pd.Series([0.1, 0.1, -0.5, 0.1])
    assert max_drawdown(r) < 0


def test_max_drawdown_no_loss():
    r = pd.Series([0.01] * 20)
    assert max_drawdown(r) == pytest.approx(0.0, abs=1e-9)


def test_sector_summary_columns():
    df = pd.DataFrame({
        "sector": ["Tech"] * 50 + ["Energy"] * 50,
        "daily_return": [0.001] * 50 + [-0.001] * 50,
    })
    result = sector_summary(df)
    assert set(result.columns) == {
        "sector", "annualized_return", "annualized_volatility", "sharpe_ratio", "max_drawdown",
    }
    assert len(result) == 2


def test_sector_summary_sorted_by_sharpe():
    # alternating returns create variance; Tech has much higher mean → higher Sharpe
    tech = [0.01 if i % 2 == 0 else 0.00 for i in range(100)]
    energy = [0.002 if i % 2 == 0 else -0.001 for i in range(100)]
    df = pd.DataFrame({
        "sector": ["Tech"] * 100 + ["Energy"] * 100,
        "daily_return": tech + energy,
    })
    result = sector_summary(df)
    assert result.iloc[0]["sector"] == "Tech"
