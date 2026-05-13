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
        color="sector",
        size=summary["sharpe_ratio"].clip(lower=0),  # bubble size = Sharpe ratio (better risk-adjusted return → larger bubble)
        size_max=45,
        title="Risk vs. Return by Sector (2010–2020)",
        labels={
            "annualized_volatility": "Annualized Volatility (Risk)",
            "annualized_return": "Annualized Return",
            "sector": "Sector",
        },
        template="plotly_white",
    )
    # per-point label positions to avoid overlapping bubbles
    positions = {
        "Technology":               "top right",
        "Consumer Discretionary":   "bottom left",
        "Health Care":              "top left",
        "Industrials":              "bottom right",
        "Communication Services":   "top right",
        "Financials":               "top right",
        "Consumer Staples":         "top right",
        "Utilities":                "bottom left",
        "Materials":                "top left",
        "Real Estate":              "bottom left",
        "Energy":                   "bottom right",
    }
    fig.for_each_trace(
        lambda t: t.update(textposition=positions.get(t.name, "top center"))
    )
    fig.update_layout(
        height=620,
        margin=dict(t=100, b=40, l=120, r=40),
        yaxis=dict(range=[0, summary["annualized_return"].max() * 1.25]),
    )
    return fig


def plot_correlation_heatmap(returns_wide: pd.DataFrame) -> go.Figure:
    corr = returns_wide.corr()
    off_diag = corr.values[corr.values < 0.9999]
    fig = go.Figure(
        go.Heatmap(
            z=corr.values,
            x=corr.columns.tolist(),
            y=corr.index.tolist(),
            colorscale="Blues",
            zmin=round(off_diag.min(), 1),
            zmax=1,
            text=corr.round(2).values,
            texttemplate="%{text}",
            textfont={"size": 9},
        )
    )
    fig.update_layout(
        title="Sector Return Correlation Matrix (2010–2020)",
        template="plotly_white",
        xaxis=dict(tickangle=-45),
        margin=dict(t=80, b=140, l=160, r=40),
        width=720,
        height=620,
    )
    return fig


def plot_rolling_sharpe(rolling: pd.DataFrame) -> go.Figure:
    smoothed = rolling.rolling(21, center=True, min_periods=10).mean()
    melted = smoothed.reset_index().melt(id_vars="date", var_name="sector", value_name="sharpe")
    fig = px.line(
        melted.dropna(),
        x="date",
        y="sharpe",
        color="sector",
        title="Rolling Sharpe Ratio by Sector (252-day, 21-day smoothed)",
        labels={"sharpe": "Sharpe Ratio", "date": "Date", "sector": "Sector"},
        template="plotly_white",
    )
    fig.update_traces(line=dict(width=1.8))
    fig.add_hline(y=0, line_dash="dash", line_color="gray", opacity=0.5)
    fig.update_layout(height=520)
    return fig


def plot_efficient_frontier(ef_df: pd.DataFrame, summary: pd.DataFrame) -> go.Figure:
    min_vol = ef_df.loc[ef_df["volatility"].idxmin()]
    max_sharpe = ef_df.loc[ef_df["sharpe"].idxmax()]

    fig = go.Figure()
    fig.add_trace(go.Scatter(
        x=ef_df["volatility"], y=ef_df["return"],
        mode="markers",
        marker=dict(color=ef_df["sharpe"], colorscale="Viridis", size=3, opacity=0.4,
                    colorbar=dict(title="Sharpe", thickness=15, x=1.02)),
        name="Random Portfolios",
        showlegend=False,
        hovertemplate="Vol: %{x:.1%}<br>Return: %{y:.1%}<extra></extra>",
    ))
    for label, pt, color in [("Min Variance", min_vol, "royalblue"), ("Max Sharpe", max_sharpe, "crimson")]:
        fig.add_trace(go.Scatter(
            x=[pt["volatility"]], y=[pt["return"]],
            mode="markers+text",
            marker=dict(color=color, size=14, symbol="star"),
            text=[label], textposition="top right",
            name=label,
        ))
    fig.add_trace(go.Scatter(
        x=summary["annualized_volatility"], y=summary["annualized_return"],
        mode="markers+text",
        marker=dict(color="black", size=7),
        text=summary["sector"], textposition="top center",
        name="Individual Sectors",
    ))
    fig.update_layout(
        title="Efficient Frontier — S&P 500 Sectors (2010–2020)",
        xaxis=dict(title="Annualized Volatility", tickformat=".0%"),
        yaxis=dict(title="Annualized Return", tickformat=".0%"),
        template="plotly_white",
        height=580,
        legend=dict(
            x=0.01, y=0.01, xanchor="left", yanchor="bottom",
            bgcolor="rgba(255,255,255,0.85)", bordercolor="lightgray", borderwidth=1,
        ),
        margin=dict(r=100),
    )
    return fig


def plot_cumulative_returns(df: pd.DataFrame) -> go.Figure:
    wide = df.pivot_table(index="date", columns="sector", values="daily_return").sort_index()
    cumulative = (1 + wide).cumprod().resample("W").last()  # weekly to reduce noise
    melted = cumulative.reset_index().melt(id_vars="date", var_name="sector", value_name="value")
    fig = px.line(
        melted.dropna(),
        x="date", y="value", color="sector",
        title="Cumulative Returns by Sector (2010–2020, $1 invested)",
        labels={"value": "Portfolio Value ($)", "date": "Date", "sector": "Sector"},
        template="plotly_white",
    )
    fig.add_hline(y=1, line_dash="dash", line_color="gray", opacity=0.4)
    fig.update_layout(height=500)
    return fig


def plot_annual_returns_heatmap(df: pd.DataFrame) -> go.Figure:
    tmp = df.copy()
    tmp["year"] = pd.to_datetime(tmp["date"]).dt.year
    annual = (
        tmp.groupby(["sector", "year"])["daily_return"]
        .apply(lambda r: (1 + r).prod() - 1)
        .rename("annual_return")
        .reset_index()
    )
    wide = annual.pivot(index="sector", columns="year", values="annual_return")
    text = [[f"{v:.1%}" if pd.notna(v) else "" for v in row] for row in wide.values]
    fig = go.Figure(go.Heatmap(
        z=wide.values,
        x=[str(y) for y in wide.columns],
        y=wide.index.tolist(),
        colorscale="RdYlGn",
        zmid=0,
        text=text,
        texttemplate="%{text}",
        textfont={"size": 10},
        colorbar=dict(title="Annual Return", tickformat=".0%"),
    ))
    fig.update_layout(
        title="Annual Return by Sector and Year (2010–2020)",
        template="plotly_white",
        xaxis=dict(title="Year"),
        margin=dict(l=160, t=80),
        height=460,
    )
    return fig


def export_for_tableau(df: pd.DataFrame, filename: str = "sector_returns.csv") -> None:
    path = OUTPUT_DIR / "tableau" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(path, index=False)
    print(f"Exported to {path}")


def export_summary_for_tableau(summary: pd.DataFrame, filename: str = "sector_metrics.csv") -> None:
    path = OUTPUT_DIR / "tableau" / filename
    path.parent.mkdir(parents=True, exist_ok=True)
    summary.to_csv(path, index=False)
    print(f"Exported to {path}")
