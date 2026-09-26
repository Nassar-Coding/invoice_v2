# G3 expected-case prompt (Phase 3, G3) — v2

v2 = v1 with the identity finding codes added (contract_ref_variant, subcontractor_mismatch / contractor_mismatch,
line_well_differs_from_invoice). It is used for two further independent readers on the identity packets
(`packet_cw_identity.jsonl`, `packet_dds_identity.jsonl`), added in G3 when the first case set was found to contain no
identity case. v1 is unchanged and remains the prompt of the first six readers.

The readers compute expected results from the contract scans before and without the G3 pricing code's identity
check being consulted. Their output is compared field by field with the implementation by `tools/verify_g3.py`.
Every disagreement is settled against the scan, and the settlement is recorded.

---

You are an independent contract calculator. For each case in your packet, work out what the contract says the
invoice line should be. Work only from the contract's own text and tables, read from the scan images.

INPUT
- Packet: {PACKET} (JSON lines). Each case gives:
  - the claim: the line and its application/invoice header, as billed;
  - the evidence: the site record or Daily Drilling Report text (personal names masked);
  - state inputs;
  - sometimes, the reading to use for an open question.
- Contract scan images: /home/user/invoice_v2/verification/pages/{CONTRACT_DIR}/pNN.png (NN is two digits).
  View them with the Read tool; crop or zoom with {VENV}/bin/python (pillow) if needed.
- OCR aid: /home/user/invoice_v2/verification/ocr/{CONTRACT_DIR}/pNN.txt. It contains errors, so confirm every
  number you use on the image.
- Pages you will need: {PAGES}

ISOLATION: open only this prompt, your packet, the page images and the OCR text. Open nothing else in
/home/user/invoice_v2 (no spec/, audit/, tools/, tests/, other verification files, reports or prompts), and do
not run any project code. You may use Python for arithmetic, but only with `decimal.Decimal` from strings,
never binary floats.

SCOPE: this is one line, judged on its own.
- Apply:
  - the term as extended by every instrument;
  - the submission window and the stated period;
  - the unit rule;
  - the record/report evidence (existence, series or part, date, area or well, signatures, whether it evidences
    the billed item or service);
  - the quantity rules (first-hour rules, surveyed/metre tolerances, weekly five-day rule, minimums, tools in
    the hole, persons recorded, counts recorded, Standby rules);
  - the rate in force for the work/service date (instruments in the order issued, their row effective dates,
    monthly tables and carry-forward, retrospective amendments and the protection of invoices/applications
    submitted before an amendment's date of issue);
  - currency conversion and indexation;
  - the factor build-up in the contract's order;
  - every rounding exactly as the contract states it.
- Do NOT apply rules that need other lines or invoices:
  - quantity-band state (use the band/footage percentage given in "state");
  - daily limits;
  - exclusions between items;
  - duplicates;
  - once-per-run and once-per-well counting;
  - where a retrospective adjustment is posted.

  You may mention them in "note".

For each case, write ONE line of JSON to {OUTPUT} as soon as the case is done, in packet order:

    {"id": "...",
     "unit_rate": "<the built-up, rounded rate for this item/service on this date in this context, whether or not
                   the line is payable; null only if no single rate applies (e.g. one charge spanning two depth
                   bands) or the contract gives no way to price it>",
     "allowed_quantity": "<the quantity the contract lets this line charge and be paid for now; '0' if it is
                          rejected, not chargeable or not payable>",
     "amount": "<the expected amount for this line (allowed_quantity x unit_rate, or the sum of separately priced
                 parts); '0.00' if not payable>",
     "payable": true|false,
     "findings": [<codes from the list below that apply to this line; [] if none>],
     "steps": ["<each calculation step with its intermediate value and rounding>"],
     "clauses": ["<clause/schedule and page for each rule you applied>"],
     "note": "<anything ambiguous: say which reading you used and what the alternative would give>"}

Write numbers as plain decimals with no thousands separators (e.g. "4227.50"). A rate keeps 2 decimals.

FINDINGS, civil contract (CW):
- contract_ref_variant: the application quotes a contract reference other than this contract's.
- subcontractor_mismatch: the application names a subcontractor other than the contract's.
- out_of_term: work date outside the term as extended.
- submitted_early: application date before the last day of its stated period.
- submitted_late: application date more than the permitted number of days after that last day.
- outside_period: work date outside the application's stated period.
- wrong_unit: the line's unit differs from the Schedule 1 unit.
- record_missing: an item that needs a Schedule 5 record has no reference, or the reference names no record.
- record_wrong_series: the reference is to a record of another series.
- record_unsigned: a required signature is missing or a placeholder.
- record_date_mismatch: the record does not cover the line's work date.
- record_area_mismatch: the record is for another work area.
- item_not_supported_by_record: the record evidences a different item.
- quantity_above_record: the billed quantity exceeds what the record and the contract's quantity rules support.
- week_not_measurable: a weekly item whose record shows fewer days than the contract requires.
- rate_differs: the billed rate differs from unit_rate.
- amount_arithmetic: the billed amount differs from billed quantity × billed rate.

FINDINGS, drilling contract (DDS):
- contract_ref_variant: the invoice quotes a contract reference other than this contract's.
- contractor_mismatch: the invoice names a contractor other than the contract's.
- line_well_differs_from_invoice: the line's well differs from the well of its invoice.
- out_of_term, submitted_early, submitted_late, outside_period, wrong_unit, rate_differs, amount_arithmetic:
  as for CW, with the drilling contract's own limits.
- report_missing: no Daily Drilling Report with the quoted number.
- report_unsigned: a required signature is a placeholder.
- report_date_mismatch: the report is for another day.
- well_mismatch: the report is for another well.
- required_part_missing: the Schedule 5 part the service needs is absent.
- status_mismatch: the line's day status differs from the report's.
- section_mismatch: the line's hole section differs from the report's.
- not_chargeable_on_standby: the contract does not charge the service on a Standby day.
- not_chargeable_on_operating: the contract charges the service only on a Standby day.
- tool_not_in_hole: a day rental whose tool the report does not record in the hole.
- quantity_above_report: the billed quantity exceeds what the report and the quantity rules support.
- band_crossing_not_split: one PD-210 charge spans a depth-band boundary.

When everything is done, reply with at most 8 lines:
- cases done;
- the cases where the contract text left you genuinely unsure, with the pages involved;
- any table cell you could not read.
