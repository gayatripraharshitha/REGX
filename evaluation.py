import os
import numpy as np
import pandas as pd
import matplotlib.pyplot as plt


TRADING_DAYS = 252


def annualised_return(series):

    return (
        (1 + series).prod()
        ** (TRADING_DAYS / len(series))
        - 1
    )


def annualised_volatility(series):

    return (
        series.std()
        * np.sqrt(TRADING_DAYS)
    )


def sharpe_ratio(series):

    vol = annualised_volatility(
        series
    )

    if vol == 0:
        return np.nan

    return (
        annualised_return(series)
        / vol
    )


def maximum_drawdown(series):

    wealth = (
        1 + series
    ).cumprod()

    peak = wealth.cummax()

    drawdown = (
        wealth / peak
        - 1
    )

    return drawdown.min()


def evaluate_results(results):

    if results.empty:

        print(
            "\nNo backtest results available."
        )

        return

    summary = {}

    for column in results.columns:

        series = (
            results[column]
            .dropna()
        )

        summary[column] = {

            "Annual Return":
                annualised_return(series),

            "Annual Volatility":
                annualised_volatility(series),

            "Sharpe Ratio":
                sharpe_ratio(series),

            "Maximum Drawdown":
                maximum_drawdown(series)
        }

    summary_df = (
        pd.DataFrame(summary)
        .T
    )

    print("\n")
    print("=" * 60)
    print("REGX PERFORMANCE SUMMARY")
    print("=" * 60)

    print(summary_df.round(4))

    os.makedirs(
        "results/comparisons",
        exist_ok=True
    )

    summary_df.to_csv(
        "results/comparisons/performance_summary.csv"
    )

    # ------------------------------------------------
    # Equity curve
    # ------------------------------------------------

    equity = (
        1 + results
    ).cumprod()

    plt.figure(
        figsize=(11, 6)
    )

    for column in equity.columns:

        plt.plot(
            equity.index,
            equity[column],
            label=column
        )

    plt.title(
        "RegX Strategy Comparison"
    )

    plt.xlabel("Date")

    plt.ylabel(
        "Growth of $1"
    )

    plt.legend()

    plt.tight_layout()

    os.makedirs(
        "figures/performance",
        exist_ok=True
    )

    plt.savefig(
        "figures/performance/equity_curve.png"
    )

    plt.close()

    print(
        "\nResults saved to:"
    )

    print(
        "results/comparisons/performance_summary.csv"
    )

    print(
        "figures/performance/equity_curve.png"
    )
