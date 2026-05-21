# plot_raw_daily_encounters.py

import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path

# =========================
# CONFIG
# =========================
INPUT_FILE = "../data/daily_counts.csv"
OUTPUT_DIR = "plots"
OUTPUT_FILE = "raw_daily_encounter_counts.png"

DATE_COL = "date"          # change if your date column has another name
COUNT_COL = "count"        # change if your count column has another name

# =========================
# LOAD DATA
# =========================
df = pd.read_csv(INPUT_FILE)

df[DATE_COL] = pd.to_datetime(df[DATE_COL])

# =========================
# AGGREGATE TOTAL DAILY SIGHTINGS
# across all barangays and species
# =========================
daily_total = (
    df.groupby(DATE_COL, as_index=False)[COUNT_COL]
    .sum()
    .sort_values(DATE_COL)
)

# Optional: force full date range from 2022-01-01 to 2026-01-31
full_dates = pd.DataFrame({
    DATE_COL: pd.date_range("2022-01-01", "2026-01-31", freq="D")
})

daily_total = full_dates.merge(daily_total, on=DATE_COL, how="left")
daily_total[COUNT_COL] = daily_total[COUNT_COL].fillna(0)

# =========================
# PLOT
# =========================
Path(OUTPUT_DIR).mkdir(exist_ok=True)

plt.figure(figsize=(12, 5))
plt.plot(daily_total[DATE_COL], daily_total[COUNT_COL], linewidth=1)

plt.title("Raw Daily Snake Encounter Counts, 2022–2026")
plt.xlabel("Date")
plt.ylabel("Total Daily Encounters")
plt.tight_layout()

output_path = Path(OUTPUT_DIR) / OUTPUT_FILE
plt.savefig(output_path, dpi=300, bbox_inches="tight")
plt.show()

print(f"Saved figure to: {output_path}")