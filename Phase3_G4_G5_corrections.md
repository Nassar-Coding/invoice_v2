# Phase 3 — G4/G5 correction round

Closes the ten frozen blockers of `Phase3_G4_G5_audit_Agent2.md` (G4 NOT PASS at gate4 `9fa5514`, G5 NOT PASS at gate5
`13eb768`). Order followed: the four G4 blockers first, G5 regenerated from the corrected G4, then the six G5 blockers.
Q12 and the civil rate the audit upheld are left as they were. No G6/G7 work; no tag moved.

Preflight (confirmed before any change): clean tree; `main` = `origin/main` = gate5 `13eb768`; tag `gate4` → `9fa5514`,
tag `gate5` → `13eb768`.

Every blocker below is fixed as a class. Each demonstrated variant is rerun through the production pipeline (raw
same-format histories materialized as claims CSVs and report files → G2 → G3 → G4 → G5), or, where the audit perturbed
an actual invoice, on that invoice. Each exit check added or changed here has a **negative control**: the tagged gate4 /
gate5 module, loaded from git (`git show <sha>:<path>`), run on the same input and rejected by the corrected oracle for
the blocker's reason (`tests/test_g4g5_corrections.py`).

## 1. Commits

| Blocker | Commit | Population effect (flags CW / DDS; gate5: 88 / 125) |
|---|---|---|
| G4-B01, G4-B02 | `018c75e` | none (no overlapping PD-210 intervals in the population) — 88 / 125 |
| G4-B03 | `d251f8c` | none (no undated line except DS-900; no undated header) — 88 / 125 |
| G4-B04 | `393220b` | flags unchanged; 4 flagged civil invoices re-attributed rate → arithmetic — 88 / 125 |
| G5 regenerated on corrected G4 | (in `393220b`) | 88 / 125 |
| G5-B04 | `60205ae` | none — 88 / 125 |
| G5-B01 | `75e2efd` (+ `fab6962`, run-context regeneration) | CW 88 → 85; 25 CW and 114 DDS flagged rows 0.80 → 0.60 — 85 / 125 |
| G5-B02 | `6f697e6` | none (no unformed invoice) — 85 / 125 |
| G5-B03 | `5ec0fcf` | none (every payment field is 0.00) — 85 / 125 |
| G5-B05 | `82bb295` | none — 85 / 125 |
| G5-B06 | `1f797bf` | flags unchanged; 4 civil re-attributions (below) — 85 / 125 |

`fab6962` exists because `75e2efd` changed `audit/g5_outcomes.py` after the G2–G4 outputs had been generated: the run
context hashes every audit module, so at `75e2efd` the committed G2–G4 outputs carried the previous context and the
G2–G4 reproduction checks would have failed on that commit. `fab6962` regenerated them (values unchanged). From then on
every commit was made only after a full regeneration from the final code of that commit.

## 2. G4 blockers

### G4-B01 — annual footage counts each metre once and keeps prior allocations

**Fix.** One PD-210 model (`audit/g4_dds.py` `_pd210`): per well-day the admissible intervals are split into elementary
segments at every boundary; the metres before a segment (Q11 A, adopted) are the length of the UNION of the earlier
admissible intervals in the Contract Year — each metre once — and a charge whose date or depths are not established is a
possible earlier contributor (a range), never omitted. Repricing keeps the allocation (G4-B02): a charge is valued only on
the segments it keeps in the scenario.

**Variants (audit's raw DDS-H06 format).** (1) 39,990 m before, two charges of the same 44,490–44,510: the one admissible
interval is 1,934.50 (10 m at 98.70 + 10 m at 94.75) and it is kept by exactly one of the two charges in every scenario
(`test_b01_duplicate_interval_counted_once_and_allocation_kept`). (2) 39,950 before, duplicate 20 m, then a distinct
20 m: unique prior metres 39,970, the last charge 1,974.00 (`test_b01_later_interval_uses_unique_prior_metres`).
Replay after removing the earlier duplicate: 1,974.00 / 1,974.00 (`test_b01_replay_after_removing_the_earlier_duplicate`).
Overlap/band interaction: the variant-1 segment sits at the 40,000 m annual edge and composes with the allocation
(`test_b02_band_interaction_duplicate_at_the_annual_edge`).

**Oracle.** verify_g4 Y3 recomputes the metres before every segment from the claims as the union of intervals
(independent of the engine's segmentation); Y6 rejects overlapping footage segments ("a metre counted twice").

**Control.** gate4 `g4_dds` (loaded from `9fa5514`) gives both variant-1 charges the full 1,934.50 and, under Q11 A,
1,934.50 for variant 2 (39,990 prior): `test_b01_control_gate4_counts_the_duplicate_twice`.

**Not established.** The DS-900/VAT consequence on a full synthetic invoice is covered by the G5 recomposition, not by a
separate invoice-level test for this blocker; Q11's interpretation itself was not reopened (as the audit allows).

### G4-B02 — the overlap allocation is a complete joint domain over coverage

**Fix.** Each contested segment is assigned to exactly one covering charge; every combination is a scenario of one local
dimension `alloc@<well>/<date>`; each charge's value is the sum over the segments it keeps. Above 256 combinations the
charges are unresolved with honest bounds (no truncated domain presented as complete).

**Variants.** The three-interval chain A 1,500–1,600, B 1,550–1,650, C 1,600–1,700: B carries 0.00 / 2,907.50 /
5,815.00 over four joint allocations, each summing to 11,630.00 of unique service value
(`test_b02_three_interval_chain_complete_joint_domain`); contained and exact duplicates (1,500–1,700 and a second
1,500–1,600): every allocation keeps exactly the 200 m union (`test_b02_contained_and_exact_duplicate`).

**Oracle.** verify_g4 Y4 `pd210_coverage_errors`: the number of allocations is the product of the cover counts; under
every allocation the kept metres sum to the union length and no charge keeps more than its interval — checked from the
claims, not the engine's groups; billing plays no part.

**Control.** gate4's pairwise allocation lacks B's zero outcome and fails the coverage oracle
(`test_b02_control_gate4_pairwise_allocation_fails_the_metre_oracle`).

**Not established.** Q7 C is applied to allocations at G5 (each contested segment to the earliest-submitted covering
charge; a same-day tie stays open) — no population invoice exercises it.

### G4-B03 — unknown chronology stays a possible contributor; no omission, no sentinel

**Fix.** Civil bands: a measurement without a work date adds [0, its count] to every ledger of its item; a division
stays determined only where both ends of the start range give the same parts (provably unchanged). Civil duplicates:
an undated measurement of the same item/area that may have been submitted no later makes a dated one possibly
disallowed. 45A release, A3 recipients (both contracts), P23: a document without a submission date is a possible
recipient / earlier application — recipient "not established", release a range. DDS: an undated charge is a possible
repeat on each dated well-day of its service; an undated well event is never an established "not on its day" finding.
G5 Q7 C: the "9999" sentinel is gone; a candidate of unknown date leaves the standing open.

**Variants.** CW-H01 with the first 600 m² undated: the later 500 m² is unresolved (valid values 37,250.00 or
36,356.00), never a determined 37,250.00; the 400 m² that no start in [0, 600] can move stays 29,800.00. CW-H10 with the
first application undated: release 96.15..192.49, recipient not established {PA-9A001, PA-9A003} (not 96.15 with
not_established = []). DDS-H01 with the first invoice undated: the repeat is open; MDS-90001 0.50 (gate5: a definite
repeat at 0.80), MDS-90002 0.60 (its own daily-limit breach makes it wrong either way).

**Oracle.** verify_g4 Y2 `chronology_errors` (undated measurements listed in every ledger of their item; undated
documents inside every recipient; no "not on its day" finding without a date); Y3 starts each ledger at the undated range.

**Controls.** gate4 gives the 500 m² a determined 37,250.00 and the release 96.15 with nothing not established; gate5's
sentinel picks a keeper at 0.80; gate4 ignores an undated DDS charge (`test_b03_control_*`).

**Not established.** The population has no undated line (except DS-900, which carries no state) and no undated header:
these branches are exercised only by the constructed histories.

### G4-B04 — deferred rate/arithmetic checks completed against each band state

**Fix.** Under each established band scenario G4 completes the displayed-rate check (one band: that band's rate; a
divided measurement: one of the item's contract band rates — one rate field cannot carry every part) and, where G3
deferred it, the arithmetic (one band: quantity × displayed rate = amount; divided: the division of the billed
quantity). Verdict pass / finding / unresolved-with-per-scenario-`breaches`; G5 applies each breach exactly in its
scenario and completes G3's deferred multi-rate check against the scenario's rate.

**Variants.** The audit's case (first band, 600 m² at 71.52 with amount 44,700.00): rate and arithmetic findings, G5
flags it (`test_b04_wrong_rate_with_the_correct_amount_is_a_finding`); rate and amount judged independently (all four
combinations); valid splits pass, a rate that is no band's rate is a finding; a genuinely unresolved state never passes;
a Q12-dependent band carries the breach under Q12 B only (flagged when Q12 B is forced).

**Oracle.** verify_g4 Y7 `deferred_rate_errors` recomputes each verdict from the trace parts and G3's band rates of the
same scenario.

**Control.** gate4 leaves `rate_differs` unresolved and gate5 passes the invoice at 0.95.

**Population.** The first formulation (a divided line must display one of its parts' rates) flagged 11 civil invoices
whose divided amounts are correct and whose displayed rate is the item's band-1 rate — the blanket finding on valid
splits the audit forbids; it was replaced by the item-band-rate rule before commit. Committed effect: flags unchanged;
PA-00303, PA-00459, PA-00506, PA-00611 (flagged at 0.50) re-attributed rate → arithmetic — under the order in which each
is wrong, its displayed rate is right and its amount is not the division.

**Not established.** Which rate a divided civil line "should" display is not stated by the source; the rule accepts any
contract band rate of the item and judges the parts by the arithmetic.

## 3. G5 blockers

### G5-B01 — claim-stated class, ground and nomination never select the contract value

**Policy adopted — Q9-3 E, the missing-evidence rule** (`spec/g5_decisions.yaml`). Well class (Cl.4 call-off), ground
class (S4/Cl.5 excavation record) and PD-210 nomination (Cl.23 call-off) are evidence scenarios, separate from the
readings of Q9-2. The invoice's statement of such a fact never selects a value and is never itself a breach. Missing
evidence is not a breach: under a reading the invoice is right when some admissible value of every unsupplied document
makes it right, and wrong only when none does — an established breach whatever the document says, reported by the
findings that hold under every value (else `no_admissible_document`). Cl.4 ("governs the whole well"): where a well's
invoices can be right only under different classes, the class is one open fact shared by them (Q9-2). Numeric export:
`contract_total` = the total on the values the supplied evidence establishes for an absent document (EXPORT-D: S4 G2;
P2/P3 Standard; Cl.23 not nominated); a row exports its own billed total only where that is an admissible contract total
(EXPORT-E, stated in `expected_basis`), else `contract_total`. Confidence 0.80 unflagged fact-dependent; 0.60 flagged
where the total depends on the unsupplied document.

**Invariant and reproduction.** Actual MDS-00753 with only its header class changed: corrected 0 / 49,892.39 / 0.80
under HPHT, Standard and Extended Reach; gate5 0 / 49,892.39 under HPHT but 1 / 49,113.13 under Standard and
1 / 49,532.73 under Extended Reach. verify_g5 Z4 rotates every drilling header's class and every unrecorded civil ground
across the whole population: no flag, category, exported total, contract total or confidence moves. Tests: claim-only
change (three billed prices × four statements); inconsistent classes for one well (both flagged 0.50, class open) and a
consistent pair (both 0 at 0.80); both nomination outcomes; civil ground statement; the Z4 check against gate5.

**Population replayed.** CW 88 → 85: PA-00291, PA-00509, PA-00898 unflagged — exactly the three the audit found resting
solely on the stated ground (§5.3); each is right under an admissible ground and has no other finding. DDS 125 → 125
(no Cl.4 conflict in the population). 25 CW and 114 DDS flagged rows 0.80 → 0.60 (the total depends on the unsupplied
document); of these 25 CW and 74 DDS move their exported total to EXPORT-D. Six sample-reader totals (PA-00111,
PA-00613, two readers each) were settled `engine`: the readers' premise was the invoice's own ground (the rejected rule);
their totals are among the outcome's `admissible_totals`. A defect found on the way: exporting EXPORT-D for a flag
resting only on procedural findings (MDS-00537, late only, billed total admissible) would have asserted an unestablished
monetary error — fixed before commit by the EXPORT-E admissibility rule.

**Not established.** EXPORT-D is a named export on absent-document values, not proof of the call-off's or the record's
content; where the missing document says otherwise, the exported figure of a flagged fact-dependent invoice is wrong
(hence 0.60). Whether a stated class contradicting the invoice's own pricing is itself a breach is not tested (no
document to test it against).

### G5-B02 — no billed or zero substitution; unknown totals explicit

**Fix.** An unvalued line carries the least and greatest of its admissible values consistent with the scenario, or
[0, not bounded] where none is established; totals are bounds, drilling through DS-900 and VAT; `expected_status`
"bounded", `expected_bounds`, export EXPORT-U = the lower bound (named, owned by G5). Defect found: the invoice's own
billed services skipped an unvalued line, so its DS-900 check ran on too small a base — fixed.

**Reproduction.** The audit's raw PD-210 input (no start depth, end 1,500 m, 50 × 42.35 = 2,117.50): exported 0.00 with
bounds [0, not bounded], flagged (`depths_missing`) at 0.30; with the billed amount 9,999.00 the export is unchanged. gate5
exported 2,117.50 and 9,999.00. Also: failed-line and no-failure variants, a partially formed drilling invoice above
the DS-900 threshold (lower bound 342,700.00 through DS-900 and VAT), a bounded unvalued civil line, a missing billed
amount.

**Oracle.** verify_g5 Z4 executes the branch on the audit's raw input through the production pipeline and requires every
unformed row to export its EXPORT-U lower bound and every "formed" figure to be formed; the gate5 engine fails it.

**Not established.** The population has no unformed invoice: this branch is exercised only by constructed inputs.

### G5-B03 — payment duties reconciled to G4's amounts, recipients and ties

**Fix.** Adjustment (both contracts) and 45A release checked against the scenario's G4 account: exact, range, or not
established; codes omitted / differs / unsupported / not established; G4's release recipient — single, same-day tie or
undated candidates — is a scenario dimension; "not the recipient" is a scenario only where some reading or tie allows
it; a correctly zero account is no omission; Q2 B never takes a range endpoint.

**Reproductions.** On actual invoices (header fields perturbed in memory, net payable kept consistent):

| Perturbation | Corrected | gate5 |
|---|---|---|
| PA-00443 adjustment 0.00 → 0.01 (account 60,508.18 under Q1 B) | flag 1 / 0.80, adjustment | flag 0 / 0.95 |
| PA-00047 unsupported adjustment 12,345.67 | flag 1 / 0.80, `adjustment_unsupported` | flag 0 / 0.95 |
| PA-00047 unsupported release 12,345.67 | flag 1 / 0.80, `release_unsupported` | flag 0 / 0.95 |
| PA-00678 release set to 0.01 | flag 1 / 0.95, `release_differs` | flag 1 / 0.95, no release finding (and an invented rate category) |
 CW-H10 tie: PA-9A003 and PA-9A004 each flagged 0.50 with `release_omitted` in its own
scenario (gate5: both 0 / 0.95).

**Oracle and control.** verify_g5 Z3 `payment_errors` reconciles each payment field to G4's accounts independently; gate5
passes the cent, both unsupported postings and the tie.

**Not established.** Every payment field in the population is 0.00; the adjustment/release amounts themselves come from
G4's accounts (A3 on submitted valuations as the proxy for "certified").

### G5-B04 — local alternatives namespaced by their evidence group

**Fix.** Local dimensions named after their group: `order@<item>/<date>`, `earlier@<group>`, `stands@<group>`,
`stands-run@<group>`, `alloc@<well>/<date>`; kinds matched by base name; Q7 C keyed per group; options under a reading
not adopted no longer open local choices.

**Reproduction.** The audit's witness: PA-X01 187,953.50 / 188,066.50 / 188,251.50 / 188,364.50 and PA-X02 13,393.50 /
13,506.50 / 13,691.50 / 13,804.50, formed; two independent same-day tie groups (4 scenarios, right in exactly one);
Q12 stays global (the order group opens only under Q12 B). gate4 + gate5: formed = False, 0.30.

**Oracle.** verify_g5 Z6 joins every invoice's legal combinations line by line — two alternatives combine only where
they agree on every shared dimension — without the engine's list of open dimensions, and requires exactly its totals
and formed status; it rejects the gate pair.

**Not established.** The population's local groups were already disjoint in practice: no population outcome changed.

### G5-B05 — DS-900 single charge, sign, amount, threshold, rounding

**Fix.** `discount_split` (two or more nonzero charges), `discount_sign` (a positive charge), `discount` (a wrong sum:
amount, threshold, half-even rounding, omission); the line's well; ordinary-service obligations deliberately not
imposed.

**Reproductions.** Actual MDS-00018 with its DS-900 (−45,109.68) split into two −22,554.84 lines, header unchanged: corrected flag 1 / 0.60, `discount_split`; gate5 flag 0 / 0.80 (the audit's result). Constructed: one correct charge passes; offsetting and positive charges; threshold
exactly 250,000.00; half-even boundaries; a zero DS-900 line where none is due.

**Oracle and control.** verify_g5 Z3 `ds900_errors` recomputes the Cl.38 duty from the claim lines in exact rationals;
gate5 passes the split.

**Not established.** The quantity/rate content of a DS-900 line is not made an obligation (the audit's quantity-7 / rate
−1 probe), as Cl.38 is a special amount rule.

### G5-B06 — findings attributed to the violated obligation

**Fix.** A line whose value an established consequence changes keeps that cause (out-of-term work: `term`, a monetary
term consequence); otherwise what actually differs — quantity, displayed rate against the scenario's rate, displayed
arithmetic, band division, else `value_differs` — never "rate" by default. Procedural breaches are identity and timing
only; verify_g5 Z4 states that set itself.

**Reproduction.** The audit's fixture (600 m² B.22.010 at 74.50 = 44,700.00 on 2 October 2026): flagged `term`, expected
0.00, no `rate_differs`, no `release_omitted`, and Z4 passes its zero valuation; a genuine rate error on the same line is
kept. gate5 adds `rate_differs`.

**Oracle and control.** verify_g5 Z3 `attribution_errors`: a rate finding needs an established rate check, a
per-scenario breach, or a judged scenario in which the displayed rate is not the line's rate; a quantity finding needs an
admissible quantity below the billed one — from the line's own facts; it rejects gate5's invented category.

**Population.** Flags unchanged. PA-00140 and PA-00382 (order-dependent, 0.50): `rate_differs` → `band_crossing_not_split` (under the order in which each is wrong the displayed rate is a band rate and the amount is not divided). PA-00659: `rate; arithmetic` → `arithmetic` (the displayed rate is the rate of an admissible ground; the established arithmetic stands). PA-00678: the `rate` category on its out-of-term line removed (`term; evidence; adjustment`).


## 4. Independent audit, round 1 (commit `1f797bf`)

Three independent auditors examined `1f797bf`. They were given only the repository, the pinned snapshot and the gate
exit conditions: G4 state, G5 outcomes, and end to end. Each was told to break the gate, reproduce claims from raw
inputs, build same-format counterexamples and check that the frozen blockers stay closed. Their reports are reproduced
unedited in Appendix A (also `verification/g45_audit/auditor_{A,B,C}_*_round1.md`).

Every finding classed BLOCKER is fixed as a general rule. Each has a regression test with a negative control
(`tests/test_g45_audit_round1.py`): the reproduction passes on the corrected code, and the same input on the audited
commit `1f797bf`, loaded from git, fails for the finding's reason. Where an oracle applies, the corrected oracle also
rejects the audited code's output. By the owner's instruction, no recheck audit round was run. These tests and
controls are the evidence of closure; no second independent reading confirms them.

| Finding | Class (auditor) | Disposition | Fix | Test / control |
|---|---|---|---|---|
| A-1 PD-210 charge without depths is not a contestant | BLOCKER (b) | fixed | a charge whose date or depths are not established is a possible contestant of every segment it may cover (its interval; else the day's reported interval; else anywhere); under Q7 C a possible contestant that would stand leaves the choice open (`g4_dds._segments`, `g5_outcomes.standing_map`) | `test_a1_*`: later charge carries a 0 alternative, `charged_twice` unresolved, flag 1 at 0.50; `1f797bf`: flag 0 at 0.80, coverage oracle rejects |
| A-2 payable-None PD-210 counted as certain prior metres | BLOCKER (b) | fixed | Q11 A lower bound counts only metres of charges payable at G3 whose nomination is not in question (or is the valued charge's own section); the rest count in the upper bound only (`g4_dds._certain`) | `test_a2_*`: the line is not established (0.30); `1f797bf` determines 1,934.50 with an established finding; footage oracle rejects |
| A-3 Q11 B drops a report whose depth is missing | BLOCKER (b) | fixed | a report whose well, date or Part A depths are not established leaves the Q11 B count unbounded above | `test_a3_*`: Q11 B `[39900, None]`, line unresolved; `1f797bf` collapses to 1,974.00; oracle rejects |
| A-4 A3 account omits lines of undated documents | BLOCKER (b) | fixed | every line that may be protected (item re-rated by the instrument, submission not established to be on/after issue, work not established to be before every effective date) is in the account; unvalued lines leave the account open on the side their rate change can move it | `test_a4_*` (civil and drilling); `1f797bf` states an exact account; new Y2 oracle `a3_contributor_errors` rejects |
| A-5 G4 crash (StopIteration) on a release with an undated reading-dependent application | NONBLOCKING (loud) | fixed | the possibly-earlier applications' readings enter the release combinations | `test_a5_*`; `1f797bf` raises StopIteration |
| A-6 divided line passes a band rate it does not reach | BLOCKER (b)/(c) | fixed | displayed rate of a divided measurement must be one of its parts' rates or the built-up (band-1, 100%) rate, the rate of which each band takes its percentage (Sch 4 Part 3; Cl.42 "the built-up rate applied"); Y7 oracle changed to the same rule from the traces | `test_a6_*` (four rates); `1f797bf` passes 69.29; oracle rejects |
| A-7 coverage oracle false alarm on an unresolved member | NONBLOCKING | fixed | an honestly unresolved member keeps no finite value; the others then charge at most the union | `test_a7_*`; the `1f797bf` oracle raises the false alarm |
| A-8 exit checks share engine assumptions | NONBLOCKING | fixed | Y3 recounts lo and hi under Q11 A and Q11 B with G3 admissibility and report gaps; Y6 checks every footage segment against the stated intervals; Y2 checks A3 contributors from the claims | `test_a8_*` negative controls |
| A-9 depths without a date make the well's PD-210 unresolved | NONBLOCKING | not changed | over-conservative, never silently wrong (disclosed below) | — |
| B-1 unestablished release/adjustment never checked, passes at 0.95 | BLOCKER (b) | fixed | the release is bounded below by the valued lines of the earlier applications (a line's value is never negative); a payment outside the bounds is an established omission or difference; a check not established caps confidence at 0.50 unflagged / 0.80 flagged (Q9-5); Z7 checks it | `test_b1_*`; `1f797bf` passes at 0.95; Z7 rejects |
| B-2 A3 lines of unknown date or value drop out | BLOCKER (b) | fixed | as A-4 (civil) | `test_b2_c1_*`; `1f797bf` takes 117.80 as exact at 0.95 |
| B-3 flagged rows exported at Standard / not nominated, contradicting their findings and the well | BLOCKER (a) | fixed | EXPORT-E extended (Q9-7): the exported total and the reported findings are those of one admissible scenario, with one well class per well (Cl.4) and one nomination per section (Cl.23), chosen without affecting the flag; `contract_total` keeps the absent-document values (EXPORT-D) as a disclosure | `test_b3_*`; `1f797bf` exports 1,150.00 with no finding naming the difference; new Z4 `export_errors` rejects |
| B-4 a rate error under every class disappears beside an unrelated finding | BLOCKER (b) | fixed | the reported findings are those of the export scenario, never an intersection that drops a breach present under every value | `test_b4_*` (three variants); `1f797bf` reports `timing` only |
| C-1 an unvalued account line erases an established omission | BLOCKER (b)/(c) | fixed | as A-4/B-1: per-line sign of the instrument's rate change (every civil A3 row raises the rate; drilling DD-120 can fall below S2's indexed rate after July 2026, so there the sign is per line) | `test_b2_c1_*[_no_quantity]`; `1f797bf` flag 0 at 0.95; Z7 rejects |
| C-2 quantity breach replaced by `rate` / `no_admissible_document` | BLOCKER (a)/(c) | fixed | one cause per differing dimension (quantity, rate, arithmetic) unless a breach on the line explains it; `no_admissible_document` removed | `test_c2_*`; population MDS-01651, MDS-01877 back to `quantity`; `1f797bf` reports `rate` |
| B nonblocking notes, C O-1–O-3 | NONBLOCKING | O-1 addressed by B-3; the single-invoice re-billing qualification is stated in Q9-7; the rest disclosed | | |

**Population effect of the round (vs `1f797bf`).** Flags unchanged: CW 85 / 900, DDS 125 / 1,906.
- Exported totals changed on 95 flagged rows (23 CW, 72 DDS). These are the fact-dependent flagged rows previously
  exported at the absent-document values: HPHT/Extended Reach wells at Standard, and PD-210 sections as not nominated
  (PD-210 at 0). They are now exported under the well-consistent export values, and every difference from the bill is
  named by a finding.
- Categories changed on 2 rows: MDS-01651 and MDS-01877, `rate` → `quantity` (C-2).
- Confidence changed on 2 rows: PA-00707 and PA-00768, 0.80 → 0.60. Each line now takes its most favourable ground,
  so their totals differ across grounds.
- The G5 reader sample now agrees on 48 of 50 reader results. The four earlier settlements for PA-00111 and PA-00613
  were removed as stale: the corrected export reproduces the readers' totals.

**Not established.**
- The export values are a named policy. Where the missing call-off or excavation record says otherwise, a flagged
  fact-dependent row's exported total is wrong (confidence 0.60).
- Round-1 closure rests on the fixes, the tests and their controls; no independent recheck was run.
- A-9 remains over-conservative: a PD-210 charge with depths but no date leaves the well's later PD-210 charges
  unresolved rather than bounded.
- The Q11 A upper bound counts a loose charge's allowed or reported metres, not a sharper physical bound.


## Appendix A — independent auditor reports, round 1 (unedited)

Each report follows verbatim between the rules; it is also kept as a file (named below).

---

`verification/g45_audit/auditor_A_g4_round1.md`:

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

---

`verification/g45_audit/auditor_B_g5_round1.md`:

# G5 audit (commit 1f797bf): four blockers found, so G5 should not pass

The committed outputs reproduce exactly and every verifier check (Z1–Z9) passes. Even so, I found four defects that meet the blocker criteria. One of them changes results in the supplied population. Every script is under `/tmp/auditB/_audit/`. Run each one as `cd /tmp/auditB && INVOICE_SNAPSHOT=/home/user/majedzahrani3/invoice-auditing-level-2 python _audit/<script>`. The `a_*`, `t_inspect` and `p_rerun` scripts first need `_audit/cache_world.py`, which pickles the G2→G4 world.

**Environment caveat:** other auditors (`/tmp/auditA`, `/tmp/auditC`) were running on the same machine at the same time. Two of my G3/G4 re-runs were OOM-killed (exit 137) and succeeded when re-run on their own. Nothing I report depends on the killed runs.

## Reproduction
- `python -m audit.g5_run` gave CW 900 invoices / 85 flagged and DDS 1,906 / 125 flagged, with 2,806 template rows and none missing. Afterwards `git status` was clean apart from `_audit/`.
- `python tools/verify_g5.py` passed Z1–Z9 with run context `89f0c33608cd82ec` and printed "G5 VERIFY OK".
- `pytest tests/test_g5_falsification.py tests/test_g4g5_corrections.py`: 65 passed.

## Findings

### B-1 — BLOCKER (b): a release or adjustment whose account is not established is never checked, and the invoice passes at 0.95
- **Script:** `_audit/b_release_unknown.py`. It runs raw CW-H10 through the production pipeline. The only change is that the first application's line loses its work date.
- **What happens:** G4 then sets the release to `None`. The recipient PA-9A003 gets flag 0 / conf 0.95 / no findings whether its claimed release is 0.00, 192.49 or 50,000.00.
- **Control:** with the work date present, 0.00 gives `release_omitted` and 50,000 gives `release_differs`.
- **What it should be:** 45A (CW p32) releases half the retention on all earlier applications. PA-9A002's retention alone is 192.30, and line values cannot be negative, so the release is at least 96.15. A claimed 0.00 is therefore an established omission.
- **Confidence rubric:** Q9-5 allows 0.95 only when "every applicable check was made". Here the release check was not made.
- **Verifier blind spot:** Z3's `payment_errors` returns `[]` on this outcome. It only reconciles release accounts stored as a single value (a string) and skips adjustment accounts with `lines_not_established`. Z7 never compares `not_established` against 0.95.
- **Adjustment path:** `_a3_amount` makes the same move to `(None, None)`, after which any adjustment value is accepted.
- **Code:**
  - `audit/g5_outcomes.py` 83–96: `payment_check` returns `lo is None → *_not_established` for any billed value.
  - `audit/g5_outcomes.py` 583–597: `_a3_amount` and `_release_amount`.
  - `audit/g4_cw.py` ~919–925: `released = None if unknown`, and no lower bound is carried.
  - `tools/verify_g5.py` `payment_errors`.
- **Why a blocker:** the G5-B03 closure explicitly lists "unknown amounts".

### B-2 — BLOCKER (b), unclosed G4-B03 variant that G5-B03 depends on: A3 protected lines of unknown value or date silently drop out of the account
- **Scripts:** `_audit/b_a3_undated_line.py` and `_audit/b_adjustment_not_established.py`. Both use raw CW-H09 with PA-99003/PA-99004 moved to 2026-05-20, so PA-99005 is the sole recipient.
- **Three triggers, same effect:**
  - PA-99001-02 loses its work date, or
  - PA-99001 loses its application date, or
  - PA-99001-02 loses its site zone.
- **What happens:** the line loses its "31A protection" reading and is no longer eligible (eligible lines go from 2 to 1). The account becomes an exact 117.80 instead of 489.80, with `lines_not_established=0`.
- **Effect on PA-99005:** a claimed adjustment of 117.80 passes at flag 0 / 0.95, and 489.80 is flagged as an established `adjustment_differs` at 0.80.
- **What it should be:** the dropped line may be protected, so the account is not established (roughly 117.80 to 489.80) and should not be treated as exact.
- **Sources:** 31A (CW p32) and A3 (p43). The G4-B03 closure says unknown chronology must stay a possible contributor "in every … payment-history calculation. Do not silently drop it."
- **Code:** `audit/g4_cw.py:713` (the eligibility filter), `audit/g3_cw.py` 44–54 (the protection reading is only added when the rate can be built), and `_sum_options` (counts only eligible lines).

### B-3 — BLOCKER (a): flagged rows export a total at Standard / not nominated, contradicting their own findings and the well's other invoices
- **Engine fixture:** `_audit/b_export_class_inconsistent.py`. Invoice A (HPHT-billed) passes, exporting its billed 1,523.75. Invoice B on the same well is also HPHT-billed but has one unsigned-report line. B is flagged with category `signature` only, yet exports 1,150.00, which values its class line at Standard (a 325 reduction that no finding names). Under HPHT, B's total is 1,523.75; under Standard, A is wrong. No single call-off supports both outputs (Cl.4 p3).
- **Population, well level** (`_audit/a_well_class.py`, output in `a_well_class.out`): 42 flagged rows export at Standard while every other invoice of their well can only be right under HPHT or Extended Reach. Examples:
  - NGP-QA-023: 10 invoices pass as HPHT; MDS-00639 exports 584,071.68, against 645,115.04 under HPHT.
  - NGP-BD-149: 10 invoices pass as HPHT; MDS-00901 (category `signature`) exports 103,088.92, against 145,977.69 under HPHT.
- **Population, row level** (`_audit/a_flagged_class_export.py`): 44 flagged DDS rows have an export carrying rate differences their own findings do not name. In 43 of them the class with the fewest rate differences is not Standard. Examples:
  - MDS-00164: category `timing; evidence_mismatch`, billed 220,472.94, exported 129,315.95, HPHT total 218,063.86.
  - MDS-01798: category `term; evidence_mismatch`, exported 130,669.85, Extended Reach total 141,024.18.
- **Size:** summed over these 44 rows, the gap between the export and the total at each row's best-fitting class is USD 1,180,715.03.
- **Why it is a defect, not just a policy choice:** EXPORT-D (Q9-3/Q9-7) is a named policy, but it is not consistent with the source. It treats the missing call-off as establishing Standard (and not nominated) for exported totals, while Q9-3 E treats the same missing document as not establishing anything for flags and categories. The export then breaks the row's own evidence trail. README scoring judges flagged rows on "whether expected_total_cents is the figure the contract actually supports".
- **Verifier blind spot:** the oracles encode the same policy, so they cannot fail on this: Z6 via `fact_values`/`FALLBACK` and Z4 via `want = contract_total`.
- **Code:** `audit/g5_outcomes.py` 159–164, 631–634, 646–659 (`class_conflict` only considers invoices that can be right) and 712–718.
- **Counter-argument:** the author can defend EXPORT-D as disclosed. I classify it as a blocker because no class value makes a row's category and exported total true at the same time, which fails the G5-B01 requirement for a "source-consistent unresolved-output policy".

### B-4 — BLOCKER (b): a rate error present under every well class disappears from the category when any unrelated finding is common
- **Engine fixture:** `_audit/b_mixed_class_category.py`. One class line is billed at Standard and another at HPHT. With nothing else wrong, the category is `rate` (`no_admissible_document`). Add a late submission or an unsigned report on a third line and the category becomes `timing` or `signature` only. The rate error vanishes from findings and category; flag and confidence (0.60) are unchanged.
- **On an actual invoice:** `_audit/p_rerun.py`, output in `p_rerun_a.out` / `p_rerun_b.out`. It changes MDS-01798-046 (MW-310) from the Extended Reach rate to the HPHT rate 3,413.19, recomputes the header, and re-runs G3→G4→G5. Every other class line of the invoice and of well NGP-BD-104 is at Extended Reach.
  - **In-term version:** flag, category (`term; evidence_mismatch`), total 130,669.85 and confidence 0.60 are all unchanged. The overcharge is invisible.
  - **Out-of-term version:** also no rate category.
- **Cause:** the engine keeps a finding only if the same (finding, line) holds under every class, and adds `no_admissible_document` only when nothing at all is common. Separately, `scenario_breaches` returns `[]` for non-payable lines, so a deferred class-rate check is never completed on out-of-term or unsigned-report lines.
- **Code:** `audit/g5_outcomes.py` 689–694 and 253–254.
- **Why a blocker:** the G5-B06 closure says "Preserve an independently demonstrated rate error." In the supplied population I found no clear instance (`_audit/a_mixed_class_population.py` returned 3 rows, all established arithmetic findings, not this pattern).

## Nonblocking observations
- **Misleading bounds on an unformed non-working reading.** When only a non-working open reading cannot be valued, the row is labelled `bounded` with bounds `[x, x]` taken from the working reading (`_audit/t_ds900_edges.py`, last case). This misstates the uncertainty, but the exported number is the working-reading total and no supplied invoice is unformed.
- **Q9-7's "flag never depends on which admissible value the bill matches" is only tested jointly per well.** Re-billing one invoice of a well at another admissible class flips the flags of its sister invoices through `class_conflict`. That is intended under Cl.4, but the claim should be qualified.
- **Only the last retrospective instrument per contract is kept.** `a3_recipients` overwrites earlier ones. Each contract has only one retrospective instrument (A3), so there is no effect today.
- **A 0.00 DS-900 line beside the correct one passes.** Treating a zero line as "no charge" is a defensible reading of Cl.38.

## Verified correct
- **Frozen blockers:**
  - G5-B01: claim-only changes (MDS-00753 class HPHT→Standard; PA-00291 ground statements) leave flag, category, total and confidence unchanged, even after a full G3/G4/G5 re-run.
  - G5-B02: the no-substitution branch and the DS-900/VAT lower bound hold.
  - G5-B03: exact accounts and ties are reconciled correctly (CW-H10 control: 0.00 gives omitted, 50,000 gives differs, 192.49 passes).
  - G5-B05: split charges, positive sign, a zero-only line when a discount is due, and a DS-900 on another well are all caught.
  - G5-B06: tests pass; the gaps are B-4 above.
- **Independent recomputations from the scans' OCR:**
  - **MDS-00753:** matches the engine (flag 0, export 49,892.39, 0.80). Built from the Sch 1 rates, the Sch 2C index for Sep 2025 (104.90), the Sch 3 6" section factor 0.885 and the class factors. Class totals: HPHT 49,892.39, Standard 49,113.13, Extended Reach 49,532.73. LW-430 and MB-702 are each charged once per well.
  - **PA-00350:** matches the engine (flag 1, `rate`, 26,560.68, 0.95). The C.32.010 rate is 1,860 × 1.06 (Z2) × G2 (27A, work after 27 Sep 2025) × 0.95 (S2), with 31A protection against A3. The A.12.030 night uplift reproduces. I did not independently check its band position or B.25.010's USD conversion.
  - **MDS-01798:** the category is right, but the export disagrees with its own class (B-3).

## Could not check
- The page images: `verification/pages/` is absent, so I worked from the OCR text.
- The full test suite and `test_g5_gate`, under memory contention.
- The Z5 sample readers.
- G4 closure beyond the A3 and release variants above.

---

`verification/g45_audit/auditor_C_e2e_round1.md`:

# Independent audit C: G4 and G5 at 1f797bf (break-the-gate, invariants and hand recomputation)

**Verdict: G4/G5 NOT PASS.** I found two blockers:
- **C-1** is a silent false pass on unseen invoices of the same format. It is a hole in the G5-B03 / G4-B03 closure ("unknown amounts") and a regression from gate5.
- **C-2** is a regression that changes the category of two supplied invoices.

Apart from these, all four invariants held, all 6 invoices I recomputed by hand agreed with the engine, and every variant from the frozen audit that I reran is closed.

Everything was done in /tmp/auditC (clone checked out at 1f797bf) and all scripts and logs are in /tmp/auditC/_audit/. /home/user/invoice_v2 was not touched. One process note: the corrections pytest run used the default tempfile location under /tmp; those directories are deleted automatically. After that I set TMPDIR to _audit/tmp, which I have since removed. A baseline in-memory run reproduced the committed `verification/g5/outcomes.jsonl` exactly (0 differences on flag, category, expected total, contract_total, confidence, findings, formed, status, open readings and not-established).

## Findings

### C-1: BLOCKER, criteria (b) and (c). An unvalued amount anywhere in the A3 or 45A account removes an established omission and passes the recipient at 0.95 or 0.80

- **Where it happens:**
  - G4 sets the whole account to "not established" as soon as any contributing line is unvalued:
    - `audit/g4_cw.py` `_retention`: `released = None if unknown` (about line 900);
    - `_sum_options` sets `lines_not_established`.
  - G5 then drops the known lower bound:
    - `_a3_amount` returns `(None, None)` when `lines_not_established` is set (`audit/g5_outcomes.py` about line 575);
    - `payment_check` turns that into `*_not_established`, which is not a failed check.
- **Why it is wrong:** the known part of each account is large and positive, and each recipient billed 0.00, so the omission is established whatever the unknown line turns out to be. The relevant clauses are CW 31A and 45A (p32), A3 (p43), and DDS 36A (p35). The frozen G5-B03 closure requires "unknown amounts" to be handled, and G4-B03 requires unknown inputs to stay possible contributors, not to wipe the account. Gate5's presence-only check would have flagged these invoices, so this is also a regression.
- **Reproduction, A3 path (`_audit/c_a3_unknown.py`):** blank the quantity of one eligible line on the real population (PA-00003-06, and DDS MDS-01092-036). This is a same-format input that G3 correctly leaves unvalued. The known account stays positive (CW 59,883.83 / DDS ≥ 289,105.18), yet:

  | Recipients | Before | After |
  |---|---|---|
  | PA-00443, PA-00006, PA-00023, PA-00380 | flag 1 @ 0.50, `adjustment_omitted` | flag 0 @ 0.95 |
  | MDS-01625, MDS-01585, MDS-01631, MDS-01645 | flag 1 @ 0.50, `adjustment_omitted` | flag 0 @ 0.80 |

  `not_established` is empty on all eight, so the uncertainty is not even disclosed. It is hidden because the first label is the not-the-recipient scenario.
- **Reproduction, release path (`_audit/c_release_unknown.py clean` vs `clean+blank`):**
  - Remove PA-00678's own two defect lines (06 and 10) and make its header consistent. PA-00678 is then flag 1 @ 0.80 with `release_omitted`; the release due is at least SAR 3,974,311.52 and it billed 0.00.
  - Additionally blank the work date of PA-00002-02, an earlier application. PA-00678 becomes **flag 0 @ 0.95** with only `release_not_established`.
  - The unrelated-invoice invariant (`_audit/inv_unrelated.py`) shows the same effect: the added application's unvalued line strips `release_omitted` from PA-00678.
- **Supplied population:** not affected today (0 unvalued account lines), which is why this is a (b) blocker and not an (a).

### C-2: BLOCKER, criteria (a) and (c). The evidence-scenario intersection replaces a class-independent quantity breach with a made-up "rate" category

- **Mechanism:**
  - Under Extended Reach and HPHT, `scenario_breaches` (the deferred-rate completion added for G4-B04) adds `rate_differs` on the class-rated DD-120 line.
  - Once a line already has a reason, `evaluate` skips `_cause`, so `quantity_above_record` is recorded only under Standard.
  - `outcome` then takes the intersection of reasons across classes, which is empty, and falls back to `no_admissible_document`. `CATEGORY` maps that to "rate" (`audit/g5_outcomes.py`, evaluate and outcome, lines 380–395 and 690–700).
- **Supplied invoices affected:**
  - MDS-01877-046: DD-120 billed 20 h; the DDR records 20 circulating hours, so 19 chargeable after the first-hour rule (21A, p35).
  - MDS-01651-025: DD-120 billed 14 h; the DDR records 10 circulating and 8 back-reaming hours.
- **Result:** both are now category "rate" with finding `no_admissible_document`. At gate5 (13eb768) they were "quantity" with `quantity_above_record@<line>`. They changed at 75e2efd and are still wrong at HEAD, so the G5-B06 requirement ("attribute findings to the actual violated obligation") is not met, and the finding no longer names the line.
- **Same mechanism on PD-210:** in my one-invoice three-interval chain fixture (`_audit/frozen_fixtures2.py`), duplicate-charged metres are also reported as "rate", because the not-nominated scenario removes the duplicate cause.
- **Reproduction:** `_audit/c2_regression_diff.py`, and `_audit/c_category_nad.py` for the reasons under each scenario.

### Observations (NONBLOCKING)

- **O-1: the absent-document export policy (EXPORT-D) is material to exported totals.** It is an owner decision, disclosed in `spec/g5_decisions.yaml` Q9-7, and flags and confidence do not depend on it. But:
  - 45 of the 49 flagged drilling invoices with PD-210 lines export totals that leave out essentially all PD-210 footage. Example: MDS-00042 exports 156,082.74 against a nominated total of 226,535.21.
  - The 49 flagged drilling invoices that state HPHT or Extended Reach are exported at Standard.
  - G6/G7 should review this against the README's "figure the contract supports".
- **O-2: four order-sensitive civil rows changed category from rate to arithmetic** (PA-00303, PA-00459, PA-00506, PA-00611, all at 0.50). This is defensible for PA-00459: under the other order the contract amount is quantity × displayed rate. For PA-00303 the difference is really where the band edge falls, so the label is arguable.
- **O-3: the DS-900 quantity 7 × rate −1 probe passes.** The frozen audit already classed this as nonblocking.

## Verified correct

- **Invariants on the real population (all 2,806 invoices):**

  | Check | Script | Result |
  |---|---|---|
  | Rows reversed / shuffled (seed 20260930) in all four CSVs | `_audit/inv_order.py` | 0 outcome differences |
  | Unrelated invoice added (MDS-00018 cloned onto new well NGP-ZZ-999 with its DDRs; PA-00002's non-banded, non-A3 lines cloned onto new site S-06 with its records) | `_audit/inv_unrelated.py` | only PA-00678 changed, the release recipient; that change led to C-1 |
  | Billing-only changes: random amounts, random rates, header totals only, all amounts zero | `_audit/inv_billing.py` | 0 `contract_total` changes |
  | Stated well class rotated twice (all drilling invoices); stated ground rotated twice (the 649 unclassified lines) | `_audit/inv_facts.py` | 0 outcome differences |

- **Submission file** (`_audit/check_submission.py`): exact template header and order, all 2,806 ids once, integer cents, billed cents = 100 × `application_total` / `invoice_total`, rows consistent with the outcomes file, no category on unflagged rows.
- **Hand recomputation** (seed 20260930: per contract one flagged, one unflagged, one from all). My own pricers, `_audit/hand_cw.py` and `_audit/hand_dds.py`, work from the terms and records only. Section and class factors, standby percentages (DDS p20) and civil uplifts and bands (CW p24) were checked against the scans.

  | Invoice | Engine result | My recomputation |
  |---|---|---|
  | PA-00678 | flag 1, "term; evidence; adjustment", 510,294.90 | same: A.15.010 out of term, E.51.010 record missing, release omitted |
  | PA-00456 | flag 0, 127,787.11 | same (right as billed) |
  | PA-00647 | flag 0, 257,731.28 | same (right as billed) |
  | MDS-01491 | flag 1, rate, 52,290.82, 0.60 | same: DD-110 on 17 Jun priced at the 8-1/2" factor instead of 6"; wrong under every class |
  | MDS-00482 | flag 0 @ 0.80 | right only under Extended Reach |
  | MDS-01384 | flag 0 @ 0.80 | right only under Standard |

  The confidence values follow the engine's stated policy.
- **Frozen blockers:**
  - `tests/test_g4g5_corrections.py`: 56 passed.
  - G4-B01/B02 carried through G5 (`_audit/frozen_fixtures2.py`): the admissible totals are 4,371,138.04 (duplicate metres counted once) and 13,374.50 (joint allocation), and the within-invoice allocation is fixed with no open reading.
  - Population variants (`_audit/frozen_pop.py`):
    - PA-00443 adjustment 0.01: flagged.
    - PA-00047 with a 12,345.67 adjustment, or instead a 12,345.67 release: flagged.
    - PA-00678 release 0.01: `release_differs`.
    - MDS-00018 with DS-900 split into two lines: flagged "discount".
    - MDS-00753 changed from HPHT to Standard: no change.

## Not checked

- The full `tools/check_g5.sh` run (per instructions).
- Hand recomputation of PD-210 annual-band invoices.
- Interpretive choices beyond the frozen scope:
  - 45A "retention held" being computed on contract values rather than billed retention;
  - Q12 / later-submission readings.

---
