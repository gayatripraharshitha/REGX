import numpy as np
from scipy.optimize import minimize


# ============================================================
# EQUAL-WEIGHT PORTFOLIO
# ============================================================

def equal_weight_portfolio(n_assets):

    return np.repeat(
        1 / n_assets,
        n_assets
    )


# ============================================================
# MINIMUM-VARIANCE PORTFOLIO
# ============================================================

def minimum_variance_portfolio(
    covariance,
    max_weight=0.10
):
    """
    Long-only minimum-variance portfolio.

    Constraints:
    - weights sum to 1
    - no short selling
    - each asset <= max_weight
    """

    n_assets = covariance.shape[0]

    # Equal-weight feasible starting point
    initial_weights = np.repeat(
        1 / n_assets,
        n_assets
    )

    # Smaller scaling for numerical stability
    SCALE = 10_000

    scaled_covariance = (
        covariance * SCALE
    )

    # Objective
    def portfolio_variance(weights):

        return (
            weights.T
            @ scaled_covariance
            @ weights
        )

    # Gradient of w'Σw = 2Σw
    def gradient(weights):

        return (
            2
            * scaled_covariance
            @ weights
        )

    # Weights must sum to 1
    constraints = {
        "type": "eq",
        "fun": lambda w: np.sum(w) - 1,
        "jac": lambda w: np.ones(n_assets)
    }

    # Long-only + 10% maximum
    bounds = [
        (0.0, max_weight)
        for _ in range(n_assets)
    ]

    result = minimize(
        portfolio_variance,
        initial_weights,
        method="SLSQP",
        jac=gradient,
        bounds=bounds,
        constraints=constraints,
        options={
            "ftol": 1e-10,
            "maxiter": 2000,
            "disp": False
        }
    )

    if not result.success:

        print(
            "Warning:",
            result.message
        )

        # Safe fallback
        return initial_weights

    return result.x

# ============================================================
# PORTFOLIO RISK
# ============================================================

def portfolio_volatility(
    weights,
    covariance
):

    variance = (
        weights.T
        @ covariance
        @ weights
    )

    return np.sqrt(variance)


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from data import load_data

    from covariance import (
        sample_covariance,
        ewma_covariance,
        ledoit_wolf_covariance
    )

    returns = load_data()

    window = returns.iloc[-252:]

    matrices = {
        "Sample":
            sample_covariance(window),

        "EWMA":
            ewma_covariance(window),

        "Ledoit-Wolf":
            ledoit_wolf_covariance(window)
    }

    print("\n" + "=" * 60)
    print("REGX PORTFOLIO OPTIMISATION")
    print("=" * 60)

    for name, cov in matrices.items():

        weights = (
            minimum_variance_portfolio(
                cov
            )
        )

        risk = portfolio_volatility(
            weights,
            cov
        )

        print(f"\n{name}")

        print(
            "Weight Sum:",
            round(weights.sum(), 6)
        )

        print(
            "Minimum Weight:",
            round(weights.min(), 6)
        )

        print(
            "Maximum Weight:",
            round(weights.max(), 6)
        )

        print(
            "Portfolio Daily Volatility:",
            round(risk, 6)
        )
