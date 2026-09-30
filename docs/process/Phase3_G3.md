# Phase 3 — Gate G3: local entitlement and pricing

> **Superseded where they differ by `Phase3_G3_corrections.md`** (G3 correction round after the independent audit
> `Phase3_G3_audit_Agent2.md` found G3 NOT PASS at `c7abc4b`: well-class and ground-class authority, band-split arithmetic,
> PD-210 tolerance, the Q5 residual). Figures below are those of `c7abc4b`.

**Governing plan:** `artifacts/phase_inputs/Phase2_plan.md` §2 (G3 row), §5, §8, §10.2. **Branch:** `main`.
**Built on:** gate1-r1 / gate2-r1 @ `8745f9c`, re-audit `Phase3_G1_G2_reaudit_Agent2.md` (its carry-forward safeguards bind G3).
**Source:** `majedzahrani3/invoice-auditing-level-2` @ `aef4924dc32506b4587de8b788b5a947e6beffec`, unchanged.

**Exit condition (plan §2, G3):** "Independently calculated clause-based cases pass, including exceptions and
boundaries; all billed code families are implemented or explicitly marked unresolved; each amount has an explainable
calculation trace." `tools/verify_g3.py` checks it with seven checks (X1–X7). `tools/check_g3.sh` runs them after
every G0/G1/G2 check and the full test suite.

**Boundary kept (no G4):**
- G3 keeps no cross-invoice state and applies no bands, caps, exclusions or duplicates.
- It does not model run or well lifecycles, and it does not post the A3 adjustment.
- It does no classification and produces no flags, invoice totals or `submission.csv`.
- Anything that needs another line is listed on the line as a `g4_dependency`, never applied.
- X5 checks this boundary. No tag was moved.

## 1. What was implemented

**Terms access** (`audit/terms.py`):
- typed, read-only lookups over the G1-verified terms and instruments, as exact `Decimal` values with their sources;
- rate history by work date (see the rate-version rules below);
- the S2/A2 discounts.

**Rate version by work date:** instrument rows and monthly tables are taken in the order issued. The latest-issued instrument that applies on the date wins, and the last published month is carried forward. A retrospective amendment is skipped for a submission made before its date of issue (CW 31A, DDS 36A).

**Civil engine** (`audit/g3_cw.py`), line checks:
- identity;
- term as extended;
- 21-day window and stated period;
- unit (Cl.26 full rejection);
- Schedule 5 evidence: record exists, series, both signatures, date or week, area, item, unit (Cl.46–47; Q3 A);
- quantity:
  - 6A first hour;
  - 47A five-day week;
  - 33A 2% survey tolerance;
  - record cap;
- rate and arithmetic.

**Civil price build-up:**
1. USD (26A) and index (29A), each half-even.
2. zone → ground (G2 after 27 Sep 2025; S4) → night (suppressed above 1.1, 27A) → rest-day (P11: rest-day alone).
3. band → discount.
4. **One** half-up rounding (Cl.28).

**Band-rated items (G4 state):**
- A reference case supplies the band as an input.
- On the population the band is unknown. Each band-rated line is priced under every band. Its billed rate is checked against all of them. Its amount is `conditional`, with one full trace per band; a quantity crossing a band edge is divided at the edge, so its amount lies between those bounds.

**Drilling engine** (`audit/g3_dds.py`), line checks:
- identity, including a line for another well;
- term, 30-day window, period, unit (Cl.35; remedy Q11);
- report evidence: day, well, signatures, Schedule 5 part (Cl.15, Cl.37; Q3 A);
- status and section as recorded (Cl.19).

**Drilling quantities by family:**
- persons (Cl.22);
- coordinator (Q5 A);
- tool-days (Cl.28);
- hours (Cl.21/21A/P10), with every Q4 reading computed;
- counts (Cl.30);
- metres with the 1% tolerance (Cl.24–25, 25A);
- PD-210 by depth band, with a boundary depth in the shallower band (Cl.23, Sch 2);
- run and well events (Cl.26–27);
- lost in hole (Cl.31/31A/P12; Q13 A).

**Drilling price build-up:** indexation (17A) → section → class (never for PD-210, 17B) → standby → discount. Each step is rounded half to even (Cl.17). DS-900 is deferred to G5.

**Every line result carries:**
- its checks and findings;
- the family it was valued under;
- unit rate, allowed quantity, amount and payable flag;
- amount status: `determined | not_payable | conditional | alternatives | deferred | unresolved`;
- reasons, alternatives, G4 dependencies, readings applied, and the current run context;
- a **replayable trace**. Each step records its operation, factor, value and source.

**Population run** (`audit/g3_run.py`): every line of both contracts, written to `verification/g3/`:
- `summary.json`;
- `decision_scopes.json`: every decision's lines under each reading;
- `trace_sample.jsonl`: one full trace per code and status.

## 2. Artifacts

| Path | Content |
|---|---|
| `audit/terms.py`, `g3_core.py`, `g3_cw.py`, `g3_dds.py`, `g3_run.py` | terms access, traces, engines, population run |
| `verification/g3/cases/synthetic_{cw,dds}.yaml`, `identity_{cw,dds}.yaml` | 121 hand-written boundary and exception cases (inputs only) |
| `verification/g3/cases/packet_*.jsonl`, `cases_index.json` | 163 case inputs: 121 synthetic, plus 42 real lines chosen by fixed criteria |
| `verification/g3/cases/expected_*.jsonl` | 8 independent readers' results, computed from the scans |
| `verification/g3/case_dispositions.yaml`, `case_comparison.json` | 36 disposed disagreements, each bound to both values; the full comparison |
| `verification/g3/scan_spot_checks.yaml` | 15 reader figures read on the page images; 5 falsification probes |
| `spec/g3_decisions.yaml` | Q3, Q4, Q5, Q8, Q11, Q13, G3-D1, G3-D2: reading, basis with pages, alternatives, cases, scope key |
| `spec/g3_code_families.yaml` | 6 civil and 12 drilling families; membership comes from the verified tables |
| `tools/g3_cases.py`, `g3_case_compare.py`, `verify_g3.py`, `check_g3.sh` | case builder, comparator (`--check` is read-only), gate, one-command check |
| `prompts/phase3/g3_expected_cases_v1.md`, `_v2.md` | reader prompts (v2 adds the identity finding codes) |
| `tests/test_g3_gate.py` | 7 positive checks and 29 negative controls |

**Changed at G3 in earlier gates' files:**
- **Loss corroboration (`audit/events.py`, `build.py`).** It now uses the lost tool's own days in the hole (P12, "the tool accumulated").
- **Carried items (`spec/carried_items.yaml`).** CI-01 is resolved. CI-02 and CI-03 are decided.
- **Stale-entry check (`tools/verify_g2.py`).** It now covers the missing-part items.
- **Question register (`spec/open_questions.yaml`).** It references the decisions.
- **Rules (`spec/rules.yaml`).** CW-R05, DDS-R06 and DDS-R17 are now `settled`. Only the status changed; the reader's statement excludes status. They were recertified in the G1 log.
- **Run context (`audit/provenance.py`).** `spec/instruments.yaml` is now a reviewed input.
- **G2 boundary test.** It is scoped to the evidence modules and now also checks that they never import the G3 layer.

## 3. Evidence per exit condition

This is the output of `PYTHON=python bash tools/check_g3.sh` in the working checkout at the commit before this report
(`c4ed906` plus the task-list count fix). The same command was re-run in a fresh clone at the final `main` commit. That
output and the commit SHA are given with the gate3 tag text, because a report cannot contain its own commit SHA.

```
SNAPSHOT VERIFY OK: 10330 files match manifest (sha256 + git blob), HEAD=aef4924d...
reading comparison reproduces committed file
SPEC VERIFY OK
159 passed
G2 VERIFY OK
case comparison reproduces the committed file
cases 163, expected 163, comparisons 784, agree 748, disposed 36, failing 0
G3 population: 98990 lines (CW 7746, DDS 91244); cases 163; run context bfb77aad06e272cd
PASS X1 independent clause-based cases pass, incl. exceptions and boundaries; inputs before outputs (git)
PASS X2 every billed code family implemented or explicitly deferred/unresolved; pricing tables applied where they apply
PASS X3 every amount's trace replays independently, cites its sources and follows the contract's rounding
PASS X4 decisions and open questions: basis, alternatives, cases and lines affected under every reading
PASS X5 boundary: no cross-line state (reverse-order evaluation identical); no classification/flag/total/submission
PASS X6 billed rate and amount never change a contract value (diagnostic only)
PASS X7 committed G3 outputs reproduce; every result carries the current run context
G3 VERIFY OK
```

### Exit condition part 1: "independently calculated clause-based cases pass, including exceptions and boundaries" (X1)

**How the cases were produced:**
- 163 cases: 78 civil and 85 drilling. Of these, 121 are synthetic boundary and exception cases and 42 are real lines chosen by fixed criteria.
- The inputs were committed before the readers wrote their outputs. For the first 153 cases (`dd73ad9`), the inputs were also committed before the pricing code (`b19d242`). X1 checks this commit order with git.
- Eight independent readers computed the expected values from the scan images: six used prompt v1 and two used v2. The readers never ran project code.

**Result:**
- 784 field comparisons: 748 agree and 36 are disposed. Each disposition is bound to both values, so a changed value reopens it.
- The disposed comparisons fall under two decisions:
  - 33 are G3-D1 (procedural breach: value kept).
  - 3 are G3-D2 (unsigned report on a service outside Schedule 5).

**Coverage of the G3 scope:** every item in the scope list has cases, and X1 checks that each case both agrees and actually shows the behaviour:

| Scope item | Cases |
|---|---|
| Identity | CW-S56, S57; DDS-S57–S60 |
| Period | CW/DDS-S47 |
| Term (both ends) | S41–S43 in each contract |
| Window (boundary day) | 21/22 days; 30/31 days; early submission |
| Evidence and signatures | 6 civil, 6 drilling |
| First hour | CW-S31, S32; DDS-S28 |
| 2% survey tolerance | 102% / 103% |
| 1% metre tolerance | 101% / 102% |
| Five-day week | 4 / 5 days |
| Six-hour minimum | DDS-S29, S30 |
| Civil Cl.26 full rejection | CW-S39, R16 |
| Drilling wrong unit | DDS-S53 |
| Rate version by work date | 6 boundary pairs; the rate changes across each |
| Retrospective protection | 31A/36A, before and on the issue date |
| FX and index half-even | CW-S19, R01, S20, R02 |
| Civil single half-up rounding | CW-S29 (43.725 → 43.73 half-up; half-even would give 43.72), CW-S30 |
| Drilling half-even every step | DDS-S26 (389.825 → 389.82; half-up would give 389.83), S27 |
| Build-up exceptions | ground; night suppressed; rest-day alone; section after indexation; no section factor on Standby |

**Readers' figures checked against the scans** (`scan_spot_checks.yaml`): I read 15 of the readers' table figures on the page images myself, across Schedules 1, 2, 2A–2D and S1. All 15 agree.

**What this does not establish:**
- **The rest of the population.** The cases cover 163 inputs. The other ~99,000 lines run through the same code paths but were not independently computed.
- **Reader independence.** It was instructed, not enforced. The git order proves when files were committed, not what the readers opened. The engine already existed in the repository when the two identity readers ran.
- **Readings fixed in the packet.** Four cases carry a fixed reading of an open question (DDS-S29/S30 for Q4, S36 and S56 for Q5). They test arithmetic under that reading, not the reading itself.
- **The 36 disposed comparisons.** They rest on my reading of the text, and the readers mostly took the other view:
  - window/period: three of the four readers who met these cases read them as not payable;
  - identity: the civil reader read not payable.
- **Shared misreadings.** Readers and engine read the same contract, so a misreading common to both would pass.
- **Civil half-even FX and index rounding.** No case lands on an exact half after the 26A or 29A step. The mode there is enforced by X3's structure check, not discriminated by an independent case. No supplied table value produces such a half in the cases.

### Exit condition part 2: "all billed code families are implemented or explicitly marked unresolved" (X2)

**Families** (`spec/g3_code_families.yaml`): 6 civil and 12 drilling. Membership comes from the G1-verified tables, not from the engine:
- civil: Schedule 5 records, the surveyed list and the Schedule 1 unit;
- drilling: the Schedule 8 "charged for" wording;
- two codes are placed by named G3 decisions: DD-102 and HC-630 (Q5).

**Result:**
- Every billed code falls in exactly one family: 60 civil and 39 drilling codes.
- On every one of 98,990 lines, the engine declares the same family as the registry.
- Implemented families:
  - every line has a value, alternatives or a stated reason;
  - each family has at least one agreeing independent case.
- DS-900 is `deferred`, owned by G5, on all 63 of its lines.
- No line is `unresolved`, and no billed code falls outside Schedule 1.
- Every pricing table that applies to a priced line appears in its trace: FX, index, zone, ground, rest-day, night, band, discount, section, class, standby, depth band, loss value and loss FX.
- One line cannot be priced: MW-310, out of term, in 2027-01, which has no published index. It carries an explicit "not priced" note and is not payable.

**What this does not establish:**
- The family split follows Schedule 8's wording and the G3 decisions. A clause nuance outside those would not be caught.
- The table-applicability check uses the same verified terms as the engine, so a table misread at G1 would pass both. G1's second verification against the scans is the only safeguard there.

### Exit condition part 3: "each amount has an explainable calculation trace" (X3)

**Result:** every trace of all 98,990 population results, and of all 163 case results, was replayed with independent `Decimal` arithmetic. Every step's value and every rounding match. In addition:
- every trace starts at a figure of the verified tables for its code;
- every step cites a clause, table or page;
- each trace ends at the result's rate and amount;
- every band alternative's own trace, and every Q4 alternative, reconciles too;
- rounding structure:
  - civil: exactly one half-up rounding, last, with half-even only directly after an FX (26A) or index (29A) step;
  - drilling: a half-even rounding after every step (Cl.17).

**What this does not establish:** that the right rate version or figure was chosen.
- Replay proves the trace is internally consistent and starts from a contract figure.
- Selection is evidenced by the X1 cases, the spot checks and the probes, not by X3.

### Further checks

- **X4, decisions.**
  - Every decision has a basis with pages, recorded alternatives, existing and agreeing cases, and a computed scope with lines decided and the effect of every reading. Decisions over 100 lines report lines and value under each reading.
  - The question and carried-item registers agree with the decisions, and no question still blocks G3.
- **X5, boundary.**
  - The whole population, evaluated line by line in reverse order, gives identical results in every field of every result, so there is no order-dependent cross-line state.
  - The G3 modules contain none of the G5+ output tokens.
  - *Not established:* an order-independent cross-line aggregation would pass the order test. The token scan is lexical. Code review found none.
- **X6, billing independence.** Every billed rate is multiplied by 1.37 (plus 0.01) and 12,345.67 is added to every billed amount. No unit rate, allowed quantity, amount, payable flag, status, alternative or family changes; only findings change. The billed **quantity** is used as a cap only where the contract makes it one ("payable as charged" up to the supported quantity).
- **X7, reproduction and context.**
  - `summary.json`, `decision_scopes.json` and `trace_sample.jsonl` reproduce from the current code and inputs.
  - Every result carries the run context `bfb77aad06e272cd`, which covers 16 code files, 5 reviewed inputs and the snapshot.
  - The G2 outputs were rebuilt after every code change, so G2 check S2 passes with the same context.

## 4. Negative controls

Every check is shown to fail on a controlled defect. The controls are in `tests/test_g3_gate.py` and pass in the suite.

| Check | Controlled defect → failure observed |
|---|---|
| X1 | dispositions removed → all 36 disposed comparisons fail (CW-S16 first); engine mutated (civil first hour dropped) → CW-S31 fails; scope case CW-S45 removed → "missing"; CW-S29 rounding mode changed → "does not show mode_at_half:half_up"; git order inverted → "inputs not committed strictly before …" |
| X2 | DDS-HOURLY removed from the registry → DD-120 "valued as DDS-HOURLY, registry family DDS-COUNTS"; LH family removed → "LH-711 billed code in no family"; DDS-DISCOUNT declared implemented → "deferred in implemented family"; owner removed → "names no owning gate"; FX step removed from a C.32.040 trace → "FX (26A) applies but its table is not in the trace"; a line relabelled CW-MEAS → "valued as CW-MEAS, registry family CW-HOUR" |
| X3 | step value +0.01 → "recorded … replayed …"; drilling rounding marked half-up → "(Cl.17: half to even)"; extra civil rounding → "2 half-up roundings"; source blanked → "cites no clause"; start 99.99 → "not a figure of the verified tables"; amount +1.00 → "!= result amount"; band alternative +0.01 → "does not follow its trace" |
| X4 | Q13 reading B effect removed → "no effect computed for reading(s) ['B']"; G3-D1 lines removed → "decides 471 lines but reading … reports no lines/value"; Q5 register set to open → status mismatch; Q4 blocks G3 → "still open and still blocks G3"; unknown case and page-less basis → both reported; CI-02 set to open → "not decided with a treatment" |
| X5 | engine that remembers earlier lines → order dependence reported; module containing `submission.csv` → reported |
| X6 | engine that accepts the billed rate when within 50% of the contract rate → contract values change with billing |
| X7 | one committed number changed → "does not reproduce"; one result without its run context → reported |

## 5. Questions and carried items

The decisions are in `spec/g3_decisions.yaml`. The scopes are in `verification/g3/decision_scopes.json` (lines decided, and the effect under each reading).

| Item | Status | Lines decided | Adopted reading → effect | Alternative(s) → effect |
|---|---|---|---|---|
| **Q3** missing Schedule 5 record | decided A | 13 (CW 9, DDS 4) | not payable in the carrying valuation/invoice (Cl.46, Cl.37) → 0.00 | B: value kept, P23 recovery → 259,341.35 on 12 single-rate lines (1 band-rated) |
| **Q4** first hour / minimum / period | **open** (moved to G5) | 7 lines where readings differ, out of 5,549 hourly lines | none adopted; every reading carried | A 34,771.88; B 34,771.88; C 37,239.24; RM-530 counts 3,174.60 (2 lines) |
| **Q5** Schedule 8 conflicts | decided | 9,007 | DD-102 per coordinator (8,151 lines, 7,732,038.60); HC-630 counted as recorded (428); DD-120 circulating hours only (428 back-reaming days) | DD-102 per tool-in-hole day → 0 chargeable (no tool exists for DD-102); HC-630 per run → 0 lines differ (every day records one run); DD-120 plus back-reaming → 0 lines would rise |
| **Q8** unsupplied documents | decided A | 26,607 | class factor from the invoice header as a disclosed proxy (24,217 lines, 73,300,566.08); PD-210 conditional on the unsupplied nomination (2,390 lines, 21,356,375.55 if nominated); civil P11 rest-day alone (0 lines) | B: all these lines unresolved (no value) |
| **Q11** drilling quantities | decided in part | 0 | accumulator: no effect (records bound 10,002 m < 40,000 m); 25A per charge against the report's interval | wrong-unit remedy kept open, A/B: 0 lines affected |
| **Q13** / **CI-01** loss hours | decided A; CI-01 resolved | 54 | Part E hours (Cl.31 "as stated on the Lost in Hole Report"), corroborated by the lost tool's own history in 54 of 54 losses → 31,427,958.99 | B: whole-well sum → 27 of 54 amounts differ, 29,241,596.08; C: not needed |
| **CI-02, CI-03** | decided under Q3 A | 3 | not payable in the carrying invoice | — |
| **G3-D1** procedural breaches (window, period, identity, one well per invoice) | decided | 471 (CW 52, DDS 419) | breach recorded, value kept → 467 payable; 1,698,500.78 on single-amount lines, plus 7 civil band lines between 153,653.46 and 165,781.30 | not payable now → 0.00 on all 471 |
| **G3-D2** unsigned report | decided | 33 | Schedule 5 services not payable (1 line); others keep their value → 55,798.69 | every line not payable → 0.00 |

- **D6 and D7** are unchanged, as explicit decisions with recorded alternatives.
- **Q1, Q2, Q6, Q7, Q9, Q10 and Q12** belong to later gates and are untouched.
- **Rules:** CW-R05, DDS-R06 and DDS-R17 are now settled. DDS-R07 (Q4), DDS-R08 (Q11 wrong unit), DDS-R15 (Q10) and DDS-R19 (PD-210 nomination) stay open.

**Not established:**
- **Whether the adopted readings are right.** They are my readings of the text, each with its alternatives computed. G3-D1 decides 471 lines on which the readers split.
- **The Q8 proxy.** It rests on the invoice header standing in for the call-off.
- **The dispositions.** No reading was adopted because it matched billing: the basis is the clause text. Billed agreement does favour G3-D1 on the window cases, which is why the alternative's full effect is reported.

## 6. Population diagnostics

Billing is never used as truth here; these are diagnostics only.

**Civil, 7,746 lines:**
- statuses: 6,706 determined, 1,025 conditional (band), 15 not payable;
- billed rate vs contract rate: of the 6,720 single-rate lines, 6,692 agree and 28 differ;
- band-rated lines: 1,018 of 1,026 are billed at one band's rate, leaving the band to G4; 8 are billed at no band's rate.

**Drilling, 91,244 lines:**
- statuses: 88,761 determined, 2,390 conditional (PD-210), 7 with Q4 alternatives, 63 deferred (DS-900), 23 not payable;
- billed rate vs contract rate: 91,123 agree and 57 differ.

**G4 dependencies listed on lines** (not applied):

| Dependency | Civil lines | Drilling lines |
|---|---|---|
| Daily limit | 1,183 | 79,579 |
| Band state | 1,026 | – |
| Exclusion | 229 | – |
| A3 adjustment | 89 | 3,309 |
| P23 link | 9 | – |
| Once per run | – | 1,023 |
| Once per well | – | 859 |
| Duplicates | every line | every line |

**Falsification probes** (`scan_spot_checks.yaml`). I took each real line where billing differs from the engine and asked whether the engine could be the one that is wrong. Each settled for the engine against the scan:

| Line | Billed | Engine | Why the engine is right |
|---|---|---|---|
| PA-00115-05 | 121.80 | 121.79 | Billing rounded at an intermediate step; Cl.28 rounds once. |
| MDS-00586-039 | 98.70 (band 4) | 76.45 (band 3) | The interval is 4,107–4,199 m, which is band 3. |
| MDS-01387-037 | 77.05 = 58.15 × HPHT 1.325 | 58.15 | 17B excludes the class factor for PD-210 (D1). |
| Five DD-121 lines | 2,893.65 (Sch 1) | 2,984.00 | Supplement No. 1 substitutes 2,984.00 from 2025-07-01 (DDS p38). |
| PA-00297-07 | 72.71 (Sch 1 base) | 252.47 | S1 monthly rate for September 2025 carried forward (CW p39). |

## 7. What the evidence does not establish (summary)

1. **No amount is final.** Every G3 amount is local:
   - bands, daily limits, exclusions, duplicates, run and well counting, the A3 posting and DS-900 all come later (G4/G5);
   - 1,025 civil lines and 2,390 PD-210 lines are conditional;
   - 7 lines carry open Q4 alternatives.
2. **Case coverage and independence.** The cases cover scope items, not the whole population. Reader independence was instructed, not enforced.
3. **Contested readings.** 36 comparisons are settled by my decisions (G3-D1, G3-D2), against the majority of readers on window/period and on civil identity.
4. **Civil half-even FX/index.** Its mode is enforced structurally (X3) but not discriminated by an exact-half case.
5. **G1 tables.** The pricing tables are trusted from G1's double verification. The 15 spot checks are a sample.
6. **The G2 changes made here.** The loss corroboration, stale check and path portability are covered by tests and by `verify_g2`. They have not been independently re-audited.
7. **Out-of-scope billing inputs.** X6 covers the billed rate and amount. The billed hole section and day status produce findings only, because the engine uses the report's values. No perturbation test covers them.

## 8. Found

1. **Band-rated civil items are G4 state.**
   - Before: pricing them at band 1 produced 866 `rate_differs` findings and "determined" amounts.
   - Now: they carry per-band traced amounts. Civil `rate_differs` fell to 36.
2. **The first case set had no identity case,** and no drilling report for another day or well and no missing report.
   - Ten cases were added: packets `41ce2bd`; readers' results and dispositions `5bb9667`.
   - G3-D1's scope had also missed the identity findings; including them took it from 273 to 471 lines.
   - The commit message of `5bb9667` still says 273. The correct figure is 471.
3. **An earlier G3-D1 note mis-counted the readers.** It said "four read not payable, one kept". In fact, of the four readers who met window/period cases, three read not payable and one kept the value. Corrected.
4. **Q13:** Part E equals the lost tool's own daily history in 54 of 54 losses. The G2 comparison against the whole-well sum was the wrong corroboration; CI-01 is resolved.
5. **A data property:** the 428 days with back-reaming hours on which DD-120 is billed are exactly the 428 days with HC-630 clean-out runs.

## 9. Time

About 6 h 15 min wall-clock on 2026-09-26, 06:25–12:40 UTC. This includes a context-summary pause and the reader runs. The plan's estimate for G3 is 4.8 h.

## Blocked on me

- Nothing blocks the gate. The only action left for me is the tag: tag pushes are refused, so the `gate3` SHA and annotation text are given in the conversation for you to create it.

## Changed

- **G3 code:** `audit/terms.py`, `g3_core.py`, `g3_cw.py`, `g3_dds.py`, `g3_run.py`.
- **G3 spec:** `spec/g3_decisions.yaml`, `g3_code_families.yaml`.
- **G3 evidence:** `verification/g3/**`.
- **G3 tools and tests:** `tools/verify_g3.py`, `g3_cases.py`, `g3_case_compare.py`, `check_g3.sh`; `tests/test_g3_gate.py`.
- **Earlier gates' files, G2 correction:** `audit/events.py`, `build.py`, `provenance.py`.
- **Earlier gates' files, registers:** `spec/carried_items.yaml`, `open_questions.yaml`, `rules.yaml` (3 statuses), `question_scopes.json`.
- **Earlier gates' files, tools:** `tools/verify_g2.py` (stale check), `param_rule_verification.py` (path portability), `question_scopes.py`.
- **Earlier gates' files, generated outputs:** `verification/param_rule_log.yaml` (3 recertified), `verification/g2/*` (rebuilt).
- **Earlier gates' files, tests:** `tests/test_g1_gate.py`, `test_g2_controls.py`, `test_g2_provenance.py`.
- **Documents:** `README.md`, `Phase3_TASKS.md`.
- **Prompts:** `prompts/phase3/g3_expected_cases_v2.md`.

## Found

- Band state makes the civil band-rated amounts conditional (1,025 lines).
- The first case set had an identity coverage gap. It is closed with 10 cases and 2 readers.
- G3-D1's scope was missing the identity findings; it is 471 lines, not 273.
- A reader-count error in a note was corrected.
- CI-01 is resolved: Part E matches the tool history in 54 of 54 losses.
- Five falsification probes each settled for the engine.
- A process slip: `git checkout audit/build.py`, used to undo a one-line negative-control edit, also discarded an uncommitted change. It was restored from the session transcript. The rebuilt outputs matched the earlier ones byte for byte (`summary.json` identical), and `loss_hours_readings` = {tool 15, tool+run 12, tool+well 25, tool+well+run 2}, as before.

## Not confirmed

- **Readings.** The adopted readings for G3-D1 (471 lines), G3-D2 and the Q8 proxies are mine, with every alternative's effect computed. The readers split on G3-D1.
- **Q4 remains open** on 7 lines.
- **Readers.** Their independence was instructed, not enforced, and their figures were checked on a sample of 15.
- **Civil half-even FX/index mode** is not discriminated by a case on an exact half.
- **Order-independent cross-line logic** is excluded by code review and a token scan, not by a test.
