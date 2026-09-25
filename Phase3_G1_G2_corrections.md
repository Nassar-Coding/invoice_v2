# Phase 3 — Correction round: G1 and G2 re-close

**Governing:**
- the independent audit of G0–G2 at `76e9518` (Phase0-1-2-audit.docx), which judged G0 PASS and G1/G2 NOT PASS;
- the plan's exit conditions (`artifacts/phase_inputs/Phase2_plan.md` §2, §4).

**Branch:** `main`. **Source:** `majedzahrani3/invoice-auditing-level-2` @ `aef4924d…`.

**Boundary kept:** no G3 work (no pricing, entitlement, cross-invoice state, classification, flags, totals or `submission.csv`), and the gate0/gate1/gate2 tags are untouched.

The audit's findings map one-to-one onto correction items C1–C4 below. All four findings are closed. Each section gives the fix, the check that proves it, the actual result, and the negative controls, which were shown failing as intended.

## C1 — G1 verification now covers every parameter and rule (audit finding 1)

**Cause.** Second verification was content-hashed only for tables and instruments. Parameters and rules had page references but no reading bound to their content. Changing `vat_pct` from 15 to 16 therefore still passed. DDS pp.9–14 and some other pages had not been re-read in Phase 3.

**Fix.**
- **Second reading of all 79 items.** Six independent readers (A–F; prompt `prompts/phase3/param_rule_second_reading_v1.md`) read every parameter (33) and rule (46) against the scan images. They could not see the spec, reports or earlier readings. For each item they gave verbatim quotes for every cited page, a verdict, and the printed value of each parameter.
- **What was corrected.** The readings found 7 rule statements that claimed more than the text says, plus 8 parameter provisions without page numbers. I corrected the statements rather than disposing of them:
  - CW-R06 and CW-R07 are now faithful, citing guideline checks 4 and 5 and Q10.
  - CW-R23 routes daywork, provisional sums and PR.01 by the contract's own conditions, with Q8.
  - CW-R24 and DDS-R22 record one outcome per invoice (guideline 12 and principle 3).
  - DDS-R09's April-2026 case now carries 36A's pre-issue protection.
  - DDS-R14 is "on any day" per Cl.22, with per-well-day recorded as new decision **D6**.
  - DDS-R17 depends on new question **Q13** (below).
  - The trench-band overlap at exactly 2 m is recorded as decision **D7**. Its scope is 0 records.
- **Re-reading.** Two fresh readers (G, H) re-read all 17 edited items. All are supported, and every document quote was machine-matched to the guideline and README text.
- **Pages never re-read.** A section reader (`prompts/phase3/section_second_reading_v1.md`) read every section on the previously un-re-read pages: CW pp.2, 4–5, 35, 37 and DDS pp.2, 9–10, 12–14, 26, 31–33. It read 12 sections and quoted 139 provisions. Eleven classifications were supported. Part VIII (DDS p.14) was not: R3 and R5–R9 have a valuation effect its owners did not name. Its ownership now names each provision's rule: R3/R4 → DDS-R07; R5/R6 → DDS-R06 with OV-DDS-05; R7/R8 → DDS-R05; R9 → DDS-R15. The disposition, bound to the corrected classification, is in `verification/section_dispositions.yaml`.
- **The log.** `tools/param_rule_verification.py` writes `verification/param_rule_log.yaml`. For each item it records:
  - the content hash of the WHOLE entry;
  - the reading and its quotes;
  - an OCR match for each quote;
  - a machine comparison of the printed value with the spec value (24 of 33 parameters are numeric or dates; 9 are wording);
  - whether the reader saw the current statement;
  - any disposition, bound to the content hash.

  Seven items needed a disposition (`verification/param_rule_dispositions.yaml`):
  - CW-R06: a label corrected exactly as reader G indicated;
  - six rules: table-row quotes whose OCR layout is weak, each value matched to the G1-verified table cell.
- **The gate.** `tools/verify_spec.py` gained two checks:
  - every parameter and rule has a current, completed reading (the hash is recomputed, so any edit fails);
  - every section on the previously un-re-read pages has a current reading.

**Result** (`tools/verify_spec.py`):
```
PASS G1 second verification against the scan recorded and current for every parameter (33) and rule (46), whole-entry content hash (DDS pp.9-14 quoted: [11, 14])
PASS G1 pages not re-read before the correction round now second-read: 12 sections, 139 provisions (CW pp.2, 4-5, 35, 37; DDS pp.2, 9-10, 12-14, 26, 31-33)
SPEC VERIFY OK
```
Reading results:
- First readings: 71 of 78 supported and 7 partly supported, all corrected. DDS-R22 was not read in the first round.
- Re-reading of the 17 edited items (readers G, H): 17 of 17 supported.
- DDS p.14 R4 (the circulating-hours rule) is quoted from the scan by the readers for DDS.P.circulating_hour_rounding and DDS-R07.

**Negative controls** (`tests/test_g1_gate.py`, and run live against the real verifier). Each fails as intended:
- `DDS.P.vat_pct` 15→16 fails with "content changed since its second reading" (exit 1);
- editing a rule title (DDS-R07 "six-hour"→"eight-hour") fails;
- editing a validation case fails;
- editing a parameter page fails;
- a missing reading fails;
- a reading of an older statement stays pending in the recorder;
- a section classification edited after its reading fails.

## C2 — DD-121 tool presence (audit finding 2)

**Cause.** `link_dds()` looked for the billed code among the report's tool codes. DD-121 has no Appendix G term of its own, so all 245 lines read "tool absent".

**Fix.** Tool presence now follows a declared basis per Schedule 8 tool-day service (`spec/evidence_dds.yaml` `tool_presence`):
- the service's own Appendix G term; or
- a contract substitute: DD-121 → DD-120. Cl.21 p.6 says "On a Standby day item DD-120 is not charged and item DD-121 is charged instead". Sch 3 Part 4 p.21 says "DD-121 is charged only on a Standby day, in place of item DD-120 (Clause 21)"; or
- no tool: DD-102, whose term "night man" names a person (Q5, cited from the Sch 8 introduction and row and App G). Its fact is now null rather than false.

A service with no Appendix G term and no declared basis fails.

**Check.** New G2 check S3 reports, per service, the share of lines where the report does not establish the tool. Any share of 90% or more must be explained by a cited no-tool entry.

**Result.**
- All 245 of 245 DD-121 lines now show the rotary steerable present.
- DD-102: 8,151 of 8,151 null, explained (Q5).
- RM-511: 3 of 806 are genuine absences. MDS-00287-082, MDS-01043-030 and MDS-01268-014 each have no "hole opener" in the hole (checked against the raw files).
- Every other code: 0.
- Resolved references carrying a semantic mismatch fell from 8,461 to 68.

**Negative controls.**
- Reintroducing the defect in memory makes the real verifier FAIL S3 ("DD-121: tool not established on 245/245 lines and no cited explanation") and S2 (exit 1).
- An undeclared tool-day service fails.

## C3 — Independent semantic verification (audit finding 3)

**Cause.** The blind comparison checked raw fields only. The derived tool codes, crew-by-service counts, invoice-to-tool facts and civil attribute names were never independently checked. The sample size was not enforced.

**Fix.** Four independent reviewers (`prompts/phase3/semantic_review_g2_v1.md`) derived the meanings from raw text and the contract scans alone. The sample is fixed by `tools/semantic_review_g2.py sample`, seed 20260926.
- **ddr (31 reports):** each tool term → code, in the hole and in the run; each crew term → code and count; the lost tool → LH code.
- **lines (84 lines, 2 per service code plus the lines the audit or G2 report singled out):** the Sch 8 tool basis, tool presence, Sch 5 part and whether present, crew count, and LH code.
- **civil (45 records):** quantity, unit, every attribute BY NAME, and the candidate Schedule 1 items.

The comparator fails on any missing or extra annotation or missing field, and compares every field by name. G2 check **S4** requires full agreement or a disposition bound to both values. The raw-field comparison is now labelled a *transcription* check (S1) and also enforces its sample. The branch coverage (E4) now includes tool, crew, required-part and LH link outcomes (118 of 118).

**Checking the reviewers.** Beyond the parser comparison, I checked the reviewers' evidence directly against the raw files, with no problems:
- every drilling report's term and crew totals against the raw "In the hole", "Tools in run" and "Crew on tour" lines;
- every line's report number and required-part presence;
- every civil quantity and attribute value against the raw narrative.

**Result.**
- `S4`: ddr 583 of 583 fields, lines 482 of 482, civil 161 of 161; 160 of 160 sampled items annotated; 0 disposed.
- The reviewers independently derived the DD-121→DD-120 substitution and the DD-102 null.

**In-scope defect found and fixed.** The reviewers read Appendix G as printed: "resistivity tool" is LW-411 (LWD density and neutron), and "density-neutron" is LW-412 (sonic). G2's source-handling observation had matched the rig word "density-neutron". It is now keyed by code:
- source carried = LW-411 in the hole on 2,590 of 2,590 days, with 0 exceptions either way;
- every Part D day has LW-411.

So `Phase3_G2.md` §6 item 2 ("source carried ≠ density-neutron") is withdrawn.

**Negative controls** (`tests/test_g2_semantic.py`, also shown live). Each fails with a named field:
- wrong tool code (gamma tool → LH-714);
- wrong crew count (DD-101 +1);
- mislabelled civil number (dia_mm read as depth_m);
- wrong tool-presence fact on the DD-121 line;
- a missing semantic annotation;
- a missing field;
- a missing transcription annotation.

## C4 — Provenance context, carried items, Q11 (audit finding 4)

**Provenance.**
- `audit/provenance.py` builds a run context. It hashes every audit module plus the spec loader, the reviewed inputs (both evidence specs and both terms files), and the snapshot (pinned commit and G0 manifest).
- Every derived fact (claim row, record, report, run, well span, link, unresolved entry, conflict: 212,717 facts) carries its id in `ctx`.
- The context is written to `verification/g2/run_context.json` and into `coverage.json`.
- The old `extraction_version()`, which covered only the specs, is removed.
- **Check S5:** every fact references the current context; the context covers every audit module; the committed context reproduces.
- **Controls:** a code-only change (a comment added to `audit/links.py`) changes the id with inputs unchanged; a reviewed-input change changes it; a fact without the context fails.

**Carried items** (`spec/carried_items.yaml`). S5 fails on any unregistered conflict or missing-part line, and on any registered item that no longer occurs.

| Id | What | Owner | Rule / question | Treatment |
|---|---|---|---|---|
| CI-01 | 27 `part_E_hours_vs_well_daily_sum` conflicts, of 54 losses: 12 equal to the run sum only, 15 matching neither reading (listed) | G3 | DDS-R17 / **Q13** (new) | value under A (Part E) and B (well daily sum through the loss day); if the 25-hour steps differ, the line is a query bounded by A and B |
| CI-02 | DDR-009-20251211 has "Gyro surveys: 1" but no Part C; line MDS-00954-021 (DD-130) | G3 | DDS-R05, DDS-R07 / Q3 | record condition decided at G3; G2 records only the absence |
| CI-03 | LW-420 lines MDS-00876-062 and MDS-01393-036: source carried, but no Part D on any day of either run | G3 | DDS-R05, DDS-R15 / Q3 | as CI-02 |

**Controls:** removing CI-02 fails (the conflict and its line are both named), and dropping a CI-03 line fails.

**Q11** now uses the records-based bound, computed from the recorded depths (Part A depth end minus depth start), not from billed PD-210 metres:

| Measure (per well, all supplied dates) | Maximum | Well |
|---|---|---|
| Physical depth increment | 6,026 m | NGP-BD-027 |
| Drilled + logged + reamed | 10,002 m | |

There are 0 negative increments. No well reaches 40,000 m under either reading. D4's scope key follows the new bound. The test `test_q11_uses_the_records_based_bound` covers it.

## Checks and results

`PYTHON=<venv> tools/check_g2.sh` on the working tree before this report was committed (all checks and tests):
```
SNAPSHOT VERIFY OK: 10330 files match manifest (sha256 + git blob), HEAD=aef4924d…; pdf_pages.json and inventory.json reproduce
reading comparison reproduces committed file
PASS G0 x4; PASS G1 x7 (tables/instruments 55; parameters 33 + rules 46; 12 sections / 139 provisions; ...); SPEC VERIFY OK
121 passed
PASS E1 rows 101796; records cw 2169/2169, dds 8151/8151 by report number; unreferenced 0/0
PASS E2 1566086 required fields; unresolved queue 0; conflicts visible 28
PASS E3 reference states separate; 68 resolved references carry a semantic mismatch (was 8461)
PASS E4 118/118 branches (incl. tool/crew/part/LH link outcomes); fixtures 29 civil, 11 DDR, 11 claims, 20 links
PASS S1 transcription civil 646/646, DDR 1029/1029, sample complete
PASS S3 tool presence: DD-102 8151/8151 null (Q5); DD-121 -> DD-120; RM-511 3/806
PASS S4 semantic: ddr 583/583, lines 482/482, civil 161/161; 160/160 sampled items
PASS S5 212717 facts reference the run context; CI-01..03 registered (G3)
PASS S2 committed outputs reproduce
G2 VERIFY OK
```
The same command was re-run in a fresh clone at the final `main` commit. That output, and the commit SHA, are given with the gate1-r1 and gate2-r1 tag text. A report cannot contain its own commit SHA.

## Artifacts changed

- **Spec:** `spec/rules.yaml` (8 rules), `terms_cw.yaml` and `terms_dds.yaml` (8 parameter labels), `open_questions.yaml` (Q11 bound, Q13, D6, D7, Q8/Q10 rule lists), `question_scopes.json`, `evidence_dds.yaml` (`tool_presence`), `carried_items.yaml` (new).
- **Code:** `audit/links.py`, `build.py`, `provenance.py` (new), and a `ctx` field on the fact classes.
- **Tools:** `tools/verify_spec.py`, `verify_g2.py`, `compare_blind_g2.py`, `question_scopes.py`; new `param_rule_verification.py` and `semantic_review_g2.py`.
- **Verification:** `verification/param_rule_{packets,readings,log,dispositions}`, `section_readings.jsonl`, `g2/semantic/`, `g2/run_context.json`, and the regenerated `g2/*.json`.
- **Prompts:** three new prompts in `prompts/phase3/`.
- **Tests:** `test_g1_gate.py` (+7), `test_g2_controls.py` (+3), `test_g2_semantic.py` (new, 8), `test_g2_provenance.py` (new, 8), plus fixtures (+6 links).
- **Documents:** `Phase3_TASKS.md`, `README.md`, and supersession notes in `Phase3_G0_G1.md` and `Phase3_G2.md`.

## Open items with scope

- **Q13** (new, G3): Part E loss hours, with 27 of 54 losses in conflict (CI-01).
- **D6 and D7:** new settled decisions with recorded alternatives.
  - D6 scope: 10,207 (date, service) pairs where every well-day is within its limit but the sum over wells is not.
  - D7 scope: 0 records.
- **Q5** unchanged: DD-102 on all 8,151 lines.
- **CI-02 and CI-03:** 3 lines, owned by G3.
- **Reader ambiguities** recorded in the readings and not resolved at G1, for example:
  - whether the DD-120 six-hour minimum applies before or after the rig-up hour (already Q4);
  - "the later instrument" meaning issue order (D2);
  - "after" versus "on or after" issue (Q1);
  - 33A versus Cl.33 "exactly";
  - the README's lack of an outcome or clause column (Q9).

## Not confirmed

- **How independent the readers were.** Isolation was instructed, not enforced. The readers report opening only the permitted files.
- **The first civil semantic reviewer was refused the raw record files** ("PII Data Handling"). I did not route around that by retrying. The civil review ran on a packet carrying only each record's title and narrative line, which contain no personal names, with the prompt amended to say so. That reviewer then hit a session rate limit after writing all 45 lines. I validated the file: 45 of 45 lines, parsed, and every value checked against the raw narrative.
- **Two G1 readers could not open the guideline file.** I did not work around it. Fresh readers G and H re-read the guideline-dependent items and opened the documents normally.
- **Sample coverage.** The semantic review covers a seeded sample: 31 of 8,151 reports, 84 of 91,244 lines and 45 of 2,169 records. Population-wide safeguards are the S3 per-service check and the E4 branch coverage.

## Time

About 1 h 45 min active on 2026-09-25: 18:15–19:10 and 22:40–23:30 UTC. The gap was a pause at the subagent session limit, which reset at 22:40 UTC.
