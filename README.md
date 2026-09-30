# Invoice audit — civil works CW-2025-0417-CIV and drilling services DDS-2025-118

This repository audits every invoice under the two contracts of
[majedzahrani3/invoice-auditing-level-2](https://github.com/majedzahrani3/invoice-auditing-level-2) at commit
`aef4924dc32506b4587de8b788b5a947e6beffec`, and produces `submission.csv`: one row for each of the 2,806 invoices.
Each row gives whether the invoice is wrong, what is wrong, the total the contract supports, and a confidence.

Result: 210 of 2,806 invoices flagged (7.5%) — 85 of 900 civil applications, 125 of 1,906 drilling invoices.

| Deliverable | File |
|---|---|
| Submission (template format, all 2,806 rows) | [`submission.csv`](submission.csv) |
| Short report and error analysis | [`ERROR_ANALYSIS.md`](ERROR_ANALYSIS.md) / [`.pdf`](ERROR_ANALYSIS.pdf) |
| One-page decision log | [`DECISION_LOG.md`](DECISION_LOG.md) / [`.pdf`](DECISION_LOG.pdf) |
| Prompts, versioned | [`prompts/phase3/`](prompts/phase3/) |
| Runnable repository | this README, [`reproduce.sh`](reproduce.sh), [`requirements.txt`](requirements.txt) |

## Setup

- Python 3.11. Install the pinned dependencies: `pip install -r requirements.txt`.
- The challenge inputs at the pinned commit, next to this repository (or anywhere, with `INVOICE_SNAPSHOT` set to
  the path):

  ```
  git clone https://github.com/majedzahrani3/invoice-auditing-level-2 ../majedzahrani3/invoice-auditing-level-2
  git -C ../majedzahrani3/invoice-auditing-level-2 checkout aef4924dc32506b4587de8b788b5a947e6beffec
  ```

## Reproduce

```
./reproduce.sh
```

The script does the following, in order:
- verifies the inputs file by file against the pinned commit (`tools/snapshot.py verify`);
- rebuilds the evidence, prices and checks every line, applies the cross-invoice state and forms one outcome per
  invoice;
- writes `submission.csv`;
- checks it independently against the template and the input invoices (`tools/check_submission.py`);
- confirms with `git diff` that the regenerated files are byte-identical to the committed ones.

It takes about 20 minutes. Everything is deterministic: no network access, no randomness outside fixed seeds.

## Verify

```
PYTHON=python tools/check_g5.sh
```

This runs every check in the chain:
- the input and specification checks;
- the evidence checks;
- the line-level, cross-invoice and outcome exit checks (`tools/verify_g3.py`, `verify_g4.py`, `verify_g5.py`);
- the comparisons with the independent readings;
- the full test suite (`python -m pytest`).

Each exit check has a negative-control test showing that it can fail. The suite also runs each defect found by
independent review through the corrected code and, as a control, through the code that had the defect.

## How it works

| Stage | Code | What it does |
|---|---|---|
| Contract terms | `spec/terms_*.yaml`, `spec/instruments.yaml`, `audit/terms.py` | every rate table, schedule and amendment transcribed from the scans, with page and provision; each cell checked by an independent second reading |
| Evidence | `audit/build.py`, `claims.py`, `records_cw.py`, `records_dds.py`, `links.py` | invoices, civil site records and daily drilling reports parsed and linked; anything unreadable or conflicting is queued, never guessed |
| Line pricing and checks | `audit/g3_cw.py`, `g3_dds.py` | each line on its own: identity, term, window, record, quantity, unit, rate in force (build-up and rounding as the contract states), arithmetic; a traced calculation per line |
| Cross-invoice state | `audit/g4_cw.py`, `g4_dds.py` | quantity bands and annual footage, daily limits, duplicates and once-only charges, the retrospective A3 difference and its recipient, retention and its release |
| Outcomes | `audit/g5_outcomes.py`, `g5_run.py` | one outcome per invoice: flag, categories, expected total (civil: sum of lines; drilling: services, DS-900 discount, VAT) and confidence |

Every reading of the contract that decides an outcome is recorded with its source and alternatives in
`spec/g3_decisions.yaml`, `spec/g4_state.yaml` and `spec/g5_decisions.yaml`; open questions are in
`spec/open_questions.yaml`. Where a contract question stays open, every admissible reading is evaluated: an invoice
wrong under some readings and right under others is flagged at confidence 0.50. Where a fact belongs to a document that
is not supplied (a drilling well's class and a section's nomination, both set by the call-off; a civil line's ground
class where no excavation record classifies it), the invoice's own statement is never taken as that fact. The rule for
these cases is in [`DECISION_LOG.md`](DECISION_LOG.md).

## Repository layout

| Path | Content |
|---|---|
| `audit/` | the pipeline (evidence, line pricing, cross-invoice state, outcomes) |
| `spec/` | contract terms and instruments as printed, rule index, decisions with sources and alternatives, open questions |
| `source/` | identity of the pinned inputs: SHA-256 and git blob of all 10,330 files, scan page hashes, input inventory |
| `verification/` | committed outputs of every stage (`g2/` … `g6/`), OCR of the scans, independent readings and their comparisons |
| `tools/` | verifiers, comparison and export tools, the submission checker, the PDF renderer |
| `tests/` | the test suite, including the negative controls |
| `prompts/phase3/` | every prompt used for AI-assisted independent readings, versioned |
| `artifacts/phase_inputs/` | the governing plan and review documents the work was held to, verbatim with hashes |
| `docs/process/` | process records: stage reports, task lists, review reports (not needed to run or verify) |

## AI assistance

This work was produced with an AI coding assistant, which wrote the code, specifications and reports under the
direction and decisions of the repository owner. Two interpretation questions were decided by the owner: Q7 C (which of
two charges of one drilling service stands) and Q6 D (a civil measurement-day question left open with both readings
reported). Separate AI model instances, given only the prompts in `prompts/phase3/` and the materials each names,
produced the independent readings used as checks:
- second readings of every contract table and rule;
- blind transcriptions and annotations of records;
- expected results for reference cases, histories and invoices;
- independent reviews of the implementation.

Their outputs are kept under `verification/` and `docs/process/audits/`. Every disagreement with the implementation is
settled against the contract scan and recorded.

## Known limitations

See [`ERROR_ANALYSIS.md`](ERROR_ANALYSIS.md): the failure types, how each was measured, and what remains uncertain.
