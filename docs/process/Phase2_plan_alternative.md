# Phase 2 — Feasibility and Implementation Plan (alternative)

| | |
|---|---|
| Source of truth | `majedzahrani3/invoice-auditing-level-2` @ `aef4924dc32506b4587de8b788b5a947e6beffec` (local clone verified at this SHA) |
| Inputs | the independent Phase 1 audit (read first); baseline understanding report (primary, with A1–A2 applied); supplementary report (with B1–B5 applied; byte-identical to my Phase 1 report) |
| Scope | Planning only. No solver, no production audit code, no invoice classification, no corrected totals, no `submission.csv`, no flag-count target. |
| Task list | `Phase2_TASKS.md` |

**How this plan was grounded.** Every rule this plan depends on was re-checked against the repository rather than against the Phase 1 summaries:

1. **Independent re-read.** Two subagents made verbatim re-reads of the contract clauses; both stopped part-way on a usage limit. Their completed pages (CW pp.1–12, DDS pp.1–8) agree with my Phase 1 page notes on every point.
2. **My own page views.** I viewed the remaining decision-critical pages this phase: CW pp.13–14, 24–27, 32–43 and DDS pp.17, 22, 24, 28, 35, 37, 40, 42.
3. **Read-only data checks.** Twelve small checks produced counts only (§14). None priced, classified or totalled an invoice.

Citations use `CW pN` / `DDS pN`: 1-based PDF pages, which equal the printed footers.

---

## 0. Governing principles (from the source and the independent audit)

1. **Contract text first; billed data second.** Explicit scope and precedence in the contract decide an interpretation. Billed-data reconciliation can *test* a reading, but it is never ground truth and never a flag target.
2. **A finding needs a named rule and named evidence.** A numeric mismatch alone is an investigation item, not a flag. **Mismatch**, **evidence reuse** and **proven duplication** are three different findings.
3. **Prevalence is context, not a target.** The README's 5–8 % describes wrong invoices; the plan never suppresses a supported finding or invents one to approach it.
4. **Five dates stay separate:** work/service date, instrument effective date, instrument issue date, submission date, and the date of a later adjustment.
5. **The judged figure is the invoice total as billed:** `application_total` (civil, SAR halalas) and `invoice_total` (drilling, USD cents). Retention, net payable, release and cash payable are not the judged total.
6. **Genuine open questions stay visible** in a decision register, each with its reading, its alternative and the invoices it touches.
7. **Explicit civil consequences:**
   * A quantity in a non-Schedule-1 unit is rejected in full, never converted (CW p6 Cl.26).
   * Where the same item, work area and date appear twice, the *later* measurement is disallowed in full (CW p8 Cl.44).
8. **Keep it simple.** Build a deterministic Python pipeline with no LLM at runtime. The contracts are transcribed once, verified, and committed as data.

## 1. Major work, dependencies and ordering

| Stage | Work | Depends on | Blocks |
|---|---|---|---|
| **S0** Scaffold | Repo layout; pinned environment; loaders for 5 CSVs + 10,320 records; ID and join invariants; `Decimal` money policy | — | all |
| **S1** Contract terms | Transcribe both contracts into `terms/cw.yaml` and `terms/dds.yaml` with page cites and verbatim quotes; pass the verification gate (§3) | S0 | S2, S4 |
| **S2** Decision register v1 | Record the reading of every open question in §6 with its alternative | S1 | S4–S7 |
| **S3** Evidence layer | Parsers for the 9 civil record families and the DDR parts A–E; vocabulary maps (App G; civil phrase lexicon); signature, area, date and join validity | S0 (parallel with S1) | S5, S6 |
| **S4** Pricing engines | CW build-up and DDS build-up with a per-line trace; golden tests from the contracts' own examples | S1, S2 | S5, S6 |
| **S5** State builders | Contract-Year bands; daily limits; exclusions; duplicate and reuse ledgers; well and run spans; retrospective-adjustment populations | S3, S4 | S6 |
| **S6** Checks | 12-check catalogue producing typed findings (invoice-local and stateful) | S3–S5 | S7 |
| **S7** Totals and decisions | Payable line amounts → expected totals; flag / category / confidence per invoice | S6 | S8, S9 |
| **S8** Validation | Clean-invoice reproduction; blast-radius review; sensitivity runs; independent hand audit; loop back to S2–S7 | S7 | S9 |
| **S9** Submission | Assemble and schema-check `submission.csv` (2,806 rows) | S8 | S10 |
| **S10** Deliverables | README and run instructions, report with failure-type analysis, one-page decision log, versioned prompts, AI disclosure | S8, S9 | — |

**Critical path:** S0 → S1 → S4 → S5 → S6 → S7 → S8 → S9. S3 runs in parallel with S1. No stage may consume a contract term until that term has passed the S1 gate.

## 2. The two contracts' materially different rules (source-checked)

| Topic | Civil CW-2025-0417-CIV | Drilling DDS-2025-118 |
|---|---|---|
| Term (work dates payable) | 05-Jan-2025 → 30-Sep-2026 (p1; A1 p40; A2 p42). Work after the extended date is "not measurable and payable" | 01-Jan-2025 → 31-Dec-2026 (p1; A1 p39; A2 p41). Services after the extended expiry are not chargeable |
| Submission window | Not before the last day of the stated period; within **21 days** of its end (p8 Cl.41) | Not before the last day of the period; within **30 days** after it (p8 Cl.33) |
| Invoice unit | One application per work area/zone; its period = first to last execution day of its items (Cl.40) | One invoice per well; consecutive days; every charge within the period (Cl.32) |
| Rate build-up | Base (instrument rate by work date; Sch 2A index / Sch 2B USD conversion first, each half-even) → zone (Series A–D only) → ground (15 listed items; **G2 for work after 27-Sep-2025**, §27A) → night uplift (13 items; **not where zone factor > 1.1**, §27A) → rest-day uplift (4 items; alone when both apply unless instructed, P11) → band % → discount (S2 5 % / A2 8 % on 4 items, "final factor … after any rebate … before the rounding") | Base (Sch 1; Sch 2 for PD-210; Sch 2C index for MW-310/HC-620; instrument rates and monthly tables) → section factor (6 codes; **not on Standby**, §17B) → class factor (8 codes; **not PD-210**, §17B) → standby % → discount (S2 4 % / A2 7 % on 5 codes, "last factor … before the rounding it requires") |
| Rounding | **Once**, on the built-up rate, half-**up** to the halala (Cl.28). A band-split line is priced part by part at its own rounded rate | Half-**even** to the cent **at every step** (Cl.17; p1) |
| Invoice-level adjustments | None in the judged total. Retention 5 % rounded down is outside it (Cl.45, §45A) | `DS-900` = −4 % of the service sum *above* 250,000 USD, per invoice (Cl.38, P11); VAT 15 % of net (Cl.39); total = net + VAT (Cl.40) |
| Quantity bands | Sch 4 Pt 3 (8 items), "Clause 30 is substituted", counted per **Contract Year** (§3A: CY1 05-Jan-2025 → 04-Jan-2026; CY2 05-Jan-2026 → 30-Sep-2026); a crossing measurement is divided | PD-210 **depth** bands (Cl.23; boundary depth → shallower band; split charges). Sch 2 Pt 2 tier counts "metres already drilled **on the well** in the Contract Year": per well by explicit wording (p17) |
| Caps and limits | Per item, **per work area per day** (Sch 4 Pt 4, Cl.31); excess not payable. E.51.020 ≤ 1 day (Cl.19). E.53.010 per P6 | Per service per day (Sch 3 Pt 5, Cl.22) |
| Exclusions | A.14.020 not measurable within 2 days after A.14.010 on the same work area (Sch 4 Pt 5; P19). E.51.020 barred on surfacing days (P21) | DD-120 only on Operating days, DD-121 only on Standby (Cl.21; Sch 3 Pt 4); "not chargeable" services get nothing on Standby (Cl.20); PD-210 only on nominated performance sections (Cl.23) |
| Hours | First hour of attendance not chargeable (§6A) | First hour in the hole not chargeable (§21A). DD-120 minimum 6 h per Operating day (Cl.21, P10) |
| Tolerances | Surveyed items (Sch 4 Pt 6): payable as measured up to +2 % over the survey, otherwise at the survey figure (§33A over Cl.33) | Metres up to +1 % over the report payable as charged (§25A) |
| Run and well events | — | DD-111 once per PDM run on its last day; LW-420 once per source run on its first day (Cl.26); MB-701/DD-140 on the well's first day, LW-430/MB-702 on its last (Cl.27; Sch 3 Pt 6) |
| Duplicates | Same item + work area + date → the **later** measurement is disallowed in full (Cl.44) | No service twice for the same well and day, **except PD-210 at different depth intervals** (Cl.29) |
| Evidence | 17 items need a Sch 5 record from a named series; signed by the foreman and countersigned by the Engineer's representative (Cl.46–47, P22); a weekly record needs ≥ 5 days worked (§47A) | One DDR per well-day, signed by the Company Representative and the lead directional driller (Cl.15). Parts B/C/D/E are conditions of payment for listed codes; "no separate run, survey, source or loss documents" (Sch 5 p24). Rig words map to codes via App G (§19A) |
| Lost in hole | — | Sch 2D SAR value ÷ month-of-loss FX, half-even, then 1 % per complete 25 h, maximum 50 % (§31A over Sch 6 and the App G footnote) |
| Retrospective instruments | A3 (issued 2026-05-12, effective 2025-11-01): C.32.010, A.14.010. §31A: pre-issue applications "not thereby incorrect"; single adjustment on the first application "on or after" issue (A3 text: "after") | A3 (issued 2026-08-17, effective 2026-02-01): DD-120, DD-101 ("Schedule 2 footage rates are unaffected"). §36A: pre-issue invoice "was correct at the rate then in force"; single adjustment on the first invoice "on or after" issue (A3 text: "after") |

## 3. Contract terms: transcription, verification gate, and change control

**What gets transcribed (S1).** For each contract, one YAML file holds:

* every rate row with its instrument, effective date, issue date and page;
* monthly tables, index and FX tables;
* factor and eligibility lists, uplift and discount scopes;
* bands, limits, exclusions, once-only lists and record requirements;
* the App G glossary;
* the precedence notes.

Every entry carries `page`, `clause` and a **verbatim quote** of the text it rests on. A separate `terms/quotes/*.md` holds the verbatim text of every clause a rule cites.

**Method — two independent reads plus machine cross-checks:**

1. **Read A.** Visual transcription of each page image at native resolution (the Phase 1 page notes are the starting draft).
2. **Read B.** An independent visual transcription by a separate agent or pass that has not seen Read A, and an OCR pass as well. The OCR engine is pinned (tesseract 5 if installable; else `rapidocr-onnxruntime`); if neither is available, Read B is a second visual read only. OCR is used only to diff numbers, never as the source.
3. **Automatic diff** of A against B on every number and every quoted clause. Each disagreement is adjudicated by viewing a zoomed crop of the page, and the resolution is logged.
4. **Internal-consistency assertions:**
   * each instrument's "rate previously payable/chargeable" equals the rate the earlier instrument set (e.g. CW A1 4,385.00 = S1's B.23.010; DDS A3 398.50 = S1's DD-120);
   * each Sch 2D SAR value = the Sch 6 USD value × 3.75;
   * extension arithmetic holds (185, 183, 181, 184 days);
   * the Schedule of Variations tables agree with the instrument pages;
   * monthly tables have no gaps inside their stated range.
5. **Golden examples from the contracts themselves.**

   | Source | Figures to reproduce |
   |---|---|
   | CW App B (p36) | 50.72, 23.74, 91.37; total 15,794.40; retention 789.72 |
   | DDS App B (p30) | 1,477.88; 2,975.75; 509.00; PD-210 split 4,070.50 + 6,498.25; net 25,662.26; VAT 3,849.34; total 29,511.60; the discount example 312,400 → −2,496.00 |
   | DDS App F (p34) | 412 h → 16 % |

   Where an example conflicts with a later clause (CW App B omits §29A indexation of C.31.010; DDS App B omits §17A indexation of MW-310), the test asserts the example's own arithmetic and records the conflict. The later explicit clause governs pricing.
6. **Billed-rate diagnostic, last and advisory only.** The Phase 1 harness reproduced the billed built-up rate on 99.5 % of civil lines. On drilling it reached 97.5 % *before* Amendment-3 timing and exact decimals were modelled. Clusters of disagreement point to a misread term; sparse, scattered disagreement is not evidence of anything about the contract.

**Gate (S1 exit, before S4 may start):**
* zero unresolved A/B disagreements;
* all consistency assertions pass;
* all golden tests pass or carry a logged, source-cited conflict;
* every rule the engine will use has a quote file entry.

**Change control.** Terms are data under version control. A change to a term re-runs the full test suite and the S8 diagnostics, and the diff of affected invoices is recorded in the decision log.

## 4. Checks: invoice-local and cross-invoice / stateful

Every check emits typed findings: `{invoice, line?, check_no, rule_id, clause, finding_type, evidence, amount_effect, interpretation_ids, confidence_tier}`.

### 4.1 Invoice-local checks (guideline order)

| # | Civil | Drilling |
|---|---|---|
| 1 | `contract_ref` = CW-2025-0417-CIV; subcontractor matches p1; period fields coherent (observed: 2 headers carry `CW-2024-0417-CIV`) | `contract_ref` = DDS-2025-118; contractor matches (observed: 2 × `DSS-2025-118`, 1 × `DDS-2025-181`) |
| 2 | Work dates within 05-Jan-2025 … 30-Sep-2026 (observed: 2 lines after) | Service dates within 01-Jan-2025 … 31-Dec-2026 (observed: 3 lines after) |
| 3 | Application date ≥ period_to and ≤ period_to + 21; line dates inside the stated period (Cl.41) | Invoice date ≥ period_end and ≤ period_end + 30; charges inside the period (Cl.32) |
| 4 | Sch 5 items need a ref of the right series. The file must exist, be signed by both roles (no placeholder), and match the line's work area and date. Weekly logs need ≥ 5 days and the work date inside the week | The cited DDR must exist, be signed by both roles, and be *for the service date* (§19A). Required parts B/C/D/E must be present (Cl.37, Sch 5) |
| 5 | Billed quantity ≤ record quantity; §6A hours = recorded − 1; §33A +2 % on surveyed items; S20 E.51.010 only for recorded hours. Billing *below* the record is payable as billed | Personnel ≤ crew words; rentals only when in the hole; counts exact (Cl.30); hours = recorded − 1 (§21A); metres vs the day's drilled metres ±1 % (§25A); PD-210 metres split by depth band |
| 6 | Item vs record wording (e.g. DX depth words decide A.12.030 vs A.12.040 per P13; pour type decides B.21.02x/03x/04x). **Unit ≠ Sch 1 unit → reject in full (Cl.26)** | Code vs App G word present in the report; unit = Sch 1 unit (Cl.35). Where two codes could fit, leave the line unresolved (guideline 6) |
| 7 | Rate in force for the work date. Instruments are applied in issue order, **and for retrospective A3 items by application date relative to 2026-05-12**. Monthly tables carry forward the last published rate | Same logic, with A3 relative to 2026-08-17. After A3's issue DD-120 is 416.00 flat from 2026-02-01, because A3 was issued after S2 (source reading; the billed data agrees) |
| 8 | Factor eligibility, §27A, P11; discount only from its start date at the % then in force; rounding per Cl.28 / §26A / §29A | §17B; standby % and "NC"; discount start dates and %; half-even at every step |
| 9 | Daily limits and exclusions (stateful, §4.2); surveyed-item rule | Daily limits; DD-120 minimum; DD-121/DD-120 by status; once-per-well and per-run timing (§4.2) |
| 10 | Cl.44 inside the application; reuse and duplicates across applications (§4.2) | Cl.29 inside the invoice (PD-210 exception); across invoices (§4.2) |
| 11 | Line amount = qty × rate (or the sum of band parts); total = Σ lines (Cl.43) | Line amounts; net = Σ charges incl. DS-900; DS-900 correct; VAT half-even; total = net + VAT |
| 12 | Outcome record per invoice (line audit table + findings) | same |

### 4.2 Cross-invoice / stateful checks

Each is computed once, globally, into a ledger that is inspectable on its own.

* **Civil annual bands.** Per item and Contract Year, the cumulative quantity is taken in **Cl.30 order**: execution date, then application number, then line number.
  * *Why that order and boundary.* §3A sets the boundaries. Sch 4 Pt 3 replaces Cl.30 but states no order, and Cl.30's order is the only one the contract gives. The billed-data diagnostic agrees: this order with the 05-Jan-2026 reset reproduces the billed band position on 98.8 % of 1,026 banded lines. The alternatives score 72.7 % (no reset) and 91.9 % (submission order).
  * *Basis.* The cumulative counts **payable** measured quantity ("the quantity measured", Sch 4 Pt 3), so a disallowed line does not advance the band. Because this choice propagates, S8 runs the billed-quantity basis alongside and hand-reviews every line whose band position differs between the two.
* **Civil daily limits and exclusions.**
  * Limits apply per item, work area and day across *all* applications; the excess falls on the later measurements in Cl.30 order.
  * The A.14.020 exclusion window runs "within 2 days following" an A.14.010 measurement on the same work area. The endpoint convention (days +1 and +2) is registered as D-10.
  * P21: no E.51.020 on a day with D.41.020, D.41.030, D.41.050, D.43.010 or D.43.020 for that work area.
* **Civil duplicates vs reuse.** These are kept separate:
  * *Cl.44 duplicate* (same item, work area and date). Only one group exists in the data, inside PA-00111 (lines 3 and 12), so the later line is disallowed. No cross-application group exists; if one did, "later" would be later application date, then application number.
  * *Evidence reuse.* 19 weekly DW logs are cited by 39 lines, all in the log's work area, within the logged week, but on *different* dates and mostly in different zones. Cl.44's same-date test does not literally apply. The applicable rules are guideline 10 ("nothing billed twice … against an earlier one") and the weekly record's quantity (one week, §47A). The earliest-**submitted** claim consumes the logged week and later claims are unsupported. This is a registered decision (D-6) with its alternative: execution-date order.
  * *Mismatch.* A record whose area or date does not match the citing line (e.g. PA-00170-04 citing PT-00189) means the line is unevidenced. It is not a duplicate.
* **Drilling duplicates, reuse and mismatch.**
  * *Cl.29 repeats.* The 3 observed groups are identical line pairs inside one invoice each; the later line is disallowed.
  * *MB-701.* Once per well; any occurrence not on the well's first DDR day, or a second occurrence, is disallowed. 3 wells have two MB-701 lines.
  * *Report-date mismatch.* 8 lines cite a DDR for another day. Of these:
    * 6 have no DDR for their service date at all: 3 fall after the term and 3 fall outside their invoice period. They are unevidenced.
    * 2 have a DDR for their own date and share code and report with another line: MDS-00128-026 and MDS-01352-007. They are mismatch findings, re-checked for duplication against the correct-day DDR before any duplicate label is used.
* **Drilling spans.**
  * **Well span** = first and last DDR date of the well. These are contiguous for all 214 wells; once-per-well lines sit on those days except for the 3 extra MB-701.
  * **Run span** = Part B first and last day. Consistent for all 1,369 well/run pairs; DD-111 matches 654/654 and LW-420 369/369.
* **Drilling Contract-Year tier.** Kept per well by explicit wording; the ledger still computes it. It is non-binding in this dataset because no well is drilled deeper than about 6,000 m, far below the first 40,000 m tier. That is a verified fact, not an assumption.
* **Retrospective catch-up** (both contracts; see D-1 and D-2):
  * *Population.* Affected-item lines with work date ≥ effective date, on invoices submitted before the issue date.
  * *Amount.* Σ (contract-correct amount at the new rate − contract-correct amount at the then-current rate), computed by our engine with the full build-up (factors, bands, discounts). Billed amounts are not the basis, so earlier billing errors do not leak in.
  * *Placement.* The first invoice submitted **on or after** issue (§31A/§36A); ties are broken by the lowest invoice number.
  * *Ties in the data.* Civil has three applications dated 2026-05-12: PA-00006, PA-00023, PA-00380. Drilling has one invoice on 2026-08-17 (MDS-01625), then three dated 2026-08-18.
  * *Protection.* Pre-issue invoices priced at then-current rates are correct. **A pre-issue invoice priced at the new rate took the change early**: that is a finding.

## 5. Validation without labelled data

There is no ground truth, so every rule passes a ladder of independent evidence **before** it runs on the full population, and the pipeline has tripwires that catch a wrong rule *before* it propagates.

**Per-rule evidence (required before a rule is enabled):**
1. **Source trace.** Clause, page and verbatim quote, verified by the second reader (S1 gate).
2. **Unit tests** built from the clause, including boundary cases:
   * effective-date days;
   * the 27-Sep-2025 and 05-Jan-2026 boundaries;
   * term-end days;
   * band thresholds landing exactly on a line;
   * half-cent and half-halala values under both rounding modes (e.g. 423.00 × 0.945 = 399.735 → 399.74 half-even; a binary float gives 399.73, so money is `Decimal` only).
3. **Golden examples** from the contract (§3.5).
4. **Canary set.** About 5 hand-worked lines per rule: positive cases, negative cases, and the **"odd but correct"** cases observed in Phase 1:
   * band-split lines;
   * survey quantities within +2 %;
   * hours at recorded − 1;
   * billing below the record;
   * weekly logs with 5–7 days.

**Propagation tripwires (run on every full execution; failures stop S9):**
* **T1 — clean-invoice reproduction.** For every invoice with no finding, the recomputed total must equal the billed total to the minor unit. An unexplained residual is an engine or reading defect to investigate. It is never a flag by itself.
* **T2 — blast radius.** Every rule reports how many lines and invoices it changes, broken down by month, item/code, zone/section/class and well. Injected errors are expected to be sparse and scattered. A rule whose findings **cluster** (for example, every line of one item in one month, or every Z3 line) is held for source review before its findings count. That is the signature of a misread effective date, index month, factor list or rounding mode. Such findings are not suppressed; they are held until the reading is re-verified.
* **T3 — state cross-checks.** Each state ledger is checked against an independent source:
  * well and run spans from the DDR sequence vs Part B;
  * band cumulative totals vs Σ quantities;
  * CY boundaries asserted from §3A dates;
  * both band bases (§4.2) compared.
* **T4 — sensitivity.** Every open reading in §6 is run both ways. The flip set is recorded; each flipping invoice has its confidence capped and is listed in the report.
* **T5 — independent hand audit.** About 60 invoices (30 per contract) are stratified:
  * flagged by category;
  * unflagged;
  * amendment and CY boundary dates;
  * same-day ties;
  * odd-but-correct cases.

  Each is re-derived end to end from the source documents alone by an independent reviewer (a separate agent pass given only the contract pages, records and the decision register). Every disagreement is root-caused to the reading, the parser, the state or the arithmetic, and fixed or registered.
* **T6 — parser coverage.** 100 % of cited records parse into their fields, or appear on a reviewed exception list. Parser outputs are diffed against a 5 % random sample read by hand.

## 6. Ambiguity register, unpriceable invoices, and confidence

**Register (decision log source).** Each entry has an ID, clause/page, the readings, the chosen reading and why, the alternative, the affected invoices (from T4), and the confidence cap it imposes.

| ID | Question | Chosen reading (reason) |
|---|---|---|
| D-1 | Which invoice carries the §31A/§36A single adjustment ("after" in A3 vs "on or after" in §31A/§36A); same-day ties | "On or after" (the general mechanism the A3s themselves cite; the billing on issue day already uses the new rates). Ties → lowest invoice number |
| D-2 | Does the catch-up adjustment belong in the judged total? | Civil: no. §45A separates "measured total" from the adjustment, and Cl.43 defines the total as Σ items. Drilling: **unresolved** whether it is a charge inside net, and so subject to VAT. Compute both, choose in S8 from source re-reading, and cap confidence. Every `adjustment` value in the data is 0.00, so an omission is reported on at most one invoice per contract |
| D-3 | DDS A3 vs S2's monthly DD-120 table | A3 (issued later) replaces DD-120 with 416.00 for services from 2026-02-01, applied to invoices submitted on/after 2026-08-17. Pre-issue invoices keep the S2 monthly rates |
| D-4 | Civil band basis: billed vs payable quantity | Payable (the text says "quantity measured"). Both bases run (T3/T4) |
| D-5 | Civil band order after "Clause 30 is substituted" | Cl.30 order (the only order stated); agrees with the billed data |
| D-6 | Weekly-log reuse: which claim is unsupported | Earliest-submitted claim is supported (guideline 10: "against an earlier one"). Alternative: execution-date order |
| D-7 | Unsigned record (1 civil: DX-00089; 3 DDRs) | Not a valid record under Cl.47 / Cl.15 and guideline 4, so the lines relying on it are unevidenced. For a DDR, that is every line of the day. Tier C confidence |
| D-8 | DDS Sch 8 wording vs specific clauses (DD-120/RM-530 "or back-reaming hour"; HC-630 "per BHA run"; DD-102 "tool in hole") | The specific clauses govern (Cl.21/§21A, Cl.30, App G "night man"): Sch 8 is not among the documents Cl.2 lists and is general. Logged |
| D-9 | Expected total for header-only procedural findings (wrong contract reference, early or late submission) | Flag it. The expected total is the contract-supported total of its lines (usually the billed total), because neither contract forfeits the charges. The alternative (zero) is recorded. Confidence covers the flag, not the amount |
| D-10 | Exclusion window endpoints and the E.53.010 wording in P6 | Days +1 and +2 after the excluding measurement; P6 read as the Sch 4 Pt 4 limit of 2 per work area per day |
| D-11 | Rate *below* the contract (e.g. a superseded lower rate) | Wrong in either direction, so flagged; the expected total may exceed the billed total. Quantity *below* the record is **not** an error |

**Inert rules** (verified in the data; implemented as documented no-ops or assertions):
* P11 concurrency: no night + rest-day line on a both-eligible item.
* DD-120 six-hour minimum: circulating hours are 8–22 whenever the tool is in the hole.
* DDS tier per well.
* S4 ground not recorded: every DX record carries a `Ground:` line.
* P2 flood watch, P9 heat suspension, H15 safety suspension, P4 rig moves, P7 crew changes: no such words anywhere in the 10,320 records.
* Drilling units: all match Sch 1.

**Unpriceable invoices.** Every row is still filled.
* A line whose value cannot be established is a **query**. Causes: a genuine two-code fit, an unparseable record after review, or a reading with no defensible choice.
* The expected total then excludes only the query lines. This follows DDS Cl.41 ("withhold a disputed charge and … pay the undisputed balance") and CW Cl.46 (not payable until the record is delivered).
* The category is `query_<reason>` and confidence reflects the chance that the invoice is wrong at all.
* The report lists every query row and what was missing.

**Confidence (probability the row's decision is right).** Each finding gets a tier probability:

| Tier | Description | P(wrong) |
|---|---|---|
| A | Deterministic arithmetic, date or reference against an explicit clause | 0.97 |
| B | Explicit rule plus a verified parser or verified term | 0.90 |
| C | Depends on a registered reading with a plausible alternative | 0.55–0.75, set by T4/T5 |
| D | Parser or vocabulary uncertainty | 0.35 |

* **Invoice P(wrong)** = 1 − Π(1 − p). The invoice is flagged if P(wrong) > 1/6. That is the Bayes rule for the README's 5 × FN + 1 × FP cost; it is our own decision, not an organiser threshold, and it is re-examined against the precision per band that T5 measures.
* **Confidence field:** P(wrong) for flagged rows; 1 − P(wrong) for unflagged rows. Unflagged rows are capped below 0.97 when parser coverage or an open reading touches them.
* **Tier recalibration.** Tier values are adjusted once, using T5 agreement rates. They are not tuned to reach any flag count.

## 7. Expected-total correctness

* **Civil:** `expected = Σ payable_amount(line)`, rounded to the halala, × 100 as an integer. For each line:

  `payable_amount = Σ over band parts of (payable_qty_part × round_half_up(built-up rate))`

  * `payable_qty` = the billed quantity, capped by the record, §33A, §6A and the daily limits.
  * The line's amount is 0 for: wrong unit, missing or invalid record, the later Cl.44 duplicate, an unsupported reuse claim, work outside the term or period, or an exclusion window.
  * Retention, release and net payable are **excluded**. The catch-up adjustment is excluded (D-2).
* **Drilling:**
  1. `services = Σ payable_amount(line)`, each amount built with half-even steps.
  2. `DS-900 = −round_half_even(4 % × max(0, services − 250,000))`, **recomputed** on the payable services.
  3. `net = services + DS-900`.
  4. `VAT = round_half_even(15 % × net)`.
  5. `expected = net + VAT`, plus any adjustment under D-2.
* **Unflagged rows:** `expected_total_cents = billed_total_cents`.
* **Identity checks:**
  * `billed_total_cents` equals the header total × 100 exactly (string-to-`Decimal`, never float).
  * Expected ≠ billed on a flagged row only if a finding changes an amount. Header-only findings (D-9) keep the recomputed total.
  * T1 must hold for every unflagged row.

## 8. Reproducibility and deliverables

* **Repository layout:**
  * `terms/` (YAML + quotes);
  * `src/audit/` (loaders, parsers, pricing, state, checks, totals, decide, submit);
  * `tests/` (golden, boundary, property, canary);
  * `outputs/` (line audit table, findings, ledgers, diagnostics, `submission.csv`);
  * `docs/` (report, decision log, AI disclosure);
  * `prompts/`;
  * the challenge data referenced by a pinned git submodule or a download script at the fixed SHA.
* **Environment.** Python 3.11 with `requirements.txt` pinned by exact version and hash (pandas, PyYAML, pytest; OCR tools only in an optional `requirements-transcribe.txt` that the pipeline does not need). One command, `make submission` (equivalently `python -m audit run`), rebuilds everything deterministically. CI or a `make check` target runs the tests and tripwires. The committed `terms/*.yaml` means reproduction never needs OCR or an LLM.
* **`submission.csv` checks:**
  * exactly the template's 2,806 ids in template order;
  * `flagged` ∈ {0, 1};
  * category blank iff `flagged` = 0, drawn from a controlled vocabulary of about 12 labels in guideline-check order;
  * integer minor units in native currency;
  * confidence in [0, 1].
* **Report** (`docs/report.md`):
  * performance on the internal evidence (T1–T5), stated as internal validation, not accuracy;
  * category counts;
  * error analysis by **3–4 failure types**, each with one worked example (candidates: transcription/reading error, evidence-parsing or vocabulary error, state/order error, rounding/arithmetic error);
  * what could not be determined.
* **Decision log** (`docs/decision_log.md`, **one page**): assumptions and D-1…D-11, with the reading chosen and why.
* **Prompts** (`prompts/`): every prompt used (Phase 1, audit, Phase 2, Phase 3 stages, subagent prompts) as numbered, dated files, with `CHANGELOG.md` showing each iteration.
* **AI disclosure** (`docs/ai_disclosure.md` and a README section): which models and tools were used, for what (transcription, coding, review), and what a human or independent pass verified.

## 9. Major failure modes and safeguards

| Failure mode | Consequence | Safeguard |
|---|---|---|
| Misread number or date in a scan | Wrong rate on every line touching it | Two independent reads + OCR diff; consistency assertions; T2 clustering; T1 |
| Wrong precedence (e.g. App B example over §29A; Sch 6 over §31A; Sch 8 over Cl.21) | Systematic repricing | Explicit precedence notes in the terms file; registered decisions; T2 |
| Wrong rounding mode or rounding step | Many cent/halala flags | Per-contract rounding tests; `Decimal` only; half-case unit tests; T1 |
| Wrong date axis (issue vs effective vs submission) | Correct pre-issue invoices flagged, or catch-ups missed | Five-date model in the schema; A3 boundary tests; same-day tie tests |
| Stateful error (band order or basis, CY boundary, span) | Cascading flags across later invoices | Global ledgers; T3; D-4/D-5 both-way runs; T5 includes post-boundary lines |
| Treating mismatch or reuse as duplication | False "billed twice" findings | Three distinct finding types; a duplicate needs the same chargeable event |
| Vocabulary or parser gap | Lines wrongly unevidenced | T6 coverage; App G used verbatim; the civil lexicon built from the full distinct-sentence list |
| Signature placeholder read as signed | Missed evidence failures | Explicit placeholder detection (`____`); role pools checked |
| Using the prevalence as a quota | Suppressed or invented flags | No count-based tuning; tiers calibrated only on T5 |
| Float money | Off-by-one-cent flags | `Decimal` from CSV strings; a lint check for float usage in `money` |
| Unflagged rows with an unexplained residual | Hidden engine bug or missed error | T1 blocks submission until each is explained |

## 10. Use of remaining time and what is cut first

No overall deadline is stated in the repository. The plan below is budgeted as shares of whatever time remains, with checkpoints.

| Share | Stages | Checkpoint |
|---|---|---|
| 20 % | S0 + S1 (terms and gate), with S3 in parallel | Gate passed |
| 25 % | S4 + S5 | Golden tests and T3 pass |
| 20 % | S6 + S7 | Findings for all 2,806 invoices; T1 holds |
| 20 % | S8 validation loop | T2–T6 reviewed |
| 15 % | S9 + S10 | Deliverables complete |

**Cut first, in order:**
1. Report polish and charts.
2. Sensitivity runs beyond the five most consequential decisions (D-1, D-2, D-4, D-6, D-7).
3. Assertions for inert rules (keep them documented).
4. The OCR leg of Read B (keep the second visual read).
5. Shrink the hand audit from 60 to 30 invoices.

**Never cut:** the S1 gate, `Decimal` money, T1, the invoice-local checks, the stateful ledgers, the submission schema check, the decision log, prompts and AI disclosure.

## 11. Evidence that each stage is complete

| Stage | Exit evidence (artifacts in the repo) |
|---|---|
| S0 | `make check` runs; loader tests prove 900 / 7,746 / 1,906 / 91,244 rows, 2,169 + 8,151 records, zero orphan joins, template id set = header id set; `pip install -r requirements.txt` reproduces from hashes |
| S1 | `terms/*.yaml` + `terms/quotes/`; `outputs/transcription_diff.csv` with 0 open rows; consistency and golden tests green (conflicts cited); gate note signed off in the decision log |
| S2 | `docs/decision_log.md` lists D-1…D-11 with chosen readings; each referenced by rule IDs in code |
| S3 | Parser coverage report: 100 % of cited civil records and DDRs parsed or on a reviewed exception list; 5 % hand-sample diff = 0; placeholder signatures detected (1 civil, 3 DDR) |
| S4 | Line-level price trace for every line; golden, boundary and rounding tests green; billed-rate diagnostic report with any cluster reviewed |
| S5 | Ledgers exported (bands per item/CY, daily limits, spans, duplicate and reuse, catch-up population) and T3 cross-checks green |
| S6 | `outputs/findings.csv` with rule, clause, evidence and tier on every finding; each finding type has canary tests |
| S7 | `outputs/invoice_decisions.csv`; T1 = 0 unexplained residuals; every flagged row cites ≥ 1 finding |
| S8 | T2 cluster review notes; T4 flip table; T5 hand-audit sheet with 100 % of disagreements root-caused |
| S9 | `submission.csv` passes the schema validator; row order and ids match the template; totals are integers in native minor units |
| S10 | README run instructions verified from a fresh clone; report with 3–4 failure types and examples; one-page decision log; `prompts/` with CHANGELOG; AI disclosure |

## 12. Not confirmed this phase (and where I looked)

* **Verbatim re-read incomplete.** The subagent pass was cut short by a usage limit; only CW pp.1–12 and DDS pp.1–8 were independently re-read. I viewed the other decision pages myself (§ header). The DDS pages *not* re-viewed this phase — pp.11–12, 14, 20–21, 27, 30, 36, 38–39, 41 — rest on the Phase 1 notes and the Phase 1 billed-rate reproduction. In particular, the Sch 8 DD-120 row wording (p27) is not re-confirmed; p28 confirms the RM-530 wording.
* **D-2 (catch-up adjustment in the drilling total, VAT treatment)** is genuinely unresolved from the text; the data has no non-zero adjustment to test it.
* **The 12 banded civil lines** that the Cl.30/CY diagnostic did not reproduce were not examined. D-4 (payable basis) predicts some of them; this is an S8 task.
* **OCR tool availability** was not tested. The plan has a fallback (a second visual read).
* **Severity is undefined in the README.** The plan does not encode it in the submission; the report uses its own clearly labelled convention.

## 13. Time spent

About **40 minutes of active work**:
* 23-Sep 00:40–00:52 UTC: inputs, subagent launch, data checks;
* the phase then paused on a usage-limit interruption;
* 24-Sep ~06:29–06:55 UTC: source page views, cross-check and writing.

## 14. Read-only data checks behind decisions (counts only)

| Check | Result | Decision it grounds |
|---|---|---|
| Civil lines in a non-Sch-1 unit | 4 (PA-00052-02, PA-00406-03, PA-00833-07, PA-00892-06) | Cl.26 full rejection is a small, deterministic rule |
| Civil same item/work area/date groups | 1, inside PA-00111 | Cl.44 "later" ordering across applications never arises |
| DW log reuse | 19 logs, 39 lines; same work area, same week, different dates and mostly different zones | Reuse ≠ Cl.44 duplicate (D-6) |
| Record `Ground:` vs line ground | 536/537 agree (the exception is the wrong-record line) | S4 inert; line ground stands |
| Night / rest-day overlap on both-eligible items | 0 | P11 inert |
| Band order and CY diagnostic | 98.8 % (Cl.30 order + 05-Jan reset) vs 72.7 % / 91.9 % | D-5, CY boundaries |
| DDR well and run spans | Contiguous for 214 wells; Part B consistent for 1,369 runs | Span ledgers from DDRs |
| DD-120 hours when steerable in hole | 8–22 | Minimum and first-hour interaction inert |
| Cl.29 repeats | 3 identical pairs within single invoices | Later line disallowed |
| Report-date mismatches | 8: 6 with no DDR for the service date, 2 sharing code and report with another line | Mismatch ≠ duplicate |
| Drilling units | 0 off-schedule | Cl.35 check inert |
| Invoice-number vs date order | 903 inversions | "First on or after" must use dates |
| Unstructured-condition text scan | 0 hits for rig move, crew change, failure, flood, heat, safety, dust, instruct | Rules documented as inert |
