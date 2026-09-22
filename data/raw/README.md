Rebuilt around a single subject — The Magnum Ice Cream Company (TMICC) —
rather than the generic "frozen dessert market" scope this folder was
originally built for. This file was rewritten alongside that rebuild;
see the main README.md's "What changed" / rebuild section for the fuller
account of what was cut and why.

## Currently used by data_pipeline.py

  magnum_ecosystem.json              The Magnum Ecosystem — extracted directly from TMICC's
                                      2025 Annual Report (146292742.pdf, kept local, not in
                                      git — see .gitignore). Real, first-party, cited.
  magnum_correlated_timeline.json    TMICC's own decisions vs competitor moves vs macro
                                      commodity swings, dated and correlated. Real, cited.
  magnum_strategic_commitments.json  Back-traced: each headline commitment (growth, margin,
                                      cost savings, capital allocation) -> the named strategic
                                      initiative actually delivering it, by region where TMICC
                                      discloses regional detail. Same source PDF, "Our strategy"
                                      and remuneration sections specifically. Real, cited.
  magnum_consultant_brief.json       ANALYSIS, not fact — top gaps, connected dots across all
                                      other files, and consultant-style recommendations. Every
                                      item cites the real fact it's built on; the synthesis
                                      itself is judgment, kept in its own file on purpose so it's
                                      never confused with a TMICC-disclosed fact.
  news/raw_items.json                Live news feed output — produced by the separate
                                      fetch_competitor_news.py (run that, not this file, to
                                      refresh it). Zero API keys — Google News RSS.
  magnum_innovation_signals.json     Replaces the old Nutrition tab. Real category-trend
                                      sourcing (FoodNavigator-USA, GreyB, MarkWideResearch) plus
                                      an honest gap: no specific, dated "better-for-you" launch
                                      confirmed this pass from the four named competitors.
  magnum_annual_report_analysis.json A document-native read of TMICC's Annual Report (Form
                                      20-F, 146292742.pdf): report map + dated strategic
                                      checkpoints, each with a page citation. Distinct from
                                      magnum_strategic_commitments.json (back-traced) and
                                      magnum_correlated_timeline.json (cross-company) — this
                                      one stays inside what the single document itself says.
  market/magnum_icecream_annual.csv  Unilever FY2021-24 + TMICC FY2025 full-year results —
                                      real, cited volume/price growth splits. TMICC-specific.
  market/magnum_regional_fy2025.csv  TMICC's FY2025 continent-level organic sales growth.
  market/magnum_regional_margins_fy2025.csv  FY2025 Adjusted EBITDA margin by region — real, from the
                                      same Annual Report. AMEA's 22.9% (vs 13.1%/14.1% for the other
                                      two regions) is the standout: both fastest-growing AND most
                                      profitable — see the Timeline tab's AMEA correlation pattern.
  market/magnum_h1_2026.csv          Real H1 2026 group results (revenue, OSG, volume/price growth),
                                      announced 30 Jul 2026 — bridges FY2025 to the present and
                                      confirms full-year guidance was reaffirmed, not walked back.
  market/magnum_h1_2026_regional.csv  Real H1 2026 OSG by region, paired with the FY2025 figure for
                                      each region for direct comparison (e.g. Americas accelerated
                                      from +0.8% to +3.2%).
  market/magnum_share_price_snapshots.csv  Real, dated MICC price/market-cap snapshots (not a
                                      continuous series — no live market-data feed here): IPO,
                                      all-time-high, the "meltdown," and the current (Sept 2026)
                                      recovered position.

## No longer used by the pipeline (left on disk as an honest archive, not deleted)

These predate the ground-up rebuild and don't fit a company-specific strategist
tool's scope — either not TMICC-specific, not live, or too mixed-confidence
relative to the "real data only" rule this rebuild follows. Nothing here was
fake — see each file's own header/basis column — they're just out of scope now,
not discredited.

  production/ice_cream_production.csv   Eurostat NACE C1052 (ice cream manufacture), Germany —
                             real, live-pullable:
                             curl "https://ec.europa.eu/eurostat/api/dissemination/statistics/1.0/data/sts_inpr_m?format=JSON&nace_r2=C1052&geo=DE&s_adj=NSA&indic_bt=PRD&unit=I21"
                             Panel removed for now (too big/old/irrelevant as the full
                             1991-present series) — kept untouched, `load_sales_trend()`
                             still defined in data_pipeline.py, just not called. Revisit
                             with a post-COVID-only (2020+) cut.
  sentiment/                US Kaggle sample (Ben & Jerry's, Häagen-Dazs, Breyers, Talenti
                             reviews) — a real dataset, but static (not live) and the
                             brands happen to map onto real ecosystem entities, so this
                             could come back as a genuine live-sentiment feature later.
  demographics/              World Bank + UKHSA UK consumption data — real, but tied to the
                             old "UK launch market" framing, not to TMICC as a company.
  market/global_market_regions.csv    Real third-party market research (Fortune Business
                             Insights), but generic worldwide category share, not TMICC-specific.
  market/company_revenue.csv          Mostly unsourced "placeholder" rows (see its own
                             confidence column) for a long tail of small/private competitors,
                             mixed with a couple of genuinely real rows (TMICC, Mackie's of
                             Scotland). Superseded by the more rigorously real ecosystem/
                             timeline data.
  market/volume_dollar_sales.csv      Explicitly confidence=placeholder throughout — always
                             illustrative, never real.
  command_center/            Intentionally never real — simulates one hypothetical retail
                             client's private cold-chain telemetry, which by definition has
                             no public dataset. Removed with command_center.py in this rebuild.
  nutrition/usda_nutrition.json      USDA FoodData Central raw per-item nutrition facts — real
                             data, but a facts table on its own wasn't a strategist insight.
                             Replaced by magnum_innovation_signals.json (competitor-intelligence
                             framing of the same underlying "is the category getting more
                             nutritious" question), rendered in the Ecosystem tab.

## Config

  ../config/watchlist.json   Companies + topics fetch_competitor_news.py queries — built
                             from magnum_ecosystem.json's real findings.

Full details on each active file, including known real column names, are in the main
README.md one level up.
