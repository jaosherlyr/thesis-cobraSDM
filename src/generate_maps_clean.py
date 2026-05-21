import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
import os

BARANGAY_SHP = "data/shapefiles/PH_Adm4_BgySubMuns/PH_Adm4_BgySubMuns.shp"
COUNTRY_SHP = "data/shapefiles/PH_Adm0_Country/PH_Adm0_Country.shp"
HSI_FOLDER = "outputs_multi"
OUTPUT_FOLDER = "final_maps_clean"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# Load shapefiles
barangays = gpd.read_file(BARANGAY_SHP)
country = gpd.read_file(COUNTRY_SHP)

barangays["adm4_psgc"] = barangays["adm4_psgc"].astype(str)

# Geometry simplification for cleaner rendering
barangays["geometry"] = barangays.geometry.simplify(0.00008, preserve_topology=True)

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizons = ["1day", "7day"]

for sp in species_list:
    for horizon in horizons:

        print(f"Generating SDM-style map for {sp} - {horizon}")

        hsi = pd.read_csv(f"{HSI_FOLDER}/{sp}_{horizon}_HSI.csv")
        hsi["barangay_psgc"] = hsi["barangay_psgc"].astype(str)

        merged = barangays.merge(
            hsi,
            left_on="adm4_psgc",
            right_on="barangay_psgc",
            how="inner"
        )

        # Compute centroids
        merged["centroid"] = merged.geometry.centroid
        merged["x"] = merged.centroid.x
        merged["y"] = merged.centroid.y

        # Mask Luzon predictions for Naja samarensis
        if sp == "Naja_samarensis":
            merged = merged[merged.centroid.y <= 12.5]

        # Clean numerical values
        merged["HSI"] = pd.to_numeric(merged["HSI"], errors="coerce")
        merged.replace([np.inf, -np.inf], np.nan, inplace=True)
        merged.dropna(subset=["HSI"], inplace=True)

        fig, ax = plt.subplots(figsize=(16, 21))

        ax.set_facecolor("#f7f7f7")

        # Base land layer
        country.plot(
            ax=ax,
            color="#f0f0f0",
            edgecolor="none"
        )

        # ------------------------------
        # KDE HOTSPOT LAYER (SAFE VERSION)
        # ------------------------------
        kde_data = merged[merged["HSI"] > merged["HSI"].quantile(0.60)]

        if len(kde_data) > 10:  # ensure enough points for KDE
            sns.kdeplot(
                x=kde_data["x"],
                y=kde_data["y"],
                weights=kde_data["HSI"],
                cmap="plasma",
                fill=True,
                alpha=0.18,
                levels=20,
                bw_adjust=0.45,
                thresh=0.05,
                ax=ax
            )

        # ------------------------------
        # BARANGAY SUITABILITY POLYGONS
        # ------------------------------
        merged.plot(
            column="HSI",
            cmap="plasma",
            vmin=0,
            vmax=1,
            linewidth=0.15,
            edgecolor="#2e2e2e",
            legend=True,
            legend_kwds={
                "label": "Habitat Suitability Index (HSI)",
                "shrink": 0.55,
                "pad": 0.02
            },
            ax=ax
        )

        # Coastline outline
        country.boundary.plot(
            ax=ax,
            linewidth=0.8,
            edgecolor="black"
        )

        ax.set_title(
            f"{sp.replace('_',' ')} – {horizon.upper()} Habitat Suitability Forecast",
            fontsize=14,
            pad=12,
            weight="bold"
        )

        ax.axis("off")

        plt.subplots_adjust(
            left=0.02,
            right=0.98,
            top=0.96,
            bottom=0.02
        )

        plt.savefig(
            f"{OUTPUT_FOLDER}/{sp}_{horizon}_clean.png",
            dpi=500,
            bbox_inches="tight",
            pad_inches=0.05
        )

        plt.close()

print("Professional SDM maps generated.")