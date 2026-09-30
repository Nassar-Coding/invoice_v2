# Phase 3 — G6 (population review and containment) and G7 (freeze and reproduce)

Governing definitions: `artifacts/phase_inputs/Phase2_plan.md` §2.
- **G6 exit:** "Every residual cluster is explained by a validated rule, source finding or visible unresolved
  question; all critical review cases are dispositioned; changes have replayed all dependent invoices; no unsupported
  pass or silent fallback remains."
- **G7 exit:** "A clean clone reproduces the same 2,806-row CSV and audit results; independent output checks pass; all
  five README deliverables and AI disclosure are present."

The owner's final instruction set the scope. There was no further independent-audit round and one population
regeneration. The existing 30-invoice sample was to be read once, in parallel. A single fresh-clone run was to be made
at the very end, on the final commit.

## G6

**Population review** (`tools/g6_review.py` → `verification/g6/review.json`, run context `85e9cfda3bff7980`, on the
outputs of `a7c61f1`/`35c7abf`):
- **Rule exposure.** Every G3 check, G4 state family and G5 finding that decides lines is counted by lines, invoices
  and flags.
- **Categories.** Flag counts per root category and per exact combination, for each contract.
  - CW roots: rate 35, duplicate 21, arithmetic 8, evidence 7, timing 6, adjustment 5, unit 4, quantity 2, limit 2,
    term 2, identity 2, evidence_mismatch 1, signature 1, eligibility 1.
  - DDS roots: rate 57, quantity 21, eligibility 14, timing 9, evidence_mismatch 8, duplicate 6, arithmetic 6,
    adjustment 4, discount 3, signature 3, identity 3, evidence 3, term 3.
- **Residuals.** 95 clusters, grouped by contract, code and explaining finding, of lines whose exported value differs
  from the bill. **Every cluster is explained by a finding, and every one lies on a flagged invoice**: no unflagged
  invoice carries a line valued differently from its bill.
- **Outliers.** The largest billed-to-expected differences per contract were each read against their findings. The
  largest, PA-00297 (D.41.020 billed under the superseded rate: 208,403.01 against 359,886.87), is an under-billing
  that the rate check names.
- **Unsupported passes.** Candidate unsupported passes or silent fallbacks: **0**.
  - Checked for every unflagged invoice: a check left unresolved and not completed later, a line with no single value,
    an unformed total, a state left unresolved with no scenario carrying it.
  - Negative controls in `tests/test_g6.py`.
- **Uncertainty.** Grouped by what the confidence rests on:
  - DDS: 1,781 unflagged at 0.80 (call-off not supplied); 117 flagged at 0.60 (total rests on the missing document);
    8 flagged at 0.50 (open readings).
  - CW: 301 unflagged at 0.80; 27 flagged at 0.60; 13 flagged at 0.50.

**Changes replayed.** The independent-audit fixes were replayed over the whole population in one regeneration
(`a7c61f1`); `docs/process/Phase3_G4_G5_corrections.md` §4 gives the before/after.

**Independent false-negative / false-positive sample — not completed.**
- The sample was drawn earlier (`tools/g6_samples.py`, seed 6606): 30 invoices from the whole population, stratified
  by the exported flag.
  - CW: 12 unflagged, 6 flagged. DDS: 8 unflagged, 4 flagged.
  - Flags are unchanged since the draw, so the strata still hold.
- Blind packets: `verification/g6/samples/packet_*.jsonl`. Prompt: `prompts/phase3/g6_independent_review_v1.md`.
- Six isolated readers were launched once, in parallel, one per packet. All six ended at once on the platform's
  account usage limit (weekly limit; reset 1 October 11:00 UTC), before writing any output.
- Per the owner's instruction, no second attempt was made. `tools/g6_sample_compare.py` has no reader output to
  compare, and `verification/g6/sample_dispositions.yaml` is absent.

**Latent finding recorded, not fixed (F6-1).** A civil or drilling line can have a G3 rate check deferred to G4 or
G5, with no scenario carrying a rate that completes it. Such a line would pass silently.
- Population: 0 lines.
- The G6 containment check (`unsupported_reasons`: "left unresolved and not completed later") would report such an
  invoice, and its test shows the check can fail.
- The engine does not flag it. Recorded as a known limitation.

**G6 exit — not met.** Residual clusters are explained, changes are replayed, and no unsupported pass or silent
fallback is found. But the critical review cases of the independent sample were not read, so they are not
dispositioned. The false-negative rate is therefore not measured by an independent reading.

## G7

- **`submission.csv`** at the repository root. It is the pipeline's output byte for byte
  (`tests/test_g7_submission.py`).
- **Independent checker.** `tools/check_submission.py` re-reads the template and both input invoice files. It checks
  exact columns and order, all 2,806 ids once in template order, flag 0/1, a category exactly when flagged, integer
  minor units, `billed_total_cents` = 100 × the judged field as printed, and confidence in [0, 1]. Nine negative
  controls each fail as intended: missing, reordered and duplicated rows, column order, billed cents, decimal cents,
  flag without a category, confidence above one, flag not 0/1.
- **Pinned dependencies** (`requirements.txt`). Python 3.11.
- **`reproduce.sh`** runs, in order:
  - input verification;
  - the evidence build and the G3, G4 and G5 runs;
  - the copy of the pipeline output to `submission.csv`;
  - the checker;
  - a `git diff --exit-code` over `submission.csv` and `verification/`.
- **README deliverables.**
  - Runnable repository: `README.md`, `reproduce.sh`, `requirements.txt`.
  - `submission.csv`.
  - Short report: `ERROR_ANALYSIS.md` and `.pdf`.
  - Prompts: `prompts/phase3/`, versioned.
  - Decision log: `DECISION_LOG.md` and `.pdf`, one page.
  - AI disclosure: README "AI assistance".
- **PDFs.** Rendered by `tools/md_to_pdf.py` with fixed metadata; the numbers were checked by extracting the PDF
  text.
- **Fresh clone.** One run on the final commit, reported in the final summary.

## Repository cleanup (classification before change)

| Item | Class | Reason |
|---|---|---|
| `audit/`, `tools/`, `tests/`, `spec/`, `source/`, `requirements.txt`, `.gitignore` | KEEP | run, test, verify |
| `verification/` (outputs, OCR, readings, comparisons, dispositions, samples) | KEEP | substantiate every claim; reproduction compares against it |
| `verification/g5/submission.csv` | KEEP | pipeline output; the root file is checked identical to it |
| `artifacts/phase_inputs/` | KEEP | governing plan and review documents, verbatim with hashes (checked by `tests/test_g0_snapshot.py`) |
| `prompts/` | KEEP (verbatim) | AI disclosure; versioned prompts |
| `Phase1_understanding_supplementary.md`, `Phase2_*`, `Phase3_*.md`, task lists (repository root) | MOVE → `docs/process/` | process records; references in `tests/test_g0_snapshot.py`, `tests/test_g3_corrections_r2.py` and `spec/corrections.yaml` updated |
| `verification/g45_audit/*.md` (independent audit reports) | MOVE → `docs/process/audits/` | process records; references updated |
| `README.md` | REWRITTEN | assessor-facing: setup, reproduce, verify, layout, AI disclosure |
| `submission.csv`, `reproduce.sh`, `ERROR_ANALYSIS.*`, `DECISION_LOG.*`, `tests/test_g7_submission.py` | ADDED | deliverables and their checks |
| `__pycache__/`, `.pytest_cache/`, `build/`, `verification/pages/` | REMOVE locally / never tracked | caches and regenerable renders (`.gitignore`) |

**Scan.** No secrets or credentials; the pattern hits are the word "token" in prose and code. Local absolute paths
appear only in:
- verbatim prompts (kept verbatim);
- the recorded reader packets and logs that name the pinned snapshot's location (evidence of what was read);
- the audit reports (verbatim).

No code path depends on them; code resolves the snapshot through `INVOICE_SNAPSHOT` or the relative default.
No machine-specific files are tracked.
