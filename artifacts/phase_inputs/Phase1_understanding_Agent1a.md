# Step 1 Understanding Report - Agent 1a

**Challenge:** Invoice Audit Exercise - Level 2  
**Reviewed:** 22 September 2026  
**Source snapshot:** [majedzahrani3/invoice-auditing-level-2](https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec), commit `aef4924dc32506b4587de8b788b5a947e6beffec`.

This is an understanding report only. No invoice classifications, expected invoice totals, submission file, or solution implementation were produced.

Inspection covered the complete README and both guidelines, all **85 scanned contract pages** through visual review supported by OCR, all five CSVs for structure and descriptive checks, and the complete record inventory for references, fields and document parts. Representative records from every civil record family and every drilling report part were read directly. This was not an audit of every individual charge.

**References:** `CW` means [civilwork/contract/CW-2025-0417-CIV.pdf][cw]; `DDS` means [drilling_services/contract/DDS-2025-118.pdf][dds]. Page references are one-based PDF pages, matching the printed page numbers. Other paths are relative to the repository snapshot above. Contract text governs over the audit guidelines; explicit replacements and exceptions must be read alongside earlier provisions.

## 1. What the challenge asks us to do

Audit every payment application under a civil engineering subcontract and every invoice under a directional drilling services contract. Determine whether each invoice is wrong, what total the contractual evidence supports, the type of error, and confidence in the conclusion. The work requires interpreting scanned contracts, their amendments, and free-text operational evidence, not merely checking multiplication.

The final population is **2,806 invoices**. The README states that **5-8% are wrong**, that some unusual-looking invoices are correct, and that no labelled development set is provided. The prevalence is an organizer statement, not a finding verified in this phase. The repository contains synthetic data and says external information is unnecessary. [Source: [README.md][readme], introduction, task, scoring and ground rules.]

## 2. Repository and dataset structure

The following counts were computed from the actual files, excluding CSV headers.

| Repository path | Verified contents |
|---|---|
| `README.md` | Challenge brief, scoring, ground rules and deliverables |
| `civilwork/contract/CW-2025-0417-CIV.pdf` | 43 pages; zero extracted text characters; one image object per page |
| `civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md` | Three guiding principles and twelve ordered checks |
| `civilwork/invoices/applications.csv` | 900 application headers; 13 columns |
| `civilwork/invoices/application_lines.csv` | 7,746 lines; 15 columns; 60 distinct item codes |
| `civilwork/records/` | 2,169 text records in nine reference families |
| `drilling_services/contract/DDS-2025-118.pdf` | 42 pages; zero extracted text characters; one image object per page |
| `drilling_services/guidelines/INVOICE_AUDIT_GUIDELINES.md` | The same twelve checks, identified for DDS |
| `drilling_services/invoices/invoices.csv` | 1,906 invoice headers; 14 columns |
| `drilling_services/invoices/invoice_lines.csv` | 91,244 lines; 16 columns; 39 distinct service codes, including `DS-900` |
| `drilling_services/records/` | 8,151 daily drilling reports |
| `submission_template.csv` | 2,806 unique invoice IDs; all five output fields blank |

There are **98,990 invoice lines and 10,320 supporting text files**. Every line joins to an existing header, every header has lines, and `line_ref` is unique within each line file. The template IDs exactly equal the union of both header files. Civil applications contain 3-14 lines; drilling invoices contain 13-93. No solution code, scorer, labels or additional instructions were found in the checked-out file inventory.

The important fields are:

| File | Identity, context and financial fields |
|---|---|
| `applications.csv` | `application_no`; `contract_ref`, `subcontractor`, `site`, `site_zone`; `period_from`, `period_to`, `application_date`; `application_total`, `retention`, `net_payable`, `adjustment`, `retention_released` |
| `application_lines.csv` | `line_ref`, `application_no`, `line_no`; `work_date`, `site`, `site_zone`, `ground_class`, `night_work`; `item_code`, `description`, `unit`, `quantity`, `rate_applied`, `amount`, `record_ref` |
| `invoices.csv` | `invoice_no`; `contract_ref`, `contractor`, `well_name`, `rig`, `field`, `well_class`; `period_start`, `period_end`, `invoice_date`; `net_amount`, `vat_amount`, `invoice_total`, `adjustment` |
| `invoice_lines.csv` | `line_ref`, `invoice_no`, `line_no`; `service_date`, `well_name`, `hole_section`, `day_status`, `depth_from_m`, `depth_to_m`; `service_code`, `description`, `unit`, `quantity`, `unit_rate`, `amount`, `report_ref` |

Civil CSV dates use `YYYY-MM-DD`; civil tickets use `DD/MM/YYYY` or weekly day lists. Drilling dates use `DD-Mon-YYYY`. All monetary fields in the four input CSVs were verified to contain two decimal places. No currency column is present: currency comes from the applicable contract.

## 3. How the two datasets and supporting records work

**Civil works.** Al-Murjan Infrastructure Contracting Company engages Ridgeway Civil Engineering LLC for measured civil and earthworks. Valuation is based on work executed, rather than an agreed lump sum. The data cover five work areas and four zones; these are different concepts, and one work area can extend across zones. `application_no` joins headers to lines; `record_ref` identifies a record's `Ticket:` and normally its filename. [CW pp.1, 20, 34; civil CSVs.]

Schedule 5 specifies records for **17 item codes**, rather than requiring the same document for every item:

| Prefix | Files | Record type | Item codes specified by Schedule 5 |
|---|---:|---|---|
| `DX` | 266 | Daily excavation record | `A.12.030`, `A.12.040` |
| `CT` | 381 | Compaction test certificate | `A.14.010`, `D.41.010`, `D.41.040` |
| `PR` | 365 | Concrete pour record | `B.21.020`, `B.21.030`, `B.21.040` |
| `PT` | 270 | Pressure test certificate | `C.31.020`, `C.32.030` |
| `MO` | 142 | Meteorological record | `E.51.010` |
| `DW` | 114 | Dewatering log | `A.16.010` |
| `CV` | 120 | CCTV survey report | `C.35.010` |
| `PS` | 143 | Plant standing record | `E.51.030` |
| `JS` | 368 | Joint survey sheet | `B.23.010`, `B.23.020`, `E.52.010` |

Records contain a ticket, project, area, date or week, narrative quantity, and two signature fields; some also state ground classification. Weekly logs list individual days worked. The words and units in narratives vary, such as “cube” for cubic metres. Clause 47A expressly permits ordinary site wording. [CW pp.27, 33; all nine `civilwork/records/` families.]

**Drilling services.** Northgate Petroleum Operating Company engages Meridian Downhole Services Ltd. Each invoice concerns one well and a period of service. The files contain **214 wells**, four fields, three well classes, and five hole-section sizes. Headers and lines join on `invoice_no`. The line's `report_ref` joins to the internal `Report:` identifier, **not directly to the filename**: `DDR-011-20260225` is inside `DDR_NGP-BD-011_20260225.txt`. The report also identifies the full well, rig and date. [DDS pp.1, 3, 8, 35; drilling CSVs and records.]

The daily report combines the evidence into parts:

| Part | Evidence and charge connection | Files containing it |
|---|---|---:|
| A | Daily status, section, depths, hours, tools, crew and event counts | 8,151 |
| B | Run number, first/last day, tools, run hours, logged/reamed metres and source status; required for motor redress and specified logging/reaming charges | 8,151 |
| C | Gyro surveys; required for `DD-130` | 479 |
| D | Source handling and certification; required for `LW-420` | 367 |
| E | Lost tool, run and accumulated hours; required for `LH-711` to `LH-714` | 54 |

Schedule 5 explicitly says there are **no separate run, survey, source or loss documents**, overriding the earlier separate-document description. An inapplicable part may be absent; an applicable required part may not. Run information repeats across daily reports and is not a fresh chargeable event on each appearance. The corpus contains 1,369 distinct well/run pairs and no duplicate well/date report pairs. [DDS pp.5, 24; complete report inventory.]

## 4. Required audit checks

Both [civil guidelines][cg] and [drilling guidelines][dg] prescribe these checks in this order:

1. Confirm the contract reference, issuer and billing period.
2. Confirm the contract was active on the work/service dates, including extensions.
3. Check the submission window and whether the billed period had ended.
4. Check the required evidence for the day/run and required signatures.
5. Check quantities against evidence, applying contractual exceptions and tolerances.
6. Identify the priced item; leave genuine competing matches unresolved.
7. Apply the rate in force for the work date, considering instruments in issue order.
8. Apply adjustments, discounts and rounding in contractual order.
9. Enforce caps, exclusions, minimums and once-only conditions.
10. Check duplicate charging within and across invoices.
11. Reconcile line amounts and totals, including contractual additions/deductions.
12. Record pass, query or part-reject, the clause, payable figure and unresolved information.

Three principles accompany them: work date matters; records are evidence; an unpriceable invoice is a query rather than an invitation to invent a figure. Important qualifications include CW's 2% survey tolerance, DDS's 1% metre tolerance, and retroactive-amendment protections. The generic quantity and date rules cannot override these clauses. [CW p.32; DDS p.35.]

## 5. Page-referenced map of the scanned contracts

### Civil contract: CW-2025-0417-CIV

| PDF page(s) | Contents and relevance |
|---|---|
| 1 | Agreement, parties, original dates, SAR, retention and working week |
| 2 | Contents; not a complete guide to later inserted conditions |
| 3-5 | General Conditions 1-24: precedence, zones/ground, working hours, instructions, records, standing time and traffic management |
| 6-7 | Clauses 25-39: units, rate build-up, rounding, original cumulative rule, daily caps, exclusions and surveys |
| 8-9 | Clauses 40-52: application window, arithmetic, duplicates, retention, records, payment and original release provisions |
| 10-11 | Specification S1-S20: measurement qualifications, tests, included costs and weather standby |
| 12-14 | Particular Conditions P1-P25: concurrent uplifts, trench bands, attendance limits, traffic-management exclusion and missing-record consequences |
| 15-16 | HSE H1-H15; safety suspension does not establish standby entitlement |
| 17-19 | Schedule 1: 60 BoQ codes across earthworks, concrete, drainage, pavements and ancillary work |
| 20 | Schedule 2: zone factors and the five work areas |
| 21 | Schedule 2A: indexed items and monthly Site Materials Index |
| 22 | Schedule 2B: three USD-priced items and monthly exchange table |
| 23 | Schedule 3: ground factors and eligible item list |
| 24-26 | Schedule 4: night/rest-day uplifts, replacement annual quantity bands, daily caps, exclusion and surveyed items |
| 27 | Schedule 5: required record types/references and five-day weekly condition |
| 28-29 | Schedule 6: daywork labour/plant rates and percentage additions |
| 30 | Schedule 7: provisional and prime-cost sums, subject to instruction |
| 31 | Schedule 8: fixed/time-related preliminaries and exclusions from factors/uplifts |
| 32-33 | Second-series conditions: contract years, chargeable hours, currency/index rounding, uplift/ground exceptions, retroactive adjustment, survey tolerance, retention release and record wording |
| 34 | Appendix A: definitions, including work area, rest day and valuation |
| 35 | Execution page |
| 36 | Appendix B: illustrative payment application |
| 37 | Appendix C: insurance and notices |
| 38 | Variation register and consolidated extended term |
| 39 | Supplement 1: substituted rates and monthly binder-course rate |
| 40 | Amendment 1: first extension; separate effective dates for rate changes |
| 41 | Supplement 2: binder-course replacement and 5% discount |
| 42 | Amendment 2: second extension, monthly haul-road rate and 8% discount |
| 43 | Amendment 3: retrospective manhole/fill rates and catch-up adjustment |

### Drilling contract: DDS-2025-118

| PDF page(s) | Contents and relevance |
|---|---|
| 1 | Agreement, parties, original term, USD, VAT, rounding and invoice window |
| 2 | Contents; does not enumerate all later material |
| 3-4 | Clauses 1-14: precedence, call-off, well class, term and suspension |
| 5 | Clauses 15-16: daily report and original description of separate records |
| 6-7 | Clauses 17-31: pricing order, rounding, standby, hours, depth, counts, run/well events, duplicates and lost tools |
| 8 | Clauses 32-42: invoices, evidence, volume discount, VAT and total |
| 9-10 | Technical requirements T1-T16: surveys, tools, source handling and delivery |
| 11-12 | Particular Conditions P1-P14: well classes, standby, minimums, discounts, no night/holiday uplifts and USD payment |
| 13 | HSE H1-H12 |
| 14 | Reporting R1-R12: report timing, corrections, hours and run records |
| 15-16 | Schedule 1: service codes, units and base rates |
| 17 | Schedule 2: four depth bands and contract-year footage bands |
| 18 | Schedule 2C: two indexed services and monthly Rig Services Index |
| 19 | Schedule 2D: SAR replacement values and monthly exchange rates |
| 20-22 | Schedule 3: section/class factors, standby rules, daily caps, once-per-well list and minimum hours |
| 23 | Schedule 4: normal staffing; actual recorded counts govern |
| 24 | Schedule 5: integrated daily report parts A-E and evidence requirements |
| 25 | Schedule 6: original USD replacement values; read with p.35 override |
| 26 | Schedule 7: tool specifications; actual daily presence governs charging |
| 27-28 | Schedule 8: service scope and charge events, including wording conflicts requiring review |
| 29 | Appendix A: definitions, including performance-drilled sections |
| 30 | Appendix B: illustrative invoice |
| 31 | Appendix C: insurance, notices and execution |
| 32-34 | Appendices D-F: illustrative daily, run, survey and loss record forms |
| 35 | Second-series conditions: years, indexation, factor exceptions, field wording, chargeable hours, metre tolerance, replacement conversion and retrospective adjustment |
| 36 | Appendix G: explicit mapping between field terminology and priced codes |
| 37 | Variation register and consolidated extended term |
| 38 | Supplement 1: steerable rates and monthly circulating-sub rates |
| 39 | Amendment 1: first extension and personnel rates |
| 40 | Supplement 2: monthly steerable rates and 4% service discount |
| 41 | Amendment 2: second extension, replacement rates and 7% discount |
| 42 | Amendment 3: retrospective steerable/personnel rates and catch-up adjustment |

## 6. Amendment and effective-date structure

Each contract contains two supplements and three amendments. **Issue date, instrument effective date, individual rate effective date, work date and invoice submission date have distinct roles.**

### Civil works

Original term: **5 January-27 September 2025**. Final extended completion: **30 September 2026**. [CW pp.1, 38, 40, 42.]

| Instrument / page | Issued | Effective | Material change |
|---|---|---|---|
| S1 / 39 | 2025-03-24 | 2025-05-01 | `B.23.010` 4,385.00; `B.21.020` 431.50; `A.16.010` 1,524.00. Monthly `D.41.020` rates May-September: 214.50, 219.80, 226.40, 223.10, 220.50. |
| A1 / 40 | 2025-08-18 | 2025-09-28 | Extends completion to 2026-03-31. **Rate rows start 2025-10-01:** `E.54.010` 948.00 and `B.23.010` 4,450.00. |
| S2 / 41 | 2025-11-12 | 2025-12-01 | `D.41.020` 228.00; 5% discount on `C.32.030`, `C.32.010`, `D.41.020`, `B.23.010`. |
| A2 / 42 | 2026-02-16 | 2026-04-01 | Extends completion to 2026-09-30; discount becomes 8% on the same four codes. `E.54.010` April-September: 976, 991, 1,013, 1,038, 1,038, 1,052. |
| A3 / 43 | 2026-05-12 | **2025-11-01** | Retrospective rates: `C.32.010` 1,984.00 and `A.14.010` 56.80. Difference on previously certified work belongs in one later adjustment. |

Amounts above are rate-table values in SAR, before applicable build-up. Monthly replacement-rate tables explicitly carry their last published rate forward until superseded. They are distinct from the index multipliers in Schedule 2A.

### Drilling services

Original term: **1 January-31 December 2025**. Final extended expiry: **31 December 2026**. [DDS pp.1, 37, 39, 41.]

| Instrument / page | Issued | Effective | Material change |
|---|---|---|---|
| S1 / 38 | 2025-05-19 | 2025-07-01 | `DD-120` 398.50; `DD-121` 2,984.00. Monthly `HC-601` July-December: 701.50, 714.00, 722.60, 719.80, 731.00, 736.40. |
| A1 / 39 | 2025-11-07 | 2026-01-01 | Extends expiry to 2026-06-30. `DD-101` 1,916.50; `MW-301` 1,708.00; `LW-401` 1,969.00. |
| S2 / 40 | 2026-02-24 | 2026-04-01 | Monthly `DD-120` April-December: 406, 411.50, 411.50, 423, 429.50, 434, 434, 441, 447.50. Introduces 4% rate discount on `DD-101`, `MW-301`, `LW-401`, `DD-120`, `MB-701`. |
| A2 / 41 | 2026-05-21 | 2026-07-01 | Extends expiry to 2026-12-31. `MW-301` 1,763.00; `MB-701` 19,237.00; rate discount becomes 7% on the same five services. |
| A3 / 42 | 2026-08-17 | **2026-02-01** | Retrospective `DD-120` 416.00 and `DD-101` 1,954.00, with one catch-up adjustment. Its interaction with S2's monthly `DD-120` table is material. |

These rates are USD before applicable build-up. The service-rate discounts are separate from the invoice-level `DS-900` discount.

CW clause 31A and DDS clause 36A protect invoices submitted before a retrospective instrument's issue: they are not wrong merely because a later rate applies retrospectively. The difference is placed on the first submission **on or after** issue. The amendment pages themselves say **after**, creating a boundary wording difference to resolve. The general variation-register statement against reopening earlier work must be read with these specific adjustment provisions. [CW pp.32, 38, 43; DDS pp.35, 37, 42.]

## 7. How source evidence connects to invoice charges

An invoice line supplies the claimed code, quantity, rate and context. Its linked record supplies the evidence of the activity. The contract establishes the chargeable item, evidence requirements, quantity qualifications, rate and timing. Invoice descriptions and rates are claims, not independent proof.

Directly inspected examples illustrate the connection without judging the invoice:

| Invoice-line reference | Supporting file | What the link establishes |
|---|---|---|
| Civil `PA-00668-04` | `civilwork/records/DX-00001.txt` | The ticket describes 210 cubic metres of trench excavation at 3 m depth, S-04, 18 January 2025, G1, with two named signatories. The line claims `A.12.030`; Schedule 1 defines the relevant depth band. |
| Civil `PA-00792-06` | `civilwork/records/DW-00001.txt` | A line dated 2 February 2025 references the week beginning 27 January and six listed days of operation. A weekly record cannot be matched by demanding its heading date equal the line date. |
| Civil `PA-00233-11` | `civilwork/records/JS-00001.txt` | Three chainage bands recorded on a joint survey link to `E.52.010`; survey evidence also brings clause 33A into consideration. |
| Drilling `MDS-01171-001`, `-002`, `-003`, `-004`, `-009` | `drilling_services/records/DDR_NGP-BD-011_20260225.txt` | One daily report supports multiple types of charge: directional crew, coordinator, motor rental, gyro survey and MWD rental. Parts A-C carry the relevant facts. |

The drilling vocabulary is expressly defined, even where it is counterintuitive:

| Field-report term | Contractual code |
|---|---|
| `night man` | `DD-102`, office-based directional coordinator |
| `MWD collar` | `MW-310`; `LH-713` in a loss record |
| `survey package` | `MW-320` |
| `gamma tool` | `LW-410`; `LH-714` in a loss record |
| `resistivity tool` | `LW-411` |
| `density-neutron` | `LW-412` |
| `float sub` | `HC-640` |

Use the complete Appendix G mapping, not ordinary industry meanings or similar invoice descriptions. [DDS pp.35-36.]

Direct reference checks found **2,193 nonblank civil line references**, representing 2,172 distinct ticket IDs. Three IDs have no corresponding record file: `CT-00126`, `MO-00089`, `PS-00039`. All 2,169 supplied civil records are referenced. There are **5,553 blank civil references**; 5,549 occur on codes outside Schedule 5's list, while four occur on listed codes. Thus, a blank reference alone is not a universal missing-evidence conclusion.

All **91,181 nonblank drilling line references** resolve to the 8,151 reports. The remaining **63 rows are `DS-900`**, with blank service date, section, status and report reference. Some supplied signature fields contain underscore placeholders: one civil record and three drilling reports. Field presence does not establish a signature. These are source observations, not invoice classifications. [Both line CSVs and complete record inventory; examples: `civilwork/records/DX-00089.txt`, `drilling_services/records/DDR_NGP-BD-149_20251122.txt`.]

## 8. Submission requirements and evaluation

The eventual deliverables are a runnable repository with pinned dependencies and reproduction instructions; `submission.csv`; a short performance/error-analysis report organized around three or four systematic failure types with examples; versioned AI prompts, including iterations; and a one-page decision log. AI assistance is permitted, expected and must be disclosed. [README, Deliverables and AI assistance.]

| Submission column | Source requirement |
|---|---|
| `invoice_id` | Preserve the template's IDs and cover all 2,806 rows |
| `flagged` | `1` means wrong; `0` means audited and considered correct |
| `error_category` | Consistent short free-text category; blank when not flagged |
| `expected_total_cents` | Contract-supported total in integer minor units |
| `billed_total_cents` | Actual billed total in integer minor units |
| `confidence` | Confidence between 0 and 1 |

**The specified target is `application_total` for civil works and `invoice_total` for drilling.** It is not civil `net_payable` or drilling `net_amount`. Multiply CSV currency amounts by 100: civil outputs are SAR halalas; drilling outputs are USD cents, despite the shared column suffix. Do not convert the two datasets into one reporting currency. Unpriceable invoices still require rows and transparent discussion of what could not be established. [README, Data and Task; `submission_template.csv`.]

CW's BoQ states VAT-exclusive rates, but its application data have no VAT field. DDS explicitly specifies 15% VAT and supplies `vat_amount`; that provision must not be imported into the civil dataset. [CW p.17; DDS pp.1, 8; both header schemas.]

Scoring covers precision, recall and F1 overall/by severity; **cost = 5 × false negatives + false positives**; expected-amount correctness for flagged invoices; confidence calibration; and category consistency. The repository provides no public labels or scoring implementation. It does not specify severity boundaries, numeric amount tolerances, an encoding for genuinely unknown expected totals, a submission deadline, or a submission channel. None should be invented. [README and verified file inventory.]

## 9. Important contractual and data facts for later work

### Civil works

- **Rate build-up and rounding:** zone, eligible ground factor, applicable night/rest-day uplifts, quantity band, then effective principal-item discount before final rate rounding. Clause 28 uses half-up rounding once after build-up; clauses 26A/29A require an earlier half-even rounding step for currency conversion/indexation. Retention is 5% of the application valuation, rounded down. [CW pp.6, 8, 32, 41-42.]
- **Factor eligibility:** zone factors are 1, 1.06, 1.145 and 1.28 for Z1-Z4, applied to series A-D, not E. Ground factors are 0.94, 1, 1.12, 1.375 and 1.63 for G1-G5, restricted to the listed codes. After **27 September 2025**, clause 27A substitutes G2 regardless of the recorded class; it also suppresses night uplift where the applicable zone factor exceeds 1.1. [CW pp.20, 23, 32.]
- **Calendar and quantity qualifications:** rest days are Friday/Saturday. Concurrent night/rest-day uplifts require written instruction; otherwise the rest-day uplift alone applies where both are eligible. Chargeable hourly quantity excludes the first hour of attendance. Survey quantities within 2% above evidence remain payable as measured; above that, the surveyed quantity governs. A recorded week needs at least five worked days. [CW pp.3, 13, 24, 32-33.]
- **History matters:** Schedule 4 replaces the original lifetime rebate with three-band quantities for eight codes, resetting by Contract Year. The anniversary is 5 January; an extension itself does not reset the year. Daily caps apply per item/work area/day. `A.14.020` is excluded for two days following `A.14.010` in the same area; specified surfacing/marking work also excludes same-day traffic management. [CW pp.6, 13, 24-26, 32.]
- **Rates labelled SAR are not universally SAR:** Schedule 2B identifies `B.23.020`, `B.25.010` and `C.32.040` as USD rates. Its exchange table is in **halalas per USD**. Schedule 2A indexes `C.31.010` and `D.41.030` separately. [CW pp.21-22, 32.]
- **Totals and submission:** application submission is not before its period's last day and is within 21 days of period end. Clause 45A releases half of earlier retention on the first application after extended completion. Its payment formula distinguishes measured total, retrospective adjustment, current retention and retention release. [CW pp.8, 32.]

### Drilling services

- **Rounding differs from civil works:** each rate build-up step is rounded half-even to cents. Indexing applies to `MW-310` and `HC-620`. Section/class factors apply only to specified services; clause 17B removes section factors on Standby and the class factor from `PD-210`. [DDS pp.6, 18, 20, 35.]
- **Depth and annual bands are distinct:** PD-210 splits at 1,500, 3,000 and 4,500 m, with rates 42.35, 58.15, 76.45 and 98.70. Schedule 2 separately describes annual footage bands at 40,000 and 120,000 metres **on the well**. Contract years follow the 1 January anniversary. [DDS pp.17, 35.]
- **Actual operating evidence governs:** tools must be present, personnel/counts supported, standby eligibility respected, and daily caps enforced. DD-120 has a six-hour operating-day minimum; DD-121 replaces it on Standby. Clause 21A excludes a rig-up hour; clause 25A permits metre quantities within 1% above the supporting record. [DDS pp.6-7, 20-24, 35.]
- **Charge timing matters:** motor redress is once per qualifying run on its last day; source handling is once per qualifying run on its first day. Mobilisation/planning are first-day well charges; demobilisation/final LWD processing are last-day charges, with LWD processing conditional on LWD use. Split depth intervals are an explicit exception to same-service/day duplicate restrictions. [DDS p.7.]
- **Lost tools:** use Schedule 2D's SAR replacement values, converted at the loss month's published exchange rate and rounded half-even before depreciation. Depreciation is 1% per complete 25 accumulated circulating hours on that well, capped at 50%; charge on the loss date. Static USD values in Schedule 6 are overridden. [DDS pp.7, 11, 19, 25, 35.]
- **Two discounts and tax:** effective 4%/7% discounts apply to selected service rates. Separately, `DS-900` is negative 4% of invoice service subtotal exceeding USD 250,000, not 4% of the entire subtotal. VAT is 15% of net. Invoice submission is not before period end and within 30 days afterward. [DDS pp.8, 40-41.]

Additional verified data facts affect interpretation:

| Observation from files | Why it matters |
|---|---|
| Civil work dates: 2025-01-07 to 2026-10-26; application dates: 2025-01-23 to 2026-10-31 | The data cross amendments and extend beyond final contractual completion. |
| Drilling service dates: 2025-01-01 to 2027-01-23; invoice dates: 2025-01-07 to 2027-01-25 | Distinguish service expiry from legitimate later invoicing; do not filter synthetic data by today's date. |
| All civil `adjustment`/`retention_released` and drilling `adjustment` values are `0.00` | The columns exist, but zero-filled inputs do not prove these contractual mechanisms are irrelevant. |
| Civil headers contain two `CW-2024-0417-CIV` references; drilling contains two `DSS-2025-118` and one `DDS-2025-181` | Preserve original identifiers when examining contract identity. |
| Invoice-number order is not submission-date order in either header file | First-submission and historical checks need actual dates. |
| Drilling reports: 7,770 Operating days, 381 Standby days; maximum reported end depth 6,026 m | These are recorded operational facts, not evidence that annual bands should be pooled across wells. |

## 10. Material matters requiring closer examination

1. **Explicit overrides versus residual conflicts.** The second-series clauses and revised schedules materially qualify early rules. Separately, DDS Schedule 8 calls `DD-102` office staffing in its introduction but describes tool presence in its row; it calls `HC-630` a BHA-run charge while clause 30 uses recorded clean-out counts. Its generic hour/metre wording also needs comparison with service-specific clauses. [DDS pp.6-7, 27-28, 35.]
2. **Retrospective amendment precedence and placement.** Resolve DDS A3's 416.00 DD-120 rate against S2's monthly rates using issue order, not effective-date sorting alone. Establish the catch-up population, affected discounts/tax, first eligible invoice, same-day ties, and the “after”/“on or after” boundary. Earlier submissions must not be retrospectively treated as wrong merely for using then-current rates. [CW pp.32, 43; DDS pp.35, 40, 42.]
3. **Financial outcome versus the scored total.** Establish how nonzero adjustments and retention findings should be reported while preserving the README's `application_total` target. The data's financial columns and clause 45A distinguish gross valuation from cash payable. Also distinguish a procedural payment hold/query from a contractually zero-valued charge. [README, Data; CW pp.8, 14, 32; DDS pp.8, 35.]
4. **Boundaries and scope.** Confirm how the first-hour rule interacts with DDS's daily minimum and “period in the hole”; how tolerances interact with caps/depth splits; annual quantity ordering; exclusion-window endpoints; and the per-well scope of annual footage bands. Do not silently adopt campaign-wide aggregation or a new reset on extension. [CW pp.6, 24-26, 32; DDS pp.6, 17, 22, 35.]
5. **Evidence availability and adequacy.** Missing ticket files, blank references on record-required codes, nonmatching record families, placeholder signatures, and required report parts need charge-level examination. A valid reference alone does not establish matching date, activity or quantity. The inventory has no separate call-offs, written uplift instructions, permits or taking-over certificates; determine what can be established from the supplied evidence without treating every unprovided background document as an invoice defect. [CW pp.3-4, 15, 27; DDS pp.3, 24; record inventory.]
6. **Source-document inconsistencies.** Contents lists omit later sections; amendment introductions reference clauses not present under those numbers, such as CW 26.4/14.2 and DDS 19.3. Illustrative forms must be checked against later indexation and chargeable-hour clauses, rather than accepted as universal worked answers. Later discount instruments also use “before that date carries no discount” while preserving earlier instruments for earlier periods. Record reasoned readings without erasing the earlier 5%/4% regimes. [CW pp.2, 32, 36, 39-42; DDS pp.2, 30, 35, 38-41.]

## 11. What the next phase must establish before implementation

The next phase should establish a verified, page-referenced interpretation of the applicable terms, resolve or explicitly log the material conflicts above, and define the evidence required to support each charge family. It must settle the distinct time/order rules, rounding stages, quantity qualifications, amendment interactions and total-field meanings before those interpretations are encoded.

It must also establish how pass/query/part-reject decisions will relate to the binary submission, how genuinely unresolved amounts and confidence will be communicated, and how contractual correctness will be checked without public labels. The README's stated prevalence cannot substitute for evidence or serve as a target number of flags. This report does not select an architecture, model, extraction method or full technical approach.

## 12. Approximate time spent

Approximately **14 minutes elapsed**, covering repository retrieval, contract OCR and visual review, dataset/reference profiling, report drafting and final checks. This is the time spent on this understanding phase, not an estimate for implementing or completing the challenge.

Phase 1 ends with this report.

[readme]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/README.md
[cw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/contract/CW-2025-0417-CIV.pdf
[dds]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/contract/DDS-2025-118.pdf
[cg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md
[dg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/guidelines/INVOICE_AUDIT_GUIDELINES.md
