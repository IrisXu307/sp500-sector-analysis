# sp500-sector-analysis

S&P 500 sector analysis (2010–2020): risk-return profiling across 11 GICS sectors using Python, pandas, SQL, Plotly, and Tableau.

## Features

- **Data pipeline** — downloads adjusted close prices via yfinance, computes daily returns, stores in SQLite
- **Risk-return metrics** — annualized return, volatility, Sharpe ratio, max drawdown, beta and alpha vs SPY
- **7 interactive charts** — cumulative returns, annual heatmap, risk-return scatter, correlation matrix, rolling Sharpe, efficient frontier
- **Dash dashboard** — all charts in a tabbed web app (`python app.py`)
- **Jupyter notebook** — end-to-end narrative walkthrough with styled metrics table
- **Tableau exports** — daily returns and metrics summary as CSVs
- **SQL queries** — window functions, rolling averages, sector rankings
- **Test suite** — 12 pytest tests covering metrics and data loading

## Project Structure

```
sp500-sector-analysis/
├── src/
│   ├── data_loader.py      # download prices, compute returns, save/load from SQLite
│   ├── metrics.py          # Sharpe, drawdown, rolling Sharpe, efficient frontier, SPY benchmark
│   └── visualizations.py   # 9 Plotly chart functions + Tableau CSV export
├── sql/
│   ├── schema.sql
│   └── queries/
│       ├── sector_returns.sql    # annual return per sector
│       ├── risk_metrics.sql      # annualized volatility per sector
│       └── window_functions.sql  # LAG, RANK, rolling avg
├── notebooks/
│   └── analysis.ipynb      # end-to-end walkthrough with all charts
├── tests/
│   ├── test_metrics.py
│   └── test_data_loader.py
├── output/
│   ├── charts/             # saved HTML charts
│   └── tableau/            # CSV exports
├── app.py                  # Dash dashboard
├── main.py                 # CLI pipeline
└── requirements.txt
```

## Quickstart

```bash
pip install -r requirements.txt

# Full pipeline: download → metrics → charts → export
python main.py

# Or run individual steps
python main.py --download          # fetch data and populate SQLite
python main.py --metrics           # print metrics table
python main.py --charts            # save HTML charts to output/charts/
python main.py --export            # export CSVs for Tableau
python main.py --test              # run pytest suite
python main.py --dashboard         # launch interactive Dash app
```

## Metrics

| Metric | Description |
|--------|-------------|
| Annualized Return | Compounded daily return × 252 |
| Annualized Volatility | Std dev of daily return × √252 |
| Sharpe Ratio | Risk-adjusted return (risk-free rate = 2%) |
| Max Drawdown | Largest peak-to-trough decline |
| Beta | Sensitivity to SPY (S&P 500 benchmark) |
| Alpha | Excess return above CAPM expectation |
| Rolling Sharpe | Trailing 252-day Sharpe, 21-day smoothed |

## Charts

| Chart | Description |
|-------|-------------|
| Annualized Return | Horizontal bar chart ranked by return |
| Cumulative Returns | $1 invested in 2010, weekly resampled |
| Year-by-Year Heatmap | Annual compounded return per sector per year |
| Risk vs. Return | Scatter with bubble size = Sharpe ratio |
| Correlation Matrix | Pairwise sector return correlations |
| Rolling Sharpe | Sharpe ratio over time, smoothed |
| Efficient Frontier | 3,000 random portfolios + min-variance and max-Sharpe stars |

## Dashboard

```bash
python app.py
# open http://localhost:8050
```

Four tabs: Risk-Return Overview · Rolling Sharpe · Efficient Frontier · Correlation Matrix

## Data Source

11 GICS sector ETFs (XLB, XLC, XLE, XLF, XLI, XLK, XLP, XLRE, XLU, XLV, XLY) via `yfinance`.  
Note: XLC launched June 2018 and XLRE launched October 2015 — their charts begin from those dates.
