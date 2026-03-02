# ==========================================
# TRAIN CNN-LSTM FOR 1-DAY AND 7-DAY
# ==========================================

import numpy as np
import tensorflow as tf
from sklearn.metrics import mean_absolute_error, mean_squared_error
import os

SEQ_LENGTH = 14
EPOCHS = 10
BATCH_SIZE = 256

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizons = ["1day", "7day"]

os.makedirs("models_multi", exist_ok=True)

for sp in species_list:
    for horizon in horizons:

        print(f"\nTraining {sp} - {horizon}")

        X = np.load(f"data/sequence_multi/X_{sp}_{horizon}.npy")
        y = np.load(f"data/sequence_multi/y_{sp}_{horizon}.npy")

        split_index = int(len(X) * 0.8)

        X_train, X_test = X[:split_index], X[split_index:]
        y_train, y_test = y[:split_index], y[split_index:]

        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(SEQ_LENGTH, 6)),
            tf.keras.layers.Conv1D(32, 3, activation="relu"),
            tf.keras.layers.MaxPooling1D(2),
            tf.keras.layers.LSTM(64),
            tf.keras.layers.Dense(32, activation="relu"),
            tf.keras.layers.Dense(1)
        ])

        model.compile(
            optimizer="adam",
            loss="mse",
            metrics=["mae"]
        )

        model.fit(
            X_train,
            y_train,
            epochs=EPOCHS,
            batch_size=BATCH_SIZE,
            validation_split=0.1,
            verbose=1
        )

        y_pred = model.predict(X_test)

        mae = mean_absolute_error(y_test, y_pred)
        rmse = np.sqrt(mean_squared_error(y_test, y_pred))

        print(f"{sp} - {horizon} MAE:", mae)
        print(f"{sp} - {horizon} RMSE:", rmse)

        model.save(f"models_multi/{sp}_{horizon}.keras")

print("\nDone training multi-horizon models.")