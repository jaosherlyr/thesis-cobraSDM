# ==========================================
# STEP 6: BUILD CNN-LSTM SEQUENCES
# ==========================================

import pandas as pd
import numpy as np

SEQ_LENGTH = 14  # 14-day lookback

# Load scaled dataset
df = pd.read_csv("data/model_dataset.csv")
df["date"] = pd.to_datetime(df["date"])

species_list = df["species"].unique()

for sp in species_list:
    print(f"\nProcessing species: {sp}")
    
    sp_df = df[df["species"] == sp].copy()
    sp_df = sp_df.sort_values(["barangay_psgc", "date"])
    
    X_list = []
    y_list = []
    
    feature_cols = [
        "count",
        "air_temperature",
        "soil_temperature",
        "soil_moisture",
        "LST_C",
        "landcover"
    ]
    
    # Group by barangay
    for barangay, group in sp_df.groupby("barangay_psgc"):
        
        group = group.sort_values("date")
        values = group[feature_cols].values
        
        # Sliding window
        for i in range(len(values) - SEQ_LENGTH):
            X_list.append(values[i:i+SEQ_LENGTH])
            y_list.append(values[i+SEQ_LENGTH][0])  # next-day count
    
    X = np.array(X_list, dtype=np.float32)
    y = np.array(y_list, dtype=np.float32)
    
    print("X shape:", X.shape)
    print("y shape:", y.shape)
    
    # Save per species
    safe_name = sp.replace(" ", "_")
    np.save(f"data/X_{safe_name}.npy", X)
    np.save(f"data/y_{safe_name}.npy", y)
    
    print(f"Saved sequences for {sp}")