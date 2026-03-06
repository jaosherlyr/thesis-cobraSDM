import geopandas as gpd
import pandas as pd
import matplotlib.pyplot as plt
import os

BARANGAY_SHP = "data/shapefiles/PH_Adm4_BgySubMuns/PH_Adm4_BgySubMuns.shp"
COUNTRY_SHP = "data/shapefiles/PH_Adm0_Country/PH_Adm0_Country.shp"
HSI_FOLDER = "outputs_multi"
OUTPUT_FOLDER = "final_maps_clean"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

barangays = gpd.read_file(BARANGAY_SHP)
country = gpd.read_file(COUNTRY_SHP)

barangays["adm4_psgc"] = barangays["adm4_psgc"].astype(str)

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizons = ["1day", "7day"]

for sp in species_list:
    for horizon in horizons:

        print(f"Generating improved map for {sp} - {horizon}")

        hsi = pd.read_csv(f"{HSI_FOLDER}/{sp}_{horizon}_HSI.csv")
        hsi["barangay_psgc"] = hsi["barangay_psgc"].astype(str)

        merged = barangays.merge(
            hsi,
            left_on="adm4_psgc",
            right_on="barangay_psgc",
            how="inner"
        )

        # Larger footprint figure
        fig, ax = plt.subplots(figsize=(15, 20))   # good thesis size

        # light background to increase contrast
        ax.set_facecolor("#ebebeb")

        merged.plot(
            column="HSI",
            cmap="plasma",

            # Fixed scale across ALL maps
            vmin=0,
            vmax=1,

            # Polygon border contrast
            linewidth=0.12,
            edgecolor="#222222",

            legend=True,
            legend_kwds={
                "label": "Habitat Suitability Index (HSI)",
                "shrink": 0.6,
                "pad": 0.01
            },
            ax=ax
        )

        # Country outline
        country.boundary.plot(
            ax=ax,
            linewidth=0.2,
            edgecolor="black"
        )

        ax.set_title(
            f"{sp.replace('_',' ')} – {horizon.upper()} Habitat Suitability Forecast",
            fontsize=12,
            pad=8
        )

        ax.axis("off")

        # Reduce whitespace margins
        plt.subplots_adjust(left=0.01, right=0.99, top=0.97, bottom=0.01)

        plt.savefig(
            f"{OUTPUT_FOLDER}/{sp}_{horizon}_clean.png",
            dpi=400,
            bbox_inches="tight",
            pad_inches=0.05
        )

        plt.close()

print("Clean maps generated.")