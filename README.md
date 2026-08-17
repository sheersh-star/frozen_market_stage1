# Frozen Dessert Market Console

A local, zero-dependency market-intelligence dashboard: a Python data pipeline
writes a JSON file, a Python stdlib server serves it, and a plain HTML/JS
front end renders it. No database, no npm install, no framework — just
`python3`.

It runs immediately on mock data. As you drop in real datasets, each panel
switches from mock to live automatically — no code changes required, and no
manual re-run required either: `server.py` watches `data/raw/` in the
background and regenerates `market_data.json` on its own whenever a file
there is added or changed (see "Self-updating" below).

The Production & Sales Trend panel is already wired to real data — a copy of
`ice_cream.csv` (FRED series IPN31152N, monthly ice cream production index,
1972–2020) lives at `data/raw/ice_cream_production.csv`.

## Quickstart

```bash
python3 server.py          # generates market_data.json, then opens http://localhost:8080
```

That's it — `server.py` now runs the pipeline itself on startup and keeps
watching for changes, so you don't need to run `data_pipeline.py` by hand
unless you want a one-off regeneration without starting the server.

Every panel shows a small badge — a solid **LIVE** ring or a dashed **MOCK**
ring — so you always know what you're looking at.

## Self-updating

`server.py` runs a background thread (`watch_and_regenerate`) that polls the
newest file-modification time in `data/raw/` every `WATCH_INTERVAL_SECONDS`
(default 15s, override with `WATCH_INTERVAL_SECONDS=5 python3 server.py`).
When that timestamp moves — a new file dropped in, an existing one edited —
it re-runs `data_pipeline.generate_market_data()` in-process to rewrite
`market_data.json`. The browser's own 30s poll (last line of `index.html`)
then picks up the fresh file on its next tick. So end to end: drop/update a
file in `data/raw/` → picked up within `WATCH_INTERVAL_SECONDS` → visible in
the browser within another 30s at most. No server restart, no manual pipeline
run.

## Project structure

```
frozen-dessert-dashboard/
├── data_pipeline.py       # builds market_data.json (real data if present, else mock)
├── fetch_usda_data.py     # optional: pulls live nutrition data from USDA's API
├── server.py               # local web server (stdlib only)
├── index.html              # the dashboard itself
├── data/
│   ├── raw/                 # <- drop your downloaded datasets here
│   └── processed/           # market_data.json lands here (generated, gitignored)
└── README.md
```

## Adding your real datasets

Drop files into `data/raw/` using these exact filenames. Nothing is
required — any file that's missing just means that panel keeps running on
mock data until you add it. Once it's there, the background watcher picks it
up on its own — see "Self-updating" above.

| File | Source | Powers | Recommended size |
|---|---|---|---|
| `ice_cream_production.csv` | Kaggle "Monthly Ice Cream Sales Data (1972–2020)" (mirrors FRED series IPN31152N) | Production & sales trend | Already provided — 577 real rows (1972–2020) |
| `ice_cream_reviews.csv` + optional `ice_cream_products.csv` | Kaggle "Ice Cream Dataset" (tysonpo) — Ben & Jerry's, Häagen-Dazs, Breyers, Talenti reviews | Brand & flavor sentiment | ~5 brands × ~20 reviews each (~100 rows in `ice_cream_reviews.csv`); 5 rows in `ice_cream_products.csv`, one per brand key |
| `usda_nutrition.json` | USDA FoodData Central API | Nutrition profile | ~8 food items in the `foods` array (only the first 12 are used) |
| `sweetener_market.csv` | USDA Sweetener Market Data (data.gov / Ag Data Commons) | Regional commodity distribution | 6 rows minimum, one per real region; up to ~24 (6 regions × 4 quarters) for a quarterly-report feel — rows per region are summed |

Column names the loaders match (case-insensitive, several aliases each — see
`_find_field` in `data_pipeline.py`):

- **`ice_cream_production.csv`**: date column `DATE` or `month`; value column
  `VALUE`, `IPN31152N`, `production`, or `units_sold`.
- **`ice_cream_reviews.csv`**: key column `key`, `product_key`, or `id`;
  rating column `stars` or `rating` (1–5).
- **`ice_cream_products.csv`**: key column `key` or `id` (must match the
  reviews file); brand column `brand` (falls back to `name`).
- **`usda_nutrition.json`**: USDA FoodData Central shape — a `foods` array of
  objects with `description` and a `foodNutrients` list (either
  `{"nutrientName": ..., "value": ...}` or the nested `{"nutrient": {"name":
  ...}, "amount": ...}` form). Nutrient names read: `Energy`, `Sugars, total
  including NLEA` (or `Total Sugars`), `Total lipid (fat)`.
- **`sweetener_market.csv`**: region column `region` or `area`, using the
  real USDA region names — New England, Mid Atlantic, North Central, South,
  West, Puerto Rico; value column `value`, `volume`, `deliveries`, `short
  tons`, or `pounds` (commas OK, e.g. `1,234`).

Notes on each, from checking the real sources while building this:

- **Production/sales**: the real columns are literally `DATE` and `VALUE`
  (index, 2017=100) — the loader looks for those first, so a straight
  Kaggle CSV should just work.
- **Brand reviews**: confirmed to cover Ben & Jerry's, Häagen-Dazs, Breyers
  and Talenti with 1–5 star ratings. Exact column names weren't
  confirmable without downloading it myself, so the loader matches several
  likely variants (`key`/`id`, `stars`/`rating`). If nothing loads, open the
  CSV, check the header row, and add the real names to the alias lists near
  the top of `data_pipeline.py` — one line each.
- **USDA nutrition**: use `fetch_usda_data.py` (below) rather than hand
  -downloading — it calls the API and saves the response in the shape the
  pipeline expects. Branded-food nutrient values are usually per serving,
  not per 100g — check `servingSize`/`servingSizeUnit` in the raw JSON if
  the numbers look off.
- **Sweetener market**: these ship from USDA as separate `.xls` files per
  region or per use-category (there's a use-category literally called "Ice
  Cream and Related Products" — worth grabbing that one specifically).
  Export whichever you pull as CSV into `data/raw/sweetener_market.csv`.
  Real region names are New England, Mid Atlantic, North Central, South,
  West, and Puerto Rico — the mock data already uses these same names so
  the panel won't visually jump when you switch it over.

### Live USDA pull

```bash
python3 fetch_usda_data.py                    # searches "ice cream"
python3 fetch_usda_data.py "gelato"            # or any query
USDA_API_KEY=your_key python3 fetch_usda_data.py
```

Get a free key at fdc.nal.usda.gov/api-key-signup — the shared `DEMO_KEY`
works for light testing but rate-limits quickly. This script needs real
internet access, so it wasn't run as part of building this (network in this
build environment is restricted); it's built directly against the
documented API contract, but give it one real test run before depending on
it.

## Customizing

- **Port**: `DASHBOARD_PORT=8081 python3 server.py`
- **Watch interval**: `WATCH_INTERVAL_SECONDS=5 python3 server.py`
- **Front-end refresh interval**: last line of `index.html`, `setInterval(..., 30000)`
- **Colors/type**: `tailwind.config` block near the top of `index.html` — the
  palette is an ice-cream-parlor dark theme (deep cocoa background, vanilla-
  cream text, strawberry-pink accent, mint/berry-red/slate status colors,
  caramel for the regional chart), validated for colorblind-safe contrast
  with the `dataviz` skill's palette checks. Swap the `colors` block for a
  client's brand palette whenever this moves toward CPG-facing work.
- **Reproducible mock data**: set `MOCK_SEED = 42` (or any int) near the
  top of `data_pipeline.py`

## What changed from the original plan

The plan this was built from was a solid skeleton but had a few real bugs
and some structural gaps once real data enters the picture:

- **Fixed broken CDN tags.** `<script src="https://jsdelivr.net">` and
  the Tailwind equivalent pointed at bare domains, not actual asset files —
  the dashboard would have loaded blank. Now pointed at the real Tailwind
  Play CDN and Chart.js UMD bundle.
- **Fixed a date-drift bug.** The mock generator built months with
  `timedelta(days=i*30)`, which slips away from real calendar months over
  time (12 steps of 30 days = 360 days, not a year). Replaced with proper
  calendar-month stepping.
- **Made the pipeline source-modular.** Originally the only way to use real
  data was to rewrite the generator function. Now each panel has its own
  loader that checks `data/raw/` first and only falls back to mock — so
  dropping in a file is the entire integration step.
- **Re-mapped every panel onto one of your four actual sources.** The
  original invented categories ("Gelato", "Plant-Based Dairy") and regions
  with no real dataset behind them. Panels now map 1:1 to your four named
  sources, using their real schemas (confirmed while building this — see
  the table above).
- **Added live/mock provenance tags** on every panel, so it's never
  ambiguous which numbers are real.
- **Turned "Variation A" into working code.** `fetch_usda_data.py` does
  the live API pull the original plan only described as a follow-up prompt.
- **Smoother refresh.** The dashboard now polls every 30s and updates
  charts in place (no full page reload, no flicker).
- **Server hardening.** Reusable ports (no more restart friction),
  configurable port via env var, and a clear message if the data file is
  missing instead of a silent blank page.
