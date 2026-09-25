# Section second-reading prompt (Phase 3 correction round, G0/G1) — v1

Used for one independent subagent reader. The pages are those not re-read in Phase 3: CW pp.2, 4–5, 35, 37
and DDS pp.2, 9–10, 12–14, 26, 31–33. Each section on them is classified in spec/sections_*.yaml either as
"not material" (with a stated reason) or as owned by named rules. The reader checks that classification
against the scan. Results are in verification/section_readings.jsonl, and
tools/verify_spec.py requires every section to be read.

---

You are an independent second reader. You are checking whether sections of a scanned contract can affect what an
invoice line may charge: its quantity, rate, amount, eligibility or required evidence.

INPUT: {PACKET}. It is JSON lines of {contract, section, pages, classification}. The page images are at
/home/user/invoice_v2/verification/pages/{cw|dds}/pNN.png (NN is two digits). The OCR aid is
/home/user/invoice_v2/verification/ocr/{cw|dds}/pNN.txt; it contains errors, so confirm everything on the image.

ISOLATION: open only this prompt, the packet, the page images and the OCR text. Open nothing else in
/home/user/invoice_v2.

FOR EACH SECTION, read its page images IN FULL. List EVERY numbered provision in the section (for example T1–T16,
H1–H12, R1–R12, P14, Cl.20–24). For each one give:
- a verbatim quote of its operative sentence;
- valuation_effect: true or false. It is true if the provision can change whether, how much or at what rate a
  service or item is charged, or what record is needed to charge it;
- a short reason.

Then judge the stated classification:
- "not material" is supported only if no provision has a valuation effect, or every provision that has one
  merely restates a rule found elsewhere in the contract. Name that clause if you can.
- "owned by X" is supported if the provisions with a valuation effect are the kind of rule the owner names
  suggest. You cannot see the owners' texts, so describe what an owner must cover.

Append ONE JSON line per section to {OUTPUT} as soon as that section is done:

    {"contract": "...", "section": "...", "pages": [...],
     "provisions": [{"label": "T5", "quote": "...", "valuation_effect": true, "reason": "..."}],
     "classification_supported": true|false,
     "discrepancies": "<provisions with a valuation effect the classification does not account for; empty if none>"}

When done, reply with at most 8 lines. Include the sections whose classification you do not support, and why.
