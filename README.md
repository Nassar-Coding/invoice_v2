# invoice_v2 — audit specification and evidence extraction (Phase 3, gates G0–G2)

Branch `main` holds the verified foundation for auditing the two contracts in
[majedzahrani3/invoice-auditing-level-2](https://github.com/majedzahrani3/invoice-auditing-level-2) at commit
`aef4924dc32506b4587de8b788b5a947e6beffec`. It contains **no** valuation engine, classification or `submission.csv`; G2 adds evidence extraction only.

Setup: Python 3.11, `pip install -r requirements.txt`, snapshot cloned per `source/SNAPSHOT.md`.
Run every G0/G1 check: `PYTHON=python tools/check_g0_g1.sh`. Run G0/G1 and G2: `PYTHON=python tools/check_g2.sh`.
Rebuild G2 outputs: `python -m audit.build` (writes `verification/g2/`; `--dump` also writes `build/evidence.jsonl`).

| Path | Content |
|---|---|
| `source/` | pinned snapshot: SHA-256 + git-blob manifest of all 10,330 files, scan page hashes, input inventory |
| `artifacts/phase_inputs/` | Phase 1 baseline report and audit, governing plan and later audits, verbatim with hashes; the supplementary Phase 1 report is `Phase1_understanding_supplementary.md` |
| `spec/terms_*.yaml`, `spec/instruments.yaml` | every contractual table and instrument, cells as printed, with page/provision |
| `spec/rules.yaml`, `guideline_checks.yaml`, `sections_*.yaml` | rule index and ownership of all 12 checks and every contract section |
| `spec/overrides.yaml`, `consequences.yaml`, `open_questions.yaml`, `question_scopes.json` | overrides, consequence table, Q1–Q12 and decisions with data-derived scopes |
| `spec/corrections.yaml` | every independent-audit correction and where it is carried |
| `verification/` | OCR, blind subagent readings, visual second-pass log, per-table verification record |
| `tools/`, `tests/` | freeze/verify tools and the test suite (incl. negative controls for the gate) |
| `prompts/phase3/` | versioned prompts used with AI subagents |
| `spec/evidence_*.yaml` | G2 evidence mapping: civil narrative templates, DDR Parts A–E keys, Appendix G/crew terms |
| `audit/` | G2 claims loader, civil and DDR parsers, run/loss events, reference + semantic links, unresolved queue |
| `verification/g2/` | G2 coverage, unresolved queue, conflicts; blind annotation sample and comparison |

Reports: `Phase3_G0_G1.md`, `Phase3_G2.md`. Task list: `Phase3_TASKS.md`.
