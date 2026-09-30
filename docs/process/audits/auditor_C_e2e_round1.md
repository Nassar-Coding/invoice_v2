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
