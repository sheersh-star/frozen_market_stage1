Scope: UK launch market, scaling to a global initiative. Regulatory/nutrition
framing is UK FSA + WHO, not US; currency is GBP; Command Center is a
hypothetical UK retail client. Two files remain US-sourced where no real
UK/EU equivalent was found (marked below) — labeled honestly, not implied
to be UK data.

Real datasets, by filename:

  ice_cream_production.csv       Eurostat NACE C1052 (ice cream manufacture), Germany,
                                  live pull:
                                  curl "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_inpr_m?format=JSON&nace_r2=C1052&geo=DE&s_adj=NSA&indic_bt=PRD&unit=I21"
                                  Germany stands in for the EU — Eurostat suppresses the
                                  EU27 aggregate at this 4-digit NACE level (confidentiality).
  ice_cream_reviews.csv          US SAMPLE — Kaggle "Ice Cream Dataset" (tysonpo). No
                                  equivalent UK/EU review dataset found.
  ice_cream_products.csv         same dataset, optional companion file
  usda_nutrition.json            US branded products — USDA FoodData Central (use
                                  fetch_usda_data.py). Values are US; the regulatory
                                  judgment applied to them (UK FSA traffic-light, WHO
                                  free-sugar %) is UK/WHO — see data_pipeline.py constants
                                  UK_SUGAR_TRAFFIC_LIGHT_* and WHO_FREE_SUGAR_*_LIMIT_G.
  global_market_regions.csv      Published market-research sizing (e.g. Fortune Business
                                  Insights' Ice Cream Market Report) — global share by
                                  continent. confidence=grounded_estimate throughout: no
                                  central body measures worldwide ice cream sales directly,
                                  so this is third-party estimation, not a primary disclosure.
  company_revenue.csv            Mixed real/grounded_estimate/placeholder, per-row basis —
                                  see the basis column for each company's citation. Leads
                                  with TMICC and Froneri (both European/UK-linked) purely
                                  by revenue magnitude; also includes Mackie's of Scotland,
                                  a real UK independent with Companies House-filed accounts.
  magnum_icecream_annual.csv     Unilever FY2021-24 + The Magnum Ice Cream Company FY2025
                                  full-year results — real, cited volume/price growth splits.
  magnum_regional_fy2025.csv     TMICC's FY2025 continent-level organic sales growth.
  volume_dollar_sales.csv        Illustrative only (confidence=placeholder throughout) —
                                  demonstrates the volume/price divergence pattern that
                                  magnum_icecream_annual.csv then shows really happened.
                                  Currency column is revenue_gbp.
  population_by_age_region.csv   World Bank population-by-age-bracket indicators
                                  (SP.POP.0014.TO / .1564.TO / .65UP.TO), 2023. Leads with
                                  United Kingdom (the launch market), then the same 5
                                  continents as global_market_regions.csv as the scale-up
                                  context. The 5-continent split is a verified exact
                                  partition of the World Bank's own World totals.
  ice_cream_consumption_by_age_uk.csv   UKHSA, citing the National Diet and Nutrition
                                  Survey (NDNS) years 5 & 6 — real UK ice-cream-specific
                                  consumption (g/day, sugar g/day, share of diet sugar,
                                  portions/year) for ages 5-11.

Command Center (equipment_health.csv, regional_inventory.csv, demand_vs_plan.csv):
  Intentionally NOT real — they simulate one hypothetical UK retail client's private
  cold-chain/inventory/demand telemetry, which by definition has no public dataset.
  Regions are UK statistical/constituent-country regions (London, South East, North
  West, Scotland, Wales, Northern Ireland); all dollar figures are GBP
  (unit_cost_gbp, exposure_gbp, impact_gbp, etc. in command_center.py). Treat this
  panel as a demo of what the system does once wired to a real client's real systems.

Retired (no current real source, kept out rather than shown as real):
  sweetener_market.csv, sweetener_market_recent.csv  — USDA's Sweetener Market Data (SMD)
    was discontinued around 2009-2010; there is no live version of this dataset to pull.
  brand_sentiment_recent.csv, ice_cream_production_recent.csv  — these fed the old "Recent
    Cycles" interactive timeline with a fictional-brand file and a since-superseded
    illustrative production file. The timeline is retired rather than kept running on
    fabricated data; ice_cream_production.csv itself is now a live pull, so the main
    trend panel needs no separate "recent" file.
  sweet_foods_by_age_us.csv  — superseded by ice_cream_consumption_by_age_uk.csv, which
    is both more geographically appropriate (UK vs US) and more directly relevant
    (ice-cream-specific consumption vs a general "sweet foods" category).

Full details on each, including known real column names, are in the main README.md one
level up.
