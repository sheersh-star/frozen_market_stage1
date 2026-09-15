"""
data_pipeline.py
-----------------
Builds data/processed/console_data.json for the dashboard.

Rebuilt from the ground up around a single subject — The Magnum Ice Cream
Company (TMICC) and the real ecosystem around it — rather than the earlier
generic "frozen dessert market" framing. Every panel here is either real
data or is simply absent from the output; there is no mock fallback left
except for the two panels below that predate this rebuild and already had
an honestly-labeled one (production trend, nutrition) — kept because
"absent panel" vs "clearly-labeled mock panel" is a real design choice, not
an oversight, and changing it wasn't part of what was asked.

Removed in this rebuild (see README.md and git history for the fuller
account of why each one was cut, and CHANGELOG-note below for a one-line
version):
  - The Executive Brief / synthesis.py: removed entirely, per instruction.
    The file itself is deleted, not just unused.
  - command_center.py and its three panels (Demand Signal, Regional
    Inventory Risk, Equipment Risk): removed. No real public dataset of a
    company's cold-chain telemetry exists — this was always acknowledged
    as illustrative-only in this project's own README, and "real data
    only" is the standing rule for this rebuild. File deleted.
  - Brand & Flavor Sentiment (US Kaggle sample), Consumer & Demographics
    (UK-launch-specific), Global Market Distribution (generic worldwide
    category share, not TMICC-specific), Company Revenue Comparison and
    Volume vs Dollar Sales (both mostly unsourced "placeholder" rows mixed
    with a little real data): all out of scope for a company-specific
    strategist tool. Their raw CSVs are left on disk, unused, as an
    honest archive of past research rather than deleted outright.

Added in this rebuild:
  - Live News Feed: reads data/raw/news/raw_items.json, produced by the
    separate fetch_competitor_news.py script (run that on a schedule; this
    pipeline only reads its output, same "one job per script" pattern as
    everything else here).
  - The Magnum Ecosystem: reads data/raw/magnum_ecosystem.json.
  - Correlated Timeline: reads data/raw/magnum_correlated_timeline.json.
  - TMICC Financial Performance: the old load_magnum_annual() logic,
    renamed and kept — it was already real, already TMICC-specific, and
    already exactly the kind of panel this rebuild is for.

Run:    python3 data_pipeline.py
Output: data/processed/console_data.json
"""

import csv
import json
import random
import datetime
from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_FILE = OUT_DIR / "console_data.json"

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


def _read_json(path):
    try:
        with open(path, encoding="utf-8") as f:
            return json.load(f)
    except (OSError, json.JSONDecodeError):
        return None


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
# 1. production / sales trend — industry-context backdrop (kept from before)
# ---------------------------------------------------------------------------

def load_sales_trend():
    real_file = RAW_DIR / "production" / "ice_cream_production.csv"
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
            return {"source": "real", "unit": "index (2021=100)", "series": out}

    # ---- fallback: mock data, seasonal, correct month math, index-like scale ----
    series = []
    for d in _recent_month_range(24):
        seasonality = 1.5 if d.month in (6, 7, 8) else (0.7 if d.month in (12, 1, 2) else 1.0)
        value = round(random.uniform(85, 115) * seasonality, 2)
        series.append({"date": d.strftime("%Y-%m"), "value": value})
    return {"source": "mock", "unit": "index (2021=100)", "series": series}


# ---------------------------------------------------------------------------
# 2. nutrition profile (USDA FoodData Central) — kept from before
# ---------------------------------------------------------------------------

UK_SUGAR_TRAFFIC_LIGHT_GREEN_MAX = 5.0
UK_SUGAR_TRAFFIC_LIGHT_AMBER_MAX = 22.5
WHO_FREE_SUGAR_10PCT_LIMIT_G = 50
WHO_FREE_SUGAR_5PCT_LIMIT_G = 25


def load_nutrition():
    real_file = RAW_DIR / "nutrition" / "usda_nutrition.json"
    payload = _read_json(real_file) if real_file.exists() else None

    if payload:
        foods = payload.get("foods", payload if isinstance(payload, list) else [])
        candidates = []
        seen_labels = set()
        for food in foods:
            raw_description = food.get("description") or ""
            if "ice cream" not in raw_description.lower():
                continue
            description = raw_description.title()
            brand = food.get("brandName") or food.get("brandOwner")
            if not brand:
                label = description
            elif brand.lower() in description.lower() or description.lower() in brand.lower():
                label = brand.title() if len(brand) >= len(description) else description
            else:
                label = f"{brand.title()} {description}"
            if label in seen_labels:
                continue
            nutrients = _extract_nutrients(food.get("foodNutrients", []))
            sugar_g = nutrients.get("Sugars, total including NLEA") or nutrients.get("Total Sugars")
            added_sugar_g = nutrients.get("Sugars, added")
            serving_size = food.get("servingSize")
            serving_unit = (food.get("servingSizeUnit") or "").lower()

            sugar_per_100g = None
            if sugar_g is not None and serving_size and serving_unit == "g":
                sugar_per_100g = sugar_g / serving_size * 100
            if sugar_per_100g is None:
                traffic_light = None
            elif sugar_per_100g <= UK_SUGAR_TRAFFIC_LIGHT_GREEN_MAX:
                traffic_light = "green"
            elif sugar_per_100g <= UK_SUGAR_TRAFFIC_LIGHT_AMBER_MAX:
                traffic_light = "amber"
            else:
                traffic_light = "red"

            item = {
                "item": label,
                "calories": nutrients.get("Energy"),
                "sugar_g": sugar_g,
                "fat_g": nutrients.get("Total lipid (fat)"),
                "protein_g": nutrients.get("Protein"),
                "sugar_per_100g": round(sugar_per_100g, 1) if sugar_per_100g is not None else None,
                "uk_traffic_light": traffic_light,
                "pct_of_who_10pct_limit": (
                    round(added_sugar_g / WHO_FREE_SUGAR_10PCT_LIMIT_G * 100) if added_sugar_g is not None else None
                ),
                "pct_of_who_5pct_limit": (
                    round(added_sugar_g / WHO_FREE_SUGAR_5PCT_LIMIT_G * 100) if added_sugar_g is not None else None
                ),
            }
            if item["calories"] is None and item["sugar_g"] is None:
                continue
            seen_labels.add(label)
            candidates.append(item)

        candidates.sort(key=lambda i: i["pct_of_who_10pct_limit"] is None)
        out = candidates[:12]
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
# 3. TMICC financial performance (real, company-specific)
# ---------------------------------------------------------------------------

def load_tmicc_financials():
    """Optional panel — reads magnum_icecream_annual.csv (+ optional
    magnum_regional_fy2025.csv) if present, else absent entirely. Public
    disclosure for this category only ever comes as annual volume-growth% /
    price-growth% splits (Unilever's Business Group reporting through
    FY2024, then TMICC's own standalone reporting from FY2025, after the
    2025-12-06 demerger) — never as absolute unit volumes or brand-level
    dollars. So instead of inventing absolute numbers, this compounds the
    disclosed annual growth rates into two indices (volume, price), each
    rebased to 100 the year before the first row.
    """
    real_file = RAW_DIR / "market" / "magnum_icecream_annual.csv"
    if not real_file.exists():
        return None

    rows = []
    for row in _read_csv(real_file):
        try:
            fy = int(row["fiscal_year"])
            usg = float(row["usg_pct"])
            volume_growth = float(row["volume_growth_pct"])
            price_growth = float(row["price_growth_pct"])
        except (KeyError, ValueError, TypeError):
            continue
        rows.append({
            "fiscal_year": fy,
            "usg_pct": usg,
            "volume_growth_pct": volume_growth,
            "price_growth_pct": price_growth,
            "confidence": row.get("confidence", "placeholder"),
            "basis": row.get("basis", ""),
        })

    if not rows:
        return None
    rows.sort(key=lambda r: r["fiscal_year"])

    volume_index = 100.0
    price_index = 100.0
    for r in rows:
        volume_index *= 1 + r["volume_growth_pct"] / 100
        price_index *= 1 + r["price_growth_pct"] / 100
        r["volume_index"] = round(volume_index, 1)
        r["price_index"] = round(price_index, 1)

    regions = []
    regional_file = RAW_DIR / "market" / "magnum_regional_fy2025.csv"
    if regional_file.exists():
        for row in _read_csv(regional_file):
            try:
                usg = float(row["usg_pct"])
            except (KeyError, ValueError, TypeError):
                continue
            region = row.get("region")
            if not region:
                continue
            regions.append({
                "region": region,
                "usg_pct": usg,
                "confidence": row.get("confidence", "placeholder"),
                "basis": row.get("basis", ""),
            })
        regions.sort(key=lambda r: -r["usg_pct"])

    return {"source": "real", "items": rows, "regions_fy2025": regions}


# ---------------------------------------------------------------------------
# 4. live news feed — pass-through from fetch_competitor_news.py's output
# ---------------------------------------------------------------------------

def load_news():
    real_file = RAW_DIR / "news" / "raw_items.json"
    payload = _read_json(real_file) if real_file.exists() else None
    if not payload:
        return None
    return payload


# ---------------------------------------------------------------------------
# 5. The Magnum Ecosystem — pass-through
# ---------------------------------------------------------------------------

def load_ecosystem():
    real_file = RAW_DIR / "magnum_ecosystem.json"
    return _read_json(real_file) if real_file.exists() else None


# ---------------------------------------------------------------------------
# 6. Correlated timeline — pass-through
# ---------------------------------------------------------------------------

def load_correlated_timeline():
    real_file = RAW_DIR / "magnum_correlated_timeline.json"
    return _read_json(real_file) if real_file.exists() else None


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
        "nutrition": load_nutrition(),
    }

    payload = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        **panels,
    }

    tmicc_financials = load_tmicc_financials()
    if tmicc_financials:
        payload["tmicc_financials"] = tmicc_financials

    news = load_news()
    if news:
        payload["news"] = news

    ecosystem = load_ecosystem()
    if ecosystem:
        payload["ecosystem"] = ecosystem

    timeline = load_correlated_timeline()
    if timeline:
        payload["correlated_timeline"] = timeline

    with open(OUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    live_count = sum(1 for p in panels.values() if p["source"] == "real")
    print(f"console_data.json written to {OUT_FILE}  ({live_count}/{len(panels)} core panels on real data)")
    for name, p in panels.items():
        tag = {"real": "REAL", "mock": "mock"}.get(p["source"], p["source"].upper())
        print(f"  - {name:<22} {tag}")
    if tmicc_financials:
        print(f"  - tmicc_financials       {len(tmicc_financials['items'])} fiscal years, {len(tmicc_financials.get('regions_fy2025', []))} regions")
    else:
        print("  - tmicc_financials       not present (drop in magnum_icecream_annual.csv to enable)")
    if news:
        print(f"  - news                   {len(news.get('items', []))} items")
    else:
        print("  - news                   not present (run fetch_competitor_news.py to enable)")
    if ecosystem:
        print(f"  - ecosystem              loaded ({ecosystem.get('generated_date', '?')})")
    else:
        print("  - ecosystem              not present (data/raw/magnum_ecosystem.json missing)")
    if timeline:
        print(f"  - correlated_timeline    {len(timeline.get('timeline', []))} events, {len(timeline.get('correlation_patterns', []))} patterns")
    else:
        print("  - correlated_timeline    not present (data/raw/magnum_correlated_timeline.json missing)")


if __name__ == "__main__":
    generate_market_data()
