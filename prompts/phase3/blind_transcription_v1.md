# Blind second-reader transcription prompt (Phase 3, G1) — v1

Used for one subagent per contract (CONTRACT = CW or DDS). The subagent sees only the scan images; it is
not given the first-pass transcription, so its reading is independent. Its output is compared cell by cell
with `spec/terms_*.yaml` by `tools/compare_readings.py`; every disagreement is re-read against the scan.

---

You are an independent second reader verifying a scanned contract. Transcribe what the scan shows.

INPUT: page images at /home/user/invoice_v2/verification/pages/{cw|dds}/pNN.png (NN two digits). View them
with the Read tool. They are 1654x2338 grayscale scans. If a cell is hard to read, crop/zoom it with
Python/PIL (the venv at {VENV} has pillow) and view the crop.

BLIND RULE: do not open any other file in /home/user/invoice_v2 (no spec/, no *.md reports, no tools/),
nor anything in /tmp. Do not use prior knowledge of what the numbers "should" be. Transcribe exactly.

PAGES: {PAGE LIST}

OUTPUT: append to {OUTPUT FILE} after EVERY page (images may be dropped from your context after ~20 views, so
never hold more than one page in memory). Format, one block per page:

    === PAGE NN ===
    TITLE: <heading text exactly>
    TABLE <n>: <table heading>
    COLUMNS: <col1> | <col2> | ...
    ROW: <cell> | <cell> | ...
    NOTE: <any footnote / note text under the table, verbatim>
    TEXT: <verbatim operative sentence(s) for clauses on the page containing numbers, dates, percentages or lists of codes>

Rules: copy every code, unit, number, percentage and date exactly as printed (keep thousands separators and
decimals as shown). Keep row order. Put ?? for any character you cannot read and say why in a NOTE. Do not
compute, correct or reconcile anything. For list-style text (e.g. "applies to the following items: ..."), copy
the full list. When done, add a final line `=== DONE ===` and reply with a 5-line summary: pages done, any ??
cells, anything that looked internally inconsistent on the page.
