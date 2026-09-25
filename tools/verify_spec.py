"""G0/G1 gate checks over the specification. Prints one line per exit condition and exits non-zero on failure.

G0: every guideline check and material contract section has an owner; independent-audit corrections recorded
    (snapshot hashes/inventory are checked by tools/snapshot.py).
G1: every active numeric cell and rule has a page/clause reference and a second verification against the scan;
    explicit overrides recorded; open interpretations have bounded alternatives and affected scopes;
    no unverified table feeds pricing.

Usage::  python tools/verify_spec.py
"""
from __future__ import annotations

import json
import re
import sys

import spec_lib as sl

EXPECTED_CORRECTIONS = (
    ["P1-A1", "P1-A2"] + [f"P1-B{i}" for i in range(1, 6)] + [f"P1-S6-{i}" for i in range(1, 9)]
    + [f"P2-B-P{i}" for i in range(1, 7)] + [f"P2-S6-{i}" for i in range(1, 9)]
    + [f"P25-B-{i}" for i in range(1, 6)] + [f"P25-S6-{i}" for i in range(1, 8)]
)
ID_LIKE = re.compile(r"^(CW|DDS)[-.]|^Q\d+$|^D\d+$|^OV-|^C-[A-Z]+$")
PAGE_REF = re.compile(r"\bp{1,2}\d|\bpp?\.?\s?\d|Sch|Cl\.|App|guideline|README|SoV|\b\d+A\b|\bP\d+|S\d|H\d|R\d|A\d|instrument")


def load_all():
    s = {k: sl.load_yaml(sl.SPEC / f"{k}.yaml") for k in
         ("rules", "overrides", "consequences", "open_questions", "guideline_checks", "sections_cw", "sections_dds",
          "corrections", "instruments", "terms_cw", "terms_dds")}
    s["scopes"] = json.loads((sl.SPEC / "question_scopes.json").read_text())
    s["log"] = sl.load_yaml(sl.VERIF / "second_pass_log.yaml")
    return s


def id_universe(s) -> dict[str, str]:
    ids = {}
    for r in s["rules"]["rules"]:
        ids[r["id"]] = "rule"
    for c in ("terms_cw", "terms_dds"):
        for tid in s[c]["tables"]:
            ids[tid] = "table"
        for p in s[c]["parameters"]:
            ids[p["id"]] = "parameter"
    for i in s["instruments"]["instruments"]:
        ids[i["id"]] = "instrument"
    for o in s["overrides"]["overrides"]:
        ids[o["id"]] = "override"
    for q in s["open_questions"]["questions"]:
        ids[q["id"]] = "question"
    for d in s["open_questions"]["decisions"]:
        ids[d["id"]] = "decision"
    for c in s["consequences"]["categories"]:
        ids[c] = "consequence"
    return ids


def check(results, name, errors):
    results.append((name, errors))


def main() -> int:
    s = load_all()
    ids = id_universe(s)
    rules = {r["id"]: r for r in s["rules"]["rules"]}
    tables = {tid: (c, t) for c, tid, t in sl.all_tables()}
    insts = {i["id"]: i for i in s["instruments"]["instruments"]}
    log = s["log"]["entries"]
    res = []

    # ---------------- G0 ----------------
    errs = []
    for key in ("sections_cw", "sections_dds"):
        doc = s[key]
        covered = set()
        for sec in doc["sections"]:
            covered |= set(sec["pages"])
            if "owners" in sec:
                if not sec["owners"]:
                    errs.append(f"{key}: empty owners for {sec['section']}")
                for o in sec["owners"]:
                    if o not in ids:
                        errs.append(f"{key}: unknown owner {o} ({sec['section']})")
            elif not sec.get("not_material"):
                errs.append(f"{key}: no owner and no not_material reason: {sec['section']}")
        missing = set(range(1, doc["page_count"] + 1)) - covered
        if missing:
            errs.append(f"{key}: pages without any section entry {sorted(missing)}")
    n_sec = len(s["sections_cw"]["sections"]) + len(s["sections_dds"]["sections"])
    check(res, f"G0 every material contract section has an owner ({n_sec} sections, CW 43 + DDS 42 pages)", errs)

    errs = []
    gc = s["guideline_checks"]["checks"]
    if [c["n"] for c in gc] != list(range(1, 13)):
        errs.append("checks are not exactly 1..12")
    for c in gc:
        for contract in ("CW", "DDS"):
            owners = c.get(contract) or []
            if not owners:
                errs.append(f"check {c['n']} has no {contract} owner")
            for o in owners:
                if o not in rules:
                    errs.append(f"check {c['n']}: unknown rule {o}")
                elif c["n"] not in rules[o]["checks"]:
                    errs.append(f"check {c['n']}: rule {o} does not list this check")
    for r in rules.values():
        contract = "CW" if r["id"].startswith("CW") else "DDS"
        for n in r["checks"]:
            if r["id"] not in gc[n - 1][contract]:
                errs.append(f"rule {r['id']} lists check {n} but guideline_checks does not")
    check(res, "G0 every guideline check (12 x 2 contracts) has an owner, consistent with rules.yaml", errs)

    errs = []
    corr = {c["id"]: c for c in s["corrections"]["corrections"]}
    for cid in EXPECTED_CORRECTIONS:
        if cid not in corr:
            errs.append(f"missing correction {cid}")
        elif not corr[cid].get("carried_in"):
            errs.append(f"{cid} has no carried_in")
        else:
            for x in corr[cid]["carried_in"]:
                if isinstance(x, str) and ID_LIKE.match(x) and x not in ids and not x.startswith("P2-"):
                    errs.append(f"{cid}: carried_in {x} does not exist")
    check(res, f"G0 audit corrections explicitly recorded ({len(EXPECTED_CORRECTIONS)} items: P1 A1-A2,B1-B5,§6; P2 B-P1-6,§6; P2.5 B-1-5,§6)", errs)

    errs = []
    qids = [q["id"] for q in s["open_questions"]["questions"]]
    for i in range(1, 12):
        if f"Q{i}" not in qids:
            errs.append(f"plan question Q{i} missing")
    check(res, f"G0 rule/ambiguity/source indexes exist (rules {len(rules)}, questions {len(qids)}, decisions {len(s['open_questions']['decisions'])})", errs)

    # ---------------- G1 ----------------
    errs = []
    n_cells = 0
    for tid, (c, t) in tables.items():
        if not t.get("source", {}).get("pages") or not t["source"].get("provision"):
            errs.append(f"{tid}: missing pages/provision")
        if t.get("use") not in sl.ALL_USES:
            errs.append(f"{tid}: bad use {t.get('use')}")
        n_cells += len(sl.numeric_cells(t))
    for c in ("terms_cw", "terms_dds"):
        for p in s[c]["parameters"]:
            if not p.get("page") or not p.get("provision"):
                errs.append(f"{p['id']}: missing page/provision")
    for iid, i in insts.items():
        if not i.get("page"):
            errs.append(f"{iid}: missing page")
    for rid, r in rules.items():
        if not r.get("sources") or not all(PAGE_REF.search(x) for x in r["sources"]):
            errs.append(f"{rid}: source without page/clause reference")
        for k in ("tables", "instruments", "overrides", "questions", "parameters"):
            for x in r.get(k, []) or []:
                if x not in ids:
                    errs.append(f"{rid}: unknown {k} ref {x}")
        if r["consequence"] not in ids:
            errs.append(f"{rid}: unknown consequence {r['consequence']}")
    check(res, f"G1 every table ({len(tables)}, {n_cells} numeric cells), parameter, instrument and rule ({len(rules)}) has a page/clause reference", errs)

    errs = []
    for tid, (c, t) in tables.items():
        e = log.get(tid)
        if not e or e.get("status") != "verified":
            errs.append(f"{tid}: no completed second verification")
        elif e["content_sha256"] != sl.canonical_hash(sl.table_content(t)):
            errs.append(f"{tid}: content changed since verification")
    for iid, i in insts.items():
        e = log.get(iid)
        if not e or e.get("status") != "verified":
            errs.append(f"{iid}: no completed second verification")
        elif e["content_sha256"] != sl.canonical_hash(sl.instrument_content(i)):
            errs.append(f"{iid}: content changed since verification")
    check(res, f"G1 second verification against the scan recorded and current for every table and instrument ({len(tables) + len(insts)})", errs)

    errs = []
    for o in s["overrides"]["overrides"]:
        for k in ("displaced", "governs", "basis", "status"):
            if not o.get(k):
                errs.append(f"{o['id']}: missing {k}")
        if o["status"] == "decision" and o.get("decision") not in ids:
            errs.append(f"{o['id']}: decision ref missing")
    check(res, f"G1 explicit overrides recorded ({len(s['overrides']['overrides'])})", errs)

    errs = []
    for q in s["open_questions"]["questions"]:
        if q["status"] == "open":
            if len(q.get("alternatives", [])) < 2:
                errs.append(f"{q['id']}: fewer than two bounded alternatives")
            if not q.get("rules") or any(r not in rules for r in q["rules"]):
                errs.append(f"{q['id']}: rules missing/unknown")
            if not q.get("blocks"):
                errs.append(f"{q['id']}: no gate named")
        for ref in q.get("scope_ref", []):
            if ref not in s["scopes"]:
                errs.append(f"{q['id']}: scope {ref} not computed")
        if not q.get("scope_ref"):
            errs.append(f"{q['id']}: no affected scope")
    for d in s["open_questions"]["decisions"]:
        if not d.get("alternative") or not d.get("reason"):
            errs.append(f"{d['id']}: alternative/reason missing")
        if not any(d["scope_key"] in s["scopes"].get(r, {}) for r in d["scope_ref"]):
            errs.append(f"{d['id']}: scope key {d['scope_key']} not computed")
    for r in rules.values():
        for q in r.get("questions", []):
            qq = next(x for x in s["open_questions"]["questions"] if x["id"] == q)
            if r["id"] not in qq["rules"] and qq["status"] == "open" and r["status"] == "open":
                errs.append(f"{r['id']} depends on {q} but {q} does not list it")
    check(res, f"G1 open interpretations have bounded alternatives and affected scopes ({len(qids)} questions, {len(s['open_questions']['decisions'])} decisions)", errs)

    errs = []
    fed = set()
    for r in rules.values():
        if r.get("pricing"):
            for t in r.get("tables", []) or []:
                fed.add(t)
            for i in r.get("instruments", []) or []:
                fed.add(i)
    for tid, (c, t) in tables.items():
        if t["use"] in sl.GATED_USES:
            fed.add(tid)
    for x in sorted(fed):
        e = log.get(x)
        content = sl.table_content(tables[x][1]) if x in tables else sl.instrument_content(insts[x])
        if not e or e.get("status") != "verified" or e["content_sha256"] != sl.canonical_hash(content):
            errs.append(f"{x} feeds pricing but is not verified at its current content")
    check(res, f"G1 no unverified table feeds pricing ({len(fed)} pricing-relevant tables/instruments checked)", errs)

    ok = True
    for name, e in res:
        print(("PASS " if not e else "FAIL ") + name)
        for x in e[:20]:
            print("     -", x)
        ok &= not e
    print("SPEC VERIFY " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
