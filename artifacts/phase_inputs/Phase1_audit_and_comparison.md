# Phase 1 — Independent audit and comparison (Agent 2)

**Current judgment: Agent 1A is currently the stronger solving agent for this understanding phase.** Both reports demonstrate substantial source understanding. 1A is the safer primary foundation because it more consistently separates contractual requirements, observations and unresolved interpretations. 1B contributes useful, more detailed extraction, but several conclusions need correction before they guide later decisions.

**Source snapshot:** repository commit [`aef4924dc32506b4587de8b788b5a947e6beffec`][repo], also identified by both reports. Reviewed inputs were the supplied Agent 1A and Agent 1B Markdown reports. Their section numbers below identify the statements being assessed. PDF page references are one-based and match the printed page numbers. All repository links are pinned to this commit.

**Independence and scope.** I inspected the README, both guidelines, all 85 contract pages, the CSV structures and joins, the complete supporting-record inventory, and representative records from every civil family and drilling report part before opening either report. I established an independent baseline first, then checked each report against the sources. Subsequent checks tested particular report claims. I did not implement a solution, classify invoices, compute corrected invoice totals, or create a submission. Reported rate-reproduction percentages in 1B were not rerun: doing so would require work beyond this understanding audit.

## 1. Independent understanding of the challenge

The task is to audit every invoice under two amended contracts using scanned contractual terms and free-text operational evidence. Arithmetic is only one check. The contract determines entitlement, item identification, evidence requirements, quantities, applicable rates, adjustments and timing. The guidelines prescribe twelve checks, but explicit contractual exceptions govern. Unresolved identification or missing information must be acknowledged rather than priced by guesswork. [README, Task and Ground rules][readme]; [civil guidelines][cg]; [drilling guidelines][dg].

| Verified population | Civil works | Directional drilling |
|---|---:|---:|
| Contract pages | 43 | 42 |
| Invoice headers | 900 | 1,906 |
| Invoice lines | 7,746 | 91,244 |
| Supporting text records | 2,169 | 8,151 |
| Currency | SAR | USD |
| Judged total | `application_total` | `invoice_total` |
| Final contractual completion/expiry | 30 September 2026 | 31 December 2026 |
| Submission window after period end | 21 days | 30 days |

The counts and total fields are confirmed by the [README][readme] and input CSVs. Terms and windows come from [CW pp.8, 38–42][cw] and [DDS pp.8, 37–41][dds]. Submission date and work date have different functions; later invoicing is not itself post-expiry service.

Lines join to headers by `application_no` or `invoice_no`. Every line has a header, every header has lines, and the template contains exactly their 2,806 unique IDs. Civil tickets use `record_ref`; drilling uses the internal `Report:` identifier, whose format differs from its filename. A report may support several services and contain repeated run information. Neither a shared reference nor a syntactically valid join proves duplication or entitlement. [Civil lines][cl]; [drilling lines][dl]; [template][template]; [example DDR][ddr-example]; [DDS pp.7, 24, 35][dds].

The most consequential contractual distinctions are:

- **Later provisions matter.** CW pp.32–33 and DDS p.35 add material exceptions absent from the early clauses and incomplete contents pages. Examples include chargeable hours, quantity tolerances, currency/index rounding, factor exclusions and retrospective adjustments. [CW pp.32–33][cw]; [DDS p.35][dds].
- **Amendments have several relevant dates.** Each contract has two supplements and three amendments. CW A1 extends the term from 28 September 2025, while its rate rows start 1 October. CW A3 was issued 12 May 2026 with effect from 1 November 2025; DDS A3 was issued 17 August 2026 with effect from 1 February 2026. Earlier submissions are protected against being deemed wrong merely because rates later change retrospectively; the difference belongs in one later adjustment. The adjustment boundary differs between the second-series clauses and amendment wording: “on or after” versus “after.” [CW pp.32, 39–43][cw]; [DDS pp.35, 38–42][dds].
- **The domains price differently.** Civil rate build-up ends with half-up rounding, with earlier half-even conversion/indexing where specified; retention rounds down. Drilling rounds half-even at each step, has selected-service discounts distinct from `DS-900`, and adds 15% VAT. Annual quantity bands, daily caps, exclusions and run/well events require the correct scope and chronology. [CW pp.6, 8, 21–26, 32, 41–42][cw]; [DDS pp.6–8, 17–22, 35, 40–41][dds].
- **Evidence is conditional and semantic.** Civil Schedule 5 specifies records for 17 codes; blank references elsewhere are not automatically defects. DDS Schedule 5 combines evidence into daily-report parts, expressly dispensing with separate run/survey/source/loss documents. Appendix G defines sometimes counterintuitive vocabulary mappings. Quantity tolerances and the first-hour rules qualify a literal comparison with the recorded quantity. [CW pp.27, 32–33][cw]; [DDS pp.24, 35–36][dds].

The eventual deliverables are a reproducible repository with pinned dependencies, the six-column submission, a short report organized around three or four systematic failure types, versioned prompts, and a one-page decision log. AI assistance must be disclosed. Amounts use integer native-currency minor units: civil halalas and drilling cents. All rows remain required, including uncertain cases. The repository states 5–8% incorrect invoices and provides no labels; it does not prescribe a candidate-finding quota, severity boundaries, or an encoding for genuinely unknown expected totals. [README, Data, Task, Scoring, AI assistance and Deliverables][readme]; [template][template].

## 2. Audit of Agent 1A

**Assessment: accurate and substantially complete for an understanding report; safe as the primary foundation with the specific additions below.** I found no material incorrect transcription in its principal amendment tables, date distinctions, dataset inventory or central contract interpretations. This is not certification of a future solution or an assertion that every possible charge has been resolved.

### Important points it got right

- **Contract-page understanding:** its page maps cover both complete PDFs, including the second-series conditions, added schedules, glossary and instruments. It identifies the substantive effect of those pages, including DDS's integrated evidence, PD-210 factor exception, and SAR-based loss valuation overriding the static USD table. [1A §§5, 9; CW pp.32–33][cw]; [DDS pp.24, 35–36][dds].
- **Amendments:** it separates issue, instrument-effective, item-effective, work and submission dates. It correctly preserves pre-issue invoice protection, the single-adjustment mechanism, CW A1's separate rate date, and the interaction of DDS A3 with S2's monthly rates. It leaves genuine placement and boundary questions visible. [1A §§6, 10; CW pp.32, 38–43][cw]; [DDS pp.35, 37–42][dds].
- **Guidelines and evidence:** it captures all twelve checks and the contract's exceptions. It distinguishes missing evidence from inapplicable evidence, ordinary record wording from absent item codes, and placeholder signature fields from actual signatures. Its reference counts and the three missing civil ticket IDs agree with the files. [1A §§3–4, 7; civil guidelines][cg]; [CW pp.27, 33][cw]; [civil lines][cl]; [signature example][cw-signature].
- **Joins and supporting records:** it correctly distinguishes work area from zone, drilling report ID from filename, and repeated run information from a new event. It explains record-to-charge relationships without treating invoice descriptions or rates as independent proof. [1A §§3, 7; CW pp.20, 34][cw]; [DDS pp.7, 24, 36][dds]; [example DDR][ddr-example].
- **Deliverables and financial semantics:** it identifies the exact judged totals, native currencies, AI disclosure, all five deliverables, and the distinction between civil gross valuation and cash payable. It does not silently invent a severity scheme or unknown-amount encoding. [1A §8; README][readme]; [CW pp.8, 32][cw].
- **Interpretive discipline:** it states the per-well scope of DDS annual footage bands and explicitly rejects using the stated prevalence as a target number of flags. It separates explicit replacements from residual Schedule 8 conflicts. [1A §§9–11; DDS pp.17, 27–28, 35][dds]; [README, calibration guidance and Ground rules][readme].

### Material omissions and corrections

| Finding | Report location and evidence | Why it matters / correction |
|---|---|---|
| **A1 — Unit rejection consequence is not made explicit.** This is an omission, not a contrary assertion. | 1A's page map mentions units, but its substantive rule summary does not state the consequence. [CW p.6, clause 26][cw] requires a quantity in a non-scheduled unit to be rejected in full rather than converted. | A next-phase reader should not infer that normalization or unit conversion is an acceptable remedy. Add this explicit rule. 1B covers it better. |
| **A2 — Civil duplicate allocation is summarized too generally.** | 1A covers cross-invoice duplicate checks but does not spell out clause 44's same-item/work-area/date condition and full disallowance of the later measurement. [CW p.8, clause 44][cw]. | Add the rule and preserve the need to determine which measurement is later. A generic duplicate warning is insufficient to decide where an eventual correction belongs. |

These are bounded handoff gaps. The absence of a complete numeric transcription is not itself a material failure at this phase: 1A supplies the page map and important qualifications. Its report should still be used alongside the contract, rather than treated as an exhaustive replacement for it.

**Unsupported claims / interpretations as fact:** no comparably consequential unsupported conclusion was established in 1A. Its unresolved matters are generally presented as unresolved. In particular, leaving the first-hour/minimum interaction, adjustment placement and unavailable background-document questions open is appropriate, not an error. [CW pp.3, 27, 32][cw]; [DDS pp.6, 22, 24, 35][dds].

## 3. Audit of Agent 1B

**Assessment: strong extraction and coverage, but not safe to adopt unchanged.** Its principal rates, amendment dates, factor distinctions, currencies and submission schema agree with the sources. Its detailed appendices are useful. The principal weakness is that a few observations or heuristics become stronger conclusions than the evidence supports.

### Important points it got right

- **Detailed contract extraction:** the page maps and numeric appendices capture rate tables, eligible factors, quantity bands, daily limits, index/FX tables and record mappings. They explicitly state civil wrong-unit rejection and the later-measurement consequence. These are substantive additions beyond 1A's summary. [1B §§5, 9 and appendices; CW pp.6, 8, 17–27][cw]; [DDS pp.15–25][dds].
- **Dates and amendments:** it correctly records CW A1's separate item dates, both final extensions, both retrospective amendments, changing discount percentages, and the distinction between service-rate discounts and `DS-900`. It also identifies the adjustment-date wording discrepancy. [1B §6 and §10.1–2; CW pp.39–43][cw]; [DDS pp.38–42][dds].
- **Guidelines and records:** its check-to-clause table is useful. It identifies survey/metre tolerances, first-hour deductions, conditional record requirements, integrated drilling evidence, signature roles and glossary conflicts. [1B §§3–4, 7; CW pp.8, 27, 32–33][cw]; [DDS pp.5, 24, 35–36][dds].
- **Dataset understanding:** its header/line joins, date formats, population counts, record families, report-part counts and missing-reference observations agree with the source structure. Its more granular observations provide useful questions for later examination. [1B §§2, 7; civil lines][cl]; [drilling lines][dl]; [civil records][cr]; [drilling records][dr].
- **Uncertainty recognition:** it identifies real Schedule 8 wording problems, adjustment-versus-total semantics, undefined severity, and the need for exact rounding. Its broader list of potential issues is valuable when treated as a review list. [1B §10; CW pp.8, 32][cw]; [DDS pp.6–7, 27–28, 35][dds]; [README][readme].

### Material errors, omissions and unsupported interpretations

**B1 — Date/reference mismatches are overgeneralized into duplicates. High priority.**

In §10.7, 1B includes the eight drilling lines citing another day's DDR in its duplicate explanation. That conclusion exceeds its evidence. DDS clause 29 concerns repeated service for the same well and day, with a specific exception for PD-210 depth intervals; a disagreement between service date and report date establishes a mismatch, not a second charge. [DDS p.7, clause 29; p.35, clause 19A][dds].

I checked the eight cited lines by service code and report reference: only two share that combination with another line; six appear once. For example, `MDS-00164-050` is the sole PD-201 line citing `DDR-107-20250305`, despite the differing service date. This is a structural counterexample to treating all eight mismatches as demonstrated duplicate events; it is not an invoice classification. [Drilling lines, `MDS-00164-050`, CSV line 7,758][dl-example]; [corresponding DDR][ddr-mismatch].

The same paragraph also treats reuse of weekly DW logs as automatically covered by full later-measurement rejection. Reuse warrants examination, but the explicit same-date test and the weekly evidence/quantity rules must be reconciled before extending that consequence across different dates. [CW p.8, clause 44; pp.27, 33, weekly-record provisions][cw]. Correct the report to distinguish evidence reuse, date mismatch and proven duplicate charging.

**B2 — The 5–8% statement is turned into a candidate-finding target. High priority.**

Section 11.7 says the union of candidate findings should land near 5–8%, and that a much larger count means a reading is repricing correct invoices. The README's percentage concerns actually wrong invoices, not every preliminary suspicion. A candidate set can be larger without demonstrating an incorrect interpretation. The README encourages calibration and warns that unusual invoices may be correct; it does not supply a quota or make this diagnostic conclusive. [README, What you have, Task and Ground rules][readme].

Use prevalence as a reason to investigate surprising results, not as an acceptance condition or reason to suppress supported findings. Similarly, §11.1's billed-rate reproduction thresholds are proposed diagnostics, not source-defined correctness gates. **Calibration itself is appropriate and expressly encouraged by the README**; the problem is the stronger target/gate language, not checking rates against billing.

**B3 — An explicit per-well scope is described as an unresolved contract-wide alternative. Medium priority.**

Section 10.4 says the annual PD-210 tier can be read per well or contract-wide, then prefers per well because that agrees with billing. Schedule 2 Part 2 explicitly scopes accumulated metres to the well within the Contract Year. The contract therefore supplies the principal reason for the per-well reading. [DDS p.17, Schedule 2 Part 2][dds].

1B reaches the supported provisional result, but invents more scope ambiguity than this passage warrants. Preserve any genuine questions about qualifying metres or boundaries; do not use observed non-application to decide between scopes that the text already distinguishes. 1A preserves this distinction better.

**B4 — The drilling duplicate exception is omitted from the operative summary. Medium priority.**

Sections 4 and 5.2 summarize clause 29 as prohibiting repeated service on a well-day without explicitly preserving PD-210's different-depth-interval exception. Elsewhere, 1B correctly describes depth-band splitting, so it has not missed depth pricing altogether. The omission is still consequential when handing off a duplicate rule. [DDS p.7, clause 29, referring to clause 23 on p.6][dds]. Add the exception directly to that rule. 1A expressly includes it in §9.

**B5 — AI disclosure is missing from the deliverable summary. Lower priority.**

Sections 1 and 8 list versioned prompts and the five deliverables, but do not explicitly state that AI assistance must be disclosed. Prompt versioning is required, but it does not erase the separate disclosure requirement. [README, AI assistance][readme]. Add the requirement; 1A already states it.

**Claims that remain unverified rather than disproved.** 1B reports 99.5% civil rate reproduction and 97.5% drilling reproduction, with explanations for residuals. The supplied reports do not include the harness or outputs needed to independently validate those figures without rebuilding pricing logic. They are self-reported reconciliation results, not demonstrated detection accuracy on a labelled set. The README explicitly provides no labels. I do not treat those figures as fabricated, as proven errors, or as evidence that 1B will outperform 1A. [1B opening and §9; README, What you have and Scoring][readme].

Its suggested probability threshold also needs a qualification: the stated 5:1 false-negative/false-positive cost supports that derivation when minimizing that binary expected cost with reliable probabilities. It is not an organizer-mandated threshold or a complete treatment of all scoring dimensions. Likewise, any proposed severity scheme remains an internal convention because the source does not define severity. [1B §§8, 10.12, 11.6; README, Scoring][readme]. These qualifications are secondary to B1–B4.

## 4. Direct comparison

| Assessment area | Agent 1A | Agent 1B | Relative assessment |
|---|---|---|---|
| Accuracy of central terms | Accurate on checked material facts and distinctions | Accurate on most terms; consequential duplicate overreach | 1A |
| Completeness | Broad coverage with two explicit-rule gaps | More detailed numeric extraction and check-to-clause mapping | 1B for extraction detail |
| Contract-page understanding | Complete maps; distinguishes explicit overrides and residual conflicts | Complete maps and useful tables; some clear wording unnecessarily reopened | Both strong; 1A better on interpretation |
| Amendments and effective dates | Correct distinctions and clear pre-issue protection | Correct dates; more concrete timing observations | Approximately equal |
| Audit guidelines | All twelve checks and contractual qualifications | All twelve, mapped to clauses | Approximately equal |
| Dataset and joins | Accurate, clearly separates claims and evidence | Accurate, with additional structural observations | Approximately equal; 1B more granular |
| Supporting records | Preserves applicability, signatures and repeated-event distinctions | Strong parsing understanding; duplicate inference needs correction | 1A |
| Submission and deliverables | Exact total fields, currencies, disclosure and unknowns | Main requirements correct; explicit disclosure omitted | 1A, modestly |
| Unsupported claims and uncertainty | Generally careful and bounded | Some observations promoted into rules; reproduction claims not independently established | 1A |
| Safe foundation for next phase | Yes, with A1–A2 added | Yes after B1–B5 are corrected; useful extraction companion meanwhile | 1A |

These assessments rest on the source-linked findings above. Extra length, more confident wording, and the agents' self-reported time expenditure receive no independent credit. Nor does lack of a full rate appendix make 1A incomplete for this phase.

## 5. Current judgment and the evidence behind it

**Selected conclusion: Agent 1A is currently the stronger solving agent.** This is a bounded judgment about the supplied understanding reports, not a prediction of final implementation quality.

The decisive evidence is the handling of distinctions that could propagate into many later decisions: a mismatched record is not automatically a duplicate; explicit per-well wording should control scope; and the stated error prevalence should not become a target for candidate findings. 1A preserves these distinctions more reliably. It also expressly separates the scored civil total from cash payable and preserves important protections around retrospective rates. [1A §§7–11; DDS pp.7, 17, 35][dds]; [CW p.32][cw]; [README][readme].

1B is stronger in detailed extraction and in making some civil consequences explicit. Its appendices and clause mapping remain valuable after checking and correction. However, the two omissions in 1A are local additions; the problems in 1B include inference rules that could affect how future evidence is judged. That difference supports a modest but meaningful preference for 1A. It does not justify dismissing 1B or claiming proven performance superiority.

## 6. Corrections to carry into the next phase

1. **Make civil unit and duplicate consequences explicit:** wrong scheduled unit means full rejection rather than conversion; clause 44 identifies the later duplicate measurement for full disallowance. [CW pp.6, 8][cw].
2. **Separate mismatch, reuse and duplication.** Check the relevant event, quantity, day/run/week and prior charge before asserting a duplicate; preserve PD-210's depth-interval exception. [CW pp.8, 27, 33][cw]; [DDS pp.7, 24][dds].
3. **Use explicit scope and precedence first.** DDS annual footage bands are per well and Contract Year. Preserve the January anniversaries, factor eligibility, second-series exceptions, and amendment issue order. Billing patterns can help check a reading but cannot replace those terms. [CW pp.24–26, 32, 38][cw]; [DDS pp.17, 35, 37][dds].
4. **Keep retrospective protections and genuine unknowns separate.** Pre-issue submissions are protected from retrospective-rate fault; adjustment boundaries, same-day ordering and placement against the judged total still require a recorded interpretation. DDS A3's interaction with S2 must be read in issue order. [CW pp.32, 43][cw]; [DDS pp.35, 40, 42][dds].
5. **Preserve financial distinctions.** Civil gross valuation, retention, release and cash payable differ. Drilling service discounts, invoice discount, net and VAT differ. Use the README's specified total and native-currency minor units. [CW pp.8, 32][cw]; [DDS pp.8, 40–41][dds]; [README, Data][readme].
6. **Treat uncertainty honestly.** Do not equate an unsigned or mismatched record with a valid evidentiary join; do not invent missing background instructions. Retain the unresolved hourly-minimum and Schedule 8 issues where the sources warrant them. [CW pp.3, 8, 27][cw]; [DDS pp.6, 22, 27–28, 35][dds]; [guidelines][dg].
7. **Remove quotas and unsupported performance implications.** The 5–8% statement is contextual evidence; reproduction of billed rates is a diagnostic. Neither establishes invoice correctness or labelled accuracy. [README, What you have, Task and Scoring][readme].
8. **Carry every deliverable requirement forward**, including explicit AI disclosure, versioned prompt iterations and the one-page decision log. Keep undefined severity and unknown-amount encoding visible rather than inventing organizer requirements. [README, AI assistance and Deliverables][readme].

These are corrections to the understanding baseline, not a technical implementation plan.

## 7. Approximate time spent

Approximately **15 minutes of active work**, covering independent source review, report comparison, targeted verification and writing. This excludes the interruption between the initial review and the user's request to continue. No time was spent implementing a solver or producing invoice decisions.

[repo]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec
[readme]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/README.md
[cw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/contract/CW-2025-0417-CIV.pdf
[dds]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/contract/DDS-2025-118.pdf
[cg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md
[dg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/guidelines/INVOICE_AUDIT_GUIDELINES.md
[cl]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/invoices/application_lines.csv
[dl]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/invoices/invoice_lines.csv
[dl-example]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/invoices/invoice_lines.csv#L7758
[template]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/submission_template.csv
[cr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records
[dr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records
[ddr-example]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records/DDR_NGP-BD-011_20260225.txt
[cw-signature]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records/DX-00089.txt
[ddr-mismatch]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records/DDR_NGP-QA-107_20250305.txt
