# Phase 2 — Feasibility and implementation plan

**Challenge:** Invoice Audit Exercise — Level 2  
**Author:** Agent 1A  
**Reviewed:** 23 September 2026  
**Source:** [majedzahrani3/invoice-auditing-level-2][repo], commit `aef4924dc32506b4587de8b788b5a947e6beffec`; the GitHub `main` commit was checked again during this phase and still matches this snapshot.

This plan governs the subsequent implementation; it does not execute it. No solver, invoice classifications, corrected invoice totals or submission file were produced in Phase 2.

The independent **Agent 2 audit was read first**. Agent 1A's understanding report is the baseline, with all eight handoff corrections in Agent 2 §6 carried forward. Agent 1B supplies useful extraction tables and examples, subject to the audit's corrections and verification against the repository. Its billed-rate reproduction figures are not accepted as validated accuracy or implementation acceptance criteria.

`CW` and `DDS` below mean the [civil contract][cw] and [drilling contract][dds]. Page numbers are one-based PDF pages and match their printed footers. Important rules are cited to the contracts; the reports remain navigation aids.

## 1. Feasibility and the implementation choice

**A complete audit is feasible as a deterministic local batch program, with reviewed contract tables and evidence extraction.** The limiting work is interpreting and validating shared rules, not processing volume. Final certainty is conditional: a small number of genuine contractual and submission ambiguities must be resolved or disclosed, rather than hidden in defaults.

The input population was rechecked directly during this phase:

| Input | Civil works | Drilling services |
|---|---:|---:|
| Headers | 900 | 1,906 |
| Lines | 7,746 | 91,244 |
| Distinct billed codes | 60 | 39, including `DS-900` |
| Supporting text files | 2,169 | 8,151 |
| Total supporting-text bytes | 557,687 | 7,698,252 |
| Largest supporting-text file | 344 bytes | 1,236 bytes |
| Currency / judged field | SAR / `application_total` | USD / `invoice_total` |

Header and line ID sets agree in both datasets; the template has 2,806 rows. The record corpus is about 8.3 MB. These facts support a single-process implementation using Python, exact decimal arithmetic, explicit date parsing and ordinary indexed collections. A database, distributed processing, learned classifier or retrieval service is unnecessary for this fixed corpus. This is a design choice, not a measured runtime promise. [Header and line CSVs][ci]; [drilling CSVs][di]; [template][template].

| Choice | Reason and limit |
|---|---|
| Reviewed structured terms, extracted once from the scans | A wrong shared rate or eligibility list can affect many invoices. OCR is an aid; the image and operative wording govern. Reuse Phase 1 images/OCR only after checking PDF identity. |
| Explicit parsers and contractual vocabulary mappings | The supplied records are short, with recurring fields and narrative forms. Use reviewed patterns for those forms; retain unmatched text as a query. DDS Appendix G expressly supplies mappings that ordinary industry semantics would get wrong. |
| Separate civil and drilling valuation functions; shared loading, provenance and reporting utilities | Civil and drilling have different rounding, evidence, quantity and financial rules. Sharing one configurable pricing engine would add risk without a demonstrated need. |
| Source-derived checks and arithmetic, with AI limited to reviewable assistance | AI may help transcribe or propose a wording match. Every accepted term/mapping must be cited and frozen. The reproducible audit should not require fresh model calls or allow model confidence to substitute for evidence. |
| Complete valuation plus a finding ledger | Only patching suspicious billed amounts can miss omitted discounts, interacting errors and errors that cancel. Keep billed values for comparison, not as the pricing oracle. |

No implementation stage may use the README's 5–8% statement as a target, stopping rule or reason to suppress supported findings. Reconciliation with billing is a useful diagnostic, as the README requests; it cannot override explicit contract text. [README, What you have, Task, Scoring and Ground rules][readme].

## 2. Work sequence and completion gates

The gates are evidence requirements, not promises of certainty. An unresolved rule can be isolated while unrelated work proceeds. It cannot silently pass its affected invoices.

| Stage | Work and dependency | Evidence required to consider the stage complete |
|---|---|---|
| **G0 — Freeze the inputs and audit specification** | Pin the source; preserve the three Phase 1 artifacts; establish rule, ambiguity and source indexes. No dependency. | File hashes and inventory match the snapshot; every guideline check and material contract section has an owner in the specification; Agent 2 corrections are explicitly recorded. |
| **G1 — Verify contractual terms and consequences** | Transcribe/review rates, units, eligibility lists, evidence conditions, timelines and financial semantics. Depends on G0. | Every active numeric cell and rule has a page/clause reference and a second verification against the scan; explicit overrides are recorded; open interpretations have bounded alternatives and affected scopes. No unverified table feeds pricing. |
| **G2 — Load claims and extract evidence** | Preserve CSV claims; parse records and join by internal reference; identify events. Depends on G0 and G1's evidence specification; can develop alongside remaining G1 review. | Every source row/file is accounted for; each required field is parsed or explicitly unresolved; reference validity and semantic validity are separate; reviewed examples cover every record family and encountered wording/layout branch. |
| **G3 — Validate local entitlement and pricing** | Implement identity/period, unit, evidence, quantity and local rate/rounding checks, separately for both contracts. Depends on relevant G1/G2 gates. | Independently calculated clause-based cases pass, including exceptions and boundaries; all billed code families are implemented or explicitly marked unresolved; each amount has an explainable calculation trace. |
| **G4 — Validate chronology and shared state** | Add bands, caps, exclusions, duplicates, run/well events, retrospective adjustments and retention history. Depends on G1–G3. | Small multi-invoice histories agree with independent expected events and amounts; ordering, reset, allocation and replay tests pass; no duplicate event or adjustment is counted twice. |
| **G5 — Reconstruct full invoice outcomes** | Combine all twelve checks and correctly aggregate expected totals, including nonlinear deductions/tax. Depends on G3/G4 for each affected scope. | Every invoice has check coverage, findings, amount status and an evidence trail; monetary and procedural outcomes remain distinct; independently reviewed complete invoices reconcile step by step. |
| **G6 — Review the full population and contain failures** | Run all invoices, investigate systematic residuals, review uncertainty and samples of apparent passes. Depends on G5. | Every residual cluster is explained by a validated rule, source finding or visible unresolved question; all critical review cases are dispositioned; changes have replayed all dependent invoices; no unsupported pass or silent fallback remains. |
| **G7 — Freeze and reproduce the deliverables** | Assign final categories/confidence, export, write the short report and decision log. Depends on G6 and an explicit policy for any unresolved export cases. | A clean clone reproduces the same 2,806-row CSV and audit results; independent output checks pass; all five README deliverables and AI disclosure are present. |

Verification is part of each stage. G6 is not the first time correctness is tested. Until G3/G4 have passed for a rule, population-wide results from that rule are diagnostic and cannot be trusted as final decisions.

## 3. The source-backed audit specification

Create a small versioned specification before encoding decisions. It should contain:

- **Terms:** code, scheduled unit, base rate/currency, rate source, factor eligibility, quantity rules, caps, exclusions, evidence requirements and rounding stages.
- **Instruments:** identifier, issue date, instrument effective date, row effective date/month, changed field, replacement/supplement relationship, carry-forward provision and page.
- **Rules:** stable ID, guideline check, scope, prerequisites, contractual consequence, source, overridden provision, uncertainty and validation cases.
- **Evidence mappings:** record wording/field, meaning, unit, applicable charge/event and source. Preserve raw wording alongside normalized values.
- **Decisions:** settled reading or open alternatives, reason, affected rules/invoices, amount sensitivity and confidence implications. The final one-page decision log is a concise view of this working register.

Do not create one universal precedence ranking from page order. Record the actual provisions: CW clause 2 and P1; DDS clause 2 and P1; explicit second-series replacements/exceptions; and the instruments' issue order and own effective dates. A specific override such as DDS clause 31A is stronger evidence than a stale Schedule 6 reference in a glossary footnote. Broken cross-references and illustrative examples do not invalidate otherwise explicit operative text. [CW pp.3, 12, 32–33, 38–43][cw]; [DDS pp.3, 11, 35–42][dds].

The table-verification inventory is finite:

| Contract | Tables and clauses to freeze |
|---|---|
| Civil | 60 Schedule 1 items and units (pp.17–19); zones/work areas (20); index and FX tables (21–22); 15 ground-eligible codes (23); night/rest lists, eight annual band schedules, nine daily caps, exclusions and surveyed items (24–26); 17 record-required codes (27); second-series rules (32–33); all five instruments (39–43). |
| Drilling | 38 Schedule 1 services plus the separate `DS-900` rule (pp.8, 15–16); depth and annual bands (17); index/FX/replacement values (18–19); factor, standby, daily-cap and once-only lists (20–22); evidence parts (24); scope and definitions (27–29); second-series rules and complete glossary (35–36); all five instruments (38–42). |

Civil daywork, provisional sums and preliminaries (pp.28–31) must be included in the coverage inventory. The observed 60-code population does not bill those distinct schedule codes. Do not build unused machinery, but retain their inclusion/exclusion implications and fail visibly if an unsupported code appears. Similarly, check special-condition narratives—flood watch, access restrictions, safety/heat suspension, rejected work, rig moves and crew changes—rather than assuming their absence from a dedicated CSV column makes them irrelevant. [CW pp.10–16][cw]; [DDS pp.11, 13–14][dds].

### Amendment register to implement

This is the verified change map. The associated monthly tables must be transcribed from the cited pages; this plan does not duplicate every numeric cell in the Phase 1 extraction appendices.

| Contract / instrument | Issued → effective | Change and implementation consequence |
|---|---|---|
| CW S1, p.39 | 2025-03-24 → 2025-05-01 | Replace `B.23.010`, `B.21.020`, `A.16.010`; monthly `D.41.020` rates. The last published monthly rate carries forward until superseded. |
| CW A1, p.40 | 2025-08-18 → 2025-09-28 | Extend to 2026-03-31. `E.54.010` and `B.23.010` rate rows start **2025-10-01**, not the extension date. |
| CW S2, p.41 | 2025-11-12 → 2025-12-01 | `D.41.020` becomes 228.00; 5% final rate discount on `C.32.030`, `C.32.010`, `D.41.020`, `B.23.010`. |
| CW A2, p.42 | 2026-02-16 → 2026-04-01 | Extend to 2026-09-30; monthly `E.54.010`; discount on the same four codes becomes 8%. |
| CW A3, p.43 | 2026-05-12 → **2025-11-01** | `C.32.010` becomes 1,984.00; `A.14.010` becomes 56.80; protect earlier submissions and account for one later adjustment. |
| DDS S1, p.38 | 2025-05-19 → 2025-07-01 | `DD-120` becomes 398.50; `DD-121` becomes 2,984.00; monthly `HC-601`. |
| DDS A1, p.39 | 2025-11-07 → 2026-01-01 | Extend to 2026-06-30; replace `DD-101`, `MW-301`, `LW-401` rates. |
| DDS S2, p.40 | 2026-02-24 → 2026-04-01 | Monthly `DD-120`; 4% final service-rate discount on `DD-101`, `MW-301`, `LW-401`, `DD-120`, `MB-701`. |
| DDS A2, p.41 | 2026-05-21 → 2026-07-01 | Extend to 2026-12-31; replace `MW-301`, `MB-701`; discount on the same five codes becomes 7%. |
| DDS A3, p.42 | 2026-08-17 → **2026-02-01** | `DD-120` becomes 416.00; `DD-101` becomes 1,954.00; protect earlier submissions and account for one later adjustment. |

**Decisions supported now:** DDS A3 was issued after S2 and its footer expressly governs overlapping rates from its effective date. Its `DD-120` rate therefore supersedes S2's monthly rate within A3's scope, subject to pre-issue submission protection. Do not retain S2 merely because a month in its table is later than A3's effective date. A3 changes rates, not the separately applicable 4%/7% discount regime. Likewise, A2's “before that date” discount wording does not erase the earlier S2 regime: the saving/precedence wording preserves earlier instruments for earlier work. [CW pp.41–43][cw]; [DDS pp.35, 40–42][dds]. Adjustment placement and issue-day handling remain separate open questions in §9.

## 4. Claims, records and charge identification

Keep three things separate: **what was billed**, **what the record states**, and **what the contract permits**. A successful join proves only that a file exists.

### Loading and provenance

Preserve source filename, CSV row/line reference, original strings and raw monetary values. Parse dates using the observed file formats; use full well and work-area identities. Money enters exact decimal arithmetic from strings and becomes integer minor units only at export. Missing numeric values, failed parsing and true zero must remain distinct.

For every derived evidence fact, retain the source file and line/span, extraction rule version and any competing interpretation. A line trace must be able to show its raw claim, linked evidence, identified charge, applicable term versions, state inputs, quantity decision, each rounded price step and all findings.

Recheck uniqueness, joins and template coverage as input assertions, not as invoice classifications. Treat `DS-900` as an invoice-level deduction: its observed blank day/report fields are not a missing daily report. Keep headers' `adjustment` fields despite all 2,806 being `0.00`; that observation cannot deactivate contractual adjustment rules. [CSV inputs][ci]; [drilling inputs][di]; [DDS p.8][dds].

### Civil evidence specification

| Record family | Required billed codes | Extract and validate |
|---|---|---|
| DX | `A.12.030`, `A.12.040` | Date, area, quantity/unit, trench depth, ground where stated; depth determines the priced trench item. |
| CT | `A.14.010`, `D.41.010`, `D.41.040` | Distinguish fill, sub-base and capping; extract quantity and its physical unit. |
| PR | `B.21.020`, `B.21.030`, `B.21.040` | Distinguish foundation, slab and wall pour; extract cubic quantity. `PR` here is a ticket prefix, not a preliminary charge code. |
| PT | `C.31.020`, `C.32.030` | Distinguish pipe length from chamber count/type. |
| MO / PS | `E.51.010` / `E.51.030` | Attendance hours and reason for standing; apply qualifying conditions and the first-hour rule. |
| DW | `A.16.010` | Week, individual days worked, area and weekly quantity; require at least five days. |
| CV | `C.35.010` | Surveyed drainage length, area and date. |
| JS | `B.23.010`, `B.23.020`, `E.52.010` | Reinforcement mass, mesh area or chainage-band count; survey tolerance applies to the appropriate quantity. |

All required tickets need the foreman's signature and Engineer's countersignature; underscore placeholders are not signatures. Ordinary site words such as “cube” may be normalized in **evidence**, without converting an invoice's wrong scheduled unit. [CW pp.8, 13–14, 27, 32–33][cw].

Direct examples to use later as parser fixtures include `DX-00001.txt`, `CT-00001.txt`, `PR-00001.txt`, `PT-00001.txt`, `MO-00001.txt`, `DW-00001.txt`, `CV-00001.txt`, `PS-00001.txt`, and `JS-00001.txt`. All were reread in Phase 2. `DW-00001` crosses a month boundary: its heading date must not be required to equal every linked line's date. Reconstruct the year's day list correctly at year boundaries too. [Civil records][cr].

The Phase 1 exceptions—three missing ticket IDs, four blank references on Schedule 5 codes, a wrong-family link and a placeholder countersignature—are review seeds, not preassigned invoice outcomes. For codes outside Schedule 5, a blank reference is not itself a breach of that schedule. Do not infer missing quantities for those codes or reject them solely because no ticket was prescribed.

### Drilling evidence specification

Index the internal `Report:` number, then validate contract, full well, rig and date. Do not construct the join by guessing the filename from a shortened well number. Every service-day line must be checked against Part A and required signatures; service-specific parts add conditions:

The required DDS signatories are the Company Representative and the lead directional driller. Preserve any revision/delivery timing available in the source; under R8, a corrected report must be signed by both before the relevant invoice is submitted. Do not invent timestamps or treat an undated supplied record as proof of its delivery date. [DDS pp.5, 14][dds].

| Part | Facts and uses |
|---|---|
| A | Authoritative daily status/section, depths, circulating/back-reaming hours, crew, tools and event counts. Compare claimed context with this evidence without silently repairing the invoice date. |
| B | Run identity, first/last dates, tools/source status and run totals. Required for `DD-111`, `LW-410/411/412/413`, `RM-510`. Repeated run totals are one fact, not quantities to sum once per daily report. |
| C | Daily gyro surveys for `DD-130`; compare with Part A. |
| D | Source run and certification for `LW-420`; tie it to the qualifying run and its first day. |
| E | Tool lost, run and accumulated hours on that well for `LH-711…714`; price the loss once, on its date. |

There are no separate run/survey/source/loss documents to demand. Apply the **complete Appendix G mapping**, including `night man → DD-102`, `gamma tool → LW-410` or `LH-714` in loss context, `MWD collar → MW-310/LH-713`, and `float sub → HC-640`. Similar Schedule 1 wording is not grounds to change that explicit map. [DDS pp.5–7, 14, 24, 35–36][dds].

Reread examples suitable for later fixtures are `DDR_NGP-BD-011_20260225.txt` (A–C), `DDR_NGP-BD-011_20260318.txt` (A/B/D), and `DDR_NGP-BD-020_20250421.txt` (A/B/E). They expose daily versus run quantities and the distinction between source handling and loss. [Drilling records][dr].

**Mismatch, reuse and duplication must have separate finding types.** A wrong-day report does not prove a second charge. A report legitimately supports several service codes. A weekly civil ticket reused on another date requires event/quantity analysis. Agent 2's counterexample, `MDS-00164-050` linked to `DDR-107-20250305`, belongs in a negative duplicate test. Only a proven repeated charge under the relevant contractual scope triggers a duplicate consequence. [Agent 2 §3, B1/B4; CW p.8][cw]; [DDS p.7][dds].

## 5. Required checks and monetary calculation

Every invoice must receive the following twelve results in guideline order, even if shared facts are computed earlier. A result is pass, finding, unresolved or not applicable with a reason. Failure of an early check must not suppress useful later checks. [Civil guidelines][cg]; [drilling guidelines][dg].

| Check | Required implementation behavior |
|---|---|
| 1. Identity and period | Preserve reference/issuer discrepancies; validate header-line context and period definitions. A plausible typo is not silently rewritten. |
| 2. Active term | Apply all extensions to work/service dates: CW 2025-01-05 through 2026-09-30; DDS 2025-01-01 through 2026-12-31. A later submission can concern valid earlier work. |
| 3. Submission window | No submission before period end; CW at most 21 days after, DDS at most 30. Check line containment and contract-specific period definitions separately. |
| 4. Required evidence | Reference existence, correct family/day/week/run, semantic activity, required parts and signatures; not simply nonblank fields. |
| 5. Quantities | Establish permitted quantity from the correct evidence scope, first-hour provisions, tolerances, minimums and caps. Do not automatically increase every underclaimed quantity to its record maximum. |
| 6. Priced item | Compare claim with the supported activity and unit; preserve genuinely competing matches. Do not pick the cheapest item or the item whose rate happens to reconcile. |
| 7. Rate version | Resolve by work date and instrument issue order, with separate treatment of pre-issue retrospective protection. |
| 8. Build-up | Apply eligible factors/discounts only, in contractual order with explicit decimal rounding points. |
| 9. Limits | Evaluate all relevant local and historical caps, exclusions, run/well events and minimums. |
| 10. Duplicates | Use contract-specific event identity, applicable exceptions and explicit allocation of the disallowed occurrence. |
| 11. Arithmetic | Check billed arithmetic independently, then reconstruct expected monetary components. Recompute deductions/tax after corrections; do not sum overlapping error deltas. |
| 12. Outcome | Retain clauses, evidence, expected amount or unresolved amount status, all findings and confidence basis. An unflagged row requires actual check coverage. |

### Civil valuation

For each supported measurement:

1. Identify its scheduled item/unit and eligibility. **CW clause 26 rejects a quantity in a different scheduled unit in full; do not convert it into an accepted charge.** This consequence is mandatory, not merely a warning. Record synonyms used in tickets do not weaken this rule. [CW p.6][cw].
2. Establish measurable quantity, including recorded-week qualification, chargeable hours, surveyed tolerance, daily limits, exclusions and duplicates. Keep physical evidence, measured quantity and currently payable quantity distinct where evidence-delivery rules differ.
3. Select the applicable base/substituted/monthly rate. For `B.23.020`, `B.25.010`, `C.32.040`, convert USD using **halalas per USD divided by 100**, then round half-even to a halala. For indexed `C.31.010`, `D.41.030`, apply the work month's index/base-100 and round half-even before build-up. A published monthly replacement price is not an index multiplier. [CW pp.21–22, 32, 39–42][cw].
4. Apply zone → eligible ground → eligible night → eligible rest-day → annual quantity-band percentage → current principal-item discount. Round the resulting rate half-up once, then multiply the applicable quantity segment by that rounded rate. Sum separately priced segments when a band is crossed. Do not require every legitimate split line to equal total quantity times its one displayed rate. [CW pp.6, 24–26, 41–42][cw].
5. Sum supported line amounts for the measured application total. Calculate retention, release and retrospective payment adjustments separately as described in §8.

Mandatory exceptions: zones apply to A–D, not E; ground factors only to Schedule 3's listed codes; take G2 for work after 2025-09-27; suppress night uplift where the applicable zone factor exceeds 1.1; Friday/Saturday are rest days; when both uplifts could apply, use rest-day alone without the specified written instruction. The first hour of attendance is excluded. Survey claims up to and including 102% of the survey are payable as measured; above that, revert to the surveyed quantity, not 102%. [CW pp.3, 13, 20, 23–27, 32–33][cw].

Both excessive and deficient contractual rates must be detected. A lower billed rate is not automatically acceptable merely because it benefits the payer. Conversely, a lower quantity permitted by a “payable as measured” clause is not automatically an omitted charge.

### Drilling valuation

For each supported service/event:

1. Establish well/day/run, actual crew/tool presence, correct service/unit, Operating/Standby status and quantity. Use Part A daily depths for daily footage and the required Part B evidence; do not substitute a repeated run-total quantity for every daily charge. Apply source certification/loss evidence and special-day exclusions where relevant.
2. Select the versioned rate. Index `MW-310` and `HC-620` using the service month; split `PD-210` by 1,500/3,000/4,500 m depth boundaries and, independently, any contract-year footage boundary. Apply the annual percentage to each applicable depth-priced segment: 100% through 40,000 m, 96% through 120,000 m, then 92%, with half-even rounding at the monetary step. A depth boundary belongs to the shallower band. Footage bands are **per well and Contract Year**, explicitly settled by Schedule 2 Part 2; the qualifying metre population still needs an explicit definition. [DDS pp.6, 17–18, 35][dds].
3. Apply section → well class → standby → effective selected-service discount, rounding half-even to cents at each applicable step. Section factors do not apply on Standby; well-class factors do not apply to `PD-210`. Eligibility lists govern, not every service in a name family. [DDS pp.6, 20–22, 35, 40–41][dds].
4. Price loss items from Schedule 2D's SAR replacement amount divided by the loss month's SAR-per-USD exchange value; round the USD value half-even before depreciation. Depreciation is 1% per complete 25 accumulated circulating hours on the well, including the loss day, capped at 50%; round as required. Do not use the old fixed USD Schedule 6 values. [DDS pp.7, 11, 19, 25, 35][dds].
5. Multiply allowed quantities by built-up rates; sum services, recompute `DS-900`, net, VAT and invoice total. Keep selected-service rate discounts distinct from the invoice discount.

`DD-120` is an Operating-day hourly service with a six-hour minimum when the tool is in the hole; `DD-121` replaces it on Standby. Hourly rig-up and minimum interactions remain an explicit decision item, not an unexamined `max` formula. Metre claims up to and including 101% of support are payable as charged; beyond it, revert to supported metres. Preserve the depth-interval requirements when applying that tolerance. [DDS pp.6–7, 22, 35][dds].

Use evidence-driven reverse checks for **contractually required** deductions, adjustments, minimums and timed events that may be missing from the claimed lines. Do not turn every unbilled record fact into a new charge: determine whether the contract requires inclusion on this invoice and avoid claiming quantities on the contractor's behalf without a contractual basis.

## 6. Cross-invoice state and ordering

A global sequence sorted by invoice ID is wrong. Different rules need different histories. Build these histories from the complete population and supporting evidence, with explicit identities and before/after states:

| State | Key / ordering | Required behavior and safeguards |
|---|---|---|
| Civil annual measured quantities | Contract + item + Contract Year; execution date, then application number and line number as the working ordering convention | Reset on 5 January, not an extension or invoice boundary. Split only the part crossing each band. Schedule 4 substitutes clause 30; document preservation of its unchanged chronological tie ordering. Resolve which measured quantities enter the state before trusting downstream rates. [CW pp.6, 24–25, 32.] |
| Civil daily caps | Item + work area + work date, across applications | Aggregate at the work-area level, not zone; excess cannot move to another day. Do not apply a cap independently to each invoice. [CW pp.6, 20, 26.] |
| Civil exclusions | Work area and dated measurements | `A.14.020` following `A.14.010`; same-day `E.51.020` exclusion when one of `D.41.020`, `D.41.030`, `D.41.050`, `D.43.010`, `D.43.020` is measured. Test same-day and day-2/day-3 boundaries explicitly. [CW pp.6, 13, 26.] |
| Civil duplicate measurements | Same item + work area + work date, within/across applications | **Disallow the later measurement in full**, not a proportional reduction of both. Establish “later” using available chronology; unresolved ties stay visible. A weekly record repeated on different dates needs separate evidence/event analysis. [CW p.8, clause 44; pp.27, 33.] |
| Drilling daily limits/duplicates | Full well + date + service; interval identity for `PD-210` | Check daily aggregate limits across invoices. Preserve legitimate nonoverlapping PD-210 depth charges; test overlap/repeated intervals rather than rejecting all same-day PD-210 lines. Clause 29 does not itself supply civil's later-copy allocation rule. [DDS pp.6–7, 20–22.] |
| Drilling run events | Full well + BHA run, corroborated first/last dates | `DD-111`: motor run, once on last day. `LW-420`: source run, once on first day with required certification. Repeated Part B metadata does not create repeated events. Reconcile conflicting run metadata before pricing. [DDS pp.7, 24.] |
| Drilling well events | Full well and complete supported day history | `MB-701`, `DD-140` on first day; `MB-702`, qualifying `LW-430` on last day. Derive boundaries from records, not merely dates of billed lines; check whether observed endpoints reliably represent spud/release. [DDS pp.3, 7.] |
| Drilling annual footage | Full well + Contract Year; dated physical intervals | Reset on 1 January. Count each qualifying interval once and preserve depth-band segmentation. Do not aggregate across wells; do not omit the rule merely because the observed population may never reach 40,000 m. [DDS pp.17, 35.] |
| Loss history | Full well + identified lost tool/event | Use Part E's accumulated hours and corroborating history; do not substitute the run total or campaign hours. [DDS pp.7, 11, 24, 35.] |
| Retrospective adjustments / retention | Contract and, where justified, well or valuation scope; actual submission dates | Distinguish work ordering from submission ordering; process adjustments/releases once and retain the original affected lines. Scope/tie questions are in §9. [CW p.32; DDS p.35.] |

Never conflate physical work, accepted measurement, payment eligibility and previously certified/invoiced amounts. An unsupported payment is not proof that work never happened; a duplicate claim is not extra physical quantity. The state specification must say which quantity each accumulator uses, with a source or a disclosed assumption.

Do not let incidental CSV order decide an allocation. Use a stable tie-breaker for reproducibility only after documenting that it is a convention rather than a contractual fact. Where allocations change invoice-level results, retain both possibilities until adjudicated. Corrections to an early measurement must trigger replay of every later dependent band, exclusion or adjustment calculation. At this dataset size, a complete deterministic rerun is safer than maintaining intricate incremental caches.

## 7. Retrospective amendments: separate two valuations

The system needs a valuation of an invoice under the terms applicable **when it was submitted**, and a separate account of a subsequent retrospective difference. Selecting the final rate table for all historical invoices would incorrectly flag protected submissions. Selecting rates only by submission date would misprice ordinary work-date changes. [CW pp.32, 43][cw]; [DDS pp.35, 42][dds].

For each A3:

1. Identify the affected codes and work-date interval; retain work date, original submission date, instrument effective date and issue date separately.
2. For submissions before issue, retain the rate regime then applicable. Protection applies to the retrospective change only; unrelated errors are still auditable.
3. For eligible submissions once the amendment is available, select amended rates for work within its effective scope, preserving work-date factors, quantity bands and discounts. Do not substitute the discount prevailing on the adjustment date for the original work-date discount.
4. Identify work already valued/certified or services already invoiced that qualify for catch-up. Civil certification is not independently represented by a separate dataset, so the use of submitted applications as its proxy needs disclosure.
5. Revalue that same eligible population under the old and amended rate regimes, isolating the amendment's effect from unrelated invoice corrections. Preserve line-level differences, including negative differences where a replacement rate is lower.
6. Post one adjustment to the eligible receiving submission and nowhere else. Never both revise the historical judged total for the same retrospective difference and charge that difference again later.
7. Reconcile total accrued differences with the posted adjustment and any explicitly unresolved balance. Resolve the discount/VAT and judged-field treatment before final amount output; an aggregate raw rate difference alone is insufficient.

The “after” versus “on or after” wording is materially relevant, not hypothetical. Direct inspection of the header files confirms three CW applications dated 12 May 2026 (`PA-00006`, `PA-00023`, `PA-00380`) and one DDS invoice dated 17 August 2026 (`MDS-01625`). Those are date observations, not decisions about their correctness or adjustment entitlement. [CW headers][ch]; [DDS headers][dh].

Required miniature histories include work before/at the effective date, a protected submission before issue, an issue-day submission, multiple first-date candidates, old work submitted later, a month whose S2 rate exceeds A3, and an adjustment already present. The latter must work in a synthetic fixture despite the actual adjustment columns being all zero.

## 8. Expected totals and payment consequences

Maintain separate results for **document compliance**, **contract-supported measured/service value**, **payment due/withheld**, and **the README's judged total**. A procedural payment hold does not necessarily make the contract value zero. CW clause 43, for example, says an arithmetically inconsistent application is returned unpaid; that does not justify exporting zero as the correctly summed application total. [README, Data and Task][readme]; [CW p.8][cw].

| Component | Civil | Drilling |
|---|---|---|
| Billed total for export | Original `application_total` × 100 | Original `invoice_total` × 100 |
| Ordinary expected total | Sum of correctly valued measured lines, including separately priced band segments | Corrected service subtotal, less the contractual invoice discount, plus VAT |
| Invoice discount | No DDS-style discount | Half-even rounding of 4% of the service subtotal **above** USD 250,000; zero at/below threshold; one negative `DS-900` charge |
| Tax | Do not import DDS's VAT into CW; the supplied CW schema and valuation provisions do not establish that addition | Half-even rounding of 15% of corrected net; total = net + VAT |
| Payment fields | 5% retention rounded down to the halala; first eligible release is half earlier retention, rounded down; clause 45A payment = measured total + retrospective adjustment − retention + release | Keep adjustment separately traceable; its interaction with net/discount/VAT requires an explicit interpretation |

[CW pp.6, 8, 17, 32][cw]; [DDS pp.8, 35, 40–41][dds].

Recompute the whole invoice after supported corrections. Removing a drilling service may move the subtotal below the discount threshold and change VAT; simply subtracting its billed amount from `invoice_total` is wrong. Likewise, two findings on the same line must not deduct that line twice. A duplicate rejected in full can also have an incorrect rate, but its allowed monetary contribution remains one value.

Before final outcomes, freeze a **consequence table**, distinguishing:

- **Explicit full rejection:** civil wrong-unit quantities and the later proven civil duplicate; explicit nonchargeable services/work after the final term. Apply to the affected charge, not automatically every line on its invoice.
- **Quantity/rate correction:** use the supported quantity or rate under the applicable exceptions; preserve both overbilling and underbilling findings.
- **Conditional payment eligibility:** missing required evidence/signatures/parts; distinguish currently unsupported payment from eventual entitlement, and civil P23's next-valuation recovery from an immediate correction. Avoid recovering the same amount twice.
- **Procedural discrepancy:** identity, period or submission-window failures. Record the breach; derive a supported monetary total independently where possible instead of imposing a blanket zero without a clause.
- **Payment-only discrepancy:** retention, release or adjustment effects outside the selected judged field. Keep the finding and amount consequence separate; the binary submission treatment of payment-only defects is an open reporting interpretation.

A flagged row may legitimately have no change to its judged total if the defect is nonmonetary. Conversely, offsetting errors can leave the billed total unchanged while the invoice is wrong. Neither `flagged` nor pass status should be derived solely from total inequality.

Genuinely unknown expected totals stay **unknown internally**, with missing facts or competing supported values identified. No automatic zero, blank, billed-value copy or midpoint is authorized as a substitute for knowledge. For an ambiguous but priceable case, choose and disclose the strongest source-supported reading, retain alternatives, and lower confidence appropriately. For a genuinely unpriceable case, the README still requires the row but does not specify the numeric encoding; resolve that export convention before G7. If it remains unresolved, disclose the incompatibility rather than silently omit the row or claim a contract-supported amount. This is a final-output issue, not a reason to stop work on all other invoices. [README, Task][readme]; [guidelines, principle 3][cg].

## 9. Material open questions and how to handle them

The following are real decision tasks. They are not permission to reopen explicit terms such as per-well footage scope, civil unit rejection or the two rounding regimes. Address each by reading its cited provisions together, writing a small contrasting case, and assessing which results depend on it. Billing may expose a problem with a reading but cannot settle it by majority vote.

| ID | Question / evidence | Next action, scope and stopping rule |
|---|---|---|
| **Q1** | A3 adjustment recipient: “after” versus “on or after”; CW ties; DDS per-well invoicing versus the singular first invoice. [CW pp.32, 43; DDS pp.8, 35, 42.] | Compare the specific amendment and incorporated clause; inspect candidate submission dates and available ordering evidence. Retain strict-after/inclusive and any justified per-contract/per-well variants. Do not place the entire adjustment on every candidate or arbitrarily select the smallest ID. Finalize affected amounts only under an explicit logged reading. |
| **Q2** | Adjustment financial basis: already certified versus submitted CW work; placement against `application_total`; DDS treatment under `DS-900` and VAT. [CW pp.8, 32, 43; DDS pp.8, 35, 42; README.] | Define the prior population, historical basis and receiving-invoice accounting, separately for each contract. The preferred CW field separation is measured total versus clause 45A cash payment; do not silently put cash payable into the judged field. Preserve alternative adjustment treatments and request narrow clarification if the supplied terms remain insufficient. |
| **Q3** | Missing-record consequence now versus P23 recovery from the next valuation; no delivery/certification timestamps. [CW pp.8, 14, 27.] | Determine what absence in the supplied repository establishes, and whether the charge was already certified. Keep a current-payment hold and later recovery as linked events, never two independent deductions of the same obligation. Record any proxy used for delivery/certification. |
| **Q4** | DDS hourly quantity: first hour of each “period in the hole,” daily minimum, and circulating/back-reaming scope. [DDS pp.6–7, 22, 27–28, 35.] | Use daily/run boundaries to test possible period definitions and minimum-before/after-deduction effects; do not equate a BHA run with a chargeable period without evidence. Separate DD-120 and RM-530. If the data cannot distinguish readings, retain that limitation rather than treating reconciliation as proof. |
| **Q5** | DDS Schedule 8 conflicts: DD-102 coordinator versus tool; HC-630 BHA run versus clean-out count; generic metre descriptions. [DDS pp.6–7, 27–29, 36.] | Apply express schedule precedence, then reconcile internal schedule text, referenced clauses and glossary. DD-102's introduction and glossary support coordinator evidence, but acknowledge the contradictory row. Freeze a reasoned service-specific interpretation; retain alternatives where the event or quantity changes. No blanket “specific clause always wins” shortcut. |
| **Q6** | Civil band-state quantity, preservation of ordering after clause 30 substitution; daily cap/duplicate allocation; exclusion endpoints. [CW pp.6, 8, 24–26, 32.] | Distinguish measured from merely claimed or unpaid quantities. Test cases where a rejected early claim changes a later band. Use the old execution/application/line order as a documented working convention where unchanged, not as evidence that all other state questions are settled. Examine day 0/1/2/3 and same-day ties. |
| **Q7** | Weekly evidence reuse and drilling duplicate allocation. [CW pp.8, 27, 33; DDS pp.7, 24.] | Prove repeated charging of the same supported event, considering quantities and dates. Repeated references alone are insufficient. Do not transfer CW's full-later-copy rule to DDS without a supporting basis. |
| **Q8** | Missing background evidence: call-offs/performance-section nomination, written uplift instructions, permits and well endpoints. [CW pp.3, 13, 15; DDS pp.3, 6–7, 29.] | Distinguish a missing prescribed invoice record from a background document not supplied anywhere. Use explicit defaults only where the contract gives them (e.g. CW concurrent uplifts). If consistent header class or observed first/last report dates must serve as proxies, disclose them and check contradictions. Do not manufacture instructions or mark every invoice wrong for a globally unprovided document. |
| **Q9** | Binary treatment of payment-only defects; unknown expected-total encoding; confidence semantics and undefined severity. [README; CW pp.8, 32.] | Keep internal compliance, payment and judged-total outcomes separate. Use the README's row-confidence meaning; never redefine confidence as probability of being wrong for every row. Ask only a narrow submission-semantics question if needed; do not invent organizer severity cutoffs or amount tolerances. |
| **Q10** | Possible omitted charges and underbilling versus acceptable partial claiming. [CW pp.6, 32; DDS pp.6–8, 35.] | Apply explicit minimum/once-only/discount obligations and correct contract rates in either direction. Determine inclusion in the specific invoice before adding an unclaimed item; record evidence alone does not prove all possible charges must appear there. |
| **Q11** | Remaining DDS quantity/consequence details: which drilled metres enter the annual accumulator; metre tolerance versus depth intervals/caps; wrong-unit monetary consequence. [DDS pp.6–8, 17, 35.] | The per-well scope is settled. Specify whether its accumulator includes all physical drilling or only performance-chargeable footage, without double-counting logged/reamed metres. Test tolerance at split boundaries. Clause 35 requires scheduled units but does not state CW clause 26's full-rejection remedy; do not import that remedy without justification. |

A question is closed by a defensible source reading and a discriminating case, or is retained as an explicit assumption with identified consequences. Initial investigation should be timeboxed; unresolved questions need visible ownership and affected scopes, not unlimited debate. Low-impact unresolved issues must not consume the budget reserved for testing and final reproduction. [README, Ground rules][readme].

## 10. Establishing correctness without labels

There is no public truth set. The implementation must establish **contractual consistency, extraction correctness and reproducibility**, while honestly limiting claims about detection performance. Do not report F1, recall or calibrated probabilities from unlabelled reconciliation rates.

### Independent checks before a rule is trusted

1. **Verify the source, not just the transcription.** Check every numeric table and exception against the image in a separate pass. Compare Phase 1A/1B extraction as an additional cross-check, not two votes overriding the scan. Mark unreadable cells unresolved. Store the exact source and reviewer note for every disagreement.
2. **Create small source-derived reference cases before the corresponding rule code.** Calculate expected intermediate steps independently with a calculator or separate minimal worksheet. Do not obtain expected test values by calling the production valuation function or importing its computed outputs.
3. **Test parsers independently of billing.** Annotate raw records before comparing with invoice claims. Cover every civil family, all DDR parts, each encountered narrative variant, missing/placeholder signatures, month/year-crossing weeks and repeated run metadata. Every unparsed relevant field goes to a visible queue; it must not default to zero or become a pass.
4. **Use complete-invoice reference reviews.** Start with about 12 civil and 24 drilling invoices chosen for rule coverage, not suspicious prices, then add only cases needed for uncovered interactions. Work from records and terms before inspecting billed reconciliation. Include multi-invoice histories and several apparent passes. These are reviewer-adjudicated fixtures, not organizer labels.
5. **Protect a small review sample from rule tuning.** Predetermine a reproducible sample within both contracts and major periods/service families. Review it after rules are frozen; do not repeatedly choose the interpretation that fits that sample's billed values.

### Required boundary and interaction cases

| Family | Cases that must discriminate between plausible mistakes |
|---|---|
| Rates/time | Day before/on/after every operative rate/discount/extension date; CW 28 September versus 1 October; monthly carry-forward; issue date versus effective date; preserve 5%/4% before the later 8%/7% regime. |
| Rounding/FX | Exact half-cent/halala cases; CW intermediate half-even then final half-up; DDS half-even at each factor; retention floor at one-halala boundaries; halalas-per-USD conversion in both directions. No binary-float tolerance to mask disagreement. |
| Quantities | Wrong invoice unit versus harmless record vocabulary; 102%/101% exactly and just above; first hour, zero/low hours, minimum and cap interactions; evidence quantity below/above the claim. |
| State | Last unit below/at/above every band; one line crossing a band; January anniversaries versus extensions; rejected/duplicate early quantities; same item/day in different areas versus the same area. |
| Duplicates | Repeated report supporting different services; wrong-day reference with no second charge; legitimate split PD-210 intervals; overlapping intervals; weekly ticket reuse that has and has not been proven to repeat a charge. |
| Drilling events | Tool absent/present; Operating/Standby; eligible standby percentages and nonchargeable services; run first/last day, source certification; LWD conditional final processing; loss at 24/25 hours and at the 50% depreciation cap. |
| Totals | DDS subtotal below/at/above 250,000; missing/duplicate `DS-900`; service correction crossing the threshold; VAT recomputation; offsetting errors; civil gross versus retention/net; one adjustment posted once. |
| Uncertainty | A record parsed confidently but semantically mismatched; an explicit ambiguity changing amount only versus changing the binary decision; inability to price without a required fact. |

Add a limited set of invariants and controlled mutations that test real risks: input reordering cannot change results; adding another well cannot change an existing well's annual footage; adding another work area cannot consume a civil area's daily cap; repeating a run summary cannot multiply a run charge; changing one rate affects only its eligible dates/codes and downstream monetary dependencies. Invariants must respect real cross-invoice effects rather than assume all invoices are independent.

### Population review and containment

After the reference cases pass, compare contract-derived and billed quantities, rates, line amounts and header components separately. Group residuals by rule version, code, date regime, evidence pattern and rounding stage. A broad mismatch is a trigger to recheck a shared assumption, not an instruction to force reconciliation.

Maintain a dependency index from term/mapping/decision to affected lines, state histories and invoices. If a shared extraction or interpretation is unverified, quarantine its dependent conclusions from high-confidence release. Fix the rule, rerun its reference cases, then replay the complete dependent history. A high overall match percentage cannot excuse an untested rare rule or a systematic small error.

Review all unresolved groups, competing duplicate/adjustment allocations, parser failures and material disagreements between interpretations. Manually inspect every distinct loss-record pattern and all cases where loss valuation differs from the verified calculation; the 54 Part E records are small enough for complete evidence review if needed. Inspect at least one full trace from every finding mechanism, all exceptional high-impact cases, and a reproducible stratified sample of apparent passes. Expand testing only to resolve a specific uncovered branch or failure.

The release evidence is a coverage matrix, source-checked reference results, explained residuals, sensitivity results and a reproducible rerun. There is **no acceptance target for flag count or billed-rate agreement**.

## 11. Decisions, categories and confidence

Use an internal finding ledger with rule ID, invoice/line/event, evidence, clause, finding type, monetary consequence, uncertainty and review status. Distinguish confirmed breaches from suspicions and from rules that do not apply. One unresolved identification must not silently become a “correct” line because no amount was produced.

Use consistent categories such as identity/period, term, submission timing, missing evidence, signature, evidence mismatch, unit, quantity, duplicate, charge eligibility, rate/factor, discount, rounding/arithmetic and retrospective/payment adjustment. Record all independent findings internally. For the free-text submission field, use a stable ordered combination of applicable categories, avoiding redundant symptoms of the same cause; leave it blank only for an unflagged row. The final short report groups **failures of the method** into three or four systematic types, not merely a catalogue of these invoice categories.

Track decision confidence and amount confidence separately internally. The exported `confidence` describes confidence in the selected row, including its chosen amount, rather than `P(wrong)` regardless of `flagged`. Use the weaker materially relevant basis when a clear breach has an uncertain amount. Do not multiply correlated check confidences or treat a large set of matching lines as independent proof of a shared rule.

A provisional, reproducible rubric can use the following levels, finalized before export:

| Indicative value | Basis |
|---|---|
| 0.95 | Clear operative rule, verified extraction/evidence, independently checked calculation and complete applicable-check coverage; no material open dependency. |
| 0.80 | Strong supported result with a disclosed limited assumption; reasonable alternatives do not change the material conclusion or chosen amount. |
| 0.60 | A disclosed interpretation is needed and credible alternatives change the outcome or amount. |
| 0.30 | Material missing evidence or an amount that cannot be established reliably; requires an explicit query/export policy. |

These are judgment conventions, **not empirically calibrated probabilities or source-defined thresholds**. Review both flagged and unflagged samples within each band for consistency, and lower a whole dependent group if a common assumption weakens. High-confidence apparent passes require all relevant checks, not just arithmetic agreement. No row should receive a high value merely because a parser matched.

The 5:1 false-negative/false-positive cost justifies spending review effort on missed-error risk. A `P(wrong) > 1/6` threshold follows only for that isolated binary expected-cost objective with reliable probabilities; this task supplies neither such probabilities nor a single-objective scoring mandate. Do not mechanically apply that threshold to the row-confidence rubric. Likewise, monetary exposure can prioritize review internally, but it is not the organizer's undefined severity scheme. [README, Scoring][readme]; [Agent 2 §3, qualifications].

## 12. Major failure modes and safeguards

| Failure that can spread | Safeguard / release evidence |
|---|---|
| Incorrect scanned rate, unit, decimal or eligibility list | Two source-image checks of every active table; cited cells; independent boundary examples; dependency index to re-evaluate every affected invoice. |
| Correctly parsed words mapped to the wrong charge | Contract glossary and contextual mappings; blind record annotation; preserve alternatives; no nearest-price matching. |
| Repeated evidence treated as repeated work, or date mismatch treated as duplication | Separate link validity, event identity and prior charge tests; negative fixtures from Agent 2; depth and weekly exceptions retained. |
| Wrong quantity/state scope contaminates later invoices | Explicit keys and clocks, separate measured/payable quantities, full-history fixtures, before/after state traces and complete replay after changes. |
| Retroactive rates imposed on protected history or adjustment charged repeatedly | Separate original valuation and adjustment account; issue/effective/submission matrix; sum-of-differences reconciliation and exactly-once posting checks. |
| Wrong rounding or financial field | Decimal operations with named rounding points; independent arithmetic check; gross/payment separation; DDS discount and VAT recomputation. |
| Billing agreement or stated prevalence becomes circular validation | Freeze source readings/reference cases before population reconciliation; held-aside review sample; no quota or agreement threshold. |
| An unresolved rule silently becomes a pass or a confident total | Explicit unknown states; per-invoice check coverage; confidence caps and source-linked review queue; export policy checked before release. |

These failure mechanisms should also shape the final method-error report: source/interpretation failures, evidence/event failures, chronology/state failures, and monetary aggregation/rounding failures are plausible groups. Use actual validation findings or documented limitations as examples; do not invent labelled “misses.”

## 13. Reproducibility and eventual deliverables

Build the eventual runnable repository around a small number of transparent artifacts: immutable source inputs or a commit-pinned retrieval step with hashes; reviewed term/mapping tables; evidence extraction and audit code; reference cases; a detailed audit ledger; and the required reports/prompts. This is an artifact contract, not a requirement for a framework or elaborate directory hierarchy.

Pin the Python/runtime and dependencies actually used, including OCR/rendering tools if regeneration is part of the workflow. Preserve verified extraction artifacts with PDF hashes so reproducing the submission does not depend on nondeterministic OCR or fresh AI output. Record date formats, decimal precision/rounding, stable order conventions, rule/decision versions and any sampling seed. Keep actual prompts and iterations as they occur; disclose AI assistance and do not reconstruct missing prompt history as if it were contemporaneous.

Provide one documented command to reproduce the submission and audit artifacts, plus a verification command for reference cases and output integrity. A clean run must need no hidden notebook state, manually patched invoice output, external service credentials or unversioned local file. Preserve the original template order for straightforward comparison.

The exact submission columns, in template order, are `invoice_id`, `flagged`, `error_category`, `expected_total_cents`, `billed_total_cents`, `confidence`. The shared `_cents` suffix means SAR halalas for civil and USD cents for drilling; it does not authorize converting both into one currency.

| Required deliverable | Final acceptance evidence |
|---|---|
| Runnable repository | Clean clone/install/run reproduces results with pinned inputs, dependencies and decisions. Report runtime and environment from the actual final run. |
| `submission.csv` | Exact six template columns; all 2,806 original unique IDs; binary flags; blank categories only when unflagged; integer native-currency minor units; billed amounts copied exactly from the specified original header field; confidence in [0,1]. |
| Short report | Explain validation evidence, coverage, unresolved scope and actual runtime; analyze three or four systematic method failure types with examples. State that labelled precision/recall/F1 and empirical calibration cannot be measured from this repository. |
| Versioned prompts | Preserve extraction/review/code-assistance prompts and iterations; explicit AI disclosure. |
| One-page decision log | Concise assumptions, conflicting clauses, chosen readings and unresolved consequences; trace to the fuller working register where necessary. |

The final exporter must independently check schema, row coverage, minor-unit conversion and the judged-field mapping. A reproducibility comparison must exclude incidental timestamps from the substantive result comparison. Do not hand-edit the submission after generation; fix a source-linked rule or reviewed decision and regenerate. [README, Deliverables and AI assistance][readme]; [submission template][template].

## 14. Use of the remaining challenge time

Neither the supplied brief nor the user specifies how much time remains. Do not invent an organizer deadline. A reasonable working estimate is **20–30 focused hours after this plan**, conditional on evidence/interpretation review; use 24 hours only as a scheduling example, not a promise or challenge requirement.

| Work allocation | Share of available time | Example if 24 hours remain |
|---|---:|---:|
| G0/G1 source/specification verification and highest-impact questions | 12% | 2.9 h |
| G2 input/evidence extraction and parser validation | 13% | 3.1 h |
| G3 local entitlement, rates and monetary reference cases | 20% | 4.8 h |
| G4/G5 shared state, retrospective accounting and complete totals | 22% | 5.3 h |
| G6 systematic residual review, uncertainty and apparent-pass checks | 23% | 5.5 h |
| G7 clean reproduction and required deliverables | 10% | 2.4 h |

Start with high-dependency uncertainties—amendment accounting, quantity-state basis and hourly/event scope—while verifying common rate and glossary tables. Maintain the decision and prompt logs throughout; do not defer them to the final hour. Build a small end-to-end case in each contract before expanding all families, then fill the complete coverage matrix. Both contracts and all twelve checks remain in scope.

Timebox the first investigation of a disputed clause to roughly 20–30 minutes. If the available evidence does not resolve it, document supported alternatives, isolate the affected population and move on; revisit according to its actual impact. Under a shorter budget, reduce optional presentation and unused abstractions, reuse verified extraction, and prioritize review by shared-rule exposure. Preserve the validation/reproduction reserve and honest uncertainty; do not buy apparent completeness with guessed amounts or a desired flag count.

## 15. Phase 2 completion and time spent

Phase 2 included reading the complete independent audit first, then both supplied understanding reports; rechecking the GitHub commit, both guidelines, CSV populations/schemas and adjustment fields; rereading all nine civil record families and drilling A–E examples; and revisiting the governing clauses, schedules and all instruments. The most consequential passages were checked directly in the scanned pages, including CW pp.6, 8, 32, 43 and DDS pp.17, 27–28, 35, 42.

The immediate implementation handoff is **G0/G1**, using the verified change map, evidence specification, explicit consequence rules and open-question register above. No new Phase 1 discovery exercise is needed; targeted source verification and adjudication remain part of the implementation gates.

**Approximate time spent on Phase 2:** 21 minutes, including source rechecks, planning, drafting and final review. This measures this planning phase only, not the earlier understanding work or the implementation estimate above.

Phase 2 ends with this plan. Implementation requires a subsequent instruction.

[repo]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec
[readme]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/README.md
[cw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/contract/CW-2025-0417-CIV.pdf
[dds]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/contract/DDS-2025-118.pdf
[cg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md
[dg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/guidelines/INVOICE_AUDIT_GUIDELINES.md
[ci]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/invoices
[di]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/invoices
[ch]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/invoices/applications.csv
[dh]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/invoices/invoices.csv
[cr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records
[dr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records
[template]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/submission_template.csv
