# ==========================================
# GENERATE HSI FOR 1-DAY AND 7-DAY MODELS
# ==========================================

import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.preprocessing import MinMaxScaler
import os

SEQ_LENGTH = 14

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizons = ["1day", "7day"]

# Load full scaled dataset (needed to reconstruct barangay-date mapping)
df = pd.read_csv("data/model_dataset.csv")
df["date"] = pd.to_datetime(df["date"])

os.makedirs("outputs_multi", exist_ok=True)

for sp in species_list:
    for horizon in horizons:

        print(f"\nGenerating HSI for {sp} - {horizon}")

        # ----------------------------
        # Load trained model
        # ----------------------------
        model = tf.keras.models.load_model(
            f"models_multi/{sp}_{horizon}.keras"
        )

        # ----------------------------
        # Load sequences
        # ----------------------------
        X = np.load(
            f"data/sequence_multi/X_{sp}_{horizon}.npy"
        )

        # Predict abundance
        y_pred = model.predict(X, batch_size=512)
        y_pred = y_pred.flatten()

        # ----------------------------
        # Reconstruct barangay-date mapping
        # ----------------------------

        sp_name_clean = sp.replace("_", " ")
        sp_df = df[df["species"] == sp_name_clean].copy()
        sp_df = sp_df.sort_values(["barangay_psgc", "date"])

        reconstructed = []
        index_counter = 0

        horizon_days = 1 if horizon == "1day" else 7

        for barangay, group in sp_df.groupby("barangay_psgc"):

            group = group.sort_values("date").reset_index(drop=True)

            # valid prediction dates
            target_dates = group["date"].iloc[
                SEQ_LENGTH + horizon_days - 1:
            ].values

            n_preds = len(target_dates)

            preds = y_pred[index_counter:index_counter + n_preds]

            temp_df = pd.DataFrame({
                "barangay_psgc": barangay,
                "date": target_dates,
                "predicted_abundance": preds
            })

            reconstructed.append(temp_df)
            index_counter += n_preds

        pred_df = pd.concat(reconstructed, ignore_index=True)

        # ----------------------------
        # Aggregate predicted abundance per barangay
        # ----------------------------

        barangay_mean = (
            pred_df
            .groupby("barangay_psgc")["predicted_abundance"]
            .mean()
            .reset_index()
        )

        # ----------------------------
        # Convert to Habitat Suitability Index (HSI)
        # ----------------------------

        scaler = MinMaxScaler()
        barangay_mean["HSI"] = scaler.fit_transform(
            barangay_mean[["predicted_abundance"]]
        )

        # ----------------------------
        # Save output
        # ----------------------------

        barangay_mean.to_csv(
            f"outputs_multi/{sp}_{horizon}_HSI.csv",
            index=False
        )

        print(f"Saved HSI file: outputs_multi/{sp}_{horizon}_HSI.csv")

print("\nDone generating all HSI files.")