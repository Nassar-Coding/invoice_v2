# Phase 3 — G3 correction round 3

**Scope.** Targeted fixes for the independent re-audit `Phase3_G3_reaudit_r2_Agent2.md`. It found G3 NOT PASS at `3c308ab` (gate3-r2):
- B1, B2 and D8/Q5 closed;
- one blocker open (§6): a PD-210 charge with a blank start or end depth crashed the engine.

The round's goal added a second fix. Every field G2 can leave None or unresolved, in every civil and drilling code family, is run through the G3 engines and the batch with that field empty. Each case must give an explicit result, never an exception or a silent default. The sweep is kept as a permanent X-check that the old engine must fail.

**Boundary.**
- No G4: no band allocation, caps, cross-invoice state, duplicates, or run or well lifecycles.
- No classification, flag, total or `submission.csv`.
- No tag was moved.

**Sources.**
- Implementation: `main` of Nassar-Coding/invoice_v2.
- Challenge, pinned: majedzahrani3/invoice-auditing-level-2 @ `aef4924dc32506b4587de8b788b5a947e6beffec`, verified by G0 against its manifest on every run.
- Clauses used: DDS-2025-118 Cl.34 (p8), the drilling guidelines principle 3 and check 12, and the clauses cited on each result.

**Base.** `main` = `origin/main` = `3c308ab`, clean tree, at the start. Round-3 commits, in order:

| Commit | Content |
|---|---|
| `07d61b0` | Fix 1: a PD-210 charge without its depths |
| `1e62a6a` | Fix 2: the nullable-field sweep; engine crashes and silent defaults fixed; X8 |
| `ed7ba60` | Fix 2 follow-up: defects found by trying to break fix 2 (the output stage, batch keys, report identity, dominance); X8 widened |
| `b3a39e4` | Fix 2 follow-up: a header number that two rows carry |
| `89d3202` | this report, first version; task list |
| `cdcd355` | the case-path control corrected (section 3, item 9); this report updated |
| `78f3ae6`, `bc61a20`, `f39f862`, and the final commit | T3 ticked after the fresh-clone run of `cdcd355` passed; report wording and corrections (a run time, test counts, this table). These change only this report and the task list. |

**Result.**
- **Fix 1.** A PD-210 charge missing its start depth, its end depth or both returns an explicit `depths_missing` finding. The result is unresolved, with its source line, reason and owner (G5). This holds on the case path, through the typed G2 loader and in the batch. Facts that hold for every possible interval are kept. The gate3-r2 engine raises `TypeError` on the same probes.
- **Fix 2.** Every input G2 can leave empty or unresolved gives an explicit result through both engines, the batch and the output stage, in all 18 code families. That is 12,230 input states and 200 batch runs, with 0 failures. The gate3-r2 engines fail the same check 3,212 times.
- **Falsification.** Trying to break my own fixes found nine more defects, including a crash in the output stage and a control of mine that passed for the wrong reason. All are fixed, each with a control.
- **Checks.** All G0–G3 checks and 272 tests pass. The fresh-clone run at the final SHA is reported in the conversation, because a report cannot carry its own commit.

---

## 1. Fix 1 — a PD-210 charge without its depths

**Re-audit (§6).** Two probes crashed the gate3-r2 engine with `TypeError` in `_pd210`:
- DDS-S72 with `depth_from_m = None`;
- the real line MDS-00018-023 with its start depth set to None in the batch.

Cl.34 (p8) requires a PD-210 charge to state "the depths at which the charged interval starts and ends".

### Fix

These are the changes in `audit/g3_dds.py` (`_pd210_depths_missing`, `_unresolved`) and `audit/g3_core.py` (`Inputs`, `LineResult.input_gap`):

- **Finding.** Each missing depth is an input check with finding `depths_missing` (Cl.34 p8). The check names the depth that is stated, if any, and the line's G2 source (`file:line`).
- **Value.** The value is unresolved:
  - `amount_status` is `unresolved` and `payable` is None;
  - there is no amount, quantity, rate or alternative;
  - the reason reads "… not guessed from the report, not zero";
  - the conditions are `input` (owner G5, basis Cl.34) and, as before, the `nomination` condition (G5).
- **Kept.** What holds for every interval inside the report's measured interval stays on the result:
  - the report's interval, the metres drilled on the day, and the bands with their rates;
  - a charge above the day's metres (`quantity_above_report`, 25A);
  - the rate where the whole day lies in one band (`rate_differs`, or a pass).
- **Established consequences still decide.** For example, a section that is not performance-drilled is not payable whatever the depths.
- **Batch.** An error on one line becomes an explicit `engine_error` result, which X3 rejects. The other lines carry on.

### Evidence

| Probe | Path | Result |
|---|---|---|
| DDS-S72, start None | case path | unresolved; "depth_from_m: the charge states no start depth (it states depth_to_m 1550)"; conditions input and nomination, both G5; kept: "the report measures 1450-1550 m, 100 m drilled on the day, in band 1 (1450-1500 m) at 42.35, band 2 (1500-1550 m) at 58.15" |
| DDS-S72, end None | case path | the same, "no end depth (it states depth_from_m 1450)" |
| DDS-S72, both None | case path | two `depths_missing` checks, the same unresolved result |
| MDS-00018-023, start None | population batch | was conditional at USD 8,838.80 if nominated; now unresolved; "[drilling_services/invoices/invoice_lines.csv:665]"; 0 other lines changed |
| MDS-00018-039, end None; MDS-00018-054, both None | population batch | were USD 9,827.35 and 9,594.75; now unresolved; sources csv:681 and csv:696 |
| the same three lines, cells blanked in a copy of the snapshot CSV | the real G2 loader (typed None, queued "required field blank"), then `g3_dds.run` | the same results; the other 91,241 drilling lines are unchanged |
| DDS-S68 (report 2,900–3,000 m, band 2 only), start None, 150 m at 76.45 | case path | unresolved, and `quantity_above_report` and `rate_differs` stay findings |
| DDS-S68, end None, 100 m at 58.15 | case path | unresolved; neither finding |
| DDS-S72, start None, section 17-1/2" | case path | not payable (`not_performance_section`) |

The DDS-S72 packet has no description field, so the case path also shows `claim_field_missing` for the description (Cl.34). The population lines have descriptions.

### Controls (fail as intended)

- The gate3-r2 engine, called as it was designed, values the complete DDS-S72 case. On all three depth probes it raises `TypeError: '>' (or '<') not supported between instances of 'decimal.Decimal' and 'NoneType'`.
- It stops its batch on the blanked snapshot with the same error.
- X3 rejects a contained `engine_error`.

The tests require these exact errors (see section 3, item 9).

These are in `tests/test_g3_corrections_r3.py`.

---

## 2. Fix 2 — every input G2 can leave empty or unresolved (X8)

### Inventory

The inventory is G2's own, never a hand list:
- every column of the four claim files (`audit.claims.FILES`);
- every key of the civil record layout and of the drilling report (`spec/evidence_cw.yaml`, `spec/evidence_dds.yaml`), found by mutating each sample document as text and re-parsing it with the real G2 parsers. Every empty value and queue entry is therefore exactly what G2 hands over.

Empty values are the ones G2 leaves: typed fields are None; text fields are `""`, or None for a short row.

| | Claim line | Header | Document keys | Parts / headings | Families |
|---|---|---|---|---|---|
| Civil | 15 | 13 | 11 (record keys, title, narrative, both signatures, Days on) | — | 6: CW-MEAS, CW-REC, CW-SURV, CW-WEEK, CW-HOUR, CW-UNSCHEDULED |
| Drilling | 16 | 14 | 36 (header 5, signatures 2, part keys 29) | 5 / 5 | 12: DDS-PERSONS, -COORDINATOR, -TOOL-DAY, -WELL-EVENT, -COUNTS, -RUN-EVENT, -HOURLY, -PERFORMANCE, -METRES, -LOSS, -DISCOUNT, -UNSCHEDULED |

The sweep also covers these states:
- a document key dropped, garbled, or written twice (G2 keeps the last value and queues it);
- list entries G2 cannot recognise: a tool term, a crew entry, a day worked;
- the line's header not found;
- the line reference emptied (G2 then identifies the row by `file:line`), or shared by two lines;
- a report number carried by two files;
- a header number carried by two rows.

**Sample.** 142 lines:
- the first line of every billed code;
- the first line showing each input-sensitive feature: night work, each zone, rest day, a protected submission, a record, each status and hole section;
- the first line showing each thing the output stage's decision scopes select on: each finding, alternative dimension, question reading and amount status;
- a line built from a real one with its code replaced, for each of the two families no line is billed in (Z.99.999 and ZZ-999).

Every claim field is emptied on at least one line of every family. X8 asserts this coverage itself.

**Criteria.** Any one of these is a failure:
1. An exception, or an `engine_error`.
2. An input matters to the line's value, and the result does not name it; or it fixes a value anyway; or it makes the line not payable without the contract's own rule for that absent input. "Matters" means an admissible other value of the input changes the value. That is established by probing with other values from the population, date shifts, the document's own date, one code per family and unit, Appendix G tool terms, and crew terms. The contract's rules for absent inputs are record or report missing or unsigned, and a required part missing.
3. An input does not matter, yet emptying it changes the value ("a known value lost"). There is one exception: the keys that join a line to its header, or a report to the lines citing it. Emptied or repeated, the joined document is no longer attributed to the line, and G3 never attributes a document by its content. For those keys the result must still be explicit.
4. The batch fails to complete, fails to give every line its own result, or gives a result that differs from the direct evaluation of the same inputs.
5. The output stage (`audit.g3_run`) fails to complete over each batch's results. It must also count every line once, and compare no rate for a line that has no value at G3. A decision scope that reaches such a line must list it as not valued instead of counting it.
6. Coverage fails, as defined above.

### Result

**Current engines.** 12,230 input states, 0 failures:

| Outcome | States |
|---|---|
| unresolved and named | 2,192 |
| not payable by the contract's own rule for that absent input | 159 |
| carrying every value the input could take | 9 |
| unchanged (the input does not matter to that line) | 9,870 |
| out of scope (G2 accepted a garbled value as a value) | 359 |

There were also 200 batch runs, each through the output stage.

**The gate3-r2 engines (`3c308ab`)** fail the same check with 3,212 errors:
- 1,380 states raise an exception, across 25 inputs:
  - civil: application date, period from and period to, the application number empty or repeated, line amount, quantity, rate and work date;
  - drilling: invoice date, period start and end, the invoice number empty or repeated, both PD-210 depths, quantity, service code, service date and unit rate, the report's depth start and end, the Part E circulating hours, and Part A dropped or its heading garbled.
- 1,795 states across 47 inputs fail criteria 2 or 3: handled silently, fixed by a default, rejected without a rule, or (2 states) a known value lost. Examples:
  - a blank civil unit treated as `wrong_unit`;
  - a blank zone or night-work statement priced anyway;
  - an unreadable status, section, crew or tool list, or report Date, taken as a value or ignored;
  - signatures and missing parts decided without naming the input.
- 37 batch runs fail.

### What fix 2 changed in the engines

These are the changes in `1e62a6a`:
- **Inputs.** Both engines read every field as a G2 input that may be empty (`g3_core.empty`). A gap is recorded with its provenance (`Inputs`: line, header and document sources, the document's queued and twice-written fields). It is never replaced by a default.
- **Unresolved value.** A value that depends on a missing input is unresolved (owner G5, with the reason). Every check that does not need that input still runs, and an established not-payable consequence still decides the line.
- **Relevance is decided, not assumed.** Where an input can only matter in some cases, the engine checks whether it does:
  - submission-date protection (31A/36A) is tested between "after every issue" and "on the work date";
  - the night uplift is tested both ways;
  - status is needed only where it prices the service;
  - hourly services are brute-forced over 0–24 hours and the run's first-day variants;
  - Days on matter only below five readable days;
  - tool and crew entries matter only if the service's tool is not found, or the crew recorded is below the charge.
- **Twice-written keys.** A key written twice is taken from neither copy.

---

## 3. Falsification of fixes 1 and 2 — found and fixed

After each fix I tried to break the completion claim, including branches no case exercises:
- pairwise and all-empty claim fields on every sample line: 49,032 evaluations;
- a population-wide fuzz, in which every line has one field emptied and every document one key line dropped: 98,990 lines, 10,320 documents;
- identity states: shared line references, and repeated report and header numbers.

These found the defects below. Items 1–8 are fixed in `ed7ba60` and `b3a39e4`, and item 9 in the close commit. Each has a regression test and a control in `tests/test_g3_corrections_r3.py`. The output stage (`audit/g3_run.py`) was not changed by fixes 1 and 2, so the gate3-r2 output stage is also the one they left in place.

1. **The output stage crashed.** `g3_run.decision_scopes` raised in four cases:
   - `TypeError` on an empty billed quantity (Q3 reading B);
   - `KeyError` on a blank line reference;
   - `KeyError` on a shared line reference;
   - `ValueError` when re-pricing a zone line that was unresolved.

   **Fix:** every lookup follows the batch key; a missing quantity or rate lists the line as not valued.
2. **Lines with no value were valued as 0 or dropped.** Unresolved lines, and deferred lines (DS-900), were counted as 0 in decision-scope values. Q3 reading B also left out three civil lines whose rate is conditional (PA-00111-13, PA-00609-01 and PA-00613-01), so B understated SAR 258,170.41–282,470.38 as 213,426.16. The summary counted the 63 DS-900 lines as "rate not single".

   **Fix:**
   - each result carries the rate domain its rate check formed (`LineResult.rates`), and reading B prices every line at every admissible rate;
   - a scope lists its unvalued lines by status (`lines_not_valued`);
   - the summary counts a line with no value at G3 as `value_not_formed` (the 63 DS-900 lines), and a line whose rate was never formed as `rate_not_formed` (1 line: MW-310, out of term). Both used to be counted as "rate not single".
3. **The batch could drop a line.** Two lines sharing a `line_ref` replaced each other's result, and the second line's provenance was attached to the first. A blank reference was keyed inconsistently.

   **Fix:** `g3_core.result_keys` keys a line with no reference, or a shared one, by its source position, for results and Inputs alike.
4. **A report number carried by two files was resolved silently.** G2 indexes the first file and queues the second, and the engine used the first.

   **Fix:** the charge is unresolved and names both files (owner G5). No fact is taken from either file. Unindexable files now come from G2's by-file index. A charge that cites no report is `report_missing` even when some other file cannot be indexed.
5. **A header number carried by two rows was resolved silently.** The engine used the last row.

   **Fix:** `g3_core.headers_by_id`. The line takes no header fact from either row and names both rows.
6. **Established consequences were hidden in three places.**
   - A twice-written foreman line hid a missing Engineer's countersignature.
   - An empty or unscheduled civil item code hid an established out-of-term.
   - An unscheduled drilling code did the same.

   **Fix:** each is now not payable. An empty drilling code stays unresolved even out of term, because it may be the invoice-level DS-900, which no finding on the day decides (Cl.38).
7. **X8 itself was weaker than it claimed.**
   - Its sample did not reach the decision scopes.
   - Its "line_ref empty" batch run did not empty `line_ref`.
   - The code probe only ever tripped the unit rule, because it used codes in other units.
   - Date probes lacked the document's own date.
   - A not-payable line's rate and route counted as its value.

   **Fix:** all corrected. X8 now also runs the output stage and asserts coverage.
8. **The flag for unindexed reports was over-broad.** It counted duplicate-number queue entries as unindexable files.

   **Fix:** the flag now comes from G2's by-file index (files with no report number).
9. **A control of mine passed for the wrong reason.** Since fix 1, the case harness (`tools/g3_case_compare.py`) passed the new `inputs` argument unconditionally. The case-path control therefore raised `TypeError: evaluate() got an unexpected keyword argument 'inputs'` from the gate3-r2 engine, not the depth crash it was meant to show. It could not tell a guarded engine from an unguarded one.

   **Fix:**
   - the harness passes `inputs` only to an engine that takes it, as X8's adapter does;
   - the control first shows the gate3-r2 engine values the complete case, then requires the depth error itself;
   - the other two exception controls (the gate3-r2 batch, and the gate3-r2 output stage on an empty quantity) now also require their exact errors, and the output-stage control first shows that stage completing on the complete world.

---

## 4. Controls (fail as intended)

| Check | Control | Result |
|---|---|---|
| Fix 1, case path and batch | the gate3-r2 engine, called as designed | values the complete case; `TypeError … 'decimal.Decimal' and 'NoneType'` on each depth probe; its batch stops with the same error |
| X3 | a contained `engine_error` | rejected |
| X8, whole | the gate3-r2 engines | 3,212 errors (above) |
| X8 criterion 2 | an engine that fills a blank zone with Z1 | "does not name it (silent)" |
| X8 criterion 2 | the same default, named in a reading | "fixes a value" |
| X8 criterion 3 | an engine that makes a line unresolved on an input that does not matter | "a known value lost" |
| X8 criterion 4 | a batch that drops the lines with an empty quantity | "results for" |
| X8 criterion 4 | a batch that drops G2's provenance | "differs from its direct evaluation" |
| X8 criterion 5 | the gate3-r2 output stage | `TypeError` (empty quantity), `KeyError` (blank reference), and "the summary compares or values … lines that have no value at G3" |
| X8 criterion 5 | a scope that hides unvalued lines | "reaches N line(s) … lists 0 as not valued" |
| X8 criterion 6 | a family on which a field was never emptied | a coverage error |
| X8, report identity | the gate3-r2 drilling engine (takes G2's first file) | "doc Report='repeated'" failure |
| Batch keys | the gate3-r2 `run()` on two lines sharing a reference | 3 results for 4 lines |
| Header number repeated | the `ed7ba60` engine (takes the last row) | uses a header fact |
| Dominance, signatures | the `1e62a6a` engine | unresolved where not payable is established |
| Q3 reading B | the gate3-r2 `evaluate_as_payable` | None for the three conditional-rate lines |
| A line with no value | the gate3-r2 `_money` | values a DS-900 line at "0" |

---

## 5. Regression

- **B1, B2, D8.** `tests/test_g3_corrections_r2.py` passes: 59 tests (32 test functions, some parametrized), including their controls.
- **F1–F4, Q5, D1, X4.** `tests/test_g3_corrections.py` passes: 22 tests.
- **Round 3.** `tests/test_g3_corrections_r3.py` passes: 32 tests.
- **Population against gate3-r2** (`3c308ab`), on all 98,990 lines: every value, status, payability, finding code, reason, alternative and trace is identical. The only differences are:
  - the new rate domain on each result (7,746 civil and 91,180 drilling lines; the other 64 have no rate formed: 63 DS-900 lines and 1 MW-310 line out of term);
  - 41 check details reworded (8 civil, 33 drilling), so that `record_missing` names the `record_ref` and an unsigned finding names the signature line.
- **Population against `ed7ba60`:** identical.
- **Case comparison:** 192 cases, 903 comparisons, 858 agree, 45 disposed, 0 failing. Unchanged.
- **Outputs regenerated:**
  - `verification/g3/decision_scopes.json`: Q3 reading B SAR 213,426.16 becomes 258,170.41–282,470.38;
  - `verification/g3/summary.json`: 63 lines are `value_not_formed` and 1 is `rate_not_formed`, both formerly `rate_not_single`;
  - `verification/g3/trace_sample.jsonl`: rates added;
  - `verification/g2/{run_context,coverage,conflicts}.json`: the run-context id, since the code changed.
- **Gate.** `tools/check_g3.sh` runs G0, G1, G2, the full test suite, the case comparison and `verify_g3` X1–X8. It passes locally at `b3a39e4` with 272 tests, and in fresh clones of `89d3202` (596 s) and `cdcd355` (605 s). The run at the final SHA is in the conversation.

---

## 6. What this does not establish

1. **No population line has an empty input.** Every empty-input behaviour is shown on probes, the 142-line sample, pairwise and all-empty evaluations, and the fuzz. None of it is shown on real data.
2. **Relevance is probed, not proven.** "The input matters" and "nothing lost" rest on the probe values. An effect that no probe reaches is judged irrelevant. The value must then stay unchanged, but X8 would not demand "unresolved" for it.
3. **Some inputs are outside the sweep because of G2's limits:**
   - a garbled value G2 accepts as a value (359 states; for example a report `Well: ??`, a `??` signature line read as signed, or `Report: ??`);
   - report header keys written twice, which G2 does not queue;
   - G2 conflicts, as opposed to unresolved fields (for example a Days on entry outside its week).
4. **Identity is never inferred.** When G2 no longer attributes a document or header to a line (an unindexable report, or a report or header number carried by two rows), the line is unresolved. That holds even where every candidate would give the same value; "not payable whichever file it is" is not concluded.
5. **Interpretations, not confirmed by the contract owner:**
   - Missing inputs become unresolved with owner G5 (a query to the contractor). This follows your instruction and the drilling guidelines principle 3 and check 12.
   - An empty drilling code stays unresolved even out of term, on the Cl.38 reading of DS-900.
6. **Some states are rejected by G2's own gate.** Duplicate line references, duplicate header numbers, and reports not indexed exactly once all fail G2's E1. G3 handles them explicitly anyway, but through a passing G2 they never reach it.
7. **No independent reader read the missing-input cases.** This round had no reader round.
8. **Coverage is by sample.** The sample is the first line per code, feature and scope selector. The fuzz empties one field per line, not every field on every line.
9. **Q3 reading B is a bound for band-rated lines.** It prices a band-rated quantity at its lowest and highest admissible rate. The division at a band edge is G4 state.

---

## 7. Time

| Event | UTC, 27 Sep 2026 |
|---|---|
| Round-3 goal arrived | 06:18 |
| Fix 1 (`07d61b0`) | 06:36 |
| Fix 2 (`1e62a6a`) | 07:28 |
| Fix 2 follow-up (`ed7ba60`) | 08:33 |
| Fix 2 follow-up, header numbers (`b3a39e4`) | 08:51 |
| Report, first version (`89d3202`) | 08:53 |
| Control corrected (`cdcd355`) | 08:58 |
| Fresh clone of `cdcd355`: `check_g3.sh` passed (272 tests, X1–X8) | 08:58–09:08, 605 s |
| Task list and report corrections (`78f3ae6`, `bc61a20`, `f39f862`) | 09:08–09:11 |
| Final commit; fresh-clone run at the final SHA | in the conversation |

Each local `check_g3.sh` run takes about 9 minutes, of which the full test suite is 8 minutes 17 seconds. X8 takes about 35 seconds.

---

**Blocked on me:** nothing. Tag pushes are refused in this environment, so the gate3-r3 SHA and annotation text are given in the conversation for you to tag.

**Changed:**
- **Fix 1.** A PD-210 charge without its start depth, end depth or both is an explicit unresolved result: `depths_missing` (Cl.34), the source line, the reason, and owner G5. Facts that hold for every interval are kept; the interval is never guessed and never zero. The batch contains line errors.
- **Fix 2.** Every input G2 can leave empty or unresolved is recorded with its provenance and never defaulted, in both engines, the batch and the output stage. Report and header identity, and batch keys, are never resolved silently. X8 checks this permanently: 12,230 states, 18 families, 200 batch runs, with coverage asserted.

**Found:**
- **By the sweep:** 25 inputs that crashed the gate3-r2 engines, 47 handled silently, and 37 failing batch runs. All are fixed.
- **By falsifying my own fixes:** the output-stage crash, lines with no value counted as 0 or dropped (Q3 reading B understated), batch key collisions, report and header numbers resolved silently, three hidden established consequences, weaknesses in X8 itself, and a case-path control that passed for the wrong reason. All are fixed.

**Not confirmed:**
- No real line exercises an empty input.
- Relevance rests on probes.
- G2's accepted garbled values, unqueued repeated report header keys, and G2 conflicts are outside the sweep.
- The owner-G5 treatment and the DS-900 reading are interpretations.
- No independent reader read the missing-input cases.
