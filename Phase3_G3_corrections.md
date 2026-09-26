# Phase 3 — G3 correction round (independent audit Phase3_G3_audit_Agent2.md)

**Audit judgment:** G3 NOT PASS at `c7abc4b`, with four defects (F1–F4) and an unsettled Q5 residual. This round corrects them at source.

**Governing documents:**
- the audit's §8 (closure evidence) and the plan (`artifacts/phase_inputs/Phase2_plan.md` §2, §6, §8);
- the pinned challenge `aef4924d`, with every clause read on the scan images.

**Boundary kept:**
- No G4 work: no band allocation, caps, cross-invoice state, duplicates or run/well lifecycles.
- No classification, flags, totals or `submission.csv`.
- No tag was moved.

**Supersession:** this report supersedes `Phase3_G3.md` where the two differ.

**Starting state:** a clean tree, with `main` = `origin/main` = `c7abc4b`.

## Evidence

This is the output of `PYTHON=python bash tools/check_g3.sh` in the working checkout at `5a9db3e`, the commit before this report:

```
SNAPSHOT VERIFY OK: 10330 files ...; SPEC VERIFY OK (13 questions, 8 decisions)
181 tests passed (G0-G2, G3 gate controls, G3 correction-round controls)
G2 VERIFY OK
case comparison reproduces the committed file
cases 180, expected 180, comparisons 837, agree 801, disposed 36, failing 0
G3 population: 98990 lines (CW 7746, DDS 91244); cases 180; run context 826da5aa1ce06a49
PASS X1 ... PASS X7
G3 VERIFY OK
```

The same command was then re-run in a fresh clone at the final `main` commit. That output, and the commit SHA, are given with the gate3-r1 tag text in the conversation, because a report cannot contain its own SHA.

**Independent cases:**
- 17 new cases (13 synthetic and 4 real lines named by the audit) and 24 earlier cases re-read from the same inputs. Four new readers worked from the scans with prompt v3.
- The inputs were committed at `647ee8a`, before any reader ran.
- Every new and re-read case agrees with its reader.
- The only disposed comparisons are the 36 unchanged G3-D1/G3-D2 dispositions, each bound to both values.
- I checked the readers' new figures and the clauses behind each fix on the page images (`verification/g3/scan_spot_checks.yaml`, `correction_round`).

## F1 — the invoice header set the well class (Q8)

**Fix.**
- **Source:** DDS Cl.4 (p3) says "The well class stated in the call-off governs the whole well". P2 and P3 (p11) apply HPHT and Extended Reach "where the call-off so states".
- **No call-off evidence:** no call-off is supplied, and no report states a class.
- **Engine (`audit/g3_dds.py`):** each of the 7 class-rated services is priced under every class, and each class gets a full trace.
- **Status:** the amount is `conditional`, with the condition `class` owned by G5.
- **Header disclosure:** the invoice header's class is disclosed on the line as "the claim, not authority".
- **Rate check:** a billed rate that equals one class's rate leaves the rate check unresolved. A billed rate that matches no class is `rate_differs`.
- **PD-210:** it stays class-free (17B, D1) and conditional on the nomination on all 2,390 lines, owned by G5.

**Audit counterexample.** MDS-00001-008 / MW-310 used to give 2,953.29 "determined" under a Standard header and 3,913.11 "determined" under an HPHT header. Now both headers give identical results: status conditional, no single rate, and three alternatives (Standard 2,953.29; Extended Reach 3,470.12; HPHT 3,913.11). The test is `test_f1_header_class_does_not_set_the_rate`.

**Negative controls** (they fail as intended). An engine that takes the header class is rejected twice:
- X2 reports "class-rated service without every admissible class";
- X6 reports "a contract value changes with a claim-stated classification".

The tests are `test_f1_control_x2_*` and `test_f1_control_x6_*`.

**Exposure.** 24,217 lines (24,215 payable). Their values, in USD, by class:

| Class | Value (USD) |
|---|---|
| Standard | 66.79 M |
| Extended Reach | 78.48 M |
| HPHT | 88.49 M |
| Header-proxy reading (the old behaviour) | 73.33 M |

**Independent readers:** DDS-S66, DDS-S67 and DDS-R23, plus 19 re-read class-rated cases, all agree.

**Not established.**
- The call-off facts themselves.
- Consistency of the header class within a well: it corroborates the header's consistency, not the call-off's content.

## F2 — the application set the ground class

**Fix.**
- **Sources:**
  - CW S4 (p10): material is "classified at the point of excavation and recorded on the daily excavation record", and "a classification not recorded on the day ... shall be taken to be G2".
  - Cl.5 (p3): the Engineer determines the class and confirms it in writing.
- **Engine (`audit/g3_cw.py`), which class applies:**
  - 27A's G2 for work after 27 Sep 2025;
  - otherwise, the class recorded on the supplied site record;
  - otherwise, every class G1–G5, as `conditional` with owner G5.
- **What the line discloses** in the third case:
  - S4's G2 as the value if nothing was recorded on the day;
  - the application's class, as the claim.
- **Why no default is taken:** an unsupplied record is not proof that nothing was recorded, so neither G2 nor the claim's class is selected.
- **Unverifiable comparison:** where no record is supplied, `ground_differs_from_record` is `unresolved`. The v3 readers raised this independently, and they were right.

**Audit counterexample.** PA-00031-06 / A.12.050 claims G4 with no record. It used to give 72.05 determined, and 52.40 if the claim said G2. Now it is conditional over G1 49.26 / G2 52.40 / G3 58.69 / G4 72.05 / G5 85.41, with identical results whichever class the claim states. The test is `test_f2_application_ground_class_does_not_set_the_rate`.

**Negative controls.** An engine that takes the claimed class is rejected by both X6 and X2 (`test_f2_control_*`).

**Exposure.** 650 lines, as in the audit:
- 649 payable and conditional, plus 1 not payable because its record is missing;
- 521 claim a class other than G2.

Their value is SAR 7.97 M to 13.90 M across the classes. The old claim-as-proxy reading gave SAR 10.09 M to 10.16 M.

**Independent readers:** CW-S59 (no record), CW-S60 (the record's G3 governs), CW-S61 (27A), CW-R23 (PA-00031-06), and 5 re-read cases, all agree.

**Not established.** Whether the unsupplied daily records exist, or what they state.

## F3 — the arithmetic check ignored the band division

**Fix.** Cl.28 (p6) says: "where Clause 30 divides a quantity at a rebate threshold, each part is multiplied by its own rounded rate and the amount is their sum". Schedule 4 Part 3 (p24) says a measurement crossing a band "is divided at the band".

Where the band is G4 state (unknown), `band_split` checks whether a division at a band edge reproduces the billed amount exactly:
- it uses the contract's own band rates, per ground alternative;
- the division is between adjacent bands, or across all three where the quantity exceeds band 2;
- each part is taken at the quantity's precision.

If a division reproduces the amount, the arithmetic check is `unresolved`, with the division stated. If none does, it is a finding. No allocation is chosen, so no G4 work is done early.

**Audit counterexample.** PA-00076-08 / D.41.040 is now `unresolved`: 207 × 34.56 (band 1) + 51 × 32.83 (band 2) = 8,828.25, found independently. Across the population, 29 of 32 civil arithmetic findings become unresolved and 3 remain findings, as the audit found.

**Counterparts:**
- CW-S62 (A.13.010, amount 4,950.00, above every band's whole-quantity amount) is a finding;
- CW-S63 (a consistent amount) has none;
- CW-R22 (PA-00610-02, no bands) stays a finding.

**Negative control.** With the division disabled, PA-00076-08 becomes a finding again (`test_f3_control_*`). X1 requires each of these outcomes (scope item "F3").

**Reader prompt.** The fix is in a new version only, `prompts/phase3/g3_expected_cases_v3.md`. v1 and v2 are unchanged. Its arithmetic definition now follows Cl.28, so the comparison target no longer carries the old one-rate assumption.

**Not established.**
- Which division, if any, is the true one: that is G4's cumulative quantity.
- Divisions at a finer precision than the billed quantity's.

## F4 — PD-210 priced a different quantity from the one it allowed; X3 missed it

**Fix (`_pd210`).**
- **Allowed metres:** the charged metres where they are within 25A's 1% of the report-supported metres for the charged interval; otherwise the supported metres.
- **Parts:** the parts always carry the allowed metres. In one band, the charged metres take that band's rate (Cl.23: "the band in which the metres lie").
- **Crossing charges:** if a charge crosses a band edge and differs from its interval, the difference can't be placed. Each placement becomes an alternative (`tolerance`, owner G5), and no inconsistent fields are emitted.
- **Depths finding:** `depths_differ_from_quantity` (Cl.34) is now recorded whatever 25A allows. The v3 reader was right on DDS-S69.

**Audit counterexample.** The audit's synthetic 2,900–3,000 m interval with 101 m charged is now 101 m × 58.15 = 5,873.15, with parts, allowed quantity and amount in agreement:
- 99 m gives 5,756.85;
- 102 m gives 100 m, 5,815.00;
- the crossing 1,450–1,550 m charge with 101 m gives two alternatives, 5,067.35 or 5,083.15.

Independent readers DDS-S68 to DDS-S71 agree.

**X3 strengthened.**
- Replay accumulates part quantities, and they must equal the allowed quantity.
- Every part's rate must be its Schedule 2 band's rate.
- Every part's depths must lie inside that band, with the boundary belonging to the shallower band.
- A part whose quantity differs from its depths must name 25A.
- Every alternative's trace is replayed.

**Negative controls, the audit's two failures:**
- a coherent part rate of 999.00 is rejected: "PD-210 part rate 999.00 is not band 2's 58.15";
- a coherent 100 m part on a 101 m allowance is rejected: "trace quantity 100 != allowed quantity 101".

**Not established.** No population amount changed: all 2,390 PD-210 billed quantities equal their intervals, and the value if nominated is unchanged at USD 21,356,375.55.

## Q5 residual — DD-120, RM-530 and HC-630

**Why Cl.2 does not settle it.** The texts read on the scans:
- **Schedule 8 (pp27–28):** "each circulating or back-reaming hour" for both DD-120 and RM-530, and for HC-630 "each BHA run, as Clause 26 describes".
- **Cl.26 (p7):** covers only DD-111 and LW-420.
- **Cl.21 and Cl.30 (pp6–7):** a circulating hour for DD-120, and back-reaming hours and clean-out runs "in the numbers recorded".
- **Cl.2 (p3):** "A Schedule prevails over a Part". But the same clause lists the contract documents as Parts I–VII, Schedules 1–6 and Appendices A–C. Schedule 8 (and Parts VIII–IX and Appendices D–G) are bound in the contract but not listed. The civil Cl.2 lists even less.

So Cl.2's precedence doesn't rank Schedule 8 by its own terms. This is recorded as new decision **D8** (`spec/open_questions.yaml`): every bound document is operative, the lists are incomplete, and the listed-only alternative would strip Cl.26/28/46, 17A, 21A and 25A. No precedence resolution is claimed.

**Fix: scoped alternatives on every line** (Q5 is now "decided in part"):
- DD-120 hours are computed as circulating (Cl.21, Sch 1) and as circulating-or-back-reaming (the Sch 8 row), each crossed with the Q4 readings.
- RM-530 is computed likewise.
- HC-630 is computed as the recorded count (Cl.30) and as one per BHA run (Sch 8).

**Where the readings differ:**
- On 3 lines, the readings differ, and those lines carry every combination:
  - MDS-00856-039, DD-120: USD 5,118.40 to 6,781.88;
  - MDS-01338-026 and MDS-01651-025, RM-530: USD 3,174.60.
- On all 428 HC-630 lines the two HC-630 readings agree. They carry the G4 dependency "once_per_run (HC-630 under the Schedule 8 reading)".

**Owners:** G5 for the readings; G4 for the once-per-run event.

**DD-102** stays decided (A, 8,151 lines).

**Independent readers:** DDS-S64 (8 circulating plus 3 back-reaming hours) and DDS-S65 (two clean-out runs) agree. The reader gave both readings in each.

**Not established:** which reading the parties intended.

## Also required

- **X6, claim-derived classifications.** It now also perturbs the invoice's well class, the application's ground class, and the line's hole section and day status. No contract value changes on any of the 98,990 lines. X2 also requires every admissible class to be carried, with an owner.
  - The zone and night work are claim facts: Cl.4, Cl.7 and Cl.42 name no other evidence. They are not perturbed. Instead they are disclosed on each line and decided as **G3-D3**, with the alternative's effect:
    - zone: 6,978 lines, SAR 141.4 M to 180.0 M across the zones, against SAR 158.6 M as stated;
    - night: 167 lines, SAR 7.09 M without the uplift, against SAR 7.75 M as stated.
- **Currency separation.** Every value in `decision_scopes.json` is keyed SAR (civil) or USD (drilling). G3-D1 is now SAR 0.89 M to 1.00 M plus USD 0.90 M to 0.98 M. X4 rejects a mixed value; the control uses the audit's own 1,698,500.78.
- **G3-D1 value versus payment.** "Payable" means the local contract value is supported. Whether the non-compliant submission is payable now is left to G5. This is stated in the decision's `value_vs_payment` and in the scope note; the test is `test_d1_value_payment_distinction_and_currencies`.
- **Q11 owner.** Q11 now blocks G5. X4 rejects a question left open or decided in part without a later owner, and rejects a partly decided entry without a residual owner.
- **Q13 preserved.** Part E is used, corroborated by the lost tool's own history in 54 of 54 losses; the value is unchanged at USD 31,427,958.99.

## Artifacts

- **Engines:**
  - `audit/g3_core.py`: results now carry `conditions` and unresolved findings;
  - `audit/g3_cw.py`: F2, F3 and the disclosures;
  - `audit/g3_dds.py`: F1, F4, the Q5 residual, and alternatives with full traces;
  - `audit/terms.py`: band edges;
  - `audit/g3_run.py`: per-currency scopes, per-reading effects, and G3-D3.
- **Registers:**
  - `spec/g3_decisions.yaml`: Q5, Q8 and Q11 decided in part with residual owners; G3-D1 value/payment; G3-D3;
  - `spec/open_questions.yaml`: Q5, Q8 and Q11 now block G5; D8 added;
  - `spec/question_scopes.json`: D8's scope.
- **Checks:**
  - `tools/verify_g3.py`: X1 correction scope items and the rate boundary under every class; X2 completeness; X3 PD-210 parts and every alternative; X4 owners and currency; X6 claim perturbation;
  - `tools/g3_case_compare.py`: alternatives, unresolved findings, per-version vocabularies, and re-read supersession.
- **Cases:**
  - `verification/g3/cases/correction_{cw,dds}.yaml`;
  - packets `*_correction.jsonl` and `*_reread.jsonl`;
  - `expected_*_correction.jsonl` and `expected_*_reread.jsonl`;
  - `prompts/phase3/g3_expected_cases_v3.md`.
- **Tests:** `tests/test_g3_corrections.py` (22 tests); `tests/test_g3_gate.py` (6 controls retargeted to non-class-rated lines, every trace or the new wording, none dropped).

## Open items with owner

| Item | Owner | Scope |
|---|---|---|
| Class-conditional amounts | G5 | 24,215 lines |
| Ground-conditional amounts | G5 | 649 lines |
| PD-210 nomination | G5 | 2,390 lines |
| PD-210 tolerance placement | G5 | 0 real lines |
| Q4 | G5 | 7 lines |
| Q5 residual readings | G5 | 3 lines |
| HC-630 once per run | G4 | 428 lines |
| Q11 wrong-unit remedy | G5 | 0 lines |
| Band state | G4 | 1,026 lines |
| Band-split arithmetic | G4 | 29 lines |

The G3-D1, G3-D2 and G3-D3 decisions and D8 are recorded with their alternatives.

## Time

About 55 minutes of active work, 16:30–17:25 UTC on 2026-09-26, including four reader runs of about 5–9 minutes each, done in parallel.

## Blocked on me

- Nothing blocks the round.
- I can't push tags, so the gate3-r1 SHA and annotation text are in the conversation for you to create the tag.
- For your decision rather than as a blocker: D8, G3-D3, and the choice to keep the Q5 residual open rather than resolve it by Cl.2 are all recorded with alternatives. Overruling any of them changes only the named lines.

## Changed

- **Engines, registers and checks:** as listed under Artifacts.
- **Case material:** 17 new cases, 24 re-reads, prompt v3, and 4 reader files.
- **Regenerated outputs:** `verification/g2/*` (run context) and `verification/g3/*`.
- **Documents:** `Phase3_TASKS.md` (correction round section), a supersession note in `Phase3_G3.md`, and `README.md`.

## Found

- **Cl.2 lists (D8).** Both contracts' Cl.2 lists omit documents the contracts rely on, so Cl.2's precedence can't rank Schedule 8.
- **Unverifiable ground comparison.** It was silently treated as passing; it is now unresolved (a reader finding).
- **Missing depths finding.** PD-210 above tolerance did not record Cl.34's depths finding (a reader finding).
- **X1 boundary predicate.** It assumed single rates. It now requires the rate to change under every admissible class.
- **Reader prompt page error.** I gave the civil re-read reader Appendix B at pp30–31; it is on p36. The reader found it. Its result followed 29A over the illustrative example, which agrees with the G1 override register.
- **Earlier miscount.** My last G3 commit message said 273 lines for G3-D1; the correct figure is 471, which `Phase3_G3.md` already records.

## Not confirmed

- **Facts no supplied document records:** the call-off (class, nomination), the daily excavation records and Engineer's confirmations (ground), the band state, and the zone and time of work.
- **Reader independence:** it remains instructed, not enforced. The correction-round readers ran after the engines existed, although their inputs were committed first.
- **Contested readings:** the Q5 residual, D8, G3-D1, G3-D2 and G3-D3 are my readings with computed alternatives; none is confirmed by the parties.
- **Civil FX/index half-even at an exact half:** still not discriminated by a case.
- **Order-independent cross-line logic:** still excluded by code review and a token scan only.
