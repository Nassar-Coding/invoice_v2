# Phase 2.5 — Solution-family exploration

**Source:** `majedzahrani3/invoice-auditing-level-2` @ `aef4924dc32506b4587de8b788b5a947e6beffec` (local clone re-verified). **Inputs:** the Phase 2 Agent 2 audit (read first), `Phase2_plan_Agent1a.md`, `Phase2_plan_Agent1b.md`, `Phase2_TASKS_Agent1b.md`, and the Phase 1 audit. **Scope:** exploration only. No solver, parser, OCR, classification, totals or submission. `CW pN` / `DDS pN` are PDF pages, which equal the printed pages.

## 1. The challenge characteristics that drive the architecture

These facts come from the repository, not from the plans. They decide which families survive.

| # | Driver | Evidence | Architectural implication |
|---|---|---|---|
| D1 | **The contracts are images; the terms are finite.** 85 pages with no text layer, but roughly 100 priced codes, about 25 dated or monthly tables and 10 instruments. | PDF inspection (Phase 1); CW pp.17–27, 38–43; DDS pp.15–25, 37–42 | Extraction is a **one-time, bounded** job. It is worth heavy verification, not repeated re-reading at run time. |
| D2 | **The evidence vocabulary is closed.** The 2,169 civil records hold **26 distinct narrative templates** once digits are masked (CT 5, PR 5, JS 4, DX 3, DW 2, MO 2, PS 2, PT 2, CV 1). The 8,151 DDRs are key–value with **36 field keys, 5 crew terms and 15 tool terms**, every term defined in App G. | Read-only scan this phase (§12); DDS p36 | Semantic mapping can be **enumerated and reviewed completely**. There is no long tail of unseen wording for a model to interpret at run time. |
| D3 | **Correctness depends on exact arithmetic.** Two different rounding regimes (CW Cl.28 half-up once, with §26A/§29A half-even first; DDS Cl.17 half-even at every step), FX and index conversions, DS-900 above a threshold, VAT. | CW pp.6, 32; DDS pp.6, 8, 35 | The expected total must be **computed exactly to the minor unit**. Probabilistic generation of amounts is disqualifying. |
| D4 | **Heavy cross-invoice state.** Contract-year bands with splits, daily caps per work area, exclusion windows, once-per-well and once-per-run events, duplicates across invoices, and retrospective adjustments keyed to submission dates. | CW pp.6, 8, 24–26, 32, 43; DDS pp.7, 17, 22, 35, 42 | Decisions are **not invoice-local**. A family that reasons one invoice at a time needs an external global ledger anyway. |
| D5 | **Scale.** 2,806 invoices, 98,990 lines, 8.26 MB of records. | CSVs; byte count this phase | Trivial for local computation. Material for per-invoice LLM calls: every invoice would need the relevant contract context and a well's history. |
| D6 | **No labels.** Scoring rewards contract-supported amounts and calibrated confidence. A wrong shared rule "propagates silently". | README, Scoring and Calibration | Validation must come from **source-derived cases and independent re-derivation**. Every decision must be traceable to a clause and to evidence. |
| D7 | **Reproducibility and auditability are deliverables.** Clone, run, reproduce; versioned prompts; decision log. | README, Deliverables | Runtime nondeterminism is a direct cost against a required deliverable. |
| D8 | **Genuine interpretive questions are few and discrete.** About a dozen, e.g. A3 adjustment placement, Sch 8 conflicts, band basis, reuse allocation. | Phase 2 plans (1A Q1–Q11, 1B D-1–D-11); CW pp.32, 43; DDS pp.27–28, 35, 42 | Interpretation is needed **per clause, once**, not per invoice. It belongs in a reviewed decision register. |

## 2. The existing Phase 2 family

Both plans share one core solving model, beneath their different layouts.

**F1 — Contract-compiled valuation engine.** The contract is *compiled once* into verified structured terms. Records are *parsed once* into structured facts through a reviewed, closed vocabulary. A deterministic engine then **re-values every line from first principles**: entitlement, quantity, rate in force, build-up, rounding, state, and totals. Findings are emitted where the claim diverges, each tied to a clause and evidence.

* Billed values are claims to compare against. They are never the oracle.
* AI assists only at build time (transcription, proposing mappings, code), and every accepted output is frozen and reviewed.
* Validation comes from source-derived reference cases, boundary tests, independent re-derivation and residual review.

1A and 1B differ inside F1: consequence semantics, confidence aggregation, how precedence is argued. The Phase 2 audit ranks those; it does not test the family. That is this report's job.

## 3. Families considered

| Family | Core model | Status |
|---|---|---|
| **F1** Contract-compiled valuation engine | Compile terms and vocabulary once; deterministic full re-valuation plus global state | **Viable (preferred)** |
| **F2** LLM-as-auditor | For each invoice, an LLM (optionally with tools) reads the relevant contract text, records and history, then reasons to a verdict, category and expected total | **Viable only in a constrained role; rejected as the primary solver** |
| **F3** Billing-inferred rules / anomaly detection | Infer rates and rules from the majority of billed lines (the modal rate per item, month and factor), then flag outliers or train a scorer | **Rejected** as a solver; its useful part is already in F1 as a diagnostic |
| **F4** Declarative constraint / logic model (Datalog, SMT, rules engine) | Same knowledge as F1, expressed as constraints solved by an engine | **Superficial variant of F1** |
| **F5** Hybrid: F1 runtime + LLM at build and review time in bounded, verified roles | See §7 | **This is F1 done properly; not a separate runtime family** |

Why F2 is the only genuinely different credible family: it changes **where interpretation happens** (per invoice, at run time, by a model) and **how amounts are produced** (reasoned rather than computed). F3 changes the **source of truth** (the billing instead of the contract). F4 changes only the notation.

## 4. How each credible family handles the difficult parts

| Difficulty | F1 compiled engine | F2 LLM-as-auditor |
|---|---|---|
| Scanned contracts | Transcribe once with multimodal reading plus a second independent read (and OCR where available); adjudicate diffs; freeze with page cites | Re-reads scanned text or a transcription on every call. Without a frozen transcription, a misread varies from call to call; with one, it inherits F1's extraction step anyway |
| Clauses, supplements, amendments | Encoded as dated rate rows applied in issue order; overrides recorded clause by clause | Model reasons per invoice about precedence. Its readings can differ between invoices (inconsistency across the population) |
| Effective dates and retrospective adjustments | Five-date model (work, effective, issue, submission, adjustment); two valuations; exactly-once posting checked globally | The per-invoice view cannot see other invoices' submission dates without an external index. "First invoice on or after issue" is inherently global |
| Free-text records | 26 civil templates and the 5 + 15 DDR terms enumerated, mapped and reviewed once (D2) | Interprets each record freshly. That strength is unused here because the vocabulary is closed, and it adds mapping variance |
| Evidence → charge identification | Explicit joins, family/series, date/area/well/run checks, App G map; mismatch, reuse and duplication as distinct typed findings | Good at spotting semantic contradictions in one record. Weak at *systematically* separating mismatch, reuse and duplication across 99k lines |
| Invoice-local rules | Deterministic; every branch unit-tested | Plausible per invoice but unverifiable per rule; a missed rule in one prompt is silent |
| Cross-invoice state (bands, caps, spans, reuse) | Global ledgers with explicit keys, ordering (Cl.30), replay after corrections | Requires the same ledgers built outside the model. The model then adds nothing to the state computation |
| Once-per-run and once-per-well | Derived from DDR Part B and well spans (verified contiguous; 1,369 runs consistent) | Needs the whole well history in context: up to 51 days × about 45 lines |
| Bands, caps, discounts, exclusions, VAT, rounding | Exact `Decimal` with named rounding points; half-up vs half-even per contract | Unreliable at half-cent, half-halala and split-band arithmetic; must delegate to code, which is F1 |
| Contract-supported expected totals | Computed by construction: payable lines → DS-900 → VAT | Generated or delegated. Generation fails D3; delegation reduces F2 to F1 plus commentary |

## 5. Where LLM reasoning and deterministic processing belong

LLM reasoning genuinely adds value in these places, all **build-time or review-time**:
1. **Reading scanned pages.** No text layer exists and the OCR tool is unconfirmed. A multimodal read of 85 pages, done twice independently, is the practical extraction route; Phase 1 extraction reproduced billed rates widely, as a diagnostic.
2. **Clause interpretation drafting.** For the roughly 12 genuine questions (D8), a model can set out readings and point to discriminating cases. A reviewed decision register freezes the result.
3. **Proposing vocabulary mappings.** For the 26 civil templates and 20 DDR terms, a model proposes the mappings and a reviewer confirms them against App G and Sch 5.
4. **Independent adversarial re-derivation** of sampled invoices from the source pages alone, as a validation witness.

Deterministic computation belongs in: record parsing (closed templates), joins, state ledgers, rate selection, build-up, rounding, totals, and export. The reason is not that "less AI is safer" in the abstract. It is D2 (nothing left for a model to interpret), D3 (exact arithmetic), D4 (global state) and D7 (reproducible replay).

## 6. Uncertainty control and correctness without labels

| Concern | F1 | F2 |
|---|---|---|
| Transcription uncertainty | Controlled at one gate: two reads, diff, adjudication, frozen terms with page cites. The blast radius is known from a dependency index | Spread across calls and not isolated. A misread in one context window is invisible |
| Interpretation uncertainty | One registered reading per question; both readings run; flip sets recorded | Implicit and per call. The same clause can be read two ways on two invoices, which cannot be measured without re-running |
| Evidence and mapping uncertainty | Closed lexicon with 100 % coverage and a reviewed exception queue | Per-call; unmeasured |
| State and rounding uncertainty | Unit tests at thresholds, half-cases and boundary days; replay invariants | Not addressable inside the model |
| Catching a wrong rule before it propagates | The rule is enabled only after source-derived cases pass; residuals are grouped by rule, code, month and regime (a cluster means a shared misreading); a held-out review sample; mutation and invariant tests | Only by sampling outputs. A shared misreading in the prompt or context affects all calls alike and looks consistent, which is exactly the "silent propagation" the README warns about |
| Evidence that the answer is right | Traceable line computation, source-cited rules, independent re-derivation on a sample | Reasoning transcripts, which are plausible but not a verification of arithmetic or completeness |

## 7. Is a hybrid preferable?

Yes, but the only meaningful hybrid is **F1's runtime with bounded, verified LLM work at build and review time** (§5). The parts genuinely benefit from different mechanisms:
* **perception of scanned pages** → a multimodal model, with a second independent read, because the input has no text layer;
* **interpretation of ~12 clauses** → model-drafted readings plus a human-style decision register, because the input is natural language with conflicts, and a decision should be made once;
* **valuation and state** → deterministic code, because the task is exact, global and reproducible;
* **validation** → an independent model re-derivation as a witness that shares no code with the engine, catching errors a single pipeline would make consistently.

A *runtime* hybrid, calling an LLM per record or per line to map evidence, was considered and rejected. D2 shows the mapping space is closed (26 templates, 20 terms), so a runtime model would add variance and cost without covering anything the frozen lexicon does not. A runtime LLM as a *per-invoice second opinion* is rejected as a decision source for the same reasons as F2. As a sampled validation witness it is kept (above).

## 8. Strengths, risks, complexity and cost

| | F1 (+ build-time LLM) | F2 LLM-as-auditor |
|---|---|---|
| Key strengths | Exact, complete, consistent, replayable; every flag is clause- and evidence-traced; state is explicit | Fast to prototype; flexible on unanticipated wording; natural-language rationales |
| Systemic risks | One wrong extracted term or reading propagates consistently (mitigated by the gate, dependency index and residual clustering); rule-coverage gaps (mitigated by the 12-check coverage matrix) | Inconsistent readings across invoices; arithmetic error; missed global context; nondeterministic replay; confident but wrong rationales that are hard to audit |
| Implementation complexity | Moderate: about 100 codes, ~25 tables, 9 parsers + 1 DDR parser, ~10 state ledgers | Low to start, high to make trustworthy (it ends up needing F1's ledgers and calculator) |
| Inference / operational cost | Negligible at run time; the model is used once, over 85 pages and ~50 phrases | ~2,806 calls with large contexts (contract rules + records + history); repeated per iteration; model and version pinning required |
| Validation burden | Front-loaded (terms gate, reference cases) and then cheap to re-run | Continuous; every prompt change needs a full re-sample. No unit-level assurance |
| Likely time | Consistent with 1A's 20–30 h estimate (not measured) | Faster to a first answer; slower to a defensible one |
| Reproducibility | Byte-identical from a clone, with no credentials | Requires API access, a pinned model and cached responses; even with caching, the reasoning isn't re-derivable |

## 9. Direct comparison of the viable options

| Criterion (from §1 drivers) | F1 | F2 | Winner |
|---|---|---|---|
| D1 bounded extraction | Extract once, verify hard | Re-extract per call | F1 |
| D2 closed vocabulary | Fully enumerable; complete review | Flexibility unused | F1 |
| D3 exact amounts | Native | Must delegate | F1 |
| D4 global state | Native | Must delegate | F1 |
| D5 scale and cost | Trivial | Material | F1 |
| D6 validation without labels | Testable per rule | Sample-only | F1 |
| D7 reproducibility | Deterministic | Weak | F1 |
| D8 discrete interpretation | Register; decide once | Implicit, per call | F1 (using an LLM for drafting) |
| Handling genuinely novel text | Needs a parser update | Strong | F2, but no such text was found (D2) |

## 10. Rejected alternatives

* **F3 billing-inferred rules / anomaly scoring.** Rejected as a solver. It makes the billing the source of truth, which inverts the README's calibration principle and the carried-forward rule that the contract comes first. It cannot see errors that are consistent across invoices, or omissions: a discount omitted on every line in a period becomes "the mode". It cannot price retrospective adjustments or produce contract-supported totals. It has no labels to learn from. Its **useful kernel**, residual clustering of billed values against the contract-derived value, is already an F1 diagnostic (1B T2, 1A §10).
* **F4 declarative constraints / Datalog / SMT.** Same knowledge acquisition, same determinism and same validation as F1. The only difference is how the rules are written down, and the rules are mostly arithmetic with sequential state (Cl.30 ordering, splits, half-even steps), which suits imperative code at least as well. Discarded as an implementation variation.
* **Per-contract separate architectures.** Both contracts share the driver profile (D1–D8). Separate valuation functions inside F1 are a design detail, not a family.
* **End-to-end OCR plus a text-only LLM.** A variant of F2 with a weaker perception step (OCR on skewed, grainy scans), so it is dominated by F2's own multimodal read, and F2 is already rejected.
* **Supervised ML on synthetic self-labels.** Its labels would come from F1's own findings, so it is circular. It adds no information.
* **"More AI" or "less AI" framing.** Rejected per the brief. The placement in §5 follows D1–D8, not a preference.

## 11. Current judgment

**The existing Phase 2 family (F1) remains the natural choice because the credible alternative is weaker, provided F1 is run as the build-time hybrid of §7.** Among the options offered, that is "the existing approach remains the natural choice", with the qualifier that its LLM roles should be designed explicitly (perception, clause drafting, mapping proposals, independent witness) rather than treated as incidental assistance.

Evidence behind the judgment:
1. **The evidence vocabulary is closed.** 26 civil templates; 36 DDR keys, 5 crew and 15 tool terms, all in App G. This removes F2's main advantage.
2. **Exact, two-regime rounding and threshold/VAT arithmetic** (CW pp.6, 32; DDS pp.6, 8, 35) make generated amounts unacceptable. F2 must delegate them to code, collapsing into F1.
3. **Global state is pervasive** (bands with Cl.30 order, caps across applications, well and run spans, first invoice on or after issue), so a per-invoice reasoner needs F1's ledgers regardless.
4. **The README's warning about silent propagation** favours a family where a shared rule is a single inspectable artifact with tests, which is F1.
5. **The interpretive load is small and discrete** (≈12 questions), so it is best decided once and logged. Per-invoice reasoning would re-decide it inconsistently.

## 12. Evidence that could realistically change this judgment

| Finding | Where it would come from | Effect |
|---|---|---|
| **Open evidence vocabulary.** A material share of records (say >2 % of cited records) contain wording outside the 26 templates or 20 terms, or narratives that contradict the structured fields in ways that need judgment | G2 parser coverage run; the exception queue | Strengthens a **runtime LLM mapping component** (F1 + a runtime model for the exception queue only, with frozen, cached outputs) |
| **Extraction cannot be made reliable.** Two independent reads keep disagreeing on numeric cells, or the tables prove partly illegible | G1 transcription diff | Does not favour F2 (it would face the same pages). It would lower confidence and widen the decision register, and could favour asking for clarification |
| **Interpretive load is much larger than ~12.** E.g. many charges need case-by-case contractual judgment that no rule captures | G3/G5 unresolved-rule counts | Would move F1 toward an F2-style **reviewed per-case adjudication queue**, still with deterministic amounts |
| **Deterministic coverage fails in practice.** A large residual cluster that no source-grounded rule explains after review | G6 residual review | Would indicate a missing rule family. Re-read the contract first; F3-style inference only as a lead, never as truth |
| **An LLM witness systematically out-performs the engine** on the independent re-derivation sample (finding real errors the engine misses, confirmed from source) | Validation witness sample | Would justify promoting the LLM to a **runtime second-opinion channel** for flagged-candidate generation, with engine-computed amounts |
| **Reproducibility requirement relaxed**, or cached model outputs accepted as reproducible artifacts | Organiser clarification | Lowers F2's cost penalty but not its arithmetic or state disadvantages |

What would *not* change it: agreement or disagreement with billed values alone, or the flag count relative to 5–8 %.

## 13. Not confirmed, and where I looked

* **Template count as a closure proof.** 26 templates is exact for the *masked* narrative line. I did not verify that every template's numbers carry consistent units, or that no template is ambiguous between items (e.g. the two DX wordings for 2–4 m). Looked at: all 2,169 civil record bodies; DDR key lines, `Crew on tour` and `In the hole` / `Tools in run`. Part C/D/E free-value fields were counted as keys, not semantically reviewed.
* **Cost figures for F2** are structural estimates (calls × context), not measured.
* **OCR availability** is still untested (carried over from Phase 2).
* **The time estimates** reuse 1A's unmeasured 20–30 h estimate for F1.
* **Subagents were not used this phase.** The question did not divide naturally, and the previous phase's subagents stopped on a usage limit. All claims above were checked directly or are cited to earlier verified artifacts.
* **Output file name.** The brief names both `Phase2_5_solution_exploration_Agent3.md` (Output) and `..._Agent1b.md` (Done means). The report is written to the Agent3 name, with an identical copy at the Agent1b name.

## 14. Approximate time spent

About **25 minutes** of active work: reading the audit and plans, the vocabulary and corpus check, and writing.
