import numpy as np
from sklearn.covariance import LedoitWolf

# ============================================================
# 1. SAMPLE COVARIANCE
# ============================================================

def sample_covariance(window):
    """
    Standard historical covariance matrix.
    """

    return window.cov().values


# ============================================================
# 2. EWMA COVARIANCE
# ============================================================

def ewma_covariance(window, decay=0.94):
    """
    Gives more importance to recent observations.
    """

    data = window.values
    n = len(data)

    # Higher weight for recent observations
    weights = np.array([
        decay ** (n - 1 - i)
        for i in range(n)
    ])

    weights = weights / weights.sum()

    # Weighted mean
    mean = np.average(
        data,
        axis=0,
        weights=weights
    )

    centered = data - mean

    # Weighted covariance
    cov = np.zeros(
        (data.shape[1], data.shape[1])
    )

    for i in range(n):

        x = centered[i].reshape(-1, 1)

        cov += (
            weights[i]
            * (x @ x.T)
        )

    return cov


# ============================================================
# 3. LEDOIT-WOLF COVARIANCE
# ============================================================

def ledoit_wolf_covariance(window):
    """
    Shrinkage covariance estimator.
    Reduces noise in the sample covariance matrix.
    """

    model = LedoitWolf()

    model.fit(
        window.values
    )

    return model.covariance_


# ============================================================
# 4. FIXED BLEND
# ============================================================

def fixed_blend_covariance(
    ewma_cov,
    lw_cov,
    alpha=0.50
):
    """
    Simple fixed combination used as a benchmark.
    """

    return (
        alpha * ewma_cov
        +
        (1 - alpha) * lw_cov
    )


# ============================================================
# ADAPTIVE COVARIANCE
# ============================================================

def adaptive_covariance(
    ewma_cov,
    lw_cov,
    alpha
):
    """
    Combines EWMA and Ledoit-Wolf
    using an adaptive weight.
    """

    alpha = np.clip(
        alpha,
        0.10,
        0.80
    )

    return (
        alpha * ewma_cov
        +
        (1 - alpha) * lw_cov
    )


# ============================================================
# METHOD A
# DIRECT FEATURE-BASED ADAPTATION
# ============================================================

def method_a_alpha(feature_row):
    """
    Uses market features directly
    to determine alpha.
    """

    vol_shock = feature_row[
        "volatility_shock"
    ]

    corr_shift = feature_row[
        "correlation_shift"
    ]

    cov_instability = feature_row[
        "covariance_instability"
    ]

    # Simple starter score
    score = (
        0.40 * (vol_shock - 1)
        +
        0.30 * corr_shift
        +
        20 * cov_instability
    )

    alpha = 0.45 + score

    return float(
        np.clip(
            alpha,
            0.10,
            0.80
        )
    )


# ============================================================
# METHOD B
# CLUSTER-GUIDED ADAPTATION
# ============================================================

def method_b_alpha(cluster, alpha_map=None):
    """
    Returns alpha according to the market regime.

    alpha_map should be determined from the
    characteristics of the fitted clusters.
    """

    if alpha_map is None:
        alpha_map = {
            0: 0.75,
            1: 0.30,
            2: 0.50
        }

    return float(
        alpha_map[int(cluster)]
    )


# ============================================================
# 5. MATRIX VALIDATION
# ============================================================

def validate_covariance(cov):
    """
    Basic checks for a covariance matrix.
    """

    symmetric = np.allclose(
        cov,
        cov.T,
        atol=1e-10
    )

    diagonal_non_negative = (
        np.diag(cov) >= 0
    ).all()

    finite = np.isfinite(
        cov
    ).all()

    eigenvalues = np.linalg.eigvalsh(
        cov
    )

    positive_semidefinite = (
        eigenvalues.min() >= -1e-10
    )

    return {
        "shape": cov.shape,
        "symmetric": symmetric,
        "non_negative_variances":
            diagonal_non_negative,
        "finite_values":
            finite,
        "positive_semidefinite":
            positive_semidefinite,
        "minimum_eigenvalue":
            eigenvalues.min()
    }


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from data import load_data
    from features import (
    create_market_features,
    run_pca,
    run_clustering
)

    returns = load_data()

    # Use latest 252 trading days
    window = returns.iloc[-252:]

    print("\n" + "=" * 60)
    print("REGX COVARIANCE ESTIMATION")
    print("=" * 60)

    sample_cov = sample_covariance(
        window
    )

    ewma_cov = ewma_covariance(
        window
    )

    lw_cov = ledoit_wolf_covariance(
        window
    )

    fixed_cov = fixed_blend_covariance(
        ewma_cov,
        lw_cov
    )

    matrices = {
        "Sample": sample_cov,
        "EWMA": ewma_cov,
        "Ledoit-Wolf": lw_cov,
        "Fixed Blend": fixed_cov
    }

    for name, cov in matrices.items():

        print(f"\n{name}")

        validation = validate_covariance(
            cov
        )

        for key, value in validation.items():

            print(
                f"{key}: {value}"
            )

    print("\nAverage Variance:")

    for name, cov in matrices.items():

        avg_variance = (
            np.diag(cov).mean()
        )

        print(
            f"{name}: "
            f"{avg_variance:.8f}"
        )

    print("\nAverage Absolute Covariance:")

    for name, cov in matrices.items():

        n = cov.shape[0]

        mask = ~np.eye(
            n,
            dtype=bool
        )

        avg_covariance = (
            np.abs(cov[mask]).mean()
        )

        print(
            f"{name}: "
            f"{avg_covariance:.8f}"
        )
    # ========================================================
    # METHOD A + METHOD B TEST
    # ========================================================

    features = create_market_features(
        returns
    )

    (
        pca_data,
        explained_variance,
        cumulative_variance,
        pca_model,
        pca_scaler
    ) = run_pca(
        returns,
        n_components=5
    )

    (
        cluster_data,
        cluster_model,
        cluster_scaler
    ) = run_clustering(
        features,
        pca_data,
        n_clusters=3
    )

    # Latest available feature row
    latest_features = (
        features
        .dropna()
        .iloc[-1]
    )

    # Latest cluster
    latest_cluster = int(
        cluster_data
        .iloc[-1]["cluster"]
    )

    # Method A alpha
    alpha_a = method_a_alpha(
        latest_features
    )

    # Method B alpha
    alpha_b = method_b_alpha(
        latest_cluster
    )

    # Adaptive covariance matrices
    method_a_cov = adaptive_covariance(
        ewma_cov,
        lw_cov,
        alpha_a
    )

    method_b_cov = adaptive_covariance(
        ewma_cov,
        lw_cov,
        alpha_b
    )

    print("\n" + "=" * 60)
    print("REGX ADAPTIVE METHODS")
    print("=" * 60)

    print(
        "\nLatest Cluster:",
        latest_cluster
    )

    print(
        "Method A Alpha:",
        round(alpha_a, 4)
    )

    print(
        "Method B Alpha:",
        round(alpha_b, 4)
    )

    print("\nMethod A Validation:")

    print(
        validate_covariance(
            method_a_cov
        )
    )

    print("\nMethod B Validation:")

    print(
        validate_covariance(
            method_b_cov
        )
    )

    print("\nAverage Variance:")

    print(
        "Method A:",
        np.diag(
            method_a_cov
        ).mean()
    )

    print(
        "Method B:",
        np.diag(
            method_b_cov
        ).mean()
    )
