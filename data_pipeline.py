"""
data_pipeline.py
-----------------
Builds data/processed/console_data.json for the dashboard.

Rebuilt from the ground up around a single subject — The Magnum Ice Cream
Company (TMICC) and the real ecosystem around it — rather than the earlier
generic "frozen dessert market" framing. Every panel here is either real
data or is simply absent from the output; the one exception is production
trend, which predates this rebuild and already had an honestly-labeled mock
fallback — kept because "absent panel" vs "clearly-labeled mock panel" is a
real design choice, not an oversight, and changing it wasn't part of what
was asked. Nutrition (which had the same mock fallback) was removed
entirely on 22 Sep 2026 in favor of load_innovation_signals() below.

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
# 2. Nutrition panel removed — see data/raw/README.md. The raw USDA dataset
# (data/raw/nutrition/usda_nutrition.json) is untouched on disk, just no
# longer loaded here; superseded by load_innovation_signals() below, which
# reframes the same question ("is the category getting more nutritious") as
# competitor intelligence rather than a raw nutrition-facts table.
# ---------------------------------------------------------------------------



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

    # Regional Adjusted EBITDA margins, FY2025 — same primary source, new file
    margins = []
    margins_file = RAW_DIR / "market" / "magnum_regional_margins_fy2025.csv"
    if margins_file.exists():
        for row in _read_csv(margins_file):
            try:
                margin = float(row["adjusted_ebitda_margin_pct"])
            except (KeyError, ValueError, TypeError):
                continue
            region = row.get("region")
            if not region:
                continue
            margins.append({
                "region": region,
                "adjusted_ebitda_margin_pct": margin,
                "confidence": row.get("confidence", "placeholder"),
                "basis": row.get("basis", ""),
            })
        margins.sort(key=lambda r: -r["adjusted_ebitda_margin_pct"])

    # H1 2026 results — bridges FY2025 (above) to the present
    h1_group = {}
    h1_file = RAW_DIR / "market" / "magnum_h1_2026.csv"
    if h1_file.exists():
        for row in _read_csv(h1_file):
            metric = row.get("metric")
            if not metric:
                continue
            try:
                value = float(row["value"])
            except (KeyError, ValueError, TypeError):
                continue
            h1_group[metric] = {
                "value": value, "unit": row.get("unit", ""),
                "confidence": row.get("confidence", "placeholder"), "basis": row.get("basis", ""),
            }

    h1_regional = []
    h1_regional_file = RAW_DIR / "market" / "magnum_h1_2026_regional.csv"
    if h1_regional_file.exists():
        for row in _read_csv(h1_regional_file):
            region = row.get("region")
            try:
                osg = float(row["osg_pct"])
                fy2025_comp = float(row["fy2025_osg_pct_for_comparison"])
            except (KeyError, ValueError, TypeError):
                continue
            if not region:
                continue
            h1_regional.append({
                "region": region, "osg_pct": osg, "fy2025_osg_pct": fy2025_comp,
                "confidence": row.get("confidence", "placeholder"), "basis": row.get("basis", ""),
            })
        h1_regional.sort(key=lambda r: -r["osg_pct"])

    # Share price snapshots — dated points, not a continuous series (no live
    # market-data feed here), each independently sourced and confidence-tagged
    share_price = []
    price_file = RAW_DIR / "market" / "magnum_share_price_snapshots.csv"
    if price_file.exists():
        for row in _read_csv(price_file):
            date = row.get("date")
            if not date:
                continue
            price = row.get("price_usd") or None
            mcap = row.get("market_cap_usd_billions") or None
            share_price.append({
                "date": date,
                "price_usd": float(price) if price else None,
                "market_cap_usd_billions": float(mcap) if mcap else None,
                "note": row.get("note", ""),
                "confidence": row.get("confidence", "placeholder"),
                "source": row.get("source", ""),
            })
        share_price.sort(key=lambda r: r["date"])

    return {
        "source": "real",
        "items": rows,
        "regions_fy2025": regions,
        "regional_margins_fy2025": margins,
        "h1_2026": h1_group,
        "h1_2026_regional": h1_regional,
        "share_price_snapshots": share_price,
    }


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


def load_strategic_commitments():
    real_file = RAW_DIR / "magnum_strategic_commitments.json"
    return _read_json(real_file) if real_file.exists() else None


def load_consultant_brief():
    """The one deliberately non-fact panel — analysis and judgment built on
    top of everything else, not TMICC's own disclosed position. Kept in its
    own file specifically so it can never be confused with a sourced fact."""
    real_file = RAW_DIR / "magnum_consultant_brief.json"
    return _read_json(real_file) if real_file.exists() else None


def load_innovation_signals():
    """Competitor better-for-you/nutrition-innovation intelligence — rendered
    inside the Ecosystem tab's Competitors section, not its own tab. See the
    file's own framing_note for why this replaced the old Nutrition panel."""
    real_file = RAW_DIR / "magnum_innovation_signals.json"
    return _read_json(real_file) if real_file.exists() else None


def load_annual_report_analysis():
    """A document-native read of TMICC's Annual Report (Form 20-F) — report
    map + dated strategic checkpoints, each with a page citation. Deliberately
    its own tab/file rather than merged into Strategy or Timeline."""
    real_file = RAW_DIR / "magnum_annual_report_analysis.json"
    return _read_json(real_file) if real_file.exists() else None


# ---------------------------------------------------------------------------
# assemble + write
# ---------------------------------------------------------------------------

def generate_market_data():
    if MOCK_SEED is not None:
        random.seed(MOCK_SEED)

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # sales_trend deliberately excluded from output for now — the full
    # 1991-present Eurostat series was too big/old/irrelevant as shown. The
    # loader function below is left in place, untouched, and the real data
    # at data/raw/production/ice_cream_production.csv is untouched too —
    # this is a "remove from view for now," not a deletion. Revisit with a
    # post-COVID-only cut (2020+) when that conversation happens.

    payload = {
        "last_updated": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
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

    strategy = load_strategic_commitments()
    if strategy:
        payload["strategic_commitments"] = strategy

    brief = load_consultant_brief()
    if brief:
        payload["consultant_brief"] = brief

    innovation = load_innovation_signals()
    if innovation:
        payload["innovation_signals"] = innovation

    annual_report = load_annual_report_analysis()
    if annual_report:
        payload["annual_report_analysis"] = annual_report

    with open(OUT_FILE, "w") as f:
        json.dump(payload, f, indent=2)

    print(f"console_data.json written to {OUT_FILE}")
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
    if strategy:
        print(f"  - strategic_commitments  {len(strategy.get('headline_commitments', []))} commitments, {len(strategy.get('cross_cutting_initiatives', []))} back-traced initiatives")
    else:
        print("  - strategic_commitments  not present (data/raw/magnum_strategic_commitments.json missing)")
    if brief:
        print(f"  - consultant_brief       {len(brief.get('top_gaps', []))} gaps, {len(brief.get('connected_dots', []))} connected dots, {len(brief.get('recommendations', []))} recommendations")
    else:
        print("  - consultant_brief       not present (data/raw/magnum_consultant_brief.json missing)")
    if innovation:
        print(f"  - innovation_signals     {len(innovation.get('named_competitor_launches', []))} competitor-launch entries (gap-labeled this pass)")
    else:
        print("  - innovation_signals     not present (data/raw/magnum_innovation_signals.json missing)")
    if annual_report:
        print(f"  - annual_report_analysis {len(annual_report.get('strategic_checkpoints', []))} strategic checkpoints")
    else:
        print("  - annual_report_analysis not present (data/raw/magnum_annual_report_analysis.json missing)")


if __name__ == "__main__":
    generate_market_data()
