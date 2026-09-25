# Blind record-annotation prompt (Phase 3, G2) — v1

Used for two subagents (civil records; daily drilling reports). Each reads only the raw text files of a
seeded sample (verification/g2/blind/sample.json, seed 20260925, stratified by record family / DDR part
combination) and writes what each file says. It does not see the parser, the evidence specification or the
invoices, so its reading is independent. tools/compare_blind_g2.py compares it field by field with the
parser; every disagreement is settled against the raw file.

## Common rules
- Read each file with the Read tool from /home/user/majedzahrani3/invoice-auditing-level-2/<dir>/<file>.
- BLIND RULE: do not open anything under /home/user/invoice_v2 except your output file; do not open other
  records or the CSVs. Do not run parsers or regexes over the corpus: read each file yourself.
- Copy strings exactly as written. Dates as YYYY-MM-DD. Numbers as written (strings).
- Append one JSON object per file (one line) to the output file immediately after reading that file.
- Finish with a 5-line summary of anything unusual.

## Civil schema
{"ticket", "title" (first line), "job", "area" (full value), "date" or null, "week_beginning" or null,
 "days_on" (list of YYYY-MM-DD with the correct year; [] if none), "ground" (full value or null),
 "narrative" (the free-text line), "quantity" (number in the narrative that measures the work),
 "unit_words" (the unit word(s) attached to it as written, e.g. "m3", "cube", "square metres", "m", "t"),
 "other_numbers" ({label: value} for any other number in the narrative, e.g. depth, diameter, mix),
 "foreman", "engineer", "foreman_is_real_signature", "engineer_is_real_signature" (false if only underscores)}

## Drilling schema
{"file", "report", "contract", "well", "rig", "date", "parts" (e.g. ["A","B","D"]),
 "A": {every key: value exactly as written}, "B": {...}, "C": {...}|null, "D": {...}|null, "E": {...}|null,
 "company_rep", "lead_dd", "company_is_real_signature", "lead_is_real_signature"}
