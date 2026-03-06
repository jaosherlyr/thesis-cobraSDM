import pandas as pd
from itertools import combinations

# -----------------------------
# SETTINGS
# -----------------------------

species_list = [
    "Naja_philippinensis",
    "Naja_samarensis",
    "Ophiophagus_hannah"
]

horizon = "7day"  # use 7-day for spatial stability
threshold = 0.6

# -----------------------------
# LOAD DATA
# -----------------------------

data = {}

for sp in species_list:
    print(f"Loading {sp}...")
    
    df = pd.read_csv(f"outputs_multi/{sp}_{horizon}_HSI.csv")
    
    # Keep only high suitability
    high = df[df["HSI"] >= threshold]
    
    data[sp] = set(high["barangay_psgc"])
    
    print(f"High-suitability count: {len(data[sp])}")

# -----------------------------
# PAIRWISE OVERLAP
# -----------------------------

results = []

for sp1, sp2 in combinations(species_list, 2):
    
    overlap = data[sp1].intersection(data[sp2])
    overlap_count = len(overlap)
    
    results.append([
        f"{sp1} & {sp2}",
        overlap_count
    ])
    
    print(f"\nOverlap between {sp1} and {sp2}: {overlap_count}")

# -----------------------------
# TRIPLE OVERLAP
# -----------------------------

triple_overlap = set.intersection(*data.values())
triple_count = len(triple_overlap)

results.append([
    "All Three Species",
    triple_count
])

print("\nTriple Overlap:", triple_count)

# -----------------------------
# FINAL TABLE
# -----------------------------

df_results = pd.DataFrame(
    results,
    columns=["Species Combination", "Overlap Count"]
)

print("\nFinal Overlap Table:")
print(df_results)

df_results.to_csv("cross_species_overlap_summary.csv", index=False)