# Phase 3 — Gates G0 and G1

**Governing plan:** `artifacts/phase_inputs/Phase2_plan.md` §2 (G0/G1 exit conditions), §3, §8, §9. **Branch:** `opus_stage2` only.
**Source:** `majedzahrani3/invoice-auditing-level-2` @ `aef4924dc32506b4587de8b788b5a947e6beffec`.
**Boundary kept:** there is no evidence parser, valuation engine, cross-invoice state, classification, flag, total or `submission.csv`. The only data code is read-only counting, used for the inventory and the question scopes.

## 1. What was implemented

- **G0 — freeze.**
  - SHA-256 and git-blob hashes for all 10,330 snapshot files, checked against the pinned git tree.
  - A pixel-sample hash for each of the 85 scanned pages. Every page image read in Phases 1–3 was confirmed identical to the scan.
  - An input inventory and join checks.
  - Preserved Phase artifacts.
  - Source, rule and ambiguity indexes.
  - Ownership maps for every contract section and all 12 guideline checks.
  - An explicit register of the independent-audit corrections.
- **G1 — terms and consequences.**
  - 45 tables with 483 numeric cells and 33 dated parameters, each carrying page and provision.
  - A register of all 10 instruments.
  - A second verification of every table and instrument against the scan, by three independent means:
    - my own visual re-read of every cell on the image;
    - a **blind** subagent transcription per contract, made without access to the first pass;
    - tesseract OCR of all 85 pages.
  - An overrides register (20 entries).
  - A consequence table (6 categories).
  - A question register: Q1–Q12 with bounded alternatives, plus 5 settled decisions that keep a recorded alternative. Affected scopes are computed from the CSVs.
  - A content-hashed verification log and a gate that stops any unverified or later-edited table from feeding pricing.

## 2. Artifacts created or changed (all on `opus_stage2`)

| Area | Files |
|---|---|
| Snapshot | `source/SNAPSHOT.md`, `manifest.tsv`, `pdf_pages.json`, `inventory.json`; `tools/snapshot.py` |
| Phase inputs | `artifacts/phase_inputs/` (baseline Phase 1 report, independent Phase 1/2/2.5 audits, governing plan, `MANIFEST.sha256`). The supplementary Phase 1 report is `Phase1_understanding_supplementary.md`, hash-identical to the supplied copy. |
| Specification | `spec/terms_cw.yaml`, `terms_dds.yaml`, `instruments.yaml`, `rules.yaml` (46), `guideline_checks.yaml`, `sections_cw.yaml`, `sections_dds.yaml` (156 sections), `overrides.yaml`, `consequences.yaml`, `open_questions.yaml`, `question_scopes.json`, `corrections.yaml` (41), `sources.yaml` |
| Verification | `verification/second_pass_visual_log.txt`, `second_pass_log.yaml`, `reading_comparison.json`, `blind/`, `ocr/`, `phase2_verbatim/` |
| Tools | `extract_pages.py`, `compare_readings.py`, `record_verification.py`, `question_scopes.py`, `verify_spec.py`, `spec_lib.py`, `check_g0_g1.sh` |
| Tests, run setup | `tests/` (36 tests), `requirements.txt`, `README.md`, `.gitignore`, `prompts/phase3/blind_transcription_v1.md` |
| Task list | `Phase3_TASKS.md` |

## 3. Evidence that G0 passed

Exit condition: *"File hashes and inventory match the snapshot; every guideline check and material contract section has an owner in the specification; audit corrections are explicitly recorded."*

- **Snapshot.** `tools/snapshot.py verify` from a clean clone printed: `SNAPSHOT VERIFY OK: 10330 files match manifest (sha256 + git blob), HEAD=aef4924d…; pdf_pages.json and inventory.json reproduce`.
- **Inventory against the plan's own figures.** Tests assert, independently of the frozen files:
  - 900/1,906 headers and 7,746/91,244 lines;
  - 60/39 codes;
  - 2,169/8,151 records, of 557,687/7,698,252 bytes;
  - template of 2,806 rows equal to the header IDs;
  - the observations later gates depend on (zero adjustments, three missing civil records, same-day submissions, contract-reference variants).
- **Ownership.** `verify_spec.py` reports:
  - `PASS G0 every material contract section has an owner (156 sections, CW 43 + DDS 42 pages)`;
  - `PASS G0 every guideline check (12 x 2 contracts) has an owner, consistent with rules.yaml`.
  - Non-operative sections carry an explicit `not_material` reason rather than an owner.
- **Corrections.** `PASS G0 audit corrections explicitly recorded (41 items …)`. The 41 items are:
  - Phase 1: A1–A2, B1–B5 and §6 items 1–8;
  - Phase 2: B-P1 to B-P6 and §6 items 1–8;
  - Phase 2.5: B-1 to B-5 and §6 items 1–7.
- **Indexes.** `PASS G0 rule/ambiguity/source indexes exist (rules 46, questions 12, decisions 5)`.

## 4. Evidence that G1 passed

Exit condition: *"Every active numeric cell and rule has a page/clause reference and a second verification against the scan; explicit overrides are recorded; open interpretations have bounded alternatives and affected scopes. No unverified table feeds pricing."*

- **References.** `PASS G1 every table (45, 483 numeric cells), parameter, instrument and rule (46) has a page/clause reference`.
- **Second verification.** `PASS G1 second verification against the scan recorded and current for every table and instrument (55)`.
  - The visual pass found **0 numeric discrepancies** in the first-pass transcription.
  - It made 37 wording or structure fixes, none numeric:
    - 33 paraphrased descriptions in the coverage-only Schedules 6–8;
    - 4 lost-in-hole descriptions;
    - Schedule 4/5 wording;
    - Appendix G restructured to its printed 24-row, code-first layout;
    - the daily-limit unit column;
    - three page corrections.
  - The blind readers agreed on 544/547 numeric cells and 1,025/1,047 text cells. OCR agreed on 522/547. Every residual was settled on the scan and dispositioned in `second_pass_log.yaml`:
    - comparator layout artifacts;
    - OCR noise such as "7125" read for 725;
    - derived cells that cite clauses outside the blind pages.
- **Overrides.** `PASS G1 explicit overrides recorded (20)`.
- **Open interpretations.** `PASS G1 open interpretations have bounded alternatives and affected scopes (12 questions, 5 decisions)`.
- **Pricing gate.** `PASS G1 no unverified table feeds pricing (49 pricing-relevant tables/instruments checked)`.
  - A verified table's content hash is recomputed on every run.
  - Regenerating the log never re-certifies a changed table (tested).
- **Negative controls.** Eight tests prove the gate fails on each class of defect:
  - a changed rate;
  - a changed instrument;
  - an unowned page;
  - an unowned check;
  - a missing correction;
  - a question with one alternative or no scope;
  - a rule with no page reference;
  - an unverified or re-edited table.
- **Worked examples**, recomputed with exact `Decimal` arithmetic in the tests, not by production code:
  - CW App B (50.72, 23.74, 91.37; 15,794.40; retention 789.72; net 15,004.68);
  - DDS App B (1,477.88, 2,975.75, 509.00, 58.15/76.45; net 25,662.26; VAT 3,849.34; 29,511.60);
  - Clause 38 (312,400 → −2,496.00);
  - App F (412 h → 16%);
  - the float pitfall (423 × 0.945 → 399.74 half-even; float gives 399.73).
- **Consistency tests:**
  - every "rate previously payable" chain;
  - Sch 2D = Sch 6 × 3.75;
  - identical FX tables in both contracts;
  - extension lengths of 185, 183, 181 and 184 days;
  - issue order and the retrospective flags;
  - completeness counts against the plan §3 inventory (60, 15, 13, 4, 8, 9, 17; 38, 29, 22, 12, 24, 4).

## 5. Unresolved questions and blockers, with scope

No question blocks G0 or G1. All twelve stay **open by design**, with bounded alternatives in `spec/open_questions.yaml`. The rules that depend on them carry `status: open` and cannot yield final outcomes until the question is closed or disclosed. Scopes are populations a reading *can* affect, not findings.

| Q | Scope (from `question_scopes.json`) | Blocks |
|---|---|---|
| Q1 A3 recipient ("after" vs "on or after"; ties) | CW: 89 lines in 72 pre-issue applications. Recipient is PA-00006/00023/00380 (tie on 2026-05-12) or PA-00443 (2026-05-14). DDS: 3,309 lines in 511 pre-issue invoices across 68 wells. Recipient is MDS-01625, or the tie MDS-01585/01631/01645. Per-well variant: 56 wells have no later invoice. | G4 |
| Q2 Adjustment placement against the judged total, DS-900 and VAT | Same populations | G5 |
| Q3 Missing record: exclude now vs P23 recovery | 2,197 Schedule 5 lines: 4 blank references, 3 with no file, 1 wrong series | G3 |
| Q4 DDS first hour, minimum and period | 4,606 DD-120 lines (none billed at 6 hours or fewer); 943 RM-530 lines | G3 |
| Q5 Schedule 8 conflicts | 8,151 DD-102, 428 HC-630, 4,606 DD-120 and 943 RM-530 lines | G3 |
| Q6 Civil state basis, caps, exclusion day count | 1,026 band-item, 1,183 cap-item, 125 A.14.020 and 104 E.51.020 lines; 1 repeated item/area/date group | G4 |
| Q7 Weekly reuse; DDS repeat allocation | 20 civil references on more than one date (19 of them DW); 187 repeated DDS well/date/code groups (184 of them PD-210) | G4 |
| Q8 Unsupplied background documents | 2,390 PD-210 lines (performance-section nomination); 0 civil night-on-rest-day lines for double-listed items | G3 |
| Q9 Binary treatment, unknown-total encoding, confidence | Population-wide; identity variants PA-00560, PA-00711, MDS-00672, MDS-00988, MDS-01799 | G7 (decide early) |
| Q10 Omitted obligations | 66 invoices billed above 250,000, of which 3 have no DS-900 (billed-based diagnostic) | G5 |
| Q11 DDS accumulator metres; Cl.35 remedy | Maximum billed PD-210 is 3,355 m per well-year, so no band can change on this data | G3 |
| **Q12 (new)** CW Contract Year reset on 5 Jan 2026 | 378 band-item lines on or after 2026-01-05 (648 before) | G4 |

## 6. Checks run and their results

| Command (clean clone of `opus_stage2` @ `bf40eb8`) | Result |
|---|---|
| `tools/snapshot.py verify` | `SNAPSHOT VERIFY OK` (10,330 files; HEAD aef4924d) |
| `tools/compare_readings.py` | blind 544/547, OCR 522/547 numeric agreement; reproduces the committed comparison |
| `tools/verify_spec.py` | 9 × PASS, `SPEC VERIFY OK` |
| `pytest -q tests` | **36 passed** |
| `tools/check_g0_g1.sh` | runs all of the above |

## 7. Plan assumptions the implementation challenged

1. **The CW Contract Year reset is not settled.**
   - Plan §6 states the bands "reset on 5 January".
   - The verbatim 3A (p.32) reads: "The final Contract Year ends on the Date for Completion as extended by any Amendment, however long that leaves it; an extension of time does not begin a new Contract Year."
   - This supports a no-reset reading as well. The original completion date (27 Sep 2025) fell inside Contract Year 1, so on that reading Year 1 would simply stretch to 30 Sep 2026.
   - I registered this as Q12. The working reading is the plan's; 378 lines depend on it.
   - The DDS 3A lacks "however long that leaves it", and there Q11 shows the choice cannot matter on this data.
2. **PD-210's class factor is a decision with a live counter-argument, not a bare fact.**
   - 17B and the App B example exclude the factor.
   - Schedule 2's note and the Schedule 3 Part 2 list include PD-210, and Cl.2 says a Schedule prevails over a Part.
   - Kept as D1 with its alternative. Scope: 941 PD-210 lines on non-Standard wells.
3. **Both App B examples omit the operative indexation** (C.31.010 under 29A; MW-310 under 17A). The plan's rule on illustrative examples was applied and recorded as D3.
4. **The Phase 2.5 solution-family selection was not contradicted.**
   - The blind transcription agreed with the first pass on every numeric cell. This supports reviewed deterministic extraction.
   - Nothing here bears on the record-vocabulary assumption, because that is G2 work.

## 8. Not confirmed, and limitations

- **Blind readers.** The blind rule was instructed to the subagents but not technically enforced. Their reports state they opened only page images and their own output. Their pages cover every pricing table; they did not re-read pp.1–16 or the appendices outside their lists.
- **Pages not re-read in Phase 3:**
  - CW pp.2, 5, 35, 37;
  - DDS pp.2, 9–14, 26, 29, 31–33.
  - None holds a pricing table. The P1–P14 and R1–R12 wording comes from the Phase 1 notes.
  - CW pp.1, 3–4, 6–8, 10–12 and DDS pp.1, 3–8 rely on the Phase 2 verbatim second reading.
- **Validation cases.** The `validation` cases in `rules.yaml` are specifications for G3/G4. They are not built.
- **Time.** About 4¾ hours of wall-clock time (13:15–18:05 UTC), including roughly 7 minutes each of background subagent runs. Active effort was not measured separately.

**AI disclosure.** This work was produced by Claude. It used two blind-transcription subagents, whose prompt is saved in `prompts/phase3/`, and tesseract OCR as a non-authoritative aid.
