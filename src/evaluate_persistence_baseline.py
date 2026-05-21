import numpy as np
import pandas as pd
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os

SEQ_LENGTH = 14

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizons = ["1day", "7day"]

results = []

def persistence_baseline(X_test):
    """
    Naive persistence baseline:
    predict the future encounter intensity using
    the last observed count in the input sequence.

    X_test shape: (num_samples, seq_length, num_features)
    feature index 0 = count
    """
    return X_test[:, -1, 0]

for sp in species_list:
    for horizon in horizons:
        print(f"\nEvaluating {sp} - {horizon}")

        # Load sequences
        X = np.load(f"../data/sequence_multi/X_{sp}_{horizon}.npy")
        y = np.load(f"../data/sequence_multi/y_{sp}_{horizon}.npy")

        # Chronological split (same as training)
        split_index = int(len(X) * 0.8)
        X_test = X[split_index:]
        y_test = y[split_index:]

        # -----------------------------
        # CNN-LSTM model evaluation
        # -----------------------------
        model = tf.keras.models.load_model(
            f"../models_multi/{sp}_{horizon}.keras"
        )

        y_pred_model = model.predict(X_test, verbose=0).flatten()

        mae_model = mean_absolute_error(y_test, y_pred_model)
        rmse_model = np.sqrt(mean_squared_error(y_test, y_pred_model))

        print("CNN-LSTM MAE:", mae_model)
        print("CNN-LSTM RMSE:", rmse_model)

        results.append({
            "Species": sp,
            "Forecast Horizon": horizon,
            "Model": "CNN-LSTM",
            "MAE": mae_model,
            "RMSE": rmse_model
        })

        # -----------------------------
        # Persistence baseline
        # -----------------------------
        y_pred_baseline = persistence_baseline(X_test)

        mae_baseline = mean_absolute_error(y_test, y_pred_baseline)
        rmse_baseline = np.sqrt(mean_squared_error(y_test, y_pred_baseline))

        print("Baseline MAE:", mae_baseline)
        print("Baseline RMSE:", rmse_baseline)

        results.append({
            "Species": sp,
            "Forecast Horizon": horizon,
            "Model": "Persistence",
            "MAE": mae_baseline,
            "RMSE": rmse_baseline
        })

# Convert to DataFrame
df_results = pd.DataFrame(results)

# Optional: nicer species labels
species_name_map = {
    "Naja_philippinensis": "N. philippinensis",
    "Naja_samarensis": "N. samarensis",
    "Ophiophagus_hannah": "O. hannah"
}
df_results["Species"] = df_results["Species"].map(species_name_map)

# Optional: nicer horizon labels
horizon_map = {
    "1day": "1-day",
    "7day": "7-day"
}
df_results["Forecast Horizon"] = df_results["Forecast Horizon"].map(horizon_map)

# Round for display
df_results["MAE"] = df_results["MAE"].round(6)
df_results["RMSE"] = df_results["RMSE"].round(6)

# Sort rows nicely
df_results = df_results.sort_values(
    by=["Species", "Forecast Horizon", "Model"]
).reset_index(drop=True)

print("\nFinal Evaluation Table:")
print(df_results)

# Save results
os.makedirs("outputs_multi", exist_ok=True)
df_results.to_csv("outputs_multi/forecast_performance_with_baseline.csv", index=False)

print("\nSaved to: outputs_multi/forecast_performance_with_baseline.csv")