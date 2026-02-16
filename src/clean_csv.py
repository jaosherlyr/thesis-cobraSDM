#!/usr/bin/env python3
"""
clean_sightings.py (FILTER MODE – FINAL CANONICAL)

Purpose:
- Drop invalid / out-of-range dates
- Drop empty / invalid locations
- Enforce YYYY/MM/DD date format
- Normalize Philippine locations
- NO new columns
"""

import sys
import re
import pandas as pd

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
START_DATE = pd.Timestamp("2000-01-01")
END_DATE = pd.Timestamp.today()

ISLAND_GROUPS = ["Luzon", "Visayas", "Mindanao"]
ZIP_PATTERN = re.compile(r"\b\d{4}\b")

SHORTCUTS = {
    # ── Cities / Places ──
    r"\bppc\b": "Puerto Princesa City",
    r"\bsjdm\b": "San Jose Del Monte",
    r"\bcdo\b": "Cagayan De Oro",
    r"\bcmu\b": "Central Mindanao University",

    # ── Provinces / Regions ──
    r"\bne\b|\bn\.e\b": "Nueva Ecija",
    r"\bddo\b": "Davao de Oro",
    r"\bdav\s?sur\b": "Davao Del Sur",
    r"\bdavao\s?or\b": "Davao Oriental",

    # ── Abbreviations / Normalization ──
    r"\bmt\.?\b": "Mountain",
    r"\bprov\.?\b": "Province",
    r"\bzambo\b": "Zamboanga",

    r"\b(cam\s?sur|camsur|cam\.?\s?sur)\b": "Camarines Sur",
    r"\bcam\s?norte\b": "Camarines Norte",
    r"\bsta\b\.?": "Santa",
    r"\bsto\b\.?": "Santo",
    r"\bmp\b\.?": "Mountain Province",
    r"\bzsp\b\.?": "Zamboanga Sibugay",
    r"\bzambo\.?\s?norte\b": "Zamboanga Del Norte",
    r"\bbrg[ya]\b\.?": "Barangay",
    r"\bdrt\b": "Dona Remedios Trinidad",
    r"\bst\b\.": "Saint",

    r"\bgov\s*gen(?:eral)?\b": "Governor Generoso",
    r"\bgen\s?tri\b": "General Trias",
    r"\bgen\b\.?": "General",

    r"\brnsat\b": "Rizal National School of Arts and Trades",
    r"\bgensan\s+conel\b": "Barangay Conel, General Santos",
    r"\bgensan\b": "General Santos",

    r"\b(nueva\s+)?vi[sz]caya\b": "Nueva Vizcaya",
}

CLARIFICATIONS = {
    r"\bnaval\b": "Naval, Santa Rosa, Laguna",
    r"\bcamp\s?1\b": "Camp 1, Tuba, Benguet",
    r"\bpio\s?v\.?\s?corpus\b": "Pio V. Corpuz",
}

# ─────────────────────────────────────────────
# LOCATION CLEANER
# ─────────────────────────────────────────────
def clean_location(loc: str) -> str:
    if not isinstance(loc, str):
        return ""

    loc = loc.strip()
    if loc in {"", "-", "."}:
        return ""

    # Normalize punctuation
    loc = loc.replace("..", "").replace(".", " ")
    loc = re.sub(r"\s+", " ", loc)

    # Remove noise words
    loc = re.sub(r"\btia\b", "", loc, flags=re.I)
    loc = re.sub(r"\bptpa\b", "", loc, flags=re.I)
    loc = re.sub(r"\bsdo\b", "", loc, flags=re.I)

    # Remove ALL existing Philippines (we re-add once)
    loc = re.sub(r"\bPhilippines\b", "", loc, flags=re.I)

    # Normalize "Province of X" → "X Province"
    loc = re.sub(
        r"\bprovince\s+of\s+([A-Za-z\s]+)",
        r"\1 Province",
        loc,
        flags=re.I
    )

    # Clarifications first
    for pat, rep in CLARIFICATIONS.items():
        if re.search(pat, loc, flags=re.I):
            loc = rep

    # Shortcuts
    for pat, rep in SHORTCUTS.items():
        loc = re.sub(pat, rep, loc, flags=re.I)

    # Extract ZIP
    zip_match = ZIP_PATTERN.search(loc)
    zip_code = zip_match.group(0) if zip_match else None
    if zip_code:
        loc = ZIP_PATTERN.sub("", loc)

    # City cleanup
    loc = re.sub(r"\b(city|cty)\s+", ", ", loc, flags=re.I)
    loc = re.sub(r"\b(city|cty)\b", "", loc, flags=re.I)

    # Extract island group
    island = None
    for ig in ISLAND_GROUPS:
        if re.search(rf"\b{ig}\b", loc, flags=re.I):
            island = ig
            loc = re.sub(rf"\b{ig}\b", "", loc, flags=re.I)

    # Cleanup commas
    loc = re.sub(r"\s*,\s*", ", ", loc).strip(", ")

    # Rebuild canonical ending
    if island:
        loc = f"{loc}, {island}"

    loc = f"{loc}, Philippines"

    if zip_code:
        loc = f"{loc} {zip_code}"

    loc = re.sub(r"\s+,", ",", loc)
    loc = re.sub(r"\s+", " ", loc).strip(", ")

    return loc


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────
def main(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    print(f"📥 Rows loaded: {len(df)}")

    REQUIRED_COLS = ["date", "species", "location"]
    missing = [c for c in REQUIRED_COLS if c not in df.columns]
    if missing:
        raise ValueError(f"Missing required columns: {missing}")

    # ── DATE NORMALIZATION ──
    df["date"] = df["date"].astype(str)
    df["date"] = df["date"].str.replace(
        r"^(\d{4})-(\d{2})-(\d{2})$",
        r"\1/\2/\3",
        regex=True
    )

    parsed = pd.to_datetime(df["date"], errors="coerce")

    df = df[parsed.notna()]
    parsed = parsed[parsed.notna()]

    mask = (parsed >= START_DATE) & (parsed <= END_DATE)
    df = df[mask]
    parsed = parsed[mask]

    df["date"] = parsed.dt.strftime("%Y/%m/%d")

    # ── LOCATION CLEANING ──
    before = len(df)
    df["location"] = df["location"].apply(clean_location)
    df = df[df["location"] != ""]

    print(f"❌ Dropped invalid locations: {before - len(df)}")

    df = df.reset_index(drop=True)
    df.to_csv(output_csv, index=False)

    print(f"\n✅ Cleaned CSV saved to: {output_csv}")
    print(f"📊 Final rows: {len(df)}")


# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python clean_sightings.py input.csv output_cleaned.csv")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])