# Phase 2.5 — Independent solution-selection audit (Agent 2)

**Selection: retain the existing solution family**—reviewed contractual policy and evidence mappings, explicit historical state, and deterministic exact valuation, assisted by LLMs for extraction, interpretation proposals and independent source review. No materially different primary architecture is justified by the inspected evidence. No discriminating experiment is required before making this family selection.

**Agent 1A provides the stronger exploration.** It evaluates stronger versions of the alternatives and distinguishes demonstrated facts from architectural expectations. Agent 1B contributes the better corpus inventory, whose principal counts I independently reproduced. Their convergence is justified, but several of 1B's arguments for it are too categorical.

This selects a family, not every proposed contractual interpretation. The source-supported corrections from the planning audit remain review requirements. Implementation, G0/G1, invoice classification and final totals were not begun.

## 1. Review basis and independent selection criteria

I established the criteria below before reading the two exploration reports. I used the completed Phase 1 and Phase 2 audits as context, confirmed that the supplied background copies match the previously reviewed artifacts, and checked the repository rather than treating either prior judgment as authority. GitHub and the local source agree on commit [`aef4924dc32506b4587de8b788b5a947e6beffec`][repo].

**A** below means `Phase2_5_solution_exploration_Agent1a.md`; **B** means `Phase2_5_solution_exploration_Agent1b.md`. Both were read in full. Section references identify their claims; repository links are pinned to the reviewed commit. Contract page numbers are printed/PDF page numbers.

Fresh checks concentrated on selection-critical evidence: the README and guidelines; a descriptive inventory of all 10,320 record files; numeric roles within civil narrative forms; DDR vocabulary and Parts C–E; and targeted contract images, including CW p.27/p.32 and DDS pp.7, 24, 27, 35–36. This was corpus inspection, not implementation of an evidence parser or valuation engine. The established source review supplied the remaining contract context.

| Criterion | What should determine the family |
|---|---|
| **Actual semantic workload** | Determine whether the fixed corpus has a manageable set of meanings, numeric roles and exceptions. File count, template count and recognized keywords alone do not establish correct interpretation. The README expressly makes record-to-item identification part of the task. [README, records][readme]; [guidelines, check 6][cg]. |
| **Reusable policy versus individual judgment** | Separate shared clauses and dated regimes from case-specific evidence, allocations and unknown facts. Repeated policy favours reviewed reuse; pervasive unresolved case semantics would strengthen model-led adjudication. [CW pp.27, 32, 38–43][cw]; [DDS pp.24, 27–28, 35–42][dds]. |
| **Historical and monetary fidelity** | Every credible family must preserve global ordering, event identity, retrospective protection and exact rounding. These requirements favour explicit computation; they do not by themselves prohibit an LLM from selecting premises while using exact tools. [CW pp.6, 8, 24–26, 32][cw]; [DDS pp.6–8, 17, 35][dds]. |
| **Incremental information** | Ask what a runtime model or constraint solver would discover beyond reviewed records and policy. Flexible semantic interpretation and joint feasible allocations are real contributions; repeated narration or arithmetic generation is not. [README, task and evidence joins][readme]; [DDS pp.7, 24, 36][dds]. |
| **Independent error detection** | The chosen family must expose wrong shared meanings and missing obligations, not merely reproduce its own formulas. Bills, reported prevalence, model agreement and solver consistency are insufficient truth labels. [README, no labels and Calibration][readme]. |
| **Reproduction and practical burden** | Compare complete workflows, including extraction, verification, inference, review and replay. The deliverable is a reproducible submission, not a particular language or ban on runtime AI. No remaining deadline or measured comparative performance is supplied. [README, AI assistance and Deliverables][readme]. |

The population—2,806 invoices and 98,990 lines—supports automated local processing and makes wholly manual valuation unattractive. It does not establish a numerical speed or accuracy advantage for any unimplemented candidate. [README, inventory][readme].

## 2. Independent findings that drive the selection

### 2.1 The language is sufficiently bounded to select reviewed deterministic parsing

I reproduced B's principal inventory. For civil records I grouped the narrative paragraph after replacing contiguous digits with a placeholder; for DDRs I enumerated colon-delimited keys and comma-separated crew/tool terms, removing crew counts. This describes the pinned corpus, without assigning invoice outcomes.

| Corpus observation | Independent result and limit |
|---|---|
| Civil narratives | **26 forms across 2,169 records:** CT 5, PR 5, JS 4, DX 3, DW 2, MO 2, PS 2, PT 2, CV 1. This confirms B §1/D2. [Civil records][cr]. |
| DDR structure and vocabulary | **36 field keys; 5 crew terms; 15 tool terms** across 8,151 DDRs. I checked all 20 terms against Appendix G. The two tool-list fields have the same observed vocabulary. [DDR records][dr]; [DDS p.36][dds]. |
| Parts not semantically reviewed by B | Part C occurs in **479** records, D in **367**, E in **54**. Their observed values remain restricted: two surveyed sections; one source description, `density and neutron`; certification `Yes`; four loss-tool names, all covered by Appendix G. Counts, run identifiers and accumulated hours vary numerically. [DDR records][dr]; [DDS pp.24, 36][dds]. |
| Numeric roles masked by the template count | In the corresponding forms, pipe diameter is consistently **400**, chamber diameter **1800**, mesh designation **393**, Type **1**, and the numeric trench-depth wording **3 m**. Quantities vary separately. This supports bounded interpretation, while showing why masking digits alone discards meaningful information. [Civil records][cr]; examples [CT-00002][ct], [PT-00001][pt1], [PT-00170][pt], [DX-00001][dx]. |

These observations materially strengthen A's explicitly limited spot checks. There is no observed large tail of unconstrained narrative wording requiring fresh interpretation on every record. For this fixed challenge, reviewed mappings plus explicit exception handling are a well-supported choice.

However, **lexical coverage is not entitlement coverage**. A weekly narrative must be checked against its listed working days and the five-day condition. A pressure-test certificate can describe pipe or a chamber. `gamma tool` maps to different service/loss contexts, and repeated run metadata is not a fresh daily quantity. Dates, signatures, units, contextual meaning and conflicting evidence remain obligations even when every string matches a pattern. [CW p.27][cw]; [DW-00008][dw]; [PT-00170][pt]; [DDS pp.7, 24, 36][dds]; [example DDR][ddr].

Thus B's inventory is correct; its inference that there is consequently nothing left for a model to interpret is too strong. The evidence supports a manageable review burden, not a completed semantic correctness proof.

### 2.2 Interpretation is substantially reusable, but not exhausted by a dozen questions

Most policy is shared: item schedules, eligibility lists, contract-year rules, amendments and explicit vocabulary. One reviewed interpretation can be applied across many invoices. Repeated per-invoice rediscovery of those terms supplies little additional information. [CW pp.17–27, 32, 39–43][cw]; [DDS pp.15–24, 35–42][dds].

Individual applications still depend on facts and history: which days a weekly ticket supports, whether two references represent the same event, what a run boundary establishes, and which invoice receives a retrospective adjustment. DDS Schedule 8 also contains genuinely conflicting text; Appendix G does not automatically reconcile all of it. [CW pp.27, 32, 43][cw]; [DDS pp.7, 24, 27–28, 35–36, 42][dds].

B §1/D8 derives its “about a dozen” estimate from the plans' question registers. Those are useful inventories, not an independently established upper bound on interpretations. A single question about adjustment recipients or quantity state can generate many factual cases. The supported conclusion is that **shared interpretation dominates**, while case-level exceptions must remain possible.

### 2.3 Exact totals and state constrain every family, without choosing one by themselves

Civil final-rate half-up rounding has later half-even conversion/index stages; drilling has staged half-even rounding and downstream discount/VAT effects. Retroactive instruments protect earlier submissions and require a subsequent single adjustment. Once-per-run/well events and annual accumulators require history beyond an invoice. [CW pp.6, 8, 24, 32, 43][cw]; [DDS pp.6–8, 17, 35, 42][dds].

Consequently, an isolated invoice prompt and generated monetary answer are unsuitable. But a model can select evidence, an interpretation and valuation instructions while exact tools maintain state and calculate amounts. That remains a different family if the model's case judgment determines entitlement. A §§5–6 recognizes this; B §§3–4/11 incorrectly treats delegation itself as collapse into the compiled-policy family.

The stronger reason to select compiled policy is the combination of **repeated policy, bounded evidence language and expensive shared-rule verification**. It allows one reviewed correction to be applied consistently across the population. It does not make that correction inherently right.

## 3. Audit of Agent 1A

**Assessment: broad enough, source-grounded and appropriately conditional.** Its preference survives scrutiny without depending on the prior Phase 2 ranking.

Material strengths:

- **It compares genuinely different solving processes.** A §4 preserves competing evidence allocations in a joint feasibility model; §5 gives model-led adjudication exact tools and full histories. This avoids defeating alternatives by withholding capabilities they could realistically use. The distinctions matter for weekly evidence, repeated run records and adjustment placement. [CW pp.27, 32][cw]; [DDS pp.7, 24, 35][dds].
- **It identifies where a compiler can fail systematically.** A §3 names confidently wrong semantic mappings, wrong state inputs and omitted obligations. Its independent review begins from records and contractual requirements rather than merely checking the engine's trace. That addresses the README's warning about shared extraction errors. [README, Calibration][readme]; [both guideline checklists][cg].
- **It treats exact tools and reproducibility fairly.** A §5 distinguishes recorded-decision replay from fresh inference, and requires replay to rebuild calculations rather than return a cached final CSV. That is a plausible interpretation of the README's reproduction requirement; fresh-inference stability is a separate limitation to disclose. [README, Deliverables and AI assistance][readme].
- **It avoids evidence-first overreach.** A §4 notes that records do not necessarily enumerate every payable item or prove that every possible charge belongs on the current invoice. Civil Schedule 5 is item-specific; DDR run records repeat. This protects a reconstruction method from inventing a complete billing obligation. [CW p.27][cw]; [DDS p.24][dds].

Limits requiring qualification, rather than a different selection:

1. **Its own corpus evidence is narrow.** A §2 explicitly relies on representative records, so its bounded-language premise was not established comprehensively by A alone. The full-corpus inventory in §2.1 above supplies additional support. Credit its candid limit; do not credit it with a coverage verification it did not perform. [A §2; civil records][cr]; [DDR records][dr].
2. **Its effort comparisons are unmeasured.** A §4's 1.5–2× estimate for full constraint reconstruction and §3's inherited 20–30-hour allowance are labelled estimates. Neither should decide selection or become a delivery commitment. The defensible burden argument is that constraints still require the same source extraction plus a reviewed feasible-allocation model; no measured multiplier is available. [A §§3–5/7; README, deliverables][readme].
3. **Its future checks are useful safeguards, not prerequisites for selecting a family.** A §7 presents them for a later authorized phase. There is currently enough source evidence to choose the primary family without building competing pilots. No candidate's accuracy has been established.

I found no material repository contradiction in A's family-selection reasoning that requires replacing its recommendation.

## 4. Audit of Agent 1B

**Assessment: useful empirical support, but the comparison is narrowed by several unsupported exclusions.** Correcting those exclusions still leaves its preferred family well supported.

Its strongest contribution is the reproducible narrative/key/vocabulary inventory, independently confirmed above. Its proposals for transcription disagreement review, source-derived cases, impact grouping and an exception queue are also useful controls. Its §13 discloses exactly what the inventory did not verify. These are substantive strengths, not credit for report length. [B §§1, 5–6, 12–13; README, Calibration][readme].

### Material corrections to the selection argument

| Finding | Evidence and correction |
|---|---|
| **B-1: Semantic closure is asserted beyond the check performed.** | B §§1/D2, 5, 7 and 11 treat 26 forms/20 terms as complete mapping coverage. B §13 then acknowledges unverified numeric meaning, possible item ambiguity and unreviewed C–E values. The source requires contextual item identification, weekly-day checks and specific DDR parts, not merely recognized strings. Replace “nothing left to interpret” with “bounded observed vocabulary, suitable for reviewed mappings with unresolved cases retained.” [CW p.27][cw]; [DDS pp.24, 36][dds]; [guidelines, checks 4–6][dg]. My extra checks strengthen boundedness but do not retroactively validate B's stronger proof claim. |
| **B-2: The tool-assisted LLM alternative is weakened unnecessarily.** | B §§3–4 says amounts are reasoned rather than computed and that delegation reduces the alternative to commentary; §§6/8 say there is no unit-level assurance and only output sampling. A model may choose entitlement while code calculates it, and structured decisions can be tested against source-derived cases, invariants and equivalence checks. Exact tools do not prove its interpretation, but neither do they erase its distinct role. [DDS pp.6–8, 27, 35–36][dds] separate evidence/entitlement questions from arithmetic. No repository rule requires an LLM-led family to generate amounts, reread scans afresh or omit shared decisions. [README][readme]. |
| **B-3: Constraint reconstruction is dismissed as notation.** | B §§3/10 is correct for a deterministic rule engine written declaratively. It omits the materially different case where the solver retains and jointly tests competing event/charge allocations. Weekly evidence, run events, PD-210 interval exceptions and single adjustment placement provide concrete possible applications. [CW pp.27, 32][cw]; [DDS pp.7, 24, 35][dds]. This omission weakens breadth; it does not establish that a full constraint solver is preferable. |
| **B-4: Reproducibility is overstated as an exclusion.** | B §§8–9/12 implies that cached model decisions need organizer relaxation and otherwise require API access to reproduce. The README requires a runnable repository reproducing the submission and permits AI; it does not demand fresh model reasoning on every replay. Versioned, source-linked intermediate decisions can support exact offline recalculation. Whether they are adequately justified remains reviewable. A cached final CSV alone would be weak evidence, but that is not the strongest alternative. [README, AI assistance and Deliverables][readme]. |
| **B-5: A bounded vocabulary is confused with a closed interpretive workload.** | B §1/D8 and §11 infer interpretation once per clause and essentially none per case from the plans' approximately twelve questions. That does not settle factual allocation, missing evidence or the scope of an hourly period; a single shared ambiguity can have different consequences across histories. [CW pp.27, 32][cw]; [DDS pp.7, 24, 27, 35][dds]. Review shared policy once where possible, without forbidding source-grounded case adjudication. |

Three lesser assertions should also remain provisional. B §10 has no measured basis for declaring OCR plus a text model dominated by multimodal reading; all readers face the same scans. B §8's faster/slower comparisons and approximately 2,806 calls assume a particular invocation granularity, not a compulsory architecture or measured total effort. B §12's illustrative >2% exception threshold is not source-derived: one rare, high-impact exception may justify review. These claims should not drive selection. [B §§8, 10, 12–13; README, scans, Calibration and absence of a specified compute budget][readme].

The description of F1 as exact, complete and consistent in B §8 also needs to distinguish intended capability from demonstrated coverage. Deterministic replay supplies consistency; completeness and correctness still require independent evidence.

## 5. Strongest alternatives and direct comparison

### Joint constraint reconstruction

This is a credible separate family when it searches across admissible allocations or histories rather than merely evaluating fixed rules. It can reveal that several allocations remain possible and identify conclusions that survive all of them. A §4 represents this fairly; B's F4 dismissal does not.

Nevertheless, the repository already supplies explicit invoice-to-record references, record identities, dates and well/run fields. Many consequences are prescribed directly, including run first/last-day events and civil's later-duplicate rule. The central work is therefore source interpretation and exact historical evaluation, with some allocation uncertainties; pervasive open assignment search has not been demonstrated. [README, Data][readme]; [CW p.8/p.27][cw]; [DDS pp.7, 24][dds].

Constraint solving cannot infer absent contractual facts, resolve conflicting authority from consistency alone, or safely choose the allocation that best fits billed totals. As a full replacement it adds formalization and validation work without removing the common source-reading burden. Retain **bounded joint ambiguity analysis** when an identified history needs it; that is an auxiliary technique, not a reason to redesign the whole audit.

### LLM-led adjudication with exact tools and cached decisions

This also remains credible. A model could add information by identifying an overlooked condition, recognizing contradictory evidence or making a supported case distinction missing from a compiled rule. Complete histories, shared interpretations, source citations and exact tools can mitigate its weaknesses. Its inputs need not be independently reread from scans on every call, and its recorded decisions can be replayed.

The inspected corpus does not demonstrate enough such incremental work to warrant making fresh case judgment the population-wide authority. Vocabulary is restricted, explicit Appendix G mappings override intuitive similarity, and most policy is reusable. A runtime model still needs verified source content, global history and an exact monetary layer, while its decisions need consistency checks and review. [§2.1 above; DDS pp.7, 24, 35–36][dds]; [README, reproduction][readme]. This is a reasoned workload comparison, not measured proof that model-led auditing would score worse.

Retain **source-led adversarial review and reviewed exception interpretation**. If that work later demonstrates repeated source-confirmed improvements that cannot be captured economically by shared policy, a larger runtime role becomes worth reconsidering. An exception queue with frozen accepted facts is within the existing assisted family, not automatically a new architecture.

### Other approaches

Billing-inferred rates and anomaly detection lack authority to set contractual totals or detect a consistently omitted discount; there are no organizer labels. They may direct attention after an independent valuation, never supply the truth criterion. [README, no labels, amounts and Ground rules][readme]; [amended discount regimes, CW pp.41–42][cw]; [DDS pp.40–41][dds].

An evidence-first event ledger with fixed decisions, SQL instead of Python, spreadsheet formulas, retrieval and build-time code generation are implementation choices within a family. A second independently reasoned implementation can aid validation but does not eliminate a shared interpretation error. No additional materially credible primary family was found missing from **the two reports together**; the important omissions are in B's treatment of constraints and the strongest runtime hybrid.

| Comparison | Current judgment |
|---|---|
| Breadth and fair treatment of alternatives | **A stronger:** separate joint reconstruction and tool-assisted adjudication; B dismisses or restricts these prematurely. [A §§4–5; B §§3–4/10.] |
| Empirical input characterization | **B stronger:** the verified full-corpus form/vocabulary counts materially improve on A's spot checks. Qualification of their meaning remains necessary. [A §2; B D2/§13; this audit §2.1.] |
| Common-error and uncertainty reasoning | **A stronger:** explicitly separates internally consistent output from source correctness and permits case-level uncertainty under every family. [A §§3–6; B §§6/8/11; README, Calibration][readme]. |
| Overall family conclusion | **Convergence survives independent challenge.** Shared policy plus bounded language justifies the existing family even after B's weaker exclusion arguments are removed. |

## 6. Validation conditions and corrections to carry forward

These are conditions on trusting the selected family, not a rewritten implementation plan.

1. **Verify meanings, not just pattern matches.** Review numeric roles, units, dates, working-day conditions, signatures, required DDR parts and contextual Appendix G mappings. Unmatched or contradictory evidence must remain visible. Cover rare source/loss parts as well as common daily records. [CW p.27][cw]; [DDS pp.24, 35–36][dds].
2. **Keep policy uncertainty separate from missing facts.** Preserve competing readings where they affect outcomes; do not demote Schedule 8 using an incomplete document list or assume its contradictory rows are automatically decisive. Nor should a model or constraint solver invent the missing premise. [DDS pp.3, 27–28, 35–36][dds]; [guidelines, check 6][dg].
3. **Preserve historical distinctions.** Measured, claimed and currently payable quantities are different candidates for state. Check complete connected histories, exactly-once events, changes to earlier inputs, retrospective protection and later settlement. Include payment-history obligations even when they do not alter the judged total. [CW pp.6, 8, 14, 24–27, 32, 43][cw]; [DDS pp.7, 17, 35, 42][dds].
4. **Prove monetary consequences separately from detecting a breach.** Unknown value, temporary hold and contractual rejection are not interchangeable. Preserve the README's judged fields, native minor units, rounding order, and DDS discount/VAT recomputation. Do not restore the earlier plan's automatic zero contribution for every query or inflated confidence from correlated findings. [README, Data/Task/Calibration][readme]; [CW pp.8, 32][cw]; [DDS pp.6, 8, 35][dds]; Phase 2 audit B-P1/B-P2.
5. **Challenge systematic mistakes independently of the selected implementation.** Use source-derived expectations, blind record interpretation and complete-history reasoning that do not inherit the engine's answer. Review apparent passes and findings. Deliberately include conflicting clauses, amendment boundaries, repeated run facts, quantity tolerances and rare events. Self-generated tests and two readers sharing the same premise are not independent confirmation. [README, no labels and Calibration][readme]; [both guidelines][dg].
6. **Use diagnostics without turning them into labels.** Residual clusters can reveal one wrong rule; source-supported clusters may also be real. Billing agreement can conceal offsetting errors, omitted obligations or nonmonetary defects. Do not optimize to billed totals, use the 5–8% range as a quota, or call internal review organizer-labelled accuracy. [README][readme]; [guidelines, checks 1–12][cg].
7. **Preserve reproducibility and scope.** Pin sources, reviewed facts/decisions, dependencies and prompt versions; make their effects traceable. A model-assisted alternative must replay intermediate decisions into amounts, not merely store final answers. All twelve checks, all 2,806 rows and all five eventual deliverables remain required. [README, Task and Deliverables][readme]; [template][template].

These controls can expose systematic errors in the selected family because they challenge its inputs, rule meaning and historical consequences separately. They are not a guarantee that all errors will be found. The lack of labels limits claims of empirical accuracy and calibration under every candidate.

## 7. Final selection, readiness and time

**The existing solution family should be selected.** A materially different hybrid is unnecessary: assisted extraction, reviewed exception handling and independent LLM challenge already fit that family. Selective constraint analysis adds value where competing allocations are actually identified, without replacing ordinary valuation.

No unresolved selection-critical fact currently requires a discriminating experiment. The record inventory directly addresses the largest empirical uncertainty behind the choice. Remaining semantic, contractual and monetary verification is required under every family; it should not be repackaged as a demand to prototype several whole solutions. The recommendation remains revisable if later source-confirmed evidence shows pervasive semantic exceptions or coupled allocation ambiguity, but such evidence has not been established here.

**The family-selection gate is complete; individual rules and final outputs are not thereby approved.** Carry forward the Phase 2 audit's corrections and the conditions above. This report neither starts G0/G1 nor authorizes an automatic move into implementation. No solver, invoice classifications, final corrected totals or `submission.csv` were produced, and neither implementation plan was rewritten.

**Approximate time spent:** about 12 minutes of active work on the independent criteria, artifact review, corpus profiling, targeted source checks, comparison, writing and verification. Earlier phases are excluded.

[repo]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec
[readme]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/README.md
[cw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/contract/CW-2025-0417-CIV.pdf
[dds]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/contract/DDS-2025-118.pdf
[cg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/guidelines/INVOICE_AUDIT_GUIDELINES.md
[dg]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/guidelines/INVOICE_AUDIT_GUIDELINES.md
[cr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records
[dr]: https://github.com/majedzahrani3/invoice-auditing-level-2/tree/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records
[template]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/submission_template.csv
[ct]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records/CT-00002.txt
[pt1]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records/PT-00001.txt
[pt]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records/PT-00170.txt
[dx]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records/DX-00001.txt
[dw]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/civilwork/records/DW-00008.txt
[ddr]: https://github.com/majedzahrani3/invoice-auditing-level-2/blob/aef4924dc32506b4587de8b788b5a947e6beffec/drilling_services/records/DDR_NGP-BD-218_20251109.txt
