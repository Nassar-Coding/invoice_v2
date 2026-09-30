# Phase 1 — Step 1 Understanding Report (Agent 1)

| | |
|---|---|
| Challenge source | `majedzahrani3/invoice-auditing-level-2` @ `aef4924` ("Add challenge README and submission template") |
| Date | 2026-09-22 |
| Scope | Understanding only. **No invoice has been classified, no submission produced and no solution designed.** |

**How this report was produced.** I read the README and both guideline files, then profiled every CSV (pandas) and every record type. I extracted all 85 scanned contract pages as native 1654×2338 page images, read each page visually and transcribed it into page notes. As a final step I checked the transcription against the billed data. This was an extraction check, not an audit. With my transcribed terms, the billed unit rate reproduces on **99.5 % of civil lines (7,710 / 7,746)** and **97.5 % of drilling lines**. For drilling, most of the gap has two known causes (Amendment 3 timing and float rounding; see §9–10), and 40 isolated lines remain. Where contract wording conflicts, I also noted which reading the billed data follows. That is calibration evidence for the next phase, not a decision.

**Citation convention.** `CW pN` means PDF page N of `civilwork/contract/CW-2025-0417-CIV.pdf`, and its printed footer carries the same number. `DDS pN` means PDF page N of `drilling_services/contract/DDS-2025-118.pdf`. Clauses are cited as they are numbered in the contract, e.g. `Cl.41` or `§36A`.

---

## 1. What the challenge asks us to do

* **Audit every invoice** under two contracts: 900 civil payment applications and 1,906 drilling invoices, **2,806 in total**. Apply the twelve checks in `INVOICE_AUDIT_GUIDELINES.md` to each. Where the guidelines and the contract differ, **the contract governs**, and the difference should be reported (README, "Ground rules").
* **Extracting the terms from the scans is part of the task.** Both PDFs are photographed paper with no text layer, and every pricing term must come from them: rate schedules, supplements and amendments, definitions.
* **Linking evidence is part of the task.** Site records and daily reports are free text in site language. Establishing which priced item a charge belongs to, and which record evidences it, has to be done.
* **There are no labels.** The calibration principle is: *"if your reading of a clause reprices invoices that reconcile exactly as billed, your reading is probably wrong"*.
* **5–8 % of invoices are wrong**, roughly 140–225 of 2,806. Some odd-looking invoices are deliberately correct.
* **Deliverables:**
  1. A runnable repo with pinned dependencies that reproduces the submission.
  2. `submission.csv` covering all 2,806 rows.
  3. A short report: performance, plus an error analysis grouped by 3–4 systematic *failure types*, with an example of each.
  4. The prompts as versioned files, showing any iteration.
  5. A one-page decision log covering assumptions, unresolved ambiguities and the choice made for each.

## 2. Repository and dataset structure (verified from the files)

| Path | Content | Verified facts |
|---|---|---|
| `README.md` | Brief | — |
| `submission_template.csv` | `invoice_id,flagged,error_category,expected_total_cents,billed_total_cents,confidence` | 2,806 rows: `PA-00001…PA-00900` and `MDS-00001…MDS-01906` |
| `civilwork/contract/CW-2025-0417-CIV.pdf` | 43 pages, each a single greyscale image, 0 text characters | Page image 1654×2338 (A4 at about 200 dpi) |
| `civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md` | 3 principles and 12 checks | Byte-identical to the drilling file apart from the title and scope lines |
| `civilwork/invoices/applications.csv` | `application_no, contract_ref, subcontractor, site, site_zone, period_from, period_to, application_date, application_total, retention, net_payable, adjustment, retention_released` | 900 rows; `adjustment` and `retention_released` are 0.00 on **all** rows |
| `civilwork/invoices/application_lines.csv` | `line_ref, application_no, line_no, work_date, site, item_code, description, unit, site_zone, ground_class, quantity, rate_applied, amount, night_work, record_ref` | 7,746 rows (3–14 per application); 60 item codes; integer quantities |
| `civilwork/records/*.txt` | 9 record types | 2,169 files: CT 381, JS 368, PR 365, PT 270, DX 266, PS 143, MO 142, CV 120, DW 114 |
| `drilling_services/contract/DDS-2025-118.pdf` | 42 pages, same scan format | 0 text characters |
| `drilling_services/invoices/invoices.csv` | `invoice_no, contract_ref, contractor, well_name, rig, field, well_class, period_start, period_end, invoice_date, net_amount, vat_amount, invoice_total, adjustment` | 1,906 rows; `adjustment` 0.00 on **all** rows |
| `drilling_services/invoices/invoice_lines.csv` | `line_ref, invoice_no, line_no, service_date, well_name, service_code, description, unit, hole_section, day_status, depth_from_m, depth_to_m, quantity, unit_rate, amount, report_ref` | 91,244 rows (13–93 per invoice); 38 service codes plus `DS-900` |
| `drilling_services/records/*.txt` | Daily Drilling Reports (DDR) | 8,151 files, one per well-day |

**Formats and joins**

* Civil CSV dates are ISO. Civil records use `DD/MM/YYYY`. Drilling CSVs and DDRs use `DD-Mon-YYYY`.
* Money is printed with 2 decimals in the contract currency: SAR for civil, USD for drilling. The submission needs integer minor units.
* Lines join to headers on `application_no` / `invoice_no`, with no orphans in either direction.
* **Civil** `record_ref` is the file stem (`PR-00177` → `records/PR-00177.txt`).
* **Drilling** `report_ref` `DDR-194-20250101` → `records/DDR_NGP-BD-194_20250101.txt`. The field code is *not* in the ref. The mapping is still unambiguous because the 214 well numbers are unique across fields. The `Report:` line inside every file equals its ref (8,151 / 8,151).

**Population**

* **Civil:** one subcontractor (Ridgeway Civil Engineering LLC). Five work areas, `S-01`…`S-05`, and four zones, `Z1`–`Z4`. Each application covers one work area and one zone, and every line carries the same site and zone as its header. Work dates run 2025-01-07 → 2026-10-26; application dates 2025-01-23 → 2026-10-31.
* **Drilling:** one contractor (Meridian Downhole Services Ltd). 214 wells, 13 rigs, 4 fields. Invoice counts by well class: Standard 1,099, Extended Reach 505, HPHT 302. Class, rig and field are constant per well across invoices. Service dates run 2025-01-01 → **2027-01-23**; invoice dates 2025-01-07 → 2027-01-25. Periods are typically 1–6 days per well.

## 3. How the two contract datasets and their supporting records work

### 3.1 Civil works — CW-2025-0417-CIV (SAR)

* **Parties and structure** (CW p1). The Contractor is Al-Murjan Infrastructure Contracting Company; the Subcontractor is Ridgeway Civil Engineering LLC. The project is "Northern Industrial Access Road and Platform, Package 4 — Civil Works"; the records say "Northern Access Road, Package 4". This is a measure-and-value subcontract with no lump sum.
* **Pricing.** Sixty BoQ items in Series A–E (CW p17–19) carry *base* rates. Each is built up per **Cl.27** in this order:
  1. zone factor (Sch 2);
  2. ground factor (Sch 3);
  3. night uplift;
  4. rest-day uplift;
  5. cumulative-quantity band (Sch 4 Pt 3);
  6. the instrument discount, as the final factor (S2 §2.2 / A2 §2.3).

  The result is **rounded once**, half-up, to the halala (**Cl.28**).
  * USD-denominated items are first converted (Sch 2B, §26A), and indexed items first indexed (Sch 2A, §29A). Both of those steps round half-even.
* **Application.** The period runs from the first to the last execution date of the items included (Cl.40). An application may not be submitted before the period's last day, and must be submitted within 21 days of it (Cl.41). The total equals the sum of line amounts (Cl.43). Retention is 5 % of the total, **rounded down** (Cl.45), giving `net_payable`.
* **Records** (Sch 5, CW p27). **Seventeen items are not payable without a delivered record** from a named series; the other 43 items need none. The nine record types map one-to-one to the nine series:

  | Series | Record |
  |---|---|
  | DX | Daily Excavation Record |
  | CT | Compaction Test Certificate |
  | PR | Concrete Pour Record |
  | PT | Pressure Test Certificate |
  | MO | Meteorological Record |
  | DW | Dewatering Log (weekly) |
  | CV | CCTV Survey Report |
  | PS | Plant Standing Record |
  | JS | Joint Survey Sheet |

  * Each record holds: title, ticket, job, `Area` (the work area), and either `Date` or, for weekly logs, `Week beginning` plus `Days on`. Some also carry `Ground`.
  * The substance is **one free-text sentence carrying the quantity**, in site words.
  * It is signed by the Subcontractor's **foreman** and countersigned by the **Engineer's representative** (Cl.47, P22).

### 3.2 Directional drilling — DDS-2025-118 (USD)

* **Parties** (DDS p1, p31). The Company is Northgate Petroleum Operating Company; the Contractor is Meridian Downhole Services Ltd.
* **Invoicing.** A call-off per well fixes the rig, field and **well class for the whole well** (Cl.4). Each well is invoiced separately, over a period of consecutive days (Cl.32). An invoice may not be submitted before the period's last day, and must be submitted within 30 days (Cl.33).
* **Pricing** (Cl.18, each step rounded **half-even** to the cent per Cl.17):
  1. Start from the Sch 1 rate. PD-210 is priced from Sch 2; MW-310 and HC-620 are indexed under Sch 2C/§17A; instrument rates apply where they exist.
  2. Apply the hole-section factor. Six codes are section-rated; the factor is **not applied on a Standby day** (§17B).
  3. Apply the well-class factor. Eight codes are class-rated; the factor is **not applied to PD-210** (§17B).
  4. Apply the standby percentage (Sch 3 Pt 3).
  5. Apply the instrument discount (S2 4 %, A2 7 %) as the last factor.
* **Totals.** Net equals the sum of lines, including the `DS-900` line (Cl.36). `DS-900` is −4 % of the part of the services total above USD 250,000, per invoice (Cl.38, P11). VAT is 15 % (Cl.39); total = net + VAT (Cl.40).
* **Evidence.** One **DDR per well-day** (Cl.15; Sch 5, DDS p24) with these parts:

  | Part | Content | Present in |
  |---|---|---|
  | A | Operations summary | Every report |
  | B | BHA run record | Every report |
  | C | Gyro surveys | 479 reports |
  | D | Radioactive-source handling | 367 reports |
  | E | Lost in hole | 54 reports |

  Reports are written in **rig words, not codes** (§19A). The words map to codes through **Appendix G** (DDS p36). Each DDR is signed by the **Company Representative** and the **lead directional driller** (Cl.15).

## 4. The audit checks we are required to perform

The guidelines, identical for both contracts, set three principles: work date first, the record is the evidence, and say when you do not know. They then list twelve checks. The table shows where each check lives in each contract.

| # | Guideline check | Civil (CW) | Drilling (DDS) |
|---|---|---|---|
| 1 | Invoice belongs to the contract: reference, issuer, period | p1 reference and parties | p1 reference and parties |
| 2 | Contract live on the work dates, as extended | p1; A1 §1.1; A2 §2.1 → **05-Jan-2025 … 30-Sep-2026** | p1; A1; A2 → **01-Jan-2025 … 31-Dec-2026** |
| 3 | Raised inside the window, after the period closed | Cl.40–41: not before the last day, **≤ 21 days** | Cl.32–33: not before the last day, **≤ 30 days** |
| 4 | Every line has its record, correctly signed | Cl.46–47, §47A, P22, P23, Sch 5 | Cl.15, Cl.37, Sch 5, §19A |
| 5 | Quantities are the recorded ones | Cl.33 + §33A (+2 %), §6A (hours − 1), S20 | Cl.19–25, Cl.30, §21A (hours − 1), §25A (+1 %) |
| 6 | Each line identified against a priced item | Cl.26 (unit), P13 (trench depth → item), Sch 5 wording, §47A | Cl.35 (unit), App G glossary, §19A, R5/R6 |
| 7 | Rate in force on the work date; instruments in the order issued | Schedule of Variations p38; S1–A3; §29A, §26A | Schedule of Variations p37; S1–A3; §17A; Sch 2 |
| 8 | Adjustments in the contract's order, rounded its way; discounts only from their start, at the % then in force | Cl.27–30, §27A, P11, S2 §2.2, A2 §2.3 | Cl.17–18, §17B, Cl.20, S2, A2, Cl.38 |
| 9 | Limits: caps, exclusion windows, once-only items, minimums | Sch 4 Pt 4 daily limits; Pt 5 exclusion; Cl.19; P6; P21 | Sch 3 Pt 5 limits; Pt 6 once-per-well; Cl.21 minimum 6 h; Cl.26–27; Cl.31 50 % cap |
| 10 | Nothing billed twice, in the invoice or across invoices | Cl.44: the **later** measurement is disallowed in full | Cl.29: no service twice per well-day; Cl.26–27 |
| 11 | Arithmetic reconciles: lines, subtotal, additions and deductions | Cl.28, Cl.43, Cl.45; §45A | Cl.36, Cl.38–40 |
| 12 | Outcome written down with clause, payable figure and unknowns | Submission, report, decision log | same |

**Where guidelines and contract differ (reportable; the contract governs):**

* **Guideline 5** says "billed above the record is payable up to the record". The contracts qualify this in three ways:
  * CW §33A pays joint-survey items as measured up to **+2 %** over the survey.
  * DDS §25A pays metres as charged up to **+1 %**.
  * CW §6A and DDS §21A pay hourly items at **recorded hours − 1**, so the payable quantity is not the recorded one.
* **Guideline 10** says "nothing billed twice". CW Cl.44 also decides *which* copy fails: the later one is disallowed in full.
* **Guideline 3** gives no window length; the contracts set 21 days (CW) and 30 days (DDS).
* **Guideline 7** says the later instrument governs *from its effective date*. Both contracts' Amendment 3 is **retroactive**, and CW §31A / DDS §36A defer the difference to a single later adjustment. Meanwhile each Schedule of Variations says "nothing … reopens work already measured" (CW p38, DDS p37).

## 5. Page-referenced map of each scanned contract

### 5.1 CW-2025-0417-CIV — 43 pages

| Page | Content | Pricing-relevant terms |
|---|---|---|
| 1 | Form of Subcontract | Ref CW-2025-0417-CIV; parties; measure-and-value; Commencement **05-Jan-2025**; Completion **27-Sep-2025**; SAR; retention 5 %; working week Sun–Thu; rest days Fri–Sat |
| 2 | Contents | Lists Parts I–VI, Sch 1–8, App A–C. **Omits** Part VII, Sch 2A/2B, the Schedule of Variations and all instruments |
| 3 | Part I, Cl.1–10 | Cl.2: a Schedule prevails over the General Conditions, and a later-numbered Schedule over an earlier one. Cl.4: zone = where the work is executed. Cl.5: ground classified before the work, never revised. Cl.7 night work 18:00–06:00; Cl.8 rest-day uplift, not both without a Cl.9 instruction |
| 4 | Cl.11–21 | Cl.11: E.52.010 only against a joint survey. Cl.13: certificate as a condition of payment. Cl.14: defective work not re-measured. Cl.17: daywork signed daily. **Cl.18:** standing time only as E.51.010 (MO) or E.51.030 (PS). **Cl.19:** E.51.020 at most 1 day per work area per day |
| 5 | Cl.22–24 | Non-pricing |
| 6 | Part II, Cl.25–32 | **Cl.26** a wrong unit is rejected entirely. **Cl.27** build-up order. **Cl.28** single rounding, half-up; band split. Cl.29 factors by "series". Cl.30 cumulative rebates, ordered by date, then application no., then line no. Cl.31 daily limits per work area. Cl.32 exclusions |
| 7 | Cl.33–39 | **Cl.33** surveyed items = survey quantity *exactly*. **Cl.35** temporary works, dewatering below the water table and own waste are not measurable. Cl.38 SAR/halala. Cl.39 arithmetic error → rate stands |
| 8 | Part III, Cl.40–50 | Period (40); window **21 days** (41); content (42); **total = Σ lines (43)**; **duplicates: later disallowed (44)**; retention 5 % rounded down (45); record as a condition of payment (46); record form and two signatures (47) |
| 9 | Cl.51–52 | Retention release on TOC and DLP; interest |
| 10–11 | Part IV, S1–S20 | S3: over-excavation not measured under A.14.010. **S4: ground not recorded on the day → G2**. S8: night-placing approval is not a Cl.9 instruction. S13. **S20: E.51.010 only for the hours recorded** |
| 12–14 | Part V, P1–P25 | P1 Part V prevails over I–III. P2 Z3 flood watch → E.51.010, not E.51.030. P3 Z4 no standing claims. P4 Z1 night consent ≠ uplift. **P6** E.53.010 limit. P8 bowser standing → E.51.030. **P9** heat suspension is not standby. **P11 concurrent uplifts → rest-day alone** unless instructed. P12 bands fixed. **P13 trench depth decides A.12.020/030/040.** P14 ground disputes. P15 unapproved fill. P17 rejected concrete. **P19 A.14.020 excluded within 2 days of A.14.010.** **P21 no E.51.020 on surfacing days.** P22 electronic records need both signatures. **P23 missing record → deducted from the next valuation.** P24 daywork |
| 15–16 | Part VI, H1–H15 | H2 no method statement → not measured. H4 support measured under A.15.010/020. **H15 safety suspension is not standby** |
| 17–19 | **Sch 1 BoQ** | 60 items, Series A–E, base rates (Appendix A1). Cl.26 unit rule restated |
| 20 | **Sch 2** zones and work areas | Z1 1.00, Z2 1.06, Z3 1.145, Z4 1.28, applying to Series A–D only. Five work areas S-01…S-05 (units for Cl.19, 31, 32, 44, P6) |
| 21 | **Sch 2A** indexed rates | C.31.010, D.41.030 × Site Materials Index (base 100 = 05-Jan-2025) |
| 22 | **Sch 2B** USD rates | B.23.020, B.25.010, C.32.040 in USD; halalas-per-USD table |
| 23 | **Sch 3** ground factors | G1 0.94 … G5 1.63; **applies only to the 15 listed items** |
| 24–26 | **Sch 4** Parts 1–6 | Night uplift (13 items); rest-day uplift (4); **banded quantities per Contract Year** (8 items; "Clause 30 is substituted"); daily limits (9 items); exclusion (A.14.020 / A.14.010, 2 days); surveyed items (B.23.010, E.52.010, B.23.020) |
| 27 | **Sch 5** records | 17 items → record series; the reference is quoted on the line; weekly record needs ≥ 5 days worked |
| 28–29 | Sch 6 daywork | Labour, plant and percentage additions. Not billed in the data |
| 30 | Sch 7 PS/PC sums | PS.01–05, PC.01–03. Not billed |
| 31 | Sch 8 preliminaries | PR.01–PR.14. Not billed. "PR" collides with the concrete-pour record prefix |
| 32–33 | **Part VII** particular conditions, second series | **§3A** Contract Years. **§6A** chargeable hour = attended − 1. **§26A** USD conversion, half-even, before factors. **§27A** no night uplift where zone factor > 1.1; **G2 for work after 27-Sep-2025**. **§29A** indexation, half-even. **§31A** retro instruments → single adjustment on the first application *on or after* the issue date. **§33A** +2 % survey tolerance. **§45A** retention release. **§47A** records in own words, reference quoted, week ≥ 5 days |
| 34 | App A definitions | Day, rest day (Fri/Sat), work area, night work, period, working day, etc. |
| 35 | Execution | Blank signature lines; "pages numbered consecutively … and no others" |
| 36 | App B form of application | Worked example: A.12.020 Z2 G4 → 50.72; A.14.020 → 23.74; C.31.010 Z2 → 91.37 (**no Sch 2A indexation**); total 15,794.40; retention 789.72 |
| 37 | App C | Insurances; notice addresses |
| 38 | **Schedule of Variations** | Instruments are read in the order issued; term as extended 05-Jan-2025 → 30-Sep-2026 |
| 39 | **Supplement No. 1** | New rates for B.23.010, B.21.020, A.16.010; D.41.020 monthly |
| 40 | **Amendment No. 1** | Extension of time to 31-Mar-2026; E.54.010 and B.23.010 rates from **01-Oct-2025** |
| 41 | **Supplement No. 2** | D.41.020 → 228.00; **5 % discount** on 4 items |
| 42 | **Amendment No. 2** | Extension of time to 30-Sep-2026; E.54.010 monthly; **8 % discount** |
| 43 | **Amendment No. 3** | **Retroactive** from 01-Nov-2025: C.32.010, A.14.010 |

### 5.2 DDS-2025-118 — 42 pages

| Page | Content | Pricing-relevant terms |
|---|---|---|
| 1 | Form of Agreement | Ref DDS-2025-118; parties; Commencement **01-Jan-2025**; Expiry **31-Dec-2025**; USD; VAT 15 %; "rounding to the cent, half to even, at each step"; per-well invoicing within 30 days |
| 2 | Contents | Parts I–VII, Sch 1–6, App A–C. **Omits** Parts VIII–IX, Sch 2C/2D/7/8, App D–G, the Schedule of Variations and the instruments |
| 3–4 | Part I, Cl.1–14 | Cl.2: a Schedule prevails over a Part, and Part VI over Parts I–V. **Cl.4: class per call-off for the whole well.** Cl.13: a suspension day recorded as Standby is charged under Cl.20 |
| 5 | Part II, Cl.15–16 | **DDR content and signatures** (Company Representative and lead DD); BHA run, gyro, source and LIH records |
| 6 | Part III, Cl.17–25 | **Cl.17** half-even at each step. **Cl.18** build-up order. Cl.19 status and section per the DDR. **Cl.20** standby %; "not chargeable" items get nothing. **Cl.21** DD-120 per circulating hour, **minimum 6 h** per Operating day; DD-121 on Standby. **Cl.22** personnel per the DDR, with daily limits. **Cl.23** PD-210 depth bands, split at boundaries (boundary depth goes to the shallower band). Cl.24–25 LWD and reaming metres |
| 7 | Cl.26–31 | **Cl.26** DD-111 once per run, on its last day; LW-420 once per source run, on its first day. **Cl.27** MB-701 and DD-140 on the well's first day; LW-430 and MB-702 on its last day. **Cl.28** rental only when in the hole. **Cl.29** no service twice per well-day. **Cl.30** counts per the DDR. **Cl.31** LIH: 1 % depreciation per *complete* 25 circulating hours, maximum 50 % |
| 8 | Part IV, Cl.32–42 | Per-well periods; **window ≤ 30 days**, not before the last day; unit (35); net (36); Sch 5 condition (37); **DS-900 4 % over 250k (38)**; VAT (39); total (40) |
| 9–10 | Part V, T1–T16 | Technical context (T5, T9, T11, T13, T14, T16) |
| 11–12 | Part VI, P1–P14 | P1 prevails. P2/P3 class per call-off. **P4 no charge on rig-move days.** P5 weather = Standby. **P6 failed tool charged only when recorded in the hole.** **P7 crew change counted once.** P8/P9 no night or holiday uplift. **P10 minimum per day.** P11 discount per invoice. P12 LIH hours include the day of loss. P13 standby personnel. P14 USD |
| 13 | Part VII, H1–H12 | H6: source handling certificate per run |
| 14 | Part VIII, R1–R12 | R4 circulating hours rounded (≥ 30 min = 1 h). **R5/R6 reports list tools and personnel by service code** (conflicts with §19A). R7 status is final. R8 corrections |
| 15–16 | **Sch 1** service rates | 38 codes (Appendix A2). PD-210 → Sch 2; LH-711…714 → Cl.31 |
| 17 | **Sch 2** PD-210 | Bands 0–1,500 m 42.35; ≤ 3,000 m 58.15; ≤ 4,500 m 76.45; > 4,500 m 98.70. Note "class-rated" (conflicts with §17B). **Part 2** Contract-Year metres tier 100 / 96 / 92 % |
| 18 | **Sch 2C** indexed | MW-310, HC-620 × Rig Services Index (monthly 2025-01 → 2026-12) |
| 19 | **Sch 2D** LIH in SAR | LH-711…714 SAR values; halalas-per-USD table (same as CW Sch 2B) |
| 20–22 | **Sch 3** Parts 1–7 | Section factors; class factors; **standby %** and "NC"; DD-121 on Standby only; **daily limits**; once per well; DD-120 minimum 6 h |
| 23 | Sch 4 personnel | Charged numbers follow the DDR, not this table |
| 24 | **Sch 5** DDR parts as a condition of payment | DD-111, LW-410/411/412, LW-413, RM-510 → Part B; DD-130 → C; LW-420 → D; LH → E. **"No separate run/survey/source/loss documents"** |
| 25 | Sch 6 LIH values (USD) | 145,000 / 1,250,000 / 385,000 / 520,000; depreciation rule |
| 26 | Sch 7 tool specifications | Designed sections; what is charged follows the DDR |
| 27–28 | **Sch 8** scope of each charge | DD-102 "each day the DDR records the tool in the hole" (conflicts with the intro "per coordinator"). DD-120/RM-530 "circulating **or back-reaming** hour" (conflicts with Cl.21). HC-630 "each BHA run" (conflicts with Cl.30) |
| 29 | App A definitions | Day 00:00–24:00; hole section = bit size; performance-drilled section = a nominated 12-1/4" or 8-1/2" section |
| 30 | App B form of invoice | Worked example (HPHT, Standby, PD-210 split, **no Sch 2C indexation, no class factor on PD-210**); net 25,662.26 → VAT 3,849.34 → total 29,511.60; discount example: 312,400 → −2,496.00 |
| 31 | App C + Execution | Insurances, notices |
| 32–34 | App D–F | Illustrative DDR (with codes), BHA run and gyro/LIH forms; LIH example 412 h → 16 % |
| 35 | **Part IX** second series | **§3A** Contract Years. **§17A** indexed rate, half-even. **§17B no section factor on Standby; no class factor on PD-210.** **§19A** DDR ref on every line; rig words, no codes. **§21A first hour not chargeable ("invoice charges one fewer").** **§25A metres +1 % tolerance.** **§31A LIH from Sch 2D SAR at the month-of-loss rate, before depreciation; Sch 2D governs.** **§36A** retro instrument → single adjustment on the first invoice *on or after* the issue date |
| 36 | **App G** field-report terms | Rig word → code (Appendix A2). Footnote: LIH value "Schedule 6 states" (conflicts with §31A) |
| 37 | **Schedule of Variations** | Order issued; term as extended 01-Jan-2025 → 31-Dec-2026 |
| 38 | **Supplement No. 1** | DD-120, DD-121 rates; HC-601 monthly |
| 39 | **Amendment No. 1** | Expiry → 30-Jun-2026; DD-101, MW-301, LW-401 |
| 40 | **Supplement No. 2** | DD-120 monthly; **4 % discount** on 5 codes |
| 41 | **Amendment No. 2** | Expiry → 31-Dec-2026; MW-301, MB-701; **7 % discount** |
| 42 | **Amendment No. 3** | **Retroactive** from 01-Feb-2026: DD-120, DD-101 |

**Precedence.** In both contracts the Contents page and Cl.2 omit the second-series conditions, the extra schedules, the variations and the instruments. Their standing rests on the Schedule of Variations ("read … in the order issued") and each instrument's footer ("the later governs work on or after its effective date").
* Every instrument cites a clause that does not exist: CW "Cl.26.4", "14.2", "26.6"; DDS "19.3", "19.1", "16.4".
* CW has further broken cross-references: Cl.21 and P25 point to App A for insurances and notices, and P18 points to Cl.33.
* None of these is pricing-relevant, but all belong in the decision log.

## 6. Amendment and effective-date structure

### 6.1 Civil — instruments (CW p38–43) and standing date-driven terms

| Instrument | Issued | Effective | What changes |
|---|---|---|---|
| Subcontract (p1) | — | 05-Jan-2025 | Completion 27-Sep-2025 |
| Supplement 1 (p39) | 24-Mar-2025 | 01-May-2025 | B.23.010 4,120.00 → 4,385.00; B.21.020 415.00 → 431.50; A.16.010 1,480.00 → 1,524.00. **D.41.020 monthly:** May-25 214.50, Jun 219.80, Jul 226.40, Aug 223.10, Sep 220.50; the last published rate carries forward |
| Amendment 1 (p40) | 18-Aug-2025 | 28-Sep-2025 | Completion → **31-Mar-2026** (185 days). E.54.010 876.00 → 948.00 and B.23.010 4,385.00 → 4,450.00, each **effective 01-Oct-2025**. The data follows 01-Oct: B.23.010 on 28–30 Sep is billed at 4,385 |
| Supplement 2 (p41) | 12-Nov-2025 | 01-Dec-2025 | D.41.020 220.50 → 228.00. **5 % discount** on C.32.030, C.32.010, D.41.020, B.23.010: final factor, after the band rebate, before rounding |
| Amendment 2 (p42) | 16-Feb-2026 | 01-Apr-2026 | Completion → **30-Sep-2026** (183 days). **E.54.010 monthly:** Apr-26 976, May 991, Jun 1,013, Jul 1,038, Aug 1,038, Sep 1,052. Discount deepened to **8 %** on the same four items |
| Amendment 3 (p43) | **12-May-2026** | **01-Nov-2025 (retro)** | C.32.010 1,860.00 → 1,984.00; A.14.010 53.20 → 56.80. Already-certified work is re-measured, with a **single adjustment** on the first application submitted "*after*" issue (A3) or "*on or after*" issue (§31A) |

Standing date-driven terms:
* Sch 2A monthly index (§29A) and Sch 2B monthly FX (§26A) apply by the **month of execution**.
* §27A switches ground to **G2 for work after 27-Sep-2025**.
* Sch 4 Pt 3 bands count per **Contract Year** (§3A). CY1 runs 05-Jan-2025 → 04-Jan-2026; CY2 runs 05-Jan-2026 → 30-Sep-2026, and the data supports this (§10.3).
* Rest days (Fri/Sat) and night work follow the work date.
* **Work executed after 30-Sep-2026 is not payable.**

### 6.2 Drilling — instruments (DDS p37–42) and standing date-driven terms

| Instrument | Issued | Effective | What changes |
|---|---|---|---|
| Contract (p1) | — | 01-Jan-2025 | Expiry 31-Dec-2025 |
| Supplement 1 (p38) | 19-May-2025 | 01-Jul-2025 | DD-120 384.15 → 398.50; DD-121 2,893.65 → 2,984.00. **HC-601 monthly:** Jul-25 701.50, Aug 714.00, Sep 722.60, Oct 719.80, Nov 731.00, Dec 736.40; the last published rate carries forward |
| Amendment 1 (p39) | 07-Nov-2025 | 01-Jan-2026 | Expiry → **30-Jun-2026**. DD-101 → 1,916.50; MW-301 → 1,708.00; LW-401 → 1,969.00 |
| Supplement 2 (p40) | 24-Feb-2026 | 01-Apr-2026 | **DD-120 monthly:** Apr-26 406.00, May 411.50, Jun 411.50, Jul 423.00, Aug 429.50, Sep 434.00, Oct 434.00, Nov 441.00, Dec 447.50. **4 % discount** on DD-101, MW-301, LW-401, DD-120, MB-701 (last factor; separate from, and before, Cl.38) |
| Amendment 2 (p41) | 21-May-2026 | 01-Jul-2026 | Expiry → **31-Dec-2026**. MW-301 → 1,763.00; MB-701 → 19,237.00. Discount deepened to **7 %** |
| Amendment 3 (p42) | **17-Aug-2026** | **01-Feb-2026 (retro)** | DD-120 398.50 → 416.00; DD-101 1,916.50 → 1,954.00. **Single adjustment** on the first invoice submitted "*after*" issue (A3) or "*on or after*" issue (§36A) |

Standing date-driven terms:
* Sch 2C monthly index (§17A) and Sch 2D FX at the **month of loss** (§31A).
* The Sch 2 Pt 2 metres tier counts per Contract Year (§3A).
* **Services after 31-Dec-2026 are not chargeable.**

## 7. How the source evidence connects to invoice charges

### 7.1 Civil (all figures verified in the data)

* **Record presence follows Sch 5 exactly.** 2,193 of 2,197 Sch-5 lines carry a `record_ref`, and none of the 5,549 other lines do. The blank refs on 72 % of lines are therefore legitimate. The exceptions:
  * 4 Sch-5 lines carry no ref.
  * 3 refs point to missing files: `CT-00126`, `MO-00089`, `PS-00039`.
  * 1 line cites the wrong series: `PA-00170-04` (B.23.020) cites `PT-00189`, which `PA-00238-09` also cites.
* **Record → line:**
  * **Daily records:** `Area` must equal the work area and `Date` the work date. Both agree in 2,055 of 2,056 cases.
  * **Weekly DW logs:** the work date falls in the logged week in 134 of 134 cases, and every log shows 5–7 days on, so all satisfy the ≥ 5-day rule (§47A).
  * **Item wording:** the sentence identifies the item. "trench dig 147 cube, 3 m deep" means A.12.030; "trench over four metres" means A.12.040. "wall / slab / foundation pour" means B.21.040 / B.21.030 / B.21.020. "laid … m2 of A393 mesh" means B.23.020; "tracked machine stood idle 7 hours" means E.51.030. DX and PR wording agrees with the billed item on 100 % of lines.
* **Quantity rules confirmed in the billed data:**
  * Hourly items (E.51.010, E.51.030) are billed at **recorded hours − 1** on 284 of 285 lines (§6A).
  * Where a joint-survey item is billed above the survey, 25 of 27 lines stay within **+2 %** (§33A).
  * Billing below the record is common (B.23.010 and E.52.010 at −1, B.23.020 below the survey). That is payable as billed.
* **Signatures.** The six foreman names and four Engineer's-representative names never overlap, and no record has the same person in both roles. One record, **DX-00089**, has a blank countersignature line; it is cited by `PA-00613-01`.
* **One record per charge.** Twenty records are cited by more than one line, 41 lines in all. Nineteen are weekly DW logs, one of which is cited three times; the twentieth is `PT-00189`.

### 7.2 Drilling (all figures verified in the data)

* Every service line cites a DDR; the 63 blank refs are exactly the 63 `DS-900` lines. **Eight lines cite a report for a different day than their service date:**
  * the 3 lines dated outside their invoice period;
  * the 3 lines dated after the extended term, each of which cites a report from months earlier;
  * `MDS-00128-026` and `MDS-01352-007`, which cite the previous day's report.
* **DDR field → charge:**
  * `Status` and `Hole section` select the factors (Cl.19).
  * **Crew words** set the person-days (Cl.22), mapped by App G: directional hands → DD-101, **night man → DD-102**, MWD engineers → MW-301, logging engineers → LW-401, performance engineer → PD-201.
  * **Tool words** ("In the hole") trigger day rentals (Cl.28).
  * Counts bill exactly on **100 %** of lines: gyro surveys → DD-130, pressure points → LW-413, wiper trips → HC-610, clean-out runs → HC-630.
  * **Circulating hours − 1 → DD-120** on 4,601 of 4,606 lines, and **back-reaming hours − 1 → RM-530** on 941 of 943 (§21A).
  * **Depth start/end → metres.** PD-210 daily metres match exactly on 100 % of days, split by depth band. LW-410/411/412 and RM-510 metres match on 99.9 %; 7 lines exceed +1 % (§25A).
  * **Part B** gives each run's first and last day for DD-111 (last day) and LW-420 (first day, needs Part D).
  * **Part E** gives the circulating hours accumulated on the well, which drive LIH depreciation.
* **Glossary effects.** Billing follows **Appendix G even where it cuts across the Sch 1 descriptions**:

  | Report word | Billed code | Sch 1 description of that code |
  |---|---|---|
  | gamma tool | LW-410 | "LWD resistivity, logged" |
  | resistivity tool | LW-411 | "density and neutron" |
  | density-neutron | LW-412 | "sonic" |
  | float sub | HC-640 | "cuttings bed monitoring" |
  | bit and reamer | PD-220 | — |
  | hydraulics package | PD-230 | — |
  | hole opener | RM-511 | — |
  | survey package | MW-320 | — |

  Counts line up, for example 1,190 "bit and reamer" days against 1,190 PD-220 lines.
* **DDR integrity.** All 8,151 report IDs match their file names and all state contract DDS-2025-118. Parts A and B appear in every report, C in 479, D in 367 and E in 54. **Three DDRs carry no signatures at all** (both lines blank).

## 8. Submission requirements and evaluation criteria

* **One file with all 2,806 rows**, template ids unchanged:
  * `flagged`: 1 or 0. A 0 is a claim ("audited, found nothing"), not a blank.
  * `error_category`: free-text label, blank when not flagged. Consistency is what is scored.
  * `expected_total_cents`: the total the contract supports, in integer minor units.
  * `billed_total_cents`: `application_total` or `invoice_total` × 100.
  * `confidence`: between 0 and 1.
  * Rows that cannot be priced are still rows: flag them if they are believed wrong, state the confidence honestly and explain in the report.
* **Scoring:**
  1. Precision, recall and F1 on `flagged`, overall and **by severity**. The README does not define severity.
  2. **Cost = 5 × FN + 1 × FP.** This implies flagging whenever P(wrong) > 1/6.
  3. **Amounts:** for flagged rows, whether the expected total equals the contract-supported figure.
  4. **Calibration** of confidence against precision per band. A confident but wrong extraction is penalised.
  5. **Category consistency.**
* **Deliverables:** listed in §1. The decision log must record each clause read two ways (see §10).

## 9. Important facts later implementation must account for

**Arithmetic and rounding (all verified):**
* **CW:**
  * The rate is rounded once, half-up, after the full build-up (Cl.28). USD conversion and indexation round half-even *first* (§26A, §29A).
  * When a line crosses a band threshold, **it is split into parts, each at its own rounded rate** (Cl.28/30). At least 14 of the 32 civil lines where `amount ≠ qty × rate` are such legitimate splits, i.e. odd-looking but correct.
  * Retention is `floor(5 % × total)` on 900 of 900 applications.
* **DDS:**
  * Half-even at each step (Cl.17).
  * VAT is half-even on 1,906 of 1,906 invoices.
  * `DS-900` equals −4 % × (services − 250,000) on 63 of 63 invoices.
  * Net equals Σ lines on all 1,906 invoices.
* **Use exact decimal arithmetic.** Binary floats mis-round half-cent cases: 423.00 × 0.945 = 399.735 should become 399.74 half-even, but a float gives 399.73.

**Rates and build-up.** Beyond the Sch 1 values, the data confirms the following readings.

Civil:
* Zone factors apply to Series A–D only.
* Ground factors apply only to the **15 items listed in Sch 3**, not to whole "series" as Cl.29 says.
* Night uplift applies to the 13 listed items only, **never where the zone factor exceeds 1.1** (§27A).
* **Rest-day uplift alone** applies when both uplifts could (P11).
* **Ground is taken as G2 after 27-Sep-2025** (§27A).
* **Sch 2A indexation and Sch 2B USD conversion are applied**, even though App B's example omits indexation and Sch 1's column header says "SAR".

Drilling:
* **§17B applies:** no section factor on Standby days and no class factor on PD-210. PD-210 is billed at the plain Sch 2 band rate on 99.7 % of lines.
* The **Sch 2 Pt 2 metres tier is never applied** in billing.
* DD-121 appears on Standby days only (Sch 3 Pt 4).
* After Amendment 3 was issued, **DD-101 is billed at 1,954.00 and DD-120 at a flat 416.00**. The S2 monthly table then stops being used, even for months where it was higher.
* **LIH follows §31A:** Sch 2D SAR ÷ month-of-loss FX, then 1 % per complete 25 h. This matches 46 of 54 LIH lines. The Sch 6 USD reading matches only 6 lines, all in months where the rate is exactly 375.00, so the two readings give the same figure there.

**Term, window and period facts in the data (raw observations, not audit outcomes):**

| Observation | Civil | Drilling |
|---|---|---|
| Lines after the extended term | 2: PA-00375-07 and PA-00678-10, in the only two applications with very long periods (276 and 264 days) | 3: MDS-01619-045, MDS-01798-045 and MDS-01860-039, in the only three invoices with long periods (166, 113 and 81 days). Each cites an earlier DDR |
| Submitted before the period's last day | PA-00125 (−14 d) | MDS-00645, MDS-00828, MDS-01258 |
| Submitted late | PA-00613 (26 d), PA-00708 (44 d), PA-00699 (49 d) | MDS-00537 (46 d), MDS-00199 (51 d), MDS-00038 (55 d) |
| Line dated outside the stated period | PA-00154-03, PA-00700-01 | MDS-00164-050, MDS-00541-018, MDS-00895-051 |
| Contract-reference variants | PA-00560, PA-00711 (`CW-2024-…`) | MDS-00672, MDS-00988 (`DSS-…`); MDS-01799 (`…-181`) |
| Header arithmetic | PA-00043 total exceeds Σ lines by 32.18 | MDS-00551, MDS-00916, MDS-01317: total ≠ net + VAT |

**Other raw signals (not yet audited):**
* Three invoices have services above 250k but no `DS-900` line: MDS-00072, MDS-00282, MDS-01049.
* MB-701 is billed twice on three wells: NGP-QA-054, NGP-QA-171, NGP-WS-192.
* Three drilling lines have `amount ≠ qty × rate`.
* After applying the transcribed terms, 36 civil lines and about 40 drilling lines still mismatch. They fall into recognisable patterns:
  * superseded rates;
  * factors from the wrong zone, section, class or index month;
  * standby charged at the operating rate;
  * discounts taken early or omitted;
  * DD-121 on Operating days;
  * one-halala intermediate rounding.

## 10. Material findings that need closer examination next phase

1. **Retroactive Amendment 3 and its single adjustment** (CW p43 + §31A; DDS p42 + §36A).
   * Every `adjustment` value is 0.00, so either the adjustment is missing everywhere or it is expected somewhere not yet identified.
   * **Which invoice is "first" is unclear.** The instruments say "*after*" the issue date; §31A and §36A say "*on or after*".
     * Civil ties: PA-00006, PA-00023 and PA-00380 are all dated 12-May-2026, the issue date. The next is PA-00443 on 14-May.
     * Drilling ties: MDS-01625 is dated 17-Aug-2026, the issue date. Then MDS-01585, MDS-01631 and MDS-01645 are all dated 18-Aug.
   * Invoices dated *on* the issue date already carry the new rates (PA-00006 and PA-00380 for A.14.010; MDS-01625 for DD-101 and DD-120), so the data treats issue day as "on or after".
   * Still to decide: how to compute the adjustment amount, and whether it belongs inside the judged total. By Cl.43 `application_total` is Σ lines, whereas §45A adds adjustments only to the amount *payable*.
   * Both Schedules of Variations say nothing reopens already-measured work, which conflicts with the Amendment 3s.
2. **DDS Amendment 3 versus the S2 monthly DD-120 table.** After issue, the billing uses 416.00 for every month from Feb-2026, including months where S2 was higher (Jul 423.00, Aug 429.50). I need to confirm this reading. I also need to confirm that pre-issue invoices stay correct, as §36A says.
3. **Contract Years and cumulative bands** (CW §3A; Sch 4 Pt 3, "Clause 30 is substituted").
   * Billed band rates return to 100 % in January 2026: A.14.010, B.22.010, A.12.020 and D.41.010 splits cross the first threshold again in Jan–Feb 2026.
   * That fits CY2 starting on 05-Jan-2026, not a single year extended to 30-Sep-2026.
   * Still to pin down: the exact cumulative ordering (date, then application number, then line number, per Cl.30), and how a line that crosses a threshold is split.
4. **DDS Sch 2 Pt 2 metres tier:** "metres already drilled on the well in the Contract Year" can be read per well or contract-wide. Contract-wide would reprice nearly all PD-210 lines, which were billed at 100 %. Calibration therefore favours per well, which is never binding. To be confirmed.
5. **Conflicting sources where the data already indicates the reading** (each needs a decision-log entry):
   * Sch 2 note versus §17B on PD-210;
   * App B's example versus §29A indexation;
   * Sch 2B versus Sch 1's "Rate (SAR)" header;
   * Sch 6 and App G's footnote versus §31A and Sch 2D;
   * Cl.33 ("exactly") versus §33A (+2 %);
   * Cl.29 ("series") versus Sch 3's item list;
   * A1's instrument date (28-Sep) versus its item dates (01-Oct).
6. **Identification ambiguities (guideline 6: leave unresolved rather than choose on price):**
   * **Drilling:**
     * "gamma tool" is App G's word for LW-410, but it also appears in MW-310's Sch 1 description.
     * R5/R6 require codes in reports, while §19A says reports carry none, and indeed they carry none.
     * Sch 8 describes DD-102 two ways.
     * Sch 8 counts back-reaming hours in DD-120, which Cl.21 does not.
     * HC-630 is either per run (Sch 8) or a count (Cl.30).
   * **Civil:** Cl.47 requires the item code on the record, but §47A and Sch 5 say the record need not repeat it.
7. **Expected-total semantics per failure type, needed for amount scoring:**
   * Wrong contract reference, out-of-window submission or out-of-term work: is the whole invoice unpayable, or only the affected lines?
   * Unevidenced line: Cl.46 makes it not payable, but P23 deducts it from the *next* valuation.
   * Duplicates: the later measurement is disallowed in full (Cl.44). This includes weekly items billed on different dates in the same week, as with the 19 DW logs cited more than once. It also includes drilling charges re-dated onto another day or invoice (the 8 lines citing another day's DDR).
   * Quantity over the record: cap at the record, net of tolerances.
   * **Under-billing**, such as a superseded lower rate: flag it or not, and what expected figure to give.
8. **Cross-invoice state:**
   * Civil: daily limits per work area per day across applications (Sch 4 Pt 4); the A.14.020 exclusion within 2 days of A.14.010; P21's ban on E.51.020 on surfacing days; E.53.010 per P6.
   * Drilling: once-per-well items on the well's first and last day, which needs each well's full day range across invoices; per-run first and last days; the Sch 3 Pt 5 daily limits; Cl.29 (one service per well-day, 3 duplicate well-day-code groups seen).
9. **Drilling special days:**
   * 381 Standby DDRs, with their "NC" services and standby percentages.
   * P4 rig-move days, P6 tool failures, P7 crew changes.
   * The Cl.21 minimum of 6 h never binds on billed DD-120 lines. Days with a rotary steerable in the hole but no DD-120 still need checking.
10. **Civil conditions with no obvious data field:** P2 flood watch, P9 heat suspension, H15 safety suspension, P3, P4, S4 (unrecorded ground → G2), P14 and H2. Check whether MO or PS record wording ever signals any of them.
11. **Retention release (§45A):** the first application after 30-Sep-2026 is PA-00678 (28-Oct-2026), and it shows `retention_released` 0.00. This probably affects net payable rather than the judged total. Decide whether it is relevant.
12. **Severity:** the scoring uses it, but the README never defines it. We need a working definition, for example money at stake, or error class.

## 11. What the next phase must establish before implementation begins

1. **A machine-readable, page-cited contract-terms file per contract.** It should hold:
   * rates by instrument and effective date;
   * factor lists;
   * the index, FX and monthly tables;
   * bands, limits, exclusions and once-only items;
   * record requirements and the glossary.

   Every numeric table should be re-read against the scan a second time. The billed-rate reconciliation harness used here then serves as a regression check: civil ≥ 99.5 %, and drilling close to 100 % once Amendment 3 timing and Decimal arithmetic are in place.
2. **A written decision for every item in §10**, each tested against the calibration rule: does this reading reprice invoices that reconcile exactly?
3. **Payable-amount semantics per failure type**, and how line corrections roll up:
   * Civil: Σ payable lines; retention is not in the judged total.
   * Drilling: payable services → recompute DS-900 on the corrected services → VAT → total.
4. **Record parsers and vocabulary maps with measured coverage:**
   * Civil: sentence patterns per series (quantity, unit words, depth and pour-type words), and the day lists in weekly logs.
   * Drilling: DDR key-value fields, the App G crew and tool words, and Parts C, D and E.
5. **Global computations with explicit ordering rules:**
   * cumulative bands per Contract Year;
   * cross-invoice duplicates, with "later" defined;
   * once-per-well and per-run first and last days;
   * daily limits and exclusions per work area.
6. **An error taxonomy, severity scheme and confidence plan.** Confidence should reflect evidence strength: deterministic arithmetic scores higher than an interpretive reading. The cost function implies flagging above roughly P = 1/6.
7. **A plausibility budget.** The union of candidate findings should land near 5–8 %, about 140–225 invoices. A much larger count means some reading is repricing correct invoices.
8. **Reproducibility from the start:** pinned dependencies, exact decimal arithmetic, deterministic ordering, and prompt files versioned in the repo.

## 12. Approximate time spent

**About 50 minutes** of wall-clock time (18:51 → about 19:40 UTC, 22-Sep-2026):

| Activity | Time |
|---|---|
| Brief, guidelines and repo structure; profiling the CSVs and records | ~10 min |
| Reading and transcribing all 85 scanned pages (the civil pages were read twice to capture a verbatim transcription) | ~20 min |
| Checking the transcription against billed rates and records (extraction and calibration checks) | ~10 min |
| Writing and fact-checking this report | ~10 min |

---

## Appendix A1 — Civil extracted tables (CW p17–27, p39–43)

**Sch 1 base rates** (SAR unless noted; units as listed):

| Item | Unit | Rate | Item | Unit | Rate | Item | Unit | Rate |
|---|---|---|---|---|---|---|---|---|
| A.11.010 | m2 | 3.85 | B.21.010 | m2 | 29.60 | C.31.010 ᴵ | lm | 86.20 |
| A.11.020 | m2 | 12.40 | B.21.020 | m3 | 415.00 | C.31.020 | lm | 214.00 |
| A.11.030 | no. | 148.00 | B.21.030 | m3 | 389.00 | C.31.030 | lm | 54.80 |
| A.12.010 | m3 | 21.50 | B.21.040 | m3 | 448.00 | C.31.040 | lm | 73.10 |
| A.12.020 | m3 | 34.80 | B.21.050 | m3 | 296.00 | C.32.010 | no. | 1,860.00 |
| A.12.030 | m3 | 47.60 | B.22.010 | m2 | 74.50 | C.32.020 | no. | 287.00 |
| A.12.040 | m3 | 69.20 | B.22.020 | m2 | 91.80 | C.32.030 | no. | 3,120.00 |
| A.12.050 | m3 | 52.40 | B.22.030 | lm | 42.60 | C.32.040 ᵁ | no. | 423.00 |
| A.12.060 | m2 | 6.90 | B.23.010 | tonne | 4,120.00 | C.33.010 | lm | 59.10 |
| A.13.010 | m3 | 18.90 | B.23.020 ᵁ | m2 | 38.40 | C.34.010 | no. | 965.00 |
| A.13.020 | m3 | 6.40 | B.24.010 | lm | 67.40 | C.35.010 | lm | 9.40 |
| A.13.030 | m3 | 9.80 | B.25.010 ᵁ | no. | 219.00 | D.41.010 | m2 | 41.80 |
| A.14.010 | m3 | 53.20 | B.26.010 | m2 | 17.20 | D.41.020 | m2 | 63.50 |
| A.14.020 | m3 | 22.40 | B.27.010 | lm | 89.50 | D.41.030 ᴵ | m2 | 89.40 |
| A.14.030 | m2 | 14.60 | E.51.010 | hour | 246.00 | D.41.040 | m2 | 32.60 |
| A.15.010 | m2 | 31.80 | E.51.020 | day | 684.00 | D.41.050 | m2 | 6.20 |
| A.15.020 | m2 | 49.50 | E.51.030 | hour | 312.00 | D.42.010 | lm | 71.20 |
| A.16.010 | week | 1,480.00 | E.52.010 | no. | 478.00 | D.42.020 | lm | 64.80 |
| | | | E.53.010 | day | 389.00 | D.42.030 | lm | 39.40 |
| | | | E.54.010 | week | 876.00 | D.43.010 | lm | 14.80 |
| | | | | | | D.43.020 | m2 | 42.60 |
| | | | | | | D.44.010 | no. | 31.80 |

ᴵ Indexed under Sch 2A / §29A. ᵁ Rate is in USD under Sch 2B / §26A.

**Unit anomalies in the data.** A.14.020 is also billed in `no.`, A.14.030 in `lm`, C.31.040 in `no.` and D.42.010 in `no.`. Under Cl.26 a line in a non-Sch-1 unit is rejected in its entirety.

**Factors and uplifts**

* **Zones** (Series A–D only): Z1 1.00, Z2 1.06, Z3 1.145, Z4 1.28.
* **Ground:** G1 0.94, G2 1.00, G3 1.12, G4 1.375, G5 1.63. Applies to A.11.020, A.12.010–A.12.050, A.14.020, A.15.010, A.15.020, C.31.010, C.31.020, C.31.030, C.32.010, C.32.030, C.33.010.
* **Night uplift:** A.12.020, A.12.030, A.12.040, A.14.010, C.31.010, C.31.030 at 18 %; B.21.020, B.21.030, B.21.040 at 22 %; D.41.020, D.41.030, D.43.010, D.43.020 at 25 %.
* **Rest-day uplift** (Fri/Sat): B.21.020, B.21.030, B.21.040, D.41.030 at 35 %.

**Banded quantities** (per Contract Year):

| Item | Bands |
|---|---|
| A.12.010 | 1–4,000 at 100 % · 4,001–16,000 at 96 % · > 16,000 at 93 % |
| A.12.020 | 1–1,500 at 100 % · 1,501–6,000 at 97 % · > 6,000 at 94 % |
| A.13.010 | 1–5,000 at 100 % · 5,001–20,000 at 94 % · > 20,000 at 90 % |
| A.14.010 | 1–2,000 at 100 % · 2,001–8,000 at 95 % · > 8,000 at 91 % |
| B.22.010 | 1–1,200 at 100 % · 1,201–4,800 at 96 % · > 4,800 at 93 % |
| B.23.010 | 1–60 at 100 % · 61–240 at 97 % · > 240 at 94 % |
| D.41.010 | 1–4,500 at 100 % · 4,501–18,000 at 95 % · > 18,000 at 92 % |
| D.41.040 | 1–3,500 at 100 % · 3,501–14,500 at 95 % · > 14,500 at 92 % |

**Limits and special items**

* **Daily limits** (per work area per day): A.11.010 4,500; A.12.010 1,200; B.21.020 140; C.32.010 6; D.41.030 3,200; E.51.020 1; A.13.030 800; C.32.030 3; E.53.010 2.
* **Exclusion:** A.14.020 cannot be measured within 2 days of A.14.010 on the same work area.
* **Surveyed items:** B.23.010, E.52.010, B.23.020.

**Sch 5 records required**

| Series | Items |
|---|---|
| DX | A.12.030, A.12.040 |
| CT | A.14.010, D.41.010, D.41.040 |
| PR | B.21.020, B.21.030, B.21.040 |
| PT | C.31.020, C.32.030 |
| MO | E.51.010 |
| DW | A.16.010 |
| CV | C.35.010 |
| PS | E.51.030 |
| JS | B.23.010, E.52.010, B.23.020 |

**Site Materials Index** (Sch 2A):

| Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | 100.00 | 100.40 | 101.10 | 101.80 | 102.60 | 103.90 | 104.70 | 104.20 | 105.30 | 106.80 | 107.40 | 108.10 |
| 2026 | 109.60 | 110.20 | 109.80 | 111.50 | 112.30 | 113.10 | 112.40 | 113.80 | 114.60 | 115.20 | 115.90 | 116.50 |

**Halalas per USD** (Sch 2B; identical to DDS Sch 2D):

| Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | 375.00 | 375.10 | 375.00 | 374.90 | 375.20 | 375.30 | 375.10 | 375.00 | 374.80 | 375.40 | 375.60 | 375.50 |
| 2026 | 376.00 | 375.80 | 375.90 | 376.20 | 376.40 | 376.10 | 375.70 | 376.30 | 376.60 | 376.80 | 377.00 | 376.50 |

## Appendix A2 — Drilling extracted tables (DDS p15–25, p36, p38–42)

**Sch 1 rates** (USD). The mark † flags codes whose value was *not* independently confirmed by the billed-rate check, because those lines are priced through another schedule.

| Code | Unit | Rate | Code | Unit | Rate | Code | Unit | Rate |
|---|---|---|---|---|---|---|---|---|
| DD-101 | person-day | 1,847.35 | MW-301 | person-day | 1,646.55 | RM-510 | metre | 38.45 |
| DD-102 | day | 948.60 | MW-310 ᴵ | day | 2,245.85 | RM-511 | day | 1,379.15 |
| DD-110 | day | 1,417.75 | MW-320 | day | 779.65 | RM-520 | day | 419.85 |
| DD-111 | run | 3,589.45 | MW-330 | day | 309.75 | RM-530 | hour | 264.55 |
| DD-120 | hour | 384.15 | LW-401 | person-day | 1,898.45 | HC-601 | day | 689.35 |
| DD-121 | day | 2,893.65 | LW-410 | metre | 11.37 | HC-610 | trip | 1,947.15 |
| DD-130 | survey | 2,446.15 | LW-411 | metre | 16.83 | HC-620 ᴵ | day | 539.65 |
| DD-140 | well | 12,489.50 | LW-412 | metre | 13.29 | HC-630 | run | 4,295.85 |
| PD-201 | person-day | 2,094.85 | LW-413 | point | 1,849.65 | HC-640 | day | 719.55 |
| PD-210 † | metre | Sch 2 | LW-420 | run | 2,746.55 | MB-701 | well | 18,497.50 |
| PD-220 | day | 1,148.35 | LW-430 | well | 8,394.75 | MB-702 | well | 14,196.25 |
| PD-230 | day | 639.15 | LH-711…714 † | each | Cl.31 | | | |

ᴵ Indexed under Sch 2C / §17A.

**Rig Services Index** (Sch 2C):

| Year | Jan | Feb | Mar | Apr | May | Jun | Jul | Aug | Sep | Oct | Nov | Dec |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2025 | 100.00 | 100.70 | 101.50 | 102.30 | 103.10 | 103.60 | 104.80 | 105.40 | 104.90 | 106.20 | 107.10 | 108.00 |
| 2026 | 109.30 | 110.00 | 110.60 | 111.40 | 110.90 | 112.20 | 113.00 | 112.60 | 113.90 | 114.70 | 115.30 | 116.10 |

**Lost-in-hole values** (Sch 2D, governing per §31A). Sch 6 gives the USD equivalents at 3.75.

| Code | SAR | Sch 6 USD |
|---|---|---|
| LH-711 | 543,750.00 | 145,000 |
| LH-712 | 4,687,500.00 | 1,250,000 |
| LH-713 | 1,443,750.00 | 385,000 |
| LH-714 | 1,950,000.00 | 520,000 |

Halalas per USD: the same table as Appendix A1.

**Sch 3 factors and rules**

* **Hole-section factors:** 26" 1.315; 17-1/2" 1.145; 12-1/4" 1.00; 8-1/2" 0.945; 6" 0.885. Section-rated codes: DD-110, DD-120, PD-220, MW-310, RM-510, RM-511.
* **Class factors:** Standard 1.00; Extended Reach 1.175; HPHT 1.325. Class-rated codes: DD-120, MW-310, MW-320, LW-410, LW-411, LW-412, LW-413, plus PD-210 per Sch 2, which §17B overrides.
* **Standby %:**
  * 100 %: DD-102, DD-111, MW-330, LW-420.
  * 80 %: DD-101, PD-201, MW-301, LW-401.
  * 50 %: DD-110, PD-220, PD-230, MW-310, MW-320, RM-511, RM-520, HC-601, HC-620.
  * Not chargeable: DD-120, DD-130, PD-210, LW-410, LW-411, LW-412, LW-413, RM-510, RM-530, HC-610, HC-630, HC-640.
  * Per-well and loss items are charged in full.
* **Daily limits** †: DD-101 2; DD-102 1; DD-110 1; DD-120 24 h; DD-121 1; DD-130 3; PD-201 1; PD-220 1; PD-230 1; MW-301 2; MW-310 1; MW-320 1; MW-330 1; LW-401 1; LW-413 12; RM-511 1; RM-520 1; RM-530 24 h; HC-601 1; HC-610 2; HC-620 1; HC-640 1.
* **Once per well:** DD-140, LW-430, MB-701, MB-702.
* **DD-120 minimum:** 6 h per Operating day.

**Sch 2 Part 2 metres tier** †: 1–40,000 m at 100 %; 40,001–120,000 m at 96 %; above 120,000 m at 92 %.

**Appendix G glossary** (report word → code; `(+LH-7xx)` marks the lost-in-hole code for the same tool):

| Report word | Code | Report word | Code | Report word | Code |
|---|---|---|---|---|---|
| directional hands | DD-101 | MWD collar | MW-310 (+LH-713) | hole opener | RM-511 |
| night man | DD-102 | gamma tool | LW-410 (+LH-714) | stabiliser string | RM-520 |
| mud motor | DD-110 (+LH-711) | logging engineers | LW-401 | circulating sub | HC-601 |
| rotary steerable | DD-120 (+LH-712) | resistivity tool | LW-411 | drilling jars | HC-620 |
| performance engineer | PD-201 | density-neutron | LW-412 | float sub | HC-640 |
| bit and reamer | PD-220 | MWD engineers | MW-301 | | |
| hydraulics package | PD-230 | survey package | MW-320 | | |
| | | real-time link | MW-330 | | |

**Sch 5 DDR parts** †:

| Part | Services requiring it |
|---|---|
| B | DD-111, LW-410, LW-411, LW-412, LW-413, RM-510 |
| C | DD-130 |
| D | LW-420 |
| E | LH-711…714 |
