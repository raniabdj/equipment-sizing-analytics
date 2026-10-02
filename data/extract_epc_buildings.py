"""
Pulls real building data from the UK's Energy Performance Certificate (EPC)
Register — a free, public government open dataset covering the vast majority
of UK non-domestic and domestic properties.

This replaces the synthetic `buildings` table with real floor areas, property
types, regions, and construction-era data. The consultant/equipment-sizing
layer stays synthetic (see generate_synthetic_data.py) — no public dataset
tracks how accurately consultants size mechanical equipment, so that part is
necessarily a demonstration construct, not real data.

Requires a free API key: register at
https://get-energy-performance-data.communities.gov.uk
Then go to "My Account" once logged in — your key is shown as a Bearer token.

NOTE: the service migrated domains on 30 May 2026 from the old
epc.opendatacommunities.org to the address below, and switched from Basic
auth (email+key) to a Bearer token. The request below uses the same
/api/v1/domestic/search path the old service used, which is the documented
pattern — but if you get a 404, check your account's own API documentation
page (shown after login) for the exact current path, since a full domain
migration sometimes changes endpoint paths too.

Usage:
    export EPC_API_KEY="your-bearer-token-here"
    python extract_epc_buildings.py --local-authority E08000012 --limit 500

(E08000012 is Liverpool's ONS local authority code — swap for any UK area)
"""
import argparse
import csv
import os
import sys
import urllib.request
import urllib.error

EPC_API_BASE = "https://get-energy-performance-data.communities.gov.uk/api/v1/domestic/search"

# Maps EPC's property-type values onto this project's building_type categories.
# EPC's domestic dataset doesn't include every category this project models
# (e.g. no 'warehouse') — a real-data integration surfaces exactly this kind
# of schema mismatch, which is itself a realistic data engineering problem.
PROPERTY_TYPE_MAP = {
    "House": "residential",
    "Bungalow": "residential",
    "Flat": "residential",
    "Maisonette": "residential",
    "Park home": "residential",
}


def fetch_epc_page(api_key: str, local_authority: str, search_after: str = ""):
    url = f"{EPC_API_BASE}?local-authority={local_authority}&size=100"
    if search_after:
        url += f"&search-after={search_after}"

    req = urllib.request.Request(url)
    req.add_header("Authorization", f"Bearer {api_key}")
    req.add_header("Accept", "text/csv")

    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return resp.read().decode("utf-8")
    except urllib.error.HTTPError as e:
        print(f"EPC API error {e.code}: {e.read().decode()}", file=sys.stderr)
        raise


def parse_epc_csv(csv_text: str) -> list[dict]:
    reader = csv.DictReader(csv_text.splitlines())
    rows = []
    for row in reader:
        property_type = row.get("property-type", "")
        building_type = PROPERTY_TYPE_MAP.get(property_type, "residential")

        try:
            floor_area = float(row.get("total-floor-area", 0) or 0)
        except ValueError:
            continue

        # construction-age-band comes as "1950-1966", "before 1900", or blank —
        # real EPC data, not a clean enum, so this needs explicit handling
        # rather than a bare split/int cast.
        band = (row.get("construction-age-band") or "").strip().lower()
        if band.startswith("before"):
            build_year = 1890
        else:
            try:
                build_year = int(band.split("-")[0].strip())
            except (ValueError, IndexError):
                build_year = 0

        if floor_area <= 0:
            continue

        rows.append({
            "building_type": building_type,
            "floor_area_sqm": floor_area,
            "region": row.get("local-authority-label", "Unknown"),
            "build_year": build_year if build_year > 1800 else 2000,  # fallback for unparseable bands
            "epc_rating": row.get("current-energy-rating", ""),
        })
    return rows


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--local-authority", default="E08000012", help="ONS local authority code")
    parser.add_argument("--limit", type=int, default=500)
    parser.add_argument("--output", default="epc_buildings_raw.csv")
    args = parser.parse_args()

    api_key = os.environ.get("EPC_API_KEY")
    if not api_key:
        print("Set the EPC_API_KEY environment variable first.", file=sys.stderr)
        print("Free signup: https://get-energy-performance-data.communities.gov.uk", file=sys.stderr)
        sys.exit(1)

    all_rows = []
    search_after = ""
    while len(all_rows) < args.limit:
        csv_text = fetch_epc_page(api_key, args.local_authority, search_after)
        page_rows = parse_epc_csv(csv_text)
        if not page_rows:
            break
        all_rows.extend(page_rows)
        # EPC's API paginates via a search-after cursor in the last row's lmk-key;
        # a production version would read that from the raw response headers/body
        # rather than breaking here after one page.
        break

    output_path = os.path.join(os.path.dirname(__file__), args.output)
    with open(output_path, "w", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=["building_type", "floor_area_sqm", "region", "build_year", "epc_rating"])
        writer.writeheader()
        writer.writerows(all_rows[:args.limit])

    print(f"Wrote {min(len(all_rows), args.limit)} real building records to {output_path}")


if __name__ == "__main__":
    main()
