"""G2 exit checks (artifacts/phase_inputs/Phase2_plan.md §2, G2 row). One line per exit condition.

E1 Every source row/file is accounted for.
E2 Each required field is parsed or explicitly unresolved.
E3 Reference validity and semantic validity are separate.
E4 Reviewed examples cover every record family and encountered wording/layout branch.
Also: independent blind annotation agrees with the parser, and the committed outputs reproduce.

Usage::  python tools/verify_g2.py
"""
from __future__ import annotations

import csv
import json
import sys
from collections import Counter
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

from audit import build, claims, links, records_cw, records_dds  # noqa: E402
from audit.common import SNAPSHOT  # noqa: E402

FIXTURES = ROOT / "tests" / "fixtures" / "g2_reviewed.yaml"
INVENTORY = json.loads((ROOT / "source" / "inventory.json").read_text())


# ---------------------------------------------------------------- branch definitions
def cw_record_branches(r) -> set[str]:
    b = {f"cw.family:{r.family}", f"cw.rule:{r.rule}", "cw.ground:stated" if r.ground else "cw.ground:absent",
         "cw.layout:weekly" if r.week_beginning else "cw.layout:daily"}
    if r.week_beginning:
        b.add(f"cw.days_on:{len(r.days_on)}")
        months = {(d.year, d.month) for d in r.days_on + [r.week_beginning]}
        if len(months) > 1:
            b.add("cw.week_crosses_month")
        if len({y for y, _ in months}) > 1:
            b.add("cw.week_crosses_year")
    if not r.foreman_signed:
        b.add("cw.foreman_placeholder")
    if not r.engineer_signed:
        b.add("cw.engineer_placeholder")
    return b


def ddr_branches(d, conflicts) -> set[str]:
    a, bb = d.parts.get("A", {}), d.parts.get("B", {})
    b = {f"ddr.parts:{''.join(sorted(d.parts))}", f"ddr.status:{a.get('Status')}", f"ddr.section:{a.get('Hole section')}",
         f"ddr.source_carried:{bb.get('Radioactive source carried')}"}
    b |= {f"ddr.tool:{t}" for t in d.tools_in_hole} | {f"ddr.crew:{t}" for t in d.crew_terms}
    if d.lost_tool_term:
        b.add(f"ddr.lost:{d.lost_tool_term}")
    if not d.company_signed:
        b.add("ddr.company_placeholder")
    if not d.driller_signed:
        b.add("ddr.driller_placeholder")
    b |= {f"ddr.conflict:{c}" for c in conflicts.get(d.file, ())}
    return b


def claim_branches(kind, row) -> set[str]:
    v = row.values
    if kind == "cw_headers":
        return {f"cw_header.contract_ref:{v['contract_ref']}"}
    if kind == "dds_headers":
        return {f"dds_header.contract_ref:{v['contract_ref']}"}
    if kind == "cw_lines":
        return {f"cw_line.record_ref:{'set' if v['record_ref'] else 'blank'}", f"cw_line.ground:{'set' if v['ground_class'] else 'blank'}",
                f"cw_line.night:{v['night_work']}"}
    code = v["service_code"]
    return {f"dds_line.kind:{'DS-900' if code == 'DS-900' else 'PD-210' if code == 'PD-210' else 'service'}"}


def link_branches(prefix, link) -> set[str]:
    b = {f"{prefix}.reference:{link.reference}"}
    for k in ("date_match", "work_date_is_day_on"):
        if link.semantic.get(k) is False:
            b.add(f"{prefix}.semantic:{k}=False")
    return b


# ---------------------------------------------------------------- checks
def main() -> int:
    w = build.build()
    fix = yaml.safe_load(FIXTURES.read_text())
    res = []

    # E1 -------------------------------------------------------------------------------------
    errs = []
    inv = {"cw_headers": INVENTORY["civil"]["headers"]["rows"], "cw_lines": INVENTORY["civil"]["lines"]["rows"],
           "dds_headers": INVENTORY["drilling"]["headers"]["rows"], "dds_lines": INVENTORY["drilling"]["lines"]["rows"]}
    for kind, rows in w.claims.rows.items():
        with (SNAPSHOT / claims.FILES[kind]).open(newline="") as fh:
            raw_rows = sum(1 for _ in csv.reader(fh)) - 1
        if not (len(rows) == raw_rows == inv[kind]):
            errs.append(f"{kind}: loaded {len(rows)}, file {raw_rows}, inventory {inv[kind]}")
        if any(r.source.path != claims.FILES[kind] or r.raw is None for r in rows):
            errs.append(f"{kind}: row without provenance")
        if [r.source.line for r in rows] != list(range(2, len(rows) + 2)):
            errs.append(f"{kind}: CSV line numbers not contiguous")
    for k, ok in w.claims.assertions.items():
        if not ok:
            errs.append(f"input assertion failed: {k}")
    cw_files = sorted(p.stem for p in (SNAPSHOT / "civilwork" / "records").iterdir())
    dds_files = sorted(p.name for p in (SNAPSHOT / "drilling_services" / "records").iterdir())
    if sorted(w.cw) != cw_files or len(cw_files) != INVENTORY["civil"]["records"]["files"]:
        errs.append("civil record files not all parsed")
    if sorted(w.ddr_by_file) != dds_files or len(dds_files) != INVENTORY["drilling"]["records"]["files"]:
        errs.append("drilling report files not all parsed")
    if sorted(d.file for d in w.ddr.values()) != dds_files:
        errs.append("report-number index does not hold every drilling report exactly once")
    if any(rid != d.report for rid, d in w.ddr.items()):
        errs.append("report index not keyed by internal report number")
    acc_cw, acc_dd = links.accounting(w.cw_links, w.cw), links.accounting(w.dds_links, w.ddr)
    if len(w.cw_links) != inv["cw_lines"] or len(w.dds_links) != inv["dds_lines"]:
        errs.append("not every line has a link object")
    res.append((f"E1 every source row/file accounted for: rows {sum(len(v) for v in w.claims.rows.values())} "
                f"(cw 900+7746, dds 1906+91244) with file/line provenance; records cw {len(w.cw)}/2169, dds {len(w.ddr_by_file)}/8151 "
                f"indexed by report number {len(w.ddr)}; files cited cw {acc_cw['cited']}, dds {acc_dd['cited']}, "
                f"unreferenced cw {len(acc_cw['unreferenced'])}, dds {len(acc_dd['unreferenced'])}", errs))

    # E2 -------------------------------------------------------------------------------------
    errs = []
    q = w.queue
    n_fields = 0
    for kind, rows in w.claims.rows.items():
        for r in rows:
            for k in claims.required_fields(kind, r.raw):
                n_fields += 1
                if r.values.get(k) in (None, "") and not q.has(r.ident, k):
                    errs.append(f"{kind} {r.ident}.{k} empty and not queued")
    for t, r in w.cw.items():
        need = {"family": r.family, "Area": r.area, "narrative": r.rule, "Signed (foreman)": r.foreman,
                "Countersigned (Engineer's representative)": r.engineer}
        need.update({"Week beginning": r.week_beginning, "Days on": r.days_on or None} if r.family == "DW" else {"Date": r.date})
        if r.family in ("DX", "PT"):
            need["Ground"] = r.ground
        for k, v in need.items():
            n_fields += 1
            if v is None and not (q.has(t, k) or q.has(t, "title")):
                errs.append(f"cw {t}.{k} empty and not queued")
    for f, d in w.ddr_by_file.items():
        for k in ("report", "contract", "well", "rig", "date", "company_rep", "lead_dd"):
            n_fields += 1
            if getattr(d, k) is None and not any(u.ident == f for u in q.items):
                errs.append(f"ddr {f}.{k} empty and not queued")
        for p, vals in d.parts.items():
            for k in records_dds.part_keys(p):
                n_fields += 1
                if vals.get(k) is None and not q.has(f, f"{p}.{k}"):
                    errs.append(f"ddr {f}.{p}.{k} empty and not queued")
        for t, code in list(d.tools_in_hole.items()) + list(d.tools_in_run.items()):
            if code is None and not any(u.ident == f and "Appendix G" in u.reason for u in q.items):
                errs.append(f"ddr {f}: term {t} unmapped and not queued")
    res.append((f"E2 each required field parsed or explicitly unresolved: {n_fields} required fields checked; "
                f"unresolved queue {len(q.items)}; evidence conflicts kept visible {len(q.conflicts)}", errs))

    # E3 -------------------------------------------------------------------------------------
    errs = []
    for prefix, lk, states in (("cw", w.cw_links, links.CW_REFERENCE_STATES), ("dds", w.dds_links, links.DDS_REFERENCE_STATES)):
        for ident, l in lk.items():
            if l.reference not in states:
                errs.append(f"{prefix} {ident}: unknown reference state {l.reference}")
            if l.reference in links.RESOLVED_STATES and not l.semantic:
                errs.append(f"{prefix} {ident}: resolved without semantic facts")
            if l.reference not in links.RESOLVED_STATES and l.semantic:
                errs.append(f"{prefix} {ident}: semantic facts on an unresolved reference")
            if "reference" in l.semantic:
                errs.append(f"{prefix} {ident}: reference state mixed into semantic facts")
    resolved_but_mismatched = sum(1 for l in list(w.cw_links.values()) + list(w.dds_links.values())
                                  if l.reference == "resolved" and any(v is False for v in l.semantic.values()))
    ref_counts = Counter(l.reference for l in w.cw_links.values()) + Counter(f"dds:{l.reference}" for l in w.dds_links.values())
    res.append((f"E3 reference validity separate from semantic validity: states {dict(sorted(ref_counts.items()))}; "
                f"{resolved_but_mismatched} resolved references carry at least one semantic mismatch (kept as facts)", errs))

    # E4 -------------------------------------------------------------------------------------
    errs = []
    conflicts = {}
    for c in q.conflicts:
        conflicts.setdefault(c.ident, set()).add(c.check)
    corpus, covered = set(), set()
    for r in w.cw.values():
        corpus |= cw_record_branches(r)
    for t in fix["civil_records"]:
        covered |= cw_record_branches(w.cw[t])
    for d in w.ddr_by_file.values():
        corpus |= ddr_branches(d, conflicts)
    for f in fix["drilling_reports"]:
        covered |= ddr_branches(w.ddr_by_file[f], conflicts)
    for kind, rows in w.claims.rows.items():
        by_id = {r.ident: r for r in rows}
        for r in rows:
            corpus |= claim_branches(kind, r)
        for ident in fix["claims"][kind]:
            covered |= claim_branches(kind, by_id[ident])
    for prefix, lk in (("cw_link", w.cw_links), ("dds_link", w.dds_links)):
        for l in lk.values():
            corpus |= link_branches(prefix, l)
        for ident in fix["links"][prefix.split("_")[0]]:
            covered |= link_branches(prefix, lk[ident])
    missing = sorted(corpus - covered)
    errs += [f"branch without a reviewed fixture: {m}" for m in missing]
    fams = {b for b in corpus if b.startswith("cw.family:")}
    parts = {b for b in corpus if b.startswith("ddr.parts:")}
    res.append((f"E4 reviewed fixtures cover every family and encountered wording/layout branch: {len(corpus & covered)}/{len(corpus)} "
                f"branches ({len(fams)} civil families, {sum(b.startswith('cw.rule:') for b in corpus)} narrative templates, "
                f"{len(parts)} DDR part layouts, {sum(b.startswith('ddr.tool:') for b in corpus)} tool terms); "
                f"fixtures: {len(fix['civil_records'])} civil, {len(fix['drilling_reports'])} DDR, "
                f"{sum(len(v) for v in fix['claims'].values())} claim rows, {sum(len(v) for v in fix['links'].values())} links", errs))

    # Independent blind annotation (supporting evidence for E2/E4) -----------------------------
    errs = []
    import compare_blind_g2 as cb
    cmp = {"cw": cb.compare_cw(w.cw), "dds": cb.compare_dds(w.ddr_by_file)}
    for k, v in cmp.items():
        errs += [f"{k} {x['id']} {x['field']}: blind {x['blind']!r} parser {x['parser']!r}" for x in v if not x["agree"]]
    res.append((f"S1 blind subagent annotation agrees with the parser: civil {sum(x['agree'] for x in cmp['cw'])}/{len(cmp['cw'])} fields "
                f"({len({x['id'] for x in cmp['cw']})} records), DDR {sum(x['agree'] for x in cmp['dds'])}/{len(cmp['dds'])} fields "
                f"({len({x['id'] for x in cmp['dds']})} reports)", errs))

    # Committed outputs reproduce --------------------------------------------------------------
    errs = []
    cov = json.loads(json.dumps(build.coverage(w), default=build._j))
    for name, obj in (("coverage.json", cov), ("unresolved.json", json.loads(json.dumps(q.items, default=build._j))),
                      ("conflicts.json", json.loads(json.dumps(q.conflicts, default=build._j)))):
        if json.loads((build.OUT / name).read_text()) != obj:
            errs.append(f"verification/g2/{name} does not reproduce")
    res.append(("S2 committed G2 outputs reproduce from the snapshot (coverage, unresolved, conflicts)", errs))

    ok = True
    for name, e in res:
        print(("PASS " if not e else "FAIL ") + name)
        for x in e[:25]:
            print("     -", x)
        ok &= not e
    print("G2 VERIFY " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
