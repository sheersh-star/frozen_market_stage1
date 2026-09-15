# The Magnum Ecosystem

Who The Magnum Ice Cream Company (TMICC) is actually connected to — every supplier, competitor, joint venture, shareholder, governance link, and disclosed risk that could plausibly be good or bad news for the company. Built for a TMICC strategist audience: this is the reference map the live news panel, statement analyzer, and everything else in this rebuild gets checked against.

Structured data lives in `data/raw/magnum_ecosystem.json`. This document is the narrative walkthrough.

## Primary source, and why it's unusually good

Almost everything below comes directly out of `146292742.pdf` — TMICC's own 2025 Annual Report (238 pages, filed as a Dutch N.V. disclosure, not a US SEC Form 10-K, though functionally the same kind of document). This was extracted directly from the PDF's text content — a first-party primary source, not a web summary of one. A handful of facts (the demerger date/tickers, the competitor landscape, Lakeland Dairies) were confirmed separately via web search in earlier passes of this conversation and are marked as such below.

**One honest caveat on the extraction itself:** no PDF-parsing library was available this pass, so a custom script pulled text directly out of the PDF's raw content streams. It's legible and fact-checkable (every claim below was read in its original surrounding context before being recorded), but it has irregular spacing and, in at least one case (the board-member bios), appears to interleave two adjacent people's biography text where the original PDF laid them out side-by-side. That specific section is flagged for verification below rather than stated as settled fact.

## Corporate facts
- **HQ:** Reguliersdwarsstraat 63, 1017 BK, Amsterdam, Netherlands. Dutch N.V. (naamloze vennootschap).
- **Listed as MICC** on Euronext Amsterdam, the London Stock Exchange, and the New York Stock Exchange — trading began 8 Dec 2025, following the 6 Dec 2025 demerger from Unilever.
- **Scale (FY2025):** €7.9bn revenue, 16,500 employees, 30 factories, 12 R&D centres, and a fleet of **3 million freezer cabinets** — none of which TMICC actually owns (see risk factors below).
- **Auditor:** KPMG Accountants N.V., report signed in Amstelveen on 18 Mar 2026 by engagement partner C.M.L. Priem RA.

## Major shareholders (real, dated)
| Holder | Position | As of |
|---|---|---|
| Unilever PLC | residual post-demerger stake | 8 Dec 2025 |
| BlackRock Inc. | 25,965,010 shares | 17 Dec 2025 |
| Goldman Sachs Group Inc. | 20,026,031 shares | 23 Dec 2025 |
| FIL Limited (Fidelity) | 19,894,021 shares | 10 Dec 2025 |
| Allan & Gill Gray Foundation | 19,674,251 shares | 13 Feb 2026 |

Watch Unilever's line specifically — any further disposal of its residual stake is a real, checkable signal.

## Brand portfolio
Wall's (1922), Cornetto (1959), Twister (1982), Ben & Jerry's (1978), Magnum (1989), Talenti (acquired 2014), Yasso (acquired 2023), plus Breyers, Popsicle and Carte d'Or in specific regions. The Americas region is home to Breyers, Popsicle, and Ben & Jerry's specifically. Regional product variants surfaced in the report: Magnum Dubai/Volcano/Plombir and Carte d'Or Chunkies (Türkiye), Cornetto Popcone (Pakistan).

Two brands are explicitly positioned as the company's **GLP-1/weight-loss-drug hedge** (see risk factors): Yasso and Breyers Carb Smart, both marketed as "Better-For-You."

## Joint ventures, subsidiaries, and associates
- **Magnum RFM Ice Cream Inc.** (Philippines, formerly Unilever RFM Ice Cream, Inc.) — TMICC controls via 50%+1 share and board majority. The "RFM" name strongly implies RFM Corporation, a real major Filipino food/beverage conglomerate, as the JV partner — worth confirming directly rather than assuming.
- **Selecta Wall's Land Corporation** (via WS Holding, Inc.) — 40% direct + 10% indirect, an associate rather than a controlled subsidiary. Selecta is a well-known, real Philippine ice cream brand — a second Philippines structure alongside Magnum RFM.
- **The Magnum Ice Cream Company Pakistan Limited** — 99.35% owned, consolidated.
- **US entity structure**: Magnum ICC US SpinCo/Holdco/US LLC, Ben & Jerry's Holdco LLC, Yasso Inc — the corporate scaffolding built specifically for the demerger.

## Raw material supply chain
| Material | Sourcing standard | Named partner(s) | Note |
|---|---|---|---|
| Dairy | Caring Dairy (TMICC's own animal-welfare standard) | **Lakeland Dairies** (Ireland — confirmed by you) | Ben & Jerry's US runs its own separate "Milk with Dignity" migrant-worker-protection programme |
| Cocoa | Fairtrade + Rainforest Alliance | none named — TMICC participates in the **International Cocoa Initiative**'s Forced Labour Working Group | No trading house (Cargill, Olam, Barry Callebaut) confirmed as a supplier |
| Vanilla | Fairtrade + Rainforest Alliance | **Symrise** + **Save the Children** (Vanilla for Change programme, Sava region, Madagascar) | Also a member of the Sustainable Vanilla Charter |
| Palm oil | 100% RSPO-certified | none named | Same commodity/regulation (EUDR) already tracked in the ESG Meets CPG console |
| Cane sugar | Bonsucro credits | none named | |
| Packaging | — | none named | A stated risk factor (below), but no supplier named in this pass |

## Competitors
- **Froneri** — 50/50 Nestlé/PAI Partners JV, owns Häagen-Dazs internationally, the #2 global ice cream producer by retail sales (TMICC + Froneri together ~32% of global retail sales).
- **Nestlé** — reported (Feb 2026 trade press) to be reviewing or exiting its remaining ice cream exposure, including its Froneri stake.
- **General Mills** — owns Häagen-Dazs in the US and Canada only.
- **Ferrero / Wells Enterprises** — Blue Bunny, Halo Top, Bomb Pop; Ferrero acquired Wells in 2023.

## Governance cross-links — needs individual verification
TMICC board member biographies (as extracted) show real cross-directorships at: **Koninklijke Ahold Delhaize N.V.** (major European retailer), **FrieslandCampina N.V.** (major Dutch dairy cooperative — directly relevant to TMICC's own dairy sourcing), **Wolters Kluwer N.V.**, **Heineken N.V.** (former CFO & Executive Board Member, 13 years), **Exor N.V.**, **Tesco PLC** (already tracked in the ESG Meets CPG console), **Atairos**, **Bain Capital**, **Goldman Sachs & Co. Capital Markets**, **Samsonite**, **Worldpay**, **Atento**.

**Flagged honestly:** the extraction appears to interleave at least two different board members' biography text (the PDF likely laid them out in side-by-side columns). The companies above are real and really appear in TMICC's board bios section — but which specific director holds which specific appointment needs a direct look at the report's governance pages before being stated as fact person-by-person.

## Peer groups TMICC uses about itself
- **Remuneration benchmarking peer group:** Chocoladefabriken Lindt & Sprüngli, Coca-Cola Europacific Partners, Conagra, Danone, General Mills, Lotus Bakeries, Mondelez International.
- **Total Shareholder Return (TSR) peer group** (partial — extraction cut off before the full list): Barry Callebaut, Emmi, Glanbia, Orkla.

Neither list is a "competitor" list in the product sense — they're TMICC's own chosen comparison companies for executive pay and shareholder-return benchmarking. Useful context, different category from the actual competitors above.

## Industry & regulatory bodies TMICC is named as participating in
International Cocoa Initiative · Sustainable Vanilla Charter · RSPO · Fairtrade International · Rainforest Alliance · Bonsucro · Global Animal Partnership (GAP) · EU Taxonomy Regulation (Article 8) / CSRD-ESRS reporting.

## Disclosed risk factors (from the report's own forward-looking statements)
1. **Reliance on Unilever** — an explicit, named post-demerger transition risk.
2. **Packaging sustainability capability** — named as a risk to finding sustainable packaging solutions.
3. **Customer relationship deterioration.**
4. **Raw material / commodity cost volatility.**
5. **Cold-chain distribution disruption** — named alongside climate-driven extreme weather (floods, hurricanes, droughts).
6. **Carbon taxes / freezer cabinet emissions** — the 3-million-unit freezer cabinet fleet (not owned by TMICC, placed in retail outlets) is explicitly named as the single largest emissions category and the focus of planned carbon-tax mitigation.
7. **GLP-1/weight-loss medication impact on demand** — explicitly named: "largely a US issue but increasing globally." Yasso and Breyers Carb Smart are positioned as the hedge.

## Honest gaps — nothing found this pass
- No named cocoa or vanilla **trading house** (Cargill, Olam, Barry Callebaut appears only as an unrelated TSR peer, not a supplier).
- No named **packaging material supplier** (no Huhtamaki, Amcor, or equivalent found).
- Exact **board-bio-to-name mapping** for the governance cross-links above.
- **ABN AMRO's exact role** — the name appears near the shareholder-information/AGM section, most likely as paying agent/registrar for the Amsterdam listing, but this pass didn't confirm that specifically rather than an advisory role.

## What this feeds into next
This ecosystem map is the expanded, evidence-backed version of the `watchlist.json` concept from the earlier live-news-panel spec — every named entity/material/body above is a real candidate for a news-monitoring query, and every risk factor is a real candidate for a "why does this news item matter to TMICC" tag. Next step, per your instruction, is building the live news feed panel itself against this list.
