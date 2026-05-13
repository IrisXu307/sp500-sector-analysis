import pandas as pd
import pytest

from src.data_loader import compute_returns


def _make_prices(closes, ticker="XLK", sector="Technology"):
    return pd.DataFrame({
        "ticker": ticker,
        "date": pd.date_range("2020-01-01", periods=len(closes)),
        "close": list(map(float, closes)),
        "sector": sector,
    })


def test_compute_returns_length():
    prices = _make_prices([100, 105, 100])
    result = compute_returns(prices)
    assert len(result) == 2


def test_compute_returns_no_nans():
    prices = _make_prices([100, 101, 102, 103])
    result = compute_returns(prices)
    assert result["daily_return"].isna().sum() == 0


def test_compute_returns_value():
    prices = _make_prices([100.0, 110.0])
    result = compute_returns(prices)
    assert result.iloc[0]["daily_return"] == pytest.approx(0.10)


def test_compute_returns_multiple_tickers():
    df = pd.concat([
        _make_prices([100, 101, 102], ticker="XLK", sector="Technology"),
        _make_prices([50, 51, 52], ticker="XLE", sector="Energy"),
    ])
    result = compute_returns(df)
    assert set(result["ticker"].unique()) == {"XLK", "XLE"}
    assert len(result) == 4
