from pathlib import Path
import pandas as pd


PROJECT_DIR = Path(__file__).resolve().parent
RAW_FILE = PROJECT_DIR / "data" / "raw" / "30_Industry_Portfolios_Daily.csv"
CLEAN_FILE = PROJECT_DIR / "data" / "processed" / "industry_30_clean.csv"


def load_data():
    """
    Loads and cleans the Kenneth French
    30 Industry Portfolios daily return dataset.

    Returns
    -------
    pd.DataFrame
        Clean daily returns in decimal form.
        Example:
            1.25% -> 0.0125
    """

    # --------------------------------------------------
    # 1. Check whether dataset exists
    # --------------------------------------------------

    if not RAW_FILE.is_file():
        raise FileNotFoundError(
            "\nDataset not found.\n"
            "Place the raw 30-industry CSV file here:\n"
            f"{RAW_FILE}"
        )

    print("Loading raw dataset...")

    # --------------------------------------------------
    # 2. Find the actual data section
    # --------------------------------------------------
    # Kenneth French CSV files may contain text lines
    # before the real table starts.
    # We search for the row whose first value looks
    # like an 8-digit daily date: YYYYMMDD.
    # --------------------------------------------------

    with open(RAW_FILE, "r", encoding="utf-8-sig") as file:
        lines = file.readlines()

    header_index = None

    for i, line in enumerate(lines):
        parts = line.strip().split(",")

        if len(parts) < 2:
            continue

        first_value = parts[0].strip()

        # Header is normally immediately before first YYYYMMDD row
        if first_value.isdigit() and len(first_value) == 8:
            header_index = i - 1
            break

    if header_index is None:
        raise ValueError(
            "Could not locate the daily return table "
            "inside the raw dataset."
        )

    # --------------------------------------------------
    # 3. Read only the actual data section
    # --------------------------------------------------

    df = pd.read_csv(
        RAW_FILE,
        skiprows=header_index,
        low_memory=False
    )

    # Remove completely empty columns
    df = df.dropna(axis=1, how="all")

    # --------------------------------------------------
    # 4. Rename first column as Date
    # --------------------------------------------------

    df = df.rename(
        columns={
            df.columns[0]: "Date"
        }
    )

    # --------------------------------------------------
    # 5. Keep only valid daily rows
    # --------------------------------------------------

    df["Date"] = (
        df["Date"]
        .astype(str)
        .str.strip()
    )

    valid_dates = (
        df["Date"]
        .str.match(r"^\d{8}$")
    )

    df = df[valid_dates].copy()

    # --------------------------------------------------
    # 6. Convert YYYYMMDD into datetime
    # --------------------------------------------------

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="%Y%m%d",
        errors="coerce"
    )

    df = df.dropna(
        subset=["Date"]
    )

    # --------------------------------------------------
    # 7. Clean column names
    # --------------------------------------------------

    df.columns = [
        str(column).strip()
        for column in df.columns
    ]

    # --------------------------------------------------
    # 8. Convert return columns to numeric
    # --------------------------------------------------

    return_columns = [
        column
        for column in df.columns
        if column != "Date"
    ]

    for column in return_columns:
        df[column] = pd.to_numeric(
            df[column],
            errors="coerce"
        )

    # --------------------------------------------------
    # 9. Replace French Library missing codes
    # --------------------------------------------------

    df[return_columns] = (
        df[return_columns]
        .replace(
            [-99.99, -999],
            pd.NA
        )
    )

    # --------------------------------------------------
    # 10. Sort and remove duplicate dates
    # --------------------------------------------------

    df = (
        df
        .sort_values("Date")
        .drop_duplicates(
            subset=["Date"]
        )
    )

    # --------------------------------------------------
    # 11. Check number of industry columns
    # --------------------------------------------------

    if len(return_columns) != 30:
        print(
            f"WARNING: Expected 30 industry columns "
            f"but found {len(return_columns)}."
        )

    # --------------------------------------------------
    # 12. Missing-value report
    # --------------------------------------------------

    missing_count = (
        df[return_columns]
        .isna()
        .sum()
        .sum()
    )

    print(
        "Missing return values found:",
        missing_count
    )

    # We remove rows with unavailable portfolio returns.
    # Genuine extreme market returns are NOT removed.

    df = df.dropna(
        subset=return_columns
    )

    # --------------------------------------------------
    # 13. Convert percentage returns to decimal returns
    # --------------------------------------------------
    # Kenneth French returns are normally reported
    # in percentage units:
    #
    #     1.25 = 1.25%
    #
    # Portfolio calculations require:
    #
    #     0.0125
    # --------------------------------------------------

    df[return_columns] = (
        df[return_columns] / 100.0
    )

    # --------------------------------------------------
    # 14. Set Date as index
    # --------------------------------------------------

    df = df.set_index("Date")

    # --------------------------------------------------
    # 15. Basic validation
    # --------------------------------------------------

    if not df.index.is_monotonic_increasing:
        raise ValueError(
            "Dates are not sorted correctly."
        )

    if df.index.duplicated().any():
        raise ValueError(
            "Duplicate dates remain in dataset."
        )

    if df.isna().any().any():
        raise ValueError(
            "Missing values remain after cleaning."
        )

    # --------------------------------------------------
    # 16. Save cleaned dataset
    # --------------------------------------------------

    CLEAN_FILE.parent.mkdir(
        parents=True,
        exist_ok=True
    )

    df.to_csv(
        CLEAN_FILE
    )

    # --------------------------------------------------
    # 17. Print validation summary
    # --------------------------------------------------

    print("\n" + "=" * 55)
    print("REGX DATA VALIDATION")
    print("=" * 55)

    print(
        "Observations:",
        len(df)
    )

    print(
        "Industries:",
        df.shape[1]
    )

    print(
        "Start date:",
        df.index.min().date()
    )

    print(
        "End date:",
        df.index.max().date()
    )

    print(
        "Missing values:",
        df.isna().sum().sum()
    )

    print(
        "Duplicate dates:",
        df.index.duplicated().sum()
    )

    print(
        "Minimum daily return:",
        round(df.min().min(), 4)
    )

    print(
        "Maximum daily return:",
        round(df.max().max(), 4)
    )

    print(
        "\nClean file saved to:"
    )

    print(
        CLEAN_FILE
    )

    print("=" * 55)

    return df


# ------------------------------------------------------
# Run data.py directly for testing
# ------------------------------------------------------

if __name__ == "__main__":

    returns = load_data()

    print("\nFirst 5 rows:\n")
    print(
        returns.head()
    )

    print("\nColumn names:\n")
    print(
        returns.columns.tolist()
    )
