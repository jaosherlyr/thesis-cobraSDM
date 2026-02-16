#!/usr/bin/env python3

"""
Usage:
    python assign_barangay.py input.csv shapefile.shp
"""

import sys
import os
import pandas as pd
import geopandas as gpd

OUTPUT_PATH = "data/barangay_sightings.csv"


def main(csv_path, shapefile_path):

    df = pd.read_csv(csv_path)

    required_cols = ['date', 'species', 'lat', 'long']
    for col in required_cols:
        if col not in df.columns:
            raise ValueError(f"Missing required column: {col}")

    # Sightings GeoDataFrame (WGS84)
    gdf = gpd.GeoDataFrame(
        df,
        geometry=gpd.points_from_xy(df['long'], df['lat']),
        crs="EPSG:4326"
    )

    # Load barangays and convert to WGS84
    barangays = gpd.read_file(shapefile_path)
    barangays = barangays.to_crs("EPSG:4326")

    # -----------------------------------
    # STEP 1: Within join
    # -----------------------------------
    joined = gpd.sjoin(
        gdf,
        barangays,
        how="left",
        predicate="within"
    )

    if "index_right" in joined.columns:
        joined = joined.drop(columns=["index_right"])

    # -----------------------------------
    # STEP 2: Nearest correction
    # -----------------------------------
    unmatched_mask = joined["adm4_psgc"].isnull()

    if unmatched_mask.sum() > 0:

        unmatched = joined[unmatched_mask].copy()

        # Project to metric CRS
        unmatched_proj = unmatched.to_crs("EPSG:32651")
        barangays_proj = barangays.to_crs("EPSG:32651")

        nearest = gpd.sjoin_nearest(
            unmatched_proj,
            barangays_proj,
            how="left",
            distance_col="distance_m"
        )

        if "index_right" in nearest.columns:
            nearest = nearest.drop(columns=["index_right"])

        # Identify suffixed columns from right dataframe
        right_cols = [col for col in nearest.columns if col.endswith("_right")]

        # Map right columns back to original names
        rename_map = {col: col.replace("_right", "") for col in right_cols}

        nearest = nearest.rename(columns=rename_map)

        # Columns we need from nearest
        needed_cols = [
            "adm4_psgc",
            "adm4_en",
            "adm3_psgc",
            "adm2_psgc",
            "adm1_psgc",
            "area_km2"
        ]

        joined.loc[unmatched_mask, needed_cols] = nearest[needed_cols].values

    # -----------------------------------
    # Final Cleanup
    # -----------------------------------
    joined = joined.rename(columns={
        "adm4_en": "barangay_name",
        "adm4_psgc": "barangay_psgc"
    })

    keep_cols = [
        "date",
        "species",
        "lat",
        "long",
        "barangay_psgc",
        "barangay_name",
        "adm3_psgc",
        "adm2_psgc",
        "adm1_psgc",
        "area_km2"
    ]

    joined = joined[keep_cols]

    os.makedirs("data", exist_ok=True)
    joined.to_csv(OUTPUT_PATH, index=False)

    print(f"Success. File saved to: {OUTPUT_PATH}")


if __name__ == "__main__":

    if len(sys.argv) != 3:
        print("Usage: python assign_barangay.py input.csv shapefile.shp")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
