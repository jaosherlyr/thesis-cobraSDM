import os
import pandas as pd
import geopandas as gpd
import matplotlib.pyplot as plt
from matplotlib.gridspec import GridSpec

# ===============================
# FILE PATHS
# ===============================

BARANGAY_SHP = "data/shapefiles/PH_Adm4_BgySubMuns/PH_Adm4_BgySubMuns.shp"
COUNTRY_SHP = "data/shapefiles/PH_Adm0_Country/PH_Adm0_Country.shp"
HSI_CSV = "outputs_multi/Naja_philippinensis_1day_HSI.csv"

OUTPUT_FOLDER = "choropleth"
os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# ===============================
# LOAD DATA
# ===============================

barangays = gpd.read_file(BARANGAY_SHP)
country = gpd.read_file(COUNTRY_SHP)
hsi_df = pd.read_csv(HSI_CSV)

barangays["adm4_psgc"] = barangays["adm4_psgc"].astype(int)
hsi_df["barangay_psgc"] = hsi_df["barangay_psgc"].astype(int)

merged = barangays.merge(
    hsi_df,
    left_on="adm4_psgc",
    right_on="barangay_psgc",
    how="left"
)

# ===============================
# COMPUTE TRUE ASPECT RATIO
# ===============================

minx, miny, maxx, maxy = merged.total_bounds
width = maxx - minx
height = maxy - miny
aspect_ratio = height / width

# Make width fixed, scale height accordingly
fig_width = 10
fig_height = fig_width * aspect_ratio * 1.1  # slightly taller for title

fig = plt.figure(figsize=(fig_width, fig_height))

# Map wide, colorbar narrow
gs = GridSpec(1, 2, width_ratios=[25, 1], figure=fig)

ax = fig.add_subplot(gs[0])
cax = fig.add_subplot(gs[1])

# Background
background_color = "#f2f2f2"
fig.patch.set_facecolor(background_color)
ax.set_facecolor(background_color)

# ===============================
# PLOT
# ===============================

merged.plot(
    column="HSI",
    cmap="plasma",
    linewidth=0.05,
    edgecolor="none",
    legend=True,
    ax=ax,
    cax=cax,
    vmin=0,
    vmax=1,
    missing_kwds={
        "color": "lightgrey",
        "label": "No Data"
    }
)

country.boundary.plot(
    ax=ax,
    linewidth=1.2,
    edgecolor="black"
)

# Tight bounds
ax.set_xlim(minx, maxx)
ax.set_ylim(miny, maxy)
ax.set_aspect("equal")

ax.set_title(
    "Habitat Suitability Index (HSI)\nNaja philippinensis – 1-Day Forecast",
    fontsize=11,
    pad=6
)

ax.set_axis_off()

plt.subplots_adjust(left=0.01, right=0.93, top=0.97, bottom=0.01)

output_path = os.path.join(OUTPUT_FOLDER, "Naja_philippinensis_1day_HSI_map.png")
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.close()

print("Map saved to:", output_path)