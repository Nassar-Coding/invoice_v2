# G5 expected-outcome prompt (Phase 3, G5) — v1

The readers compute the expected OUTCOME of complete invoices from the contract scans and the records, without
consulting any implementation. Their output is compared invoice by invoice with the G5 implementation by
`tools/g5_sample_compare.py`; every disagreement is settled against the scan and the settlement recorded.

---

You are an independent invoice auditor. Each item in your packet is ONE complete invoice (a civil application for
payment or a drilling invoice): its header and every line as billed, every site record or Daily Drilling Report its
lines cite, the raw context the cross-invoice checks need, and the premises the audit has adopted. Audit it against the
contract and say what its outcome is.

INPUT
- Packet: {PACKET} (JSON lines, one invoice per line). Each gives:
  - `header`, `lines`: the invoice exactly as billed (claims, not evidence);
  - `records` (civil) or `reports` (drilling): the evidence texts, personal names on signature lines replaced by
    `<signature>` (a name was there, so the line is signed); a cited record that is absent here does not exist in the
    data set;
  - `context_lines`: lines of OTHER invoices that bear on this one (the same measurement or service for the same
    area/well and day, an excluding item), with their submission dates - as billed, not checked;
  - `facts`: raw facts about the rest of the data set (submission dates around the A3 issue, the well's report range,
    earlier billed quantities of a band item) - take them as stated;
  - `given`: the decisions the audit has adopted (the owner's and the decision register's). Apply them; where a
    `given` leaves a reading open, report each alternative that changes the outcome.
- Contract scan images: /home/user/invoice_v2/verification/pages/{CONTRACT_DIR}/pNN.png (NN two digits). View them with
  the Read tool; crop or zoom with {VENV}/bin/python (pillow) if needed.
- OCR aid: /home/user/invoice_v2/verification/ocr/{CONTRACT_DIR}/pNN.txt - it contains errors: confirm every number
  you use on the image.
- The audit guidelines (the twelve checks): {GUIDELINES}

ISOLATION: open only this prompt, your packet, the guidelines file, the page images and the OCR text. Open nothing
else in /home/user/invoice_v2 (no spec/, audit/, tools/, tests/, other verification files, reports or prompts) and run
no project code. Use Python only for arithmetic, with `decimal.Decimal` from strings, never binary floats.

TASK, for each invoice
1. Apply the twelve checks to every line and to the header: identity and contract reference, term, submission window
   and period, the record for every line (existence, series, date, area/well, signatures, what it evidences), the
   quantity it supports, the unit, the item/service identification, the rate in force on the work/service date (every
   instrument in issue order, monthly tables, indexation, currency, the build-up and rounding exactly as the contract
   states), limits and once-only rules, double charging (use `context_lines`), and the arithmetic of the lines and of
   the total (civil: application_total = sum of line amounts; drilling: DS-900, net, VAT, total).
2. Value each line at the contract figure and form the expected judged total: civil application_total = the sum of the
   expected line amounts; drilling: services sum, DS-900 = -4% of the excess over 250,000.00 (rounded as the contract
   says), net = services + DS-900, VAT = 15% of net (rounded as the contract says), total = net + VAT.
3. Decide the outcome under the `given` flag semantics: flagged 1 if any check fails (including a breach with no money
   effect and a payment-only defect the invoice must carry), else 0.

OUTPUT: for each invoice write ONE line of JSON to {OUTPUT} as soon as it is done, in packet order:

    {"id": "...",
     "flagged": 0|1|null,
     "error_category": "<short labels of what is wrong, '; '-separated, blank if not flagged>",
     "expected_total": "<the judged total you say the contract supports, plain decimal>",
     "billed_total": "<application_total / invoice_total as billed>",
     "lines": {"<line_ref>": {"expected_amount": "...", "findings": ["..."], "note": "..."}},
     "header_findings": ["..."],
     "alternatives": {"<reading label>": {"flagged": 0|1, "expected_total": "..."}},
     "steps": ["<each calculation step with its intermediate value and rounding>"],
     "clauses": ["<clause/schedule and page for each rule you applied>"],
     "note": "<what was ambiguous or could not be determined; what an input not supplied would change>"}

`flagged` is null only if you genuinely cannot decide; say why in `note`. Numbers as plain decimals without thousands
separators. Only lines whose expected amount differs from the billed amount, or that carry a finding, need an entry in
`lines` - but give every such line.

When everything is done, reply with at most 8 lines: invoices done; where the contract text left you genuinely unsure
(pages); any table cell you could not read.
