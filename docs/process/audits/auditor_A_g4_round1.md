# Independent audit of G4 (chronology and shared state), commit 1f797bf

**Verdict: G4 is not closed.** I found 5 blockers. Four of them (A-1, A-2, A-3, A-4) pass every G4 exit check in `tools/verify_g4.py`. A-4 is caught only by the Y8 dependency-coverage check, and only when such an input is in the population being run. The fifth blocker (A-6) passes every exit check.

All inputs are raw same-format histories run through the production loader: `g4_histories.materialize` → `audit.build` → G3 → G4, with G5 where stated. Every script is under `/tmp/auditA/_audit/`. Run each with `cd /tmp/auditA && INVOICE_SNAPSHOT=/home/user/majedzahrani3/invoice-auditing-level-2 python _audit/<script>`. Shared helpers are in `_audit/lib.py`.

## Findings

### A-1 — BLOCKER (b); frozen blockers G4-B02 and G4-B03
**Issue:** a PD-210 charge with no depths is never treated as a possible charge of the same metres as a charge on the same well-day.

- **Script:** `_audit/a1_depthless_dup_g5.py`
- **Input:** one daily drilling report, NGP-ZZ-972, 01-Jul-2025, drilling 1500–1600 m (100 m).
  - MDS-97201 (earlier invoice, 05-Jul): PD-210, 100 m, dated 01-Jul, `depth_from_m` and `depth_to_m` blank.
  - MDS-97202 (12-Jul): PD-210, 01-Jul, 1500–1600, 100 m.
  - Both at the correct rate of 58.15. That is 200 m charged for a day that drilled 100 m.
- **Observed:**
  - MDS-97202-001 gets a G4 value of 5,815.00 with status `conditional` (on nomination only).
  - No PD-210 allocation group is formed and there is no `charged_twice` state.
  - G5 returns MDS-97202 as **flag 0, 6,687.25, confidence 0.80, no open readings**.
- **Control:** if the earlier charge states 1500–1600, G4 carries the allocation, and G5 flags MDS-97202 as the later charge and returns expected 0.00.
- **Expected:** the charge without depths can only cover metres inside the day's report interval, which here is exactly MDS-97202's interval. So MDS-97202-001 should carry a 0 alternative and an unresolved `charged_twice`.
  - Contract basis: Cl.29 (p7), PD-210 may be charged more than once a day only for different depth intervals; Cl.23 (p6); Cl.34 (p8).
  - Frozen audit: G4-B02 closure (a complete joint domain over interval coverage) and G4-B03 closure (unknown data stays a candidate everywhere).
- **Where:**
  - `audit/g4_dds.py:414-439` builds segments only from charges that have both a date and depths.
  - `:443-461` treats a charge missing either as an annual-footage contributor only.
  - `:270` makes `_undated_repeats` skip PD-210 explicitly.
- **Population:** none. There are 0 PD-210 lines without depths, so this is an unseen-input defect.

### A-2 — BLOCKER (b); G4-B01 and G4-B03
**Issue:** a PD-210 charge whose admissibility G3 left unresolved is counted as certain prior metres in the annual footage.

- **Script:** `_audit/p3_unresolved_prior.py`
- **Input:**
  - MDS-97301: 01-Jul-2025, PD-210 4500–44490 (39,990 m). Its report has a blank `Status:`, so G3 returns payable=None.
  - MDS-97302: 02-Jul, PD-210 44490–44510, billed 1,974.00.
- **Observed:**
  - MDS-97302-001 is determined at 1,934.50.
  - It carries an established finding (`footage finding footage_band_divided`).
  - The accumulator's range is [39990, 39990].
  - G5: flag 1, confidence 0.60, no open readings.
- **Comparison run:** set that report's status to `Standby`. The first charge becomes not payable (G3 payable=False). The second is then Q11 A 1,974.00 / Q11 B 1,934.50, and G5 returns flag 0 at 0.80.
- **Expected:** with admissibility unknown, the Q11 A value is either 1,934.50 or 1,974.00, and the band division is not established.
  - The engine's own Q11 A basis is "the union of the admissible PD-210 intervals" (the `_pd210` docstring).
  - The civil engine (`_counted`) already treats a G3-unresolved line as a range, (0, qty).
  - Frozen audit: the G4-B01 closure requires admissible metres counted exactly once; the G4-B03 closure says "determined only where the missing datum provably cannot change it".
- **Where:** `audit/g4_dds.py:414` (`adm` means `payable is not False`) and `:457`. The Y3 check (`verify_g4._pd210_raw:285`) makes the same assumption.

### A-3 — BLOCKER (b); G4-B01 and G4-B03 (omission under Q11 B)
**Issue:** under Q11 B, a report whose Part A depth is not established is dropped, i.e. counted as zero metres.

- **Script:** `_audit/p4_q11b_report_gap.py`
- **Input:**
  - Day 0: 17-1/2" section, no PD-210, 4000→4500 m.
  - Day 1: PD-210 4500–44400.
  - Day 2: PD-210 44400–44420.
- **Complete reports:** the line correctly carries Q11:A 1,974.00 and Q11:B 1,895.00, with footage unresolved.
- **Day-0 `Depth end` blank or written twice** (G2 then reads None): the Q11 B prior footage is 39,900, the same as Q11 A, so the line collapses to a determined 1,974.00 and the Q11 alternative disappears.
- **Expected:** the day-0 metres are an unknown amount of at least 0, so Q11 B stays open or unresolved. Contract basis: Sch 2 Part 2 (p17), "metres already drilled on the well".
- **Where:** `audit/g4_dds.py:410-411` (the `reports` filter) and `:463-465`.

### A-4 — BLOCKER (b); G4-B03 (payment-history calculation)
**Issue:** the A3 difference account omits the protected lines of any application or invoice that has no submission date, and still states a single definite total.

- **Scripts:** `_audit/c1_cw_undated.py` (part C1) and `_audit/c1b_dds_a3_undated.py`
- **Civil, CW-H09 with PA-99001's `application_date` blanked:**
  - Account: 1 eligible line, total min = max = 117.80, `lines_not_established` 0.
  - With the date present: 489.80, which includes PA-99001-02.
  - The recipient is correctly shown as not established; only the amount is wrong.
- **Drilling, DDS-H05 with MDS-90041 undated:** total 72.00 instead of 147.00. Blanking MDS-90042 gives 75.00.
- **Expected:** the undated document may have been submitted before the instrument was issued, so its difference is a possible contributor. The total should be a range or not established, not a single figure. Contract basis: CW 31A (p32) and A3 (p43); DDS 36A (p35) and A3 (p42).
- **Where:** `audit/g4_cw.py:713` and `audit/g4_dds.py:631` select eligible lines only by G3's "31A/36A protection" reading, which a line of an undated document never has.
- **Mitigation:** the Y8 dependency-coverage check does flag this (unanswered `a3_adjustment`, plus an unanswered `daily_limit`), but only if such an input is in the population verified. The engine itself outputs the understated account silently.

### A-5 — NONBLOCKING, but high priority: the G4 run crashes
The failure is loud, so it does not meet the "silent" test in (b). However, the G4-B03 release closure is not demonstrated for this variant, and a crash stops output for every invoice.

- **Script:** `_audit/c1_cw_undated.py` (part C2)
- **Input:** CW-H10, plus PA-9A010 (B.22.010, 1,200 m² on 20-Dec-2025), plus an application with no `application_date` (PA-9A011: 100 m² on 10-Jan-2026, whose band depends on Q12).
- **Observed:** `g4_cw.run` raises `StopIteration` at `audit/g4_cw.py:915` (`pick = next(...)`). The possible-reading set `present` (`:901-904`) is built only from the dated earlier applications, so the undated one's Q12 labels never match.

### A-6 — BLOCKER (b)/(c); G4-B04 split-band variant
**Issue:** on a measurement divided across bands, a displayed rate belonging to no part of it passes.

- **Script:** `_audit/b04_split_rate.py` (uses the repository's own `cw_hist` and `_cw_outcome` from `tests/test_g4g5_corrections.py`)
- **Input:** B.22.010, 1,000 m² at 74.50, then 400 m² split 200 at 74.50 + 200 at 71.52 = 29,204.00 (correct amount). The displayed rate is **69.29**, the band-3 rate.
- **Observed:** `band_rate` pass, `band_arithmetic` pass; G5 returns **flag 0, confidence 0.95, no findings**. A non-band rate such as 72.00 is correctly a finding.
- **Expected:** in the established state the only applicable rates are 74.50 and 71.52. The closure says "a correct amount never makes a wrong rate pass". Contract basis: Cl.27–28 (p6); Sch 4 Part 3.
- **Where:** `audit/g4_cw.py:674` accepts any of the item's band rates (`ra in set(rates.values())`). The Y7 oracle at `tools/verify_g4.py:707` uses the same test, so it cannot detect this.

### A-7 — NONBLOCKING: Y4 fails on honest output
This is a false alarm, not a false pass.

- **Script:** `_audit/p6_nonexact_member.py`
- **Input:** a contested well-day where one charge bills 99 m for a 100 m interval (within the 1% tolerance). The engine honestly leaves that charge unresolved.
- **Observed:** `pd210_coverage_errors` reports "has no single kept quantity" and "100 m charged for 150 unique metres". Separately, days on which every member is unresolved are skipped without checking.

### A-8 — NONBLOCKING: several exit checks share the engine's assumptions or only check structure
This is why A-1, A-2, A-3 and A-6 pass the gate (shown by `_audit/oracles_on_findings.py`).

- The Y3 footage recount checks only the Q11 A lower bound. It uses the same `payable is not False` admissibility and never checks the upper bound or Q11 B.
- Y6's "a metre counted twice" footage check inspects only the engine's own non-overlapping segment keys. It can fail if the accumulator is tampered with (`_audit/y6_footage_check.py`), but never compares against physical intervals, and it has no negative-control test.
- Y7's `deferred_rate_errors` uses the same permissive rule for divided lines as the engine.
- Y2's `chronology_errors` does not check who contributes to the A3 account.

### A-9 — NONBLOCKING: over-conservative, but honest
- **Script:** `_audit/p1_pd210_loose.py` (case P1a)
- A PD-210 charge with depths but no date has no G3 allowed quantity, which sets the upper bound to None. That makes every PD-210 on the well unresolved, instead of bounding it by the billed quantity as the civil engine does. No value is silently wrong.

## Verified and found correct
- **Reproduction:** `python -m audit.build`, `python -m audit.g3_run`, `python -m audit.g4_run` and `python tools/verify_g4.py` all ran in 4m35s with run context `89f0c33608cd82ec`. Y1–Y9 passed, "G4 VERIFY OK", and `git status` was clean apart from `_audit/`. Log: `_audit/repro_run.log`.
- **G4-B01 and G4-B02:** the repository tests cover both B01 variants, replay after removal, the three-interval chain, and contained/exact duplicates. My own multi-day, multi-invoice fixture `_audit/p5_pd210_nest_gap.py` combines a nested interval, a partial overlap, a gap, an exact duplicate on another invoice, the 40,000 m edge and a later-day charge. All 8 allocations and every value match my independent interval computation under both Q11 A and B.
- **G4-B03 (civil bands):** an undated measurement across the Contract-Year boundary under Q12 is handled correctly, both where the line is provably determined and where it becomes unresolved (`_audit/c4_cy_undated.py`). The release recipient with an undated application, and the DDS undated repeat, are also correct.
- **G4-B04:** single-band rate and amount are judged independently. A split showing a band-1 or band-2 rate passes; a non-band rate is a finding.
- **Run events:** a DD-111 whose report is missing is rejected at G3, so there is no omission (`_audit/p7_run_unknown.py`).
- **Exit checks:** every Y check has negative-control tests in `tests/test_g4_gate.py`.

## Could not check
- **Full `tools/check_g4.sh` run** (G0–G3 checks plus the whole test suite): still running at hand-off. All G0–G3 checks it had run so far passed; the test suite was at 33% with 0 failures. Log: `_audit/check_g4.log`.
- **Impossible joint scenarios from undated measurements:** when one undated measurement is a possible repeat for several dated days, G4 labels each day's choice as independent, which allows combinations where it displaces more than one day. For drilling (`_audit/c3_undated_joint.py`), G5 settles which charge stands by its own policy, so nothing visible changes. The civil `earlier@…|undated` counterpart was not tested.
- **Other untested branches:** order/tie permutations inside civil band groups with more than two ties, and G5's handling of A-2 and A-3 under other adopted readings.

Nothing in `/home/user/invoice_v2` was read or modified.
