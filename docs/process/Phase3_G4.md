# Phase 3 G4 — Chronology and shared state

**Scope:** plan §2 G4 (artifacts/phase_inputs/Phase2_plan.md): bands, caps, exclusions, duplicates across invoices,
run/well events, retrospective (A3) adjustments, retention history, and every register item assigned to G4.
**Baseline:** `gate3-r5` = 1a14df1, authorized by artifacts/phase_inputs/Phase3_G3_FD07_recheck.md ("FD07 CLOSED. G3 PASS.
G4 is authorized"). At the start the tree was clean and main = origin/main = 1a14df1.
**Challenge:** majedzahrani3/invoice-auditing-level-2 @ aef4924 (unchanged; G0 snapshot verify passes).
**Commits on main:** 081d118 (G4.0), 91e785e (packets, before any G4 code), 3b4e4fd (reader outputs), b758791 (engines
and comparison), then the verification/registers/report commit. The final SHA is in the reply. No G5–G7 work, no tag moved.

## 1. What was implemented

G4 consumes the G2 world and the closed G3 line results and never modifies them. Each G4 line is a deep copy of the G3
result, and every state consequence is added as a `StateCheck` (family, status, rule, clause, finding, ledger entry)
with a replayable trace. Where the contract or a registered open question leaves a state outcome open, every admissible
outcome is carried as a labelled alternative with its owner. Billing, incidental row order and the smallest document
number never choose.

| Module | Content |
|---|---|
| `audit/g4_core.py` | G4Line/StateCheck; alternatives: `collapse` (a dimension is dropped only where it is a full product and changes nothing), `apply_options`, owners of every dimension G4 keeps open (Q12, Q14, Q6, Q6-day0, order, stands, earlier). |
| `audit/g4_cw.py` | **Cl.44 duplicates.** Keyed on item + work area + date; a weekly item is keyed on its week (G4-D3). "Later" means the later submission; same-day submissions become `earlier` alternatives (G4-D5).<br>**Cl.32/P19/P21 exclusions.** Covers D+1 and D+2; day D is carried as Q6 D.<br>**Cl.31 daily limits.** Applied to the measurement that stands.<br>**Sch 4 Part 3 bands.** One ledger per item × Contract Year × Q12 × Q6, counted by execution date. Every order of a same-date group that changes a division is carried. A same-day duplicate tie counts once, as a range. More than 6 measurements that count at an edge are left unresolved, never assigned a convention.<br>**A3.** The difference is computed per protected line and totalled per shared reading. There is one recipient per Q1 reading.<br>**P23.** Not posted under Q3 A.<br>**Retention and release.** 5% per application, rounded down, per reading. The 45A release is made once. |
| `audit/g4_dds.py` | **Once-only charges.** Cl.29 (well-day), Cl.26 (run: DD-111 last day, LW-420 first day), Cl.27 (well: MB-701/DD-140 first report day; MB-702/LW-430 last day; LW-430 only with an LWD tool) and Cl.31 (loss) are joined into groups. A charge off its day never stands. Among admissible charges, which one stands is carried as `stands` (Q7 C).<br>**HC-630.** Charged once per BHA run under the Schedule 8 reading (Q5 residual).<br>**PD-210 overlaps.** Overlapping intervals are charged once.<br>**Cl.22 limits.** Per well-day (D6).<br>**Sch 2 Part 2 footage.** Every Q11 × Q14 reading.<br>**A3.** Difference and recipients under Q1 A, B and C. |
| `audit/g4_run.py` | Population outputs in verification/g4/: summary, decision_scopes, the `ledgers/*.json` (band ledgers, duplicate/exclusion/once groups, limits, footage, A3 accounts, P23, retention) and `changed_lines.jsonl` (every line G4 changed, with the G3 value, G4 value, state checks and traces). |
| `tools/g4_histories.py`, `tools/g4_history_compare.py` | The history packets, the history runner (materialize → G2 build → G3 → G4) and the line-by-line comparison with the readers. |
| `tools/verify_g4.py`, `tools/check_g4.sh` | Exit checks Y1–Y9 (section 3); `check_g4.sh` runs G0–G3 (incl. the whole test suite) and then G4. |
| `spec/g4_state.yaml`, `spec/g4_decisions.yaml` | State families (key, clock, quantity counted, consequence, source); decisions G4-D1…D15 with basis, alternatives, histories, scope. |
| Registers | Q1, Q6, Q12 are kept open with `g4_disposition` (blocks G5). Q7 is decided in part: CW decided, C kept open. Q6 gains alternative D (exclusion on day D). Q14 is new (drilling Contract Year). CI-03 has a G4 treatment. |

## 2. Decisions and open alternatives

| Id | Status | Reading (short) | Population effect |
|---|---|---|---|
| G4-D1 order | decided in part | Execution date; each same-date order that changes a division is carried; Cl.30's substituted wording is one labelled alternative. | 8 lines carry `order`. |
| G4-D2 Contract Year | **open** (Q12, Q14) | Both computed. | CW: 270 lines carry Q12. DDS: none change. |
| G4-D3 weekly = week | decided (Q7 CW) | Lines citing one week's log are one measurement; Cl.44 applies. | 19 week groups. |
| G4-D4 exclusion window | decided in part | D+1 and D+2 decided (Q6 C). Day D is **open** (Q6 D: P19 "within two days of" vs Cl.32/Sch 4 Pt 5 "following"). | 1 line (PA-00801-05). |
| G4-D5 "later" | decided | Later submission, else later line; same-day submissions become `earlier` alternatives. | 20 groups, no ties. |
| G4-D6 limits | decided | Applied to the quantity that stands; the excess is not carried forward. | CW PA-00243-10 (3→1), PA-00845-03 (3,440→3,200). |
| G4-D7 band basis (Q6 A/B) | **open** | Rejected quantities never count; unpaid-for-record counts under A only. | No difference on the pinned data. |
| G4-D8 A3 | decided in part | Difference per protected line, posted once; recipient **open** (Q1). | CW 89 lines: 60,508.18 (Q12 A) / 59,252.02 (Q12 B). Recipient: A = tie PA-00006/00023/00380, B = PA-00443.<br>DDS 3,309 lines: 289,180.18–345,755.27 (range over well classes, joint per well). Recipient: A = MDS-01625, B = tie of 3, C = 56 of 68 wells have none. |
| G4-D9 P23 | decided | Not posted under Q3 A (never excluded and deducted). | 9 links, 0 posted. |
| G4-D10 retention | decided | 5% per application; 45A release once. | Release on PA-00678; PA-00375 later, no release. |
| G4-D11 once-only | decided in part | Off-day charges never stand; which admissible charge stands is **open** (Q7 C). | 3 MB-701 off-day repeats; 3 pairs of stands (MDS-00476 MW-301, MDS-00580 LW-401, MDS-01654 LW-401). |
| G4-D12 HC-630 per run | decided | One per BHA run under Sch 8; which one is carried. | No run has two HC-630 charges. |
| G4-D13 footage | **open** (Q11 × Q14) | Every reading computed. | No well reaches 40,000 m. |
| G4-D14 PD-210 overlaps | decided in part | Overlapping metres charged once; the keeper is carried. | 184 same-day groups, 0 overlapping. |
| G4-D15 loss once | decided | One charge per tool code, well and lost-in-hole run. | 54 losses, none repeated. |

## 3. Evidence per exit condition (verify_g4 on the population: all PASS)

| Exit condition (plan §2) | Check | How it is checked | Result |
|---|---|---|---|
| Small multi-invoice histories agree with independent expected events and amounts | **Y1** | 24 histories: 19 synthetic, each built for one state family and its boundaries (see verification/g4/histories/meta.yaml), and 5 population slices. Six isolated subagents computed the expected lines, adjustments, retention and events from the contract scans only, two readers per history, never from engine output. Git order: packets 91e785e, then readers 3b4e4fd, then engines b758791. Every line, adjustment, recipient and retention figure is compared. | 48 reader results. 28 agree in full. 59 disagreements, all settled against the scan: 16 engine, 41 both (the contract leaves it open and the engine carries the reader's value), 2 presentation. 0 open, 0 stale. 5 engine defects came from these disagreements and were fixed (section 7). |
| Ordering tests pass | **Y2** | The population's claim rows are rerun in reverse and in a seeded shuffle, and the state must be identical. Ledgers must be in execution-date order. Each order that matters must be carried. | PASS |
| Reset tests pass | **Y3** | Every band ledger must start at 0 in its Contract Year and sum without gaps. Q12 A CY2 must begin 2026-01-05; Q12 B has no CY2. Footage is recounted independently (per well and CY, Q14 A/B). | PASS |
| Allocation tests pass | **Y4** | In every group, exactly one charge stands under each alternative. No charge off its day stands. No quantity is above its limit. A3 and 45A go on one document per reading. | PASS |
| Replay tests pass | **Y5** | A second run must be identical. Correcting an early measurement (removing the first line of the longest ledger) must replay every later entry of that ledger by exactly its count and change no other ledger. Histories without their last document must rerun reproducibly. | PASS |
| No duplicate event or adjustment counted twice | **Y6** | At most one standing measurement per item/area/date under every alternative. Each band line appears once per ledger. One A3 account per instrument. The state with the A3 account equals the state without it, so no difference is embedded in a line. No P23 is posted beside an exclusion. Each PD-210 line appears once per accumulator. | PASS |
| (supporting) traces | **Y7** | Every changed value and every alternative is replayed with independent arithmetic (verify_g3.replay). | PASS |
| (supporting) boundary | **Y8** | G3 results are byte-identical before and after G4. Every G3 `g4_dependency` is answered: CW band 1,026/1,026, daily_limit 1,183/1,183, exclusion 229/229, p23 9/9, A3 89/89; DDS daily_limit 79,579/79,579, run 1,451/1,451, well 859/859, A3 3,309/3,309. Outputs reproduce. No G5+ construct. | PASS |
| (supporting) registers | **Y9** | Decisions have page basis, existing histories and computed scopes. No question or carried item still blocks G4. | PASS |

### Expected histories used (verification/g4/histories)

| History | What it tests | Lines | Carried alternatives | Reader disagreements (settled) |
|---|---|---|---|---|
| CW-H01 | Execution-date band order across applications; one line crossing both edges | 4 | 0 | 0 / 0 |
| CW-H02 | Same-date lines at an edge (all six orders) | 4 | 3 | r1 3 (engine: r1 gave 2 of 6 orders; r2 = engine) |
| CW-H03 | Contract Year 4/5 Jan 2026 (Q12) | 3 | 1 | r1 1 (both) |
| CW-H04 | Q6: wrong-unit and unrecorded quantities in the count; P23 | 4 | 1 | r1 1, r2 1 (both: readers took Q6 B and noted A) |
| CW-H05 | Cl.44 before Cl.31; another area; next day | 5 | 0 | 0 / 0 |
| CW-H06 | Exclusion on day 0/1/2/3 and another area | 6 | 1 | 0 / 0 |
| CW-H07 | E.51.020 on a surfacing day; one-day limit | 4 | 0 | 0 / 0 |
| CW-H08 | "Later" by submission against application number; weekly reuse | 8 | 0 | r4 3 (engine) |
| CW-H09 | A3 on protected work; issue-day tie; Q1 | 6 | 0 | 0 / 0 |
| CW-H10 | Retention rounding; 45A release once | 4 | 0 | 0 / 0 |
| CW-H11 | P23 never both excluded and deducted | 2 | 0 | 0 / 0 |
| CW-H12 | A3 on a band item crossing an edge; Q12 | 3 | 1 | r4 1 (both) |
| CW-R01/R02/R03 | Population: E.52.010 twice; DW-00004 cited three times; A.14.020 same day as A.14.010 | 2/3/2 | 0/0/1 | R02 10 (engine), R03 4 (both) |
| DDS-H01 | Cl.29 across invoices; Cl.22 | 4 | 2 | 8 (Q7 C both; 2 presentation) |
| DDS-H02 | PD-210 split vs overlap | 3 | 2 | 6 (Q7 C both) |
| DDS-H03 | DD-111/LW-420 once per run; HC-630 per run | 6 | 6 | 13 (both; r5 = engine on HC-630) |
| DDS-H04 | Well events; first/last day; LWD | 6 | 0 | 0 / 0 |
| DDS-H05 | A3 (incl. S2 discount); Q1 A/B/C | 6 | 0 | 0 / 0 |
| DDS-H06 | Footage 40,000 m; Q11; 1 Jan reset | 4 | 2 | 2 (both: each reader took one reading) |
| DDS-H07 | Loss charged twice | 2 | 2 | 6 (Q7 C both) |
| DDS-R01/R02 | Population: MB-701 twice; MW-301 twice in one invoice | 2/2 | 0/2 | 0 / 0 |

Every settlement and its page reference is in verification/g4/history_dispositions.yaml.

## 4. Negative controls (tests/test_g4_gate.py, 40 tests: each check passes, then fails on a controlled defect)

| Check | Defect injected, and the check fails |
|---|---|
| Y1 | No settlements; a stale settlement; the engine value changed; readers committed after the engine; a history with no reader. |
| Y2 | The row order decides which duplicate stands (the monkeypatched duplicates); a ledger out of date order; only one order carried. |
| Y3 | A ledger that does not restart; a count that skips a measurement; a CY2 under no-reset; a footage accumulator off by 7 m. |
| Y4 | Two charges stand; a later duplicate keeps its value; an off-day charge stands; a quantity above the limit; A3 posted on two documents. |
| Y5 | A stale rerun; a cached, non-replaying engine (the correction replay fails). |
| Y6 | A line counted twice in a ledger; two standing measurements; P23 beside an exclusion; the A3 difference embedded in a line; an A3 account posted twice. |
| Y7 | A tampered trace step; a value that is not its trace's result. |
| Y8 | G3 modified by G4; an unanswered G3 dependency; outputs that do not reproduce; a G5 construct (`submission.csv`). |
| Y9 | A basis without pages, an unknown history or an uncomputed scope; a question still blocking G4; a G4 carried item without treatment. |

## 5. Falsification (tests/test_g4_falsification.py, 8 constructed histories; expectations computed by hand from the text)

I tried to break my own completion claim on ordering, resets, replay, duplicates and cross-invoice interactions,
including branches that no pinned line or committed history exercises:

1. **Same-day duplicate tie inside a band ledger.** No pinned case. Found a defect: both tied measurements advanced the band count, so the adjustment was counted twice. Fixed: the tie counts once as a range, and each tied measurement is valued from where the tie begins. Test: 600 + 600 tied, then 800 → 600 × 74.50 + 200 × 71.52 = 59,004.00.
2. **A large same-date group at an edge.** Found a defect: with more than 6 lines the convention order was used silently. Fixed: left unresolved. Also, disallowed copies multiplied the orders; only measurements that count are now permuted. Test: five areas × 250 with two disallowed copies; each of the five carries {18,625.00, 17,880.00}.
3. **A rejected (wrong-unit) A.14.010 does not exclude A.14.020.** The same line in the right unit does exclude it.
4. **Applications listed in reverse.** No change (plus Y2 reverse/shuffle on the population).
5. **45A release tie.** Two applications submitted on the same first day after completion give a `tie`, not two releases.
6. **Well with no Daily Drilling Report.** No well event stands.
7. **Correction to an early measurement.** Replays the later divisions: PA-91001-01 goes from 36,356.00 to 37,250.00, and PA-91003-01 changes.
8. **Loss charged on two invoices.** Exactly one stands in each alternative.

## 6. Population regression against gate3-r5

- **G2/G3 outputs:** verification/g2 and verification/g3 differ from gate3-r5 only in the run-context id and the code hashes of the new audit/g4_*.py files. The context hashes every `audit/*.py`. Every G3 value, finding, scope and trace is unchanged. verify_g3 X1–X8 pass after regeneration, and Y8 confirms G3 results are byte-identical after G4 runs.
- **G4 changes relative to the G3 values:** 1,048 CW lines and 9 DDS lines (verification/g4/changed_lines.jsonl). Every one is explained:

| Lines | G3 → G4 | Cause |
|---|---|---|
| 619 + 7 | conditional → determined | Band state resolved: the G3 `band` condition (owner G4) is decided by the ledger. Every reading gives one band. 7 of these differ from the billed rate (`rate_differs`). |
| 9 | conditional → determined | Band divided at an edge under every reading. |
| 254 + 14 + 1 + 1 | conditional → alternatives | Q12 changes the band (14 of them are also divided). 2 also carry `order`. |
| 5 + 1 | conditional → alternatives | `order` only: a same-date pair at an edge. |
| 111 + 3 | conditional → conditional | Band resolved; the value still depends on ground class, a fact that is not supplied. |
| 20 | determined → not payable | Cl.44 later measurements in the 20 duplicate groups (19 reused dewatering weeks, PA-00111 E.52.010); a 21st disallowed line was already not payable at G3. |
| 2 | determined → determined | Cl.31 limit: PA-00243-10 2,052.00 → 684.00; PA-00845-03 343,277.60 → 319,328.00. |
| 1 | determined → alternatives | PA-00801-05 exclusion on day D (Q6 D). |
| DDS 6 | determined → alternatives | Q7 C stands: 3 pairs. |
| DDS 3 | determined → not payable | MB-701 charged again after the well's first day (NGP-QA-054, NGP-QA-171, NGP-WS-192). |

- **No G5–G7 code:** `git diff 1a14df1` adds only G4 engines, runner, histories, checks, tests, specs, registers and verification outputs. text_errors finds no G5 construct in the G4 modules. No invoice outcome, flag, category, confidence, total or submission.csv is produced.

## 7. Found (defects in G4 scope, all fixed)

1. HC-630 once per BHA run under the Schedule 8 reading, a register item assigned to G4, was not applied (DDS-H03, r5).
2. The exclusion on the day of the excluding measurement had been decided without textual support. It is now carried as Q6 D (CW-H06, r1/r2).
3. `band_divided` and `footage_band_divided` were reported as established when the division held under some readings only.
4. A same-day repeat of a run event did not also carry Cl.29 `charged_twice`, and a well event charged again after its day did not carry `well_event_repeated`.
5. `collapse` dropped a dimension present under one reading only (a label set that is not a full product), which lost HC-630's two readings.
6. The falsification defects above: a double count in a same-day tie, a silent convention order in a large group, and rejected lines multiplying the orders.
7. Coverage gaps: a band line that is G3-not-payable and 19 DDS not-chargeable lines had no state check. They now have explicit n/a checks, and a singleton group of a G3-not-payable charge is now n/a instead of pass.
8. A register edit of mine changed a G1-verified rule entry (DDS-R12 `questions`). The G1 content-hash safeguard caught it and the edit was reverted: Q14 names DDS-R12 on its own side. No G0–G3 safeguard was weakened.

9. The G2 boundary test (tests/test_g2_controls.py::test_boundary_no_pricing_or_outcomes) globs audit/*.py except a
   named G3 set, so it failed on the new G4 modules, which import G3 by design. It now also excludes a named G4 set,
   the same pattern it uses for G3. Every G2 evidence module is still checked, and G4's own boundary is Y8. This is a
   scope extension of the test, not a relaxation of any G2 condition.

No pre-existing G2/G3 defect preventing correct G4 behaviour was found, and no closed gate was reopened.

## 8. What the evidence does not establish

- **Readers are not ground truth.** They are independent subagents of the same model family, reading the same scans. Agreement shows independent reproduction, not correctness. Where both readers and the engine share a misreading, no check here would catch it.
- **"Later" = later submission (G4-D5) and weekly = week (G4-D3) are my readings.** They are argued from the text, and 3 of 4 civil readers left "later" open between submission, application number and work date. They could be wrong.
- **Submitted applications/invoices stand in for "already certified/invoiced" (A3).** No certificate is supplied.
- **Well endpoints are the first and last Daily Drilling Reports.** The plan asks whether they represent spud and release; this is not established. Six wells have service dates after their last report, and G3 already marks those lines not payable.
- **A3 totals and the 45A release are ranges where lines carry fact alternatives** (ground class, well class). The CW release is 3.97M–4.12M, and per-line ground ranges are treated as independent across lines. That is conservative, not a joint distribution.
- **Branches unreachable on the pinned data are exercised only by constructed histories.** These include >6 counting measurements at one edge, a same-day tie inside an order-relevant group, PD-210 overlaps, HC-630 runs with two charges, footage above 40,000 m and Q6 A/B differences. Those histories cover specific shapes, not every combination.
- **Diagnostic sums only.** The amount-by-reading figures in decision_scopes.json are diagnostics (the per-reading sums across the lines that carry a dimension), not totals of any document.
- **Retention is computed on line values after G4 state.** It excludes G5 matters: DS-900, VAT, invoice arithmetic, the Q2 adjustment basis and Q9 semantics.

## 9. Anything needing the user's decision

1. **Q7 C (drilling):** should the charge on the earlier-submitted invoice stand, with the later one as the repeat? Both drilling readers read Cl.29 this way where the invoices differ. The text does not say it, and the register records "no allocation rule". G4 carries both (3 population pairs, all within one invoice, where even the readers kept both). Adopting it would decide DDS-H01/H02/H03/H07-type cases.
2. **Q6 D (civil):** is A.14.020 excluded on the same day as A.14.010? P19 says "within two days of"; Cl.32 and Sch 4 Part 5 say "following". This affects 1 line (PA-00801-05).
3. **Q12, Q14, Q1, Q6 A/B, Q11** remain open for G5 as registered. Nothing new is needed now.

## 10. Time

G4 ran from 06:46 UTC (G4.0) to the final commit on 2026-09-28, about 5.5 h of wall time. That includes a usage-limit
pause while the six readers were relaunched. The plan's budget is 5.3 h for G4/G5 shared state.

## Blocked on me

Nothing blocks G4 closure. Decisions requested: Q7 C and Q6 D (section 9). Both are carried as alternatives until you decide.

## Changed

- New files: `audit/g4_core.py`, `g4_cw.py`, `g4_dds.py`, `g4_run.py`; `tools/g4_histories.py`, `g4_history_compare.py`, `verify_g4.py`, `check_g4.sh`; `tests/test_g4_gate.py`, `test_g4_falsification.py`; `spec/g4_state.yaml`, `g4_decisions.yaml`; verification/g4/*; `prompts/phase3/g4_expected_histories_v1.md`.
- Changed: `tests/test_g2_controls.py` (named G4 module set, item 9 of section 7), `spec/open_questions.yaml` (Q1, Q6 + D, Q7, Q12 dispositions; Q14 new), `spec/carried_items.yaml` (CI-03 G4 treatment), `Phase3_TASKS.md` (G4 section).
- Regenerated outputs: verification/g2 and verification/g3 (run context only).

## Found

The nine items in section 7, all fixed within G4 scope. No G2/G3 defect was found.

## Not confirmed

- The correctness of the readings behind G4-D3 and G4-D5 beyond the reader agreement.
- That the first and last reports are the true spud and release days.
- The joint range of fact-dependent totals.
- Behaviour on combinations of the rare branches beyond the constructed histories.
