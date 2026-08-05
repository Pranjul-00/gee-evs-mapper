# -*- coding: utf-8 -*-
import argparse
import os
import sys

import ee
import questionary
import requests

DEFAULT_PROJECT_ID = "gen-lang-client-0477327602"

# A curated list of prominent Indian states for quick selection (plus a Custom option)
POPULAR_STATES = [
    "Assam", "Goa", "Gujarat", "Himachal Pradesh", "Karnataka",
    "Kerala", "Madhya Pradesh", "Maharashtra", "Rajasthan",
    "Tamil Nadu", "Uttarakhand", "Uttar Pradesh", "West Bengal",
    "Type a custom state name..."
]

def init_gee(project_id):
    try:
        ee.Initialize(project=project_id)
    except Exception as e:
        print(f"[!] Authentication/Initialization error: {e}")
        print("[!] Try running 'earthengine authenticate' first.")
        sys.exit(1)

def fetch_parks_in_state(state_name):
    """Queries GEE to fetch all protected area names inside the selected state."""
    print(f"[*] Fetching protected areas for '{state_name}' from GEE...")
    
    state_boundary = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level1") \
        .filter(ee.Filter.eq('ADM1_NAME', state_name))

    if state_boundary.size().getInfo() == 0:
        print(f"[!] Warning: State '{state_name}' not found in dataset.")
        return []

    # Get all protected area names overlapping the state geometry
    protected_areas = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
        .filterBounds(state_boundary)
    
    # Extract distinct park names
    names = protected_areas.aggregate_array('NAME').getInfo()
    
    # Clean up and deduplicate names
    unique_names = sorted(list(set([n for n in names if n])))
    return unique_names

def generate_vector_map(state_name, park_name):
    state_boundary = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level1") \
        .filter(ee.Filter.eq('ADM1_NAME', state_name))

    protected_areas = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
        .filterBounds(state_boundary)

    if park_name and park_name != "ALL PARKS":
        protected_areas = protected_areas.filter(ee.Filter.eq('NAME', park_name))

    canvas = ee.Image().byte()
    canvas = canvas.paint(featureCollection=protected_areas, color=2)
    canvas = canvas.paint(featureCollection=state_boundary, color=1, width=3)
    canvas = canvas.clip(state_boundary)

    url = canvas.getThumbURL({
        'palette': ['white', 'black', 'green'],
        'min': 0,
        'max': 2,
        'dimensions': 1200,
        'region': state_boundary.geometry().bounds()
    })
    return url

def generate_satellite_map(state_name, park_name, year):
    state_boundary = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level1") \
        .filter(ee.Filter.eq('ADM1_NAME', state_name))

    protected_areas = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
        .filterBounds(state_boundary)

    if park_name and park_name != "ALL PARKS":
        protected_areas = protected_areas.filter(ee.Filter.eq('NAME', park_name))

    start_date = f"{year}-01-01"
    end_date = f"{year}-12-31"

    satellite = ee.ImageCollection("COPERNICUS/S2_SR_HARMONIZED") \
        .filterBounds(state_boundary) \
        .filterDate(start_date, end_date) \
        .filter(ee.Filter.lt('CLOUDY_PIXEL_PERCENTAGE', 20)) \
        .median() \
        .clip(state_boundary)

    sat_vis = satellite.visualize(bands=['B4', 'B3', 'B2'], min=0, max=3000)

    park_overlay = ee.Image().byte().paint(featureCollection=protected_areas, color=1, width=3)
    park_vis = park_overlay.visualize(palette=['red'], opacity=1.0)

    state_overlay = ee.Image().byte().paint(featureCollection=state_boundary, color=1, width=3)
    state_vis = state_overlay.visualize(palette=['yellow'], opacity=1.0)

    final_map = sat_vis.blend(park_vis).blend(state_vis)

    url = final_map.getThumbURL({
        'dimensions': 1200,
        'region': state_boundary.geometry().bounds()
    })
    return url

def download_image(url, filename):
    os.makedirs("output", exist_ok=True)
    filepath = os.path.join("output", filename)
    print(f"[*] Fetching image from GEE...")
    response = requests.get(url)
    if response.status_code == 200:
        with open(filepath, 'wb') as f:
            f.write(response.content)
        print(f"[+] Saved successfully to {filepath}")
    else:
        print(f"[!] Failed to download image. Status code: {response.status_code}")

def run_interactive_menu():
    print("\n==========================================")
    print("   🌍 Google Earth Engine EVS Mapper      ")
    print("==========================================\n")
    
    # 1. Select State via Dropdown
    selected_state = questionary.select(
        "Select a State:",
        choices=POPULAR_STATES
    ).ask()

    if selected_state == "Type a custom state name..." or not selected_state:
        selected_state = questionary.text("Enter State Name:").ask().strip()

    # 2. Fetch Parks and Select via Dropdown
    parks = fetch_parks_in_state(selected_state)
    park_choices = ["ALL PARKS"] + parks

    selected_park = questionary.select(
        f"Select a Protected Area in {selected_state}:",
        choices=park_choices
    ).ask()

    # 3. Select Map Mode
    mode_choice = questionary.select(
        "Select Map Output Mode:",
        choices=[
            "Both Vector and Satellite Maps",
            "Vector Map Only (Schematic)",
            "Satellite Map Only (Sentinel-2)"
        ]
    ).ask()

    mode_map = {
        "Vector Map Only (Schematic)": "vector",
        "Satellite Map Only (Sentinel-2)": "satellite",
        "Both Vector and Satellite Maps": "both"
    }
    mode = mode_map[mode_choice]

    # 4. Optional Year Input
    year = 2023
    if mode in ["satellite", "both"]:
        year_str = questionary.text("Enter Year for Satellite Imagery:", default="2023").ask()
        if year_str.isdigit():
            year = int(year_str)

    return selected_state, selected_park, mode, year

def main():
    parser = argparse.ArgumentParser(description="Google Earth Engine EVS Map Generator")
    parser.add_argument("-s", "--state", type=str, help="Name of the State")
    parser.add_argument("-p", "--park", type=str, help="Name of the National Park")
    parser.add_argument("-m", "--mode", choices=["vector", "satellite", "both"], help="Map mode")
    parser.add_argument("-y", "--year", type=int, default=2023, help="Year for satellite imagery")
    parser.add_argument("--project", type=str, default=DEFAULT_PROJECT_ID, help="Google Cloud Project ID")

    args = parser.parse_args()

    init_gee(args.project)

    if not args.state:
        state_name, park_name, mode, year = run_interactive_menu()
    else:
        state_name = args.state
        park_name = args.park or "ALL PARKS"
        mode = args.mode or "both"
        year = args.year

    sanitized_state = state_name.lower().replace(' ', '_')
    sanitized_park = ("all_parks" if park_name == "ALL PARKS" else park_name.lower().replace(' ', '_'))

    # Process Vector Map
    if mode in ["vector", "both"]:
        print(f"\n[*] Generating VECTOR map for '{state_name}' ({park_name})...")
        vector_url = generate_vector_map(state_name, park_name)
        vector_filename = f"{sanitized_state}_{sanitized_park}_vector.png"
        download_image(vector_url, vector_filename)

    # Process Satellite Map
    if mode in ["satellite", "both"]:
        print(f"\n[*] Generating SATELLITE composite map for '{state_name}' ({year})...")
        sat_url = generate_satellite_map(state_name, park_name, year)
        sat_filename = f"{sanitized_state}_{sanitized_park}_satellite_{year}.png"
        download_image(sat_url, sat_filename)

    print("\n[+] Process complete! Outputs saved in output/")

if __name__ == "__main__":
    main()
