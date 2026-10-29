from data import load_data
from features import (
    create_market_features,
    run_pca
)
from backtest import run_backtest
from evaluation import evaluate_results


def main():

    print("\n" + "=" * 65)
    print("REGX")
    print("Regime-Aware Portfolio Risk Analysis")
    print("=" * 65)

    # ========================================================
    # STEP 1 - DATA
    # ========================================================

    print("\n[1/5] Loading and cleaning data...")

    returns = load_data()

    # ========================================================
    # STEP 2 - MARKET FEATURES
    # ========================================================

    print("\n[2/5] Analysing market conditions...")

    features = create_market_features(
        returns
    )

    print(
        "Market features created:",
        features.shape[1]
    )

    # ========================================================
    # STEP 3 - PCA
    # ========================================================

    print("\n[3/5] Running PCA analysis...")

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

    print(
        "PC1 explained variance:",
        f"{explained_variance.iloc[0] * 100:.2f}%"
    )

    print(
        "First 5 PCs explained variance:",
        f"{cumulative_variance.iloc[-1] * 100:.2f}%"
    )

    # ========================================================
    # STEP 4 - BACKTEST
    # ========================================================

    print("\n[4/5] Running walk-forward backtest...")

    (
        results,
        turnover,
        adaptive_history
    ) = run_backtest(
        returns
    )

    # ========================================================
    # STEP 5 - EVALUATION
    # ========================================================

    print("\n[5/5] Evaluating strategies...")

    summary = evaluate_results(
        results,
        turnover,
        adaptive_history
    )

    print("\n" + "=" * 65)
    print("REGX COMPLETE")
    print("=" * 65)

    print(
        "\nFinal results saved in:"
        "\nresults/comparisons/"
    )

    print(
        "\nCharts saved in:"
        "\nfigures/performance/"
    )


if __name__ == "__main__":
    main()