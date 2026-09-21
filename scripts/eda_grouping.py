"""
Week 2 Exercise, Step 7: Grouping and Aggregation

Two groupings on wildcat_loans_clean.csv:
  1. By loan_status: count, mean loan_amount (2dp), mean interest_rate (4dp),
     mean credit_score (1dp, excluding nulls), mean debt_to_income_ratio (4dp),
     sorted by count descending.
  2. By loan_purpose: count of loans and count/percentage of loans with
     loan_status == "Default", sorted by default percentage descending.
"""

import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"


def grouping_by_status(df: pd.DataFrame):
    grouped = df.groupby("loan_status").agg(
        count=("loan_status", "size"),
        mean_loan_amount=("loan_amount", "mean"),
        mean_interest_rate=("interest_rate", "mean"),
        mean_credit_score=("credit_score", "mean"),
        mean_debt_to_income_ratio=("debt_to_income_ratio", "mean"),
    )
    grouped["mean_loan_amount"] = grouped["mean_loan_amount"].round(2)
    grouped["mean_interest_rate"] = grouped["mean_interest_rate"].round(4)
    grouped["mean_credit_score"] = grouped["mean_credit_score"].round(1)
    grouped["mean_debt_to_income_ratio"] = grouped["mean_debt_to_income_ratio"].round(4)
    grouped = grouped.sort_values("count", ascending=False)

    print("=" * 90)
    print("GROUPED BY LOAN_STATUS")
    print("=" * 90)
    print(grouped)


def grouping_by_purpose(df: pd.DataFrame):
    total_by_purpose = df.groupby("loan_purpose").size().rename("count")
    default_by_purpose = df[df["loan_status"] == "Default"].groupby("loan_purpose").size().rename("default_count")

    result = pd.concat([total_by_purpose, default_by_purpose], axis=1).fillna(0)
    result["default_count"] = result["default_count"].astype(int)
    result["default_pct"] = (result["default_count"] / result["count"] * 100).round(1)
    result = result.sort_values("default_pct", ascending=False)

    print()
    print("=" * 90)
    print("GROUPED BY LOAN_PURPOSE — DEFAULT RATE")
    print("=" * 90)
    print(result)


def main():
    pd.set_option("display.width", 120)
    pd.set_option("display.max_columns", None)
    df = pd.read_csv(DATA_PATH)
    grouping_by_status(df)
    grouping_by_purpose(df)


if __name__ == "__main__":
    main()
