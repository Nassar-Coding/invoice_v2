# Phase 3 tasks — G0 and G1

Governing plan: `artifacts/phase_inputs/Phase2_plan.md` §§2–3, 8–9. Branch: `opus_stage2` only.
Boundary: stop at G1. No evidence-parsing layer beyond G0/G1 needs, valuation engine, cross-invoice state,
classification, flags, totals or `submission.csv`.

Legend: `[x]` closed with the evidence named; `[ ]` open; `[~]` closed with a recorded limitation.

## Setup
- [x] Create `opus_stage2` from the default branch `claude/pensive-wright-dgj33d` (commit 2bcfcaa).
- [x] Pin runtime: `requirements.txt` (Python 3.11; pymupdf, PyYAML, pytest, pillow).

## G0 — Freeze the inputs and audit specification
- [x] G0.1 Pin the source: `source/SNAPSHOT.md`, commit `aef4924d…`, HEAD re-checked.
- [x] G0.2 Hash every snapshot file (SHA-256 + git blob SHA-1) → `source/manifest.tsv`; check against the pinned git tree.
- [x] G0.3 Per-page identity of both scanned PDFs → `source/pdf_pages.json`; confirm the Phase 1/2 page images are pixel-identical to the scans.
- [x] G0.4 Inventory, schemas, ID sets, joins, template coverage → `source/inventory.json`; independent plan-number assertions in tests.
- [x] G0.5 Preserve the three Phase 1 artifacts (baseline report, supplementary report, independent Phase 1 audit) plus the governing plan and later audits, with hashes → `artifacts/phase_inputs/`.
- [x] G0.6 Source index (documents, pages, page hashes) → `spec/sources.yaml`.
- [x] G0.7 Contract-section ownership: every page of CW (43) and DDS (42) → owner rule/term/decision or explicit "non-operative" reason → `spec/sections_cw.yaml`, `spec/sections_dds.yaml`.
- [x] G0.8 Guideline-check ownership: 12 checks × 2 contracts → owning rules → `spec/guideline_checks.yaml`.
- [x] G0.9 Rule index with stable IDs → `spec/rules.yaml`.
- [x] G0.10 Ambiguity index → `spec/open_questions.yaml` (Q1–Q11 plus any new items).
- [x] G0.11 Independent-audit corrections register: Phase 1 A1–A2, B1–B5, §6 1–8; Phase 2 B-P1–B-P6, §6 1–8; Phase 2.5 B-1–B-5, §6 1–7 → `spec/corrections.yaml`.
- [x] G0.12 `tools/verify_spec.py` structural checks + tests; run; commit and push.

## G1 — Verify contractual terms and consequences
- [x] G1.1 Extract page images reproducibly from the PDFs (`tools/extract_pages.py`), hash-checked against `source/pdf_pages.json`.
- [x] G1.2 CW terms file `spec/terms_cw.yaml`: Sch 1 (60 items), zones/areas, index + FX, ground list, night/rest lists, 8 band schedules, 9 daily caps, exclusions, surveyed items, 17 record-required codes, rounding, financial rules, pp.28–31 coverage inventory.
- [x] G1.3 DDS terms file `spec/terms_dds.yaml`: Sch 1 (38 + DS-900), depth/annual bands, index/FX/SAR values, factor/standby/cap/once-only lists, Sch 5 parts, App G glossary, rounding, financial rules.
- [x] G1.4 Instruments register `spec/instruments.yaml`: CW S1/A1/S2/A2/A3, DDS S1/A1/S2/A2/A3 with issue/effective/row dates, changed fields, relationships, carry-forward, pages.
- [x] G1.5 Independent readings: tesseract OCR of all 85 pages + blind subagent transcription (CW 24, DDS 24 table pages) → `verification/ocr/`, `verification/blind/`, `verification/reading_comparison.json` (blind 544/547 numeric, 1025/1047 text cells agree; every residual settled on the scan).
- [x] G1.6 Second visual verification (0 numeric discrepancies; 37 wording/structure fixes, all non-numeric) of every active numeric table against the scan images; per-table log with reviewer notes → `verification/second_pass_log.yaml`.
- [x] G1.7 Internal-consistency checks (previous-rate chains, Sch 2D = Sch 6 × 3.75, extension arithmetic, App B / App F worked examples, discount example).
- [x] G1.8 Overrides register `spec/overrides.yaml` (explicit second-series replacements, instrument supersessions, stale cross-references).
- [x] G1.9 Consequence table `spec/consequences.yaml` (full rejection / correction / conditional payment / procedural / payment-only / unknown).
- [~] G1.10 Open questions (all 12 stay OPEN by design with bounded alternatives; they block G3-G7, not G1; new Q12 challenges plan §6) with bounded alternatives and affected scopes computed from the data → `spec/open_questions.yaml`, `tools/question_scopes.py`.
- [x] G1.11 Pricing gate: every table carries `verification.status`; `verify_spec.py` fails if any table referenced by an active pricing rule is not `verified`.
- [x] G1.12 Tests pass; commit and push.

## Close
- [x] Run every check and the full test suite on a clean checkout (clone of bf40eb8): snapshot OK, 9 PASS, 36 passed.
- [x] Write `Phase3_G0_G1.md`; commit and push to `opus_stage2`.

## G2 — Load claims and extract evidence (from gate1 @ bf40eb8; main @ d76e8a2)
Exit (plan §2): every source row/file is accounted for; each required field is parsed or explicitly unresolved;
reference validity and semantic validity are separate; reviewed examples cover every record family and
encountered wording/layout branch. Boundary: no pricing, entitlement, cross-invoice state, flags, totals or submission.
- [x] G2.1 Evidence-mapping specification `spec/evidence_cw.yaml`, `spec/evidence_dds.yaml` (record wording → meaning, unit, candidate items, source). — 992cd6c
- [x] G2.2 Claims loader with provenance and original strings; exact Decimal from strings; blank ≠ zero; input assertions (uniqueness, joins, template coverage). — 992cd6c (101,796 rows, file/line/raw kept)
- [x] G2.3 Civil record parser: 9 families, weekly day lists across month/year, placeholder signatures, narrative templates. — 992cd6c (2,169 records, 26 templates)
- [x] G2.4 DDR parser: header, Parts A–E, Appendix G terms (loss context), crew, signatures; index by internal report number. — 992cd6c (8,151 reports keyed by report number)
- [x] G2.5 Events from records only: BHA runs (repeated Part B metadata = one fact), source runs, losses, DW weeks; intra-record and run consistency conflicts kept visible. — 992cd6c, 75926d0 (1,369 runs; loss hours corroborated against daily history)
- [x] G2.6 Links: reference validity kept separate from semantic facts; accounting of every file (linked / unreferenced). — 992cd6c (0 unreferenced record files)
- [x] G2.7 Unresolved queue (never default); negative controls prove it fires. — `tests/test_g2_controls.py`
- [x] G2.8 Reviewed fixtures typed from raw text covering every family and wording/layout branch; blind subagent annotation of a seeded sample compared field by field. — `tests/fixtures/g2_reviewed.yaml`; blind 646/646 civil, 1029/1029 DDR fields
- [x] G2.9 `tools/verify_g2.py` exit checks; tests; G0/G1 checks still pass; report `Phase3_G2.md`; gate2 tag text. — 95 passed; G0/G1 SPEC VERIFY OK; G2 VERIFY OK (E1–E4, S1, S2)

## Correction round — G1/G2 re-close (independent G0–G2 audit of 76e9518: G0 PASS, G1/G2 NOT PASS)
Governing: the audit (Phase0-1-2-audit.docx) and plan §2 exit conditions. Boundary: no G3 work; tags gate0/gate1/gate2 untouched.
- [x] C1 (finding 1, G1) Second verification of every active parameter (33) and operative rule (46) against the scans, DDS pp.9–14 included, with attributable evidence; content hashes for parameters and rules so any edit invalidates verification; controls: vat_pct 15→16 and an edited rule fail. — 79/79 items second-read (readers A–F; 17 corrected items re-read by G, H); 12 sections / 139 provisions on the pages never re-read; verify_spec checks hashes; controls fail as intended.
- [x] C2 (finding 2, G2) DD-121 = rotary steerable Standby charge in place of DD-120 (Cl.21 p6; Sch 3 Part 4 p21): fix `link_dds()`, regenerate outputs; per-code population check of tool-in-hole false shares with cited explanations; control: reintroduced defect fails. — 245/245 DD-121 lines now show the rotary steerable present (basis DD-120); population check S3; DD-102 null (Q5, cited); RM-511 3/806 genuine absences.
- [x] C3 (finding 3, G2) Independent semantic review of derived meanings (tool term→code, service-keyed crew counts, invoice-to-tool, civil numbers by attribute name); sample completeness enforced; controls: wrong tool code, wrong crew count, mislabelled civil number, missing sample fail. — S4: ddr 583/583, lines 482/482, civil 161/161 fields by name, 160/160 sampled items; controls in tests/test_g2_semantic.py; link branches now include tool/crew/part/LH outcomes (118/118).
- [x] C4 (finding 4, G2) Run/version context over parser/link code and reviewed inputs, referenced by every derived fact (code-only change changes it); register of carried conflicts with owning gate and treatment; Q11 corrected to the records-based depth bound. — every one of 212,717 facts carries the run context; spec/carried_items.yaml CI-01..03 (G3); Q11 bound 6,026 m (NGP-BD-027); S5 + tests/test_g2_provenance.py.
- [x] C5 Report `Phase3_G1_G2_corrections.md`; all G0/G1/G2 checks and tests in a fresh clone at the final commit; annotation text for gate1-r1 and gate2-r1. — report written; fresh-clone re-run at the final commit reported with the tag text.

## G3 — Local entitlement and pricing (from gate1-r1/gate2-r1 @ 8745f9c)
Exit (plan §2): independently calculated clause-based cases pass, including exceptions and boundaries; all billed code
families are implemented or explicitly marked unresolved; each amount has an explainable calculation trace.
Binding: re-audit carry-forward safeguards (Phase3_G1_G2_reaudit_Agent2.md). Boundary: no G4 state (bands, caps,
exclusions, duplicates, run/well lifecycles), no classification, flags, final totals or submission.csv.
- [x] G3.1 Reference cases written BEFORE pricing code: 55 civil + 56 drilling synthetic boundary/exception cases and 42 real lines (inputs only); six independent readers compute expected values from the scans. — dd73ad9 (inputs committed before any pricing code); 153 cases, six readers' outputs in verification/g3/cases/expected_*.jsonl.
- [x] G3.2 Terms access and pricing engines per contract (rate version by work date and issue order, retrospective protection, FX, indexation, build-up, rounding), each amount with a replayable trace. — audit/terms.py, g3_core.py, g3_cw.py, g3_dds.py (b19d242); every amount carries a trace (X3 replays it).
- [x] G3.3 Local line checks per contract: identity/period, term, submission window, evidence and signatures, unit, identification, quantities (first hour, 2%/1% tolerances, 5-day weeks, minimum), rate, arithmetic; amount status and explicit G4 dependencies. — CW 7,746 and DDS 91,244 lines evaluated (verification/g3/summary.json); 738 case comparisons agree or are disposed (G3-D1/D2).
- [x] G3.4 Questions Q3, Q4, Q5, Q8, Q11, Q13 and carried items CI-01..03: decided with a discriminating case or kept open with alternatives and lines affected under each; G2 loss-hours corroboration corrected; stale check for missing-part items; G1 recorder path portability. — spec/g3_decisions.yaml + verification/g3/decision_scopes.json: Q3, Q5, Q8, Q13 decided; Q11 decided in part (wrong-unit remedy open, 0 lines); Q4 kept open (7 lines carry alternatives, owner G5); CI-01 resolved (Part E = tool history 54/54), CI-02/03 decided under Q3 A; stale check and recorder portability tested.
- [x] G3.5 Code-family coverage: every billed code implemented or explicitly unresolved with owner. — spec/g3_code_families.yaml: 6 civil + 12 drilling families from the verified tables; every billed code (60 civil, 39 drilling) in one family; DS-900 deferred (G5); no unresolved line; X2 checks family, value/reason and pricing tables per line.
- [x] G3.6 tools/verify_g3.py exit checks, each with a negative control that fails; all G0-G3 checks and tests; report Phase3_G3.md; fresh-clone run; gate3 tag text. — X1-X7 pass with 29 negative controls (tests/test_g3_gate.py); check_g3.sh: SPEC VERIFY OK, 159 tests, G2 VERIFY OK, G3 VERIFY OK; report Phase3_G3.md; fresh-clone run at the final commit and the gate3 text given in the conversation.

## G3 correction round — independent audit Phase3_G3_audit_Agent2.md (G3 NOT PASS at c7abc4b)
Closure evidence required (audit §8): F1/F2 supported authority or explicit conditional outcomes, false claim classes
cannot silently set value; F3 split and non-split counterexamples without doing G4 early; F4 PD-210 reconciled with
the two reproduced failures rejected; Q5 residual reconciled or kept with scope and owner; regenerated outputs with
D1's value/payment distinction, Q13 and currency separation preserved.
- [x] R1 F1 well class: class-rated services priced under every class (Cl.4; P2, P3); header disclosed, owner G5; PD-210 nomination stays conditional; MDS-00001-008 counterexample; controls (X2 completeness, X6 claim perturbation). — MDS-00001-008 identical under any header; 24,217 class-rated lines conditional (owner G5); controls X2/X6.
- [x] R2 F2 ground class: record / 27A / every class with S4's G2 disclosed; PA-00031-06 counterexample; exposure 650/521; controls. — PA-00031-06 identical under any claimed class; 650 lines (649 conditional); controls X2/X6.
- [x] R3 F3 band arithmetic: Cl.28 division at contract band rates -> unresolved, else finding; PA-00076-08 and counterparts; prompt v3. — PA-00076-08 unresolved (207 x 34.56 + 51 x 32.83); 29 unresolved / 3 findings; CW-S62/S63/R22; control.
- [x] R4 F4 PD-210: allowed metres = parts = amount under 25A; crossing ambiguity exposed; X3 part rates/depths/quantities; controls 999.00 and quantity mismatch. — 101 m -> 5,873.15 with parts = allowed; controls 999.00 and 100-vs-101 rejected; crossing charge exposed.
- [x] R5 Q5 residual: DD-120/RM-530 hours and HC-630 computed under every reading; Cl.2 list gap recorded (D8); owners G5/G4. — 3 lines carry alternatives; HC-630 once-per-run G4 dependency on 428 lines; D8 registered.
- [x] R6 X6 perturbs claim classifications; D1 value/payment; SAR/USD separated; Q11 blocks G5; G3-D3 zone/night disclosed. — X6b passes on 98,990 lines; scopes SAR/USD; Q11 blocks G5; G3-D1 value_vs_payment; G3-D3 scoped.
- [x] R7 Independent v3 readers (new cases + 24 re-reads), scan check, all checks and tests, report Phase3_G3_corrections.md, fresh clone, gate3-r1 text. — 4 v3 readers: 180 cases, 837 comparisons, 801 agree, 36 disposed (unchanged), 0 failing; check_g3.sh OK; report Phase3_G3_corrections.md; fresh clone and gate3-r1 text in the conversation.

## G3 correction round 2 — re-audit Phase3_G3_reaudit_Agent2.md (G3 NOT PASS at 83c4a61 / gate3-r1: F1, F3 closed; F2, F4 partial)
Closure evidence required: B1 a record settles the ground class only if it applies to the work (same date, area, item
basis) for every record; probe PA-00031-06 + DX-00007 not determined; a positive case; X2 and X6 reject an unrelated
record. B2 the complete admissible PD-210 allocation domain on crossing charges (all allocations, or bounds with the
intermediate values unresolved and owned); known allowed quantity kept; never an empty payable result; 98 m and 40 m
cases; X3 checks completeness; 999.00 and quantity-mismatch controls kept. D8 recorded as an interpretation with the
broader Schedule 8 reading live and weighted; Q5 residual kept; report line identities corrected. No G4.
- [x] S1 B1 ground authority: record applicability (day/week, area, item basis) for every record; X2 independent predicate (both sides); X6 cites an unrelated record on no-record ground items; cases CW-S64..S68, R24 (probe), R25. — probe conditional G1-G5 (was 85.41 determined); CW-S64 determined G3; controls: any-record engine rejected by X2 and X6, record-ignoring engine rejected by X2; population unchanged (1aef89d).
- [x] S2 B2 PD-210 domain: every allocation (<= 25) or lowest/highest with the whole domain on the owned condition; guard against empty payable results; X3 completeness (inclusion-exclusion count, vertex extremes); cases DDS-S72..S76. — 98 m: 48+50, 49+49, 50+48; 40 m: 41 ways, 1,694.00..2,326.00; controls incl. the round-1 engine and the 999.00 / quantity mismatch (b7482b1).
- [x] S3 D8: operability settled; scope of 'A Schedule prevails over a Part' = interpretation D8-I1 (broader reading weighted greater, narrower lesser; owner G5); Q5 basis and engine condition text; X4 interpretation check; report identities corrected with a pairing test. — X4 controls; the round-1 report text fails the identity test (bfb1257).
- [x] S4 Falsification of branches no case exercised: DDS Cl.17 cents on decimal metres (found by the reader on DDS-S76); report-measured depths bound the PD-210 domain (c45c0be); only the Engineer's countersigned record settles the ground class (f38aa38). Each with a control.
- [x] S5 Independent v4 readers (12 cases, before the fixes were final), scan check of their figures, dispositions (9 comparisons), all checks and tests, report Phase3_G3_corrections_r2.md, fresh clone, gate3-r2 text. — 192 cases, 903 comparisons, 858 agree, 45 disposed, 0 failing; check_g3.sh OK in a fresh clone of 51cd4a4 (240 tests; X1-X7 PASS; 3m35s); re-run at the final SHA, given with the gate3-r2 text in the conversation.

## G3 correction round 3 — re-audit Phase3_G3_reaudit_r2_Agent2.md (G3 NOT PASS at 3c308ab / gate3-r2: B1, B2, D8/Q5 closed; PD-210 blank-depth crash open)
Closure evidence required (§6): a PD-210 charge with a missing start, end or both depths returns an explicit missing-depth
finding and an unresolved local result with provenance, reason and owner, keeps independently known facts and lets the
batch carry on; never the interval guessed from the report, never zero; shown through the typed G2 handoff and the batch;
the old unguarded engine fails those controls. Plus (goal): every field G2 can leave None or unresolved, in every civil and
drilling code family, swept through the engines and the batch - explicit result, never an exception or a silent default -
as a permanent X-check the old engine fails. No G4.
- [x] T1 PD-210 missing depths: depths_missing finding (Cl.34) per missing depth with its source line; value unresolved (owner G5, reason); facts that hold for every interval inside the report's kept (day's metres, bands, a charge above the day, a single-band rate); G2 provenance handed to G3 (Inputs); batch contains any line error as an explicit engine_error that X3 rejects. — DDS-S72 packet start-only / end-only / both; MDS-00018-023/-039/-054 blanked in a snapshot copy through the real G2 loader and g3_dds.run (other 91,241 lines unchanged); MDS-00018-023 start None in memory in the population batch; the gate3-r2 engine raises TypeError on all of them.
- [x] T2 Nullable-field sweep: every G2 field (claims columns, record and report keys, whole parts, part headings, keys written twice, unrecognised list entries) x every code family through both engines and the batch; crashes and silent defaults fixed; X8 check; the gate3-r2 engine fails it. — X8 (tools/null_sweep.py): 9,396 input states on all 18 families + 195 batch runs, 0 failures (1,749 unresolved and named, 141 not payable by the contract's rule, 9 carrying every value, 7,497 unchanged); the gate3-r2 engine: 23 inputs crash (938 cases), 47 handled silently or by default (1,443), 27 batch runs fail; controls for each X8 criterion; falsification: 39,056 pairwise/all-empty evaluations and a population-wide fuzz (98,990 lines, 10,320 documents) without an error; population values unchanged.
- [x] T2b Falsification of fix 2 (found after 1e62a6a by trying to break it; all fixed in ed7ba60 and b3a39e4): the output stage (g3_run) crashed on an empty quantity (TypeError, Q3 reading B), a blank line reference (KeyError), a shared one (KeyError) and an unresolved re-priced zone line (ValueError); lines with no value at G3 were valued as 0 or left out (Q3 reading B dropped 3 conditional-rate civil lines: SAR 213,426.16 -> 258,170.41-282,470.38; 63 DS-900 lines counted as 'rate not single'); two lines sharing a line_ref replaced each other's result and provenance in the batch; a Report number carried by two files was resolved by G2's first-file default, and a header number carried by two rows by the last row; a twice-written foreman line hid a missing countersignature; an empty or unscheduled civil code, and an unscheduled drilling code, hid an established out-of-term; X8 itself: sample did not reach the decision scopes, its line_ref run did not empty line_ref, the code probe met only the unit rule, date probes lacked the document's own date, a not-payable line's rate counted as value. — X8 widened (output stage over every batch run, line_ref emptied and shared, repeated Report and header numbers, coverage of every claim field x family): 12,230 input states, 200 batch runs, 0 failures; the gate3-r2 engines fail it with 3,212 errors, the gate3-r2 output stage with exceptions; controls for each new criterion; 49,032 pairwise/all-empty evaluations and the population fuzz (98,990 lines; identity states) without an error; population values unchanged (new: each result's rate domain).
- [x] T3 Regression (B1, B2, F1-F4), falsification, report Phase3_G3_corrections_r3.md, fresh clone, gate3-r3 text. — B1/B2/D8 (tests/test_g3_corrections_r2.py, 59 tests) and F1-F4/Q5/D1/X4 (tests/test_g3_corrections.py, 22) pass; population against gate3-r2: values identical on 98,990 lines (new rate domain; 41 details reworded); cases 192/903, 858 agree, 45 disposed, 0 failing; report written; check_g3.sh passes locally at b3a39e4 (272 tests, X1-X8). Found at the close: the case-path control of T1 passed for the wrong reason (the harness passed `inputs` to the gate3-r2 engine, which rejects the argument) - harness fixed, the three exception controls now require their exact errors. Fresh clone of cdcd355: check_g3.sh passed (G0, G1, G2, 272 tests, 192 cases, X1-X8) in 605 s; the tick commit only changes this list and the report's wording, and is re-run at the final SHA (conversation).

## G3 correction round 4 — final discovery audit Phase3_G3_final_discovery_audit_Agent2.md (G3 NOT PASS at 6885224 / gate3-r3; frozen blockers FD01-FD08)
Closure evidence required: each FD's "Required closure" paragraph (audit §3), every demonstrated variant, the audit's
reproduction handled correctly, a negative control on the gate3-r3 code, what the evidence does not establish; all G0-G3
checks and tests in a fresh clone. No G4.
- [x] FD01 Signatures: signed / unsigned / unknown kept distinct in both G2 parsers (common.signature_state); unknown text is queued and never approval; G3 (both contracts, both signatory roles, ground authority) takes unsigned as the contract's consequence and unknown as unresolved. — tests/test_g3_corrections_r4.py (6 unreadable x 7 non-signing tokens x 2 roles x 2 contracts; CW-S64 ground authority); control: the gate3-r3 parser and engine keep MDS-00001-013 USD 4,892.30 and PA-00001-04 SAR 17,730.62 on '??'. Population values unchanged (34 unsigned details reworded).
- [x] FD02 Repeated evidence: both parsers collect every occurrence, then resolve - an identical repetition (header key, signature, Part key, whole Part, narrative) is read once, a differing one is queued 'key repeated' (and 'part repeated with different content') with no value taken by position; derived tools/crew/lost tool computed once from resolved values. — tests: conflicting Date/Report/Well and signatures in both orders (unresolved), identical repeats (value unchanged, no queue), the audit's MDS-00001-010 (1 hand: USD 1,847.35 with quantity_above_report, same when Part A repeated identically; unresolved when a copy differs, either order); civil key in both orders. Control: gate3-r3 keeps USD 4,892.30 on a prepended conflicting date and on unsigned-then-named, and doubles the crew (qty 2, USD 3,694.70, no finding). Population identical.
- [x] FD03 Civil item-defining attributes: spec/evidence_cw.yaml templates carry the Schedule 1 value each captured attribute must have (PT1 dia 1800, PT2 dia 400, PR1-PR5 mix 32/40, JS1 mesh A393, CT4 Type 1); a record stating another value evidences no candidate (item_not_supported_by_record naming the attribute, never repriced as another item); an unreadable value leaves the narrative unmatched (queued, unresolved). — tests: matching / different / unreadable for each role on the audit's five lines; all five PR forms x three grades. Control: gate3-r3 keeps each changed specification's candidate and value. Population identical.
- [x] FD04 Required-Part contents and certification: for a Schedule 5 service every content line of its Part (spec/evidence_dds.yaml, Sch 5 p24) is checked whether or not its price uses it - missing, unreadable (G2 now queues word-less text such as 'Sources handled: ??') or conflicting leaves the charge unresolved (owner G5); 'Source handling certified: No' is a known failure: not payable, source_handling_not_certified (Cl.37, H6). Unrelated services on the same report are untouched. — tests: all 12 Schedule 5 codes x every content line of their Part, missing and '??' (the audit's LW-420 No/??/blank/removed, DD-111 Run circulating hours, LW-410 Run last day included); control: gate3-r3 keeps USD 2,746.55 / 3,589.45 and LW-410's valuation. Population identical.
- [x] FD05 Night work: G2 types night_work as Y or N only (claims.yes_no); any other text is queued and handed over as None; G3 treats anything but Y/N as unknown - the uplift is priced both ways and the line is unresolved (naming night_work) where that changes the rate; where it cannot (item without an uplift, zone factor above 1.10 under 27A) the value stays determined. — raw CSV -> G2 loader -> G3 batch on a snapshot copy ('??', 'yes', '1', 'n', blank on uplift-eligible lines; '??'/blank on irrelevant ones); control: the gate3-r3 loader keeps '??' unqueued and the engine prices PA-00001-04 as daytime (SAR 17,730.62). Population identical.
- [x] FD06 DDS arithmetic: the billed amount is compared with quantity x rate ascertained in cents, half to even (Cl.17, Cl.18) - the rounding the valuation trace uses; the exact product billed to a fraction of a cent (case DDS-S76) is right multiplication, not a finding (its cent value is recorded). Civil keeps its exact comparison (no amount rounding rule in the civil contract; Cl.28 rounds the rate). — tests: half-cent ties rounding up to even (152.5 m -> 8,867.88) and down to even (152.3 m -> 8,856.24), an exact product, a non-tie (152.33 m), and a wrong cent for each; the nomination condition is kept. Control: gate3-r3 flags 8,867.88 and 8,856.24. Population: findings identical (details reworded).
- [x] FD07 Allocation granularity: civil - the unknown cumulative quantity (G4) may start anywhere, so the admissible amounts of a division at the band edges form the range [lowest, highest] over every start (piecewise linear, breakpoints where an edge meets either end); an amount inside it is unresolved with the range stated and no division selected, outside it a finding; drilling - pd210_step (and X3's independent grid) use the values' finest decimal place, never the spelling; the listed extremes bound every allocation at any resolution (linear in the metres placed, Cl.23). — tests: PA-00008-06 at 384 / 384.0 / 384.00 with amounts inside and outside the range; the independent 100.4/283.6 division; DDS-S72 at 98 / 98.0 / 98.00 (one domain: 1 m, 3 allocations, USD 4,908.70-4,940.30) and 98.5 / 98.50 (0.1 m, bounds computed by hand); X3 on each. Control: gate3-r3 gives 384 a finding and 384.0 unresolved, and steps 1 / 0.1 / 0.01. Population: statuses identical (29 unresolved details reworded; test_f3 updated to require the range instead of a selected division).
- [x] FD08 Missing submission date: terms.submission_regimes() - one representative submission per regime (the day before each retrospective issue date, and after every issue; G3-D1 admits early submissions) - replaces the two probes; where the regimes give different rates the line is unresolved (the date named) and carries the a3_adjustment dependency; a rate-unaffected service stays determined. Both contracts. — tests: service after issue, inside the retrospective window, and unaffected, each with submission before / on / after the issue day and missing (MDS-01650-048, MDS-01092-036, MDS-01650-039; PA-00041-01, PA-00003-06, PA-00005-03, PA-00015-04); the raw CSV loader with the date blank on MDS-01650-048's invoice and PA-00015-04's application. Control: gate3-r3 fixes MDS-01650-048 at USD 3,634.44 and PA-00041-01 at SAR 10,951.68 without the dependency. Population identical.
- [x] X8 source-derived evidence obligations: tools/null_sweep.obligations() takes each line's conditions of payment from the specs (Sch 5 Part content, Part, heading, signatures; civil Schedule 5 record lines, narrative, title, signatures); an obligated input emptied, unreadable or conflicting must leave a payable line unresolved or apply the contract's consequence, and 'nothing lost' applies only to inputs without an obligation. — X8 0 failures; control: the gate3-r3 engines fail it with ignored obligations (B.Run circulating hours, D.Sources handled ...).
- [x] Close: report Phase3_G3_corrections_r4.md; fresh clone of 7166d09: check_g3.sh passed (G0, G1, G2, 469 tests, 192 cases 0 failing, X1-X8) in 956 s; this tick commit changes only this list and is re-run at the final SHA (conversation).

## G4 — Chronology and shared state (from gate3-r5 @ 1a14df1; G3 independently closed and G4 authorized by artifacts/phase_inputs/Phase3_G3_FD07_recheck.md)
Exit (plan §2): small multi-invoice histories agree with independent expected events and amounts; ordering, reset,
allocation and replay tests pass; no duplicate event or adjustment is counted twice. Scope (plan §§2, 6, 7): bands,
caps, exclusions, duplicates, run/well events, retrospective (A3) adjustments and retention history, and every item a
register assigns to G4 (Q1, Q6, Q7, Q12; Q5 residual HC-630 once per run; carried-item once-per-run count; G3 line
dependencies: CW band_state 1,026 / daily_limit 1,183 / exclusion 229 / p23_link 9 / a3_adjustment 89 / duplicate
scope; DDS daily_limit 79,579 / a3_adjustment 3,309 / once_per_run 1,451 / once_per_well 859 / duplicate scope).
Input boundary: closed G0-G3 behaviour (G3 line results are consumed, never changed). Boundary: no G5 (invoice
outcomes, flags, categories, confidence, totals, submission.csv), no G6/G7, no tag moves.
- [x] G4.0 Inventory and preflight: clean tree, main = origin/main = gate3-r5 (1a14df1); G3 recheck preserved; source pages reread (CW pp.3-4, 6, 8, 12-14, 20, 24-26, 32-34, 38, 43; DDS pp.3, 6-8, 11, 14, 17, 21-22, 24, 27-29, 35, 37, 42); population facts for every state family.
- [x] G4.1 Multi-invoice history packets (inputs only) committed before any G4 code; independent readers compute expected events and amounts from the contract scans.
- [x] G4.2 State specification and decisions: spec/g4_state.yaml (keys, clocks, ordering, quantity basis, consequence per family); spec/g4_decisions.yaml (Q1, Q6, Q7, Q12 closed or kept with alternatives and scopes).
- [x] G4.3 Civil state engine: annual bands per item and Contract Year, daily limits per item/work area/day, exclusions, duplicate measurement, P23 links, A3 adjustment account and recipient, 45A retention history.
- [x] G4.4 Drilling state engine: daily limits per well-day (D6), Cl.29 duplicates incl. PD-210 intervals, once-per-run and once-per-well events, annual footage per well and Contract Year, loss once, A3 adjustment account and recipient.
- [x] G4.5 tools/verify_g4.py exit checks (histories, ordering, reset, allocation, replay, exactly-once, traces, reproduction, registers), each with a negative control that fails; tests.
  - Done so far: 24 histories (19 synthetic, 5 population slices), 6 isolated readers (91e785e packets -> 3b4e4fd readers -> b758791 engines); 59 disagreements all settled (verification/g4/history_dispositions.yaml), 5 engine defects fixed from them (HC-630 per run, exclusion day 0 kept open as Q6 D, finding status under partial readings, charged_twice/well_event_repeated codes, collapse of non-product label sets). Registers: Q1, Q6, Q12 kept open (blocks G5), Q7 decided in part, Q14 new; spec/g4_decisions.yaml G4-D1..D15, spec/g4_state.yaml. verify_g4 Y1-Y9 PASS on the population; tests/test_g4_gate.py (40 negative controls) and tests/test_g4_falsification.py (8 constructed histories) pass. Falsification fixed: same-day duplicate ties counted in the band ledger (now exactly once, as a range), a >6 same-date group given the convention order silently (now unresolved), rejected lines multiplying the orders.
- [ ] G4.6 Falsification of ordering, resets, replay, duplicates and cross-invoice interactions (incl. branches no case exercises); population regression against gate3-r5 with every consequential change explained; no G5-G7 code in the diff.
- [ ] G4.7 Report Phase3_G4.md; all G0-G4 checks and tests in a fresh clone of the final commit; gate4 SHA and annotation text.

## G5 — Full invoice outcomes (from gate4 = 9fa5514; G4 closed in Phase3_G4.md)
Exit (plan §2): every invoice has check coverage, findings, amount status and an evidence trail; monetary and procedural
outcomes remain distinct; independently reviewed complete invoices reconcile step by step. Scope: one outcome per
template invoice (flag, category, expected total, confidence) from G3 lines and G4 state; DS-900, VAT, retention;
Q9 closed first; owner decisions Q7 C (earlier invoice stands) and Q6 D (both readings, ambiguity rule); every other
G5-owned item decided from source or resolved by the ambiguity rule. Boundary: submission.csv only as G5's output
artifact; no G6/G7; no tag moves.
- [x] G5.0 Preflight (clean, main = origin/main = gate4 9fa5514); README, template, plan §§8, 11; header arithmetic profile.
- [x] G5.1 Q9 rule and decisions: spec/g5_decisions.yaml (Q9-1..6; Q1, Q2, Q4, Q5, D8-I1, Q6 A/B/D, Q7 C, Q8 class/ground/nomination, Q10, Q11, Q12, Q14, G3-D1..D3, totals, retention).
- [x] G5.2 Independent expected outcomes: sample packets (inputs only) and reader prompt committed before any G5 code; isolated readers compute outcomes from contracts and records.
- [x] G5.3 Outcome engine (audit/g5_*.py): per invoice checks coverage, findings, scenarios, flag, category, expected total, confidence; submission.csv; effects per alternative.
- [x] G5.4 tools/verify_g5.py exit checks, each with a negative control; falsification; regression vs gate4.
- [x] G5.5 Phase3_G5.md; all G0-G5 checks in a fresh clone; gate5 SHA and annotation.
  - Done: 2,806 outcomes (CW 88 / 900 flagged, DDS 125 / 1,906); 25 sampled invoices, 8 isolated readers, 48/50 agree, 2 settled; verify_g5 Z1-Z9 PASS; 20 negative controls, 10 falsification invoices; fixes: bill-dependent expected total on reading-disagreement invoices (Z4), check 6 coverage, Q9-4, category attribution, Q7 C same-day tie, g5_decisions YAML. Report: Phase3_G5.md.

## G4/G5 correction round — audit Phase3_G4_G5_audit_Agent2.md (G4 NOT PASS at gate4 9fa5514; G5 NOT PASS at gate5 13eb768; ten frozen blockers)
Order: the G4 blockers first, then G5 regenerated from the corrected G4 before any G5 fix (G5 results on old G4 state are
not evidence). Q12 and the 9.8% civil rate were upheld and are left as they are. Every blocker is fixed as a class, its
demonstrated variants rerun through the production pipeline, and a negative control shows the tagged gate4/gate5 code
failing the corrected oracle (tests/test_g4g5_corrections.py). Boundary: no G6/G7; no tag moves (gate4-r1/gate5-r1 SHAs and
annotation texts handed to the owner). Report: Phase3_G4_G5_corrections.md.
- [x] G4-B01 Annual PD-210 footage counts each metre once under every carried reading; repricing keeps the preceding
  allocation (one PD-210 model: elementary segments per well-day, positions over unique metres, allocation kept).
- [x] G4-B02 PD-210 overlap allocation is the complete joint domain over interval coverage (each contested segment to
  exactly one covering charge; every combination a scenario, alloc@well/date; honest unresolved bounds above 256); the
  verify_g4 oracle checks metres (coverage = union, each charge within its interval, allocations = product of cover counts).
- [x] G4-B03 Unknown chronology stays a possible contributor/candidate: civil bands, duplicates, A3 and 45A recipients
  and release, DDS once-only and A3 recipients, G5 Q7 C standing (no omission, no sentinel dates).
- [x] G4-B04 Deferred rate and arithmetic checks completed against each established band state (per scenario); a
  correct amount never makes a wrong rate pass; split bands and genuine alternatives preserved.
- [x] G5 regenerated from corrected G4 (after B01-B04): flags unchanged, CW 88/900, DDS 125/1,906; four flagged civil
  invoices change category rate -> arithmetic (PA-00303, PA-00459, PA-00506, PA-00611: under the order in which they are
  wrong the displayed rate is right and the stated amount is not the division - previously named by the G5 fallback).
- [x] G5-B01 Claim-stated class, ground and nomination never select the contract value; named unresolved-output policy
  Q9-3 E (missing evidence is not a breach; wrong only when no admissible value makes the invoice right; one class per
  well, Cl.4; export EXPORT-D on the absent-document values, EXPORT-E the invoice's own total only where it is an
  admissible contract total). Population replayed: CW 88 -> 85 (PA-00291, PA-00509, PA-00898 rested solely on the
  stated ground), DDS 125 unchanged; 25 CW and 114 DDS flagged rows 0.80 -> 0.60 (total depends on the unsupplied
  document). Z4 rotates every stated class/unrecorded ground over the population: no outcome moves.
- [ ] G5-B02 No billed or zero substitution for unvalued lines; unknown/bounded totals explicit; DS-900/VAT aggregation kept.
- [ ] G5-B03 Adjustments and releases reconciled to G4's actual amounts, recipients and ties.
- [x] G5-B04 Local alternatives namespaced by their evidence group (order@item/date, earlier@group, stands@group,
  stands-run@group, alloc@well/date); independent groups combine; PD-210 allocations under Q7 C; Z6 joins legal combinations.
- [ ] G5-B05 DS-900 checked for single charge, sign, amount, threshold and rounding.
- [ ] G5-B06 Findings attributed to the violated obligation; no fabricated rate category; Z4 separates monetary and procedural.
- [ ] Population and submission regenerated; all G0-G5 checks and tests in a fresh clone; report; SHAs and tag texts.
