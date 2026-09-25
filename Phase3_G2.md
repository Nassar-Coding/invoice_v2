# Phase 3 — Gate G2: load claims and extract evidence

**Governing plan:** `artifacts/phase_inputs/Phase2_plan.md` §2 (G2 row), §4, §10.3. **Branch:** `main`. **Built on:** gate1 @ `bf40eb8`, cleanup @ `d76e8a2`.
**Source:** `majedzahrani3/invoice-auditing-level-2` @ `aef4924dc32506b4587de8b788b5a947e6beffec`. Contract wording, including Appendix G, is taken from the verified terms in `spec/`. It was not read afresh, and no G0/G1 term was modified.
**Boundary kept:** G2 does no pricing, applies no entitlement rules, keeps no cross-invoice state, and produces no classification, flag, total or `submission.csv`. A test checks that the `audit/` package defines none of them.

## 1. What was implemented

- **Evidence-mapping specification** (`spec/evidence_cw.yaml`, `spec/evidence_dds.yaml`):
  - civil record layout and 9 families;
  - 26 narrative templates, each with its meaning, unit, candidate items and source;
  - DDR header and Parts A–E, with key types and meanings;
  - Appendix G terms resolved through the verified glossary `DDS.T20_GLOSSARY`: the loss context in Part E gives the LH codes, and crew wording gives personnel codes.
  - The extraction version (a hash of the specs plus the glossary) is `dd0fb372ad977ea4`.
- **Claims loader** (`audit/claims.py`):
  - loads all four CSVs, keeping file, line and original strings;
  - money and quantities are exact `Decimal` values parsed from the string, and a blank stays `None` rather than zero;
  - input assertions: unique IDs, every parent exists, every header has lines, the template covers every header.
- **Civil parser** (`audit/records_cw.py`):
  - handles all 9 families;
  - reconstructs weekly day lists across month and year ends: the year rolls forward, and weekday, in-week and duplicate-day checks run;
  - detects placeholder signatures;
  - validates Area against Sch 2 and Ground against Sch 3;
  - checks the ticket number against the file name.
- **DDR parser** (`audit/records_dds.py`):
  - parses the header and Parts A–E with typed values;
  - reads tools in the hole and in the run, crew counts, the lost tool, and signature placement;
  - indexes by the internal `Report:` number, not the file name;
  - raises 17 intra-report consistency checks as conflicts.
- **Events** (`audit/events.py`), built from the records only:
  - 1,369 BHA runs, where repeated Part B metadata is held as one fact per run;
  - 367 runs with source-handling days;
  - 54 losses, each corroborated against the daily history of the whole well and of the run;
  - continuity of the 214 wells.
- **Links** (`audit/links.py`):
  - one link object per invoice line;
  - the **reference state** (whether the reference resolves) is kept separate from the **semantic facts** (date, area, well, rig, status, section, unit, quantity relation, signatures, required part, crew, tool in hole, reference use count);
  - accounts for every record file.
- **Unresolved queue and conflict list** (`audit/common.py`):
  - any unparseable or missing required field is queued with its source; nothing is defaulted;
  - contradictions between records stay visible as conflicts.
- **Build outputs** (`audit/build.py`): `verification/g2/{coverage,unresolved,conflicts}.json`.

## 2. Artifacts

| Area | Files |
|---|---|
| Specification | `spec/evidence_cw.yaml`, `spec/evidence_dds.yaml` |
| Code | `audit/common.py`, `claims.py`, `records_cw.py`, `records_dds.py`, `events.py`, `links.py`, `build.py` |
| Outputs | `verification/g2/coverage.json`, `unresolved.json`, `conflicts.json` |
| Independent check | `prompts/phase3/blind_annotation_g2_v1.md`, `verification/g2/blind/{sample.json, cw_annotations.jsonl, dds_annotations.jsonl, comparison.json}`, `tools/compare_blind_g2.py` |
| Fixtures, tests | `tests/fixtures/g2_reviewed.yaml`, `tests/test_g2_fixtures.py` (46), `tests/test_g2_controls.py` (13) |
| Gate checks | `tools/verify_g2.py`, `tools/check_g2.sh` (runs the G0/G1 checks, the full test suite, then G2) |
| Task list | `Phase3_TASKS.md` (G2 section, G2.1–G2.9) |

## 3. Evidence per exit condition

Everything below comes from `tools/check_g2.sh`. Full output is in §5.

- **E1 — every source row and file is accounted for.**
  - `PASS E1 … rows 101796 (cw 900+7746, dds 1906+91244) with file/line provenance; records cw 2169/2169, dds 8151/8151 indexed by report number 8151; files cited cw 2169, dds 8151, unreferenced cw 0, dds 0`.
  - Row counts are compared three ways: loaded rows, a fresh count of the CSV file, and the G0 inventory.
  - CSV line numbers are contiguous.
  - The set of record files equals the directory listing.
  - The report index holds each DDR exactly once, keyed by its internal number.
- **E2 — each required field is parsed or explicitly unresolved.**
  - `PASS E2 … 1566086 required fields checked; unresolved queue 0; evidence conflicts kept visible 28`.
  - The queue is empty because the corpus parses completely. Negative controls prove the queue fires rather than defaulting:
    - `test_civil_bad_input_is_queued_not_defaulted`;
    - `test_ddr_bad_input_is_queued`;
    - `test_claims_loader_queues_blank_and_unparseable`, where a corrupted copy of the CSV yields exactly 4 queue items;
    - `test_weekly_day_list_checks`.
  - Blank is not zero: DS-900 lines keep blank day and report fields as `None`, and this is legitimate.
- **E3 — reference validity is separate from semantic validity.**
  - `PASS E3 … states {'blank_not_required': 5549, 'blank_required': 4, 'dds:blank_invoice_level': 63, 'dds:resolved': 91181, 'not_found': 3, 'resolved': 2189, 'wrong_series': 1}; 8461 resolved references carry at least one semantic mismatch (kept as facts)`.
  - Unresolved references carry no semantic facts, and the reference state never appears among the semantic facts.
  - MDS-00164-050 resolves and has `date_match: false`. It is the plan's negative duplicate case: a mismatch, which is kept separate from reuse and duplication.
- **E4 — reviewed examples cover every record family and every encountered wording or layout branch.**
  - `PASS E4 … 111/111 branches (9 civil families, 26 narrative templates, 6 DDR part layouts, 15 tool terms); fixtures: 29 civil, 11 DDR, 11 claim rows, 14 links`.
  - Branches are derived from the corpus:
    - family, template, ground, daily or weekly layout;
    - number of days on; weeks crossing a month or year end;
    - placeholder signatures;
    - DDR part layouts, status, section, source carried;
    - every tool, crew and loss term;
    - every conflict type;
    - every claim and link state.
  - Every fixture value was typed from the raw record or CSV text, not copied from parser output.
  - `test_fixture_coverage_check_detects_a_missing_branch` shows the check fails when a fixture is dropped.
- **Supporting evidence.**
  - `PASS S1 blind subagent annotation agrees with the parser: civil 646/646 fields (45 records), DDR 1029/1029 fields (31 reports)`. The sample was seeded with 20260925: 5 civil records per family, plus DDRs stratified by part layout, including the placeholders. The comparator's own negative control is `test_blind_comparator_detects_planted_errors`.
  - `PASS S2 committed G2 outputs reproduce from the snapshot`.

## 4. Unresolved items and visible facts, with exact scope

- **Unresolved queue: 0 items.**
- **Evidence conflicts: 28.** These are kept for G3/G4 and not resolved here.
  - `gyro_surveys_without_part_C`, 1: `DDR_NGP-WS-009_20251211.txt` has Part A "Gyro surveys: 1" but no Part C. Line MDS-00954-021 bills DD-130 against it.
  - `part_E_hours_vs_well_daily_sum`, 27 of 54 losses: Part E's accumulated hours differ from the whole-well sum of daily circulating hours through the loss day. The idents are in `conflicts.json`, and each loss's readings are in `coverage.json` under `loss_hours_readings`.
- **Reference states (civil):**
  - `not_found`, 3: PA-00609-01 → CT-00126, PA-00672-04 → PS-00039, PA-00678-06 → MO-00089;
  - `blank_required`, 4: PA-00111-12, PA-00111-13, PA-00631-10, PA-00766-12;
  - `wrong_series`, 1: PA-00170-04 → PT-00189. Area, date, activity, unit and ground all differ.
  - `blank_not_required`: 5,549 non-Schedule 5 lines, which are not breaches.
- **Semantic facts on resolved references.** These are facts, not findings.
  - **Drilling tool in hole false: 8,399 lines.**
    - DD-102, 8,151 lines: "night man" is crew, not a tool. This is the Q5 conflict, carried forward.
    - DD-121, 245 lines.
    - RM-511, 3 lines.
  - **Drilling date mismatch: 8 lines.** MDS-00128-026, MDS-00164-050, MDS-00541-018, MDS-00895-051, MDS-01352-007, MDS-01619-045, MDS-01798-045, MDS-01860-039.
  - **Required part absent: 3 lines.**
    - MDS-00954-021: Part C.
    - MDS-00876-062 → DDR-201-20251115: LW-420, Part D. The source is carried, but there is no Part D that day.
    - MDS-01393-036 → DDR-029-20260515: LW-420, Part D. Same situation.
  - **Placeholder signatures on drilling lines: 33.** They come from DDR-055-20250503, DDR-149-20251122 and DDR-218-20251029.
  - **Civil placeholder signature:** PA-00613-01 → DX-00089, where the engineer did not sign.
  - **Civil work date on a day not "on": 20 lines.**
  - **Civil quantity against the record:** equal 1,739, below 424, above 27.
  - **Civil record reused:** 38 records are cited twice and 3 are cited three times. G2 only records the use count; allocation is Q7, at G3/G4.
- **Special-condition word scan** (plan B-P6): 0 hits for all 23 words. Every civil narrative matches one of the 26 templates, so the records contain no free text. The check is kept.

## 5. Checks and results

`PYTHON=<venv> tools/check_g2.sh`, run on the working tree just before this report was committed:

```
SNAPSHOT VERIFY OK: 10330 files match manifest (sha256 + git blob), HEAD=aef4924d…; pdf_pages.json and inventory.json reproduce
reading comparison reproduces committed file
PASS G0 ×4, PASS G1 ×5, SPEC VERIFY OK
95 passed   (G0 8, G1 28, G2 59)
PASS E1, E2, E3, E4, S1, S2 — G2 VERIFY OK
```

The same checks were re-run in a clean clone at the final `main` commit before handing over the gate2 tag text.

## 6. Plan assumptions the data challenged

1. **Loss hours (§4, §10.3 "Use Part E's accumulated hours and corroborating history").** In 27 of 54 losses, Part E does not corroborate the whole-well daily history through the loss day. The readings split as follows:

   | Reading | Losses |
   |---|---|
   | Matches the well sum | 25 |
   | Matches the run sum only | 12 |
   | Matches both | 2 |
   | Matches neither | 15 |

   None of Q1–Q12 covers this. It is a candidate new question for G3, and it affects the depreciation of LH-711…714.
2. **"Radioactive source carried" is not the density-neutron tool.**
   - The flag is present exactly when the resistivity tool is present (2,590/2,590).
   - 1,497 source-carried days have no density-neutron tool.
   - 211 Part D days have no density-neutron tool.
   - This affects how G3 establishes source-handling entitlement.
3. **Part B holds run-level facts.** The plan says so, and the data confirms it:
   - Part B is identical on every day of all 1,369 runs;
   - run circulating hours equal the sum of daily Part A hours;
   - metres logged and metres reamed equal the drilled metres or zero;
   - Part D appears on the run's first day (367).
4. **DD-102 against the Sch 8 tool-in-hole row.** Every DD-102 line lacks a matching tool, because "night man" is crew. This confirms Q5 is a live conflict for every DD-102 line (8,151), not an edge case.

## 7. AI use and time

- Two blind subagents annotated the seeded sample from raw text only, using the prompt `prompts/phase3/blind_annotation_g2_v1.md`. They had no access to the parser or its outputs.
- Their annotations are committed verbatim, and every field was compared. There were no disagreements.
- Parsers, fixtures and checks were written in the main session, and fixtures were typed from the raw files.
- Approximate time: 45 minutes wall-clock, 12:30–13:15 UTC on 2026-09-25. An earlier G2 attempt that you asked me to delete is not counted.

## 8. Not confirmed (and where I looked)

- **The meaning of Part E hours for the 15 losses that match neither reading.** I looked in these places:
  - in `spec/terms_dds.yaml`:
    - `DDS.P.lih_depreciation` (p.7), "circulating hours accumulated on the well";
    - the Sch 5 Part E row, "circulating hours accumulated on the well at the time of the loss";
  - the lost-in-hole rule in `spec/rules.yaml`;
  - plan §10.3;
  - the daily history of each well and run.

  The contract wording supports the whole-well reading, but it does not explain the 15 losses that match neither reading. This is left for G3.
- **Whether a missing Part D on a billed LW-420 day means the handling was recorded on another day.** The two lines are listed in §4. G2 only records the absence.
- **The blind check is a sample.** It covers 45/2,169 civil records and 31/8,151 DDRs. Completeness for the rest rests on three things: every narrative matching a template, every DDR key being typed, and the 111-branch fixture coverage.
