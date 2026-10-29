import os
import pandas as pd


RAW_FILE = "data/raw/industry_30_raw.csv"
CLEAN_FILE = "data/processed/industry_30_clean.csv"


def load_data():

    if not os.path.exists(RAW_FILE):
        raise FileNotFoundError(
            "\nDataset not found.\n"
            "Place the 30-industry daily returns file here:\n"
            "data/raw/industry_30_raw.csv"
        )

    df = pd.read_csv(RAW_FILE)

    # Detect date column
    date_col = df.columns[0]

    df[date_col] = pd.to_datetime(
        df[date_col],
        errors="coerce"
    )

    df = df.dropna(subset=[date_col])

    df = df.sort_values(date_col)

    df = df.drop_duplicates(subset=[date_col])

    df = df.set_index(date_col)

    # Convert remaining columns to numeric
    df = df.apply(pd.to_numeric, errors="coerce")

    # Replace common Kenneth French missing-value codes
    df = df.replace([-99.99, -999], pd.NA)

    # Remove rows containing missing values
    df = df.dropna()

    # Convert percentages to decimals when needed
    # Example: 1.5 becomes 0.015
    if df.abs().median().median() > 0.1:
        df = df / 100

    os.makedirs("data/processed", exist_ok=True)

    df.to_csv(CLEAN_FILE)

    return df
