# TMICC Strategist Console

Rebuilt from the ground up around one subject — **The Magnum Ice Cream Company (TMICC)** — rather than the generic "frozen dessert market" scope this repo started as. A local, zero-dependency dashboard: a Python data pipeline writes a JSON file, a Python stdlib server serves it, and a plain HTML/JS front end renders it. No database, no npm install, no framework — just `python3`.

**The idea:** anything a TMICC strategist would want to know immediately — live news on TMICC and its named competitors, the real ecosystem TMICC sits inside (suppliers, joint ventures, shareholders, disclosed risks), a correlated timeline linking TMICC's own decisions to competitor moves and macro-commodity swings, and TMICC's real financial performance. **Zero API keys anywhere** — everything either fetched via free/keyless techniques (Google News RSS) or pulled by hand from real primary sources (TMICC's own Annual Report, Eurostat, USDA).

## Quickstart

```bash
python3 fetch_competitor_news.py   # one-off: fetch live news (run this on a schedule)
python3 server.py                  # generates console_data.json, then opens http://localhost:8080
```

`server.py` runs the pipeline itself on startup and keeps watching `data/raw/` (recursively) for changes, so you don't need to run `data_pipeline.py` by hand unless you want a one-off regeneration without starting the server. The news feed specifically needs `fetch_competitor_news.py` run separately, since fetching news is a live network operation with its own polite rate-limiting — the dashboard pipeline only reads its output.

Every panel shows a small badge — a solid **LIVE** ring or a dashed **MOCK** ring — so you always know what you're looking at. In this rebuild, only Production Trend (parked, unused) still carries that badge at all; everything else is either real or simply absent (see "What's in each panel" below).

A **Refresh dashboard** button sits at the top of the page. It re-syncs the browser to the latest published `console_data.json` immediately, instead of waiting for the 30s auto-poll — it does **not** trigger new research on its own. News/ecosystem/financials/annual-report data only change when the maintainer runs the refresh pipeline (see "Keeping the research current" below) and pushes an update; the button just means a viewer never has to wait up to 30s to see it.

## Self-updating

`server.py` runs a background thread (`watch_and_regenerate`) that polls the newest file-modification time across every file under `data/raw/` (recursively — this was a real bug fixed in this rebuild: it used to only scan the top level, silently missing `data/raw/news/raw_items.json` and everything else in a subfolder) every `WATCH_INTERVAL_SECONDS` (default 15s, override with `WATCH_INTERVAL_SECONDS=5 python3 server.py`). When that timestamp moves, it re-runs `data_pipeline.generate_market_data()` in-process to rewrite `console_data.json`. The browser's own 30s poll then picks up the fresh file on its next tick.

## Project structure

```
frozen-dessert-dashboard/
├── data_pipeline.py          # builds data/processed/console_data.json
├── fetch_competitor_news.py  # live news feed — Google News RSS, zero API keys
├── fetch_usda_data.py        # optional: pulls live nutrition data from USDA's API
├── server.py                 # local web server (stdlib only) + self-updating watcher
├── index.html                # the dashboard itself
├── data/
│   ├── config/
│   │   └── watchlist.json    # companies + topics fetch_competitor_news.py queries
│   ├── raw/                  # every input file — see data/raw/README.md for what's
│   │   │                     # currently used vs left as an honest unused archive
│   │   ├── magnum_ecosystem.json              # real, extracted from TMICC's own Annual Report
│   │   ├── magnum_correlated_timeline.json    # real, dated, cross-referenced
│   │   ├── magnum_strategic_commitments.json  # real, back-traced decision -> strategy -> initiative
│   │   ├── magnum_consultant_brief.json       # ANALYSIS, not fact — gaps/dots/recommendations
│   │   ├── magnum_innovation_signals.json     # competitor "better-for-you" intel — replaces Nutrition tab
│   │   ├── magnum_annual_report_analysis.json # 10-K Analyzer: 2 documents (FY2025 Annual Report +
│   │   │                                       # pre-listing registration statement), each with a
│   │   │                                       # report map + dated, page-cited checkpoints
│   │   ├── news/raw_items.json                # live, from fetch_competitor_news.py
│   │   ├── production/       #   Panel removed for now (see below) — data kept, untouched
│   │   ├── nutrition/        #   legacy, unused — superseded by magnum_innovation_signals.json
│   │   ├── market/           #   TMICC Financial Performance (6 files used; 3 legacy)
│   │   ├── sentiment/        #   legacy, unused — see data/raw/README.md
│   │   ├── demographics/     #   legacy, unused
│   │   └── command_center/   #   legacy, unused
│   └── processed/            # console_data.json lands here (generated by data_pipeline.py,
│                              # committed so static hosts like Netlify have something to serve)
├── docs/
│   ├── magnum_ecosystem.md               # narrative version of magnum_ecosystem.json
│   ├── magnum_correlated_timeline.md     # narrative version of magnum_correlated_timeline.json
│   ├── magnum_strategic_commitments.md   # narrative version of magnum_strategic_commitments.json
│   ├── magnum_consultant_brief.md        # narrative version of magnum_consultant_brief.json
│   └── magnum_annual_report_analysis.md  # narrative version of magnum_annual_report_analysis.json
└── README.md
```

## Navigation

The page is a tab-based single-pager, not a stacked scroll of every panel — click a tab across the top (News / Ecosystem / Strategy / Timeline / Financials / 10-K Analyzer / Brief) to switch pages; the last tab you viewed is remembered (`localStorage`) across reloads. Within a page, individual items still click-to-expand (native `<details>`/`<summary>`, no custom JS toggle needed) — the tabs replace the *outer* show/hide that used to wrap each whole panel, not the inner per-item expand.

## What's in each tab

| Tab | Source | Confidence |
|---|---|---|
| News | Google News RSS via `fetch_competitor_news.py` | real, live |
| Ecosystem (+ Innovation signals) | TMICC's own 2025 Annual Report (`146292742.pdf`), plus competitor better-for-you launch research | real, first-party (innovation signals: real trend context, gap-labeled on specific launches) |
| Strategy | Same Annual Report — "Our strategy" and remuneration sections specifically | real, first-party |
| Timeline | Cross-referenced from the ecosystem doc + targeted research | real, dated, sourced |
| Financials | Unilever/TMICC full-year results disclosures | real |
| 10-K Analyzer | TMICC's Annual Report (Form 20-F) + pre-listing registration statement, dropdown-selectable — report map + dated, page-cited strategic checkpoints per document | real, first-party |
| Brief | This project's own synthesis, built on all of the above | **analysis/judgment — not a TMICC fact, deliberately kept in its own file so it's never confused with one** |

Production & Sales Trend (Eurostat NACE C1052, Germany) is **removed from view for now** — see "The ground-up rebuild" below.

## Keeping the research current

`.claude/skills/refresh-tmicc-dashboard/SKILL.md` packages the deep-research methodology used to build the Ecosystem/Strategy/Timeline/Financials tabs — reading the current data first, searching the web for what's changed since the last pass, updating the JSON/CSV files and narrative docs with the same real-data/honest-gaps/neutral-sourcing discipline used throughout, then regenerating and verifying. Invoke it with `/refresh-tmicc-dashboard` in Claude Code from this repo.

**Manual, on-demand only, pending organizational sign-off** — run it yourself (e.g., weekly, or after noticing TMICC has posted results) rather than a scheduled cloud routine. A weekly cloud routine (PR-based, Friday 5pm UK time) is fully built and tested against the real API — it just isn't activated, since a recurring cloud agent draws on the account's usage/billing the same way any session does, and that's a decision for the team rather than one person. Activation needs only a GitHub connection (`/web-setup`) once approved — no rebuild required.

## Live news feed

`fetch_competitor_news.py` pulls real, live headlines for TMICC and its named competitors/topics — zero API keys, zero cost. Run it directly:

```bash
python3 fetch_competitor_news.py
```

**How it works:** reads `data/config/watchlist.json` (6 companies + 5 topics), queries [Google News RSS](https://news.google.com/rss/search) once per entry (free, keyless, no auth), and writes a deduplicated, normalized list to `data/raw/news/raw_items.json`. Each item is tagged a `source_type` (`official` / `press` / `aggregator` — see below) by matching its real `<source url>` domain — not by fetching a separate newsroom RSS feed, because both feed URLs guessed in the original spec (Nestlé, General Mills investor relations) turned out to be dead (HTTP 404) when actually checked. Meant to run on a schedule (cron/Task Scheduler/GitHub Action) every 30-60 minutes, not continuously — it's a single fetch-parse-write pass per run.

**Named press sources:** every company query (not topic query — see below) also runs a second, press-restricted variant appending a Google `(site:X OR site:Y OR ...)` group across 10 named outlets: Financial Times, BBC News, Reuters, The Associated Press, The New York Times, The Guardian, Al Jazeera English, Bloomberg News, Deutsche Welle, and CNN International. Live-tested before building it in — confirmed Google News RSS genuinely honors the parenthesized multi-site OR group (every returned `<source>` really was one of the tested domains, and really was about TMICC). Matching items get `source_type: "press"`, a tier between `official` and `aggregator`, colored distinctly in the UI so a named outlet's coverage is visible at a glance, not just on click.

**Companies only, not topics, and here's why:** a specific proper-noun query ("The Magnum Ice Cream Company") plus the press-outlet restriction reliably returns genuinely relevant results. A broad generic topic phrase ("cocoa price") plus the same restriction does not — narrowed to ~10 high-volume domains, Google News falls back to loosely-related/trending content from those outlets rather than returning few results. Confirmed empirically: an early test run returned NATO/Ukraine and Trump-AI headlines tagged "Cocoa price" before this was scoped down to companies only.

**Real output from live runs:** turned up news no earlier research pass had — a £50m TMICC factory upgrade in Gloucester (Nov 2025), a new TMICC Global Capability Centre in Pune (Sept 2026), and once the press sources were added, a real product recall (Froneri: "Glass Contamination Concern Leads to Recall of Outshine Frozen Fruit Bars," via The New York Times) and a real internal governance conflict (Reuters/FT: Ben & Jerry's Foundation joining a lawsuit against TMICC, and TMICC accusing a former Ben & Jerry's board chair of "serious misconduct"). Also caught and fixed two real false positives before shipping: bare `MICC` colliding with a US Army acronym ("Mission and Installation Contracting Command," via a DVIDS item), and the topic/press noise described above.

**The panel itself is condensed into 3 columns** (`index.html`'s `classify()`/`renderNewsColumn()`), designed for a strategist with no time to read details — stare, notice the dots, click to expand only what's worth a closer look:
- **TMICC** — anything matching "The Magnum Ice Cream Company" directly.
- **Competitors** — Froneri, Nestlé, General Mills, Ferrero/Wells Enterprises.
- **Ecosystem & partners** — Lakeland Dairies (a named supplier) plus every topic-only match (cocoa price, dairy supply chain, allergens, etc.) — both are ecosystem-level context rather than TMICC or a named rival. This is where a real, unplanned find landed on the very first classified run: "Lakeland fined £115,000 for Artigarvan pollution" — a real environmental fine against TMICC's own milk supplier, exactly the kind of signal this column exists to catch.

Each column: newest-first, capped to 8 for a one-screen read. Rows show the full title, source (colored by tier — green for official, brass/pink for a named press outlet, muted for generic aggregator), and relative time collapsed; click a row to expand it for the exact timestamp, the source-type badge, every matched tag, and a direct "Open article" link — no fabricated summary, since Google News RSS doesn't provide article bodies, only what's shown. A small dot marks anything published since your last visit (tracked via `localStorage`, anchored once per page load — not reset by the 30s auto-refresh, so "new" stays meaningful for the whole time a tab is open).

**Known, honest limitations:**
- Google News RSS's `<link>` is a redirect through `news.google.com`, not the publisher's real URL — confirmed by testing, not just assumed: Google's redirect is a client-side hop, not a real HTTP 3xx, so a plain redirect-follow just returns the same URL with tracking parameters. It's still fully clickable for a human; resolving the true canonical URL would need a headless browser, out of scope for a keyless stdlib script.
- No documented rate limit for this endpoint — the script is polite by design (a ~1.5s gap between each of the 11 queries per run) but this is a scraping-adjacent technique, not a stable API contract; if Google changes this endpoint's behavior, this script needs revisiting.
- This session's sandbox actually has real outbound network access (confirmed: `curl` to `news.google.com` returns real data) — worth noting since network access can't be assumed constant across environments/sessions.

## Legacy: USDA pull (superseded)

`fetch_usda_data.py` and `data/raw/nutrition/usda_nutrition.json` are no longer wired into the pipeline — the Nutrition tab they fed was removed (22 Sep 2026) in favor of the Ecosystem tab's Innovation signals sub-section, which asks the more strategist-relevant version of the same question ("is the category getting more nutritious, and who's driving it?") instead of a raw per-item facts table. The script and data are left on disk untouched, not deleted — see `data/raw/README.md`.

```bash
python3 fetch_usda_data.py                    # still runs standalone if wanted
python3 fetch_usda_data.py "gelato"
USDA_API_KEY=your_key python3 fetch_usda_data.py
```

## Strategic Priorities & Commitments

The point of this tab: back-trace from a stated number to the named initiative actually delivering it, so where an outside partner could plausibly help is visible rather than buried in stakeholder-mapping detail. Built from the same Annual Report as the ecosystem tab, specifically its "Our strategy" and remuneration sections.

**Four headline commitments found, all with exact figures:**
- Growth: Organic Sales Growth averaging **3-5%** from 2026 (medium-term)
- Margin: average annual Adjusted EBITDA margin improvement of **40-60 basis points** (medium-term)
- Cost/separation savings: a **€500 million** productivity programme (launched 2024), of which **€350-380 million** is a named Supply Chain Transformation sub-target
- Capital allocation: dividend payout ratio of **40-60%** (set at the first Capital Markets Day, Sept 2025)

**Not just messaging** — all four feed directly into CEO/CFO bonus calculation (a Financial Performance Factor scored on these same metrics, multiplied by a separate Strategic Priorities Performance Multiplier), which is real structural evidence they're taken seriously internally, not just investor-day language.

**The "where this creates room to help" section is the actual payoff** — 6 named initiatives back-traced from the commitments above (e.g. "US end-to-end supply chain reset," "Digitally-led demand creation model" — named independently in 3 separate places), each with a `partner_angle` naming the category of external help it implies. These are read off what TMICC itself named as specific, not a generic CPG-consulting checklist — see `docs/magnum_strategic_commitments.md` for the full reasoning behind each one.

Also carries a second, separate incentive layer beyond the annual bonus: a **Performance Share Plan** (long-term, evenly weighted 25/25/25/25 across OSG / margin / Free Cash Flow / market share, CEO target 120% of salary, CFO 100%) — found in the same research pass that closed a real gap from the ecosystem tab: TMICC's CEO (**Peter ter Kulve**) and CFO (**Abhijit Bhattacharya**) names.

## Financials and Timeline — deepened with real H1 2026 results and a major governance dispute

Both tabs were substantially deepened in a later pass, following the same back-tracing discipline as the Strategy tab:

- **Financials** now includes FY2025 Adjusted EBITDA margin by region (AMEA's 22.9% dwarfs Europe & ANZ's 13.1% and Americas' 14.1% — both fastest-growing and most profitable), real H1 2026 results (announced 30 Jul 2026: +4.7% OSG, full-year guidance reaffirmed), and dated share-price snapshots (IPO $9.1bn market cap → Feb 2026 "meltdown" low of $12.94 → Sept 2026 recovery to $19.50/$11.99bn, up ~32% from IPO).
- **Timeline** grew from 24 to 42 events and from 3 to 6 correlation patterns, adding a real, ongoing governance dispute between TMICC and Ben & Jerry's independent board — litigation running from Nov 2024 to the present, including a defamation suit and a consumer boycott threat. Handled with careful neutral sourcing given its sensitivity (it touches statements on Israel/Gaza) — every claim is attributed to whoever made it, none presented as settled fact. See `docs/magnum_correlated_timeline.md`'s dedicated section.

## Deepened again (18 Sep 2026): India/AMEA closed, a real court ruling, and a new Consultant's Brief tab

- **AMEA's standing gap is closed**: TMICC's real India acquisition (Kwality Wall's, 4 new factories after 50%+ sales growth), China's 2026 portfolio relaunch, and a newly-found "Frontline First" execution model. CEO Peter ter Kulve has personally attributed India's weak profitability to its cold-chain build-out — a real, disclosed margin/growth trade-off.
- **The €500m savings target got its first real progress figure**: €90m in H1 2026 alone (18% of the target in one half-year).
- **A new executive incentive plan drew real shareholder pushback**: the "Foundation Plan for Growth" passed at the May 2026 AGM with 22.63% against — over the UK Corporate Governance Code's 20% dissent threshold.
- **The Ben & Jerry's ruling got precise**: the vague "lawsuit narrowed" entry was refined with the actual 22 Aug 2026 ruling (Judge Castel dismissed 7 of 10 claims; 2 survive concerning $5m in missed payments tied to a 2022 Palestinian-territories trademark settlement) — timeline grew to 48 events, 9 patterns.
- **New: the Consultant's Brief tab.** Everything above is real fact; this tab is deliberately different — analysis and judgment built on top of it (top gaps, connected dots across all four research tabs, and concrete recommendations), kept in its own file (`magnum_consultant_brief.json`) specifically so it's never confused with a TMICC-stated fact. See `docs/magnum_consultant_brief.md`.

## Rebuilt again (22 Sep 2026): Nutrition retired, 10-K Analyzer added, manual refresh button

- **Nutrition tab removed.** The raw USDA per-item nutrition-facts table was real data but not, on its own, a strategist insight — see "Removed and replaced" above.
- **New: Innovation signals**, inside the Ecosystem tab's Competitors section. Reframes the same underlying question as competitor intelligence: real category-trend sourcing (FoodNavigator-USA, GreyB, MarkWideResearch), plus an explicit, honest gap — no specific, dated "better-for-you" launch could be confirmed this pass from any of the four named competitors. The absence is itself flagged as a signal (TMICC may currently be ahead via Yasso/Breyers Carb Smart), not silently dropped.
- **New: the 10-K Analyzer tab**, replacing Nutrition's slot in the nav. A document-native read of TMICC's Annual Report (Form 20-F) — extracted directly from `146292742.pdf` via PyMuPDF this pass (not the earlier custom regex/zlib extractor) — with a page-numbered report map and nine dated, page-cited strategic checkpoints, several genuinely new to this project (TSA exit by end-2027, the €3bn debut bond issuance with real 2029/2031/2034/2037 maturities, the €300m India-acquisition credit facility, the Dutch Corporate Governance Code compliance-by-2026 gap). Cross-checked against TMICC's investor relations site and SEC EDGAR to confirm this is still the current Annual Report. See `docs/magnum_annual_report_analysis.md`.
- **New: a "Refresh dashboard" button** at the top of the page. Re-syncs immediately to the latest published `console_data.json` rather than waiting for the 30s auto-poll — an honest capability given this is a static, zero-backend site: it does not and cannot trigger new research on its own (that still needs `/refresh-tmicc-dashboard` run by the maintainer, then a push).

## Visual redesign (22 Sep 2026): Apple-inspired, plus a scoped 10-K Analyzer refresh button

- **A second refresh button**, on the 10-K Analyzer tab specifically (`#ar-refresh-btn`). Re-fetches the same published `console_data.json` but re-renders only that panel, rather than the whole page — a genuinely scoped action, not a cosmetic duplicate of the header's global button. Same honesty caveat: re-syncs to what's published, doesn't re-run the annual-report research pass itself.
- **Full palette flip, light and accessible.** The console was a fixed dark "ice-cream-parlor" theme (near-black background, cream text, bright pink/amber accents). Replaced with a light, Apple-website-inspired palette — off-white page background, white cards, near-black text, a deep rose and a warm bronze as the two accents, muted grays for secondary text. Implementation note: since every panel's markup (including the JS render functions' template strings) references the *same* Tailwind color names throughout, the redesign only changes what hex value each name resolves to in `tailwind.config` — zero changes needed to the hundreds of individual `text-ivory`/`bg-panel`/`border-hairline`/etc. usages across the file. Every text-role color was re-verified at >=4.5:1 contrast against both the new page and card backgrounds (computed, not eyeballed) — the Chart.js financials chart's hardcoded colors (Chart.js can't read Tailwind's config) were updated by hand to match.
- **Real system fonts, not a Google Fonts load.** Fraunces/Inter/IBM Plex Mono (all Google-hosted) replaced with the actual Apple system-font stack (`-apple-system`/SF Pro) for display and body text, and a system monospace stack for the data-dense mono labels — kept as a deliberate choice (Apple's own developer-facing pages use SF Mono the same way for technical/tabular content), just off the CDN. One fewer external network dependency, no flash-of-unstyled-text.
- **Depth via shadow, not just borders.** Every card (`border-hairline rounded-lg` pattern, used ~15 times across static sections and JS-rendered `<details>` blocks alike) now also lifts on hover (`shadow-sm hover:shadow-md transition-shadow`) — Apple's soft-shadow card language instead of a flat hairline border doing all the work.
- **Accessibility additions**: explicit `:focus-visible` rings (2px solid accent, 3px offset) on every interactive element, and a `prefers-reduced-motion` override disabling all transitions/animations for anyone who's asked for that — neither existed before this pass.

## Round 3 (22 Sep 2026): richer palette + real light/dark toggle, multi-document 10-K Analyzer

**Feedback on Round 2's light theme: too flat, "looks like a document."** Responded with two changes:

- **Real light/dark toggle**, not just a fixed theme. Every Tailwind color name in `tailwind.config` now resolves through a CSS variable (`rgb(var(--c-x) / <alpha-value>)`, Tailwind's own documented pattern) instead of a static hex — toggled via `[data-theme]` on `<html>`, persisted in `localStorage`. This means the toggle works with **zero changes** to the hundreds of individual `text-ivory`/`bg-panel`/etc. usages across the file, same trick as Round 2's palette flip. **Dark is the actual default** on first visit (this console was always designed dark-first; light is the real alternate choice, not a fallback), set synchronously before paint to avoid a flash of the wrong theme.
- **Richer, warmer colors in both modes** — warm cream (not stark white) in light mode, warm near-black (not pure black) in dark mode, with the card surface visibly lighter than the page background in both (real layering, not a flat monotone field). Two bolder accents (a deep rose and a warm bronze) replace Round 2's more muted ones. Every text-role color re-verified at >=4.5:1 against both page and card backgrounds in both themes; solid-fill buttons use a new `onaccent` color token (white in light mode, near-black in dark mode) instead of a hardcoded white, so they stay correct when the theme toggles.
- **More visual "volume"**: a colored accent bar on every section heading (`main h2 { border-left: ... }`, one CSS rule, no markup changes needed anywhere) and a bolder filled pill for the active tab instead of a thin underline.
- Chart.js (financials chart) reads its colors from the same CSS variables at render time and re-renders on toggle — it can't read Tailwind's config directly, so this needed a small dedicated helper (`cssVarRGB()`).

**10-K Analyzer now covers more than one document, with a dropdown to choose.** Important honesty check first: TMICC has filed exactly **one** true Annual Report (it's only existed independently since 6 Dec 2025) — there's no second TMICC-branded annual report to add. What's real and addable is TMICC's own pre-listing SEC registration statement (**Form 20FR12B**, filed 4 Nov 2025), which carries the ice cream business's combined carve-out financial history from inside Unilever. Added as a second, honestly-labeled document (not mislabeled as a second annual report) — 7 more dated checkpoints, mostly around the **Deferred Territories** (India and Portugal weren't part of the main December 2025 demerger and ran their own separate timelines — a real structural nuance not visible anywhere else in this project). The dropdown re-renders from already-fetched data, no re-fetch needed. See `docs/magnum_annual_report_analysis.md`.

## Round 4 (22 Sep 2026): dynamic type, chocolate/rose/gold dark mode, cleaner viewer-facing copy

- **Fonts**: Fraunces (a genuinely variable/"dynamic" font — optical-size axis 9-144pt plus a weight axis) back for headings, paired with Inter for body, replacing Round 2/3's system-font stack. Reintroduces the Google Fonts load Round 2 had deliberately dropped — a direct trade of "zero external request" for real typographic character, per explicit request.
- **Dark mode recolored**: chocolate (deep cocoa page/panel, real layering between the two), rose (replacing the previous berry-toned accent), and gold (replacing the previous bronze/amber accent) — re-verified at >=4.5:1 contrast throughout. Light mode untouched.
- **Viewer-facing copy stripped of build/process narration.** The console's UI previously explained its own construction to visitors — "Rebuilt from the ground up," "Zero API keys," a footer listing every panel removed in past rebuilds, tooltips describing the refresh pipeline's internals, `docs/*.md`/`python3 *.py` references. All of that is now gone from what a visitor actually sees; it still lives here in README.md and in `docs/`, which are for whoever maintains this repo, not for a strategist reading the live dashboard. The underlying data/analysis itself is untouched — gap-labeling and fact/analysis separation inside the actual research content stayed exactly as rigorous as before, since that's business-relevant intelligence, not development history.

## Customizing

- **Port**: `DASHBOARD_PORT=8081 python3 server.py`
- **Watch interval**: `WATCH_INTERVAL_SECONDS=5 python3 server.py`
- **Front-end refresh interval**: last line of `index.html`, `setInterval(..., 30000)`
- **News query list**: `data/config/watchlist.json` — add/remove companies or topics
- **Colors/type**: `tailwind.config` block near the top of `index.html` — a light, Apple-inspired palette (22 Sep 2026 redesign), every text-role color re-verified at >=4.5:1 contrast against both page and card backgrounds (computed directly, not via the `dataviz` skill's colorblind-Delta-E check, which is a separate concern from plain contrast)
- **Reproducible mock data**: set `MOCK_SEED = 42` (or any int) near the top of `data_pipeline.py`

## The ground-up rebuild — what changed and why

This repo started as a generic "UK frozen dessert market" console (production trends, global market share, brand sentiment, a hypothetical UK retail client's Command Center). It's been rebuilt entirely around TMICC specifically, per the standing rule for this rebuild: **real data only**, and only what a TMICC strategist would actually need.

**Removed entirely:**
- **Executive Brief / `synthesis.py`** — the auto-generated, rule-based "what this cycle means" panel. Deleted, not just hidden — the file is gone, and every reference to it in `index.html` and `data_pipeline.py` is gone too.
- **Command Center / `command_center.py`** (Demand Signal, Regional Inventory Risk, Equipment Risk) — always illustrative by the project's own earlier admission, since no public dataset of a real company's cold-chain telemetry exists. File deleted.
- **Brand & Flavor Sentiment** (US Kaggle sample, static not live), **Consumer & Demographics** (UK-launch-specific, not TMICC-specific), **Global Market Distribution** (generic worldwide category share), **Company Revenue Comparison** and **Volume vs Dollar Sales** (both mostly unsourced "placeholder" rows) — all out of scope for a company-specific strategist tool. Their raw data files are left on disk as an honest archive (see `data/raw/README.md`), not deleted — none of it was fake, it just doesn't fit this dashboard's new subject.

**Added:**
- **Live News Feed** — `fetch_competitor_news.py`, see above.
- **The Magnum Ecosystem** — TMICC's real corporate structure, shareholders, brand portfolio, joint ventures, supply chain, competitors, governance cross-links, and disclosed risk factors, extracted directly from TMICC's own 2025 Annual Report.
- **Correlated Timeline** — TMICC's own dated decisions laid against competitor moves and cocoa-price swings in the same window, with three flagged correlation patterns.

**Kept, reframed:**
- **TMICC Financial Performance** (was "Real-World Precedent (Magnum)") — the exact same real data, just renamed to reflect that TMICC is now the dashboard's actual subject, not a "precedent example" for a hypothetical client.

**Removed and replaced (22 Sep 2026):**
- **Nutrition & Regulatory Exposure** — real data, but a standalone per-item nutrition-facts table wasn't a strategist insight. Replaced by **Innovation signals**, a competitor-intelligence sub-section inside the Ecosystem tab — see the dated section below.

**Removed from view, data kept for later:**
- **Production & Sales Trend** (Eurostat NACE C1052, Germany) — the full 1991-present series was too big, too old, and not relevant to show as-is. `load_sales_trend()` is still defined in `data_pipeline.py` and the real data is untouched at `data/raw/production/ice_cream_production.csv` — just not called or rendered right now. The plan is to bring it back filtered to post-COVID records only (2020+) once that's worth doing; not deleted, just parked.

## Prototype vs. live — deliberate, not a limitation

**Already live, free:** the News Feed panel genuinely fetches on demand, no cost. Production Trend (Eurostat, parked/unused) and the legacy USDA pull sit behind free public APIs and can be re-pulled anytime — see the commands above.

**Periodic real-data snapshots, not continuous feeds:** The Magnum Ecosystem, Correlated Timeline, TMICC Financial Performance, and the 10-K Analyzer are all real but hand-researched — refreshing them means re-reading TMICC's next filing or re-running the research pass that built them, not an automated pull. The "Refresh dashboard" button re-syncs to whatever was last published; it doesn't shortcut this. That's an honest description of what they are, not a shortcut that was skipped.
