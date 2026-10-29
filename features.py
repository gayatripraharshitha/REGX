import numpy as np
import pandas as pd
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

# ============================================================
# AVERAGE CORRELATION
# ============================================================

def average_correlation(window):
    """
    Calculates the average correlation between all
    pairs of industries inside a historical window.
    """

    corr_matrix = window.corr()

    values = corr_matrix.values

    # Take only upper triangle
    # so we do not count the same pair twice
    upper_triangle = values[
        np.triu_indices_from(values, k=1)
    ]

    return np.mean(upper_triangle)


# ============================================================
# COVARIANCE INSTABILITY
# ============================================================

def covariance_instability(recent_window, long_window):
    """
    Measures how much the recent covariance structure
    differs from the longer-term covariance structure.
    """

    recent_cov = recent_window.cov().values

    long_cov = long_window.cov().values

    difference = recent_cov - long_cov

    # Frobenius norm measures overall matrix difference
    instability = np.linalg.norm(
        difference,
        ord="fro"
    )

    return instability


# ============================================================
# CREATE MARKET FEATURES
# ============================================================

def create_market_features(returns):
    """
    Creates market-state features from the
    30-industry return dataset.
    """

    features = pd.DataFrame(
        index=returns.index
    )

    # --------------------------------------------------------
    # 1. Market Return
    # --------------------------------------------------------
    # Simple equal-weight average return
    # across all 30 industries.

    market_return = returns.mean(axis=1)

    features["market_return"] = (
        market_return
    )

    # --------------------------------------------------------
    # 2. 20-Day Volatility
    # --------------------------------------------------------
    # Short-term market volatility.

    features["vol_20"] = (
        market_return
        .rolling(20)
        .std()
    )

    # --------------------------------------------------------
    # 3. 252-Day Volatility
    # --------------------------------------------------------
    # Approx. one trading year.

    features["vol_252"] = (
        market_return
        .rolling(252)
        .std()
    )

    # --------------------------------------------------------
    # 4. Volatility Shock
    # --------------------------------------------------------
    # Compares recent volatility with long-term volatility.
    #
    # > 1  → recent market is more volatile
    # < 1  → recent market is calmer

    features["volatility_shock"] = (
        features["vol_20"]
        /
        features["vol_252"]
    )

    # --------------------------------------------------------
    # 5. Volatility Change
    # --------------------------------------------------------
    # Measures whether short-term volatility
    # is rising or falling.

    features["volatility_change"] = (
        features["vol_20"]
        .pct_change(20)
    )

    # --------------------------------------------------------
    # 6. Average Correlation
    # --------------------------------------------------------
    # Measures how strongly the 30 industries
    # are moving together.

    avg_corr_values = []

    for i in range(len(returns)):

        # Need at least 60 trading days
        if i < 59:
            avg_corr_values.append(
                np.nan
            )
            continue

        recent_window = (
            returns.iloc[
                i - 59:i + 1
            ]
        )

        avg_corr = average_correlation(
            recent_window
        )

        avg_corr_values.append(
            avg_corr
        )

    features["avg_correlation"] = (
        avg_corr_values
    )

    # --------------------------------------------------------
    # 7. Correlation Shift
    # --------------------------------------------------------
    # Compares current correlation with its
    # longer-term average.

    correlation_baseline = (
        features["avg_correlation"]
        .rolling(252)
        .mean()
    )

    features["correlation_shift"] = (
        features["avg_correlation"]
        -
        correlation_baseline
    )

    # --------------------------------------------------------
    # 8. Covariance Instability
    # --------------------------------------------------------
    # Compare recent 60-day covariance
    # with longer 252-day covariance.

    instability_values = []

    for i in range(len(returns)):

        if i < 251:

            instability_values.append(
                np.nan
            )

            continue

        recent_window = (
            returns.iloc[
                i - 59:i + 1
            ]
        )

        long_window = (
            returns.iloc[
                i - 251:i + 1
            ]
        )

        instability = (
            covariance_instability(
                recent_window,
                long_window
            )
        )

        instability_values.append(
            instability
        )

    features[
        "covariance_instability"
    ] = instability_values

    # --------------------------------------------------------
    # 9. Remove invalid infinite values
    # --------------------------------------------------------

    features = features.replace(
        [np.inf, -np.inf],
        np.nan
    )

    return features

# ============================================================
# PCA ANALYSIS
# ============================================================

def run_pca(returns, n_components=5):
    """
    Performs PCA on the 30 industry returns.

    PCA is used to understand common movement
    across industries.

    It does NOT remove industries from the
    portfolio.
    """

    # --------------------------------------------------------
    # 1. Standardise industry returns
    # --------------------------------------------------------
    # Industries may have different volatility levels.
    # StandardScaler makes them comparable before PCA.

    scaler = StandardScaler()

    scaled_returns = scaler.fit_transform(
        returns
    )

    # --------------------------------------------------------
    # 2. Run PCA
    # --------------------------------------------------------

    pca = PCA(
        n_components=n_components
    )

    principal_components = pca.fit_transform(
        scaled_returns
    )

    # --------------------------------------------------------
    # 3. Create PCA DataFrame
    # --------------------------------------------------------

    component_names = [
        f"PC{i + 1}"
        for i in range(n_components)
    ]

    pca_data = pd.DataFrame(
        principal_components,
        index=returns.index,
        columns=component_names
    )

    # --------------------------------------------------------
    # 4. Explained variance
    # --------------------------------------------------------

    explained_variance = pd.Series(
        pca.explained_variance_ratio_,
        index=component_names,
        name="Explained Variance"
    )

    # --------------------------------------------------------
    # 5. Cumulative explained variance
    # --------------------------------------------------------

    cumulative_variance = (
        explained_variance.cumsum()
    )

    return (
        pca_data,
        explained_variance,
        cumulative_variance,
        pca,
        scaler
    )


# ============================================================
# K-MEANS MARKET REGIME CLUSTERING
# ============================================================

def run_clustering(
    features,
    pca_data,
    n_clusters=3
):
    """
    Groups historical market conditions using K-Means.

    Uses both market-state features and the first
    three PCA components.
    """

    # --------------------------------------------------------
    # 1. Select market-state features
    # --------------------------------------------------------

    cluster_data = features[
        [
            "volatility_shock",
            "volatility_change",
            "avg_correlation",
            "correlation_shift",
            "covariance_instability"
        ]
    ].copy()

    # --------------------------------------------------------
    # 2. Add first three PCA components
    # --------------------------------------------------------

    cluster_data["PC1"] = pca_data["PC1"]
    cluster_data["PC2"] = pca_data["PC2"]
    cluster_data["PC3"] = pca_data["PC3"]

    # --------------------------------------------------------
    # 3. Remove rows where rolling features
    #    are not yet available
    # --------------------------------------------------------

    cluster_data = cluster_data.dropna()

    # --------------------------------------------------------
    # 4. Standardise clustering inputs
    # --------------------------------------------------------
    # Prevent features with larger numerical scales
    # from dominating K-Means.

    scaler = StandardScaler()

    scaled_data = scaler.fit_transform(
        cluster_data
    )

    # --------------------------------------------------------
    # 5. Fit K-Means
    # --------------------------------------------------------

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    cluster_labels = model.fit_predict(
        scaled_data
    )

    # --------------------------------------------------------
    # 6. Attach cluster labels
    # --------------------------------------------------------

    cluster_data["cluster"] = (
        cluster_labels
    )

    return (
        cluster_data,
        model,
        scaler
    )


# ============================================================
# CLUSTER SUMMARY
# ============================================================

def summarize_clusters(cluster_data):
    """
    Shows the average characteristics of each
    discovered market cluster.
    """

    summary = (
        cluster_data
        .groupby("cluster")
        .mean()
    )

    counts = (
        cluster_data["cluster"]
        .value_counts()
        .sort_index()
    )

    return summary, counts
# ============================================================
# TEST FEATURES.PY DIRECTLY
# ============================================================

if __name__ == "__main__":

    from data import load_data

    returns = load_data()

    features = create_market_features(
        returns
    )

    print("\n")
    print("=" * 60)
    print("REGX MARKET FEATURES")
    print("=" * 60)

    print(
        "\nFeature columns:\n"
    )

    print(
        features.columns.tolist()
    )

    print(
        "\nLatest 5 observations:\n"
    )

    print(
        features.tail()
    )

    print(
        "\nMissing values per feature:\n"
    )

    print(
        features.isna().sum()
    )

    print(
        "\nFeature summary:\n"
    )

    print(
        features.describe().round(4)
    )

    # ========================================================
    # PCA ANALYSIS
    # ========================================================

    print("\n")
    print("=" * 60)
    print("REGX PCA ANALYSIS")
    print("=" * 60)

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

    print("\nExplained variance by component:\n")

    for component in explained_variance.index:

        variance = (
            explained_variance[component]
            * 100
        )

        print(
            f"{component}: "
            f"{variance:.2f}%"
        )

    print(
        "\nCumulative explained variance:\n"
    )

    for component in cumulative_variance.index:

        cumulative = (
            cumulative_variance[component]
            * 100
        )

        print(
            f"{component}: "
            f"{cumulative:.2f}%"
        )

    print(
        "\nFirst 5 PCA observations:\n"
    )

    print(
        pca_data.head()
    )

    # ========================================================
    # K-MEANS CLUSTERING
    # ========================================================

    print("\n")
    print("=" * 60)
    print("REGX MARKET REGIME CLUSTERING")
    print("=" * 60)

    (
        cluster_data,
        cluster_model,
        cluster_scaler
    ) = run_clustering(
        features,
        pca_data,
        n_clusters=3
    )

    (
        cluster_summary,
        cluster_counts
    ) = summarize_clusters(
        cluster_data
    )

    print("\nCluster counts:\n")

    print(
        cluster_counts
    )

    print(
        "\nAverage characteristics of each cluster:\n"
    )

    print(
        cluster_summary.round(4)
    )
