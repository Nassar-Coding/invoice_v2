# Phase 3 — G3 correction round 4

**Scope.** The final discovery audit `Phase3_G3_final_discovery_audit_Agent2.md` froze G3's blocker set at eight classes, FD01–FD08, at `6885224` (gate3-r3). This round closes them. Each FD's "Required closure" paragraph in audit §3 defines done. The audit's FD04 note also requires X8 to judge from source-derived evidence obligations instead of asking the engine what is relevant.

**Boundary.**
- No G4: no band allocation, caps, cross-invoice state, or run or well lifecycles.
- No classification, flag, total or `submission.csv`.
- No tag was moved.

**Base.** `main` = `origin/main` = `6885224`, clean tree, at the start. One commit per FD:

| Commit | FD |
|---|---|
| `fc6ff50` | FD01 signatures |
| `ef96add` | FD02 repeated evidence |
| `60e57c3` | FD03 civil item attributes |
| `431d9ed` | FD04 required-Part content, and X8 source-derived obligations |
| `c300833` | FD05 night work |
| `95f48b4`, `d10b090` | FD06 drilling arithmetic, and a follow-up found by the case comparison |
| `45bb8de` | FD07 allocation granularity |
| `a4fc597` | FD08 missing submission date |
| (close commit) | an interaction test; this report; task list |

**Method.** Every test runs the real G2 parsers on mutated source text (records, reports, claim CSV rows), then G3 on what G2 hands over. Each negative control runs the gate3-r3 code: its G2 parsers with the helpers they imported, and its engines, on the same input. The controls are in `tests/test_g3_corrections_r4.py`, 197 tests in all.

---

## FD01 — signature text is not approval

**Fix.** `audit/common.py` `signature_state` gives each signature line one of three states:

| State | What establishes it |
|---|---|
| signed | a personal name in the records' form: initials and surname, or given name and surname |
| unsigned | the line is missing, a placeholder, or its words say nobody signed (unsigned, not signed, N/A, pending, TBC, none …) |
| unknown | any other text (`??`, "illegible", digits, "Signed", "Pending Review") |

- Both G2 parsers carry the state and queue unknown text.
- G3 applies the contract's consequence to unsigned (`record_unsigned` / `report_unsigned`; DDS Cl.15, Cl.37; CW Cl.46–47, P22) and leaves unknown unresolved.
- A countersignature that is unknown does not make a record the Engineer's ground classification (B1). Every class is carried, and the gap is named.
- The case packets mask real names as `<signature>` (`tools/g3_cases.py _mask`). The harness restores a name in the source format before parsing.

**Variants covered.**
- 6 unreadable and 7 non-signing tokens × both signatory roles × both contracts, on the audit's lines MDS-00001-013 and PA-00001-04.
- Real names still sign.
- Ground authority on CW-S64: a named countersignature gives the determined G3; `??` carries all five classes. No population line takes its class from a record for an item without a Schedule 5 record, so this is shown on the case.

**Control.** On gate3-r3, `??` in either signature leaves MDS-00001-013 at USD 4,892.30 and PA-00001-04 at SAR 17,730.62, with no finding, condition or queue item. `??` is also the Engineer's approval on CW-S64.

**Not established.**
- The name pattern fits the records' own forms. A real signature written otherwise, for example a bare surname, would be read as unknown. That is conservative, but it would leave such a line unresolved.
- No signature is authenticated as a person's.

## FD02 — repeated evidence

**Fix.** Both parsers now collect every occurrence of every header key, signature, Part and Part key, and the civil narrative, then resolve:
- **Identical repetition** states one fact, read once (Sch 5 p24: one report per well-day).
- **Differing repetition** is queued as `key repeated`, and a whole Part as `part repeated with different content`. No value is taken by position (R8 p14).
- **Derived facts** (tools, crew, lost tool) are computed once, from the resolved values.

G3 reads the queue: a conflicting Date, Report, Well, signature or crew leaves the line unresolved.

**Variants covered.**
- A conflicting Date prepended and appended, meaning both orders.
- A conflicting Report and Well.
- Unsigned-then-named and named-then-unsigned signatures, on both contracts.
- Identical repeats of Date, a signature, Part A and Part B: the value is unchanged and nothing is queued.
- The audit's MDS-00001-010: Part A with one hand gives quantity 1 and USD 1,847.35 with `quantity_above_report`. The same result holds with Part A repeated identically. A differing copy gives unresolved in either order.
- A civil key in both orders.
- Part D certification written Yes in one copy and No in the other: unresolved in either order, never the No consequence.

**Control.** gate3-r3 keeps USD 4,892.30 in two cases: a prepended conflicting date, and unsigned-then-named. It counts an identical repeated Part A's crew twice (quantity 2, USD 3,694.70, no finding).

**Not established.**
- An identical duplicate is treated as one statement. A contractor who genuinely means two separate records cannot be told apart from a copy.
- A Part stated in one copy and absent from another is conflicting for its keys.

## FD03 — civil item-defining attributes

**Fix.** Each template in `spec/evidence_cw.yaml` states the value its candidate item's Schedule 1 description requires (pp17–18):

| Template | Attribute | Required value |
|---|---|---|
| PT1 | diameter | 1800 |
| PT2 | diameter | 400 |
| PR1–PR5 | concrete | 32/40 |
| JS1 | mesh | A393 |
| CT4 | sub-base | Type 1 |

- Numbers are compared numerically.
- A record stating another value evidences no candidate. G3 gives `item_not_supported_by_record`, naming the attribute and the required value, and never reprices the claim as another item.
- An unreadable value leaves the narrative unmatched: it is queued and the line is unresolved.

**Variants covered.**
- A matching, a different and an unreadable value for each role, on the audit's five lines (PA-00002-07, PA-00002-09, PA-00001-10, PA-00003-07, PA-00008-06).
- Every PR form × three grades.

**Control.** gate3-r3 keeps each changed specification's candidate, value and findings.

**Not established.**
- The unused-template attribute values match Schedule 1 in every supplied record, so the population never exercises a mismatch.
- A narrative whose shape no template knows remains unresolved (G2 queue).

## FD04 — required Parts: content and certification

**Fix.** For a Schedule 5 service, G3 checks every content line of its Part, whether or not the price uses it (Sch 5 p24; `spec/evidence_dds.yaml`):
- A line that is missing, unreadable or conflicting leaves the charge unresolved (owner G5).
- `Source handling certified: No` is a known failure: not payable, `source_handling_not_certified` (Cl.37; H6 p13).
- G2 now queues text with no word in it (`Sources handled: ??`).
- A tool list with recognised tools counts as recorded.
- Services whose condition of payment is another Part are untouched.

**Variants covered.**
- All 12 Schedule 5 codes × every content line of their Part, each missing and `??` (65 cases).
- The audit's LW-420 variants (No, `??`, blank, Sources handled removed), DD-111 without Run circulating hours, and LW-410 without Run last day.
- Five unrelated services on the LW-420 report are unchanged.

**Control.** gate3-r3 keeps LW-420 at USD 2,746.55 in every variant and DD-111 at USD 3,589.45. It keeps LW-410's valuation without a gap.

**Not established.**
- The Part contents are those Schedule 5 and the G2 layout list. A content requirement the contract states elsewhere is not added.
- Only Part D's certification has a known-failure value. A Part B with, for example, zero metres logged is content, not a failure.

## X8 — source-derived evidence obligations (audit FD04 note)

**Fix.** `tools/null_sweep.obligations()` derives each line's conditions of payment from the specs, never from the engine:

| Contract | Obligations |
|---|---|
| Drilling | the Schedule 5 Part's content lines, the Part, its heading, and both signatures |
| Civil | the Schedule 5 record's required lines, narrative, title and signatures |

- An obligated input that is emptied, unreadable or conflicting must leave a payable line unresolved and named, or apply the contract's consequence.
- "Nothing lost" applies only to inputs without an obligation.
- An appended unrecognisable list entry leaves the required line in place, so it is judged by relevance.
- X8 on the final code: 12,184 input states and 202 batch runs, with 0 failures.

**Control.** X8 fails the gate3-r3 engines with 207 errors, all ignored obligations (for example B.Run circulating hours and D.Sources handled). An engine-derived relevance test would have accepted them.

## FD05 — night work

**Fix.**
- **G2** (`claims.yes_no`) types `night_work` as Y or N only. Anything else is queued and handed over as None.
- **G3** treats every value other than Y and N as unknown. The uplift is priced both ways, and the line is unresolved, naming `night_work`, where that changes the rate.
- **Irrelevant cases stay determined.** That covers an item without the uplift, or a zone factor above 1.10 (27A).

**Variants covered.** The raw CSV → G2 loader → G3 batch on a snapshot copy:
- `??`, `yes`, `1`, `n` and blank on uplift-eligible lines (PA-00001-04, -01, -06, -10, PA-00007-07);
- `??` and blank on lines where the fact cannot change the value (PA-00001-02, PA-00023-03, PA-00002-05, PA-00004-01);
- Y gives SAR 21,631.15 and N gives SAR 17,730.62 on PA-00001-04.

**Control.** The gate3-r3 loader leaves `??` unqueued, and its engine prices PA-00001-04 as daytime at SAR 17,730.62.

**Not established.** Lower-case `y`/`n` are treated as unknown, not as Y/N. That is a strict reading of the column's two values.

## FD06 — drilling arithmetic

**Fix.** The billed amount is compared with quantity × rate ascertained in cents, half to even (Cl.17, Cl.18), which is the rounding the valuation trace uses. The exact product billed to a fraction of a cent is correct multiplication, not a finding; the cent value is recorded.

This case, DDS-S76, was found by the case comparison right after `95f48b4`. I had committed before that comparison finished; `d10b090` restores the agreement.

Civil keeps its exact comparison: the civil contract rounds the rate (Cl.28), not the amount.

**Variants covered.**
- Ties rounding up to even (152.5 m → 8,867.88) and down to even (152.3 m → 8,856.24).
- An exact product (152.2 m), and a non-tie (152.33 m).
- A wrong cent on each, and the exact 8,867.875.
- The nomination condition is kept.

**Control.** gate3-r3 flags the correctly rounded 8,867.88 and 8,856.24.

**Not established.** The civil amount has no rounding rule to apply. If one were intended, the civil check would need the same treatment.

## FD07 — allocation granularity

**Fix.**
- **Civil.** The unknown cumulative quantity (G4) may start anywhere. The amount as a function of that start is continuous and piecewise linear. The admissible amounts of a division at the band edges are therefore the range between its lowest and highest breakpoint values. An amount inside that range is unresolved, with the range stated and no division selected. Only an amount outside it is a finding.
- **Drilling.** `pd210_step`, and X3's independent grid, use the finest decimal place the values need, never their spelling. The listed extremes bound every allocation at any resolution, because each allocation's amount is linear in the metres placed (Cl.23).

**Variants covered.**
- PA-00008-06 at 384, 384.0 and 384.00, with amounts inside and outside SAR 14,768.64–16,051.20.
- The audit's 100.4 + 283.6 division, checked independently.
- DDS-S72 at 98, 98.0 and 98.00: one domain, 1 m, 3 allocations, USD 4,908.70–4,940.30.
- DDS-S72 at 98.5 and 98.50: 0.1 m, with bounds computed by hand. X3 passes on each.

**Control.** gate3-r3 gives 384 a finding and 384.0 unresolved, and DDS steps of 1, 0.1 and 0.01.

**Not established.**
- A civil amount inside the band range is now always unresolved. Arithmetic errors that land inside it cannot be told apart from a band division until G4 supplies the cumulative quantity.
- The drilling listing resolution is a representation; the bounds are what the evidence establishes.
- `test_f3_split_line_is_unresolved_and_the_rest_reproduce` asserted the old detail, which named a division chosen from the billed amount. It now requires the range instead, a change FD07's required closure demands.

## FD08 — missing submission date

**Fix.** `terms.submission_regimes()` replaces the two old probes, which coincided whenever the work followed the issue.
- Under CW 31A and DDS 36A, a submission date decides how many retrospective issue dates follow it.
- One representative submission per regime is evaluated: the day before each retrospective issue, and after every issue.
- G3-D1 admits early submissions, so every regime is admissible.
- Where the regimes give different rates, the line is unresolved (the date named) and carries the `a3_adjustment` dependency. A rate-unaffected service stays determined.

**Variants covered.** Both contracts; submission before, on and after the issue day, and missing:

| Scenario | Drilling | Civil |
|---|---|---|
| Service after issue | MDS-01650-048 (audit) | PA-00041-01 |
| Inside the retrospective window | MDS-01092-036 | PA-00003-06 |
| Unaffected | MDS-01650-039 | PA-00005-03 |
| Band-conditional (audit) | — | PA-00015-04 |

Also covered: the raw CSV loader with the date blank on MDS-01650-048's invoice and on PA-00015-04's application. On MDS-01650-048:

| Invoice date | Result |
|---|---|
| 16 Aug | USD 3,564.68, with the dependency |
| 17 Aug (issue day) | USD 3,634.44 |
| missing | unresolved, with the dependency |

**Control.** gate3-r3 fixes MDS-01650-048 at USD 3,634.44 and PA-00041-01 at SAR 10,951.68, with no adjustment dependency.

**Not established.**
- Every regime is treated as admissible because G3-D1 keeps early submissions' local value. A narrower admissible-date rule would need its own source.
- Posting the adjustment is G4.

---

## Regression

- **Population against gate3-r3.** Every value, status, payability, finding code, alternative and trace is identical on all 98,990 lines, each FD checked against the commit before it. The only changes are reworded details: 34 unsigned findings, the drilling arithmetic details (which now show the cent value, plus Cl.17 on the check), and 29 civil band-arithmetic details (which now state a range).
- **Cases.** 192 cases, 903 comparisons, 858 agree, 45 disposed, 0 failing.
- **B1, B2, F1–F4.** `tests/test_g3_corrections.py` (22 tests) and `tests/test_g3_corrections_r2.py` (59) pass, including their controls.
- **Test updates.** Four existing test fixtures or assertions encoded the old rules and were updated:
  - G2 control fixtures that used single letters as signatures;
  - the r2 control that forced `engineer_signed`;
  - the r2 case parses (they now unmask `<signature>`);
  - `test_f3` (FD07).
- **Falsification on the final engines.** No exception or engine error, and the output stage completes:
  - 49,032 pairwise and all-empty evaluations;
  - the population-wide fuzz, 98,990 lines;
  - the identity states: shared references, and repeated report and header numbers.
- **Gate.** `tools/check_g3.sh` passed in fresh clones of `fc6ff50` (327 tests), `431d9ed` (434), `45bb8de` (458) and `a4fc597` (468). The run at the final SHA is in the conversation.

## Time

| Event | UTC, 27 Sep 2026 |
|---|---|
| Round-4 goal; clean tree confirmed at `6885224` | 15:34 |
| FD01 (`fc6ff50`) | 15:49 |
| FD02 (`ef96add`) | 16:00 |
| FD03 (`60e57c3`) | 16:04 |
| FD04 + X8 (`431d9ed`) | 16:20 |
| FD05 (`c300833`) | 16:30 |
| FD06 (`95f48b4`, `d10b090`) | 16:34–16:35 |
| FD07 (`45bb8de`) | 16:43 |
| FD08 (`a4fc597`) | 17:48, after an interruption of about an hour |
| Close commit; fresh clone at the final SHA | in the conversation |

---

**Blocked on me:** nothing. Tag pushes are refused in this environment, so the gate3-r4 SHA and annotation text are in the conversation.

**Changed:**
- **FD01.** Signatures are signed, unsigned or unknown.
- **FD02.** Repeated evidence is read once when identical and left unresolved when it differs, never by position or counted twice.
- **FD03.** Civil records support an item only if their captured attributes match Schedule 1.
- **FD04.** Schedule 5 Parts must be complete and certified, whatever the price uses.
- **FD05.** Night work is Y or N only.
- **FD06.** Drilling arithmetic uses Cl.17's cent rounding.
- **FD07.** Admissible divisions and allocations never depend on numeric spelling.
- **FD08.** A missing submission date keeps every rate regime and the adjustment dependency.
- **X8.** It judges from source-derived obligations.

**Found:**
- **DDS-S76.** The exact product billed to a fraction of a cent must not be an arithmetic finding. I found it after committing FD06, and it is fixed.
- **Case packets.** They mask real signatures as `<signature>`, so the harness restores a name before G2 reads it.
- **Tool lists.** A partially unrecognised tool list with recognised tools is recorded content.
- **An old assertion.** It encoded a defect: the F3 detail naming a division chosen from the billed amount.

**Not confirmed:**
- No population line exercises any of the eight failure classes, so every closure is shown on mutated real lines, cases and controls.
- The signature name pattern, the identical-duplicate rule, the strict Y/N reading, the admissibility of every submission regime, and the always-unresolved civil band range are interpretations stated above.
- No independent reader reviewed the round-4 cases.
