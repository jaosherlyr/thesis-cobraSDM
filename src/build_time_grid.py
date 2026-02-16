#!/usr/bin/env python3

"""
Usage:
    python build_time_grid.py input.csv
"""

import sys
import os
import pandas as pd

OUTPUT_PATH = "data/daily_time_grid.csv"

START_DATE = "2022-01-01"
END_DATE   = "2026-01-31"


def main(csv_path):

    # Load aggregated daily counts
    df = pd.read_csv(csv_path)

    required_cols = ["barangay_psgc", "species", "date", "count"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    df["date"] = pd.to_datetime(df["date"])

    # Filter to modeling window
    df = df[
        (df["date"] >= START_DATE) &
        (df["date"] <= END_DATE)
    ]

    # Get unique spatial + species combinations
    barangays = df["barangay_psgc"].unique()
    species_list = df["species"].unique()

    # Create full date range
    date_range = pd.date_range(
        start=START_DATE,
        end=END_DATE,
        freq="D"
    )

    # Create full Cartesian product
    full_index = pd.MultiIndex.from_product(
        [barangays, species_list, date_range],
        names=["barangay_psgc", "species", "date"]
    )

    full_df = pd.DataFrame(index=full_index).reset_index()

    # Merge observed counts
    full_df = full_df.merge(
        df,
        on=["barangay_psgc", "species", "date"],
        how="left"
    )

    # Fill missing counts with zero
    full_df["count"] = full_df["count"].fillna(0).astype(int)

    os.makedirs("data", exist_ok=True)
    full_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Success. File saved to: {OUTPUT_PATH}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python build_time_grid.py input.csv")
        sys.exit(1)

    main(sys.argv[1])
