import numpy as np

from scipy.optimize import minimize


def minimum_variance_portfolio(
    covariance,
    max_weight=0.10
):

    n_assets = covariance.shape[0]

    initial_weights = np.repeat(
        1 / n_assets,
        n_assets
    )

    def portfolio_variance(weights):

        return (
            weights.T
            @ covariance
            @ weights
        )

    constraints = [
        {
            "type": "eq",
            "fun": lambda w: np.sum(w) - 1
        }
    ]

    bounds = [
        (0, max_weight)
        for _ in range(n_assets)
    ]

    result = minimize(
        portfolio_variance,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints
    )

    if not result.success:

        print(
            "Warning: optimisation failed."
        )

        return initial_weights

    return result.x


def equal_weight_portfolio(n_assets):

    return np.repeat(
        1 / n_assets,
        n_assets
    )
