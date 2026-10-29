import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans


def average_correlation(window):

    corr = window.corr()

    values = corr.values

    upper_triangle = values[
        np.triu_indices_from(values, k=1)
    ]

    return np.mean(upper_triangle)


def create_market_features(returns):

    features = pd.DataFrame(index=returns.index)

    # ------------------------------------------------
    # Market volatility
    # ------------------------------------------------

    market_return = returns.mean(axis=1)

    features["vol_20"] = (
        market_return
        .rolling(20)
        .std()
    )

    features["vol_252"] = (
        market_return
        .rolling(252)
        .std()
    )

    # Volatility shock
    features["volatility_shock"] = (
        features["vol_20"]
        / features["vol_252"]
    )

    # Volatility acceleration
    features["volatility_change"] = (
        features["vol_20"]
        .pct_change(20)
    )

    # ------------------------------------------------
    # Average market correlation
    # ------------------------------------------------

    avg_corr = []

    for i in range(len(returns)):

        if i < 59:
            avg_corr.append(np.nan)
            continue

        window = returns.iloc[i-59:i+1]

        avg_corr.append(
            average_correlation(window)
        )

    features["avg_correlation"] = avg_corr

    features["correlation_shift"] = (
        features["avg_correlation"]
        - features["avg_correlation"].rolling(252).mean()
    )

    return features.replace(
        [np.inf, -np.inf],
        np.nan
    )


def run_pca(window, n_components=3):

    scaler = StandardScaler()

    scaled = scaler.fit_transform(window)

    pca = PCA(
        n_components=n_components
    )

    components = pca.fit_transform(scaled)

    return {
        "components": components,
        "explained_variance":
            pca.explained_variance_ratio_,
        "model": pca
    }


def cluster_market_states(feature_data, n_clusters=3):

    clean = feature_data.dropna().copy()

    scaler = StandardScaler()

    scaled = scaler.fit_transform(clean)

    model = KMeans(
        n_clusters=n_clusters,
        random_state=42,
        n_init=10
    )

    labels = model.fit_predict(scaled)

    result = clean.copy()

    result["cluster"] = labels

    return result, model, scaler
