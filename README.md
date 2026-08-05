# GEE EVS Mapper

A Python CLI tool powered by Google Earth Engine to query, superimpose, and export vector and satellite maps of protected areas within administrative boundaries.

---

## Prerequisites

- Python 3.10 or higher
- A Google account
- Git

---

## First-Time Setup Guide for New Users

### Step 1: Register for Google Earth Engine

1. Go to the [Google Earth Engine Code Editor](https://code.earthengine.google.com/).
2. Log in with your Google account.
3. If prompted to register, select **Unpaid / Non-Commercial** usage (e.g., Academic / Student).
4. Fill out the registration form with your institutional details and accept the terms of service.

### Step 2: Create or Select a Google Cloud Project

1. Open the [Google Cloud Console](https://console.cloud.google.com/).
2. Create a new project or select an existing one.
3. Note your **Project ID** (for example, `my-evs-project-12345`).
4. Enable the Google Earth Engine API for your project by visiting:
   `https://console.developers.google.com/apis/api/earthengine.googleapis.com/overview?project=YOUR_PROJECT_ID`
   Replace `YOUR_PROJECT_ID` with your actual Project ID and click **Enable**.

### Step 3: Clone the Repository and Set Up Environment

1. Clone this repository:
   ```bash
   git clone [https://github.com/YOUR_USERNAME/gee-evs-mapper.git](https://github.com/YOUR_USERNAME/gee-evs-mapper.git)
   cd gee-evs-mapper
