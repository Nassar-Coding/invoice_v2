# invoice_v2 — audit specification (Phase 3, gates G0 and G1)

This branch (`opus_stage2`) holds the verified foundation for auditing the two contracts in
[majedzahrani3/invoice-auditing-level-2](https://github.com/majedzahrani3/invoice-auditing-level-2) at commit
`aef4924dc32506b4587de8b788b5a947e6beffec`. It contains **no** valuation engine, classification or `submission.csv`.

Setup: Python 3.11, `pip install -r requirements.txt`, snapshot cloned per `source/SNAPSHOT.md`.
Run every G0/G1 check: `PYTHON=python tools/check_g0_g1.sh`.

| Path | Content |
|---|---|
| `source/` | pinned snapshot: SHA-256 + git-blob manifest of all 10,330 files, scan page hashes, input inventory |
| `artifacts/phase_inputs/` | Phase 1 (1A, Agent 2 audit), governing plan and Agent 2 audits, verbatim with hashes; 1B is `Phase1_understanding_Agent1.md` |
| `spec/terms_*.yaml`, `spec/instruments.yaml` | every contractual table and instrument, cells as printed, with page/provision |
| `spec/rules.yaml`, `guideline_checks.yaml`, `sections_*.yaml` | rule index and ownership of all 12 checks and every contract section |
| `spec/overrides.yaml`, `consequences.yaml`, `open_questions.yaml`, `question_scopes.json` | overrides, consequence table, Q1–Q12 and decisions with data-derived scopes |
| `spec/corrections_agent2.yaml` | every Agent 2 correction and where it is carried |
| `verification/` | OCR, blind subagent readings, visual second-pass log, per-table verification record |
| `tools/`, `tests/` | freeze/verify tools and the test suite (incl. negative controls for the gate) |
| `prompts/phase3/` | versioned prompts used with AI subagents |

Report: `Phase3_G0_G1_Agent1b.md`. Task list: `Phase3_TASKS_Agent1b.md`.
