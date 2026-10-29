"""Export the existing research pipeline as a static, Vercel-friendly snapshot."""
import json
from datetime import datetime, timezone
from pathlib import Path

import numpy as np
import pandas as pd

from data import load_data
from features import create_market_features, run_pca, run_clustering, summarize_clusters


def export_dashboard():
    project_dir = Path(__file__).resolve().parent
    returns = load_data()
    print("Computing market features, PCA and regimes...")
    features = create_market_features(returns)
    pca_data, explained, cumulative, _, _ = run_pca(returns, n_components=5)
    clusters, _, _ = run_clustering(features, pca_data, n_clusters=3)
    summary, counts = summarize_clusters(clusters)
    summary['vol_20'] = features[['vol_20']].join(clusters['cluster']).groupby('cluster')['vol_20'].mean()
    # Downsample only for rendering; all calculations above use the full daily dataset.
    frame = features.join(clusters['cluster']).resample('ME').last().dropna()
    frame['vol_20'] *= 100
    frame['vol_252'] *= 100
    series = [{"date": date.strftime('%Y-%m-%d'), **row.to_dict()}
              for date, row in frame.iterrows()]
    corr = returns.corr()
    # Monthly OHLC of a daily equal-weight industry return index, not stock prices.
    market_index = (1 + returns.iloc[-1260:].mean(axis=1)).cumprod() * 100
    monthly_index = market_index.resample('ME').ohlc().dropna()
    market_chart = [{'date': date.strftime('%Y-%m-%d'), **row.round(4).to_dict()}
                    for date, row in monthly_index.iterrows()]
    comparison_dir = project_dir / 'results' / 'comparisons'
    performance_file = comparison_dir / 'final_performance_summary.csv'
    backtest_file = comparison_dir / 'backtest_returns.csv'
    adaptive_file = comparison_dir / 'adaptive_history.csv'
    required_outputs = [performance_file, backtest_file, adaptive_file]
    if any(not path.is_file() for path in required_outputs):
        raise FileNotFoundError(
            'Backtest outputs are missing. Run python main.py before '
            'python export_dashboard.py.'
        )
    performance_frame = pd.read_csv(performance_file)
    backtest_frame = pd.read_csv(backtest_file, index_col=0, parse_dates=True)
    adaptive_frame = pd.read_csv(adaptive_file)
    performance = [{
        'strategy': row['Strategy'],
        'annualReturn': float(row['Annual Return']),
        'annualVolatility': float(row['Annual Volatility']),
        'sharpeRatio': float(row['Sharpe Ratio']),
        'maxDrawdown': float(row['Max Drawdown']),
        'averageTurnover': float(row['Average Turnover']),
        'costProxy': float(row['Cost Proxy']),
        'finalValue': float(row['Final Value']),
    } for _, row in performance_frame.iterrows()]
    payload = {
        'generatedAt': datetime.now(timezone.utc).isoformat(),
        'source': 'Kenneth French Data Library · 30 Industry Portfolios · Daily',
        'observations': len(returns), 'industries': list(returns.columns),
        'startDate': str(returns.index.min().date()),
        'endDate': str(returns.index.max().date()),
        'missing': int(returns.isna().sum().sum()),
        'duplicates': int(returns.index.duplicated().sum()),
        'warmupRows': len(returns) - len(clusters),
        'series': series,
        'marketChart': market_chart,
        'performance': performance,
        'backtest': {
            'observations': len(backtest_frame),
            'startDate': str(backtest_frame.index.min().date()),
            'endDate': str(backtest_frame.index.max().date()),
            'rebalances': len(adaptive_frame),
            'transactionCost': 0.001,
        },
        'pca': [{'name': name, 'variance': float(explained[name] * 100),
                 'cumulative': float(cumulative[name] * 100)} for name in explained.index],
        'clusters': [{'id': int(key), 'count': int(counts[key]),
                      'summary': summary.loc[key].to_dict()} for key in counts.index],
        'correlation': corr.round(4).values.tolist(),
        'scatter': [{'x': float(pca_data.loc[date, 'PC1']),
                     'y': float(pca_data.loc[date, 'PC2']),
                     'cluster': int(clusters.loc[date, 'cluster']),
                     'date': str(date.date())} for date in clusters.index[::20]],
    }
    target = project_dir / 'dashboard/public/data/dashboard.json'
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(payload, allow_nan=False, separators=(',', ':'),
                                 default=lambda v: v.item() if isinstance(v, np.generic) else v),
                      encoding='utf-8')
    print(f'Exported {len(series)} monthly chart points to {target}')
    print('PCA:', payload['pca'])
    print('Clusters:', {int(k): int(v) for k, v in counts.items()})


if __name__ == '__main__':
    export_dashboard()
