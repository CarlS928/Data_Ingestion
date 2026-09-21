"""
Week 2 Exercise, Step 4: Summary Statistics

Prints descriptive statistics (count, mean, std, min, 25%, 50%, 75%, max)
for all numeric columns in wildcat_loans_clean.csv. loan_amount is
rounded to two decimal places; other columns keep enough precision to be
useful (rates/ratios/scores rounded to 2 decimals for readability).
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"


def main():
    df = pd.read_csv(DATA_PATH)
    numeric_df = df.select_dtypes(include="number")

    stats = numeric_df.describe().T
    stats = stats.round(2)
    # loan_amount specifically rounded to 2 decimal places (already covered by the round above,
    # called out explicitly here per the specification)
    if "loan_amount" in stats.index:
        stats.loc["loan_amount"] = stats.loc["loan_amount"].round(2)

    pd.set_option("display.width", 120)
    pd.set_option("display.max_columns", None)

    print("=" * 100)
    print("DESCRIPTIVE STATISTICS FOR NUMERIC COLUMNS")
    print("=" * 100)
    print(stats)


if __name__ == "__main__":
    main()
