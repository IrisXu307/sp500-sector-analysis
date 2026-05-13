import yfinance as yf
import pandas as pd
import sqlalchemy as sa
from pathlib import Path

SECTOR_ETFS = {
    "XLB": "Materials",
    "XLC": "Communication Services",
    "XLE": "Energy",
    "XLF": "Financials",
    "XLI": "Industrials",
    "XLK": "Technology",
    "XLP": "Consumer Staples",
    "XLRE": "Real Estate",
    "XLU": "Utilities",
    "XLV": "Health Care",
    "XLY": "Consumer Discretionary",
}

DB_PATH = Path(__file__).parent.parent / "data" / "processed" / "sp500.db"


def download_prices(start: str = "2010-01-01", end: str = "2020-12-31") -> pd.DataFrame:
    tickers = list(SECTOR_ETFS.keys())
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True, threads=False)["Close"]
    raw = raw.stack().reset_index()
    raw.columns = ["date", "ticker", "close"]
    raw["sector"] = raw["ticker"].map(SECTOR_ETFS)
    raw["date"] = pd.to_datetime(raw["date"]).dt.date
    missing = set(tickers) - set(raw["ticker"].unique())
    if missing:
        print(f"Warning: missing data for {sorted(missing)} — consider re-running download")
    return raw


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    prices = prices.sort_values(["ticker", "date"])
    prices["daily_return"] = prices.groupby("ticker")["close"].pct_change()
    return prices.dropna(subset=["daily_return"])


def _engine():
    return sa.create_engine(f"sqlite:///{DB_PATH}", connect_args={"timeout": 30})


def save_to_db(prices: pd.DataFrame, returns: pd.DataFrame) -> None:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    engine = _engine()
    try:
        prices[["date", "ticker", "sector", "close"]].to_sql(
            "sector_prices", engine, if_exists="replace", index=False
        )
        returns[["date", "ticker", "sector", "daily_return"]].to_sql(
            "sector_returns", engine, if_exists="replace", index=False
        )
    finally:
        engine.dispose()
    print(f"Saved to {DB_PATH}")


def download_benchmark(start: str = "2010-01-01", end: str = "2020-12-31") -> pd.DataFrame:
    close = yf.download("SPY", start=start, end=end, auto_adjust=True, threads=False)["Close"]
    df = pd.DataFrame({"date": close.index, "close": close.values})
    df["date"] = pd.to_datetime(df["date"])
    df["daily_return"] = df["close"].pct_change()
    return df.dropna(subset=["daily_return"])


def load_returns() -> pd.DataFrame:
    engine = _engine()
    try:
        return pd.read_sql("SELECT * FROM sector_returns", engine, parse_dates=["date"])
    finally:
        engine.dispose()


if __name__ == "__main__":
    prices = download_prices()
    returns = compute_returns(prices)
    save_to_db(prices, returns)
