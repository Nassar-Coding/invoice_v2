# G2 semantic review prompt (Phase 3 correction round) — v1

(Amended before the civil review ran: the civil packet carries the title and narrative lines, because the
first civil reviewer was refused direct access to the record files on personal-data grounds. The narrative
holds no personal data.)

Used for four independent subagent reviewers: ddr (31 reports), lines_1 and lines_2 (84 invoice lines), and
civil (45 records). The population is fixed by `tools/semantic_review_g2.py sample` (seed 20260926). Every
answer is compared field by field, by name, with what the G2 parser and linker derive
(`tools/semantic_review_g2.py compare`). A missing or extra annotation fails the check. Each disagreement is
settled against the raw file and the scan.

---

You are an independent reviewer. Your job is to derive the MEANING of raw site records and invoice lines from
the contract scans. You do not only transcribe. Work only from the raw files and scan pages named below.

ISOLATION: open only these:
- this prompt;
- your packet {PACKET};
- the raw files your packet names, by their exact paths (do not list directories; the civil packet names none);
- the scan page images /home/user/invoice_v2/verification/pages/{dds|cw}/pNN.png;
- the OCR aids /home/user/invoice_v2/verification/ocr/{dds|cw}/pNN.txt. OCR contains errors; confirm on the image.

Open nothing else in /home/user/invoice_v2. That means no spec/, audit/, tools/, tests/, reports,
verification/g2/ or other prompts. Do not run the project's code.

Write ONE JSON line per packet item to {OUTPUT} immediately after finishing that item. Keep the packet order.

## TASK ddr  (drilling contract DDS; packet items: {"file", "path"})
Contract pages you need: Appendix G (dds p36) maps the rig's report words to service codes. Schedule 1
(dds pp15–16) lists the codes.

For each report, read Part A "In the hole", Part A "Crew on tour", Part B "Tools in run" and, if present,
Part E "Lost in hole tool". Output:

    {"file": "...",
     "in_the_hole":  {"<term exactly as written>": "<service code Appendix G gives for it>", ...},
     "tools_in_run": {"<term>": "<code>", ...},
     "crew": {"<service code of the crew term>": <number of persons written>, ...},
     "lost_tool": {"term": "<term>", "code": "<code>"} or null}

Where Appendix G gives one term to two codes (a rental/service code and a lost-in-hole LH code), decide from
the part the term appears in. A tool lost in the hole (Part E) is the LH item. A tool that is merely in the
hole or in the run is the non-LH item. If a term has no Appendix G code, give null and explain in "note".

## TASK lines  (drilling contract DDS; packet items: {"line_ref", "csv_header", "csv_row", "report_file"})
Contract pages you need:
- Schedule 8, Scope of Services (dds pp27–28): what each service's charge is for;
- Appendix G (dds p36): report terms;
- Schedule 3 Part 4 (dds p21) and Clause 21 (dds p6): Standby substitution;
- Schedule 5 (dds p24): which part of the Daily Drilling Report evidences which services;
- Schedule 4 (dds p23): personnel.

For each invoice line, read the CSV row. Then read the Daily Drilling Report it cites, at the report_file path.
Its "Report:" line must equal the row's report_ref. Output:

    {"line_ref": "...",
     "tool_day_service": true|false,   # Schedule 8 says this service is charged for "each day the Daily Drilling
                                       # Report records the tool in the hole"
     "tool_code": "<code>"|null,       # only if tool_day_service: the service code whose Appendix G TOOL term would
                                       # show that tool in Part A "In the hole". If the contract says this service is
                                       # charged in place of another service, give that other service's code. If
                                       # the service has no tool term at all (e.g. its Appendix G term names a
                                       # person), give null.
     "tool_in_hole": true|false|null,  # only if tool_day_service: does Part A "In the hole" list that tool term?
                                       # null when tool_code is null
     "required_part": "A".."E"|null,   # the Daily Drilling Report part that Schedule 5 names as the record for
                                       # this service code, if Schedule 5 names one
     "required_part_present": true|false|null,   # does the cited report contain that part? null if no part named
     "crew_recorded": <int>|null,      # only for a personnel service (Schedule 4): how many persons of that
                                       # service's Appendix G crew term the report's "Crew on tour" records
                                       # (0 if none); null for other services
     "lost_tool_code": "<code>"|null,  # only for an LH-7xx line: the LH code of the tool Part E says was lost
                                       # (null if the report has no Part E)
     "note": "<anything unclear, with the wording you relied on>"}

For every field that is not a tool-day, personnel or LH line, use exactly false or null as stated above.

## TASK civil  (civil contract CW; packet items: {"ticket", "title", "narrative"})
The packet carries each record's title line and its narrative line, taken verbatim from the raw file (no other
record content is needed and none is provided; do not open the record files).
Contract pages you need:
- Schedule 1 Bill of Quantities (cw pp17–19): item codes, descriptions, units;
- P13 (cw p13): trench depth bands;
- Schedule 5 (cw p27): records.

For each record, read its narrative line. Output:

    {"ticket": "...",
     "quantity": "<the measured quantity, digits as written>",
     "unit": "m3|m2|lm|no.|hour|week|tonne",   # the physical unit of that quantity, normalised
                                              # ('cube' = m3; 'm' of pipe or run = lm; 't' = tonne;
                                              # a count of things = no.)
     "attributes": {<name>: "<value>", ...},    # EVERY other fact the narrative states, labelled with exactly
                                                # one of these names:
         depth_m   - a single stated trench depth in metres (digits; not a range or a bound written in words)
         dia_mm    - a stated diameter in millimetres (digits)
         type      - a stated material Type number (e.g. 'Type 1' -> "1")
         mix       - a concrete mix/strength as 'NN/NN' (drop any leading 'C')
         mesh      - a mesh reference as written (e.g. "A393")
         reason    - for standing/idle time: weather | rain | waiting on access | not stated
       Use {} if there are none. If the narrative states a number that fits none of these names, add it
       under "other:<short description>".
     "candidate_items": ["<Schedule 1 code>", ...],   # the Schedule 1 item(s) whose description this recorded work
                                                     # matches. Use P13's bands where a depth decides the item.
                                                     # List every code that fits if the record cannot tell them apart.
     "note": "<anything unclear>"}

When all items are done, reply with at most 8 lines:
- items done;
- any item you could not complete;
- any term or code you found ambiguous, with the scan wording.
