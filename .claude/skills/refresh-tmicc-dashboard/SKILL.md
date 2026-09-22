---
name: refresh-tmicc-dashboard
description: Refreshes the TMICC Strategist Console's research-backed data (ecosystem, innovation signals, strategic commitments, correlated timeline, financials, annual report analysis, news) by searching the web for real developments since the last pass, then updates the JSON/CSV data files, the narrative docs, and regenerates the pipeline. No API keys anywhere — WebSearch/WebFetch for research, Google News RSS (via fetch_competitor_news.py) for live news.
---

# Refresh the TMICC Strategist Console

This dashboard's value comes entirely from real, sourced, periodically-refreshed research — not a one-time snapshot. This skill is that refresh, packaged so it can be run on demand or on a schedule instead of redone from scratch in conversation each time.

**Read this whole file before doing anything.** The discipline below (real data only, honest gaps, neutral sourcing on sensitive topics, no duplicated facts) is not optional flavor — it's the entire reason this dashboard is worth anything. A refresh that violates it is worse than no refresh.

## Before you start: read the current state

Do not re-derive this project from scratch. Read, in order:
1. `README.md` — current structure and status
2. `data/raw/magnum_ecosystem.json` + `docs/magnum_ecosystem.md`
3. `data/raw/magnum_strategic_commitments.json` + `docs/magnum_strategic_commitments.md`
4. `data/raw/magnum_correlated_timeline.json` + `docs/magnum_correlated_timeline.md`
5. `data/raw/market/*.csv` (financials)
6. `data/raw/magnum_annual_report_analysis.json` + `docs/magnum_annual_report_analysis.md`
7. `data/raw/magnum_innovation_signals.json` (no separate doc — small enough to live in-file)
8. The `generated_date` / `last_verified` fields in each JSON file — that's your baseline. You're looking for what's changed **since** that date, not re-researching everything from zero.

## Step 1 — the mechanical part (no reasoning needed, run it first)

```bash
python3 fetch_competitor_news.py
```

This refreshes `data/raw/news/raw_items.json` live (Google News RSS, zero API keys). It's fast, deterministic, and doesn't need your judgment — do it first so the rest of your research has current news to react to. If it errors, note why in your final summary but continue with the rest of the refresh; a failed news fetch shouldn't block everything else.

## Step 2 — the research part (this is the actual skill)

For each of the four areas below, search the web for real developments **since the baseline date you found above**. Use targeted queries, not vague ones — this repo's own research history shows narrow, specific queries (a company name in quotes, a specific event type) outperform broad ones. Live-test anything non-obvious (a query pattern, a site restriction) before trusting it, the way earlier passes did for Google News RSS's `site:` OR-grouping.

### Ecosystem (`data/raw/magnum_ecosystem.json`)
Check for: new shareholders or share disposals (Unilever's residual stake is explicitly flagged as one to watch), brand portfolio changes (acquisitions, divestments), new or resolved joint ventures, new named suppliers, new disclosed risk factors, leadership changes, and whether any item in `gaps_not_found_this_pass` can now be closed with a real source.

### Strategic Commitments (`data/raw/magnum_strategic_commitments.json`)
Check for: updated guidance (has the 3-5% OSG / 40-60bps margin range changed?), productivity programme progress against the €500m/€350-380m targets, new named initiatives in quarterly or half-year results, AMEA's own regional strategy breakdown (a standing gap since the first pass), and the actual named contents of the "Strategic Priorities Performance Multiplier" (also a standing gap).

### Correlated Timeline (`data/raw/magnum_correlated_timeline.json`)
Check for: new TMICC strategic decisions, competitor moves, macro-commodity swings, market reactions, and — given it's a live, unresolved thread — updates to the Ben & Jerry's governance dispute specifically. New events get **appended** with the next sequential `t` id, never inserted by editing existing ids. Re-sort the `timeline` array by date afterward. Consider whether any new event plus an existing one forms a new correlation pattern worth adding to `correlation_patterns` — but only if it's a real, dated connection, not a forced one.

### Financials (`data/raw/market/*.csv`)
Check for: the next quarterly/half-year/annual results release, updated share price/market cap, any new regional breakdown. Add new dated rows to the existing CSVs (e.g. `magnum_share_price_snapshots.csv`) or new CSV files following the same one-dataset-per-file convention already established — don't overwrite historical rows.

### Annual Report Analysis (`data/raw/magnum_annual_report_analysis.json`)
Only changes when TMICC files a new Annual Report (next one expected ~Feb 2027) or when a previously-unread filing (the two 2026 Form 6-Ks are a standing gap) gets read in. Re-check TMICC's investor relations site + SEC EDGAR each pass to confirm you're still working from the current filing before spending time on it. Every checkpoint needs a real page citation — don't add one without re-opening the source PDF.

### Innovation Signals (`data/raw/magnum_innovation_signals.json`)
Re-run named-competitor searches (Froneri, Nestlé, General Mills, Ferrero/Wells Enterprises) plus "protein"/"low sugar"/"better-for-you" each pass. The moment a real, dated, named launch is found, promote it out of `named_competitor_launches`' gap entry into its own dated entry (`competitor`, `launch`, `date`, `source` fields — the render code in `index.html` already expects this shape). Don't force a weak or generic trend-piece into looking like a specific launch — the gap entry is honest and fine to leave as-is if nothing concrete turns up.

### Consultant's Brief (`data/raw/magnum_consultant_brief.json`) — revisit last, and only after everything above is updated
This file is different in kind from the others: it's analysis and judgment, not TMICC-disclosed fact. After updating Ecosystem/Strategy/Timeline/Financials/Annual Report/Innovation Signals, re-read this file and ask: does any new fact close a listed gap, add a new connected dot, or change whether a recommendation still makes sense? Update it to match — but never let a fact leak in here disguised as analysis, and never let an opinion leak into the fact files disguised as fact. The separation is the entire point of this file existing on its own.

## The non-negotiable discipline

- **Every fact needs a real source.** Cite it (outlet name, or the primary document) in the same field-naming pattern already used throughout (`source`, `basis`, `confidence`). Never write a number you found nowhere.
- **Label what you didn't find as a gap, don't guess.** If a query comes back empty or ambiguous, say so explicitly (`"gap": "..."` or add to `gaps_not_found_this_pass`) rather than filling the space with a plausible-sounding assumption. This repo's own history has multiple examples of exactly this (AMEA's regional breakdown, the Strategic Priorities Multiplier contents, several supplier names) — leaving them open is correct, not a failure.
- **Neutral, attributed framing for anything contested or sensitive.** The Ben & Jerry's/TMICC governance dispute is the template: every claim is written as "X alleges" / "Y's filing states," none as settled fact, and it explicitly does not take a position on the underlying Israel/Gaza issue. Apply the same standard to any new sensitive material — litigation, activist-investor conflict, political controversy.
- **Don't duplicate.** Read existing entries before adding — if a "new" finding is really the same fact already recorded, update/annotate the existing entry rather than creating a near-duplicate.
- **Don't silently overwrite a sourced fact with an unsourced one.** If new information conflicts with what's recorded, note the discrepancy rather than picking one silently.

## Step 3 — regenerate and verify

```bash
python3 data_pipeline.py
```

Then verify end-to-end, the same way every prior change in this repo has been verified — don't skip this:
1. Confirm the JSON files you edited are still valid (`python3 -c "import json; json.load(open('...'))"`).
2. Serve locally (`python3 -m http.server 8099` or similar, in the background) and confirm `index.html` and `data/processed/console_data.json` both return 200.
3. Cross-check that every `document.getElementById(...)` / `querySelector('#...')` id used in `index.html`'s script still has a matching element — a one-line Python regex check, already used repeatedly in this repo's own history, is enough.
4. If you added new fields the frontend doesn't render yet, either add minimal rendering for them or note clearly in your summary that they're captured in the data but not yet surfaced in the UI — don't leave that ambiguous.

## Step 4 — update the narrative docs

`docs/magnum_ecosystem.md`, `docs/magnum_strategic_commitments.md`, `docs/magnum_correlated_timeline.md`, and `docs/magnum_annual_report_analysis.md` are the human-readable read of the JSON data — keep them in sync with whatever you changed. Match the existing tone and structure (short, sourced, gaps stated plainly) rather than introducing a new style. Innovation Signals has no separate doc (small enough to live in-file) — update the JSON directly.

## Step 5 — commit

Follow this repo's existing commit-message convention: a clear summary line, then a body explaining what was found and why it matters, organized by area, closing with an honest note on what's still a gap. Do not push without the user's go-ahead unless they've told you otherwise.

## Running this

**Decided: manual, on-demand only, by explicit organizational choice** — invoke with `/refresh-tmicc-dashboard` whenever a refresh is wanted (e.g., weekly, or right after noticing TMICC has posted results — FY results have landed in Feb, half-year in Jul/Aug so far). Runs on the regular interactive session, no separate billing/usage question to think about.

A scheduled cloud routine (via the `schedule` skill) was built, tested against the real API, and then intentionally not activated — GitHub was never connected to unblock it. It draws on the account's usage/billing the same way any session does, which is the kind of recurring commitment that needs sign-off beyond one person's call. **The routine gets activated only once that sign-off happens** — connect GitHub (`/web-setup` or https://claude.ai/connect-github) and the exact same creation call is ready to run again at that point, not before.

## What this skill deliberately does not do

- It does not call any paid API. WebSearch/WebFetch (which run outside this sandbox) and Google News RSS (keyless) are the only network access involved.
- It does not invent numbers to fill gaps.
- It does not resolve genuinely contested claims (e.g., the Ben & Jerry's dispute) in either party's favor.
- It does not push to GitHub on its own initiative.
