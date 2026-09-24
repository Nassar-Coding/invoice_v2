# Phase 3 tasks — G0 and G1 (Agent 1B)

Governing plan: `artifacts/phase_inputs/Phase2_plan_Agent1a.md` §§2–3, 8–9. Branch: `opus_stage2` only.
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
- [x] G0.5 Preserve the three Phase 1 artifacts (1A, 1B, Agent 2 Phase 1 audit) plus the governing plan and later audits, with hashes → `artifacts/phase_inputs/`.
- [x] G0.6 Source index (documents, pages, page hashes) → `spec/sources.yaml`.
- [x] G0.7 Contract-section ownership: every page of CW (43) and DDS (42) → owner rule/term/decision or explicit "non-operative" reason → `spec/sections_cw.yaml`, `spec/sections_dds.yaml`.
- [x] G0.8 Guideline-check ownership: 12 checks × 2 contracts → owning rules → `spec/guideline_checks.yaml`.
- [x] G0.9 Rule index with stable IDs → `spec/rules.yaml`.
- [x] G0.10 Ambiguity index → `spec/open_questions.yaml` (Q1–Q11 plus any new items).
- [x] G0.11 Agent 2 corrections register: Phase 1 A1–A2, B1–B5, §6 1–8; Phase 2 B-P1–B-P6, §6 1–8; Phase 2.5 B-1–B-5, §6 1–7 → `spec/corrections_agent2.yaml`.
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
- [x] Write `Phase3_G0_G1_Agent1b.md`; commit and push to `opus_stage2`.
