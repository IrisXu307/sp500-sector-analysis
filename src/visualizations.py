import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path

OUTPUT_DIR = Path(__file__).parent.parent / "output"


def plot_sector_returns(summary: pd.DataFrame) -> go.Figure:
    fig = px.bar(
        summary.sort_values("annualized_return"),
        x="annualized_return",
        y="sector",
        orientation="h",
        title="Annualized Return by Sector (2010–2020)",
        labels={"annualized_return": "Annualized Return", "sector": "Sector"},
        color="annualized_return",
        color_continuous_scale="RdYlGn",
    )
    return fig


def plot_risk_return_scatter(summary: pd.DataFrame) -> go.Figure:
    fig = px.scatter(
        summary,
        x="annualized_volatility",
        y="annualized_return",
        text="sector",
        size=summary["sharpe_ratio"].clip(lower=0),
        title="Risk vs. Return by Sector (2010–2020)",
        labels={
            "annualized_volatility": "Annualized Volatility (Risk)",
            "annualized_return": "Annualized Return",
        },
    )
    fig.update_traces(textposition="top center")
    return fig


def plot_correlation_heatmap(returns_wide: pd.DataFrame) -> go.Figure:
    corr = returns_wide.corr()
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="RdBu",
            zmin=-1,
            zmax=1,
        )
    )
    fig.update_layout(title="Sector Return Correlation Matrix (2010–2020)")
    return fig


def export_for_tableau(df: pd.DataFrame, filename: str = "sector_returns.csv") -> None:
    path = OUTPUT_DIR / "tableau" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Exported to {path}")
