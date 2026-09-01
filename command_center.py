"""
command_center.py
------------------
Supply chain command center: equipment risk, regional inventory risk,
demand-sensing gap detection, and a unified agent activity log.

The whole point of this module: every number is computed once and reused
everywhere it's displayed — the table recommendation, the log entry, and
the KPI totals all read from the same computation, so a table row and its
log entry can never contradict each other. That's the specific failure
mode this module exists to prevent (a mocked-up panel can show "expedite
14,000 units from region X" in a table while its own log shows a
different quantity from a different region, because a human typed the
two independently — here there is exactly one function that decides a
reallocation, and both the table and the log read its output).

This pipeline regenerates a fresh snapshot each run, not a continuously
running system with persisted history — so the activity log and KPIs are
"this cycle," not a faked "trailing 7 days."

This scenario is scoped to a hypothetical UK retail client — the 6
"regions" below are UK statistical/constituent-country regions (London,
South East, North West, Scotland, Wales, Northern Ireland), and dollar
figures are GBP throughout. As with the rest of the Command Center, this
is illustrative demo data (no public dataset of a real company's cold-chain
telemetry exists), not a real client's actual operational numbers.

Expected files in data/raw/ (all three required — see build() below):
  1. equipment_health.csv   (equipment_id, region, asset_type,
     failure_risk_pct, days_to_predicted_failure, units_at_risk,
     unit_cost_gbp, confidence, reading_date)
  2. regional_inventory.csv (region, weeks_on_hand, weeks_to_expiry,
     units_on_hand, unit_cost_gbp, confidence, snapshot_date)
  3. demand_vs_plan.csv     (region, date, sensed_demand_units,
     production_plan_units, event_note)
"""

import csv
from pathlib import Path

# ---------------------------------------------------------------------------
# thresholds & policy — documented, not magic numbers
# ---------------------------------------------------------------------------

STOCKOUT_WEEKS_ON_HAND = 2.0
SPOILAGE_WEEKS_TO_EXPIRY = 2.5
EQUIPMENT_HIGH_RISK_PCT = 50.0
DEMAND_GAP_THRESHOLD_PCT = 15.0

# Auto-execute policy: impact ceiling (GBP) AND confidence tier, combined,
# plus a hard carve-out — maintenance-dispatch actions always require human
# approval regardless of impact size, since dispatching a technician is a
# real-world action a business would want a human to sign off on.
AUTO_EXECUTE_MAX_IMPACT_GBP = 75000
AUTO_EXECUTE_CONFIDENCE_TIERS = {"real", "grounded_estimate"}
CONFIDENCE_RANK = {"placeholder": 0, "grounded_estimate": 1, "real": 2}


def _auto_execute(action_type, impact_gbp, confidence):
    if action_type == "maintenance_dispatch":
        return False
    if impact_gbp is not None and impact_gbp >= AUTO_EXECUTE_MAX_IMPACT_GBP:
        return False
    return confidence in AUTO_EXECUTE_CONFIDENCE_TIERS


def _weaker_confidence(a, b):
    return a if CONFIDENCE_RANK.get(a, 0) <= CONFIDENCE_RANK.get(b, 0) else b


def _read_csv(path):
    with open(path, newline="", encoding="utf-8-sig") as f:
        return list(csv.DictReader(f))


# ---------------------------------------------------------------------------
# 1. equipment risk
# ---------------------------------------------------------------------------

def compute_equipment_risk(raw_dir):
    path = Path(raw_dir) / "equipment_health.csv"
    if not path.exists():
        return None

    items = []
    for row in _read_csv(path):
        try:
            risk = float(row["failure_risk_pct"])
            days = int(float(row["days_to_predicted_failure"]))
            units = int(float(row["units_at_risk"]))
            unit_cost = float(row["unit_cost_gbp"])
        except (KeyError, ValueError):
            continue
        exposure_gbp = units * unit_cost
        items.append({
            "equipment_id": row["equipment_id"],
            "region": row["region"],
            "asset_type": row["asset_type"],
            "failure_risk_pct": risk,
            "days_to_predicted_failure": days,
            "units_at_risk": units,
            "unit_cost_gbp": unit_cost,
            "exposure_gbp": exposure_gbp,
            "exposure_basis": f"{units:,} units x £{unit_cost:.2f}/unit",
            "confidence": row.get("confidence", "placeholder"),
            "reading_date": row.get("reading_date"),
            "high_risk": risk >= EQUIPMENT_HIGH_RISK_PCT,
        })
    items.sort(key=lambda x: -x["failure_risk_pct"])
    return items


# ---------------------------------------------------------------------------
# 2. regional inventory risk + reallocation recommendation
# ---------------------------------------------------------------------------

def compute_regional_inventory(raw_dir):
    path = Path(raw_dir) / "regional_inventory.csv"
    if not path.exists():
        return None

    regions = []
    for row in _read_csv(path):
        try:
            weeks_on_hand = float(row["weeks_on_hand"])
            weeks_to_expiry = float(row["weeks_to_expiry"])
            units_on_hand = int(float(row["units_on_hand"]))
            unit_cost = float(row["unit_cost_gbp"])
        except (KeyError, ValueError):
            continue

        if weeks_on_hand < STOCKOUT_WEEKS_ON_HAND:
            status = "Stockout risk"
        elif weeks_to_expiry < SPOILAGE_WEEKS_TO_EXPIRY:
            status = "Spoilage risk"
        else:
            status = "Balanced"

        regions.append({
            "region": row["region"],
            "weeks_on_hand": weeks_on_hand,
            "weeks_to_expiry": weeks_to_expiry,
            "units_on_hand": units_on_hand,
            "unit_cost_gbp": unit_cost,
            "inventory_value_gbp": units_on_hand * unit_cost,
            "confidence": row.get("confidence", "placeholder"),
            "snapshot_date": row.get("snapshot_date"),
            "status": status,
            "recommendation": None,
            "recommendation_action": None,
        })

    # Reallocation matching: each stockout-risk region draws from whichever
    # surplus region can transfer the most units without dropping below its
    # own safe threshold. This single computation feeds both the table's
    # "recommendation" column and (if it clears the auto-execute policy)
    # the activity log entry — they read the same result, so they can't
    # end up naming different regions or quantities.
    donors = [r for r in regions if r["status"] != "Stockout risk"]
    for region in regions:
        if region["status"] == "Spoilage risk":
            region["recommendation"] = (
                f"Trigger regional promo — {region['units_on_hand']:,} units at risk before expiry"
            )
            continue
        if region["status"] == "Balanced":
            region["recommendation"] = "Monitor"
            continue

        # status == "Stockout risk"
        sell_through_per_week = (
            region["units_on_hand"] / region["weeks_on_hand"] if region["weeks_on_hand"] else 0
        )
        shortfall_weeks = STOCKOUT_WEEKS_ON_HAND - region["weeks_on_hand"]
        shortfall_units = round(shortfall_weeks * sell_through_per_week) or 1

        best_donor, best_transfer = None, 0
        for donor in donors:
            if donor["region"] == region["region"]:
                continue
            donor_surplus_weeks = donor["weeks_on_hand"] - STOCKOUT_WEEKS_ON_HAND
            if donor_surplus_weeks <= 0:
                continue
            donor_sell_through = (
                donor["units_on_hand"] / donor["weeks_on_hand"] if donor["weeks_on_hand"] else 0
            )
            donor_transferable = round(donor_surplus_weeks * donor_sell_through)
            if donor_transferable > best_transfer:
                best_transfer, best_donor = donor_transferable, donor

        if best_donor:
            transfer_units = min(shortfall_units, best_transfer)
            region["recommendation"] = f"Expedite {transfer_units:,} units from {best_donor['region']}"
            region["recommendation_action"] = {
                "type": "reallocation",
                "from_region": best_donor["region"],
                "to_region": region["region"],
                "units": transfer_units,
                "impact_gbp": transfer_units * region["unit_cost_gbp"],
                "confidence": _weaker_confidence(region["confidence"], best_donor["confidence"]),
            }
        else:
            region["recommendation"] = "No surplus region available to cover shortfall"

    regions.sort(key=lambda r: r["weeks_on_hand"])
    return regions


# ---------------------------------------------------------------------------
# 3. demand signal vs production plan
# ---------------------------------------------------------------------------

def compute_demand_signal(raw_dir):
    path = Path(raw_dir) / "demand_vs_plan.csv"
    if not path.exists():
        return None

    by_region = {}
    for row in _read_csv(path):
        try:
            sensed = int(float(row["sensed_demand_units"]))
            plan = int(float(row["production_plan_units"]))
        except (KeyError, ValueError):
            continue
        region = row["region"]
        by_region.setdefault(region, []).append({
            "date": row["date"],
            "sensed_demand_units": sensed,
            "production_plan_units": plan,
            "gap_units": sensed - plan,
            "gap_pct": (sensed - plan) / plan * 100 if plan else 0,
            "event_note": (row.get("event_note") or "").strip(),
        })
    if not by_region:
        return None

    for series in by_region.values():
        series.sort(key=lambda r: r["date"])

    # Feature whichever region had the largest gap anywhere in the window —
    # computed, never hardcoded. Deliberately NOT just the latest day: an
    # event (e.g. a heatwave-driven spike) can resolve back toward plan by
    # the end of the window, and the point of demand sensing is to surface
    # that it happened, not to miss it because today looks normal again.
    featured_region, featured_series, max_gap = None, None, -1
    for region, series in by_region.items():
        region_peak_gap = max(abs(p["gap_pct"]) for p in series)
        if region_peak_gap > max_gap:
            max_gap, featured_region, featured_series = region_peak_gap, region, series

    event_note = event_date = None
    for point in featured_series:
        if abs(point["gap_pct"]) >= DEMAND_GAP_THRESHOLD_PCT:
            event_date = point["date"]
            if point["event_note"]:
                event_note = point["event_note"]
                break

    return {
        "featured_region": featured_region,
        "gap_pct": round(max_gap, 1),
        "series": featured_series,
        "event_note": event_note,
        "event_date": event_date,
    }


# ---------------------------------------------------------------------------
# 4. unified activity log
# ---------------------------------------------------------------------------

def build_activity_log(equipment, regional):
    entries = []

    for eq in equipment or []:
        if not eq["high_risk"]:
            continue
        impact = eq["exposure_gbp"]
        auto = _auto_execute("maintenance_dispatch", impact, eq["confidence"])
        entries.append({
            "date": eq.get("reading_date"),
            "action": f"Flagged {eq['equipment_id']} ({eq['asset_type']}, {eq['region']}) for maintenance",
            "impact_gbp": impact,
            "impact_basis": eq["exposure_basis"],
            "status": "auto_executed" if auto else "pending_approval",
            "source": f"equipment:{eq['equipment_id']}",
        })

    for r in regional or []:
        if r["status"] == "Spoilage risk":
            impact = r["inventory_value_gbp"]
            auto = _auto_execute("promo", impact, r["confidence"])
            entries.append({
                "date": r.get("snapshot_date"),
                "action": (
                    f"{'Triggered' if auto else 'Recommended'} regional promo, {r['region']} "
                    f"({r['units_on_hand']:,} units at risk)"
                ),
                "impact_gbp": impact,
                "impact_basis": f"{r['units_on_hand']:,} units x £{r['unit_cost_gbp']:.2f}/unit",
                "status": "auto_executed" if auto else "pending_approval",
                "source": f"regional:{r['region']}",
            })

        action = r.get("recommendation_action")
        if action:
            impact = action["impact_gbp"]
            auto = _auto_execute(action["type"], impact, action["confidence"])
            verb = "Reallocated" if auto else "Recommended: expedite"
            entries.append({
                "date": r.get("snapshot_date"),
                "action": f"{verb} {action['units']:,} units, {action['from_region']} to {action['to_region']}",
                "impact_gbp": impact,
                "impact_basis": f"{action['units']:,} units x £{r['unit_cost_gbp']:.2f}/unit",
                "status": "auto_executed" if auto else "pending_approval",
                "source": f"regional:{action['to_region']}",
            })

    entries.sort(key=lambda e: -(e["impact_gbp"] or 0))
    return entries


# ---------------------------------------------------------------------------
# 5. KPI aggregation
# ---------------------------------------------------------------------------

def compute_kpis(equipment, regional, activity_log):
    spoilage_exposure = sum(
        r["inventory_value_gbp"] for r in (regional or []) if r["status"] == "Spoilage risk"
    )
    cash_tied_up = sum(r["inventory_value_gbp"] for r in (regional or []))
    equipment_exposure = sum(e["exposure_gbp"] for e in (equipment or []) if e["high_risk"])

    auto_entries = [e for e in (activity_log or []) if e["status"] == "auto_executed"]
    autonomous_count = len(auto_entries)
    autonomous_impact = sum(e["impact_gbp"] or 0 for e in auto_entries)

    return {
        "spoilage_exposure_gbp": spoilage_exposure,
        "cash_tied_up_gbp": cash_tied_up,
        "equipment_exposure_gbp": equipment_exposure,
        "autonomous_actions_count": autonomous_count,
        "autonomous_actions_impact_gbp": autonomous_impact,
    }


# ---------------------------------------------------------------------------
# entry point
# ---------------------------------------------------------------------------

def build(raw_dir):
    """Returns None (graceful no-op) unless all three files are present —
    same optional-panel pattern as the rest of the pipeline."""
    equipment = compute_equipment_risk(raw_dir)
    regional = compute_regional_inventory(raw_dir)
    demand = compute_demand_signal(raw_dir)

    if equipment is None or regional is None or demand is None:
        return None

    activity_log = build_activity_log(equipment, regional)
    kpis = compute_kpis(equipment, regional, activity_log)

    return {
        "kpis": kpis,
        "equipment": equipment,
        "regional_inventory": regional,
        "demand_vs_plan": demand,
        "activity_log": activity_log,
    }
