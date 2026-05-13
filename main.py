"""
S&P 500 Sector Analysis Pipeline

Usage:
  python main.py                        # run full pipeline
  python main.py --download             # download data and save to DB only
  python main.py --metrics              # print metrics table (requires DB)
  python main.py --charts               # save HTML charts to output/ (requires DB)
  python main.py --export               # export Tableau CSV (requires DB)
  python main.py --test                 # run pytest test suite
  python main.py --dashboard            # launch interactive Dash dashboard
  python main.py --metrics --charts     # combine steps
"""

import argparse
from pathlib import Path

OUTPUT_DIR = Path("output") / "charts"


def run_download(args):
    from src.data_loader import download_prices, compute_returns, save_to_db
    print("Downloading sector ETF prices...")
    prices = download_prices(start=args.start, end=args.end)
    returns = compute_returns(prices)
    save_to_db(prices, returns)


def run_metrics(args):
    from src.data_loader import load_returns
    from src.metrics import sector_summary
    returns = load_returns()
    summary = sector_summary(returns)
    print("\nSector Risk-Return Summary")
    print("=" * 60)
    print(
        summary.to_string(
            index=False,
            formatters={
                "annualized_return": "{:.2%}".format,
                "annualized_volatility": "{:.2%}".format,
                "sharpe_ratio": "{:.3f}".format,
                "max_drawdown": "{:.2%}".format,
            },
        )
    )
    print()
    return summary


def run_charts(args, summary=None):
    from src.data_loader import load_returns
    from src.metrics import sector_summary
    from src.visualizations import (
        plot_sector_returns,
        plot_risk_return_scatter,
        plot_correlation_heatmap,
    )

    if summary is None:
        returns = load_returns()
        summary = sector_summary(returns)
    else:
        returns = load_returns()

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    charts = {
        "sector_returns.html": plot_sector_returns(summary),
        "risk_return_scatter.html": plot_risk_return_scatter(summary),
        "correlation_heatmap.html": plot_correlation_heatmap(
            returns.pivot_table(index="date", columns="sector", values="daily_return")
        ),
    }
    for filename, fig in charts.items():
        path = OUTPUT_DIR / filename
        fig.write_html(path)
        print(f"Saved chart: {path}")


def run_export(args):
    from src.data_loader import load_returns
    from src.visualizations import export_for_tableau
    returns = load_returns()
    export_for_tableau(returns)


def run_dashboard(args):
    import subprocess
    import sys
    subprocess.run([sys.executable, "app.py"])


def run_tests(args):
    import subprocess
    import sys
    result = subprocess.run(["pytest", "tests/", "-v"], check=False)
    sys.exit(result.returncode)


def main():
    parser = argparse.ArgumentParser(description="S&P 500 sector analysis pipeline")
    parser.add_argument("--download", action="store_true", help="Download data and save to DB")
    parser.add_argument("--metrics", action="store_true", help="Print sector metrics table")
    parser.add_argument("--charts", action="store_true", help="Generate and save HTML charts")
    parser.add_argument("--export", action="store_true", help="Export Tableau CSV")
    parser.add_argument("--dashboard", action="store_true", help="Launch interactive Dash dashboard")
    parser.add_argument("--test", action="store_true", help="Run pytest test suite")
    parser.add_argument("--start", default="2010-01-01", help="Start date (default: 2010-01-01)")
    parser.add_argument("--end", default="2020-12-31", help="End date (default: 2020-12-31)")
    args = parser.parse_args()

    if args.test:
        run_tests(args)
        return

    if args.dashboard:
        run_dashboard(args)
        return

    run_all = not any([args.download, args.metrics, args.charts, args.export])

    if run_all or args.download:
        run_download(args)

    summary = None
    if run_all or args.metrics:
        summary = run_metrics(args)

    if run_all or args.charts:
        run_charts(args, summary=summary)

    if run_all or args.export:
        run_export(args)


if __name__ == "__main__":
    main()
