import os
import numpy as np
import pandas as pd
import matplotlib

matplotlib.use("Agg")

import matplotlib.pyplot as plt


TRADING_DAYS = 252
TRANSACTION_COST = 0.001


# ============================================================
# PERFORMANCE METRICS
# ============================================================

def annualised_return(series):

    series = series.dropna()

    total_growth = (
        (1 + series).prod()
    )

    years = (
        len(series)
        / TRADING_DAYS
    )

    return (
        total_growth ** (1 / years)
        - 1
    )


def annualised_volatility(series):

    return (
        series.std()
        * np.sqrt(TRADING_DAYS)
    )


def sharpe_ratio(series):

    ann_return = (
        annualised_return(series)
    )

    ann_vol = (
        annualised_volatility(series)
    )

    if ann_vol == 0:
        return np.nan

    return (
        ann_return
        / ann_vol
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


# ============================================================
# MAIN EVALUATION
# ============================================================

def evaluate_results(
    results,
    turnover,
    adaptive_history
):

    print("\n" + "=" * 65)
    print("REGX FINAL PERFORMANCE EVALUATION")
    print("=" * 65)

    summary = []

    for strategy in results.columns:

        series = (
            results[strategy]
            .dropna()
        )

        strategy_turnover = (
            turnover[
                turnover["Strategy"]
                ==
                strategy
            ]["Turnover"]
        )

        avg_turnover = (
            strategy_turnover.mean()
        )

        total_cost_proxy = (
            strategy_turnover.sum()
            * TRANSACTION_COST
        )

        final_value = (
            (1 + series)
            .cumprod()
            .iloc[-1]
        )

        summary.append(
            {
                "Strategy":
                    strategy,

                "Annual Return":
                    annualised_return(
                        series
                    ),

                "Annual Volatility":
                    annualised_volatility(
                        series
                    ),

                "Sharpe Ratio":
                    sharpe_ratio(
                        series
                    ),

                "Max Drawdown":
                    maximum_drawdown(
                        series
                    ),

                "Average Turnover":
                    avg_turnover,

                "Cost Proxy":
                    total_cost_proxy,

                "Final Value":
                    final_value
            }
        )

    summary_df = pd.DataFrame(
        summary
    )

    summary_df = (
        summary_df
        .sort_values(
            "Sharpe Ratio",
            ascending=False
        )
    )

    print(
        "\nPerformance Summary:\n"
    )

    print(
        summary_df.round(4)
    )

    # ========================================================
    # SAVE TABLE
    # ========================================================

    os.makedirs(
        "results/comparisons",
        exist_ok=True
    )

    summary_df.to_csv(
        "results/comparisons/"
        "final_performance_summary.csv",
        index=False
    )

    # ========================================================
    # EQUITY CURVE
    # ========================================================

    equity = (
        1 + results
    ).cumprod()

    plt.figure(
        figsize=(12, 6)
    )

    for column in equity.columns:

        plt.plot(
            equity.index,
            equity[column],
            label=column
        )

    plt.title(
        "RegX Strategy Performance"
    )

    plt.xlabel(
        "Date"
    )

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
        "figures/performance/"
        "equity_curve.png"
    )

    plt.close()

    # ========================================================
    # DRAWDOWN CHART
    # ========================================================

    plt.figure(
        figsize=(12, 6)
    )

    for column in results.columns:

        wealth = (
            1 + results[column]
        ).cumprod()

        peak = wealth.cummax()

        drawdown = (
            wealth / peak
            - 1
        )

        plt.plot(
            drawdown.index,
            drawdown,
            label=column
        )

    plt.title(
        "RegX Portfolio Drawdowns"
    )

    plt.xlabel(
        "Date"
    )

    plt.ylabel(
        "Drawdown"
    )

    plt.legend()

    plt.tight_layout()

    plt.savefig(
        "figures/performance/"
        "drawdown.png"
    )

    plt.close()

    # ========================================================
    # ALPHA HISTORY
    # ========================================================

    if not adaptive_history.empty:

        adaptive_history[
            "Date"
        ] = pd.to_datetime(
            adaptive_history[
                "Date"
            ]
        )

        plt.figure(
            figsize=(12, 5)
        )

        plt.plot(
            adaptive_history["Date"],
            adaptive_history["Alpha_A"],
            label="Method A"
        )

        plt.plot(
            adaptive_history["Date"],
            adaptive_history["Alpha_B"],
            label="Method B"
        )

        plt.title(
            "Adaptive Alpha Through Time"
        )

        plt.xlabel(
            "Date"
        )

        plt.ylabel(
            "Alpha"
        )

        plt.legend()

        plt.tight_layout()

        plt.savefig(
            "figures/performance/"
            "adaptive_alpha.png"
        )

        plt.close()

    # ========================================================
    # CLUSTER COUNTS
    # ========================================================

    if (
        "Cluster"
        in adaptive_history.columns
    ):

        cluster_counts = (
            adaptive_history[
                "Cluster"
            ]
            .value_counts()
            .sort_index()
        )

        print(
            "\nDetected Regime Counts:\n"
        )

        print(
            cluster_counts
        )

    print(
        "\nSaved:"
    )

    print(
        "results/comparisons/"
        "final_performance_summary.csv"
    )

    print(
        "figures/performance/"
        "equity_curve.png"
    )

    print(
        "figures/performance/"
        "drawdown.png"
    )

    print(
        "figures/performance/"
        "adaptive_alpha.png"
    )

    return summary_df


# ============================================================
# RUN DIRECTLY
# ============================================================

if __name__ == "__main__":

    results = pd.read_csv(
        "results/comparisons/"
        "backtest_returns.csv",
        index_col=0,
        parse_dates=True
    )

    turnover = pd.read_csv(
        "results/comparisons/"
        "turnover.csv"
    )

    adaptive_history = pd.read_csv(
        "results/comparisons/"
        "adaptive_history.csv"
    )

    summary = evaluate_results(
        results,
        turnover,
        adaptive_history
    )
