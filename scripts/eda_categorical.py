"""
Week 2 Exercise, Step 5: Exploring Categorical Variables

For each categorical column (loan_purpose, loan_status, state) in
wildcat_loans_clean.csv, prints the count and percentage of rows for
each unique value, sorted most to least frequent. Percentages are
shown to one decimal place.
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"

CATEGORICAL_COLUMNS = ["loan_purpose", "loan_status", "state"]


def print_distribution(df: pd.DataFrame, column: str):
    counts = df[column].value_counts().sort_values(ascending=False)
    pct = (counts / len(df) * 100).round(1)
    summary = pd.DataFrame({"count": counts, "pct": pct})
    print("=" * 60)
    print(f"{column.upper()} — {df[column].nunique()} unique values")
    print("=" * 60)
    print(summary)
    print()


def main():
    df = pd.read_csv(DATA_PATH)
    for col in CATEGORICAL_COLUMNS:
        print_distribution(df, col)


if __name__ == "__main__":
    main()
