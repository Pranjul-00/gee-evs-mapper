import argparse
import os
import sys
import ee
import requests

DEFAULT_PROJECT_ID = "gen-lang-client-0477327602"

def init_gee(project_id):
    try:
        ee.Initialize(project=project_id)
    except Exception as e:
        print(f"[!] Authentication/Initialization error: {e}")
        print("[!] Try running 'earthengine authenticate' first.")
        sys.exit(1)

def generate_vector_map(state_name, park_name):
    state_boundary = ee.FeatureCollection("FAO/GAUL_SIMPLIFIED_500m/2015/level1") \
        .filter(ee.Filter.eq('ADM1_NAME', state_name))

    if state_boundary.size().getInfo() == 0:
        print(f"[!] Error: State '{state_name}' not found in GAUL dataset.")
        sys.exit(1)

    # Filter park geometrically and by partial string match if provided
    protected_areas = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
        .filterBounds(state_boundary)

    if park_name:
        protected_areas = protected_areas.filter(ee.Filter.stringContains('NAME', park_name))

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

    if state_boundary.size().getInfo() == 0:
        print(f"[!] Error: State '{state_name}' not found in GAUL dataset.")
        sys.exit(1)

    protected_areas = ee.FeatureCollection("WCMC/WDPA/current/polygons") \
        .filterBounds(state_boundary)

    if park_name:
        protected_areas = protected_areas.filter(ee.Filter.stringContains('NAME', park_name))

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
        print(f"[û] Saved successfully to {filepath}")
    else:
        print(f"[!] Failed to download image. Status code: {response.status_code}")

def main():
    parser = argparse.ArgumentParser(description="Google Earth Engine EVS Map Generator")
    parser.add_argument("-s", "--state", type=str, help="Name of the State (e.g. Assam, Goa)")
    parser.add_argument("-p", "--park", type=str, help="Name of the National Park (optional)")
    parser.add_argument("-m", "--mode", choices=["vector", "satellite"], default="vector", help="Map mode: vector or satellite")
    parser.add_argument("-y", "--year", type=int, default=2023, help="Year for satellite imagery (default: 2023)")
    parser.add_argument("--project", type=str, default=DEFAULT_PROJECT_ID, help="Google Cloud Project ID")

    args = parser.parse_args()

    # Interactive prompt if arguments aren't supplied via CLI flags
    state_name = args.state or input("Enter State Name (e.g., Assam): ").strip()
    park_name = args.park if args.park is not None else input("Enter Park Name (press Enter to include all parks): ").strip()

    init_gee(args.project)

    print(f"\n[*] Processing {args.mode.upper()} map for state: '{state_name}' | park query: '{park_name or 'ALL'}'...")

    if args.mode == "vector":
        url = generate_vector_map(state_name, park_name)
    else:
        url = generate_satellite_map(state_name, park_name, args.year)

    sanitized_state = state_name.lower().replace(' ', '_')
    sanitized_park = (park_name.lower().replace(' ', '_') if park_name else "all_parks")
    filename = f"{sanitized_state}_{sanitized_park}_{args.mode}.png"

    download_image(url, filename)

if __name__ == "__main__":
    main()
