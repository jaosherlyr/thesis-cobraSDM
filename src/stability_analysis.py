import pandas as pd

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

results = []

for sp in species_list:
    
    print(f"\nProcessing {sp}...")
    
    # Load 1-day and 7-day HSI outputs
    df_1 = pd.read_csv(f"outputs_multi/{sp}_1day_HSI.csv")
    df_7 = pd.read_csv(f"outputs_multi/{sp}_7day_HSI.csv")
    
    # Merge on barangay code
    merged = df_1.merge(
        df_7,
        on="barangay_psgc",
        suffixes=("_1day", "_7day")
    )
    
    # Compute Pearson correlation
    correlation = merged["HSI_1day"].corr(merged["HSI_7day"])
    
    # Compute mean difference (7-day minus 1-day)
    mean_diff = (merged["HSI_7day"] - merged["HSI_1day"]).mean()
    
    results.append([sp, correlation, mean_diff])
    
    print("Correlation:", correlation)
    print("Mean Difference:", mean_diff)

# Convert to table
df_results = pd.DataFrame(
    results,
    columns=[
        "Species",
        "Correlation (1-day vs 7-day HSI)",
        "Mean Difference (7-day - 1-day)"
    ]
)

print("\nFinal Stability Table:")
print(df_results)

# Optional: Save to CSV for thesis
df_results.to_csv("forecast_stability_results.csv", index=False)