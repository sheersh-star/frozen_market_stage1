"""
synthesis.py
------------
The fifth layer on top of the four descriptive panels: cross-references them
for signals a human might miss, ranks by materiality, and writes 2-3 flags
in plain English. Fully rule-based — no network calls, no API key, no cost.
Detection and prose generation both happen here in plain Python.

Dollar figures are attached only where they can be honestly anchored, and
every one carries a `basis` string plus `is_assumption` so the UI can label
it clearly.

  - Regional (sweetener_market.csv): DORMANT — this detector reads real
    quarter-over-quarter volume change from a US-regional file modeled on
    USDA's Sweetener Market Data, discontinued ~2009-2010. The file no
    longer ships in data/raw/, so detect_regional_signals() gracefully
    returns no candidates (see its docstring). Left in place rather than
    deleted in case a live regional-volume source turns up later.
  - Brand sentiment: illustrative-only — the reviewed *sample* volume times
    an assumed retail unit price, explicitly not a market-size claim.

The Production & Sales Trend panel is an index (2017=100), not a volume or
revenue figure, and no volume baseline has been supplied, so it is reported
as a %-change signal only, never dollarized.

Nutrition Profile has no natural margin story and isn't included here.
"""

import csv
import datetime
from pathlib import Path

# ---------------------------------------------------------------------------
# assumptions — labeled, easy to replace with real figures later
# ---------------------------------------------------------------------------

ASSUMPTIONS = {
    # midpoint of the $0.40-$0.50/lb range supplied for refined sugar
    "sugar_price_per_lb": 0.45,
    # midpoints of the supplied retail unit price ranges
    "retail_unit_price": {
        "premium_pint": 6.00,       # $5.50-$6.50 — name-brand pints
        "mass_market_tub": 4.00,    # $3.50-$4.50 — standard grocery tubs
        "impulse_single": 3.00,     # $2.50-$3.50 — bars/cones, single-serve
    },
    # supplied but unused today — no dairy-volume dataset yet to anchor it
    "milk_price_per_cwt": 20.00,
}

# Brand label (as load_brand_sentiment() emits it) -> retail price tier.
# Unmapped brands still get a % or score-based signal, just no dollar figure.
BRAND_TIER = {
    "Ben & Jerry's": "premium_pint",
    "Haagen-Dazs": "premium_pint",
    "Talenti": "premium_pint",
    "Van Leeuwen": "premium_pint",
    "Breyers": "mass_market_tub",
    "Store Brand": "mass_market_tub",
    "Blue Bell": "mass_market_tub",
    "Magnum": "impulse_single",
    "Klondike": "impulse_single",
}

REGIONAL_THRESHOLD_PCT = 10.0
TREND_THRESHOLD_PCT = 5.0
MIN_BRAND_SAMPLE = 15


# ---------------------------------------------------------------------------
# detectors — each returns a list of candidate signal dicts (may be empty)
# ---------------------------------------------------------------------------

def detect_regional_signals(raw_dir):
    """DORMANT — sweetener_market.csv doesn't ship anymore (see module
    docstring): it modeled USDA's Sweetener Market Data, discontinued
    ~2009-2010, and its US-regional shape doesn't match the global-continent
    data that replaced it for the main panel. Always returns [] until a live
    quarterly-cadence regional-volume source exists to read here instead.
    """
    path = Path(raw_dir) / "sweetener_market.csv"
    if not path.exists():
        return []

    by_region = {}
    with open(path, newline="", encoding="utf-8-sig") as f:
        for row in csv.DictReader(f):
            region = row.get("region")
            quarter = row.get("quarter")
            try:
                value = float(str(row.get("value", "")).replace(",", ""))
            except (TypeError, ValueError):
                continue
            if not region or not quarter:
                continue
            by_region.setdefault(region, {})[quarter] = value

    candidates = []
    for region, quarters in by_region.items():
        if len(quarters) < 2:
            continue
        ordered = sorted(quarters.items())  # "YYYY-Qn" sorts correctly
        (_, prior), (latest_q, latest) = ordered[-2], ordered[-1]
        if prior == 0:
            continue
        pct_change = (latest - prior) / prior * 100
        if abs(pct_change) < REGIONAL_THRESHOLD_PCT:
            continue
        delta_volume = latest - prior
        dollar = delta_volume * ASSUMPTIONS["sugar_price_per_lb"]
        candidates.append({
            "type": "regional",
            "region": region,
            "quarter": latest_q,
            "prior_volume": prior,
            "latest_volume": latest,
            "pct_change": pct_change,
            "dollar_estimate": {
                "amount_usd": dollar,
                "basis": (
                    f"real volume delta of {delta_volume:,.0f} lbs (assumed unit) "
                    f"x ${ASSUMPTIONS['sugar_price_per_lb']:.2f}/lb assumed sugar price "
                    "(midpoint of $0.40-$0.50/lb) - volume is real, price is an assumption"
                ),
                "is_assumption": True,
            },
        })

    candidates.sort(key=lambda c: abs(c["dollar_estimate"]["amount_usd"]), reverse=True)
    return candidates


def detect_trend_signal(market_data):
    """Index-based signal only - never dollarized (no volume/revenue anchor)."""
    series = (market_data.get("sales_trend") or {}).get("series") or []
    if len(series) < 2:
        return None

    latest, prior = series[-1], series[-2]
    if prior["value"] == 0:
        return None
    mom_pct = (latest["value"] - prior["value"]) / prior["value"] * 100
    if abs(mom_pct) < TREND_THRESHOLD_PCT:
        return None

    yoy_pct = None
    if len(series) >= 13:
        year_ago = series[-13]
        if year_ago["value"] != 0:
            yoy_pct = (latest["value"] - year_ago["value"]) / year_ago["value"] * 100

    return {
        "type": "trend",
        "latest_date": latest["date"],
        "latest_value": latest["value"],
        "mom_pct": mom_pct,
        "yoy_pct": yoy_pct,
        "dollar_estimate": None,
    }


def detect_brand_signals(market_data):
    """Point-in-time only - the reviews dataset has no date field, so a
    genuine multi-cycle trend claim isn't computable from today's schema.
    """
    items = (market_data.get("brand_sentiment") or {}).get("items") or []
    candidates = []
    for item in items:
        if item.get("status") not in ("Declining", "Trending Up"):
            continue
        if item.get("mention_volume", 0) < MIN_BRAND_SAMPLE:
            continue

        brand = item["flavor"]  # brand label, per load_brand_sentiment()
        tier = BRAND_TIER.get(brand)
        dollar_estimate = None
        if tier:
            price = ASSUMPTIONS["retail_unit_price"][tier]
            amount = price * item["mention_volume"]
            dollar_estimate = {
                "amount_usd": amount,
                "basis": (
                    f"{item['mention_volume']} sampled reviews x ${price:.2f} assumed "
                    f"{tier.replace('_', ' ')} unit price - illustrates this dataset's "
                    "reviewed sample only, not total market sales"
                ),
                "is_assumption": True,
            }

        candidates.append({
            "type": "brand",
            "brand": brand,
            "status": item["status"],
            "score": item["sentiment_score"],
            "mention_volume": item["mention_volume"],
            "dollar_estimate": dollar_estimate,
        })

    candidates.sort(key=lambda c: abs(c["score"] - 4.0), reverse=True)
    return candidates


# ---------------------------------------------------------------------------
# selection — diversity-first, not pure dollar-magnitude sorting
# ---------------------------------------------------------------------------
#
# Regional dollar figures are real-volume-anchored and naturally much larger
# than the deliberately sample-scoped, illustrative brand figures. Sorting
# every candidate by raw dollar size would let regional signals drown out
# brand signals every time - exactly the "three separate charts" outcome
# this layer exists to avoid. Instead: pick the strongest candidate from
# each panel type, bundle a brand-decline + regional-cost-increase pair into
# one cross-panel "margin story" flag when both are present (that always
# leads, since a cross-referenced story is the point), and otherwise order
# by how directly each remaining flag's dollar figure is anchored.

def _select_and_rank(regional_candidates, brand_candidates, trend_signal):
    best_regional = regional_candidates[0] if regional_candidates else None
    best_brand = brand_candidates[0] if brand_candidates else None

    bundle = None
    if (
        best_brand is not None
        and best_brand["status"] == "Declining"
        and best_regional is not None
        and best_regional["pct_change"] > 0  # a cost *increase*, not a decrease
    ):
        bundle = {"type": "bundle", "brand": best_brand, "regional": best_regional}
        best_regional = None
        best_brand = None

    ordered = []
    if bundle is not None:
        ordered.append(bundle)
    if best_regional is not None:
        ordered.append(best_regional)
    if best_brand is not None:
        ordered.append(best_brand)
    if trend_signal is not None:
        ordered.append(trend_signal)

    return ordered[:3]


# ---------------------------------------------------------------------------
# prose — plain Python templates, no LLM
# ---------------------------------------------------------------------------

def _fmt_usd(amount):
    sign = "-" if amount < 0 else ""
    return f"{sign}${abs(amount):,.0f}"


def _write_regional(signal):
    region = signal["region"]
    pct = signal["pct_change"]
    direction = "up" if pct > 0 else "down"
    dollar = signal["dollar_estimate"]["amount_usd"]
    cost_word = "incremental" if dollar > 0 else "reduced"
    headline = f"{region} sweetener costs {direction} {abs(pct):.1f}% QoQ"
    body = (
        f"{region} sweetener deliveries moved from {signal['prior_volume']:,.0f} to "
        f"{signal['latest_volume']:,.0f} lbs quarter-over-quarter ({direction} "
        f"{abs(pct):.1f}%), representing roughly {_fmt_usd(dollar)} in {cost_word} raw "
        f"sugar cost exposure at an assumed ${ASSUMPTIONS['sugar_price_per_lb']:.2f}/lb "
        "(midpoint of the $0.40-$0.50/lb range)."
    )
    return headline, body


def _write_brand(signal):
    brand = signal["brand"]
    status = signal["status"]
    score = signal["score"]
    volume = signal["mention_volume"]
    verb = "declining" if status == "Declining" else "trending up"
    headline = f"{brand} sentiment {verb}"
    body = (
        f"{brand} is currently {'the weakest' if status == 'Declining' else 'among the strongest'} "
        f"performer in this dataset's brand sentiment, averaging {score:.2f}/5 across "
        f"{volume} reviews sampled."
    )
    dollar_estimate = signal["dollar_estimate"]
    if dollar_estimate:
        body += (
            f" At an assumed unit price, that sample represents roughly "
            f"{_fmt_usd(dollar_estimate['amount_usd'])} of reviewed-unit retail value - "
            "illustrative of price-tier exposure in this sample, not total market sales."
        )
    return headline, body


def _write_trend(signal):
    direction = "up" if signal["mom_pct"] > 0 else "down"
    headline = f"Production index {direction} {abs(signal['mom_pct']):.1f}% MoM"
    body = (
        f"The production index reading for {signal['latest_date']} is "
        f"{signal['latest_value']:.1f} (2017=100), {direction} {abs(signal['mom_pct']):.1f}% "
        "versus the prior month"
    )
    if signal["yoy_pct"] is not None:
        yoy_dir = "up" if signal["yoy_pct"] > 0 else "down"
        body += f", and {yoy_dir} {abs(signal['yoy_pct']):.1f}% year-over-year"
    body += (
        ". This is an index-based signal - no revenue anchor has been supplied for this "
        "panel, so no dollar figure is attached."
    )
    return headline, body


def _write_bundle(signal):
    brand_s = signal["brand"]
    regional_s = signal["regional"]
    brand, region = brand_s["brand"], regional_s["region"]
    regional_dollar = regional_s["dollar_estimate"]["amount_usd"]
    headline = f"Margin pressure: {brand} softening while {region} costs rise"
    body = (
        f"{brand} is currently averaging {brand_s['score']:.2f}/5 across "
        f"{brand_s['mention_volume']} sampled reviews, while {region} - a sweetener-"
        f"delivery region - posted a {regional_s['pct_change']:.1f}% QoQ cost increase "
        f"(roughly {_fmt_usd(regional_dollar)} in assumed incremental sugar cost exposure "
        f"at ${ASSUMPTIONS['sugar_price_per_lb']:.2f}/lb). Together this is a margin story, "
        "not two separate charts: a softening brand and rising input costs in the same "
        "reporting cycle."
    )
    return headline, body


_WRITERS = {
    "regional": _write_regional,
    "brand": _write_brand,
    "trend": _write_trend,
    "bundle": _write_bundle,
}


# ---------------------------------------------------------------------------
# recommendations — small, staged, implementable next steps per signal
# ---------------------------------------------------------------------------
# Each observation gets 2-3 concrete stages (this week / this month / this
# quarter), grounded in the signal's own numbers rather than generic advice.
# These are suggestions sized for a category/ops team to actually act on,
# not strategy-deck language.

def _recommend_regional(signal):
    region = signal["region"]
    pct = signal["pct_change"]
    dollar = signal["dollar_estimate"]["amount_usd"]
    if pct > 0:
        return [
            {"stage": "This week", "action": (
                f"Check whether {region}'s sugar cost move is transient (spot-market "
                "blip) or structural (contract repricing) before reacting."
            )},
            {"stage": "This month", "action": (
                f"If structural, get a comparison quote from an alternate sweetener "
                f"supplier for {region}, or negotiate a volume-based rate to offset "
                f"the ~{_fmt_usd(dollar)} exposure."
            )},
            {"stage": "This quarter", "action": (
                f"If {region} repeats this move next cycle, reduce sourcing "
                "concentration there rather than absorbing the cost again."
            )},
        ]
    return [
        {"stage": "This week", "action": (
            f"Confirm {region}'s lower sweetener cost is durable, not a one-cycle dip."
        )},
        {"stage": "This month", "action": (
            f"If durable, lock in the lower rate with a forward contract for {region} "
            f"before it reverts."
        )},
        {"stage": "This quarter", "action": (
            f"Redirect the freed ~{_fmt_usd(abs(dollar))} toward the category's "
            "weakest-performing brand or region."
        )},
    ]


def _recommend_brand(signal):
    brand = signal["brand"]
    if signal["status"] == "Declining":
        return [
            {"stage": "This week", "action": (
                f"Pull {brand}'s lowest-scoring reviews and tag the top 2-3 recurring "
                "complaints (flavor, texture, price, availability)."
            )},
            {"stage": "This month", "action": (
                f"Run a targeted fix on {brand}'s weakest SKU - reformulation, price "
                "adjustment, or a promotion tied to the specific complaint, not "
                "the whole line."
            )},
            {"stage": "This quarter", "action": (
                f"If sentiment hasn't recovered, consider consolidating {brand} into "
                "a stronger sibling line rather than continuing to invest evenly."
            )},
        ]
    return [
        {"stage": "This week", "action": (
            f"Confirm {brand} has enough shelf/inventory support to capture the "
            "current demand rather than stocking out."
        )},
        {"stage": "This month", "action": (
            f"Increase {brand}'s promotional placement while sentiment is high - "
            "this is the cheapest window to convert attention into share."
        )},
        {"stage": "This quarter", "action": (
            f"Use {brand} as the anchor for a flavor-line extension or premium-tier "
            "push while it's outperforming."
        )},
    ]


def _recommend_trend(signal):
    if signal["mom_pct"] < 0:
        return [
            {"stage": "This week", "action": (
                "Check whether the drop matches the same month last year (seasonal) "
                "before treating it as a demand signal."
            )},
            {"stage": "This month", "action": (
                "If not seasonal, trim the next production run rather than building "
                "inventory against softening demand."
            )},
            {"stage": "This quarter", "action": (
                "Revisit the production plan if the decline persists for another cycle."
            )},
        ]
    return [
        {"stage": "This week", "action": (
            "Confirm current supply chain capacity can sustain this pace without "
            "rush freight or overtime costs eating the gain."
        )},
        {"stage": "This month", "action": (
            "Pre-book raw material volumes at current prices before sustained demand "
            "pulls input costs up."
        )},
        {"stage": "This quarter", "action": (
            "Evaluate a capacity increase only if the uptrend holds for another cycle."
        )},
    ]


def _recommend_bundle(signal):
    brand = signal["brand"]["brand"]
    region = signal["regional"]["region"]
    return [
        {"stage": "This week", "action": (
            f"Route {brand} and {region} to the same owner as one margin-risk ticket, "
            "not two separate category/procurement items."
        )},
        {"stage": "This month", "action": (
            f"Model a small price or pack-size adjustment on {brand} SKUs sourced from "
            f"{region} to absorb the cost increase without a full reformulation."
        )},
        {"stage": "This quarter", "action": (
            f"If both trends persist, evaluate resourcing {brand}'s {region}-linked "
            "SKUs from a lower-cost region rather than repeatedly repricing."
        )},
    ]


_RECOMMENDERS = {
    "regional": _recommend_regional,
    "brand": _recommend_brand,
    "trend": _recommend_trend,
    "bundle": _recommend_bundle,
}


def _materiality(signal):
    if signal["type"] == "bundle":
        brand_m = _materiality(signal["brand"])
        regional_m = _materiality(signal["regional"])
        return (brand_m + regional_m) * 1.5
    dollar = signal.get("dollar_estimate")
    if dollar:
        return abs(dollar["amount_usd"])
    if signal["type"] == "trend":
        return abs(signal["mom_pct"]) * 50  # documented heuristic, not a dollar-equivalent scale
    if signal["type"] == "brand":
        return abs(signal["score"] - 4.0) * 100
    return 0.0


def _signal_ids(signal):
    if signal["type"] == "bundle":
        return _signal_ids(signal["brand"]) + _signal_ids(signal["regional"])
    if signal["type"] == "regional":
        return [f"regional:{signal['region']}"]
    if signal["type"] == "brand":
        return [f"brand:{signal['brand']}"]
    if signal["type"] == "trend":
        return [f"trend:{signal['latest_date']}"]
    return []


def _rank_and_write(regional_candidates, brand_candidates, trend_signal):
    """Shared by the single-cycle brief and the per-month timeline: select,
    bundle, rank, and write flags from whatever candidates were detected.
    """
    ranked = _select_and_rank(regional_candidates, brand_candidates, trend_signal)

    flags = []
    for i, signal in enumerate(ranked):
        headline, body = _WRITERS[signal["type"]](signal)
        dollar_estimate = (
            signal["dollar_estimate"] if signal["type"] != "bundle"
            else signal["regional"]["dollar_estimate"]
        )
        flags.append({
            "rank": i + 1,
            "headline": headline,
            "body": body,
            "dollar_estimate": dollar_estimate,
            "materiality_score": round(_materiality(signal), 2),
            "signals_used": _signal_ids(signal),
            "recommendation": _RECOMMENDERS[signal["type"]](signal),
        })
    return flags


# ---------------------------------------------------------------------------
# entry point — single cycle
# ---------------------------------------------------------------------------

def generate_synthesis(market_data, raw_dir):
    regional_candidates = detect_regional_signals(raw_dir)
    brand_candidates = detect_brand_signals(market_data)
    trend_signal = detect_trend_signal(market_data)

    flags = _rank_and_write(regional_candidates, brand_candidates, trend_signal)

    return {
        "generated_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "mode": "rule-based",
        "flags": flags,
    }


# ---------------------------------------------------------------------------
# "Recent Cycles" timeline — one brief per month, interactive
# ---------------------------------------------------------------------------
#
# RETIRED (dormant, not deleted). generate_synthesis_timeline() requires
# three quarterly-granularity recent-window files, none of which have a
# current real source:
#   - ice_cream_production_recent.csv — superseded; ice_cream_production.csv
#     is now itself a live FRED pull, so no separate "recent" file is needed
#   - sweetener_market_recent.csv — same discontinued-USDA-SMD problem as
#     detect_regional_signals() above
#   - brand_sentiment_recent.csv — used entirely fictional brand names
#     (never real data to begin with)
# None of these three files ship in data/raw/ anymore, so this function
# gracefully returns None (its documented no-op behavior) and the front end
# hides the Recent Cycles / Full History toggle entirely. Left in place
# rather than deleted in case a real quarterly-cadence source for both
# regional volume and named-brand sentiment turns up later.
#
# Regional and brand figures are linearly interpolated between quarterly
# data points to fill in the months between — disclosed, not hidden: every
# month inside one quarter-to-quarter span moves along the same straight
# line, so it isn't an independent monthly measurement. The threshold used
# to flag a regional move is scaled down accordingly (a monthly step under
# linear interpolation is roughly one third of the quarterly move).

TIMELINE_REGIONAL_THRESHOLD_PCT = REGIONAL_THRESHOLD_PCT / 3


def _quarter_to_year_month(quarter_str):
    """'2024-Q3' -> (2024, 8) — the quarter's midpoint month, used as the
    interpolation anchor."""
    year_str, q_str = quarter_str.split("-Q")
    qnum = int(q_str)
    return int(year_str), (qnum - 1) * 3 + 2


def _quarter_bounds_year_month(quarter_str):
    """'2024-Q3' -> ((2024, 7), (2024, 9)) — first and last month in the quarter."""
    year_str, q_str = quarter_str.split("-Q")
    qnum = int(q_str)
    year = int(year_str)
    return (year, (qnum - 1) * 3 + 1), (year, (qnum - 1) * 3 + 3)


def _ym_to_index(year, month):
    return year * 12 + (month - 1)


def _index_to_ym(idx):
    year, month0 = divmod(idx, 12)
    return year, month0 + 1


def _month_to_quarter(date_str):
    """'2025-01' -> '2025-Q1'"""
    year, month = date_str.split("-")
    qnum = (int(month) - 1) // 3 + 1
    return f"{year}-Q{qnum}"


def interpolate_monthly(quarterly_points):
    """quarterly_points: [(quarter_str, value), ...], any order.

    Returns one entry per month spanning from the first quarter's first
    month to the last quarter's last month, linearly interpolated between
    quarter midpoints (held flat before the first / after the last anchor,
    never extrapolated). Each entry: {"date": "YYYY-MM", "value": float,
    "interpolated": bool} — interpolated is False only at the exact quarter
    midpoint anchors.
    """
    if not quarterly_points:
        return []

    pts = sorted(quarterly_points, key=lambda p: p[0])
    anchors = [(_ym_to_index(*_quarter_to_year_month(q)), v) for q, v in pts]

    start_ym, _ = _quarter_bounds_year_month(pts[0][0])
    _, end_ym = _quarter_bounds_year_month(pts[-1][0])
    start_idx = _ym_to_index(*start_ym)
    end_idx = _ym_to_index(*end_ym)

    out = []
    for idx in range(start_idx, end_idx + 1):
        year, month = _index_to_ym(idx)
        if idx <= anchors[0][0]:
            value, interpolated = anchors[0][1], idx != anchors[0][0]
        elif idx >= anchors[-1][0]:
            value, interpolated = anchors[-1][1], idx != anchors[-1][0]
        else:
            value, interpolated = None, None
            for (a_idx, a_val), (b_idx, b_val) in zip(anchors, anchors[1:]):
                if a_idx <= idx <= b_idx:
                    t = 0 if a_idx == b_idx else (idx - a_idx) / (b_idx - a_idx)
                    value = a_val + t * (b_val - a_val)
                    interpolated = idx not in (a_idx, b_idx)
                    break
        out.append({"date": f"{year:04d}-{month:02d}", "value": value, "interpolated": interpolated})
    return out


def _read_csv_rows(path):
    if not Path(path).exists():
        return None
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


def _read_recent_production(raw_dir):
    rows = _read_csv_rows(Path(raw_dir) / "ice_cream_production_recent.csv")
    if not rows:
        return None
    out = []
    for row in rows:
        try:
            d = datetime.datetime.strptime(str(row["DATE"])[:7], "%Y-%m")
            out.append({"date": d.strftime("%Y-%m"), "value": float(row["VALUE"])})
        except (KeyError, ValueError):
            continue
    out.sort(key=lambda r: r["date"])
    return out or None


def _read_recent_regional(raw_dir):
    rows = _read_csv_rows(Path(raw_dir) / "sweetener_market_recent.csv")
    if not rows:
        return None
    by_region = {}
    for row in rows:
        try:
            value = float(str(row["value"]).replace(",", ""))
        except (KeyError, ValueError):
            continue
        region, quarter = row.get("region"), row.get("quarter")
        if not region or not quarter:
            continue
        by_region.setdefault(region, []).append((quarter, value))
    return by_region or None


def _read_recent_brand(raw_dir):
    rows = _read_csv_rows(Path(raw_dir) / "brand_sentiment_recent.csv")
    if not rows:
        return None
    by_brand = {}
    for row in rows:
        try:
            score = float(row["avg_score"])
            count = int(float(row["review_count"]))
        except (KeyError, ValueError):
            continue
        brand, quarter = row.get("brand"), row.get("quarter")
        if not brand or not quarter:
            continue
        entry = by_brand.setdefault(brand, {"scores": [], "counts": {}})
        entry["scores"].append((quarter, score))
        entry["counts"][quarter] = count
    return by_brand or None


def generate_synthesis_timeline(raw_dir):
    """Returns None (graceful no-op) unless all three recent-window files
    are present, matching the rest of the pipeline's fallback style."""
    production = _read_recent_production(raw_dir)
    regional_raw = _read_recent_regional(raw_dir)
    brand_raw = _read_recent_brand(raw_dir)
    if not production or len(production) < 2 or not regional_raw or not brand_raw:
        return None

    regional_by_date = {
        region: {m["date"]: m for m in interpolate_monthly(points)}
        for region, points in regional_raw.items()
    }

    brand_by_date = {}
    for brand, data in brand_raw.items():
        months = interpolate_monthly(data["scores"])
        brand_by_date[brand] = {
            m["date"]: {
                "date": m["date"],
                "score": m["value"],
                "interpolated": m["interpolated"],
                "review_count": data["counts"].get(_month_to_quarter(m["date"]), 0),
            }
            for m in months
        }

    months_timeline = []
    for i in range(1, len(production)):
        date, prior_date = production[i]["date"], production[i - 1]["date"]

        trend_signal = None
        if production[i - 1]["value"] != 0:
            mom = (production[i]["value"] - production[i - 1]["value"]) / production[i - 1]["value"] * 100
            if abs(mom) >= TREND_THRESHOLD_PCT:
                trend_signal = {
                    "type": "trend", "latest_date": date, "latest_value": production[i]["value"],
                    "mom_pct": mom, "yoy_pct": None, "dollar_estimate": None,
                }

        regional_candidates = []
        for region, by_date in regional_by_date.items():
            cur, prev = by_date.get(date), by_date.get(prior_date)
            if not cur or not prev or prev["value"] == 0:
                continue
            pct = (cur["value"] - prev["value"]) / prev["value"] * 100
            if abs(pct) < TIMELINE_REGIONAL_THRESHOLD_PCT:
                continue
            delta = cur["value"] - prev["value"]
            dollar = delta * ASSUMPTIONS["sugar_price_per_lb"]
            regional_candidates.append({
                "type": "regional", "region": region, "quarter": date,
                "prior_volume": prev["value"], "latest_volume": cur["value"], "pct_change": pct,
                "dollar_estimate": {
                    "amount_usd": dollar,
                    "basis": (
                        f"interpolated monthly volume delta of {delta:,.0f} lbs (assumed unit; "
                        f"linearly interpolated between quarterly data points) x "
                        f"${ASSUMPTIONS['sugar_price_per_lb']:.2f}/lb assumed sugar price"
                    ),
                    "is_assumption": True,
                },
            })
        regional_candidates.sort(key=lambda c: abs(c["dollar_estimate"]["amount_usd"]), reverse=True)

        brand_candidates = []
        for brand, by_date in brand_by_date.items():
            cur = by_date.get(date)
            if not cur or cur["review_count"] < MIN_BRAND_SAMPLE:
                continue
            score = cur["score"]
            if score >= 4.3:
                status = "Trending Up"
            elif score < 3.8:
                status = "Declining"
            else:
                continue
            tier = BRAND_TIER.get(brand)
            dollar_estimate = None
            if tier:
                price = ASSUMPTIONS["retail_unit_price"][tier]
                amount = price * cur["review_count"]
                dollar_estimate = {
                    "amount_usd": amount,
                    "basis": (
                        f"{cur['review_count']} reviews (this quarter's aggregate, held flat "
                        f"across its 3 months) x ${price:.2f} assumed {tier.replace('_', ' ')} "
                        "unit price - illustrates the reviewed sample only"
                    ),
                    "is_assumption": True,
                }
            brand_candidates.append({
                "type": "brand", "brand": brand, "status": status, "score": score,
                "mention_volume": cur["review_count"], "dollar_estimate": dollar_estimate,
            })
        brand_candidates.sort(key=lambda c: abs(c["score"] - 4.0), reverse=True)

        flags = _rank_and_write(regional_candidates, brand_candidates, trend_signal)
        months_timeline.append({"date": date, "value": production[i]["value"], "flags": flags})

    return {
        "mode": "rule-based",
        "provenance": "illustrative recent window - not sourced from a real economic data release",
        "interpolation_note": (
            "Regional and brand figures are linearly interpolated between quarterly data "
            "points, not independently measured for each month."
        ),
        "months": months_timeline,
    }
