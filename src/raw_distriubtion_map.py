import pandas as pd
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
import os

OUTPUT_FOLDER = "../plots"

os.makedirs(OUTPUT_FOLDER, exist_ok=True)

# --- Load data ---
df = pd.read_csv("../data/daily_counts.csv")

# --- Convert date ---
df['date'] = pd.to_datetime(df['date'])

# --- Filter date range ---
start_date = "2022-01-01"
end_date = "2026-01-31"
df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

# --- Aggregate total counts per day ---
daily_total = df.groupby('date')['count'].sum().reset_index()

# --- Fill missing dates with 0 ---
full_dates = pd.date_range(start=start_date, end=end_date)
daily_total = daily_total.set_index('date').reindex(full_dates, fill_value=0)
daily_total = daily_total.rename_axis('date').reset_index()

# --- Plot ---
plt.figure(figsize=(12, 5), facecolor='white')

# Use plasma colormap
color = plt.cm.plasma(0.6)

# plt.plot(daily_total['date'], daily_total['count'], color=color, linewidth=1.5)
plt.plot(daily_total['date'], daily_total['count'], color=color, linewidth=1.5)
plt.fill_between(daily_total['date'], daily_total['count'], color=color, alpha=0.15)

# --- Axis formatting ---
plt.xlabel("Year")
plt.ylabel("Total Snake Encounters")
plt.title("Daily Snake Encounter Counts")

# Year ticks only
ax = plt.gca()
ax.xaxis.set_major_locator(mdates.YearLocator())
ax.xaxis.set_major_formatter(mdates.DateFormatter('%Y'))

plt.xticks(rotation=45)

# Clean grid
plt.grid(alpha=0.2)

plt.tight_layout()

# --- Save figure ---
plt.savefig(f"{OUTPUT_FOLDER}/snake_timeseries-final.png", dpi=300, facecolor='white')

plt.show()