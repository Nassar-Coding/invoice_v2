# G4 expected-history prompt (Phase 3, G4) — v1

The readers compute the expected results of small multi-invoice histories from the contract scans, without
consulting any implementation. Their output is compared history by history with the G4 implementation by
`tools/verify_g4.py`. Every disagreement is settled against the scan, and the settlement is recorded.

---

You are an independent contract calculator. Each item in your packet is a small HISTORY: several applications for
payment (civil contract) or invoices (drilling contract), their lines, and the site records or Daily Drilling
Reports those lines cite. Work out what the contract says each line should be once the WHOLE history is taken into
account, and what the contract says must be posted once for the history as a whole. Work only from the contract's own
text and tables, read from the scan images.

INPUT
- Packet: {PACKET} (JSON lines, one history per line). Each history gives:
  - `documents`: each application/invoice header and its lines, exactly as billed (claims, not evidence);
  - `records` (civil) or `reports` (drilling): the evidence texts the lines cite, personal names on signature lines
    replaced by `<signature>` (a name was there, so the line is signed);
  - `given`: premises stated for that history (for example, the reading of a question that has been decided, or a
    fact about the evidence that is not reproduced). Take them as stated.
  A record or report that is not in the history was not supplied to you: do not assume it exists or what it says. A
  line of the history is the only measurement or charge of its kind unless another line of the SAME history says
  otherwise; there are no other applications or invoices.
- Contract scan images: /home/user/invoice_v2/verification/pages/{CONTRACT_DIR}/pNN.png (NN two digits). View them with
  the Read tool; crop or zoom with {VENV}/bin/python (pillow) if needed.
- OCR aid: /home/user/invoice_v2/verification/ocr/{CONTRACT_DIR}/pNN.txt. It contains errors: confirm every number you
  use on the image.
- Pages you will need: {PAGES}

ISOLATION: open only this prompt, your packet, the page images and the OCR text. Open nothing else in
/home/user/invoice_v2 (no spec/, audit/, tools/, tests/, other verification files, reports or prompts), and do not run
any project code. You may use Python for arithmetic, but only with `decimal.Decimal` from strings, never binary
floats.

SCOPE
1. Each line on its own, as the contract values any line: the term as extended, the evidence (existence, series or
   part, date, work area or well, signatures, whether it evidences the billed item or service), the unit rule, the
   quantity rules, the rate in force on the work/service date (instruments in the order issued, row effective dates,
   monthly tables, retrospective amendments and the protection of documents submitted before an amendment's issue),
   currency conversion and indexation, the factor build-up in the contract's order, every rounding exactly as the
   contract states it.
2. Then EVERYTHING that depends on other lines, other documents or the order of events, across the whole history:
   - annual quantity bands (civil) and annual footage bands (drilling): what is counted, from when, in what order, when
     the count restarts, and how a quantity crossing a band edge is divided and priced;
   - daily limits;
   - items or services that exclude one another;
   - measurements or charges that repeat another (same item/service, place and day; the contract's own test);
   - charges made once per run, once per well, or once per loss, and the day they belong to;
   - a retrospective amendment: which work or services it re-prices, the difference on each line, the total, and the
     ONE document it is posted on;
   - retention on each application and its release (civil);
   - the consequence of a missing record for later valuations (civil).
   Apply the contract as written. Where it gives no rule for something the result depends on (for example which of
   two equal charges is the one not payable, or the order of two measurements of the same day), do not choose one:
   give every admissible result in `alternatives` and say why in `note`. Where the contract text itself can be read
   two ways and the result depends on it, give both readings as alternatives and say which clauses point each way.
3. Do NOT invent facts the history does not give (a well class, a nomination, an instruction, a certificate): where a
   pricing input depends on a document that is not supplied, apply any rule the contract gives for that situation; if
   none, give the value under each admissible input in `alternatives`.

OUTPUT: for each history write ONE line of JSON to {OUTPUT} as soon as it is done, in packet order:

    {"id": "...",
     "lines": {"<line_ref>": {"payable": true|false|null,
                              "allowed_quantity": "<quantity payable now; '0' if not payable; null if it depends on an alternative>",
                              "amount": "<expected amount for the line; '0.00' if not payable; null if it depends on an alternative>",
                              "parts": [{"quantity": "...", "rate": "...", "amount": "...", "basis": "<band/segment>"}],
                              "findings": [<codes below that are established for this line>],
                              "alternatives": {"<label>": {"allowed_quantity": "...", "amount": "..."}} or {},
                              "note": "..."}},
     "adjustments": [{"instrument": "<e.g. A3>", "by_line": {"<line_ref>": "<difference>"}, "difference": "<total>",
                      "recipient": "<document number, or null if the contract does not settle it>",
                      "recipient_alternatives": {"<label>": "<document number or 'none'>"}, "note": "..."}],
     "retention": {"<application_no>": {"retention": "...", "released": "..."}},
     "events": ["<anything else the contract posts once for the history, with the document it goes on>"],
     "steps": ["<each calculation step with its intermediate value and rounding>"],
     "clauses": ["<clause/schedule and page for each rule you applied>"],
     "note": "<what was ambiguous; which reading you used and what the alternative gives>"}

`parts` is needed only where a line is priced in more than one part (for example a quantity divided at a band edge);
otherwise give []. `adjustments`, `retention` and `events` may be empty. Write numbers as plain decimals without
thousands separators ("4227.50"). A rate keeps 2 decimals.

Alternative labels: "reading:<a few words>" for a reading of text the contract does not settle; "order:<a few words>"
for an order or allocation the contract does not settle; "class:<class>", "ground:<class>" for an input not supplied.
Join several with "|". When you give alternatives, set allowed_quantity/amount to the single value only if every
alternative has the same one, else null.

FINDINGS (use only codes that are established for the line; describe anything else in `note`):
- civil, local: contract_ref_variant, out_of_term, submitted_early, submitted_late, outside_period, wrong_unit,
  record_missing, record_wrong_series, record_unsigned, record_date_mismatch, record_area_mismatch,
  item_not_supported_by_record, quantity_above_record, week_not_measurable, rate_differs, amount_arithmetic;
- civil, across the history: band_divided (the line's quantity is divided at an annual band edge), above_daily_limit
  (part of the quantity exceeds the daily limitation), excluded_by_other_item (the item is not measurable because of
  another item's measurement), duplicate_measurement (the contract disallows this measurement because the same
  measurement appears earlier);
- drilling, local: contract_ref_variant, out_of_term, submitted_early, submitted_late, outside_period, wrong_unit,
  report_missing, report_unsigned, report_date_mismatch, well_mismatch, required_part_missing, status_mismatch,
  section_mismatch, not_chargeable_on_standby, not_chargeable_on_operating, tool_not_in_hole, quantity_above_report,
  band_crossing_not_split, depths_differ_from_quantity, rate_differs, amount_arithmetic;
- drilling, across the history: charged_twice (the service is charged again for the same well and day),
  above_daily_limit (the day's quantity exceeds the daily limit), run_event_repeated, well_event_not_on_its_day,
  well_event_repeated, lwd_not_run, loss_repeated, footage_band_divided.

When everything is done, reply with at most 8 lines:
- histories done;
- the histories where the contract text left you genuinely unsure, with the pages involved;
- any table cell you could not read.
