#!/usr/bin/env python3
import os
import glob
import sys

# ==========================================
# CONFIGURATION (EDIT HERE)
# ==========================================

# Option 1: Explicit file list (in exact order you want)
input_files = [
    "data/env/Barangay_Daily_Env_2022_1.csv",
    "data/env/Barangay_Daily_Env_2022_2.csv",
    "data/env/Barangay_Daily_Env_2022_3.csv",
    "data/env/Barangay_Daily_Env_2022_4.csv",
    "data/env/Barangay_Daily_Env_2022_5.csv",
    "data/env/Barangay_Daily_Env_2022_6.csv",
    "data/env/Barangay_Daily_Env_2022_7.csv",
    "data/env/Barangay_Daily_Env_2022_8.csv",
    "data/env/Barangay_Daily_Env_2022_9.csv",
    "data/env/Barangay_Daily_Env_2022_10.csv",
    "data/env/Barangay_Daily_Env_2022_11.csv",
    "data/env/Barangay_Daily_Env_2022_12.csv",
    "data/env/Barangay_Daily_Env_2023_1.csv",
    "data/env/Barangay_Daily_Env_2023_2.csv",
    "data/env/Barangay_Daily_Env_2023_3.csv",
    "data/env/Barangay_Daily_Env_2023_4.csv",
    "data/env/Barangay_Daily_Env_2023_5.csv",
    "data/env/Barangay_Daily_Env_2023_6.csv",
    "data/env/Barangay_Daily_Env_2023_7.csv",
    "data/env/Barangay_Daily_Env_2023_8.csv",
    "data/env/Barangay_Daily_Env_2023_9.csv",
    "data/env/Barangay_Daily_Env_2023_10.csv",
    "data/env/Barangay_Daily_Env_2023_11.csv",
    "data/env/Barangay_Daily_Env_2023_12.csv",
    "data/env/Barangay_Daily_Env_2024_1.csv",
    "data/env/Barangay_Daily_Env_2024_2.csv",
    "data/env/Barangay_Daily_Env_2024_3.csv",
    "data/env/Barangay_Daily_Env_2024_4.csv",
    "data/env/Barangay_Daily_Env_2024_5.csv",
    "data/env/Barangay_Daily_Env_2024_6.csv",
    "data/env/Barangay_Daily_Env_2024_7.csv",
    "data/env/Barangay_Daily_Env_2024_8.csv",
    "data/env/Barangay_Daily_Env_2024_9.csv",
    "data/env/Barangay_Daily_Env_2024_10.csv",
    "data/env/Barangay_Daily_Env_2024_11.csv",
    "data/env/Barangay_Daily_Env_2024_12.csv",
    "data/env/Barangay_Daily_Env_2025_1.csv",
    "data/env/Barangay_Daily_Env_2025_2.csv",
    "data/env/Barangay_Daily_Env_2025_3.csv",
    "data/env/Barangay_Daily_Env_2025_4.csv",
    "data/env/Barangay_Daily_Env_2025_5.csv",
    "data/env/Barangay_Daily_Env_2025_6.csv",
    "data/env/Barangay_Daily_Env_2025_7.csv",
    "data/env/Barangay_Daily_Env_2025_8.csv",
    "data/env/Barangay_Daily_Env_2025_9.csv",
    "data/env/Barangay_Daily_Env_2025_10.csv",
    "data/env/Barangay_Daily_Env_2025_11.csv",
    "data/env/Barangay_Daily_Env_2025_12.csv",
    "data/env/Barangay_Daily_Env_2026_1.csv",
]

# Option 2: Folder mode (comment out input_files above if using this)
# input_folder = "/path/to/folder_containing_csvs"

output_file = "data/environmental_data.csv"

# ==========================================
# DO NOT EDIT BELOW
# ==========================================

def get_csv_files():
    if input_files:
        return input_files

    # If using folder mode
    if 'input_folder' in globals():
        files = sorted(glob.glob(os.path.join(input_folder, "*.csv")))
        return files

    print("No input files or folder defined.")
    sys.exit(1)


def merge_csv(files, output_path):
    if not files:
        print("No files found.")
        sys.exit(1)

    print("Merging in this order:")
    for f in files:
        print(" -", f)

    with open(output_path, "wb") as outfile:
        for i, file_path in enumerate(files):
            with open(file_path, "rb") as infile:
                if i == 0:
                    # Write entire first file (including header)
                    outfile.write(infile.read())
                else:
                    # Skip first line (header) safely
                    infile.readline()
                    outfile.write(infile.read())

    print(f"\nMerge complete → {output_path}")


if __name__ == "__main__":
    files = get_csv_files()
    merge_csv(files, output_file)