"""
Week 2 Exercise, Step 8: Relationships Between Variables

1. Computes and prints the correlation matrix for all numeric columns in
   wildcat_loans_clean.csv (excluding identifiers loan_id and
   borrower_id), rounded to two decimal places, and identifies the three
   strongest correlations (positive or negative, excluding self-pairs).
2. Creates a scatter plot of credit_score (x) vs interest_rate (y),
   colored by loan_status, saved as outputs/scatter_credit_rate.png.
"""

import itertools

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd
from pathlib import Path

DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"
OUTPUT_DIR = Path(__file__).resolve().parent.parent / "outputs"

EXCLUDE_COLS = ["loan_id", "borrower_id"]
STATUS_COLORS = {
    "Current": "#4C72B0",
    "Paid Off": "#55A868",
    "Delinquent": "#DD8452",
    "Default": "#C44E52",
}


def correlation_analysis(df: pd.DataFrame):
    numeric_df = df.select_dtypes(include="number").drop(columns=EXCLUDE_COLS, errors="ignore")
    corr = numeric_df.corr().round(2)

    pd.set_option("display.width", 120)
    pd.set_option("display.max_columns", None)

    print("=" * 90)
    print("CORRELATION MATRIX (numeric columns, excluding loan_id / borrower_id)")
    print("=" * 90)
    print(corr)

    # Identify the three strongest correlations, excluding self-pairs and duplicate pairs
    pairs = []
    for col_a, col_b in itertools.combinations(corr.columns, 2):
        pairs.append((col_a, col_b, corr.loc[col_a, col_b]))
    pairs.sort(key=lambda x: abs(x[2]), reverse=True)

    print()
    print("=" * 90)
    print("THREE STRONGEST CORRELATIONS")
    print("=" * 90)
    for col_a, col_b, val in pairs[:3]:
        print(f"{col_a} <-> {col_b}: {val}")


def scatter_plot(df: pd.DataFrame):
    fig, ax = plt.subplots(figsize=(10, 7))
    for status, color in STATUS_COLORS.items():
        subset = df[df["loan_status"] == status]
        ax.scatter(subset["credit_score"], subset["interest_rate"], s=18, alpha=0.6,
                   color=color, label=status)

    ax.set_title("Credit Score vs. Interest Rate by Loan Status")
    ax.set_xlabel("Credit Score")
    ax.set_ylabel("Interest Rate (%)")
    ax.legend(title="Loan Status")
    fig.tight_layout()

    out_path = OUTPUT_DIR / "scatter_credit_rate.png"
    fig.savefig(out_path, dpi=150)
    plt.close(fig)
    print(f"\nSaved: {out_path}")


def main():
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(DATA_PATH)
    correlation_analysis(df)
    scatter_plot(df)


if __name__ == "__main__":
    main()
