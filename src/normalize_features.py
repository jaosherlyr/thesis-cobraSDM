# ==========================================
# STEP 5: NORMALIZE ENVIRONMENTAL FEATURES
# ==========================================

import pandas as pd
from sklearn.preprocessing import MinMaxScaler
import joblib

# Load model dataset
df = pd.read_csv("data/model_dataset.csv")

# Features to scale
feature_cols = [
    "air_temperature",
    "soil_temperature",
    "soil_moisture",
    "LST_C",
    "landcover"
]

scaler = MinMaxScaler()

df[feature_cols] = scaler.fit_transform(df[feature_cols])

# Save scaler for later inference use
joblib.dump(scaler, "data/feature_scaler.save")

# Save normalized dataset
df.to_csv("data/model_dataset_scaled.csv", index=False)

print("Normalization complete.")
print("Saved: data/model_dataset_scaled.csv")
print("Scaler saved: data/feature_scaler.save")