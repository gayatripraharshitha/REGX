# RegX

RegX is a regime-aware portfolio risk analysis project.

The system analyses daily returns from 30 industry portfolios
and compares traditional covariance estimators with adaptive
risk-estimation methods.

## Core Methods

- Sample Covariance
- EWMA
- Ledoit-Wolf
- Method A: Direct Feature-Based Adaptation
- Method B: Clustering-Guided Adaptation
- PCA
- K-Means Clustering
- Minimum-Variance Portfolio Optimisation
- Walk-Forward Backtesting

## Python Files

1. main.py
2. data.py
3. features.py
4. covariance.py
5. portfolio.py
6. backtest.py
7. evaluation.py

## Run

Install dependencies:

pip install -r requirements.txt

Place the dataset at:

data/raw/industry_30_raw.csv

Then run:

python main.py
