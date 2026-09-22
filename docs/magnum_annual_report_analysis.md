# 10-K Analyzer — a per-year read of TMICC's financial history

Where `docs/magnum_strategic_commitments.md` back-traces a commitment to the initiative delivering it, and `docs/magnum_correlated_timeline.md` correlates TMICC against competitors and macro events, this document is organized by **fiscal year** — one entry per year, each with real dated checkpoints and figures, cited back to whichever filing actually covers it. Structured data lives in `data/raw/magnum_annual_report_analysis.json`; this is the narrative read.

**Four years, selectable in the console via a dropdown** (FY2025 down to FY2022, most recent first). Important honesty note, unchanged from the previous pass: TMICC has filed exactly **one** true Annual Report (FY2025) — it only began independent existence on 6 December 2025. FY2022-2024 are not separate annual reports; they're **combined carve-out financial statements** for the Ice Cream Business, extracted from TMICC's own pre-listing SEC registration statement (Form 20FR12B, filed 4 Nov 2025) — the real document that carries this history from inside Unilever. Organized by year for the strategist's mental model; sourced honestly underneath, and each entry's `source_document.filing_type` says exactly what it actually is.

## FY2025 — the full Annual Report (Form 20-F)

The richest entry — a real report map (see below) plus 14 dated checkpoints, merging what were previously two separate document entries in this panel: the Annual Report itself, and the Deferred Territories/reorganisation checkpoints from the registration statement (both cover events in and around FY2025, so they now live together under one year).

### Report map

Four chapters:

1. **Management Report** (p.5) — About us, Leadership perspectives, Our strategy, Our people, Review of the year, Sustainability, Risk management, Corporate governance
2. **Financial Statements** (p.85) — Consolidated + Company financial statements and notes
3. **Sustainability Statements** (p.148) — Environmental, Social, and Governance disclosures
4. **Further Information** (p.218) — non-IFRS reconciliations, shareholder information, cautionary statement

### Strategic checkpoints

- **1 July 2025** — reorganisation anchor date.
- **30 June 2025** — pro forma capitalisation at listing: €587m cash, €4,049m total indebtedness, €2,143m share capital.
- **H1 2025** — interim combined carve-out results: revenue €4,503m (H1 2024: €4,394m, +2.5%), operating profit €569m (H1 2024: €608m, **-6.4%**) — real margin compression heading into listing, worth watching against full FY2025 once disclosed.
- **2024** — €500m productivity programme launched (three levers: supply chain transformation, overhead reduction, technology-enabled operations).
- **6 December 2025** — demerger completed; TMICC began independent trading.
- **November 2025** — €3bn debut bond issuance across four tranches (2029/2031/2034/2037), 2.75-4% interest, oversubscribed 7x+; financial liabilities €3,416m (2024: €333m), average debt maturity 7.5 years.
- **By January 2026 / April 2026** — India Deferred Territory: demerger effective, then Kwality Wall's trading start (actual completion, per Ecosystem/Strategy tabs, was 30 March 2026 — close to but later than this original plan).
- **Q1 2026** — Portugal Deferred Territory demerger effective; asset sale has up to 3 years from share sale to complete.
- **2026 (to be drawn)** — €300m credit facility for the Indian acquisition.
- **By 2026** — full Dutch Corporate Governance Code compliance (Provision 1.4.3(ii)-(iv)) — not yet met as a newly-standalone company.
- **~End 2027** (30 months from 1 July 2025) — exit all Transitional Services Agreements with Unilever.
- **By 2028** — Vanilla for Change: 80% of Madagascar farmers to regenerative agriculture, 1 million trees planted.
- **From 2026** — new cabinet energy-efficiency technology on new freezer-cabinet purchases.
- **By 2050** — Net Zero across Scope 1, 2, 3.

One clarification worth flagging: the report's cautionary statement (p.235) lists "potential acquisition in India" only inside standard forward-looking-statements boilerplate — most plausibly the already-known Kwality Wall's deal, not a second undisclosed one.

### Strategic analysis — what this means, and what to watch

Two items, deliberately kept separate from the facts above (analysis, not TMICC's stated position):

1. **H1 2025's operating profit fell 6.4% even as revenue rose 2.5%** — real margin compression right before listing, and the registration statement doesn't say whether it's one-off separation costs or something structural. That ambiguity is itself the finding: a strategist shouldn't wave this through. Watch FY2025's full-year results for whether separation costs get broken out as a distinct line, and whether H2 shows a clean rebound.
2. **Four separate multi-year commitments converge on 2027-2029**: the first bond maturity (2029), the Vanilla for Change target (2028), the "near-term" climate scenario window (2026-2030), and the medium-term OSG/margin guidance all land in the same few years. That's a cluster, not four independent risks — worth underwriting as one scenario window, not a checklist of separate items.

## FY2024, FY2023, FY2022 — combined carve-out financials

None of these are standalone documents — they're the Combined Carve-Out Income Statement inside the same registration statement, extracted directly from its financial-statements tables (not summarized secondhand). Real, precise figures:

| Year | Revenue | YoY | Operating profit | Margin | Net profit | YoY |
|---|---|---|---|---|---|---|
| FY2022 | €7,506m | — | €737m | 9.8% | €527m | — |
| FY2023 | €7,618m | +1.5% | €742m | 9.7% | €509m | **-3.4%** |
| FY2024 | €7,947m | +4.3% | €764m | 9.6% | €595m | +16.9% |

Notes on what these numbers actually say:

- **FY2023's net profit fell despite revenue growth** — a real, non-obvious finding. The drivers: a €10m net monetary loss from hyperinflationary economies (vs €2m in FY2022), and taxation rising to €203m (vs €173m) even though profit before tax was higher.
- **FY2024 was the strongest year across the board** — revenue growth accelerated, and net profit rebounded sharply (+16.9%), helped by no hyperinflation monetary loss that year at all.
- **Operating margin drifted down slowly across all three years**: 9.8% → 9.7% → 9.6%. Not a big move, but a consistent direction worth watching against the newly-launched productivity programme's promised 40-60bps annual improvement.
- **FY2024 regional split** (the only year with this granularity disclosed): Europe and ANZ €3.1bn (39% of revenue), Americas €2.9bn (36%) — AMEA at roughly €1.9bn (~25%) is a computed residual, not directly disclosed at this level. 70% of Group revenue came from developed markets, 30% from emerging markets.
- **A real balance-sheet signal**: goodwill roughly doubled from €272m (FY2022) to €585m (FY2024), and intangible assets from €381m to €793m — consistent with a meaningful acquisition somewhere in this window. The specific transaction wasn't identified this pass — a genuine gap, not a guess.
- **The growth rates above are reported revenue growth**, computed directly from the raw carve-out figures — not TMICC's own constant-currency "organic sales growth" non-IFRS metric, which isn't disclosed for these carve-out years. Worth not conflating the two.

## Strategic analysis for FY2022-2024

Each year's entry carries its own `strategic_analysis` — real interpretation, not just the raw figures:

- **FY2022**: this is the baseline the entire standalone thesis gets judged against. Its 9.8% operating margin is the *highest* of the three carve-out years — FY2023 and FY2024 both drifted slightly lower. The €500m productivity programme has to reverse a real multi-year trend, not just build on a flat one.
- **FY2023**: the revenue-up-profit-down pattern traces to two named, real items (hyperinflation loss, higher taxation) — and Turkey-linked hyperinflation recurs across all three years, pointing to a structural emerging-market currency exposure that TMICC no longer has Unilever's larger treasury function to absorb. Worth checking whether TMICC discloses its own hedging policy now that it's independent.
- **FY2024**: the goodwill/intangibles jump flagged as a gap in the previous pass is now plausibly explained — Unilever's real, dated acquisition of Yasso (closed Q3 2023, confirmed via contemporaneous press coverage) lines up with the timing, and connects to the Strategy tab's own "Better-For-You" hedge already built around that same brand. Also: FY2024's headline net-profit growth (+16.9%) is largely an FX-absence effect, not proof the productivity programme is working — operating profit (+3.0%) is the more honest read. And AMEA's small revenue share (~25%) despite its outsized margin performance elsewhere in this project is a real, still-open gap the India acquisition is a direct response to.

## Honest gaps across the whole panel

- FY2022 is the earliest year any TMICC-related filing covers — no data found for FY2021 or earlier.
- The Yasso connection to FY2023's goodwill increase is plausible and well-timed, but not a TMICC-confirmed attribution — treat it as a strong inference, not a stated fact.
- No regional/segment breakdown was found for FY2022 or FY2023 (only FY2024's was disclosed at that granularity).
- The two 2026 Form 6-K filings haven't been read into the FY2025 entry yet.
- Exact pagination for the FY2025 Annual Report's "Further Information" chapter sub-sections is approximate.
- No dedicated FX/hyperinflation hedging policy was found disclosed anywhere in this project's research so far — flagged in FY2023's analysis as worth chasing specifically.
