-- S&P 500 Sector Analysis Schema

CREATE TABLE IF NOT EXISTS sector_prices (
    date        DATE NOT NULL,
    ticker      TEXT NOT NULL,
    sector      TEXT NOT NULL,
    open        REAL,
    high        REAL,
    low         REAL,
    close       REAL NOT NULL,
    volume      INTEGER,
    PRIMARY KEY (date, ticker)
);

-- df["daily_return"] = df.groupby("ticker")["close"].pct_change();
CREATE TABLE IF NOT EXISTS sector_returns (
    date            DATE NOT NULL,
    ticker          TEXT NOT NULL,
    sector          TEXT NOT NULL,
    daily_return    REAL,
    PRIMARY KEY (date, ticker)
);
