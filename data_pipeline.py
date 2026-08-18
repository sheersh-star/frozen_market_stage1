"""
data_pipeline.py
-----------------
Builds data/processed/market_data.json for the dashboard.

Works out of the box with realistic mock data. As you gather real datasets,
drop them into data/raw/ using the filenames below — each loader checks for
its file first and only falls back to mock data if it isn't there yet. You
never have to touch this file just to switch a panel from mock to real.

Expected files in data/raw/ (all optional):

  1. ice_cream_production.csv
     Source: Kaggle "Monthly Ice Cream Sales Data (1972-2020)", which mirrors
     the FRED series IPN31152N (Industrial Production: Ice Cream & Frozen
     Dessert, NAICS 31152, index 2017=100). Real columns are literally
     DATE and VALUE — this loader looks for those first.
     -> powers the production/sales trend panel

  2. ice_cream_reviews.csv  (+ optional ice_cream_products.csv)
     Source: Kaggle "Ice Cream Dataset" (tysonpo) — scraped reviews for
     Ben & Jerry's, Häagen-Dazs, Breyers and Talenti, 1-5 star ratings.
     If you also save the companion products file, reviews get grouped by
     brand name instead of by raw product key.
     -> powers the brand & flavor sentiment panel

  3. usda_nutrition.json
     Source: USDA FoodData Central API (api.nal.usda.gov/fdc/v1/foods/search).
     Save the raw JSON response for a query like "ice cream" — see
     fetch_usda_data.py, which does this for you with one command.
     -> powers the nutrition panel

  4. sweetener_market.csv
     Source: USDA Farm Service Agency Sweetener Market Data (SMD), via
     data.gov / Ag Data Commons. These ship as regional .xls files —
     grab the "Ice Cream and Related Products" use-category file (or
     combine a few regions), and save it as CSV here. Real region names
     are: New England, Mid Atlantic, North Central, South, West, Puerto Rico.
     -> powers the regional commodity distribution panel

None of these need to be exact — the loaders match on several likely column
name variants (see _find_field). If a real file's columns don't match at
all, that panel just quietly keeps using mock data; check the console output
after running this script to see what loaded as real vs. mock.

Run:    python3 data_pipeline.py
Output: data/processed/market_data.json
"""

import csv
import json
import random
import datetime
from pathlib import Path

import synthesis

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_FILE = OUT_DIR / "market_data.json"

# Real region names used by USDA's Sweetener Market Data reports.
REAL_REGIONS = ["New England", "Mid Atlantic", "North Central", "South", "West", "Puerto Rico"]

# Set an integer here (e.g. 42) if you want reproducible mock data run-to-run.
MOCK_SEED = None


# ---------------------------------------------------------------------------
# helpers
# ---------------------------------------------------------------------------

def _find_field(row, aliases):
    """Case-insensitive lookup of the first matching column name in a CSV row dict."""
    lower_map = {k.lower().strip(): k for k in row.keys() if k}
    for alias in aliases:
        if alias.lower() in lower_map:
            return row[lower_map[alias.lower()]]
    return None


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _recent_month_range(n_months):
    """n_months of calendar-correct month starts, ending on the current month.

    Deliberately not `date + timedelta(days=i*30)`: repeated 30-day jumps
    drift away from real month boundaries (12 jumps = 360 days, not a year),
    so labels slowly desync from the months they claim to represent.
    """
    today = datetime.date.today()
    y, m = today.year, today.month
    months_back = []
    for _ in range(n_months):
        months_back.append(datetime.date(y, m, 1))
        m -= 1
        if m < 1:
            m = 12
            y -= 1
    return list(reversed(months_back))


def _extract_nutrients(food_nutrients):
    """FoodData Central has returned nutrients in two different shapes
    depending on endpoint/version — a flat one (nutrientName/value) and a
    nested one (nutrient.name/amount). Handle both rather than guess.
    """
    out = {}
    for n in food_nutrients:
        nested = n.get("nutrient")
        if isinstance(nested, dict):
            name = nested.get("name", "")
            value = n.get("amount")
        else:
            name = n.get("nutrientName", "")
            value = n.get("value")
        if name:
            out[name] = value
    return out


# ---------------------------------------------------------------------------
# 1. production / sales trend
# ---------------------------------------------------------------------------

def load_sales_trend():
    real_file = RAW_DIR / "ice_cream_production.csv"
    if real_file.exists():
        rows = _read_csv(real_file)
        out = []
        for row in rows:
            date_raw = _find_field(row, ["date", "month"])
            value_raw = _find_field(row, ["value", "ipn31152n", "production", "units_sold"])
            if not date_raw or value_raw is None:
                continue
            try:
                d = datetime.datetime.strptime(str(date_raw)[:7], "%Y-%m")
                value = float(value_raw)
            except ValueError:
                continue
            out.append({"date": d.strftime("%Y-%m"), "value": round(value, 2)})
        if out:
            out.sort(key=lambda r: r["date"])
            return {"source": "real", "unit": "index (2017=100)", "series": out}

    # ---- fallback: mock data, seasonal, correct month math, index-like scale ----
    series = []
    for d in _recent_month_range(24):
        seasonality = 1.5 if d.month in (6, 7, 8) else (0.7 if d.month in (12, 1, 2) else 1.0)
        value = round(random.uniform(85, 115) * seasonality, 2)
        series.append({"date": d.strftime("%Y-%m"), "value": value})
    return {"source": "mock", "unit": "index (2017=100)", "series": series}


# ---------------------------------------------------------------------------
# 2. brand & flavor sentiment
# ---------------------------------------------------------------------------

def load_brand_sentiment():
    reviews_file = RAW_DIR / "ice_cream_reviews.csv"
    products_file = RAW_DIR / "ice_cream_products.csv"

    if reviews_file.exists():
        reviews = _read_csv(reviews_file)
        products_by_key = {}
        if products_file.exists():
            for p in _read_csv(products_file):
                key = _find_field(p, ["key", "id"])
                if key:
                    products_by_key[key] = p

        agg = {}
        for r in reviews:
            key = _find_field(r, ["key", "product_key", "id"])
            stars_raw = _find_field(r, ["stars", "rating"])
            if key is None or stars_raw is None:
                continue
            try:
                stars = float(stars_raw)
            except ValueError:
                continue
            brand = None
            product = products_by_key.get(key)
            if product:
                brand = _find_field(product, ["brand"]) or _find_field(product, ["name"])
            label = brand or key
            bucket = agg.setdefault(label, {"total": 0.0, "count": 0})
            bucket["total"] += stars
            bucket["count"] += 1

        if agg:
            out = []
            for label, b in agg.items():
                avg = b["total"] / b["count"]
                out.append({
                    "flavor": label,
                    "sentiment_score": round(avg, 2),
                    "mention_volume": b["count"],
                    "status": "Trending Up" if avg >= 4.3 else ("Declining" if avg < 3.8 else "Stable"),
                })
            out.sort(key=lambda x: -x["mention_volume"])
            return {"source": "real", "items": out[:12]}

    # ---- fallback mock ----
    flavors = ["Vanilla Bean", "Sea Salt Caramel", "Dark Chocolate", "Mint Chip", "Mango Passion", "Cookie Dough"]
    out = [
        {
            "flavor": f,
            "sentiment_score": round(random.uniform(3.8, 4.9), 2),
            "mention_volume": random.randint(500, 3000),
            "status": random.choice(["Trending Up", "Stable", "Declining"]),
        }
        for f in flavors
    ]
    return {"source": "mock", "items": out}


# ---------------------------------------------------------------------------
# 3. nutrition profile (USDA FoodData Central)
# ---------------------------------------------------------------------------

def load_nutrition():
    real_file = RAW_DIR / "usda_nutrition.json"
    if real_file.exists():
        try:
            with open(real_file, encoding="utf-8") as f:
                payload = json.load(f)
        except (json.JSONDecodeError, OSError):
            payload = None

        if payload:
            foods = payload.get("foods", payload if isinstance(payload, list) else [])
            out = []
            for food in foods[:12]:
                nutrients = _extract_nutrients(food.get("foodNutrients", []))
                out.append({
                    "item": food.get("description", "Unknown item"),
                    "calories": nutrients.get("Energy"),
                    "sugar_g": nutrients.get("Sugars, total including NLEA") or nutrients.get("Total Sugars"),
                    "fat_g": nutrients.get("Total lipid (fat)"),
                    "protein_g": nutrients.get("Protein"),
                })
            out = [o for o in out if o["calories"] is not None or o["sugar_g"] is not None]
            if out:
                return {"source": "real", "items": out}

    # ---- fallback mock ----
    categories = ["Premium Ice Cream", "Gelato", "Sorbet", "Frozen Yogurt", "Plant-Based Dairy"]
    out = [
        {
            "item": c,
            "calories": random.randint(180, 320),
            "sugar_g": round(random.uniform(14, 26), 1),
            "fat_g": round(random.uniform(6, 18), 1),
            "protein_g": round(random.uniform(0.3, 5.5), 1),
        }
        for c in categories
    ]
    return {"source": "mock", "items": out}


# ---------------------------------------------------------------------------
# 4. regional sweetener / commodity distribution
# ---------------------------------------------------------------------------

def load_regional_distribution():
    real_file = RAW_DIR / "sweetener_market.csv"
    if real_file.exists():
        rows = _read_csv(real_file)
        agg = {}
        for row in rows:
            region = _find_field(row, ["region", "area"])
            volume_raw = _find_field(row, ["value", "volume", "deliveries", "short tons", "pounds"])
            if not region or volume_raw is None:
                continue
            try:
                volume = float(str(volume_raw).replace(",", ""))
            except ValueError:
                continue
            agg[region] = agg.get(region, 0) + volume

        if agg:
            total = sum(agg.values()) or 1
            out = [{"region": r, "share": round(v / total * 100, 1)} for r, v in agg.items()]
            out.sort(key=lambda x: -x["share"])
            return {"source": "real", "items": out}

    # ---- fallback mock, using the real SMD region names ----
    shares = [random.uniform(1, 10) for _ in REAL_REGIONS]
    total = sum(shares)
    out = [{"region": r, "share": round(s / total * 100, 1)} for r, s in zip(REAL_REGIONS, shares)]
    out.sort(key=lambda x: -x["share"])
    return {"source": "mock", "items": out}


# ---------------------------------------------------------------------------
# assemble + write
# ---------------------------------------------------------------------------

def generate_market_data():
    if MOCK_SEED is not None:
        random.seed(MOCK_SEED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    panels = {
        "sales_trend": load_sales_trend(),
        "brand_sentiment": load_brand_sentiment(),
        "nutrition": load_nutrition(),
        "regional_distribution": load_regional_distribution(),
    }

    payload = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **panels,
    }
    payload["synthesis"] = synthesis.generate_synthesis(payload, RAW_DIR)
    timeline = synthesis.generate_synthesis_timeline(RAW_DIR)
    if timeline:
        payload["synthesis_timeline"] = timeline

    with open(OUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    live_count = sum(1 for p in panels.values() if p["source"] == "real")
    print(f"market_data.json written to {OUT_FILE}  ({live_count}/4 panels on real data)")
    for name, p in panels.items():
        tag = "REAL" if p["source"] == "real" else "mock"
        print(f"  - {name:<22} {tag}")
    print(f"  - synthesis flags       {len(payload['synthesis']['flags'])}")
    if timeline:
        print(f"  - recent-cycles timeline  {len(timeline['months'])} months")
    else:
        print("  - recent-cycles timeline  not present (drop in the 3 recent-window CSVs to enable)")


if __name__ == "__main__":
    generate_market_data()
