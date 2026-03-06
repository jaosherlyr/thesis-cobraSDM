import pandas as pd

# ---------------------------
# SETTINGS
# ---------------------------

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizons = ["1day", "7day"]

threshold = 0.6  # High suitability threshold


# ---------------------------
# ANALYSIS
# ---------------------------

results = []

for sp in species_list:
    for hz in horizons:
        
        print(f"\nProcessing {sp} - {hz}...")
        
        # Load HSI file
        df = pd.read_csv(f"outputs_multi/{sp}_{hz}_HSI.csv")
        
        total_barangays = len(df)
        
        high = df[df["HSI"] >= threshold]
        high_count = len(high)
        
        percentage = (high_count / total_barangays) * 100
        
        results.append([
            sp,
            hz,
            total_barangays,
            high_count,
            percentage
        ])
        
        print("Total barangays:", total_barangays)
        print("High suitability (HSI ≥ 0.6):", high_count)
        print("Percentage:", percentage)


# ---------------------------
# FINAL TABLE
# ---------------------------

df_results = pd.DataFrame(
    results,
    columns=[
        "Species",
        "Forecast Horizon",
        "Total Barangays",
        "High Suitability (HSI ≥ 0.6)",
        "Percentage (%)"
    ]
)

print("\nFinal High-Suitability Summary:")
print(df_results)

# Optional: Save for thesis formatting
df_results.to_csv("high_suitability_summary.csv", index=False)