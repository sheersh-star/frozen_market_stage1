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
     Source: FRED series IPN31152N (Industrial Production: Ice Cream &
     Frozen Dessert, NAICS 31152, index 2017=100), pulled live from
     fred.stlouisfed.org/graph/fredgraph.csv?id=IPN31152N. Real columns are
     literally DATE and VALUE — this loader looks for those first. Re-pull
     periodically (curl works directly against that URL, no API key) to
     keep the trend panel current — the Fed publishes with roughly a
     2-week lag under the G.17 Industrial Production release.
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

  4. global_market_regions.csv
     Source: published third-party market-research sizing (e.g. Fortune
     Business Insights' Ice Cream Market Report) giving global share by
     continent. USDA's Sweetener Market Data (SMD) was the original real
     source for this panel's US-regional predecessor, but that program was
     discontinued around 2009-2010 — there is no current public version of
     it, which is why this panel is now global-continent market share
     instead. No central body measures worldwide ice cream sales directly,
     so every row here is confidence=grounded_estimate with its own basis
     citation, never "real" in the government/audited-disclosure sense.
     -> powers the global market distribution panel

None of these need to be exact — the loaders match on several likely column
name variants (see _find_field). Every optional panel (company revenue,
volume/dollar sales, Magnum precedent, command center) is simply absent
from the JSON if its file isn't there — check the console output after
running this script to see what's populated.

Run:    python3 data_pipeline.py
Output: data/processed/market_data.json
"""

import csv
import json
import random
import datetime
from pathlib import Path

import synthesis
import command_center

BASE_DIR = Path(__file__).resolve().parent
RAW_DIR = BASE_DIR / "data" / "raw"
OUT_DIR = BASE_DIR / "data" / "processed"
OUT_FILE = OUT_DIR / "market_data.json"

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
            seen_labels = set()
            for food in foods:
                description = (food.get("description") or "Unknown item").title()
                brand = food.get("brandName") or food.get("brandOwner")
                # Branded FoodData Central entries are overwhelmingly just
                # "ICE CREAM" — the brand is what actually distinguishes rows.
                if not brand:
                    label = description
                elif brand.lower() in description.lower() or description.lower() in brand.lower():
                    label = brand.title() if len(brand) >= len(description) else description
                else:
                    label = f"{brand.title()} {description}"
                if label in seen_labels:
                    continue
                nutrients = _extract_nutrients(food.get("foodNutrients", []))
                item = {
                    "item": label,
                    "calories": nutrients.get("Energy"),
                    "sugar_g": nutrients.get("Sugars, total including NLEA") or nutrients.get("Total Sugars"),
                    "fat_g": nutrients.get("Total lipid (fat)"),
                    "protein_g": nutrients.get("Protein"),
                }
                if item["calories"] is None and item["sugar_g"] is None:
                    continue
                seen_labels.add(label)
                out.append(item)
                if len(out) == 12:
                    break
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
# 4. global market distribution by region
# ---------------------------------------------------------------------------
#
# Previously sourced from USDA's Sweetener Market Data (SMD), whose 6
# US-only regions (New England, Mid Atlantic, ...) matched the file's real
# region taxonomy but whose values were hand-approximated, not a live pull —
# and the SMD program itself was discontinued around 2009-2010, so there is
# no current public version of that dataset regardless. Replaced with a
# global-continent market-share breakdown so the panel reflects worldwide
# distribution as requested, sourced from published third-party market
# research rather than a primary government/company disclosure — hence
# confidence is grounded_estimate throughout, not real (see basis per row).

def load_regional_distribution():
    real_file = RAW_DIR / "global_market_regions.csv"
    out = []
    if real_file.exists():
        for row in _read_csv(real_file):
            region = row.get("region")
            try:
                share = float(row["share_pct"])
            except (KeyError, ValueError, TypeError):
                continue
            if not region:
                continue
            out.append({
                "region": region,
                "share": share,
                "confidence": row.get("confidence", "placeholder"),
                "basis": row.get("basis", ""),
            })

    if not out:
        return {"source": "unavailable", "items": []}
    out.sort(key=lambda x: -x["share"])
    return {"source": "real", "items": out}


# ---------------------------------------------------------------------------
# 5. company revenue comparison (FY2025 vs FY2026)
# ---------------------------------------------------------------------------

def load_company_revenue():
    """Optional panel — reads company_revenue.csv if present, else the panel
    is simply absent (same graceful pattern as the synthesis timeline). Two
    rows per company (fiscal_year 2025 and 2026) are grouped into one record
    with a computed YoY delta and a confidence tier ("real" / "grounded_estimate"
    / "placeholder", from the CSV's `confidence` column) rather than the
    dashboard's usual binary real/mock badge — most of these companies never
    disclose ice-cream-specific revenue, so a three-way honesty signal matters
    more here than elsewhere.
    """
    real_file = RAW_DIR / "company_revenue.csv"
    if not real_file.exists():
        return None

    by_company = {}
    for row in _read_csv(real_file):
        company = row.get("company")
        try:
            fy = int(row["fiscal_year"])
            revenue = float(row["revenue_usd_millions"])
        except (KeyError, ValueError, TypeError):
            continue
        if not company or fy not in (2025, 2026):
            continue
        entry = by_company.setdefault(company, {
            "company": company,
            "ultimate_owner": row.get("ultimate_owner", ""),
            "scope": row.get("scope", ""),
        })
        entry[f"fy{fy}"] = revenue
        entry[f"confidence_{fy}"] = row.get("confidence", "placeholder")
        entry[f"basis_{fy}"] = row.get("basis", "")

    out = []
    for entry in by_company.values():
        fy2025, fy2026 = entry.get("fy2025"), entry.get("fy2026")
        if fy2025 is None or fy2026 is None:
            continue
        delta_pct = (fy2026 - fy2025) / fy2025 * 100 if fy2025 else None

        tiers = {entry.get("confidence_2025"), entry.get("confidence_2026")}
        if "real" in tiers:
            confidence = "real"
        elif "grounded_estimate" in tiers:
            confidence = "grounded_estimate"
        else:
            confidence = "placeholder"

        out.append({
            "company": entry["company"],
            "ultimate_owner": entry["ultimate_owner"],
            "scope": entry["scope"],
            "fy2025": round(fy2025, 1),
            "fy2026": round(fy2026, 1),
            "delta_pct": round(delta_pct, 1) if delta_pct is not None else None,
            "confidence": confidence,
            "basis_2025": entry.get("basis_2025", ""),
            "basis_2026": entry.get("basis_2026", ""),
        })

    if not out:
        return None
    out.sort(key=lambda x: -x["fy2026"])
    return {"source": "real", "items": out}


# ---------------------------------------------------------------------------
# 6. volume vs dollar sales
# ---------------------------------------------------------------------------

def load_volume_dollar_sales():
    """Optional panel — reads volume_dollar_sales.csv if present, else absent
    (same graceful pattern as the other add-on panels). Deliberately kept as
    two separate series rather than one dual-axis chart: volume (units) and
    dollar sales ($) are different scales, and a shared y-axis between them
    would fabricate a visual correlation that isn't really there. The front
    end renders them as two independent charts plus one indexed-to-100
    comparison, which is the honest way to show whether they're diverging.
    """
    real_file = RAW_DIR / "volume_dollar_sales.csv"
    if not real_file.exists():
        return None

    rows = []
    for row in _read_csv(real_file):
        try:
            volume = float(row["volume_units"])
            dollars = float(row["dollar_sales_usd"])
        except (KeyError, ValueError, TypeError):
            continue
        date = row.get("date")
        if not date:
            continue
        rows.append({
            "date": date,
            "volume_units": volume,
            "dollar_sales_usd": dollars,
            "confidence": row.get("confidence", "placeholder"),
        })

    if not rows:
        return None
    rows.sort(key=lambda r: r["date"])

    # Index both series to the first month = 100, so a divergence (e.g. unit
    # volume growing faster than dollar revenue — a price/promo signal) is
    # readable on one shared axis without mixing units.
    base_volume = rows[0]["volume_units"] or 1
    base_dollars = rows[0]["dollar_sales_usd"] or 1
    for r in rows:
        r["volume_index"] = round(r["volume_units"] / base_volume * 100, 1)
        r["dollar_index"] = round(r["dollar_sales_usd"] / base_dollars * 100, 1)

    return {"source": "real", "series": rows}


# ---------------------------------------------------------------------------
# 7. real-world precedent — Unilever Ice Cream / The Magnum Ice Cream Company
# ---------------------------------------------------------------------------

def load_magnum_annual():
    """Optional panel — reads magnum_icecream_annual.csv if present, else the
    panel is simply absent. Public disclosure for this category only ever
    comes as annual volume-growth% / price-growth% splits (Unilever's Business
    Group reporting through FY2024, then The Magnum Ice Cream Company's own
    standalone reporting from FY2025 on, after its 2025-12-06 demerger) —
    never as absolute unit volumes or brand-level dollars. So instead of
    inventing absolute numbers, this compounds the disclosed annual growth
    rates into two indices (volume, price), each rebased to 100 the year
    before the first row — the same indexed-comparison approach used for
    volume_dollar_sales.csv, applied to real, cited figures instead of
    illustrative ones. FY2023 is the real-world instance of the pattern that
    panel was built to demonstrate: volume -6.0%, price +8.8%.
    """
    real_file = RAW_DIR / "magnum_icecream_annual.csv"
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
    regional_file = RAW_DIR / "magnum_regional_fy2025.csv"
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
    revenue = load_company_revenue()
    if revenue:
        payload["company_revenue"] = revenue
    cc = command_center.build(RAW_DIR)
    if cc:
        payload["command_center"] = cc
    volume_dollar = load_volume_dollar_sales()
    if volume_dollar:
        payload["volume_dollar_sales"] = volume_dollar
    magnum_annual = load_magnum_annual()
    if magnum_annual:
        payload["magnum_real_precedent"] = magnum_annual

    with open(OUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    live_count = sum(1 for p in panels.values() if p["source"] == "real")
    print(f"market_data.json written to {OUT_FILE}  ({live_count}/4 panels on real data)")
    for name, p in panels.items():
        tag = {"real": "REAL", "mock": "mock"}.get(p["source"], p["source"].upper())
        print(f"  - {name:<22} {tag}")
    print(f"  - synthesis flags       {len(payload['synthesis']['flags'])}")
    if timeline:
        print(f"  - recent-cycles timeline  {len(timeline['months'])} months")
    else:
        print("  - recent-cycles timeline  retired (no current real source for the quarterly regional/brand recent-window data it needed)")
    if revenue:
        print(f"  - company revenue         {len(revenue['items'])} companies")
    else:
        print("  - company revenue         not present (drop in company_revenue.csv to enable)")
    if cc:
        print(f"  - command center          {len(cc['activity_log'])} log entries, {len(cc['equipment'])} equipment, {len(cc['regional_inventory'])} regions")
    else:
        print("  - command center          not present (drop in equipment_health.csv, regional_inventory.csv, demand_vs_plan.csv to enable)")
    if volume_dollar:
        print(f"  - volume vs dollar sales  {len(volume_dollar['series'])} months")
    else:
        print("  - volume vs dollar sales  not present (drop in volume_dollar_sales.csv to enable)")
    if magnum_annual:
        print(f"  - magnum real precedent   {len(magnum_annual['items'])} fiscal years")
    else:
        print("  - magnum real precedent   not present (drop in magnum_icecream_annual.csv to enable)")


if __name__ == "__main__":
    generate_market_data()
