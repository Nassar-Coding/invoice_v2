# Parameter and rule second-reading prompt (Phase 3 correction round, G1) — v1

Used for six independent subagent readers (groups A–F: CW parameters, CW rules R01–R12, CW rules R13–R24,
DDS parameters, DDS rules R01–R11, DDS rules R12–R22). Each reader gets one reading packet produced by
`tools/param_rule_verification.py packet`. Its output is recorded by `tools/param_rule_verification.py record`.
Every quote is then machine-matched to the page's OCR text, and a parameter's printed value is machine-compared
with the specification. Any verdict other than "supported" is settled against the scan image by the reviewer.

---

You are an independent second reader. You are checking statements that someone else wrote about a scanned
contract. Report exactly what the scan says. Do not assume the statements are right.

INPUT
- Packet: {PACKET} (JSON lines). Each item has id, kind (parameter|rule), contract (CW|DDS), pages (the scan
  pages the statement cites), documents (non-contract sources, if any) and statement (the full entry to verify).
- Scan page images: /home/user/invoice_v2/verification/pages/{cw|dds}/pNN.png (NN is two digits, 1654x2338
  grayscale). View them with the Read tool. Crop or zoom with Python/PIL if a passage is hard to read. The venv
  is {VENV}/bin/python and has pillow.
- OCR text of each page: /home/user/invoice_v2/verification/ocr/{cw|dds}/pNN.txt. Use it only to FIND a passage.
  It contains recognition errors. Every quote you give must be checked against the IMAGE and typed as printed.
- Non-contract documents cited as "guideline check N" or "README Task":
  /home/user/majedzahrani3/invoice-auditing-level-2/README.md and
  /home/user/majedzahrani3/invoice-auditing-level-2/{civilwork|drilling_services}/guidelines/INVOICE_AUDIT_GUIDELINES.md.

ISOLATION: do not open any other file in /home/user/invoice_v2. That means no spec/, audit/, tools/, tests/,
reports (*.md), verification/*.yaml or *.json, verification/blind/, verification/g2/, verification/phase2_verbatim/,
verification/second_pass_visual_log.txt, or other prompts. Do not open anything in /tmp except your own crops.
Your reading must not depend on anyone else's reading.

FOR EACH ITEM, in packet order:
1. Open every cited page image. Locate each cited provision (clause, schedule part, note, paragraph such as P13,
   S4, R4 or 6A). If a cited provision is not on the cited page, find the page where it actually is and say so.
2. Check every claim in the statement against the printed text:
   - parameters: value, page, provision and note;
   - rules: title, scope (where it states a contractual fact), sources, the validation cases (check any arithmetic
     against the printed numbers), and parameter_values.

   Some rules state an interpretation that the contract leaves open. Judge only whether the statement correctly
   reports what the text says and relies on. Describe any ambiguity you see; do not resolve it.
3. Quote the operative wording verbatim from the image. Give at least one quote for EVERY cited page, even if it
   only shows the page is the right one. For a document, give {"document": "<path>", "text": "..."} instead of a
   page. Keep each quote to the shortest passage that proves the point (normally one or two sentences). Put ??
   where a character is illegible.
4. Append ONE line of JSON to {OUTPUT} immediately after finishing the item. Never hold more than one item
   unwritten, because images may drop out of your context:

   {"id": "...", "reader": "{GROUP}", "verdict": "supported|partly_supported|not_supported",
    "printed_value": "<parameters only: the value exactly as printed, e.g. '15 per cent', '5 January 2025'>",
    "quotes": [{"page": 8, "text": "..."}],
    "source_labels_ok": true,
    "discrepancies": "<every claim the text does not support or states differently, and any wrong page/clause label; empty string if none>",
    "pages_read": [8]}

Verdicts:
- supported: every claim follows from the quoted text.
- partly_supported: at least one claim is missing from, or differs from, the text. List each one in discrepancies.
- not_supported: the main claim is contradicted by the text.

When all items are done, reply with at most 8 lines:
- items done;
- counts per verdict;
- the ids that are not "supported", each with one line on why;
- any page you could not read.
