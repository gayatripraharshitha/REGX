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

    initial_weights = np.repeat(
        1 / n_assets,
        n_assets
    )

    # Scale objective for numerical stability
    SCALE = 1_000_000

    def portfolio_variance(weights):

        variance = (
            weights.T
            @ covariance
            @ weights
        )

        return SCALE * variance

    constraints = {
        "type": "eq",
        "fun": lambda w: np.sum(w) - 1
    }

    bounds = [
        (0, max_weight)
        for _ in range(n_assets)
    ]

    result = minimize(
        portfolio_variance,
        initial_weights,
        method="SLSQP",
        bounds=bounds,
        constraints=constraints,
        options={
            "ftol": 1e-12,
            "maxiter": 1000
        }
    )

    if not result.success:

        raise RuntimeError(
            "Portfolio optimisation failed: "
            + result.message
        )

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