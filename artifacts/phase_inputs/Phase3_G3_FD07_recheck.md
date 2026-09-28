# FD07 DDS focused recheck — gate3-r5

**FD07 (drilling): CLOSED. G3: PASS.**

**G3 is independently closed. G4 is authorized.**

The correction satisfies the DDS closure specification. The changed assertions replace the unsupported grid/count rules with the specification's domain, rounding and uncertainty rules; they were not merely weakened to obtain a pass. No blocking regression caused by this correction was found within the bounded recheck.

## 1. Audited state and scope

| Item | Independently verified state |
|---|---|
| Current main and audited commit | [1a14df132c833c1e2b5760b7a8cd737d801d0e11](https://github.com/Nassar-Coding/invoice_v2/commit/1a14df132c833c1e2b5760b7a8cd737d801d0e11) |
| Main tree | `737bc564e0bee5a0e142cb169634c546ce0d7555` |
| gate3-r5 | Annotated tag object `4b8808a76597cd88465f6354180c108fd2f634bb`, resolving to the audited commit |
| Substantive correction commit | `68be3eda7b26628d5d39e397023eebc718709add`; the final commit adds the correction report |
| Negative-control baseline | gate3-r4 / `77537c5e8c64b779bf6bdb714758195b388c23fc` |
| Challenge snapshot used | `aef4924dc32506b4587de8b788b5a947e6beffec`; existing checkout clean |
| Reproduced run context | `32892104871ee4d3` |

The standard was **Phase3_G3_FD07_closure_spec_Agent2.md**, including sections 5–7. I read its current supplied copy and the committed [correction report](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/Phase3_G3_FD07_correction.md), inspected the [complete correction diff](https://github.com/Nassar-Coding/invoice_v2/compare/77537c5e8c64b779bf6bdb714758195b388c23fc...1a14df132c833c1e2b5760b7a8cd737d801d0e11), and executed the relevant production and verification code read-only in memory. No implementation repository file, commit, tag or branch was changed. No G4 work was performed.

The retrieved closure specification contains sections 1–7 rather than literal A–I deliverable headings. The A–I index below maps its closure package to the evidence checked; it adds no requirements.

## 2. Closure package A–I

| Index | Requirement checked | Judgment and reproduced evidence |
|---|---|---|
| A | Source-consistent allocation domain | **PASS.** The inferred `pd210_step`/finite-count machinery is removed. The domain retains the previously accepted report capacities, allowed quantity and coupled sum constraints. It no longer excludes fractions by decimal spelling. |
| B | Honest representation and ownership | **PASS.** Nondegenerate cases serialize as continuous, step/count null, enumerable/exhaustive false, unresolved with G5 ownership. Samples are identified as samples. Nomination remains separately owned by G5. |
| C | Bounds, cents and singleton handling | **PASS.** Exact two-band bounds reproduce the specification, including the non-vertex rounded minimum in fixture B. Larger domains use a labeled conservative enclosure. Forced allocations remain single complete traces. |
| D | X3 detects the specified failure classes | **PASS.** Valid fractional witnesses pass. Wrong totals, capacity breaches, changed rates, wrong cents, false finite completeness, missing ownership, resolved state, excluded outcomes and an unjustified single amount are rejected. |
| E | Section 5 fixtures and spelling equivalence | **PASS.** All A–F fixtures, 98/98.0/98.00 and 98.5/98.50 pass through production G2 parsing, G3 and JSON serialization. Required findings and nomination are retained. |
| F | Witness membership and billing independence | **PASS.** All nine specified witnesses replay and pass X3. The seven committed rate/amount perturbations leave the domain, quantity, status and witnesses unchanged. |
| G | Section 6 gate3-r4 negative control | **PASS.** The old implementation runs successfully, then fails for the intended three-point/off-grid defect. Its added fractional witness has a valid trace; the failure is not an API or harness error. |
| H | Replacement assertions and reader evidence | **PASS.** Each listed replacement follows the specification, as detailed in section 5 below. Original reader files and dispositions are unchanged; obsolete grid counts remain visible as superseded evidence. |
| I | Section 7 constraints, provenance and regression | **PASS.** Confirmed 98 m endpoints unchanged; no actual allocation selected; no line dropped; civil unchanged; generated outputs reproduce. All 98,990 supplied line results are unchanged apart from run context. |

Implementation evidence: [domain and amount bounds](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/audit/g3_dds.py#L903-L1082), [trace/collapse/finish](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/audit/g3_dds.py#L606-L757), [X3 domain verification](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tools/verify_g3.py#L582-L748), [fixed fixtures and mutations](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tests/test_g3_fd07_dds.py).

## 3. Fixed results and independent arithmetic

| Fixture | Allowed metres | Allocation / amount output | Result |
|---|---:|---|---|
| A, including 98 / 98.0 / 98.00 | 98 | Continuous q1 ∈ [48,50], q2=98−q1; **USD 4,908.70–4,940.30** | PASS |
| B, including 98.5 / 98.50 | 98.5 | Continuous q1 ∈ [48.5,50]; **USD 4,937.77–4,961.48** | PASS |
| C, report and charge 1499–1502 | 2.2 | Continuous q1 ∈ [0.2,1], q2 ∈ [1.2,2]; **USD 112.13–124.77** | PASS |
| D | 100 | Forced 50/50 allocation; **USD 5,025.00** | PASS |
| E, exact 1% upper tolerance | 101 | Continuous q1 ∈ [50,51]; **USD 5,067.35–5,083.15** | PASS |
| F, charged 101.01 | 100 | Forced 50/50 allocation; **USD 5,025.00** | PASS |

Every non-singleton has `amount=null`, `unit_rate=null`, conditional status, and both allocation/G5 and nomination/G5 conditions. D and F retain conditional status because nomination is still unknown, but do not retain an unresolved allocation condition. The specification's required local findings remain, and claim arithmetic passes.

The case adapter also retains its pre-existing `claim_field_missing` finding because it omits the description when forming the engine input. The same occurs in the old baseline; it does not arise from this correction or replace a required finding.

| Fixture | Allocation witness | Reproduced USD amount |
|---|---|---:|
| A | 49.5 / 48.5 | 4,916.60 |
| A | 49.75 / 48.25 | 4,912.65 |
| B | 49.75 / 48.75 | 4,941.72 |
| B | 49.99985 / 48.50015 | 4,937.77 |
| B | 48.5 / 50 | 4,961.48 |
| C | 0.55 / 1.65 | 119.24 |
| C | 0.333 / 1.867 | 122.67 |
| D | 50 / 50 | 5,025.00 |
| E | 50.5 / 50.5 | 5,075.26 |

I independently recalculated the A/B/C/E bounds using rational arithmetic over the **whole** allocation interval: endpoints, every half-cent transition, and interior points between transitions. This reproduced all four exact ranges without using the engine's sampling window or X3's algorithm.

The engine's bounded search is also justified: two rounded parts differ from their unrounded sum by at most one cent, so an extremum can be found within the stated two-cent unrounded-cost window of the linear extreme. For more bands, widening the linear bounds by half a cent per part and taking the integer-cent enclosure is sound. Those wider bounds are explicitly conservative, as the closure specification permits.

Section 7's coincident-price constraint was also exercised: a 0.00001 m partial allocation whose sampled prices both round to zero retains a **continuous unresolved domain**, `amount=null` and both G5 conditions. It is not collapsed to a selected zero amount or dropped.

These results establish domain completeness and correct uncertainty representation. They do not establish the actual factual split or resolve nomination, neither of which this recheck requires.

## 4. Negative control and safeguards

The unmodified gate3-r4 engine reached the expected DDS-S72 output: 98 allowed metres, step 1, three alternatives at 4,908.70 / 4,924.50 / 4,940.30, and `not_listed="none"`. Its own domain checker initially returned no errors.

The new closure assertion then failed specifically on that finite-completeness claim. After adding the valid 49.5/48.5 witness, its trace replay returned no errors, while the old domain checker returned:

```text
PD-210 allocation (Decimal('49.5'), Decimal('48.5')) is not admissible
(sum 98, bands [(Decimal('48'), Decimal('50')), (Decimal('48'), Decimal('50'))], step 1)

PD-210 allocation domain incomplete: 4 distinct allocation(s) listed,
the domain holds 3 (step 1); amounts 4908.70..4940.30
```

The corrected X3 accepts the same valid witness on the corrected domain. It rejects every specified corruption of total, capacities, rate, cents, completeness, ownership and bounds. The committed control is at [test_g3_corrections_r4.py, lines 605–658](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tests/test_g3_corrections_r4.py#L605-L658).

The case comparator was challenged separately. Changing the engine's domain upper limit from 50 to 49.9 makes the source-domain comparison disagree. Changing a reader's alternative amount by one cent also makes the alternatives comparison disagree. Thus the replacement is not unconditional acceptance of whatever the corrected engine produces. See [comparison rules](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tools/g3_case_compare.py#L155-L243).

## 5. Every listed assertion replacement

I compared the actual diff with section 6 of **Phase3_G3_FD07_correction.md** and executed the affected assertions. Each row below is **confirmed as a rule replacement, not a loosening**.

| File / test or check | Why the replacement satisfies the fixed specification |
|---|---|
| `test_g3_corrections_r2.py` — `test_b2_98_m_carries_every_allocation` | Replaces the three-point set/count with continuous-domain membership, including 49.5/48.5; still fixes the exact 4,908.70–4,940.30 bounds and G5 ownership. |
| Same — `test_b2_40_m_is_never_an_empty_payable_result` | Removes the fictitious count 41, while requiring the full [0,40] domain, nonempty witness output, correct endpoints and unresolved remainder. |
| Same — `test_b2_control_x3_rejects_the_incomplete_domain` | The deliberately incomplete old engine still executes and fails because its complete domain is absent. The failure is no longer tied to the obsolete count of three. |
| Same — `test_b2_control_x3_rejects_one_missing_enumerated_allocation` | Requires two distinct samples and separately corrupts the domain range. X3 rejects the lost range, preserving the substantive completeness check. |
| Same — `test_b2_control_x3_rejects_bounds_that_are_not_the_extremes_or_hide_the_domain` | Tests duplicated witnesses, an enclosure narrowed to the low sample, a missing domain and a false finite count. All targeted corruptions fail. |
| Same — `test_b2_decimal_metres_are_ascertained_in_cents_and_the_control_fails` | Replaces 16 samples with two witnesses and the specified 4,937.77 minimum; retains the unrounded-cent negative control. |
| Same — `test_b2_falsification_crossing_charges` and helpers | Replaces the engine-derived grid oracle with independently derived coupled ranges and a whole-interval rounding oracle for two bands. Multi-band cases require a conservative enclosure and interior membership checks. |
| Same — `test_b2_scenarios_cover_every_branch` | Coverage now distinguishes exact two-band and conservative multi-band behavior, retaining reductions, excesses, whole and fractional quantities. The removed list/count branches no longer exist. |
| Same — `test_b2_four_bands_checked_by_x3_independent_count` | Requires a continuous four-band domain; deliberately restoring the old finite count 56 is rejected. |
| Same — `test_b2_the_report_bounds_where_the_metres_lie` | Requires independently projected report-based bounds and witness membership; an absent domain is allowed only when those constraints force a singleton. |
| Same — `test_b2_control_a_domain_bounded_by_the_charge_is_rejected` | The unsupported charge-based allocation remains rejected for violating report bounds; only the diagnostic wording changes. |
| `test_g3_corrections.py` — F4 crossing/tolerance test | Retains both endpoint witnesses for 101 m, but represents every split over [50,51] continuously instead of claiming only two possibilities. |
| `verify_g3.py` — B2 case expectations | S71–S76 now assert the specified continuous domains and exact/conservative bounds. All six expectations pass; S75's conservative enclosure is permitted by the spec. |
| Same — `domain` check kind | Requires continuous mode, null step/count, non-exhaustiveness, correct bounds/kind, no selected amount and witness output. X3 separately enforces the remaining domain/ownership constraints. |
| `test_g3_corrections_r4.py` — spelling test | Requires identical full domains for 98/98.0/98.00 and the fixed endpoints, replacing the unsupported identical 1 m grid. |
| Same — fractional-charge test | Requires no step, identical 98.5/98.50 domains and the spec's exact 4,937.77–4,961.48 range. The one-cent change is explicitly grounded in fixture B, not relaxed tolerance. |

Code evidence: [round-2 replacements](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tests/test_g3_corrections_r2.py#L213-L493), [F4 replacement](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tests/test_g3_corrections.py#L203-L215), [gate expectations](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tools/verify_g3.py#L121-L171), [round-4 replacements](https://github.com/Nassar-Coding/invoice_v2/blob/1a14df132c833c1e2b5760b7a8cd737d801d0e11/tests/test_g3_corrections_r4.py#L570-L599).

## 6. Regression, reproducibility and limits

Independently reproduced:

- **33** fixed-spec test instances, **43** affected/related DDS test instances, and **6** closed civil-FD07 regression instances passed. Assertions were executed directly from fetched source in a write-prohibited process; this is not a claim of running the full pytest command.
- Production population comparison: **7,746 CW + 91,244 DDS = 98,990 lines**, with **zero changed result fields after excluding context identity**. CW code is unchanged; its outputs were also rerun and compared. No supplied PD-210 line has a nondegenerate allocation domain, so the fixed cases and adversarial checks remain essential evidence.
- The generated G3 summary and all **135** trace-sample records reproduce. G2 coverage, conflicts and run context reproduce after normal JSON normalization.
- The context change is explained by **only `audit/g3_dds.py`** changing among the context's implementation hashes. Reviewed G1/evidence inputs are unchanged.
- The case-comparison file reproduces byte-for-byte: **192 cases, 903 comparisons, 858 agreements, 45 retained dispositions, zero failures**. Only five comparison rows change: the S72–S76 grid-count rows become source-domain rows, retaining their original reader counts.
- The diff contains no civil engine change, no G2 parser/claims/evidence change, no altered original reader files or dispositions, and no G4 implementation.

**G0–G2 remain valid within their already audited scope.** The correction changes the local G3 DDS allocation mechanism and its verification; shared generated artifacts are consistent with the new provenance context. No qualifying regression was established.

The reported full **503-test fresh-clone run** and the implementation's additional 150 random probes were not independently repeated as those exact commands. Closure rests on the reproduced fixed requirements, direct corruption controls, independent arithmetic, committed-output reproduction and bounded population comparison above. These execution limits do not leave a closure-spec requirement unverified.

The actual allocation and nomination remain correctly assigned to G5. A conservative multi-band enclosure remains an enclosure, not a selected amount or proof that every cent inside it is attained. These are the intended later-gate responsibilities, not remaining FD07 defects.

**Final disposition: FD07 CLOSED. G3 PASS. No remaining blocker under the frozen set.**

**G3 is independently closed. G4 is authorized.**

Approximate active recheck time: **20 minutes**, excluding the interruption. Work stopped after this verification.
