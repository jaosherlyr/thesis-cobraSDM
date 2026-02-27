"""
Usage:
    just to get the list of unique barangays so the google api wont go crazy
"""

import pandas as pd

df = pd.read_csv("/Users/sjao/Development/thesis-cobraSDM/data/redistributed_counts.csv")

# Clean PSGC properly
df["barangay_psgc"] = (
    df["barangay_psgc"]
    .astype(float)
    .astype(int)
)

unique_psgc = sorted(df["barangay_psgc"].unique())

print("Total unique barangays:", len(unique_psgc))

# Generate JavaScript numeric list (NO QUOTES)
js_list = "var selectedPSGC = [\n"
js_list += ",\n".join([f"  {code}" for code in unique_psgc])
js_list += "\n];"

print(js_list)