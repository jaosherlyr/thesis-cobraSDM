import numpy as np
import pandas as pd
import tensorflow as tf
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

# =========================
# SETTINGS
# =========================
SPECIES = "Naja_philippinensis"
HORIZON = "1day"
SEQ_LENGTH = 14

# Zoomed active window
XMIN = pd.Timestamp("2025-09-01")
XMAX = pd.Timestamp("2026-01-31")

# =========================
# LOAD DATA
# =========================
df = pd.read_csv("../data/model_dataset.csv")
df["date"] = pd.to_datetime(df["date"])

species_name_in_csv = SPECIES.replace("_", " ")
df = df[df["species"] == species_name_in_csv].copy()
df = df.sort_values(["barangay_psgc", "date"])

# =========================
# LOAD SEQUENCES + MODEL
# =========================
X = np.load(f"../data/sequence_multi/X_{SPECIES}_{HORIZON}.npy")
y = np.load(f"../data/sequence_multi/y_{SPECIES}_{HORIZON}.npy")

split_index = int(len(X) * 0.8)
X_test = X[split_index:]

model = tf.keras.models.load_model(f"../models_multi/{SPECIES}_{HORIZON}.keras")
y_pred = model.predict(X_test, verbose=0).flatten()

horizon_days = 1 if HORIZON == "1day" else 7

# =========================
# RECONSTRUCT TIME SERIES
# =========================
records = []
global_index = 0

for barangay, group in df.groupby("barangay_psgc"):
    group = group.sort_values("date").reset_index(drop=True)
    max_index = len(group) - SEQ_LENGTH - horizon_days + 1

    for i in range(max_index):
        target_date = group.loc[i + SEQ_LENGTH + horizon_days - 1, "date"]

        records.append({
            "global_index": global_index,
            "barangay": barangay,
            "date": target_date,
            "y_true": y[global_index]
        })

        global_index += 1

df_plot = pd.DataFrame(records)

# Keep only test set
df_plot = df_plot[df_plot["global_index"] >= split_index].copy()

# Attach predictions
df_plot["test_index"] = df_plot["global_index"] - split_index
df_plot["y_pred"] = df_plot["test_index"].apply(lambda i: y_pred[int(i)])

# Select top 3 active barangays
activity = df_plot.groupby("barangay")["y_true"].sum().sort_values(ascending=False)
top_barangays = activity.head(3).index.tolist()

df_plot = df_plot[df_plot["barangay"].isin(top_barangays)].copy()

# Keep only zoomed date range
df_plot = df_plot[(df_plot["date"] >= XMIN) & (df_plot["date"] <= XMAX)].copy()

print("Top barangays:", top_barangays)

# =========================
# PLOT
# =========================
fig, axes = plt.subplots(
    nrows=len(top_barangays),
    ncols=1,
    figsize=(12, 8),
    sharex=True,
    facecolor="white"
)

if len(top_barangays) == 1:
    axes = [axes]

actual_colors = plt.cm.plasma(np.linspace(0.2, 0.7, len(top_barangays)))
pred_colors = plt.cm.plasma(np.linspace(0.5, 0.95, len(top_barangays)))

for ax, brgy, actual_color, pred_color in zip(axes, top_barangays, actual_colors, pred_colors):
    sub = df_plot[df_plot["barangay"] == brgy].sort_values("date")

    print(f"\nBarangay {brgy}")
    print(sub.loc[(sub["y_true"] > 0) | (sub["y_pred"] > 0.01), ["date", "y_true", "y_pred"]].head(20))

    ax.plot(
        sub["date"], sub["y_true"],
        color=actual_color,
        linewidth=1.6,
        linestyle="solid",
        marker="o",
        markersize=4,
        label="Actual"
    )

    ax.plot(
        sub["date"], sub["y_pred"],
        color=pred_color,
        linewidth=1.8,
        linestyle="dashed",
        alpha=0.95,
        label="Predicted"
    )

    # Vertical lines only for actual spike dates
    spikes = sub[sub["y_true"] > 0]
    ax.vlines(
        spikes["date"], 0, spikes["y_true"],
        color="black",
        alpha=0.3,
        linewidth=1
    )

    ax.set_ylabel("Count")
    ax.set_title(f"Barangay {brgy}", fontsize=10)
    ax.grid(alpha=0.25)
    ax.legend(loc="upper right", fontsize=8)
    ax.set_xlim(XMIN, XMAX)
    ax.set_ylim(bottom=0)
    ax.yaxis.set_major_locator(plt.MaxNLocator(integer=True))

    # Monthly ticks
    ax.xaxis.set_major_locator(mdates.MonthLocator(interval=1))
    ax.xaxis.set_major_formatter(mdates.DateFormatter("%b %Y"))

    print(sub["y_true"].corr(sub["y_pred"]))

axes[-1].set_xlabel("Date")

fig.suptitle(
    "Predicted vs Actual Snake Encounter Intensity in Selected Barangays",
    fontsize=16
)

plt.setp(axes[-1].xaxis.get_majorticklabels(), rotation=45, ha="right")
plt.tight_layout(rect=[0, 0, 1, 0.96])

os.makedirs("../plots", exist_ok=True)
plt.savefig("../plots/pred_vs_actual_zoomed.png", dpi=300, facecolor="white")
plt.show()
