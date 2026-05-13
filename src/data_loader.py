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
    raw = yf.download(tickers, start=start, end=end, auto_adjust=True)["Close"]
    raw = raw.stack().reset_index()
    raw.columns = ["date", "ticker", "close"]
    raw["sector"] = raw["ticker"].map(SECTOR_ETFS)
    raw["date"] = pd.to_datetime(raw["date"]).dt.date
    return raw


def compute_returns(prices: pd.DataFrame) -> pd.DataFrame:
    prices = prices.sort_values(["ticker", "date"])
    prices["daily_return"] = prices.groupby("ticker")["close"].pct_change()
    return prices.dropna(subset=["daily_return"])


def save_to_db(prices: pd.DataFrame, returns: pd.DataFrame) -> None:
    engine = sa.create_engine(f"sqlite:///{DB_PATH}")
    prices[["date", "ticker", "sector", "close"]].rename(
        columns={"close": "close"}
    ).to_sql("sector_prices", engine, if_exists="replace", index=False)
    returns[["date", "ticker", "sector", "daily_return"]].to_sql(
        "sector_returns", engine, if_exists="replace", index=False
    )
    print(f"Saved to {DB_PATH}")


def load_returns() -> pd.DataFrame:
    engine = sa.create_engine(f"sqlite:///{DB_PATH}")
    return pd.read_sql("SELECT * FROM sector_returns", engine, parse_dates=["date"])


if __name__ == "__main__":
    prices = download_prices()
    returns = compute_returns(prices)
    save_to_db(prices, returns)
