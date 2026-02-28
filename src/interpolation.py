# ==========================================
# STEP 4: SMART ENVIRONMENTAL IMPUTATION
# ==========================================

import pandas as pd

df = pd.read_csv("data/raw/model_dataset_raw.csv")
df["date"] = pd.to_datetime(df["date"])

df = df.sort_values(["barangay_psgc", "date"])

# ERA5 variables (continuous climate variables)
era5_cols = [
    "air_temperature",
    "soil_temperature",
    "soil_moisture"
]

# LST (can have cloud gaps)
lst_cols = ["LST_C"]

# Landcover (quasi-static over short term)
landcover_cols = ["landcover"]

# ----------------------------
# Interpolate ERA5
# ----------------------------

df[era5_cols] = (
    df.groupby("barangay_psgc")[era5_cols]
    .apply(lambda x: x.interpolate(method="linear"))
    .reset_index(drop=True)
)

# ----------------------------
# Forward-fill LST
# ----------------------------

df[lst_cols] = (
    df.groupby("barangay_psgc")[lst_cols]
    .apply(lambda x: x.fillna(method="ffill"))
    .reset_index(drop=True)
)

# ----------------------------
# Forward-fill landcover
# ----------------------------

df[landcover_cols] = (
    df.groupby("barangay_psgc")[landcover_cols]
    .apply(lambda x: x.fillna(method="ffill"))
    .reset_index(drop=True)
)

# Final safety fill
df = df.fillna(method="bfill")

print("Remaining NaNs:")
print(df.isna().sum())

df.to_csv("data/model_dataset.csv", index=False)

print("Saved: data/model_dataset.csv")