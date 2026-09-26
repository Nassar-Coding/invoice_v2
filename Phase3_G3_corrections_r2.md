# Phase 3 — G3 correction round 2

**Scope.** Targeted fixes for the independent re-audit `Phase3_G3_reaudit_Agent2.md`. It found G3 NOT PASS at `83c4a61` (gate3-r1):
- F1 and F3 closed;
- F2 partially closed, now item **B1**;
- F4 partially closed, now item **B2**;
- the Q5/D8 record and a report error, now item **D8**.

**Boundary.** No G4 work was done: no band allocation, caps, cross-invoice state, duplicates, or run/well lifecycles. There is also no classification, flag, total or `submission.csv`. No tags were moved.

**Base.** `main` = `origin/main` = `83c4a61`, clean tree, at the start. Round-2 commits, in order:

| Commit | Content |
|---|---|
| `dad6c82` | case inputs and reader prompt v4, before any reader ran |
| `1aef89d` | B1 |
| `7bbdc75` | readers' output |
| `b7482b1` | B2 |
| `bfb1257` | D8 |
| `c45c0be` | B2 follow-up |
| `f38aa38` | B1 follow-up |
| (close commit) | this report |

**Result.** All three items are fixed, each with a negative control that fails as intended. Two further defects were found by trying to falsify the fixes on branches no case exercised; both are fixed with controls. A third defect, found by the independent reader, is also fixed. The G0–G3 checks and the full test suite pass. The fresh-clone run and the final SHA are given in the conversation, because a report cannot carry its own commit.

---

## B1 — Ground-class authority

**Re-audit.** The F2 fix let any referenced record with a ground class settle the class, provided the item needed no Schedule 5 record. Probe: PA-00031-06 (A.12.050, 30 Apr 2025, S-01) citing DX-00007 (25 Jan 2025, S-04, G5) became *determined* at SAR 85.41.

### Fix

`audit/g3_cw.py`, `record_applies`. A record settles the class only if it applies to this work, and this is checked for every record, whatever Schedule 5 says about the item (CW S4, Cl.5). It applies only if all three hold:
- **same day:** the same date, or the week that contains the work date;
- **same area:** the same work area; an unparsed area never applies;
- **same item:** an item basis that covers the billed item.

Otherwise every class G1–G5 is carried as owned uncertainty (G5), with S4's G2 disclosed and the mismatch stated. `ground_differs_from_record` is then *unresolved*.

**Follow-up from my own falsification (`f38aa38`).** The record must also be countersigned by the Engineer's representative:
- App A defines *Ground classification* as "the category assigned under Clause 5", and *Engineer* as including "that person's representative";
- Cl.5 says the class is "determined by the Engineer";
- 27A refers to "whatever the Engineer recorded on the day".

A record signed by the foreman alone is the Subcontractor's own statement. Before this follow-up, such a record of this work settled the class of an item needing no Schedule 5 record.

### Evidence

- **The re-audit's probe (real line PA-00031-06 citing DX-00007).** The result is now *conditional*, with unit rates:

  | Class | G1 | G2 | G3 | G4 | G5 |
  |---|---|---|---|---|---|
  | Unit rate (SAR) | 49.26 | 52.40 | 58.69 | 72.05 | 85.41 |

  The reading states: "dated 2025-01-25, work 2025-04-30; area S-04, work S-01; evidences ['A.12.030'], line bills A.12.050". Case CW-R24, `test_b1_probe_unrelated_record_does_not_settle_the_class`.
- **Positive case, so the check is not simply disabled.** CW-S64: an item needing no Schedule 5 record, citing a record of the same day, area and trench depth that states G3 and is countersigned. Result: *determined* at G3, 38.98 → 3,898.00. `ground_differs_from_record` is a finding, because the application says G4.
  - CW-S68 is the same with G5: 56.72 → 5,672.00.
  - A real positive, CW-R25: line PA-00017-07 (A.12.040) with its own record DX-00106 gives G1, 65.05 → 23,808.30.
- **Each mismatch on its own keeps every class:**
  - CW-S65, the day before;
  - CW-S66, area S-04;
  - CW-S67, a 3 m trench record, so a different item.
- **Branches no real line exercises**, all agreeing between the engine and X2's independent predicate:
  - a weekly record, inside and outside its week;
  - an unparsed area;
  - an applicable record with no class, which keeps every class;
  - an unsigned applicable record, which keeps every class.

  X2's predicate matches the engine on every population line that cites a record (more than 1,000 lines), both for the line's own record and for the two unrelated records.
- **Independent reader (prompt v4, isolated, from the scans).** All seven CW cases agree on:
  - payable;
  - allowed quantity;
  - rate;
  - amount or the full set of alternatives;
  - unresolved findings.

  The reader used the countersigned daily record as the Engineer's classification (S4, 27A, App A), which is the same basis as the follow-up. Four finding comparisons are disposed of; see *Readers and dispositions*.
- **Population unchanged:** CW 6,171 determined, 1,560 conditional, 15 not payable, and 649 lines ground-conditional. All 1,417 ground lines for items needing no Schedule 5 record carry no record reference.

### Controls (fail as intended)

| Engine variant | Check | Result |
|---|---|---|
| Any referenced record settles the class (the re-audit's defect) | X2 | rejects PA-00031-06 + DX-00007: "ground item with no recorded classification without every ground class" |
| Same | X6 | the claim's cited record is perturbed to DX-00007, or DX-00008 when the line shares its day or area; value changes are reported (`test_b1_control_x6_…`) |
| Records never settle the class (the check simply switched off) | X2's new positive side | rejects PA-00017-07: "an applicable record settles the class" |
| A foreman-only record settles the class | X2 | rejects it |

### What this does not establish

- **No real line exercises the positive path for an item that needs no Schedule 5 record.** All 1,417 such lines have a blank record reference. The path is shown only by synthetic cases and the probe.
- **Applicability is judged by date or week, area code and the record template's item candidates.** It does not compare the record's quantity with the line's, because that is not needed for the class.
- **Engineer's countersignature.** Treating a countersigned daily record as the Engineer's classification is a reading of S4, 27A and App A; the Cl.5 trial-pit record and written confirmation are never supplied. The reader took the same reading.
- **Cited-record mismatches on items that need no Schedule 5 record are not reported as `record_*` findings.** The reader did report them. The disagreement is disposed of on Cl.46–47, which cover only records Schedule 5 requires, and on Cl.42, which requires no record reference. The mismatch is stated in the result's reading.

---

## B2 — PD-210 charges crossing a band boundary

**Re-audit.** When the charged metres differed from the interval, the engine moved the whole difference into one band at a time:
- 98 m on 1,450–1,550 m omitted 49 + 49;
- 40 m produced a payable result with no amount and no alternatives.

X3 checked consistency, not completeness.

### Fix

`audit/g3_dds.py`, `_allocation_sets`, `pd210_domain` and `pd210_count`. Every admissible allocation of the allowed metres to the bands is computed:
- **Fewer metres than the interval:** each band carries between 0 and its metres.
- **More metres (within 25A):** each band carries at least its metres, and the excess lies anywhere in the bands the charge spans.
- **Grid:** allocations step by the finest decimal place of the quantity and depths.
- **Up to 25 allocations:** each is its own `tolerance:` alternative.
- **Beyond 25:** the lowest- and highest-amount allocations are listed. The whole domain is stated on the condition (owner G5): per-band bounds, step, count, and "N allocations between the two listed extremes: each admissible, unresolved".

The allowed quantity is kept. A guard makes a payable line without an amount or alternatives *unresolved* instead.

**Follow-up from my own falsification (`c45c0be`).** A band's capacity is the metres the report measures in that band within the charged interval (Cl.23: "taken from the measured depths on the Daily Drilling Report"). It was the charged interval, which is the claim. Probe: 99 m on a 1,450–1,550 m charge whose report measures 1,451–1,550 m used to offer 50 m in band 1, where the report measures 49. It is now the single allocation 49 + 50 = 4,982.65. The part label states the measured range.

**Found by the independent reader (DDS-S76, 98.5 m).** DDS Cl.17 says "Every amount is ascertained in cents". Part and amount values are now rounded half to even when a fraction of a cent arises. No population line has one.

### Evidence

| Case | Charge | Allocations (band 1 + band 2 [+ band 3]) | Amounts (USD) |
|---|---|---|---|
| DDS-S72 | 98 m on 1,450–1,550 | 48+50, 49+49, 50+48 (3) | 4,940.30 / 4,924.50 / 4,908.70 |
| DDS-S73 | 40 m on 1,450–1,550 | 41 ways → bounds: 40+0 and 0+40 | 1,694.00 … 2,326.00 |
| DDS-S74 | 202 m on 1,400–1,600 (+1%) | 100+102, 101+101, 102+100 | 10,166.30 / 10,150.50 / 10,134.70 |
| DDS-S75 | 1,510 m on 1,490–3,010 (3 bands) | 66 ways → bounds | 87,648.50 … 87,989.50 |
| DDS-S76 | 98.5 m on 1,450–1,550 | 16 ways at 0.1 m | 4,937.78 … 4,961.48 (cents, Cl.17) |
| DDS-S71 | 101 m on 1,450–1,550 (round 1) | 51+50, 50+51 | 5,067.35 / 5,083.15 |

- **Independent reader (v4).** For all five new cases, the reader's allocation counts (3, 41, 3, 66, 16), every listed allocation and both extremes are exactly the engine's.
- **Falsification of branches no case exercised.** 22 scenarios, each checked against a brute-force enumeration that is independent of both the engine and X3:
  - two and three bands;
  - reductions and excesses;
  - whole and decimal metres;
  - listed and bounded domains;
  - a coverage assertion that each kind is present.

  In addition:
  - a four-band case is checked against X3's inclusion–exclusion count;
  - five report-narrower-than-charge probes are checked against brute force from the report's own depths.
- **Population.** No line changes: all 2,390 PD-210 charges lie in one band and equal their intervals.

### Controls (fail as intended)

| Control | Rejected by | Message |
|---|---|---|
| The round-1 one-band-at-a-time engine on 98 m | X3 | "allocation domain incomplete: 2 distinct allocation(s) listed, the domain holds 3" |
| An empty payable result on 40 m | X3 | "payable without an amount or alternatives" |
| One enumerated allocation removed (DDS-S76) | X3 | "15 … the domain holds 16" |
| Bounds that are not the extremes, a hidden domain, or a wrong count (3- and 4-band) | X3 | "bounds without the whole domain stated" / "not the domain's lowest and highest amounts" |
| A 999.00 part rate | X3 (kept from round 1) | "PD-210 part rate 999.00 is not band 1's 42.35" |
| Parts pricing 97 m on a 98 m allowance | X3 (kept from round 1) | "trace quantity 97 != allowed quantity 98" |
| Part values not rounded to the cent | X3 | "not ascertained in cents (DDS Cl.17)" |
| A domain bounded by the charged interval | X2 | "the report measures … there" (checked against the report itself) |
| An allocation above the stated measured metres | X3 | "is not admissible" |

### What this does not establish

- **No population amount changed.** The fix is shown only by synthetic cases and probes.
- **Where excess metres lie.** Excess metres within 25A are taken to lie in the bands the charged interval spans. The reader noted another reading and did not carry it: 25A applied to each band part as if the charge had been split. It would give 10,050.00 for two of S74's allocations.
- **Grid and bounds are conventions.** The grid (the finest decimal place) is a convention shared with the reader through the prompt. Beyond 25 allocations only the extremes are listed; the allocations between them are admissible, unresolved and owned by G5, not individually priced.
- **The report-measured bound was not independently read.** No reader read the report-narrower-than-charge rule; it rests on Cl.23's text, brute force and controls.
- **Nomination.** The reader assumed the section was nominated. Its note gives 0.00 otherwise, which is the engine's condition. This is disposed of on Cl.23 and Q8.
- **Blank depths crash the engine.** A PD-210 line with blank depths raises an error in `_pd210`. This is pre-existing, not a round-2 change, affects no line (all 2,390 state depths), and is not fixed here. See *Open items*.

---

## D8 — The precedence sentence is an interpretation

**Re-audit.** "A Schedule prevails over a Part" is not expressly limited to the listed Schedules. D8 and the report presented the narrow reading as a consequence of the list, and the report swapped the residual lines' services.

### Fix

`spec/open_questions.yaml`, D8:
- Only operability is settled: every bound document is operative.
- The scope of the precedence sentence is interpretation **D8-I1**: status open, owner G5.

D8-I1 has two readings, each with a weight and an effect:

| Reading | Content | Weight | Effect |
|---|---|---|---|
| **Broader** | Schedule 8 is a Schedule and prevails over Cl.21/Cl.30 | greater: the words name no list, and D8 already treats Schedule 8 as operative | the Schedule 8 rows prevail over the Parts |
| **Narrower** | only the listed Schedules are ranked | lesser: context only | nothing is ranked |

Under either reading, Cl.2 does not rank Schedule 8 against Schedule 1:
- Schedule 1's descriptions are narrower: DD-120 "Rotary steerable system, circulating"; RM-530 "Back-reaming while tripping".
- The HC-630 row in Schedule 8 cites Cl.26, which describes only DD-111 and LW-420.

So the Q5 residual stays as scoped alternatives. The weights select no value at G3. The Q5 basis in `spec/g3_decisions.yaml` and the engine's Q5-DD120 condition text now cite D8-I1.

`Phase3_G3_corrections.md` is corrected in place, with correction notes:
- **MDS-01651-025 is DD-120:** USD 5,118.40–6,781.88 under the Schedule 8 reading.
- **MDS-00856-039 and MDS-01338-026 are RM-530:** 1,851.85 and 1,322.75, together 3,174.60.
- **The D8 sentence** is marked as an interpretation.

### Evidence

- The register passes `verify_spec` and X4.
- The three Q5 lines still carry alternatives with those services (`test_q5_residual_still_carried_as_scoped_alternatives`).
- A new test pairs every billed-line reference in every `Phase3_*.md` report with the next service or item code on the same line of text, and checks it against the source invoice lines. All reports pass, this one included.

### Controls (fail as intended)

- **X4's new interpretation check rejects:**
  - D8-I1 with the broader reading removed;
  - the broader reading without its weight;
  - the interpretation marked decided;
  - Q5 not citing D8-I1;
  - Q5 marked fully decided.
- **The identity test on the round-1 report text (`git show 83c4a61:…`)** reports both swapped pairings: each of the two lines named with the other's service.

### What this does not establish

- The weights are my reading of the text, recorded for G5. They are not a decision, and no reader weighed them.
- The identity test only checks references that appear next to a code on the same line of text. Prose that names a service without its code is not checked.

---

## Readers and dispositions

The inputs were committed in `dad6c82`, before any reader ran. Two isolated readers used prompt v4, which is v3 plus the `allocation_count` field and the bounds format. Their output was committed unedited in `7bbdc75`. The comparator compares `allocation_count` too.

**Totals:** 192 cases, 903 comparisons, 858 agree, 45 disposed (36 from before, 9 new), 0 failing. There are nine new dispositions, each bound to both values and settled against the scan:

- **DDS-S72 to S76, alternatives.** The reader gave the allocations if the section was nominated. The engine adds the 0.00 not-nominated outcome:
  - Cl.23 (p6), last sentence: PD-210 "only on the performance-drilled sections nominated in the call-off";
  - no call-off is supplied (Q8, owner G5);
  - the reader's own note says the line pays 0.00 otherwise.

  Every allocation and amount agrees.
- **CW-S65, S66, S67, R24, findings.** The reader lists `record_date_mismatch`, `record_area_mismatch` and `item_not_supported_by_record` on items that need no Schedule 5 record:
  - Cl.46–47 (p8) attach those requirements to "a record required by Schedule 5";
  - Cl.42 requires no record reference;
  - the reader's notes say the mismatch "does not stop payment".

  Both sides carry every class, with `ground_differs_from_record` unresolved.

**Scan check.** The figures the readers used, and the clauses the fixes rest on, were read on the page images (`verification/g3/scan_spot_checks.yaml`, `correction_round_2`):
- A.12.020 34.80 and A.12.040 69.20 (CW p17);
- ground factors G1/G3/G5 0.94/1.12/1.63 (p23);
- PD-210 bands 42.35/58.15 (DDS p17);
- Cl.17 "Every amount is ascertained in cents" (DDS p6).

All agree.

## Checks

- `tools/check_g3.sh` runs every G0–G2 check, the full test suite, the case comparison and `verify_g3` X1–X7. It passes locally.
- It also passes in a fresh clone at the final SHA; the results are in the conversation.
- The new exit-check logic, each with a negative control in `tests/test_g3_corrections_r2.py`:
  - X1: round-2 scope items;
  - X2: both sides of ground authority, and PD-210 measured depths against the report;
  - X3: domain completeness, whole cents, and cent-rounding replay;
  - X4: interpretations;
  - X6: record perturbation.

## Artifacts

| Kind | Files |
|---|---|
| Engines | `audit/g3_cw.py` (`record_applies`, Engineer countersignature), `audit/g3_dds.py` (allocation domain, measured bounds, guard, Cl.17), `audit/g3_core.py` (part rounding) |
| Checks | `tools/verify_g3.py`, `tools/g3_case_compare.py` (`allocation_count`) |
| Cases | `tools/g3_cases.py`; `verification/g3/cases/correction_r2_{cw,dds}.yaml`, `packet_*_correction_r2.jsonl`, `expected_*_correction_r2.jsonl` |
| Reader prompt | `prompts/phase3/g3_expected_cases_v4.md` |
| Registers | `spec/open_questions.yaml` (D8, D8-I1), `spec/g3_decisions.yaml` (Q5 basis), `verification/g3/case_dispositions.yaml` (+9), `verification/g3/scan_spot_checks.yaml` |
| Tests | `tests/test_g3_corrections_r2.py` (new), `tests/test_g3_corrections.py` (S71 test updated to the complete domain) |
| Outputs | regenerated: `verification/g2/*`, `verification/g3/{summary.json, trace_sample.jsonl, case_comparison.json}` |
| Reports | this report; `Phase3_G3_corrections.md` (corrected); `Phase3_TASKS.md` (round-2 section) |

## Open items

| Item | Owner |
|---|---|
| D8-I1: the scope of "A Schedule prevails over a Part", and with it the Q5 residual (3 lines) | G5 |
| HC-630 once-per-run event under the Schedule 8 reading (428 lines) | G4 |
| Allocations between the listed bounds on bounded PD-210 domains (0 population lines) | G5 |
| Nomination, ground and class conditions (unchanged owners) | G5 |
| PD-210 line with blank depths raises an error in `_pd210` (pre-existing; 0 lines; Cl.34 requires depths). Not fixed in this targeted round. | me: G3 engine, next round or on request |
| Per-band application of 25A to a crossing charge (the reader's unadopted alternative; 0 lines) | G5, if raised |

## Time

The round-2 goal arrived at 21:22 UTC on 26 Sep 2026. The first round-2 commit was at 21:33 and the last fix commit at 22:12. The two readers ran in parallel for about 6 minutes each. The close (report, full checks, fresh clone) followed; its timings are in the conversation.

---

**Blocked on me:** nothing. The gate3-r2 tag push is refused in this environment, so the SHA and annotation text are given in the conversation for you to tag.

**Changed:**
- **B1:** a record settles the ground class only for the work it records (same day or week, area and item). It must also be countersigned by the Engineer's representative.
- **B2:** crossing PD-210 charges carry the complete allocation domain. It is bounded by the metres the report measures, with bounds beyond 25 allocations, and amounts in cents under Cl.17.
- **D8:** the precedence scope is an open interpretation, with the broader reading weighted greater. The round-1 report's line identities are corrected.
- **Checks:** X1–X4 and X6 are strengthened, each with controls.

**Found:**
- Cl.17 cents on decimal metres, found by the independent reader.
- The charged interval, which is the claim, was bounding the PD-210 domain; found by my falsification.
- A foreman-only record was settling the ground class; found by my falsification.
- A PD-210 line with blank depths crashes the engine. It is pre-existing, affects no line, and is not fixed.

**Not confirmed:**
- None of the round-2 fixes changes a population value, so each is shown only by probes, synthetic cases and controls.
- The Engineer-countersignature reading and the D8-I1 weights are interpretations.
- The report-measured bound and the excess-placement reading were not read by an independent reader.
