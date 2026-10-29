import numpy as np
import pandas as pd

from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA
from sklearn.cluster import KMeans

from features import create_market_features

from covariance import (
    sample_covariance,
    ewma_covariance,
    ledoit_wolf_covariance,
    fixed_blend_covariance,
    adaptive_covariance,
    method_a_alpha,
    method_b_alpha
)

from portfolio import (
    equal_weight_portfolio,
    minimum_variance_portfolio
)


# ============================================================
# SETTINGS
# ============================================================

LOOKBACK = 252
MAX_WEIGHT = 0.10

# 0.10% cost per unit of turnover
TRANSACTION_COST = 0.001

# Start final historical simulation here
TEST_START = "2000-01-01"


# ============================================================
# TURNOVER
# ============================================================

def calculate_turnover(
    old_weights,
    new_weights
):

    return np.sum(
        np.abs(
            new_weights - old_weights
        )
    )


# ============================================================
# PREPARE METHOD B
# ============================================================

def prepare_method_b(
    returns,
    features,
    training_end="1999-12-31"
):
    """
    Fits PCA and K-Means using only
    pre-test historical observations.
    """

    train_returns = returns.loc[
        :training_end
    ]

    train_features = features.loc[
        :training_end
    ]

    # ----------------------------------------
    # PCA
    # ----------------------------------------

    pca_scaler = StandardScaler()

    scaled_returns = (
        pca_scaler.fit_transform(
            train_returns
        )
    )

    pca = PCA(
        n_components=3
    )

    train_pcs = pca.fit_transform(
        scaled_returns
    )

    pca_df = pd.DataFrame(
        train_pcs,
        index=train_returns.index,
        columns=[
            "PC1",
            "PC2",
            "PC3"
        ]
    )

    # ----------------------------------------
    # Clustering data
    # ----------------------------------------

    clustering_data = train_features[
        [
            "volatility_shock",
            "volatility_change",
            "avg_correlation",
            "correlation_shift",
            "covariance_instability"
        ]
    ].copy()

    clustering_data = (
        clustering_data.join(
            pca_df
        )
    )

    clustering_data = (
        clustering_data.dropna()
    )

    cluster_features = [
        "volatility_shock",
        "volatility_change",
        "avg_correlation",
        "correlation_shift",
        "covariance_instability",
        "PC1",
        "PC2",
        "PC3"
    ]

    cluster_scaler = (
        StandardScaler()
    )

    scaled_cluster_data = (
        cluster_scaler.fit_transform(
            clustering_data[
                cluster_features
            ]
        )
    )

    kmeans = KMeans(
        n_clusters=3,
        random_state=42,
        n_init=10
    )

    labels = kmeans.fit_predict(
        scaled_cluster_data
    )

    clustering_data[
        "cluster"
    ] = labels

    # ----------------------------------------
    # Determine regime severity
    # ----------------------------------------
    # Higher volatility shock +
    # higher correlation +
    # higher covariance instability
    # = more stressed regime.

    summary = (
        clustering_data
        .groupby("cluster")[
            [
                "volatility_shock",
                "avg_correlation",
                "covariance_instability"
            ]
        ]
        .mean()
    )

    # Standardise only for ranking clusters
    stress_summary = (
        summary - summary.mean()
    ) / summary.std()

    stress_score = (
        stress_summary.sum(axis=1)
    )

    ranked_clusters = (
        stress_score
        .sort_values()
        .index
        .tolist()
    )

    # Least stressed -> lowest EWMA weight
    alpha_map = {
        ranked_clusters[0]: 0.30,
        ranked_clusters[1]: 0.50,
        ranked_clusters[2]: 0.75
    }

    print(
        "\nMethod B Alpha Map:",
        alpha_map
    )

    return (
        pca_scaler,
        pca,
        cluster_scaler,
        kmeans,
        alpha_map,
        cluster_features
    )


# ============================================================
# RUN BACKTEST
# ============================================================

def run_backtest(returns):

    print("\nPreparing market features...")

    features = create_market_features(
        returns
    )

    (
        pca_scaler,
        pca,
        cluster_scaler,
        kmeans,
        alpha_map,
        cluster_features
    ) = prepare_method_b(
        returns,
        features
    )

    strategies = [
        "Equal Weight",
        "Sample",
        "EWMA",
        "Ledoit-Wolf",
        "Fixed Blend",
        "Method A",
        "Method B"
    ]

    all_returns = []

    turnover_records = []

    alpha_records = []

    previous_weights = {
        strategy: None
        for strategy in strategies
    }

    # ----------------------------------------
    # Monthly rebalance dates
    # ----------------------------------------

    test_returns = returns.loc[
        TEST_START:
    ]

    rebalance_dates = (
        test_returns
        .groupby(
            test_returns.index.to_period("M")
        )
        .tail(1)
        .index
    )

    print(
        "Backtest rebalances:",
        len(rebalance_dates)
    )

    # ----------------------------------------
    # Walk forward
    # ----------------------------------------

    for i, date in enumerate(
        rebalance_dates[:-1]
    ):

        history = returns.loc[
            :date
        ]

        if len(history) < LOOKBACK:
            continue

        window = history.iloc[
            -LOOKBACK:
        ]

        # ====================================
        # Covariance estimates
        # ====================================

        sample_cov = (
            sample_covariance(window)
        )

        ewma_cov = (
            ewma_covariance(window)
        )

        lw_cov = (
            ledoit_wolf_covariance(
                window
            )
        )

        fixed_cov = (
            fixed_blend_covariance(
                ewma_cov,
                lw_cov,
                alpha=0.50
            )
        )

        # ====================================
        # METHOD A
        # ====================================

        feature_rows = (
            features
            .loc[:date]
            .dropna()
        )

        if feature_rows.empty:
            continue

        latest_feature = (
            feature_rows.iloc[-1]
        )

        alpha_a = method_a_alpha(
            latest_feature
        )

        method_a_cov = (
            adaptive_covariance(
                ewma_cov,
                lw_cov,
                alpha_a
            )
        )

        # ====================================
        # METHOD B
        # ====================================

        latest_returns = (
            returns
            .loc[[date]]
        )

        scaled_latest_returns = (
            pca_scaler.transform(
                latest_returns
            )
        )

        pc_values = (
            pca.transform(
                scaled_latest_returns
            )[0]
        )

        cluster_row = pd.DataFrame(
            [{
                "volatility_shock":
                    latest_feature[
                        "volatility_shock"
                    ],

                "volatility_change":
                    latest_feature[
                        "volatility_change"
                    ],

                "avg_correlation":
                    latest_feature[
                        "avg_correlation"
                    ],

                "correlation_shift":
                    latest_feature[
                        "correlation_shift"
                    ],

                "covariance_instability":
                    latest_feature[
                        "covariance_instability"
                    ],

                "PC1": pc_values[0],

                "PC2": pc_values[1],

                "PC3": pc_values[2]
            }]
        )

        scaled_cluster = (
            cluster_scaler.transform(
                cluster_row[
                    cluster_features
                ]
            )
        )

        cluster = int(
            kmeans.predict(
                scaled_cluster
            )[0]
        )

        alpha_b = method_b_alpha(
            cluster,
            alpha_map
        )

        method_b_cov = (
            adaptive_covariance(
                ewma_cov,
                lw_cov,
                alpha_b
            )
        )

        # ====================================
        # PORTFOLIO WEIGHTS
        # ====================================

        covariance_models = {

            "Sample":
                sample_cov,

            "EWMA":
                ewma_cov,

            "Ledoit-Wolf":
                lw_cov,

            "Fixed Blend":
                fixed_cov,

            "Method A":
                method_a_cov,

            "Method B":
                method_b_cov
        }

        weights = {}

        weights[
            "Equal Weight"
        ] = equal_weight_portfolio(
            returns.shape[1]
        )

        for name, covariance in (
            covariance_models.items()
        ):

            weights[name] = (
                minimum_variance_portfolio(
                    covariance,
                    MAX_WEIGHT
                )
            )

        # ====================================
        # NEXT MONTH
        # ====================================

        next_date = (
            rebalance_dates[i + 1]
        )

        future_returns = (
            returns.loc[
                (returns.index > date)
                &
                (returns.index <= next_date)
            ]
        )

        if future_returns.empty:
            continue

        # ====================================
        # APPLY PORTFOLIOS
        # ====================================

        month_result = pd.DataFrame(
            index=future_returns.index
        )

        for strategy in strategies:

            w = weights[strategy]

            portfolio_return = (
                future_returns.values
                @ w
            )

            # ------------------------------
            # Transaction costs
            # ------------------------------

            if (
                previous_weights[
                    strategy
                ]
                is not None
            ):

                turnover = (
                    calculate_turnover(
                        previous_weights[
                            strategy
                        ],
                        w
                    )
                )

                cost = (
                    turnover
                    * TRANSACTION_COST
                )

                portfolio_return[
                    0
                ] -= cost

            else:

                turnover = 0

            turnover_records.append(
                {
                    "Date": date,
                    "Strategy":
                        strategy,
                    "Turnover":
                        turnover
                }
            )

            previous_weights[
                strategy
            ] = w.copy()

            month_result[
                strategy
            ] = portfolio_return

        all_returns.append(
            month_result
        )

        alpha_records.append(
            {
                "Date": date,
                "Alpha_A": alpha_a,
                "Alpha_B": alpha_b,
                "Cluster": cluster
            }
        )

        # Simple progress display
        if i % 50 == 0:

            print(
                f"Processed "
                f"{date.date()}"
            )

    # ========================================
    # COMBINE RESULTS
    # ========================================

    results = pd.concat(
        all_returns
    )

    turnover_df = pd.DataFrame(
        turnover_records
    )

    alpha_df = pd.DataFrame(
        alpha_records
    )

    # ========================================
    # SAVE
    # ========================================

    results.to_csv(
        "results/comparisons/"
        "backtest_returns.csv"
    )

    turnover_df.to_csv(
        "results/comparisons/"
        "turnover.csv",
        index=False
    )

    alpha_df.to_csv(
        "results/comparisons/"
        "adaptive_history.csv",
        index=False
    )

    print("\n" + "=" * 60)

    print(
        "REGX BACKTEST COMPLETE"
    )

    print("=" * 60)

    print(
        "Observations:",
        len(results)
    )

    print(
        "Start:",
        results.index.min()
    )

    print(
        "End:",
        results.index.max()
    )

    return (
        results,
        turnover_df,
        alpha_df
    )


# ============================================================
# TEST
# ============================================================

if __name__ == "__main__":

    from data import load_data

    returns = load_data()

    (
        results,
        turnover,
        adaptive_history
    ) = run_backtest(
        returns
    )

    print(
        "\nFirst Results:\n"
    )

    print(
        results.head()
    )

    print(
        "\nAdaptive History:\n"
    )

    print(
        adaptive_history.head()
    )
