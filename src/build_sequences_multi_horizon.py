# ==========================================
# BUILD SEQUENCES FOR 1-DAY AND 7-DAY
# ==========================================

import pandas as pd
import numpy as np
import os

SEQ_LENGTH = 14
HORIZONS = {
    "1day": 1,
    "7day": 7
}

df = pd.read_csv("data/model_dataset.csv")
df["date"] = pd.to_datetime(df["date"])

species_list = df["species"].unique()

os.makedirs("data/sequence_multi", exist_ok=True)

for sp in species_list:

    print(f"\nProcessing species: {sp}")

    sp_df = df[df["species"] == sp].copy()
    sp_df = sp_df.sort_values(["barangay_psgc", "date"])

    feature_cols = [
        "count",
        "air_temperature",
        "soil_temperature",
        "soil_moisture",
        "LST_C",
        "landcover"
    ]

    for horizon_name, horizon_days in HORIZONS.items():

        print(f"  Building {horizon_name} sequences...")

        X_list = []
        y_list = []

        for barangay, group in sp_df.groupby("barangay_psgc"):

            group = group.sort_values("date")
            values = group[feature_cols].values

            max_index = len(values) - SEQ_LENGTH - horizon_days + 1

            for i in range(max_index):
                X_list.append(values[i:i+SEQ_LENGTH])
                y_list.append(values[i+SEQ_LENGTH+horizon_days-1][0])

        X = np.array(X_list, dtype=np.float32)
        y = np.array(y_list, dtype=np.float32)

        safe_name = sp.replace(" ", "_")

        np.save(f"data/sequence_multi/X_{safe_name}_{horizon_name}.npy", X)
        np.save(f"data/sequence_multi/y_{safe_name}_{horizon_name}.npy", y)

        print("    X shape:", X.shape)
        print("    y shape:", y.shape)

print("\nDone building multi-horizon sequences.")