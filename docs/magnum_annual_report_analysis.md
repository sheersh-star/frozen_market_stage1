# 10-K Analyzer — a document-native read of TMICC's Annual Report

Where `docs/magnum_strategic_commitments.md` back-traces a commitment to the initiative delivering it, and `docs/magnum_correlated_timeline.md` correlates TMICC against competitors and macro events, this document stays inside a single primary source — TMICC's own Annual Report 2025 — and reads it the way a 10-K analyzer would: a map of the document's own structure, plus a chronological list of dated checkpoints the report itself states, each with a page citation. Structured data lives in `data/raw/magnum_annual_report_analysis.json`; this is the narrative read.

## The document itself

TMICC files a **Form 20-F**, not a US-domestic 10-K — it's a Netherlands-incorporated company listed on NYSE, LSE, and Euronext Amsterdam, and 20-F is the SEC's annual-report equivalent for a foreign private issuer. Functionally it plays the same disclosure role as a 10-K, which is why this panel is framed as a 10-K-style analyzer rather than requiring a literal US filing.

- **Title:** The Magnum Ice Cream Company N.V. — Annual Report 2025
- **FY covered:** year ended 31 December 2025
- **Filed with the SEC:** 18 March 2026
- **Length:** 238 pages
- **Local file:** `146292742.pdf` (kept local, not in git — see `.gitignore`)
- **SEC source:** https://www.sec.gov/Archives/edgar/data/2071668/000110465926029805/micc-20251231x20f.htm

Checked TMICC's investor relations site and SEC EDGAR on 22 Sep 2026: this FY2025 report is still the current, latest Annual Report. The FY2026 Annual Report isn't due until early 2027. Two 2026 Form 6-K filings exist (interim/current disclosures, including AGM results) but haven't been read into this panel yet — an honest gap, not an oversight.

## Report map

Four chapters, each with its own internal structure — used here as a navigation aid, not duplicated content:

1. **Management Report** (p.5) — About us, Leadership perspectives, Our strategy, Our people, Review of the year, Sustainability, Risk management, Corporate governance
2. **Financial Statements** (p.85) — Consolidated + Company financial statements and notes
3. **Sustainability Statements** (p.148) — Environmental, Social, and Governance disclosures
4. **Further Information** (p.218) — non-IFRS reconciliations, shareholder information, cautionary statement

## Strategic checkpoints found this pass

Nine dated, page-cited items — some genuinely new to this project's research, some corroborating (with new specifics) what's already in the Strategy or Ecosystem tabs:

- **2024** — €500m productivity programme launched (p.17), already tracked in Strategy, corroborated here with its three named levers.
- **6 December 2025** — Demerger from Unilever completed; TMICC began independent trading (p.13) — the report's own "defining milestone" framing.
- **November 2025** — €3bn debut bond issuance across four tranches (2029/2031/2034/2037), 2.75–4% interest, order book oversubscribed 7x+; financial liabilities rose to €3,416m (2024: €333m), average debt maturity 7.5 years (p.28). **New**: this is TMICC's real debt-maturity wall, not previously captured anywhere in this project.
- **2026 (to be drawn)** — €300m credit facility earmarked specifically for the Indian ice cream business acquisition (p.28). **New**: the financing detail behind the already-tracked Kwality Wall's transaction.
- **By 2026** — TMICC expects full compliance with the 2025 Dutch Corporate Governance Code's Best Practice Provision 1.4.3(ii)-(iv); not yet fully compliant as a newly-standalone company (p.82). **New** — a self-disclosed governance checkpoint distinct from the Foundation Plan for Growth shareholder-dissent story tracked in the Timeline.
- **By end of 2027** — TMICC plans to exit all remaining Transitional Services Agreements (TSAs) with Unilever (p.17). **New.**
- **By 2028** — Vanilla for Change programme (with Symrise and Save the Children, Madagascar): 80% of enrolled farmers transitioned to regenerative agriculture; 1 million trees planted (up from 585,000), survival rate target 40%→65% (p.180). **New.**
- **From 2026** — new cabinet energy-efficiency technology begins rolling out on new freezer-cabinet purchases (p.171) — connects directly to the freezer-cabinet fleet risk already flagged in Ecosystem (TMICC's largest single emissions source, a fleet it doesn't own).
- **By 2050** — Net Zero ambition across Scope 1, 2, and 3 (p.32), with explicit climate scenario-planning horizons: near-term 2026–2030, medium-term 2031–2039.

## One clarification worth flagging

The report's cautionary statement (p.235) lists "potential acquisition in India" among its example categories of forward-looking statements. Read in context, this is boilerplate — a list of statement *types*, not a fresh disclosure — and most plausibly refers to the already-known Kwality Wall's transaction rather than a second, undisclosed India deal. Flagged explicitly so it isn't mistaken for new news on a future pass.

## Honest gaps

- The two 2026 Form 6-K filings haven't been read into this panel yet.
- Exact pagination for the "Further Information" chapter's sub-sections (non-IFRS reconciliations, shareholder information, cautionary statement) was ambiguous in extraction — approximate, not authoritative.
