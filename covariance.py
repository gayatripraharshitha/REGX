import numpy as np

from sklearn.covariance import LedoitWolf


# ============================================================
# BASIC COVARIANCE ESTIMATORS
# ============================================================

def sample_covariance(window):

    return window.cov().values


def ewma_covariance(window, decay=0.94):

    data = window.values

    n = len(data)

    weights = np.array([
        decay ** (n - 1 - i)
        for i in range(n)
    ])

    weights = weights / weights.sum()

    mean = np.average(
        data,
        axis=0,
        weights=weights
    )

    centered = data - mean

    cov = np.zeros(
        (data.shape[1], data.shape[1])
    )

    for i in range(n):

        x = centered[i].reshape(-1, 1)

        cov += weights[i] * (x @ x.T)

    return cov


def ledoit_wolf_covariance(window):

    model = LedoitWolf()

    model.fit(window.values)

    return model.covariance_


# ============================================================
# COVARIANCE BLENDING
# ============================================================

def adaptive_covariance(
    ewma_cov,
    lw_cov,
    alpha
):

    alpha = np.clip(alpha, 0.10, 0.80)

    return (
        alpha * ewma_cov
        +
        (1 - alpha) * lw_cov
    )


# ============================================================
# METHOD A
# DIRECT FEATURE-BASED ADAPTATION
# ============================================================

def method_a_alpha(features):

    """
    Starter adaptation rule.

    This is only the initial implementation.
    Final coefficients should be selected using
    training and validation data.
    """

    volatility_shock = features.get(
        "volatility_shock",
        1
    )

    correlation_shift = features.get(
        "correlation_shift",
        0
    )

    volatility_change = features.get(
        "volatility_change",
        0
    )

    score = (
        0.40 * (volatility_shock - 1)
        +
        0.30 * correlation_shift
        +
        0.30 * volatility_change
    )

    alpha = 0.45 + score

    return float(
        np.clip(alpha, 0.10, 0.80)
    )


# ============================================================
# METHOD B
# CLUSTERING-GUIDED ADAPTATION
# ============================================================

def method_b_alpha(cluster, cluster_alpha_map=None):

    if cluster_alpha_map is None:

        cluster_alpha_map = {
            0: 0.30,
            1: 0.50,
            2: 0.70
        }

    return cluster_alpha_map.get(
        int(cluster),
        0.50
    )
