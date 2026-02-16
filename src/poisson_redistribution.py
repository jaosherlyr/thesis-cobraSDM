#!/usr/bin/env python3

"""
Usage:
    python poisson_redistribution.py input.csv
"""

import sys
import os
import pandas as pd
import numpy as np

OUTPUT_PATH = "data/redistributed_counts.csv"


def main(csv_path):

    df = pd.read_csv(csv_path)
    df["date"] = pd.to_datetime(df["date"])

    required_cols = ["barangay_psgc", "species", "date", "count"]
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    np.random.seed(42)

    new_counts = []

    # Process each barangay × species independently
    for (bgy, sp), group in df.groupby(["barangay_psgc", "species"]):

        group = group.sort_values("date").copy()

        # Compute rolling mean (14-day window)
        group["rolling_mean"] = (
            group["count"]
            .rolling(window=14, min_periods=1, center=True)
            .mean()
        )

        updated_counts = []

        for _, row in group.iterrows():

            if row["count"] > 0:
                # Keep observed sightings
                updated_counts.append(row["count"])
            else:
                # Apply Poisson only to zero days
                lam = row["rolling_mean"]
                simulated = np.random.poisson(lam)
                updated_counts.append(simulated)

        group["count"] = updated_counts

        new_counts.append(group[["barangay_psgc", "species", "date", "count"]])

    final_df = pd.concat(new_counts)

    os.makedirs("data", exist_ok=True)
    final_df.to_csv(OUTPUT_PATH, index=False)

    print(f"Success. File saved to: {OUTPUT_PATH}")


if __name__ == "__main__":

    if len(sys.argv) != 2:
        print("Usage: python poisson_redistribution.py input.csv")
        sys.exit(1)

    main(sys.argv[1])
