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
