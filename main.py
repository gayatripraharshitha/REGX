from data import load_data
from features import create_market_features
from backtest import run_backtest
from evaluation import evaluate_results


def main():

    print("=" * 60)
    print("RegX - Regime-Aware Portfolio Risk System")
    print("=" * 60)

    # Step 1: Load and clean data
    returns = load_data()

    print("\nDataset loaded successfully.")
    print("Shape:", returns.shape)

    # Step 2: Market analysis
    features = create_market_features(returns)

    print("\nMarket features generated.")
    print(features.tail())

    # Step 3: Run complete backtest
    results = run_backtest(returns)

    # Step 4: Evaluate results
    evaluate_results(results)

    print("\nRegX experiment completed.")


if __name__ == "__main__":
    main()
