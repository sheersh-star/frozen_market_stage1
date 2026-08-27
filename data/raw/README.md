Real datasets, by filename:

  ice_cream_production.csv       FRED series IPN31152N, live pull:
                                  curl "https://fred.stlouisfed.org/graph/fredgraph.csv?id=IPN31152N"
                                  Re-pull periodically to keep the trend panel current (~2-week
                                  publication lag under the Fed's G.17 release).
  ice_cream_reviews.csv          Kaggle "Ice Cream Dataset" (tysonpo)
  ice_cream_products.csv         same dataset, optional companion file
  usda_nutrition.json            USDA FoodData Central (use fetch_usda_data.py)
  global_market_regions.csv      Published market-research sizing (e.g. Fortune Business
                                  Insights' Ice Cream Market Report) — global share by
                                  continent. confidence=grounded_estimate throughout: no
                                  central body measures worldwide ice cream sales directly,
                                  so this is third-party estimation, not a primary disclosure.
  company_revenue.csv            Mixed real/grounded_estimate/placeholder, per-row basis —
                                  see the basis column for each company's citation.
  magnum_icecream_annual.csv     Unilever FY2021-24 + The Magnum Ice Cream Company FY2025
                                  full-year results — real, cited volume/price growth splits.
  magnum_regional_fy2025.csv     TMICC's FY2025 continent-level organic sales growth.
  volume_dollar_sales.csv        Illustrative only (confidence=placeholder throughout) —
                                  demonstrates the volume/price divergence pattern that
                                  magnum_icecream_annual.csv then shows really happened.

Retired (no current real source, kept out rather than shown as real):
  sweetener_market.csv, sweetener_market_recent.csv  — USDA's Sweetener Market Data (SMD)
    was discontinued around 2009-2010; there is no live version of this dataset to pull.
  brand_sentiment_recent.csv, ice_cream_production_recent.csv  — these fed the old "Recent
    Cycles" interactive timeline with a fictional-brand file and a since-superseded
    illustrative production file. The timeline is retired for now rather than kept running
    on fabricated data; ice_cream_production.csv itself is now a live pull, so the main
    trend panel needs no separate "recent" file.

Command Center inputs (equipment_health.csv, regional_inventory.csv, demand_vs_plan.csv)
are intentionally NOT real — they simulate one hypothetical retail client's private
cold-chain/inventory/demand telemetry, which by definition has no public dataset. Treat
that panel as a demo of what the system does once wired to a real client's real systems.

Full details on each, including known real column names, are in the main README.md one
level up.
