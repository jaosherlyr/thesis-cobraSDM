# ==========================================
# STEP 2: DATA CLEANING & HARMONIZATION
# ==========================================

import pandas as pd

# ----------------------------
# 1. LOAD FILES
# ----------------------------

counts_path = "data/redistributed_counts.csv"
env_path = "data/environmental_data.csv"

counts = pd.read_csv(counts_path)
env = pd.read_csv(env_path)

print("Files loaded.")
print("Counts shape:", counts.shape)
print("Env shape:", env.shape)


# ----------------------------
# 2. FIX PSGC DATATYPE
# ----------------------------
# Sometimes PSGC loads as float (e.g., 102802046.0)
# That breaks merging.

counts["barangay_psgc"] = counts["barangay_psgc"].astype(float).astype(int)
env["adm4_psgc"] = env["adm4_psgc"].astype(float).astype(int)

print("PSGC converted to int.")


# ----------------------------
# 3. FIX DATE FORMAT
# ----------------------------
# Neural networks require consistent temporal ordering.
# Merge requires identical datetime dtype.

counts["date"] = pd.to_datetime(counts["date"])
env["date"] = pd.to_datetime(env["date"])

print("Dates converted to datetime.")


# ----------------------------
# 4. REMOVE DUPLICATES
# ----------------------------

counts = counts.drop_duplicates(
    subset=["barangay_psgc", "species", "date"]
)

env = env.drop_duplicates(
    subset=["adm4_psgc", "date"]
)

print("Duplicates removed.")


# ----------------------------
# 5. SORT FOR TIME-SERIES ORDER
# ----------------------------

counts = counts.sort_values(
    ["barangay_psgc", "species", "date"]
).reset_index(drop=True)

env = env.sort_values(
    ["adm4_psgc", "date"]
).reset_index(drop=True)

print("Data sorted.")


# ----------------------------
# 6. BASIC SANITY CHECKS
# ----------------------------

print("\nData Types (Counts):")
print(counts.dtypes)

print("\nData Types (Env):")
print(env.dtypes)

print("\nMissing values (Env):")
print(env.isna().sum())


# ----------------------------
# 7. SAVE CLEANED VERSIONS
# ----------------------------

counts.to_csv("data/clean_counts.csv", index=False)
env.to_csv("data/clean_env.csv", index=False)

print("\nCleaned files saved:")
print("data/clean_counts.csv")
print("data/clean_env.csv")