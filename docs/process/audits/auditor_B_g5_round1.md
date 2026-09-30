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
