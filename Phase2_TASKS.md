# Phase 2 task list — alternative plan

Phase 2 is feasibility and planning only. Deliverable: `Phase2_plan_alternative.md`.
Started 2026-09-23 00:40 UTC. Snapshot `aef4924dc32506b4587de8b788b5a947e6beffec`.

## Setup and inputs
- [x] Confirm the pinned snapshot SHA and the working branch; confirm the Phase 1 page images, notes and venv survive.
- [x] Read the independent Phase 1 audit (corrections A1–A2, B1–B5 and its eight carry-forward corrections).
- [x] Read the baseline report (primary). Confirm the attached supplementary report is identical to my Phase 1 report (diff = 0).

## Source re-checks (the repository is authoritative)
- [x] CW: independent verbatim re-read of the decision-critical clauses (subagent), then my cross-check against the Phase 1 notes.
- [x] DDS: independent verbatim re-read of the decision-critical clauses (subagent), then my cross-check against the Phase 1 notes.
- [x] Adjudicate every discrepancy by viewing the page myself. Spot-check each subagent's quotes against the page images.

## Read-only data checks that ground planning decisions
- [x] Civil: lines in non-Schedule-1 units (Cl.26 scope).
- [x] Civil: Cl.44 same item/work area/date groups; compare application-date and application-number order.
- [x] Civil: DW weekly-log reuse (site, zone, week, dates). Keep evidence reuse separate from duplication.
- [x] Civil: whether DX/PT record `Ground:` agrees with the line's ground_class (S4 scope).
- [x] Civil: which cumulative basis the billed band splits follow (billed quantity vs payable quantity; Cl.30 ordering).
- [x] Civil: night-flag and rest-day distribution; the P11 and 27A interactions visible in the data.
- [x] Drilling: well spans (DDR first/last day) against once-per-well charges.
- [x] Drilling: run spans (Part B) against DD-111 and LW-420 timing.
- [x] Drilling: whether the DD-120 six-hour minimum / first-hour interaction can bind.
- [x] Drilling: Cl.29 repeat groups and the 8 report-date mismatches (mismatch vs reuse vs duplicate).
- [x] Drilling: unit field against Schedule 1 units (Cl.35).
- [x] Both: invoice-number order vs submission-date order; same-day ties at the Amendment 3 issue dates.
- [x] Both: text scans for conditions with no structured field (rig move, crew change, tool failure; flood watch, heat, safety).

## Feasibility
- [ ] OCR tooling availability — NOT tested (fallback: second visual read); listed in plan §12.
- [x] Python and dependency pinning approach.

## Plan writing (`Phase2_plan_alternative.md`)
- [x] 1. Major work, dependencies, ordering.
- [x] 2. Both contracts' materially different rules.
- [x] 3. Terms, amendments and evidence: the transcription method and verification gate.
- [x] 4. Invoice-local and cross-invoice / stateful checks.
- [x] 5. Validation without labels; propagation safeguards.
- [x] 6. Ambiguity register, unpriceable handling, confidence.
- [x] 7. Expected-total correctness for both datasets.
- [x] 8. Reproducibility and every deliverable (incl. AI disclosure, versioned prompts, one-page decision log).
- [x] 9. Failure modes and safeguards.
- [x] 10. Time use and cut order.
- [x] 11. Stage-completion evidence.
- [x] Not-confirmed list and time spent.

## Close-out
- [x] Commit and push to `claude/pensive-wright-dgj33d`.
- [x] End-of-run report: Blocked on me / Produced / Found / Not confirmed.

## Added during the phase
(new items are appended here as they are found)
- [x] Subagent re-reads stopped on a usage limit after CW pp.1–12 and DDS pp.1–8; both agreed with the Phase 1 notes. The remaining decision pages were viewed directly (see plan header and §12).
- [x] Added: 8 drilling report-date mismatches classified (6 with no DDR for the service date; 2 re-check for duplication).
- [x] Added: civil band order / Contract-Year diagnostic (98.8 % under Cl.30 order + §3A reset).
- [ ] Open for Phase 3: DDS pp.11–12, 14, 20–21, 27, 30, 36, 38–39, 41 not re-viewed this phase.
