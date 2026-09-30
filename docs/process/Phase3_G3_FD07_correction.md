# Phase 3 G3 — FD07 closure, drilling (DDS) side

**Scope:** Phase3_G3_FD07_closure_spec_Agent2.md, DDS PD-210 allocation domain only. Civil FD07, FD01–FD06, FD08 and X8
are not touched. Baseline `gate3-r4` = 77537c5e8c64b779bf6bdb714758195b388c23fc (tree clean, main = origin/main at start).
Challenge snapshot aef4924 (DDS-2025-118: Cl.17–18 and 23 p6; R3 p14; 25A p35; Schedule 2 p17).

**Commits on main:** `68be3ed` (the FD07 DDS correction and regenerated outputs); then this report (final commit: see
the reply). No G4 work.

## 1. What changed

| Place (spec section 4) | Change |
|---|---|
| `audit/g3_dds.py` — call to `pd210_step`; `pd210_step` | Removed. No step is inferred from decimal precision; nothing restricts the domain to a grid. |
| `audit/g3_dds.py` — `pd210_domain`, `pd210_count`, `_allocation_sets` | `pd210_domain` (B2's report caps, 25A excess) kept. `pd210_coupled` added: per-band ranges projected through the sum. `pd210_count` and `ENUMERATE_MAX` removed. A nondegenerate domain is stated on the `tolerance` condition (owner G5) as below. A domain the constraints reduce to one allocation returns that allocation alone: exhaustive, no step, no allocation condition. `pd210_amount_bounds` gives exact bounds on two bands and a labelled conservative enclosure beyond. |
| `audit/g3_dds.py` — traces, `_collapse`, `_finish` | Each witness trace carries a note saying it is one sample of the continuous domain, not the selected amount. `_collapse` never drops the `tolerance` dimension. The `_finish` reading no longer says "every admissible result carried with its trace" when a continuous domain is present. |
| `tools/verify_g3.py` — `_grid_exponent`, `_ie_count`, `pd210_domain_errors` | Grid, inclusion–exclusion count and the modulo rejection removed. X3 checks 1–6 are implemented (section 3). |
| `tools/g3_case_compare.py` — `compare` | Reader alternatives are compared by domain membership. The readers' grid `allocation_count` is replaced by a source-derived domain row (`allocation_domain`), with the reader count kept in the row. Reader files and `case_dispositions.yaml` are untouched. |
| `tests/test_g3_corrections_r4.py` — FD07 DDS block | The three-point assertion is replaced. Spelling equivalence and the gate3-r3 control are kept, and the gate3-r4 negative control is added. |
| Approved additions | `tests/test_g3_corrections_r2.py` (round-2 allocation-domain tests), `tests/test_g3_corrections.py::test_f4_crossing_charge…`, and `tools/verify_g3.py` lines 122–123 and 165–168 (section 6). |
| New | `tests/test_g3_fd07_dds.py`: fixtures A–F, the witness table, billing variation, and the X3 rejections of items 5–6. |

Representation for DDS-S72, serialized by `LineResult.to_json`:
`amount=null`, `unit_rate=null`, `amount_status="conditional"`, `allowed_quantity="98"`, with the condition
`{"dimension":"tolerance","owner":"G5","domain":{…}}` holding:

- `mode="continuous"`, `step_m=null`, `count=null`, `enumerable=false`, `exhaustive=false`, `domain_complete=true`, `sum_m="98"`
- `charged_m="1450-1550"`, `report_m="1450-1550"`
- `parts=[{band, min_m, max_m, measured_capacity_m, from_m, to_m, interval_m, measured, rate, rate_source "DDS.T02_DEPTH_BANDS band n (Sch 2 p17), USD per metre"}]`
- `coupling`, and `rounding="each band part in cents, half to even, then added (Cl.17, Cl.18, Cl.23 p6)"`
- `amount_bounds_usd={"min":"4908.70","max":"4940.30","kind":"exact"}`
- `samples` (the witness labels), `samples_role`, and `remainder="every other allocation in the domain: admissible, unresolved, owner G5"`
- `state="unresolved"`, `owner="G5"`

The nomination condition (G5) stays. There is no `not_listed` key and no finite count. The witnesses are
`tolerance:witness at the lowest amount, 50 m in band 1 + 48 m in band 2` (4908.70) and
`…highest amount, 48 m in band 1 + 50 m in band 2` (4940.30).

**Exact bounds (two bands):** the amount g(x) = R(x·r1) + R((A−x)·r2) is constant between half-cent transition points.
Because |g − h| ≤ 0.01 for the unrounded h, an extreme lies within 0.02/|r1−r2| m of the linear vertex. In that window the
engine evaluates every transition point, both ends and a point inside every gap. X3 recomputes the bounds by a different
method: it enumerates band-1 cent values and takes band 2's extreme cents over each half-open preimage. A third method,
used only in the tests and the falsification runs, scans every transition over the whole domain. All three agree on every
fixture and on 150 random crossings.

## 2. Fixtures (spec section 5) — `tests/test_g3_fd07_dds.py::test_fixture`

All fixtures run production G2 parsing of the DDS-S72 packet (masks restored by `unmask`), then G3, then `to_json`.

| Test | Allowed | Domain | Bounds / value | Reader-vocabulary findings | Arithmetic |
|---|---|---|---|---|---|
| A | 98 | [48,50] / [48,50] | 4908.70–4940.30 exact | depths_differ, band_crossing | pass |
| A-spelling 98 / 98.0 / 98.00 | 98 | identical serialized domain | identical | identical | pass |
| B 98.5 / 98.50 | 98.5 | [48.5,50] / [48.5,50] | 4937.77–4961.48 exact | depths_differ, band_crossing | pass |
| C 1499–1502, 2.2 | 2.2 | [0.2,1] / [1.2,2] | 112.13–124.77 exact | depths_differ, band_crossing | pass |
| D 100 | 100 | singleton 50/50, exhaustive, one trace | 5025.00, conditional, unit_rate null, nomination only | band_crossing | pass |
| E 101 | 101 | [50,51] / [50,51] | 5067.35–5083.15 exact | depths_differ, band_crossing | pass |
| F 101.01 | 100 | singleton 50/50 | 5025.00, conditional | depths_differ, quantity_above_report, band_crossing | pass |

Every line also carries `claim_field_missing` (description). The case packet has no description field, gate3-r4 reports
the same finding on DDS-S72, and it is outside the readers' vocabulary.

**Witnesses** (`test_witness_is_admissible_and_replays`): every row of the spec table is replayed with independent Decimal
half-even arithmetic, checked for membership (sum and coupled bounds), added in memory as a correctly formed trace, and
accepted by X3 with no errors. All nine witnesses pass:

- A: 49.5/48.5 = 4916.60; 49.75/48.25 = 4912.65
- B: 49.75/48.75 = 4941.72; 49.99985/48.50015 = 4937.77; 48.5/50 = 4961.48
- C: 0.55/1.65 = 119.24; 0.333/1.867 = 122.67
- D: 50/50 = 5025.00
- E: 50.5/50.5 = 5075.26

The B vertex 50/48.5 gives 4937.78, above the exact minimum of 4937.77 (`test_b_rounded_minimum_is_not_at_the_vertex`).

**Billing variation** (`test_billing_variation_never_selects_an_allocation`): only A's rate and amount are varied, over
42.35/4916.60, 50.17/4916.60, 42.35/4908.69, 42.35/4940.31, 58.15/5698.70, 1.00/98.00 and 60.00/9999.99. The domain,
allowed quantity, status, bounds and witness set are unchanged, and X3 is clean.

## 3. X3 (spec section 4, items 1–6) — `pd210_domain_errors`

1. Constraints come from the traces' intervals and measured depths ("report measures …"), the allowed metres and the
   verified Schedule 2 table, using B2's rules and projection through the sum. Nothing is asked of the engine.
2. Each allocation is checked for its sum and its coupled bounds. There is no grid.
3. A nondegenerate domain must be `continuous` with step null, count null, not enumerable, not exhaustive, `unresolved`,
   owner G5, and no `not_listed:"none"`. It must have at least two samples and no single amount. A singleton is recognized
   from the constraints, and a singleton carried as a domain is rejected.
4. The domain's rates must match Schedule 2. Each witness's amount must equal the sum of half-even band cents. Parts are
   also checked by `pd210_part_errors` and `_check_trace`. `exact` bounds must equal X3's independent exact bounds.
   `conservative` bounds must enclose X3's bounds (two bands) or X3's enclosure (more bands). Every witness must lie
   within the bounds.
5. and 6. Shown failing directly (`test_x3_rejects_invalid_witnesses`, `test_x3_rejects_a_mutated_continuous_result`):

| Mutation of A | X3 message (contains) |
|---|---|
| valid 49.5/48.5 at 4916.60 | *no error* |
| 49.5/48.6 | `PD-210 allocation (…49.5, …48.6) does not sum to the allowed 98 m` |
| 50.1/47.9 | `… is outside the domain's bounds` |
| band 1 rate 42.36 | `PD-210 part rate 42.36 is not band 1's 42.35` |
| 49.5/48.5 at 4916.61 | `amount 4916.61, band parts in cents half to even give 4916.60` |
| claim of a complete three-allocation domain (enumerated, step 1, count 3, exhaustive, not_listed none) | `PD-210 allocation domain is continuous and unresolved … the result states {'mode': 'enumerated', 'step_m': '1', 'count': 3, …}` |
| tolerance condition removed / owner blank | `without an owned 'tolerance' condition (G5)` |
| state `resolved` | `… is continuous and unresolved …` |
| max 4940.29 | `… exclude the admissible allocation (…48, …50) at 4940.30` |
| conservative 4916.61–4940.30 with the 4916.60 witness | `… exclude the admissible allocation (…49.5, …48.5) at 4916.60` |
| exact min 4908.69 | `… are not the domain's lowest and highest rounded amounts 4908.70..4940.30` |
| single amount 4916.60 | `… given the single amount 4916.60` |

## 4. Negative control on gate3-r4 (spec section 6) — `test_fd07_control_gate3_r4_claims_a_complete_three_point_domain`

The test loads `audit/g3_dds.py` and `tools/verify_g3.py` as committed at 77537c5 and runs them on the unmodified DDS-S72
packet through the same G2 parsing.

1. The old path reaches allowed 98 with `mode enumerated, step_m "1", count 3, listed 3, not_listed "none"` and alternatives
   4908.70 / 4924.50 / 4940.30. Its own `pd210_domain_errors` is clean.
2. The new closure assertion fails with:
   `AssertionError: domain claimed finite or complete: {'mode': 'enumerated', 'allowed_m': '98', 'step_m': '1', 'count': 3, 'parts': […], 'listed': 3, 'not_listed': 'none'}`.
   The new X3 also rejects it: `PD-210 allocation domain is continuous and unresolved (owner G5; no source fixes a metre step), the result states {'mode': 'enumerated', 'step_m': '1', 'count': 3, …}, nothing unlisted`.
3. A correctly formed 49.5/48.5 witness replays to 4916.60 (`_check_trace` clean). The old `pd210_domain_errors` returns exactly:
   - `PD-210 allocation (Decimal('49.5'), Decimal('48.5')) is not admissible (sum 98, bands [(Decimal('48'), Decimal('50')), (Decimal('48'), Decimal('50'))], step 1)`
   - `PD-210 allocation domain incomplete: 4 distinct allocation(s) listed, the domain holds 3 (step 1); amounts 4908.70..4940.30`
4. The corrected verifier accepts that witness on the corrected result and rejects the wrong-total, capacity, rate,
   cents, completeness, ownership and bounds mutations.

## 5. Regression and regenerated outputs

`audit.build`, `audit.g3_run` and `tools/g3_case_compare.py` were rerun. The run context is now `32892104871ee4d3` (was
`010e7cb8794995e5`); only the `audit/g3_dds.py` hash changed.

**Full supplied population against gate3-r4** (every `to_json` field except `ctx`, old g3_cw/g3_dds executed from
77537c5): 7,746 CW and 91,244 DDS lines, **0 lines changed** in value, status, findings or any other field. No supplied
PD-210 line has a nondegenerate crossing domain. Civil is unchanged by construction: `g3_cw.py` was not modified, and 0
CW lines differ.

| Output | Change |
|---|---|
| `verification/g3/summary.json`, `trace_sample.jsonl`, `verification/g2/*` | run-context id only; trace sample: 135/135 records identical apart from `ctx` |
| `verification/g3/case_comparison.json` | 5 rows: `allocation_count` (DDS-S72..S76: reader 3/41/3/66/16, engine same) → `allocation_domain` (reader count kept; source-derived continuous domain = engine domain, agree). Totals unchanged: 192 cases, 903 comparisons, 858 agree, 45 disposed, 0 failing. The S71..S76 `alternatives` rows are unchanged: every reader value is admitted by membership, and the existing Q8 nomination dispositions still match. |

**Falsification beyond the spec's fixtures** (scratch scripts, not committed):

- 150 random crossings at 1500/3000/4500 m, with narrowed reports and quantities between 0.5× and 1.0101× plus fractions.
  Engine bounds equal the whole-domain brute force, the witnesses attain both bounds, and X3 is clean: 0 mismatches.
- Edge cases, all consistent with brute force and X3:
  - zero measured metres in band 1 with a 0.5 m excess ([0,0.5] / [50,50.5]);
  - 0.001 m;
  - 99.999 m;
  - bands 2–3 and 3–4;
  - four bands (conservative);
  - a charge wider than the report forcing one allocation.
- One defect was found and fixed before commit: a forced allocation lost its "report measures …" part label, so X3 misread
  the domain. `test_b2_the_report_bounds…` covers it.

## 6. Replaced assertions (the user approved these files; spec wins where it conflicts)

| File | Test | Old assertion | New assertion | Spec |
|---|---|---|---|---|
| tests/test_g3_corrections_r2.py | test_b2_98_m_carries_every_allocation | `_allocs(r) == {48/50, 49/49, 50/48}`; amounts == [4908.70, 4924.50, 4940.30]; `count == 3`, `mode == "enumerated"` | those three and 49.5/48.5 lie in the domain; witness amounts [4908.70, 4940.30]; exact bounds 4908.70–4940.30; `count is None`, `mode == "continuous"`, `step_m is None` | §3, §4 (g3_dds 899–976), §7 |
| 〃 | test_b2_40_m_is_never_an_empty_payable_result | `(mode, count, listed) == ("bounds", 41, 2)`; "39 allocations between the two listed extremes" in `not_listed` | `(mode, count, samples) == ("continuous", None, 2)`; `remainder` names the other allocations and G5 | §3 |
| 〃 | test_b2_control_x3_rejects_the_incomplete_domain | "domain incomplete: 2 … the domain holds 3" | "allocation domain not stated on its condition" (control still fails) | §4 X3 3, 6 |
| 〃 | test_b2_control_x3_rejects_one_missing_enumerated_allocation | "domain incomplete: 15 … holds 16" | "sampled by fewer than two allocations"; added: a stated range cut to 48.5–49.9 is rejected ("the constraints give 98.5 m in …") | §4 X3 3, 6 |
| 〃 | test_b2_control_x3_rejects_bounds_that_are_not_the_extremes_or_hide_the_domain | "are not the domain's lowest and highest amounts"; domain popped → "bounds without the whole domain stated"; `count = 2` → same | "sampled by fewer than two allocations", plus bounds narrowed to the lowest sample → "do not enclose every admissible amount"; domain popped → "allocation domain not stated on its condition"; `count = 66` → "allocation domain is continuous and unresolved" | §4 X3 4, 6 |
| 〃 | test_b2_decimal_metres_are_ascertained_in_cents_and_the_control_fails | `len(alternatives) == 16`; amounts ⊇ {4937.78, 4961.48} | `len == 2` (witnesses); amounts ⊇ {4937.77, 4961.48} | §5 B, rounding detail |
| 〃 | test_b2_falsification_crossing_charges (helper `_brute(step)` → `_span`, `_rounded_range`) | `count == len(grid)`, mode enumerated/bounds by grid size; listed == grid, or extremes over the grid | continuous, count and step None; parts == independently derived coupled ranges; witnesses are members; two bands: exact bounds == whole-domain half-cent brute force; three bands: conservative, encloses 300 random interior allocations | §4 X3 1, 2, 4; §7 |
| 〃 | test_b2_scenarios_cover_every_branch | branch component listed/bounds by grid count | exact (two bands) / conservative (more) | §3 |
| 〃 | test_b2_four_bands_checked_by_x3_independent_count | `("bounds", 56, 4)`; `count = 55` → "bounds without the whole domain stated" | `("continuous", None, 4)`; `count = 56` → "allocation domain is continuous and unresolved" | §3, §4 |
| 〃 | test_b2_the_report_bounds_where_the_metres_lie (approved in a follow-up) | `got == every` over the integer grid (≤ 25) | every allocation is within the report's coupled bounds; the domain's parts equal them, or a forced single allocation | §4 X3 1, 2 |
| 〃 | test_b2_control_a_domain_bounded_by_the_charge_is_rejected (approved in a follow-up) | "is not admissible" | "is outside the domain's bounds" (control still fails) | §4 (verify_g3 643–644) |
| tests/test_g3_corrections.py | test_f4_crossing_charge_with_a_tolerance_difference_is_exposed | labels == {"tolerance:51 m in band 1 + 50 m in band 2", "tolerance:50 m …"}; `count == 2` | the allocation part of the labels is the same pair; `count is None`, continuous, parts [(50,51), (50,51)] | §3 |
| tools/verify_g3.py 122–123 | case expectations (B2 group) | `domain:enumerated:2/3/3/16`, `domain:bounds:41/66` | `domain:continuous:<min>:<max>:<kind>`: S71 5067.35–5083.15, S72 4908.70–4940.30, S73 1694.00–2326.00, S74 10134.70–10166.30, S75 87648.49–87989.51 conservative, S76 4937.77–4961.48 (bounds checked by three methods) | §3, §5 |
| tools/verify_g3.py 165–168 | `domain` check kind | mode, `count == n`, `len(alternatives) == n or 2` | mode, step and count None, not exhaustive, bounds and kind equal, amount None, ≥ 2 witness alternatives | §3, §4 |
| tests/test_g3_corrections_r4.py | test_fd07_dds_domain_is_independent_of_spelling | `("1", 3, "enumerated")`; the three alternatives' min/max | `(None, None, "continuous")`; identical domains; bounds 4908.70–4940.30 | §4 (tests 555–597), §5 A-spelling |
| 〃 | test_fd07_dds_fractional_charge_constructed_independently | `step_m == "0.1"`; min = vertex 4937.78 | `step_m is None`; min = vertex − 0.01 = 4937.77, max 4961.48; 98.50 gives the same domain | §5 B |

`test_fd07_control_gate3_r3_depends_on_spelling` is unchanged. Every other assertion in the edited tests is unchanged.

## 7. Fresh-clone gate

`tools/check_g3.sh` on a fresh clone of `68be3ed` passed in 836 s: G0/G1 all PASS, **503 tests passed**, G2 VERIFY OK
(S5, run context 32892104871ee4d3; S2), G3 X1–X8 all PASS, G3 VERIFY OK. The final commit adds only this report and gets
the same gate on a fresh clone (the reply gives the result).

## 8. Limits

- The actual split is not established: it stays unresolved with G5. Nomination is unresolved (G5).
- Bounds over three or more bands are a labelled conservative enclosure, not exact extrema, which the spec permits.
  S75's reader values (87648.50, 87989.50) are attained by vertex witnesses; whether a fractional split reaches a cent
  lower or higher is not established.
- A rounded extreme attained only at a non-terminating rational point would have no decimal witness. The bound would still
  be exact and a domain-end sample would be listed. Random search found no such case.
- The supplied population has no nondegenerate PD-210 domain, so the change is exercised by cases, fixtures and
  falsification, not by population lines.
- The group label on `tools/verify_g3.py` line 121 ("listed, or bounds with the domain stated") and the
  `g3_case_compare.py` module docstring are outside the approved lines and are unchanged.
- The singleton descriptor is used during valuation only. The serialized singleton is its one complete part trace, with no
  allocation condition, which spec section 5 allows.
- This work has not been independently rechecked. G4 authorization is unchanged.
