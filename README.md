# invoice_v2 — audit specification, evidence extraction and local pricing (Phase 3, gates G0–G3)

Branch `main` holds the verified foundation for auditing the two contracts in
[majedzahrani3/invoice-auditing-level-2](https://github.com/majedzahrani3/invoice-auditing-level-2) at commit
`aef4924dc32506b4587de8b788b5a947e6beffec`. G2 adds evidence extraction; G3 adds local entitlement and pricing of each line on its own
(no cross-invoice state, bands, caps, duplicates or run/well lifecycles; no classification, flags, totals or `submission.csv`).

Setup: Python 3.11, `pip install -r requirements.txt`, snapshot cloned per `source/SNAPSHOT.md`.
Run every G0/G1 check: `PYTHON=python tools/check_g0_g1.sh`. Run G0/G1 and G2: `PYTHON=python tools/check_g2.sh`.
Run G0–G3 (all checks, full test suite incl. the G3 negative controls): `PYTHON=python tools/check_g3.sh`.
Rebuild G2 outputs: `python -m audit.build` (writes `verification/g2/`; `--dump` also writes `build/evidence.jsonl`).
Rebuild G3 outputs: `python -m audit.g3_run` (writes `verification/g3/`; `--dump` also writes `build/g3_results.jsonl`, every line with its trace);
`python tools/g3_case_compare.py` re-compares the reference cases. Any code change changes the run context, so rebuild G2 then G3.

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
| `verification/g2/` | G2 coverage, unresolved queue, conflicts, run context; blind transcription and independent semantic review (`semantic/`) |
| `spec/carried_items.yaml` | disclosed G2 conflicts and missing records, each with owning gate, rule, question and treatment |
| `verification/param_rule_*`, `section_readings.jsonl` | G1 second reading of every parameter, rule and previously un-re-read page (correction round) |
| `audit/terms.py`, `g3_core.py`, `g3_cw.py`, `g3_dds.py`, `g3_run.py` | G3 terms access, traced pricing engines and local line checks per contract, population run |
| `spec/g3_decisions.yaml`, `spec/g3_code_families.yaml` | G3 decisions (Q3–Q13, G3-D1/D2) with basis, alternatives and cases; code-family coverage |
| `verification/g3/` | reference cases (inputs, independent readers' expected values, dispositions, comparison), summary, decision scopes, trace sample, scan spot checks |

Reports: `Phase3_G0_G1.md`, `Phase3_G2.md`, `Phase3_G1_G2_corrections.md` (supersedes the G1/G2 reports where they differ), `Phase3_G3.md`,
`Phase3_G3_corrections.md` (supersedes `Phase3_G3.md` where they differ). Task list: `Phase3_TASKS.md`.
