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

for sp in species_list:
    for horizon in horizons:
        
        print(f"\nEvaluating {sp} - {horizon}")
        
        # Load sequences
        X = np.load(f"data/sequence_multi/X_{sp}_{horizon}.npy")
        y = np.load(f"data/sequence_multi/y_{sp}_{horizon}.npy")
        
        # Chronological split (same as training)
        split_index = int(len(X) * 0.8)
        X_test = X[split_index:]
        y_test = y[split_index:]
        
        # Load trained model
        model = tf.keras.models.load_model(
            f"models_multi/{sp}_{horizon}.keras"
        )
        
        # Predict
        y_pred = model.predict(X_test, verbose=0)
        
        # Compute metrics
        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))
        
        results.append([sp, horizon, mae, rmse])
        
        print("MAE:", mae)
        print("RMSE:", rmse)

# Convert to DataFrame
df_results = pd.DataFrame(
    results,
    columns=["Species", "Forecast Horizon", "MAE", "RMSE"]
)

print("\nFinal Evaluation Table:")
print(df_results)