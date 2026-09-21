"""
Week 2 Exercise: Exploratory Data Analysis - Initial Inspection

Loads wildcat_loans_clean.csv and prints:
  - the shape of the dataset (rows and columns)
  - all column names with their data types
  - the count of missing values for every column
"""

import pandas as pd
from pathlib import Path

# Path to the data file, relative to this script's location
DATA_PATH = Path(__file__).resolve().parent.parent / "02_Data" / "Raw" / "wildcat_loans_clean.csv"


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


if __name__ == "__main__":
    main()
