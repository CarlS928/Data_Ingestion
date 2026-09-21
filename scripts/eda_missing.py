"""
Week 2 Exercise, Step 3: Analyzing Missing Values

Prints the count and percentage of missing values for every column in
wildcat_loans_clean.csv. Then, for the credit_score column specifically,
compares the distribution of loan_status and loan_purpose among rows
where credit_score is missing against the full dataset, to help judge
whether the missingness is random or concentrated in a particular group.
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"

pd.set_option("display.float_format", lambda x: f"{x:.1f}")


def main():
    df = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("MISSING VALUES: COUNT AND PERCENTAGE PER COLUMN")
    print("=" * 60)
    missing_count = df.isnull().sum()
    missing_pct = (missing_count / len(df) * 100).round(2)
    missing_summary = pd.DataFrame({"missing_count": missing_count, "missing_pct": missing_pct})
    print(missing_summary)

    print()
    print("=" * 60)
    print("CREDIT_SCORE MISSINGNESS: loan_status DISTRIBUTION")
    print("=" * 60)
    missing_mask = df["credit_score"].isnull()

    status_missing = (df.loc[missing_mask, "loan_status"].value_counts(normalize=True) * 100).round(1)
    status_full = (df["loan_status"].value_counts(normalize=True) * 100).round(1)
    status_compare = pd.DataFrame({
        "pct_among_missing_credit_score": status_missing,
        "pct_full_dataset": status_full,
    }).fillna(0)
    print(status_compare)

    print()
    print("=" * 60)
    print("CREDIT_SCORE MISSINGNESS: loan_purpose DISTRIBUTION")
    print("=" * 60)
    purpose_missing = (df.loc[missing_mask, "loan_purpose"].value_counts(normalize=True) * 100).round(1)
    purpose_full = (df["loan_purpose"].value_counts(normalize=True) * 100).round(1)
    purpose_compare = pd.DataFrame({
        "pct_among_missing_credit_score": purpose_missing,
        "pct_full_dataset": purpose_full,
    }).fillna(0)
    print(purpose_compare)

    print()
    n_missing = missing_mask.sum()
    pct_missing = n_missing / len(df) * 100
    print(f"Summary: {n_missing} missing credit_score values ({pct_missing:.1f}% of {len(df)} loans).")


if __name__ == "__main__":
    main()
