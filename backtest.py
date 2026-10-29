import numpy as np
import pandas as pd

from covariance import (
    sample_covariance,
    ewma_covariance,
    ledoit_wolf_covariance,
    adaptive_covariance,
    method_a_alpha
)

from portfolio import (
    minimum_variance_portfolio,
    equal_weight_portfolio
)

from features import create_market_features


LOOKBACK = 252

MAX_WEIGHT = 0.10

TRANSACTION_COST = 0.001


def calculate_turnover(
    old_weights,
    new_weights
):

    return np.sum(
        np.abs(
            new_weights - old_weights
        )
    )


def run_backtest(returns):

    features = create_market_features(
        returns
    )

    strategies = [
        "equal_weight",
        "sample",
        "ewma",
        "ledoit_wolf",
        "method_a"
    ]

    portfolio_returns = {
        name: []
        for name in strategies
    }

    dates = []

    # ------------------------------------------------
    # Monthly rebalance dates
    # ------------------------------------------------

    monthly_dates = (
        returns
        .resample("ME")
        .last()
        .index
    )

    previous_weights = {}

    for rebalance_date in monthly_dates:

        history = returns.loc[
            returns.index <= rebalance_date
        ]

        if len(history) < LOOKBACK:
            continue

        window = history.iloc[-LOOKBACK:]

        current_features = (
            features
            .loc[:rebalance_date]
            .dropna()
        )

        if len(current_features) == 0:
            continue

        feature_row = (
            current_features
            .iloc[-1]
            .to_dict()
        )

        # --------------------------------------------
        # Covariance estimates
        # --------------------------------------------

        sample_cov = sample_covariance(
            window
        )

        ewma_cov = ewma_covariance(
            window
        )

        lw_cov = ledoit_wolf_covariance(
            window
        )

        alpha_a = method_a_alpha(
            feature_row
        )

        method_a_cov = (
            adaptive_covariance(
                ewma_cov,
                lw_cov,
                alpha_a
            )
        )

        # --------------------------------------------
        # Portfolio weights
        # --------------------------------------------

        weights = {}

        weights["equal_weight"] = (
            equal_weight_portfolio(
                returns.shape[1]
            )
        )

        weights["sample"] = (
            minimum_variance_portfolio(
                sample_cov,
                MAX_WEIGHT
            )
        )

        weights["ewma"] = (
            minimum_variance_portfolio(
                ewma_cov,
                MAX_WEIGHT
            )
        )

        weights["ledoit_wolf"] = (
            minimum_variance_portfolio(
                lw_cov,
                MAX_WEIGHT
            )
        )

        weights["method_a"] = (
            minimum_variance_portfolio(
                method_a_cov,
                MAX_WEIGHT
            )
        )

        # --------------------------------------------
        # Find next month's returns
        # --------------------------------------------

        future = returns.loc[
            returns.index > rebalance_date
        ]

        if len(future) == 0:
            continue

        next_month = future[
            future.index.to_period("M")
            ==
            future.index[0].to_period("M")
        ]

        if len(next_month) == 0:
            continue

        # --------------------------------------------
        # Apply portfolio weights
        # --------------------------------------------

        for strategy in strategies:

            w = weights[strategy]

            daily_returns = (
                next_month.values @ w
            )

            # Transaction cost at rebalance
            if strategy in previous_weights:

                turnover = calculate_turnover(
                    previous_weights[strategy],
                    w
                )

                trading_cost = (
                    turnover
                    * TRANSACTION_COST
                )

                daily_returns[0] -= (
                    trading_cost
                )

            portfolio_returns[
                strategy
            ].extend(daily_returns)

            previous_weights[
                strategy
            ] = w.copy()

        dates.extend(
            next_month.index
        )

    results = pd.DataFrame(
        portfolio_returns
    )

    if len(dates) >= len(results):

        results.index = dates[
            :len(results)
        ]

    return results
