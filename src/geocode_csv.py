#!/usr/bin/env python3
"""
geocode_csv.py (robust, terminal-only failure reporting)

Usage:
    python geocode_csv.py input.csv output_geocoded.csv
"""

import sys
import time
import pandas as pd
from geopy.geocoders import Nominatim
from geopy.exc import GeocoderTimedOut, GeocoderServiceError

# ─────────────────────────────────────────────
# CONFIG
# ─────────────────────────────────────────────
LOCATION_COL = "location"
LAT_COL = "lat"
LON_COL = "long"

USER_AGENT = "cobra-sdm-thesis-geocoder"
REQUEST_DELAY = 1.5   # seconds (policy-safe)
TIMEOUT_SEC = 5       # hard timeout

# ─────────────────────────────────────────────
def safe_geocode(geolocator, query):
    """Geocode once, fail fast, no retries."""
    try:
        return geolocator.geocode(query, timeout=TIMEOUT_SEC)
    except (GeocoderTimedOut, GeocoderServiceError):
        return None
    except Exception:
        return None

# ─────────────────────────────────────────────
def main(input_csv, output_csv):
    df = pd.read_csv(input_csv)

    if LOCATION_COL not in df.columns:
        raise ValueError(f"Missing required column: '{LOCATION_COL}'")

    geolocator = Nominatim(user_agent=USER_AGENT)

    cache = {}
    lat_list = []
    lon_list = []
    failed = []

    print("🌍 Geocoding started (safe mode)…")

    for i, loc in enumerate(df[LOCATION_COL]):
        if not isinstance(loc, str) or not loc.strip():
            lat_list.append(None)
            lon_list.append(None)
            continue

        if loc in cache:
            lat, lon = cache[loc]
        else:
            result = safe_geocode(geolocator, loc)
            if result:
                lat, lon = result.latitude, result.longitude
            else:
                lat, lon = None, None
                failed.append(loc)

            cache[loc] = (lat, lon)
            time.sleep(REQUEST_DELAY)

        lat_list.append(lat)
        lon_list.append(lon)

        if (i + 1) % 10 == 0:
            print(f"  Processed {i + 1}/{len(df)}")

    df[LAT_COL] = lat_list
    df[LON_COL] = lon_list
    df.to_csv(output_csv, index=False)

    # ── SUMMARY ───────────────────────────────
    print("\n✅ Geocoding complete")
    print(f"📍 Output file: {output_csv}")
    print(f"📊 Total rows: {len(df)}")
    print(f"🧠 Cached unique locations: {len(cache)}")
    print(f"⚠️ Failed geocodes: {len(failed)}")

    if failed:
        print("\n❌ Locations that failed to geocode:")
        for loc in sorted(set(failed)):
            print(f"  - {loc}")

# ─────────────────────────────────────────────
if __name__ == "__main__":
    if len(sys.argv) != 3:
        print("Usage: python geocode_csv.py input.csv output_geocoded.csv")
        sys.exit(1)

    main(sys.argv[1], sys.argv[2])
