"""
Interactive Dash dashboard for S&P 500 sector analysis.

Run:
    python app.py
    python main.py --dashboard
"""

import sys
from dash import Dash, dcc, html

from src.data_loader import load_returns, download_benchmark
from src.metrics import sector_summary, add_benchmark_metrics, rolling_sharpe, efficient_frontier
from src.visualizations import (
    plot_sector_returns,
    plot_risk_return_scatter,
    plot_correlation_heatmap,
    plot_rolling_sharpe,
    plot_efficient_frontier,
)

print("Loading data...")
try:
    returns = load_returns()
except Exception:
    print("Database not found. Run 'python main.py --download' first.")
    sys.exit(1)

print("Computing metrics...")
summary = sector_summary(returns)
returns_wide = returns.pivot_table(index="date", columns="sector", values="daily_return")

print("Downloading SPY benchmark...")
try:
    benchmark = download_benchmark()
    summary = add_benchmark_metrics(summary, returns, benchmark)
    has_benchmark = True
except Exception:
    has_benchmark = False
    print("Could not download SPY — benchmark metrics skipped.")

print("Computing rolling Sharpe ratios...")
rolling = rolling_sharpe(returns)

print("Computing efficient frontier (3,000 portfolios)...")
ef_df = efficient_frontier(returns)

app = Dash(__name__, title="S&P 500 Sector Analysis")

_tab_style = {"padding": "12px 20px"}
_selected_style = {"padding": "12px 20px", "borderTop": "3px solid #2c3e50", "fontWeight": "bold"}

app.layout = html.Div(
    style={"fontFamily": "Arial, sans-serif", "maxWidth": "1200px", "margin": "0 auto", "padding": "24px"},
    children=[
        html.H1(
            "S&P 500 Sector Analysis (2010–2020)",
            style={"textAlign": "center", "color": "#2c3e50", "marginBottom": "4px"},
        ),
        html.P(
            "Risk-return profiling of 11 GICS sectors using daily ETF prices.",
            style={"textAlign": "center", "color": "#7f8c8d", "marginBottom": "24px"},
        ),
        dcc.Tabs(
            children=[
                dcc.Tab(label="Risk-Return Overview", style=_tab_style, selected_style=_selected_style, children=[
                    dcc.Graph(figure=plot_sector_returns(summary)),
                    dcc.Graph(figure=plot_risk_return_scatter(summary)),
                ]),
                dcc.Tab(label="Rolling Sharpe Ratio", style=_tab_style, selected_style=_selected_style, children=[
                    dcc.Graph(figure=plot_rolling_sharpe(rolling)),
                ]),
                dcc.Tab(label="Efficient Frontier", style=_tab_style, selected_style=_selected_style, children=[
                    dcc.Graph(figure=plot_efficient_frontier(ef_df, summary)),
                ]),
                dcc.Tab(label="Correlation Matrix", style=_tab_style, selected_style=_selected_style, children=[
                    dcc.Graph(figure=plot_correlation_heatmap(returns_wide)),
                ]),
            ],
        ),
    ],
)

if __name__ == "__main__":
    app.run(debug=False)
