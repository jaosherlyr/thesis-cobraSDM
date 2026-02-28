# ==========================================
# STEP 3: BUILD FINAL MODEL DATASET
# ==========================================

import pandas as pd

# ----------------------------
# 1. LOAD CLEAN FILES
# ----------------------------

counts_path = "data/redistributed_counts_clean.csv"
env_path = "data/environmental_data_clean.csv"

counts = pd.read_csv(counts_path)
env = pd.read_csv(env_path)

print("Files loaded.")
print("Counts shape:", counts.shape)
print("Env shape:", env.shape)


# ----------------------------
# 2. ENSURE DATATYPES MATCH
# ----------------------------

counts["barangay_psgc"] = counts["barangay_psgc"].astype(int)
env["adm4_psgc"] = env["adm4_psgc"].astype(int)

counts["date"] = pd.to_datetime(counts["date"])
env["date"] = pd.to_datetime(env["date"])


# ----------------------------
# 3. MERGE COUNTS + ENVIRONMENT
# ----------------------------

df = counts.merge(
    env,
    left_on=["barangay_psgc", "date"],
    right_on=["adm4_psgc", "date"],
    how="left"
)

df = df.drop(columns=["adm4_psgc"])

print("Merged dataset shape:", df.shape)


# ----------------------------
# 4. CHECK FOR ENVIRONMENTAL GAPS
# ----------------------------

missing_env = df[[
    "air_temperature",
    "soil_temperature",
    "soil_moisture",
    "LST_C",
    "landcover"
]].isna().sum()

print("\nMissing environmental values:")
print(missing_env)


# ----------------------------
# 5. SORT FOR TIME SERIES
# ----------------------------

df = df.sort_values(
    ["barangay_psgc", "species", "date"]
).reset_index(drop=True)


# ----------------------------
# 6. SAVE RAW MERGED DATA
# ----------------------------

df.to_csv("data/model_dataset_raw.csv", index=False)

print("\nSaved: data/model_dataset_raw.csv")