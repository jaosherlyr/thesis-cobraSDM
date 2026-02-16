#!/usr/bin/env python3

"""
Usage:
    python aggregate_daily_counts.py input.csv
"""

import sys
import os
import pandas as pd

OUTPUT_PATH = "data/daily_counts.csv"


def main(csv_path):

    # Load barangay-assigned sightings
    df = pd.read_csv(csv_path)

    required_cols = [
        "date",
        "species",
        "barangay_psgc"
    ]

    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Ensure date is datetime
    df["date"] = pd.to_datetime(df["date"])

    # -----------------------------------------
    # Aggregate daily counts
    # -----------------------------------------
    daily_counts = (
        df
        .groupby(["barangay_psgc", "species", "date"])
        .size()
        .reset_index(name="count")
    )

    # Optional: sort for cleanliness
    daily_counts = daily_counts.sort_values(
        ["barangay_psgc", "species", "date"]
    )

    # Save output
    os.makedirs("data", exist_ok=True)
    daily_counts.to_csv(OUTPUT_PATH, index=False)

    print(f"Success. File saved to: {OUTPUT_PATH}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python aggregate_daily_counts.py input.csv")
        sys.exit(1)

    main(sys.argv[1])
