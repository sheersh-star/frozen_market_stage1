"""
fetch_usda_data.py
-------------------
Optional helper: pulls live nutrition data from USDA FoodData Central and
saves it to data/raw/usda_nutrition.json, ready for data_pipeline.py to pick
up on the next run.

Get a free API key at https://fdc.nal.usda.gov/api-key-signup — the shared
DEMO_KEY below works for light testing but is rate-limited, so swap in your
own key once you have one.

Run:
    python3 fetch_usda_data.py
    python3 fetch_usda_data.py "gelato"          # custom query
    USDA_API_KEY=your_key python3 fetch_usda_data.py "frozen yogurt"

Note: this script needs real internet access to api.nal.usda.gov, so it
wasn't run as part of building this project — double check it against your
own key before relying on it.
"""

import json
import os
import sys
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path

API_KEY = os.environ.get("USDA_API_KEY", "DEMO_KEY")
QUERY = sys.argv[1] if len(sys.argv) > 1 else "ice cream"
OUT_FILE = Path(__file__).resolve().parent / "data" / "raw" / "usda_nutrition.json"


def fetch():
    params = urllib.parse.urlencode({
        "api_key": API_KEY,
        "query": QUERY,
        "dataType": "Branded",
        "pageSize": 25,
    })
    url = f"https://api.nal.usda.gov/fdc/v1/foods/search?{params}"
    print(f"Fetching: {url.replace(API_KEY, '***')}")

    req = urllib.request.Request(url, headers={"User-Agent": "frozen-dessert-dashboard/1.0"})
    with urllib.request.urlopen(req, timeout=15) as resp:
        data = json.loads(resp.read().decode("utf-8"))

    OUT_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUT_FILE, "w") as f:
        json.dump(data, f, indent=2)

    print(f"Saved {len(data.get('foods', []))} items to {OUT_FILE}")
    print("Now run: python3 data_pipeline.py")


if __name__ == "__main__":
    try:
        fetch()
    except urllib.error.HTTPError as e:
        print(f"USDA API returned an error: {e.code} {e.reason}")
        if e.code == 429:
            print("You're likely rate-limited on DEMO_KEY — get a free key at "
                  "https://fdc.nal.usda.gov/api-key-signup and re-run with USDA_API_KEY set.")
    except urllib.error.URLError as e:
        print(f"Couldn't reach the USDA API: {e.reason}")
    except Exception as e:
        print(f"Fetch failed: {e}")
