# Phase 2 — Independent audit and comparison (Agent 2)

**Judgment: Agent 1A currently has the stronger Phase 2 plan.** This conclusion comes from the Phase 2 evidence, not the Phase 1 ranking. Both plans have a feasible basic approach and substantially address the Phase 1 corrections. The decisive difference is that 1A better controls uncertainty, monetary consequences and dependent historical calculations. Several specific rules in 1B would be unsafe to encode unchanged.

**Implementation readiness:** 1A is ready for a controlled start at its G0/G1 stages, with its existing interpretation and validation gates enforced. This does not mean its open valuation questions are settled. 1B requires the material corrections below before its plan should govern implementation. No implementation is performed or authorized automatically by this report.

## 1. Review basis and independent benchmark

I first reread the completed Phase 1 independent audit, README and both guidelines, then recorded the benchmark below **before opening either Phase 2 plan**. The GitHub integration confirmed that `main` remains at [`aef4924dc32506b4587de8b788b5a947e6beffec`][repo], matching the reviewed local source. I then read all three supplied files in full and revisited the contract pages needed to verify material findings.

References to **A** mean `Phase2_plan_Agent1a(1).md`, the supplied copy of Agent 1A's plan; **B** means `Phase2_plan_Agent1b.md`; **BT** means `Phase2_TASKS_Agent1b.md`. Section and decision IDs refer to those documents. Repository citations are pinned to the verified commit; PDF page numbers match the printed pages. The [Phase 1 audit][phase1] is the established baseline, not a substitute for the sources.

This review tests planning quality. It does not certify claimed experiments or future performance. I did not rebuild either agent's pricing diagnostics, write a solver, assign invoice outcomes, calculate final corrected totals or create `submission.csv`.

### What a sound plan must establish

| Requirement | Implementation-readiness standard and source basis |
|---|---|
| **Verified terms and precedence** | Rates, units, eligibility lists, dates and exceptions must have source provenance and a verification gate before use. Explicit overrides must be distinguished from genuinely conflicting wording. A blanket page-order or “specific clause wins” rule is insufficient. [CW pp.3, 12, 32–33, 38–43][cw]; [DDS pp.3, 11, 35–42][dds]. |
| **Evidence-to-charge mapping** | Preserve claims separately from record facts and contractual entitlement. Validate internal references, dates, areas/wells, required parts, signatures and vocabulary. Missing, inapplicable, unparsed and contradictory evidence must remain distinct. [CW pp.8, 27, 33][cw]; [DDS pp.5, 24, 35–36][dds]; [guidelines, checks 4–6][cg]. |
| **Chronology and amendments** | Work date, issue date, effective date, submission date and contract-year boundaries need distinct treatment. Preserve protected pre-issue valuations, calculate the retrospective difference separately, and post it once under a documented recipient/accounting interpretation. [CW pp.32, 40–43][cw]; [DDS pp.35, 39–42][dds]. |
| **Local and historical rules** | Use the correct item/area/day, well/day/run and annual scopes. Distinguish evidence reuse from repeated chargeable events; preserve PD-210's interval exception. Define which quantities enter each history and propagate corrections to dependent invoices. [CW pp.6, 8, 24–27][cw]; [DDS pp.6–7, 17, 20–24][dds]. |
| **Pricing and corrected totals** | Preserve domain-specific units, FX/index conversion, rounding stages, bands, tolerances, minimums, exclusions, discounts and VAT. Reconstruct coherent amounts without double deductions. Keep measured value, payment holds, adjustments and the README's judged total separate. [CW pp.6, 8, 14, 21–26, 32][cw]; [DDS pp.6–8, 17–22, 35][dds]; [README, Data][readme]. |
| **Validation without labels** | Use independently reasoned source cases, boundary/interaction tests, evidence annotations, appropriate invariants and complete-history reviews. Billing agreement and prevalence are diagnostics, not truth labels or acceptance quotas. Reviewer agreement is not organizer-labelled accuracy. [README, What you have, Scoring and Ground rules][readme]. |
| **Coverage and uncertainty** | Account for all invoices and applicable checks. A parser failure or unresolved rule must not silently become a pass or a known zero. Confidence must not increase merely because several correlated symptoms were emitted. The source requires honest uncertainty and a row for every invoice. [Both guidelines, principles and checks 6/12][cg]; [README, Task and Calibration][readme]. |
| **Execution order and containment** | Stages need dependencies, exit evidence and restrictions on unverified results. Material choices must be resolved or explicitly bounded before dependent calculations are trusted. Setup and extraction may begin before every later interpretation is settled. This is a planning control derived from the source's warning about systematic extraction errors. [README, Calibration][readme]. |
| **Feasibility and reproducibility** | The fixed corpus should not require unnecessary infrastructure or fresh model calls to replay. Pin source inputs, dependencies and reviewed artifacts; preserve prompts and disclosure; produce all five deliverables. A plan must not invent a deadline or claim measured performance from estimates. [README, What you have, AI assistance and Deliverables][readme]. |

The verified scale is 2,806 headers, 98,990 lines and 10,320 short text records. I also reproduced A's record-size figures: 557,687 civil bytes and 7,698,252 drilling bytes. This supports both agents' local batch choice; it does not establish their eventual runtime or correctness. [Repository inventory][repo]; [README][readme]; [civil records][cr]; [drilling records][dr].

A sound Phase 2 plan need not contain a finished implementation or every adjudicated amount. It must make unresolved dependencies visible and prevent them from becoming hidden production assumptions.

## 2. Audit of Agent 1A

**Assessment: executable, sufficiently complete and appropriately ordered for a gated implementation start.** I found no new material source contradiction requiring redesign. Its greater length receives no credit by itself; the useful content is its explicit treatment of consequences, dependencies and validation.

### Material strengths

| Strength and plan evidence | Why it matters, with source evidence |
|---|---|
| **G0–G7 have meaningful exit evidence; local checks precede historical integration.** A §2 also permits unrelated work while an uncertain rule remains isolated. | This contains a shared extraction error before final decisions and avoids making an unresolved clause block all progress. The README explicitly warns that an erroneous extracted rate propagates widely. [README, Calibration and Ground rules][readme]. |
| **Precedence is provision-specific.** A §3 and Q5 reject universal page-order and specificity shortcuts. | This is necessary because DDS clause 2, Schedule 8's internally conflicting rows and second-series exceptions cannot be reduced to one convenient blanket rule. [DDS pp.3, 27–28, 35][dds]. |
| **Evidence parsing is independent of billing, with meaningful unknown states.** A §4 distinguishes record facts, claim fields, prescribed evidence and globally unavailable background documents. | It avoids selecting an item by its billed price, treating missing optional evidence as a defect, or multiplying repeated run totals. It preserves Schedule 5 and Appendix G requirements. [CW pp.27, 33][cw]; [DDS pp.24, 35–36][dds]; [guidelines, check 6][dg]. |
| **Historical state is explicitly typed and replayed.** A §6 separates physical, measured, payable and previously invoiced quantities, and requires downstream replay after an early correction. | Annual bands, daily caps and exclusions are different histories. A temporarily unsupported payment is not automatically proof that no measurable work occurred. [CW pp.6, 8, 24–25][cw]. |
| **Retroactivity is treated as two valuations.** A §7 protects historical submissions, isolates rate-change differences from other corrections, preserves work-date discounts and checks exactly-once posting. | This directly addresses the interaction between normal work-date pricing and later retrospective instruments. [CW pp.32, 43][cw]; [DDS pp.35, 40–42][dds]. |
| **Corrected totals are not merely billed totals minus findings.** A §8 prevents overlapping deductions, recomputes DDS discount/VAT, and separates procedural holds from contract-supported value. | Clauses defining totals differ from clauses governing withholding and recovery. This distinction is essential to the requested expected amount. [CW pp.8, 14, 32][cw]; [DDS p.8][dds]; [README, Data/Task][readme]. |
| **Validation tests the interpretation and implementation separately.** A §10 requires source-derived expected values before corresponding code, blind record annotation, full-history examples, controlled mutations and a review sample protected from tuning. | These controls are stronger evidence than reproducing billed prices. They directly address the lack of organizer labels and the danger of shared-rule errors. [README, What you have and Scoring][readme]. |
| **Reproducibility and deliverables are complete.** A §§11–14 cover row confidence, versions, prompts, disclosure, pinned replay, output integrity and method-failure analysis. | They match the README and template without inventing labelled F1, severity cutoffs or empirical calibration. [README, Task, Scoring, AI assistance and Deliverables][readme]; [template][template]. |

The Phase 1 unit-rejection and civil duplicate-allocation omissions are expressly corrected in A §§5–6. The plan also preserves the drilling interval exception. [CW pp.6, 8][cw]; [DDS p.7][dds].

### Remaining weaknesses and obligations

These are bounded execution risks, not invented errors or reasons to require a finished solver at the planning stage:

- **Its open-question register is substantial.** Q1–Q7/Q11 affect recipient allocation, payment history, quantities and state. Those decisions can change later amounts. The gates address the risk, but the first implementation work must turn each question into an explicit decision/status and identify the stage it blocks. A statement that the plan was approved must not be treated as approval of every unresolved formula. **Evidence:** A §§2, 6–9; [CW pp.6, 8, 14, 24, 32, 43][cw]; [DDS pp.6–8, 27–28, 35, 42][dds].
- **Unknown-total export remains a completion dependency.** A §8 correctly refuses to invent a numeric answer, but deferring the convention until G7 could create a late packaging obstacle if genuinely unpriceable cases remain. Surface that decision during early consequence review; do not resolve it by automatically zeroing uncertain lines. **Evidence:** A §8/Q9; [README, Task][readme]; [guidelines, principle 3][cg]. This does not block input/specification work.
- **The 20–30-hour estimate and proposed review sample are planning assumptions.** A labels them appropriately. They are not demonstrated capacity or accuracy. Reassess the estimate after the first complete civil and drilling examples, retaining the validation reserve and adding cases for uncovered interactions rather than treating a sample count as sufficient proof. **Evidence:** A §§10, 14; [README, absence of a time budget and lack of labels][readme].

No material omission of an entire guideline check, source family, amendment mechanism or required deliverable was established. The plan's explicit uncertainty is generally a strength: the README permits reasoned, logged choices where a clause remains ambiguous. [README, Ground rules][readme].

## 3. Audit of Agent 1B, including TASKS

**Assessment: a feasible architecture with useful controls, but not safe as the governing plan unchanged.** Its problems are concentrated in particular decision rules and omitted consequences, rather than in the choice of Python, structured terms or separate pricing engines.

### Material strengths and improvements

1. **Phase 1 corrections are genuinely incorporated.** B §§0, 2 and 4 distinguish mismatch, reuse and duplication; preserve PD-210's exception and per-well footage scope; state civil unit/later-copy consequences; and reject flag-count targets. B §8 now explicitly includes AI disclosure. These improvements should be credited rather than carrying the old criticisms forward automatically. [CW pp.6, 8][cw]; [DDS pp.7, 17][dds]; [README][readme].
2. **Transcription control is concrete.** B §3 proposes two reads, a numeric/quotation disagreement record and adjudication against the scan before use. It recognizes that illustrative examples can conflict with operative provisions and should not override them. This is useful execution detail, provided independent arithmetic checks are not mistaken for proof of the applicable rule. [CW pp.32, 36][cw]; [DDS pp.30, 35][dds].
3. **Validation is not simply postponed to S8.** B §5 requires source evidence, boundary tests and hand-worked cases before a rule is enabled. Its scope-of-impact review and explicit no-unexplained-residual check are valuable. The stage table alone would understate these earlier checks. [B §§1, 3, 5; README, Calibration][readme].
4. **The ordinary monetary pipeline and reproducibility are largely sound.** B §§2, 7–8 preserve native currencies, separate rate and invoice discounts, recompute DDS VAT, commit reviewed terms and require a fresh-clone reproduction. [DDS pp.6, 8, 35, 40–41][dds]; [README, Data and Deliverables][readme].

### Material findings

**B-P1 — Genuinely unknown value is converted into a zero contribution. High priority; correct before coding totals.**

**Plan evidence:** B §6, “Unpriceable invoices,” includes ambiguous code matches, parser failures and readings with no defensible choice, then excludes all such query lines from the expected total. It cites DDS clause 41 and CW clause 46.

**Source check:** DDS clause 41 permits withholding a disputed charge while paying the undisputed balance. Clauses 36–40 separately define invoice net, discount, VAT and total. CW clause 46 concerns a specifically required, undelivered record. Neither establishes that every parser failure or unresolved interpretation has a known contract-supported value of zero. The README asks what the invoice should have totalled; guideline principle 3 requires an unpriceable case to remain a query. [DDS p.8][dds]; [CW p.8][cw]; [README, Data/Task][readme]; [guidelines][dg].

**Consequence:** this policy can turn uncertainty into an unsupported amount reduction, then alter DDS discount and tax as well. Distinguish an explicit rejection, a substantiated payment hold and a genuinely unknown valuation. A §§8–9 make that distinction more safely. This criticism does not imply that a proven missing mandatory record can never justify a zero currently payable amount.

**B-P2 — The probability aggregation creates unsupported confidence. High priority; replace before decisions are encoded.**

**Plan evidence:** B §6 assigns finding probabilities, calculates invoice probability as `1 − product(1 − p)`, applies the 1/6 threshold, and exports confidence in the binary decision. D-9 explicitly says confidence covers the flag rather than the amount.

**Reasoning:** the product calculation requires assumptions about the joint occurrence of findings that the plan does not establish. Findings can share a missing record, interpretation or arithmetic cause. As a simple hypothetical, emitting the same 0.90-strength evidence twice would produce 0.99 without adding information. The chosen tier values are judgments, not established probabilities. A small reviewer-agreement exercise cannot by itself validate that joint model or prove population calibration.

**Source check:** the README describes confidence in the submitted row and penalizes confidently wrong extraction; it provides no labels or prescribed finding-probability model. Its 5:1 cost supports the threshold derivation only for the isolated binary decision with reliable probabilities. B correctly labels the threshold as its own choice, but that does not supply the missing probability basis. [README, Task and Scoring][readme].

**Correction:** account for shared causes and distinguish decision confidence from amount confidence. Do not let several correlated symptoms conceal an uncertain total. A §11 handles these dependencies explicitly; neither agent's suggested numeric confidence levels should be advertised as empirically calibrated.

**B-P3 — Schedule 8 is discounted using an unsupported blanket precedence argument. High priority; correct before affected service rules are frozen.**

**Plan evidence:** D-8 says the specific clauses govern because Schedule 8 is general and absent from clause 2's document list. B §9 treats Schedule 8 taking precedence over clause 21 as a failure mode.

**Source check:** DDS p.3 does list only earlier parts/schedules/appendices, but also states that a Schedule prevails over a Part. The incomplete enumeration likewise omits Part IX and Appendix G, which B correctly uses elsewhere. Omission therefore does not, by itself, justify selectively demoting Schedule 8. Schedule 8 contains actual service-specific statements: DD-120/RM-530 hour wording, HC-630's event and DD-102's contradictory introduction/row. [DDS pp.3, 27–28, 35–36][dds].

**Correction:** adjudicate each conflict using its text, explicit overrides and incorporated references; preserve a documented alternative where necessary. The preferred outcome might still match B's choice for an individual service. The defect is treating one unsupported shortcut as sufficient authority for all of them. A §3/Q5 is stronger here.

**B-P4 — The civil state basis and its dependency order are insufficiently defined. Medium–high priority.**

**Plan evidence:** B §4.2 counts only payable measured quantity in annual bands, so every disallowed line stops advancing the band. It says state ledgers are computed once globally. The stage chain creates those ledgers in S5 before the S6 checks and S7 payable amounts, although those consequences can determine the proposed band input.

**Source check:** Schedule 4 Part 3 speaks of measured quantity. Clause 46 separately suspends payment pending evidence; P23 provides a subsequent recovery mechanism. Measured quantity, claimed quantity and currently payable quantity therefore cannot simply be declared interchangeable. [CW pp.8, 14, 24–25][cw].

B deserves credit for proposing billed/payable sensitivity runs. However, those two alternatives do not automatically capture the distinction between unsupported payment and accepted physical measurement. The plan also needs an explicit dependency boundary: establish the relevant entitlement/measurement inputs before trusting stateful prices, and replay dependent histories after changes. A §§6–7/Q6 states this more clearly. This finding identifies an unresolved dependency, not proof that every proposed band result would be wrong.

**B-P5 — Payment-history rules are not fully carried into the checks. Medium priority; add coverage and a reporting decision.**

**Plan evidence:** B §§2 and 7 exclude retention/release from the judged total, correctly. But its checks, state ledgers and decision register do not explicitly cover clause 45A's first-post-completion release or P23's next-valuation missing-record recovery. Those mechanisms are absent from the operative plan, beyond the general separation of fields.

**Source check:** CW p.32 specifies the release event and payment formula; p.14 specifies P23's later recovery. The guidelines require contractual additions/deductions and a recorded outcome. Exclusion from the README's selected total does not alone dispose of whether a separate compliance finding exists. [CW pp.14, 32][cw]; [guidelines, checks 11–12][cg]; [README, Data][readme].

**Correction:** cover these histories and document whether/how payment-only defects affect the binary outcome, while preserving the judged field. Do not recover an amount both immediately and again later. A §§6–9 includes these questions. I am not asserting that every payment-field defect must change `expected_total_cents`.

**B-P6 — Some “inert rule” decisions and the proposed cut order are too weakly supported. Medium priority.**

**Plan evidence:** B §6 permits documented no-ops for several rules; §14 uses agreement between existing records and billed ground fields to support leaving line ground in force, and keyword absence to declare special conditions inert. Section 10 then allows removing assertions for inert rules.

**Source check:** S4 concerns classification actually recorded on the excavation day; the count of matching available DX/PT records is narrower than the full applicability question. Schedule 5 prescribes tickets for only particular items. Likewise, absence of selected words is not by itself proof that no synonymous narrative expresses a condition. [CW pp.10, 27][cw]; [README, free-text records][readme].

**Correction:** it is reasonable to avoid elaborate machinery for a rule proven inapplicable to the pinned corpus. Retain a scope check or explicit evidence limitation establishing that inapplicability; do not turn a partial check into a universal default or cut its only guard. This does not require manufacturing missing background evidence or flagging every unprovided document.

### Choices that are not established errors

- **Registered tie and allocation conventions:** B's inclusive issue-day reading, lowest-ID tie-breaker and earliest-submitted weekly allocation are more committed than A's alternatives. A recorded convention is permissible under the README, so commitment alone is not a fault. However, issue-day prices do not prove adjustment placement, and numerical ID order is not a contractual submission-time fact. Where invoice attribution changes, preserve the alternative and confidence limitation. [B D-1/D-6; CW pp.8, 27, 32, 43][cw]; [DDS pp.35, 42][dds]; [README, Ground rules][readme].
- **DDS adjustment placement:** B correctly marks D-2 unresolved. Its §7 formula must remain provisional until discount/VAT and recipient scope are settled; adding an adjustment after VAT is not already established merely because the formula shows it there. A's broader Q1/Q2 is better specified, but the source does not justify declaring B's final answer wrong before it has chosen one. [DDS pp.8, 35, 42][dds].
- **Billing reconciliation:** T1 is useful if it compares independently computed totals and requires investigation of residuals. It becomes circular only if equality is obtained by copying billed totals or changing unsupported terms to fit. B explicitly rejects quotas, so I do not repeat the Phase 1 quota criticism. [B §§0, 5, 7; README][readme].

### What the TASKS file actually adds

BT is primarily a **record of Phase 2 work**, not a separate implementation backlog. Its opening scope, checked plan-writing sections and close-out items establish that purpose. It usefully records the interrupted independent rereads, untested OCR availability and pages still needing review. Those disclosures help distinguish completed work from future S1 verification.

It does not add new implementation dependencies or acceptance tests beyond B's own §§1/11. The checked “independent reread” items also need to be read with BT's later partial-completion note; they do not establish a completed future verification gate. B §12 makes the limitation explicit. This is a status-presentation issue, not evidence of concealment or a reason to penalize the interrupted work.

Thus the file adds modest provenance and continuity value. It neither earns an extra-artifact advantage nor compensates for B-P1–B-P6. A's gates are directly comparable despite living in one file.

## 4. Direct comparison

| Dimension | Agent 1A | Agent 1B | Evidence-based judgment |
|---|---|---|---|
| Feasible core approach | Local deterministic batch, reviewed terms, no runtime model dependency | Same general choice, concrete proposed layout | **Approximately equal.** Both fit the source scale and reproduction requirement. A §1; B §§0/8; [README][readme]. |
| Precedence and amendments | Explicit overrides, two valuations, open recipient/accounting questions | Correct principal chronology; D-8 shortcut and narrower placement assumptions | **A stronger.** B-P3 and the documented D-2 limitations; [DDS pp.3, 8, 27–28, 35, 42][dds]. |
| Evidence mapping | Raw facts, semantic joins, required-part scope, background-document limitations | Good families/glossary/signatures; improved mismatch distinction | **Both strong; A more cautious on inadequate evidence.** A §4; B §§2–4; B-P1/P6. |
| Cross-invoice rules | Separate state quantities, correct scopes, replay and allocation questions | Useful ledgers, but payable-basis/dependency and payment-history gaps | **A stronger.** B-P4/P5; [CW pp.8, 14, 24, 32][cw]. |
| Pricing and ordinary totals | Exact stages and interactions, overlapping findings handled | Correct main build-up and DDS recalculation | **Mostly equal on settled arithmetic; A stronger on consequences.** A §§5/8; B §§2/7; B-P1/P5. |
| Validation without labels | Independent expectations, protected sample, interactions and invariants | Two reads, hand cases, residual and scope-of-impact controls | **Both useful; A stronger overall.** A §10 protects against tuning and shared causes; B §5 adds concrete diagnostics. [README, Calibration][readme]. |
| Confidence and unknowns | Explicit unknown values; separate decision/amount confidence; no correlation multiplication | Automatic query exclusion and independence-style probability product | **A materially stronger.** B-P1/P2. |
| Sequencing and containment | Gated rule use, local-to-historical integration, replay | Named stages and exit artifacts; incomplete state dependency | **A stronger.** A §§2/6/10 versus B §§1/4.2/11; B-P4. |
| Reproducibility/deliverables | Complete | Complete, with useful concrete commands/artifacts | **Approximately equal.** A §13; B §8; [README, Deliverables][readme]. |
| Time and complexity | Conditional 20–30-hour estimate, reserved validation time, risk-based expansion | Budget shares, explicit cut order, larger fixed review commitments | **A slightly stronger control of scope.** No actual remaining deadline is known; B should retain applicability guards and size review by coverage. A §14; B §§5/10; B-P6. |

No credit is assigned for report length, confidence of prose, number of files, prior ranking or reported effort. Neither plan establishes real detection accuracy before implementation and validation.

## 5. Selection and implementation readiness

**Select Agent 1A's Phase 2 plan as the governing plan for the next phase.** The preference is substantive: unsupported zero amounts, correlated-confidence inflation and blanket precedence reasoning could systematically corrupt a later solution. A addresses those risks directly. Its treatment of historical measurement, payment and replay is also more complete.

The preference is stronger than a formatting or detail advantage, but it is not proof that Agent 1A will achieve a better final score. B's extraction and review controls are useful, and its Phase 1 corrections demonstrate real improvement.

Useful parts of B worth retaining as review requirements are:

- **The explicit transcription disagreement artifact** in §3: it makes source review auditable. It should distinguish transcription disagreement from a genuinely ambiguous clause.
- **T1's concrete residual check:** an apparent pass should have no unexplained difference between independently recomputed and billed totals. It is a diagnostic gate, not a requirement to force billing agreement.
- **T2's breakdown of affected scope** by code/month/context: this can quickly expose one shared incorrect term. Clustering is a reason for review, not proof that legitimate findings must be scattered.
- **The candid not-confirmed list** in §12/BT: retaining exact verification limits prevents an incomplete reread from being mistaken for a completed gate.

These are audit recommendations, not a merged implementation design. They do not import B's query-value or probability policies.

| Readiness decision | Meaning |
|---|---|
| **1A: ready for a controlled implementation start** | Begin with G0/G1 and the relevant evidence work when separately instructed. Affected pricing/state rules remain gated by their source decisions and independent cases. No requirement to finish every later artifact before starting setup. |
| **1B: revise before it governs implementation** | Correct B-P1–B-P3 and explicitly address B-P4–B-P6. Starting to encode its current totals/confidence/precedence rules would create avoidable rework and systematic risk. |
| **Final invoice decisions: not yet ready under either plan** | Neither plan is an implemented, validated solution. Open accounting and evidence consequences must pass their gates before final amounts or a submission are released. |

## 6. Corrections and conditions to carry forward

1. **Preserve unknown amounts as unknown until justified.** Keep rejection, temporary payment hold, disputed charge and unresolved valuation distinct. Decide the genuinely unknown-total export convention early enough to avoid a late completion block. [B-P1; README, Task][readme]; [CW p.8][cw]; [DDS p.8][dds].
2. **Use service-specific precedence decisions.** Do not dismiss Schedule 8 merely because an incomplete earlier list omits it; do not automatically accept its conflicting rows either. Record the reasoned interpretation and sensitive alternatives. [B-P3; DDS pp.3, 27–28, 35–36][dds].
3. **Define each history's quantity and order before trusting its output.** Measurement, payment eligibility and raw claims are distinct. Include dependency/replay tests for early corrections and all required payment-history mechanisms. [B-P4/P5; CW pp.6, 8, 14, 24–25, 32][cw].
4. **Close or bound the retrospective accounting choices before affected totals are final.** Preserve pre-issue protection; settle adjustment population, recipient/ties, well-versus-contract scope and interaction with discounts/VAT without double posting. [A Q1/Q2; B D-1/D-2; CW pp.32, 43][cw]; [DDS pp.8, 35, 40–42][dds].
5. **Do not aggregate correlated findings into artificial certainty.** Keep amount uncertainty visible even when a breach is clear. Treat reviewer agreement and confidence tiers as limited internal evidence, not organizer calibration. [B-P2; README, Scoring][readme].
6. **Retain applicability checks when reducing scope.** A verified inactive rule may need little machinery; partial keyword coverage or agreement with billed fields cannot silently replace its contractual condition. [B-P6; CW pp.10, 27][cw]; [README, free-text records][readme].
7. **Require independent expected cases and complete-history checks before release.** Protect some review cases from tuning; keep both flagged and apparent-pass review; use billed residuals only after source-derived computation. [A §10; B §5; README, What you have and Calibration][readme].
8. **Preserve complete coverage and reproducibility.** All twelve checks, both contracts, 2,806 rows, native minor units, versioned prompts, AI disclosure and all five deliverables remain required. No short-budget cut should silently turn unfinished work into a pass. [Both guidelines][cg]; [README][readme]; [template][template].

## 7. Approximate time spent

Approximately **12 minutes of active work** for the independent benchmark, full reading of the three Phase 2 files, targeted source verification, comparison and report checks. This excludes the earlier Phase 1 audit. No solver implementation or invoice classification was undertaken.

[repo]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec
[readme]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/README.md
[cw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/contract/CW-2025-0417-CIV.pdf
[dds]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/contract/DDS-2025-118.pdf
[cg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md
[dg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/guidelines/INVOICE_AUDIT_GUIDELINES.md
[cr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records
[dr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records
[template]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/submission_template.csv
[phase1]: sandbox:/workspace/scratch/89f7e186609f/Phase1_audit_and_comparison_Agent2.md
