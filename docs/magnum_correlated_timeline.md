# The Magnum Correlated Timeline

TMICC's own disclosed strategic decisions, laid against the competitor moves and macro-commodity swings happening around them in the same window (Dec 2022 – Sept 2026). Structured data lives in `data/raw/magnum_correlated_timeline.json` (24 dated events, 3 flagged correlation patterns); this is the narrative read.

This is the second layer on top of `docs/magnum_ecosystem.md` — that document answered *who TMICC is connected to*; this one answers *when things actually happened, and what happened at the same time*.

## The three patterns worth a strategist's attention

### 1. TMICC's rocky debut and Nestlé's exit announcement landed exactly one week apart
- **12 Feb 2026** — TMICC's first maiden full-year results as a standalone company. Messy: sharp declines in earnings and cash flow, profit below forecast, driven partly by one-off separation costs. The stock had closed at an all-time high of $19.87 the day before — then "melted" (AJ Bell's own word) on the results.
- **19 Feb 2026** — Nestlé's own FY2025 results: "advanced negotiations" to sell its remaining ice cream business (Asia, Canada, parts of Latin America — ~$1.2bn revenue) to Froneri. CEO Philipp Navratil called ice cream "a distraction" from Nestlé's pivot to coffee and pet care.

Both are ordinary annual-results announcements, so the one-week gap could simply be shared reporting-season timing rather than one causing the other. But it's a real, dated coincidence worth tracking: does a second major player publicly retreating from the category color how the market reads TMICC's own standalone story going forward? This is exactly the kind of thing the live news panel should flag automatically the next time it happens again.

### 2. Two competitors ceded direct local control within four months of each other
- **19 Feb 2026** — Nestlé exits ice cream operations in Asia/Canada/Latin America to Froneri, keeping only its 50% Froneri stake.
- **~Jun 2026** — General Mills sells its Häagen-Dazs *retail and gifting* shops in mainland China to a consortium led by tea-chain operator Ningji, while keeping the *foodservice* side.

Both moves are large multinationals handing off direct operational control of ice cream in complex markets while keeping the brand/licensing value. TMICC runs the structural opposite in some of its own complex markets — majority-controlled joint ventures in the Philippines (Magnum RFM Ice Cream Inc., Selecta Wall's Land Corporation — see `docs/magnum_ecosystem.md`). Worth tracking whether full control outperforms or underperforms the emerging peer pattern of handing local operations to partners.

### 3. The exact commodity headwind TMICC blamed for FY2025 margin pressure is now easing — with a new risk already visible
- **13 Jun 2024** — Cocoa futures hit an all-time high, briefly over $11,530/tonne.
- **12 Feb 2026** — TMICC's own FY2025 results explicitly name cocoa inflation (plus a stronger euro) as a driver of 380bps of cost inflation, offset by pricing actions and a productivity programme.
- **Sept 2026 (now)** — Cocoa has retreated to roughly $4,000/tonne, about a third of the 2024 peak.
- **Also now** — Early surveys of the 2026/27 West African crop (harvest begins October) show below-average cherelle formation — a weak-start signal that could reopen the same pressure before it's fully resolved.

The next thing to watch: does TMICC's FY2026 commentary show margin recovery, or a rollback of the pricing actions taken during the high-cost period? The October crop signal is the one concrete date that could flip this back the other way.

## Full dated timeline

| Date | Actor | Category | Event |
|---|---|---|---|
| 2022-12-07 | Ferrero/Wells | competitor move | Ferrero agrees to acquire Wells Enterprises (Blue Bunny, Bomb Pop, Halo Top) — baseline context |
| 2024-06-13 | Macro/Cocoa | commodity | Cocoa futures hit all-time high, >$11,530/tonne |
| 2025-02-06 | General Mills / pre-TMICC | competitor move | General Mills and Unilever's ice cream division reported discussing market trends together |
| 2025 Q2 | Macro/Cocoa | commodity | Global cocoa grinding falls ~5% YoY (Asia -16%) |
| 2025-08-22 | Macro/Cocoa | commodity | CNBC signals a "sweeter" 2026 cocoa-price outlook |
| 2025-09 | TMICC | strategic decision | First Capital Markets Day — 40-60% dividend payout target announced |
| 2025-09-26 | TMICC | governance | Board appointment recorded (identity needs verification) |
| 2025-10-27 | Froneri | competitor move | Trade press cites Froneri's strength as validating the spin-off |
| 2025-12-06 | TMICC | strategic decision | Demerger from Unilever completed |
| 2025-12-08 | TMICC | strategic decision | MICC begins trading (Amsterdam/LSE/NYSE), ~$9.1bn initial market value |
| 2025-12-09 | Market | market reaction | First analyst ratings/outlook published post-listing |
| 2025-12-10 | Shareholder | filing | FIL Limited (Fidelity) discloses 19.89M shares |
| 2025-12-15 | General Mills/Industry | competitor move | Named in a "Major Dairy Industry Deals" roundup alongside Lactalis, Fonterra, Unilever, Arla |
| 2025-12-17 | Shareholder | filing | BlackRock discloses 25.97M shares |
| 2025-12-23 | Shareholder | filing | Goldman Sachs Group discloses 20.03M shares |
| 2026-02-11 | Market | market reaction | MICC closes at all-time high, $19.87 |
| 2026-02-12 | TMICC | strategic decision | Maiden FY2025 results — messy; Italy reset; 380bps cost inflation named |
| 2026-02-12 | Market | market reaction | Shares "melt" — AJ Bell's "Magnum's meltdown" |
| 2026-02-13 | Shareholder | filing | Allan & Gill Gray Foundation discloses 19.67M shares |
| 2026-02-19 | Nestlé | competitor move | Announces advanced talks to sell remaining ice cream ops to Froneri; CEO calls ice cream "a distraction" |
| 2026-02-20 | Analysts/Trade press | market reaction | Retrospective framing Nestlé's move against TMICC's rocky week |
| 2026-03-18 | TMICC | governance | KPMG signs the audited FY2025 Annual Report |
| 2026-06 | General Mills | competitor move | Sells Häagen-Dazs China retail/gifting shops to Ningji-led consortium, keeps foodservice |
| 2026-09 | Macro/Cocoa | commodity | Cocoa retreats to ~$4,000/tonne; 2026/27 crop shows early weak-start signal |

## Honest gaps in this pass
- **Date precision varies.** Most events are dated to the exact day (real, sourced); a few (cocoa grinding data, the September 2025 Capital Markets Day, General Mills' China deal, the current cocoa-price snapshot) are only sourced to a month or quarter — marked with `date_precision` in the JSON rather than presented as more precise than they are.
- **Correlation ≠ causation, stated explicitly in every pattern above.** Reporting-season overlap is a real, ordinary alternative explanation for pattern #1 specifically — flagged rather than glossed over.
- **Ferrero/Wells Enterprises is quiet in this window** — no new 2025-2026 news surfaced. That's itself informative (no competitive pressure visible from that flank right now) but is an absence-of-evidence finding, not a confirmed "nothing happening."
- **General Mills' exact December 2025 dairy-deal involvement** — the trade roundup names General Mills but this pass didn't confirm which specific deal or action that refers to.

## What this feeds into next
Every `correlates_with` link in the JSON is exactly the kind of connection the live news panel should be drawing automatically once it's running — a new competitor headline landing within days of a TMICC disclosure is the signal worth surfacing immediately, which is the whole point of the panel per your original brief.
