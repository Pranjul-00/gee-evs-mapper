# GEE EVS Mapper

A Python CLI tool powered by Google Earth Engine (GEE) to query, superimpose, and export high-resolution vector and satellite maps of protected areas (National Parks, Wildlife Sanctuaries) within regional administrative boundaries.

---

## Features

- **Interactive Selection Menus:** Searchable terminal dropdowns powered by `questionary` to select states and automatically fetch all protected areas inside them in real time.
- **Dual Map Modes:**
  - **Vector Mode:** High-contrast schematic maps with solid polygon fills (ideal for academic reports).
  - **Satellite Mode:** Sentinel-2 cloud-free RGB composite satellite overlays.
- **Automated Local Export:** Directly saves 1200px PNG map images to a local `output/` directory without needing the GEE web Code Editor.
- **CLI & Interactive Execution:** Run through guided prompts or pass fast command-line flags.
- **Resilient Network Handler:** Handles self-signed certificates and SSL inspection on university or institutional Wi-Fi networks.

---

## Prerequisites

- Python 3.10 or higher
- A Google account
- Git

---

## First-Time Setup Guide for New Users

### Step 1: Register for Google Earth Engine

1. Open the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Sign in with your Google account.
3. Select **Unpaid / Non-Commercial** usage (e.g., Academic / Student).
4. Fill out the registration form with your institution details and accept the terms of service.

### Step 2: Create and Enable a Google Cloud Project

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Note your **Project ID** (for example, `my-evs-project-12345`).
4. Enable the Google Earth Engine API by visiting:
   `https://console.developers.google.com/apis/api/earthengine.googleapis.com/overview?project=YOUR_PROJECT_ID`
   *(Replace `YOUR_PROJECT_ID` with your actual project ID and click **Enable**).*

### Step 3: Clone the Repository and Set Up Environment

1. Clone the repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/gee-evs-mapper.git](https://github.com/YOUR_USERNAME/gee-evs-mapper.git)
   cd gee-evs-mapper
   ```

2. Create and activate a Python virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate
   ```

3. Install the dependencies:
   ```bash
   pip install -r requirements.txt
   ```

### Step 4: Authenticate Your Machine

1. Run the Earth Engine CLI authorization command:
   ```bash
   earthengine authenticate
   ```
2. Follow the web link to log in with your registered Google account and authorize access.
3. Copy and paste the authorization token back into your terminal if prompted.

---

## Usage Guide

### Mode 1: Interactive Menu Mode (Recommended)

Run `main.py` without any arguments to trigger interactive terminal dropdowns:

```bash
python3 main.py
```

1. Use arrow keys or type to select a state (e.g., `Assam`, `Goa`, `Uttar Pradesh`).
2. The script will query GEE and render a second dropdown containing all protected areas inside that state.
3. Select a specific park (e.g., `Kaziranga`, `Dudhwa`) or choose `ALL PARKS`.
4. Select your map rendering mode (`Vector`, `Satellite`, or `Both`).

If you are using your own Google Cloud Project ID, pass the `--project` flag:
```bash
python3 main.py --project YOUR_PROJECT_ID
```

### Mode 2: Command Line Flag Mode

Bypass the interactive menu by providing command-line flags directly:

- **Generate a Vector map:**
  ```bash
  python3 main.py -s "Assam" -p "Kaziranga" -m vector
  ```

- **Generate a Satellite composite map for a specific year:**
  ```bash
  python3 main.py -s "Goa" -m satellite -y 2023
  ```

- **Generate both Vector and Satellite maps simultaneously:**
  ```bash
  python3 main.py -s "Uttarakhand" -p "Corbett" -m both
  ```

---

## Command Line Arguments

| Short Flag | Long Flag | Description | Default |
|---|---|---|---|
| `-s` | `--state` | Name of the target state | Interactive Prompt |
| `-p` | `--park` | Name of the national park | ALL PARKS |
| `-m` | `--mode` | Render mode (`vector`, `satellite`, `both`) | `both` |
| `-y` | `--year` | Year for Sentinel-2 satellite imagery | `2023` |
| | `--project` | Google Cloud Project ID | Default Configured ID |

---

## Troubleshooting

### SSL Certificate Verification Error (`SSLCertVerificationError`)
If you run the script on institutional or campus Wi-Fi networks, you may encounter an SSL error caused by network proxies or self-signed certificates.

**Fix:** The script is already configured with `verify=False` in the image download function to automatically bypass local SSL inspection and prevent crashes.

### Externally Managed Environment (`PEP 668`)
If installing packages with `pip` fails on Linux distributions like Ubuntu:
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

---

## Datasets Used

- **FAO GAUL (2015, Level 1):** Global Administrative Unit Layers for state and provincial boundaries.
- **UNEP-WCMC WDPA:** World Database on Protected Areas for national park polygons.
- **Copernicus Sentinel-2:** Level-2A Surface Reflectance satellite imagery composites.

---

## File Output Structure

All output PNG images are automatically named and saved into the `output/` directory:

```text
gee-evs-mapper/
ÃÄÄ output/
³   ÃÄÄ assam_kaziranga_vector.png
³   ÃÄÄ assam_kaziranga_satellite_2023.png
³   ÀÄÄ goa_nanda_lake_satellite_2023.png
ÃÄÄ main.py
ÃÄÄ requirements.txt
ÃÄÄ .gitignore
ÀÄÄ README.md
```
