#!/usr/bin/env python3
"""
merge_csv.py

Purpose:
- Merge multiple CSV files into one
- Require columns: date, species, lat, long
- Preserve rows exactly (no transformation)
- Fail if any input CSV is missing required columns

Usage:
    python merge_csv.py output.csv input1.csv input2.csv ...
"""

import sys
import pandas as pd

REQUIRED_COLUMNS = ["date", "species", "lat", "long"]


def main(output_csv, input_csvs):
    all_frames = []

    for path in input_csvs:
        try:
            df = pd.read_csv(path)
        except Exception as e:
            raise RuntimeError(f"❌ Failed to read '{path}': {e}")

        missing = [c for c in REQUIRED_COLUMNS if c not in df.columns]
        if missing:
            raise ValueError(
                f"❌ '{path}' is missing required columns: {missing}"
            )

        # Keep ONLY required columns (order enforced)
        df = df[REQUIRED_COLUMNS]

        all_frames.append(df)
        print(f"✅ Loaded {len(df)} rows from {path}")

    if not all_frames:
        raise RuntimeError("❌ No input CSVs provided")

    merged = pd.concat(all_frames, ignore_index=True)
    merged.to_csv(output_csv, index=False)

    print(f"\n✅ Combined CSV saved to: {output_csv}")
    print(f"📊 Total rows merged: {len(merged)}")


if __name__ == "__main__":
    if len(sys.argv) < 3:
        print(
            "Usage:\n"
            "  python merge_sightings.py output.csv input1.csv input2.csv ..."
        )
        sys.exit(1)

    output_csv = sys.argv[1]
    input_csvs = sys.argv[2:]

    main(output_csv, input_csvs)
