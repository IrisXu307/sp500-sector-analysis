# sp500-sector-analysis

S&P 500 sector analysis (2010–2020): risk-return profiling across 11 GICS sectors using Python, pandas, SQL, Plotly, and Tableau.

## Project Structure

```
sp500-sector-analysis/
├── data/
│   ├── raw/                  # original downloaded data
│   └── processed/            # SQLite database
├── src/
│   ├── data_loader.py        # download prices, compute returns, save to DB
│   ├── metrics.py            # Sharpe ratio, max drawdown, volatility
│   └── visualizations.py    # Plotly charts + Tableau CSV export
├── sql/
│   ├── schema.sql            # table definitions
│   └── queries/
│       ├── sector_returns.sql    # annual return per sector
│       ├── risk_metrics.sql      # annualized volatility per sector
│       └── window_functions.sql  # LAG, RANK, rolling avg
├── notebooks/
│   └── analysis.ipynb        # end-to-end walkthrough
├── output/
│   └── tableau/              # CSV exports for Tableau dashboards
└── requirements.txt
```

## Metrics Computed

| Metric | Description |
|--------|-------------|
| Annualized Return | Mean daily return × 252 |
| Annualized Volatility | Std dev of daily return × √252 |
| Sharpe Ratio | Risk-adjusted return (risk-free rate = 2%) |
| Max Drawdown | Largest peak-to-trough decline |

## Quickstart

```bash
pip install -r requirements.txt

# Download data and populate SQLite DB
python src/data_loader.py
```

## Data Source

Sector ETFs (XLB, XLC, XLE, XLF, XLI, XLK, XLP, XLRE, XLU, XLV, XLY) via `yfinance`.
