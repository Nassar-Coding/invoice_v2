# Phase 3 G5 — Full invoice outcomes

**Scope:** plan §2 G5 (artifacts/phase_inputs/Phase2_plan.md): combine the G3 line results and the G4 state into one
outcome per invoice (flag, category, expected judged total, confidence) in the template format, with DS-900, VAT and
retention applied per the contracts. Q9 closed first; owner decisions Q7 C and Q6 D applied; every other G5 item decided
from source or resolved by the ambiguity rule.
**Baseline:** gate4 = 9fa5514 (remote tag verified). At the start the tree was clean and main = origin/main = 9fa5514.
**Challenge:** majedzahrani3/invoice-auditing-level-2 @ aef4924 (README, submission_template.csv, contracts,
guidelines). **Commits on main:** a1ba628 (Q9 rule and decisions), 7c371e4 (sample packets, inputs only), d72d413
(reader outputs), 034dda5 / 14cfdac (engine, outcomes, effects), 7ff3954 (exit checks, controls, fixes), then this
report. The final SHA is in the reply. No G6/G7 work; submission.csv exists only as G5's output artifact
(verification/g5/submission.csv); no tag moved.

## 1. What was implemented

| Module | Content |
|---|---|
| `audit/g5_outcomes.py` | **Invoice assembly.** Every template invoice gets its header and its claim lines, each line carrying the G4-valued copy of its G3 result.<br>**Scenarios.** Readings decided from source are fixed (Q12 A, Q14 A, Q6 A, Q11 A). The owner's Q7 C allocation is applied: the earlier-submitted invoice's charge stands, and a same-day tie between invoices stays open. The invoice's own statements of unsupplied facts (well class, ground class) are tested in every scenario (Q9-3). Readings still open (order, Q6 D, Q4, Q5, Q1 recipient) are enumerated as scenarios.<br>**Evaluation per scenario.** Each line's contract value is compared with its billed value and its established findings. Also checked: header arithmetic (civil total = sum of lines; drilling DS-900, net, VAT and total), procedural findings, and the payment-only duties (the A3 adjustment on its recipient, the 45A release).<br>**Outcome.** Flag, category, expected total and confidence follow Q9-1..Q9-6. Lines are never repriced. |
| `audit/g5_run.py` | Writes verification/g5/: `outcomes.jsonl` (per invoice: scenarios, findings with their lines, line values, check coverage 1–12), `summary.json`, `decision_effects.json` (flags under every alternative) and `submission.csv` (the six template columns, template order). |
| `tools/g5_samples.py`, `tools/g5_sample_compare.py` | The independent sample (section 4) and its comparison. |
| `tools/verify_g5.py`, `tools/check_g5.sh` | Exit checks Z1–Z9 (section 3). `check_g5.sh` runs G0–G4 (incl. the whole test suite), then G5. |
| `spec/g5_decisions.yaml` | The Q9 rule and every G5 decision with its source, alternatives and effect key. |
| Registers | `spec/open_questions.yaml`: every G5-owned question carries a `g5_disposition`. Q2, Q6, Q7 (owner), Q9, Q10, Q12 and Q14 are decided at G5. Q1 is resolved by rule. The G3/G4-owned Q4, Q5, Q8, Q11 and the D8-I1 interpretation keep their gates' statuses (a G3 safeguard requires it), are resolved by rule, and are reported at G7. |

## 2. The Q9 rule (spec/g5_decisions.yaml `q9_rule`)

**Q9-1, flag semantics.**
- An invoice is wrong when any of the twelve checks fails:
  - a line value that differs from what was billed;
  - header arithmetic that does not reconcile;
  - an established breach with no money effect (identity, term, window, period, evidence);
  - a payment-only defect the invoice must carry: the A3 adjustment omitted from its recipient, or the 45A release omitted.
- Sources: README "flagged 1 if you believe the invoice is wrong" and its list of error types, which includes "an adjustment omitted"; the guidelines' twelve checks.
- Alternative B, flag only a changed judged total, would flag CW 77 / DDS 110 instead of 88 / 125.

**Q9-2, open readings** (the ambiguity rule).
- Wrong under every admissible reading: flag 1 with the confidence its evidence supports.
- Readings disagree on whether it is wrong: flag 1 at 0.50. This is a flagged uncertainty (README: "a stated doubt costs a reviewer a few minutes"); the reading that matches the bill is never chosen.
- Readings agree it is wrong but disagree on its total: confidence at most 0.60.
- The expected total is always the total under the working reading, which is chosen from source before any comparison with the bill.

**Q9-3, facts assigned to documents not supplied** (DDS well class, CW ground class, PD-210 nomination).
- Every admissible value is priced (G3), and the invoice's own statement is tested in every scenario. A statement the scenario contradicts is itself a breach, so the invoice can be correct only in the scenario matching its own statements.
- It is flagged when it is wrong in that scenario, and therefore in every scenario.
- It is not flagged when it is fully correct there and nothing in the records contradicts it. Its confidence is then capped at 0.80, because the governing document is missing.
- The statement never prices anything.

**Q9-4, unknown total.**
- Confidence 0.30, flagged only when a check fails, expected total = the best-supported value.
- 0 invoices on the pinned data.

**Q9-5, confidence rubric** (plan §11 levels; these are conventions, not calibrated probabilities):

| Value | When |
|---|---|
| 0.95 | The same outcome and amount under every reading and input. |
| 0.80 | Rests on a stated unsupplied fact, the owner's Q7 C allocation, or a procedural/payment-only flag. |
| 0.60 | Readings agree the invoice is wrong but disagree on its total. |
| 0.50 | Readings disagree on whether it is wrong. |
| 0.30 | The total cannot be formed. |

**Q9-6, categories.** The ordered root categories of the established findings, with no symptom repeated; blank when not flagged.

## 3. Evidence per exit condition (verify_g5 on the population: all PASS)

| Exit condition (plan §2, G5) | Check | How | Result |
|---|---|---|---|
| Every invoice has an outcome (goal: all 2,806, exactly one each) | **Z1** | Template ids against outcomes; `submission.csv` schema, order, binary flags, category iff flagged, integer minor units, billed cents = 100 × `application_total` / `invoice_total`, confidence in [0, 1]. | PASS: 2,806 outcomes for 2,806 unique template ids; 0 missing, 0 extra. |
| … check coverage | **Z2** | Each of checks 1–12 has a recorded status on every invoice, over exactly its claim lines. | PASS |
| … findings, amount status and an evidence trail | **Z3** | A flag implies at least one established finding with its line or header. The category equals the root categories of those findings, and every finding code is mapped. An unflagged invoice has no finding under any scenario. | PASS |
| Monetary and procedural outcomes remain distinct | **Z4** | A procedural- or payment-only flag keeps the contract value (no blanket zero). Every billed line amount, rate and header total is multiplied by 1.37 and increased by 11.11; no expected total may move. | PASS (after the fix in section 7) |
| Independently reviewed complete invoices reconcile step by step | **Z5**, **Z6** | Z5: flag and expected total of 25 sampled invoices against 8 isolated readers (section 4), with git order packets → readers → engine. Z6: every expected total recomputed from its line values with exact rational arithmetic (DS-900, VAT half-even). | PASS: 48 of 50 reader results agree; 2 settled against the scan. Every total reconciles. |
| (supporting) ambiguity rule and rubric | **Z7** | flag = 0 only when correct in every scenario; disagreement at 0.50; unsupplied-fact rows at most 0.80; unformed at most 0.30; only rubric values. | PASS |
| (supporting) decisions and registers | **Z8** | Every G5 decision has a computed effect; no question blocks G5; the owner's decision is recorded as the owner's. | PASS |
| (supporting) reproduction and boundary | **Z9** | Committed outputs reproduce; a digest of all G3 results and G4 state is identical before and after G5. | PASS |

## 4. Expected-outcome agreement (independent sample)

**Selection** (tools/g5_samples.py). The selection uses raw data only, never engine output:
- 7 civil and 6 drilling invoices drawn at random (seed 5505). The civil draw is from band-free applications; the drilling draw is from invoices of at most 22 lines.
- 7 civil and 5 drilling invoices picked for raw features: header arithmetic, submission window, the same item/site/date billed twice, the A3 issue-date submissions, and the DS-900 line.
- The packets were committed (7c371e4) before the readers' outputs (d72d413) and before any G5 engine commit.
- The 8 readers were isolated: contract scans, records and guidelines only. Two readers per packet.
- The engine code was written while the readers ran; the readers could not open it.

| Invoice | Engine flag / expected / confidence | Readers |
|---|---|---|
| PA-00735 | 0 / 61,568.79 / 0.80 | r1 agrees. r2 flagged it (billed 7 against a survey of 8): settled **engine** — 33A (p32) pays a quantity not above the survey as measured. |
| PA-00047, PA-00764, PA-00376, PA-00671, PA-00340 | 0 / as billed / 0.95 | all agree |
| PA-00740 | 0 / 320,550.78 / 0.80 | agree |
| PA-00613 | 1 / 60,849.08 / 0.80 (timing; signature) | agree: late, and DX-00089 not countersigned |
| PA-00708, PA-00699 | 1 / as billed / 0.80 (timing) | agree |
| PA-00043 | 1 / 231,425.26 / 0.80 (arithmetic) | agree: header 32.18 above its lines |
| PA-00111 | 1 / 368,252.12 / 0.80 (evidence; duplicate) | agree |
| PA-00006 | 1 / 353,308.02 / 0.50 (adjustment) | agree (Q1 A tie) |
| PA-00443 | 1 / 280,688.88 / 0.50 (adjustment) | r1 agrees. r2 adopted 31A and gave 0, with 1 as its alternative: settled **both** (Q1 open → Q9-2). |
| MDS-00753, MDS-01738, MDS-00751, MDS-00448, MDS-00525 | 0 / as billed / 0.80 | all agree |
| MDS-00072 | 1 / 1,455,037.84 / 0.80 (discount) | agree: DS-900 missing |
| MDS-00282 | 1 / 521,298.25 / 0.80 (discount) | agree |
| MDS-01268 | 1 / 50,573.00 / 0.80 (eligibility) | agree: RM-511 with no hole opener in the hole |
| MDS-00537, MDS-01258, MDS-00828 | 1 / as billed / 0.80 (timing) | agree |

Two readers raised doubts they did not act on:
- Drilling readers noted that under other 21A hour readings some hourly invoices would flip. These are the Q4 readings; on the pinned data only 7 invoices carry Q4 alternatives, and none of them is in the sample.
- One civil reader (r2 of the second civil packet) noted P3 on a PA-00740 standing line, and did not apply it.

## 5. Decisions: flags per contract under each alternative (verification/g5/decision_effects.json)

Adopted flags: **CW 88 of 900 (9.8%), DDS 125 of 1,906 (6.6%)**.

| Item | Adopted (source or rule) | Lines / invoices it bears on | Flags under each alternative (CW / DDS) |
|---|---|---|---|
| Q9 | Q9-1: any breach | all | B, changed total only: 77 / 110 |
| Q2 | A: adjustment outside the judged total (45A p32; Cl.36-40 p8) | the 8 A3 candidate recipients | B: 88 / 125 (8 expected totals change, no flag) |
| Q1 | Open; ambiguity rule; C (per well) rejected, since 36A is singular | CW PA-00006/00023/00380 (A), PA-00443 (B); DDS MDS-01625 (A), MDS-01585/01631/01645 (B) | A only: 87 / 122; B only: 85 / 124 |
| Q7 C | **Owner**: the earlier invoice's charge stands | 6 lines / 3 DDS invoices (each pair within one invoice) | either charge stands: 88 / 125 (no change) |
| Q6 D | **Owner**: both kept; ambiguity rule | PA-00801-05 (1 invoice) | A only: 88; B only: 87 |
| Q6 A/B | A ('the quantity measured', Sch 4 Pt 3) | 0 lines | B: no change |
| Q12 | A: reset on 5 Jan 2026 (3A p32, 'each following Contract Year runs from that anniversary') | 270 lines / 181 CW invoices | B: **248** / 125 |
| Q14 | A (DDS 3A p35) | 0 lines | B: no change |
| Q11 | A | 0 lines | B: no change |
| Q4 | Open; ambiguity rule; working reading A | 7 DDS invoices | A only: 125; B only: 125; C only: 122; counts only: 121 |
| Q5 residual / D8-I1 | Open; ambiguity rule; working reading Sch 1 / Cl.21 / Cl.30 | DD-120: 1 invoice; RM-530: 2; HC-630: 0 | Sch 8 only: 124 (DD-120), 123 (RM-530) |
| order | Open; ambiguity rule; working reading Cl.30 wording | 8 lines / 8 CW invoices | Cl.30 order only: 80; each other order: 82 |
| Q8 class | Q9-3 (stated class tested in each scenario) | 24,215 lines / 1,906 DDS invoices | B, query all: 386 / **1,906**; C, defaults (Standard/G2): 359 / 883 (combined facts policy) |
| Q8 ground | Q9-3 | 649 lines / 335 CW invoices | included in the Q8 B/C rows |
| PD-210 nomination | Q9-3 (the charge states the nomination) | 2,390 lines / 638 DDS invoices | B: in the query row; C (no nomination): all 638 wrong |
| G3-D1 | Decided at G3: a procedural breach keeps the line's value | 471 lines / CW 8, DDS 12 | not payable now: these invoices are already flagged; only their totals change |
| G3-D2 | Decided at G3 | 33 lines / 3 DDS invoices | all lines not payable: already flagged; totals change |
| G3-D3 | Decided at G3: zone and night as stated | 7,746 lines / 900 CW invoices | not computed per invoice; every civil value would become zone-conditional |
| Q10 | A: only what the contract requires is added | — | B not computed |
| DS-900/VAT | Cl.38-40 (p8), half-even | all drilling | — (3 DS-900 findings: MDS-00072, MDS-00282, MDS-01049) |
| retention/45A | Payment fields; release on PA-00678 | PA-00678 | release omitted: flagged under every reading |

Several alternatives would take a contract far outside the README's 5–8% (Q12 B at 27.6%; facts at defaults or as queries at 40–100%). That context corroborates the adopted readings; it does not decide them. Q12 is decided on the words of 3A, and the facts on Q9-3.

**Population outcome summary:**

| Contract | Flagged | Basis | Judged total changed | Confidence bands |
|---|---|---|---|---|
| CW | 88 | 75 wrong under every reading; 13 readings disagree | 69 | flagged: 40 @0.95, 35 @0.80, 13 @0.50<br>unflagged: 514 @0.95, 298 @0.80 |
| DDS | 125 | 117 wrong under every reading; 8 readings disagree | 110 | flagged: 114 @0.80, 3 @0.60, 8 @0.50<br>unflagged: 1,781 @0.80 |

- Every drilling invoice rests on the unsupplied call-off class, so none is above 0.80.
- 0 invoices are unpriceable.
- Categories: CW rate 38, duplicate 18, timing 5, adjustment 4, arithmetic 3, evidence 3, …; DDS rate 51, quantity 21, eligibility 7, timing 6, arithmetic 6, adjustment 4, discount 3, … (summary.json).

Two stated-fact findings came out of Q9-3:
- 4 civil lines are priced at a ground class other than the one they state (PA-00291-05, PA-00320-04, PA-00509-02, PA-00898-01), and 5 at no admissible class.
- 2 drilling invoices are priced at a class other than their header's.
- All of these are flagged under every class.

## 6. Negative controls (tests/test_g5_gate.py, 20 tests) and falsification (tests/test_g5_falsification.py, 9 tests)

| Check | Defect injected, and the check fails |
|---|---|
| Z1 | A missing row, a flagged row without a category, a billed cents figure off by one, confidence 1.5, an outcome dropped. |
| Z2 | A lost claim line; a check with no recorded status. |
| Z3 | A flag without a finding; a category that is not the root categories of its findings; an unflagged invoice that is wrong under a scenario. |
| Z4 | A procedural invoice valued at zero; an engine that takes the (perturbed) billed total as its expected total. |
| Z5 | No settlements; a changed engine figure; a stale settlement; readers committed after the engine. |
| Z6 | A total 0.01 off its lines; a line changed without its total; the independent half-even routine checked on .xx5 boundaries. |
| Z7 | The matching reading chosen (a mixed invoice unflagged); an unsupplied-fact row at 0.95; a disagreement row at 0.95. |
| Z8 | An uncomputed effect; a question still blocking G5; the owner's decision unrecorded. |
| Z9 | A non-reproducing output; a G3/G4 digest that changes; G5 run on a history leaves G3/G4 identical. |

Falsification invoices, each built by hand, with expectations taken from the contract:
1. A correction that takes a drilling invoice below the DS-900 threshold. Expected total 276,000.00, not the billed total minus the correction.
2. Services of exactly 250,000.00, which get no discount.
3. A VAT half-even boundary.
4. Offsetting line errors with the total unchanged: flagged.
5. A header class contradicting the pricing: flagged under every class, at the stated class's total.
6. A line that cannot be valued: 0.30, flagged only when another check fails.
7. A same-day Q7 C tie between two invoices: both at 0.50. With a later invoice, only the later one is wrong.
8. An A3 adjustment that is carried is not flagged; one that is omitted is.
9. A procedural-only breach keeps its value, and is not flagged under Q9 B.
10. The expected total of a reading-disagreement invoice is independent of the bill. This is the regression test for the defect Z4 found.

## 7. Found (defects within G2–G5 scope, all fixed)

1. **Z4 (billing authority).** The expected total of an invoice where readings disagree was the first reading under which it is wrong. That depends on the bill (8 civil order invoices). It is now always the working reading's total.
2. **Z2.** Check 6 (identification) was recorded only on DS-900 lines. It is now recorded from the G3 code family of every line.
3. **Q9-4 consistency.** An input that could not be formed was itself counted as a failed check. It no longer is (0 invoices affected).
4. **Category attribution.** An amount wrong only because of a G4 rule left open (Q6 D exclusion) was labelled `rate`. It now carries the rule's category. Established G3 conditions such as unresolved arithmetic are not used as labels.
5. **Q7 C same-day tie between invoices.** This was never detected (the tie test compared the invoice to itself). The tie now stays open.
6. **`spec/g5_decisions.yaml` was not valid YAML** (an unquoted colon in a status). verify_g5 Z8 caught it.
7. **The G2 boundary test** now names the G5 module set, as it names the G3 and G4 sets. Every G2 evidence module is still checked.
8. **G1/G3/G4 safeguards kept.** The G3-owned register entries (Q4, Q5, Q8, Q11) and D8-I1 keep the statuses their gates' checks require.

No closed-gate defect had to be reopened. G3 results and G4 state are unchanged (Z9 digest).

## 8. What the evidence does not establish

- **The flag semantics are an interpretation of the README.** Procedural and payment-only defects are flagged (Q9-1). The organizer may count only invoices whose total is wrong: Q9 B gives 77 / 110 flags.
- **The unsupplied-fact rule (Q9-3) presumes the invoice's own statements** of class, ground and nomination are not false when nothing contradicts them. The rule tests those statements, but no document can confirm them. 1,781 unflagged drilling rows and 298 unflagged civil rows rest on this, at 0.80.
- **Ambiguity-rule flags are doubts, not findings.** 21 invoices are flagged at 0.50 because readings disagree: Q1 recipients (8), order (8), Q6 D (1), Q4/Q5 (4). The owner forbids choosing the reading that matches the bill, so these are flagged.
- **The independent sample is small and biased.** 25 invoices; band-free civil applications; drilling invoices of at most 22 lines, plus raw-feature picks. The readers are subagents of the same model family reading the same scans, so shared misreadings would pass. Band-item lines were given readers as raw earlier billed quantities, not validated counts.
- **Expected totals are only as good as the G3 prices and G4 state.** Their own limits are in Phase3_G3*.md and Phase3_G4.md, including the unresolved G3 identification limits, the readings kept open and the first/last-report well endpoints.
- **Confidence values are the plan's conventions**, not calibrated probabilities.
- **G3-D3 (zone and night as stated) was not recomputed per invoice** under its alternatives.
- **The civil flag rate (9.8%) is above the README's 5–8%.** The excess is not explained here; the categories are dominated by `rate` (38) and `duplicate` (18). G6 owns the population review of residual clusters.

## 9. Time

G5 ran from 12:57 UTC (preflight) to about 22:00 UTC on 2026-09-28. The readers were blocked by a session usage limit from about 13:15 to 21:10 and relaunched, and the worker restarted once (a killed verify run). Active work was about 3.5 h. The plan's budget is 5.3 h for G4/G5 together.

## Blocked on me

Nothing blocks G5 closure. Two points you may want to rule on; each is reported with its counts and needs no action to close G5:
- Q9-1: whether procedural and payment-only defects should be flagged (B: 77 / 110).
- Q9-3: whether the invoices' own class and ground statements may stand where nothing contradicts them (the alternatives flag 40–100% of invoices).

## Changed

- **New:** `audit/g5_outcomes.py`, `audit/g5_run.py`; `tools/g5_samples.py`, `g5_sample_compare.py`, `verify_g5.py`, `check_g5.sh`; `tests/test_g5_gate.py`, `test_g5_falsification.py`; `spec/g5_decisions.yaml`; `prompts/phase3/g5_expected_outcomes_v1.md`; `verification/g5/*` (including `submission.csv`).
- **Changed:** `spec/open_questions.yaml` (G5 dispositions), `tests/test_g2_controls.py` (named G5 module set), `Phase3_TASKS.md` (G5 section).
- **Regenerated:** verification/g2, g3 and g4 outputs (run context only).

## Found

The eight items in section 7, all fixed. No G2/G3/G4 defect was found.

## Not confirmed

- Whether the organizer counts procedural and payment-only defects as wrong.
- Whether the stated facts are true.
- The correctness of the 21 ambiguity-rule flags.
- The reason for the civil flag rate above the README range (G6).
- Outcomes on invoice shapes beyond the sample and the constructed invoices.
