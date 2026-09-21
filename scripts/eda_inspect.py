"""
Week 2 Exercise: Exploratory Data Analysis - Initial Inspection

Loads wildcat_loans_clean.csv, prints to the screen, and saves a
Markdown summary report, covering:
  - the shape of the dataset (rows and columns)
  - all column names with their data types
  - the count of missing values for every column
"""

import pandas as pd
from datetime import datetime
from pathlib import Path

# Path to the data file, relative to this script's location
DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"

# Where to save the Markdown summary report
OUTPUT_PATH = Path(__file__).resolve().parent.parent / "03_Drafts" / "eda_inspect_summary.md"


def build_report(df: pd.DataFrame) -> str:
    lines = []
    lines.append("# EDA Inspection Report")
    lines.append("")
    lines.append(f"**Data file:** `{DATA_PATH.name}`  ")
    lines.append(f"**Generated:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    lines.append("")

    lines.append("## Shape (rows, columns)")
    lines.append("")
    lines.append(f"{df.shape[0]} rows x {df.shape[1]} columns")
    lines.append("")

    lines.append("## Column Names and Data Types")
    lines.append("")
    lines.append("| Column | Dtype |")
    lines.append("|---|---|")
    for col, dtype in df.dtypes.items():
        lines.append(f"| {col} | {dtype} |")
    lines.append("")

    lines.append("## Missing Values per Column")
    lines.append("")
    lines.append("| Column | Missing Count |")
    lines.append("|---|---|")
    for col, count in df.isnull().sum().items():
        lines.append(f"| {col} | {count} |")
    lines.append("")

    return "\n".join(lines)


def main():
    df = pd.read_csv(DATA_PATH)

    print("=" * 60)
    print("SHAPE (rows, columns)")
    print("=" * 60)
    print(df.shape)

    print()
    print("=" * 60)
    print("COLUMN NAMES AND DATA TYPES")
    print("=" * 60)
    print(df.dtypes)

    print()
    print("=" * 60)
    print("MISSING VALUES PER COLUMN")
    print("=" * 60)
    print(df.isnull().sum())

    report = build_report(df)
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)
    OUTPUT_PATH.write_text(report, encoding="utf-8")
    print()
    print(f"Markdown summary saved to: {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
