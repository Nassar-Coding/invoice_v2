"""Every number in the error analysis and the decision log, recomputed from the repository's outputs and looked for in
both the Markdown and the text extracted from the PDF (so the PDF says what the outputs say).

Usage::  python tools/check_report_numbers.py        (exit 0 when every figure is found in both)
"""
from __future__ import annotations

import json
import subprocess
import sys
from collections import Counter
from pathlib import Path

import pymupdf

ROOT = Path(__file__).resolve().parents[1]
BEFORE = "1f797bf"          # the outputs the export-rule correction is measured against


def n(x: int) -> str:
    return f"{x:,}"


def outcomes(text: str) -> dict:
    return {json.loads(x)["invoice_id"]: json.loads(x) for x in text.splitlines() if x.strip()}


def figures() -> dict:
    out = outcomes((ROOT / "verification" / "g5" / "outcomes.jsonl").read_text())
    by = {c: [o for o in out.values() if o["contract"] == c] for c in ("CW", "DDS")}
    conf = {c: Counter((o["flagged"], o["confidence"]) for o in by[c]) for c in by}
    fl = {c: sum(o["flagged"] for o in by[c]) for c in by}
    tot = len(out)
    f = {}
    for c in by:
        f[f"{c} invoices"] = n(len(by[c]))
        f[f"{c} flagged"] = f"{fl[c]} ({100 * fl[c] / len(by[c]):.1f}%)"
        f[f"{c} flagged confidences"] = " / ".join(str(conf[c][(1, x)]) for x in ("0.95", "0.80", "0.60", "0.50"))
        f[f"{c} unflagged confidences"] = " / ".join(n(conf[c][(0, x)]) for x in ("0.95", "0.80"))
    f["total flagged"] = f"{fl['CW'] + fl['DDS']} of {n(tot)} invoices ({100 * (fl['CW'] + fl['DDS']) / tot:.1f}%)"
    rv = json.loads((ROOT / "verification" / "g6" / "review.json").read_text())
    for c, top in (("CW", 5), ("DDS", 5)):
        roots = sorted(rv["categories"][c]["root"].items(), key=lambda kv: -kv[1])[:top]
        f[f"{c} top categories"] = ", ".join(f"{k} {v}" for k, v in roots)
    g3 = json.loads((ROOT / "verification" / "g3" / "case_comparison.json").read_text())
    f["line cases"] = f"{g3['comparisons']} comparisons, {g3['agree']} agree; all {g3['comparisons'] - g3['agree']} differences"
    hc = json.loads((ROOT / "verification" / "g4" / "history_comparison.json").read_text())
    f["histories"] = f"{hc['summary']['reader_results']} readings of {hc['summary']['histories']} histories, " \
                     f"{hc['summary']['agree_in_full']} agree in full; all {hc['summary']['disagreements']} line-level"
    sc = json.loads((ROOT / "verification" / "g5" / "sample_comparison.json").read_text())
    agree = sum(1 for e in sc.values() for r, d in e["readers"].items() if not d)
    res = sum(len(e["readers"]) for e in sc.values())
    f["invoice sample"] = f"{res} readings of {len(sc)} invoices, {agree} agree"
    f["drilling fact"] = f"{n(sum(1 for o in by['DDS'] if o['fact_dependent']))} invoices depend on the class, " \
                         f"{sum(1 for o in by['DDS'] if o['nomination_dependent'])} also on a nomination"
    f["civil ground"] = f"{sum(1 for o in by['CW'] if o['fact_dependent'])} invoices depend on an unrecorded ground"
    f["flagged fact 0.60"] = f"CW {conf['CW'][(1, '0.60')]}, DDS {conf['DDS'][(1, '0.60')]}"
    m = out["MDS-00753"]
    f["MDS-00753"] = [f"{float(x):,.2f}" for x in m["admissible_totals"]]
    mixed = {c: [o for o in by[c] if o["wrong_under"] and o["right_under"]] for c in by}
    f["open CW rows"] = f"Civil ({len(mixed['CW'])} rows)"
    f["open DDS rows"] = f"Drilling ({len(mixed['DDS'])} rows)"
    q1 = {c: sum(1 for o in mixed[c] if any("Q1" in lab for lab in o["wrong_under"] + o["right_under"])) for c in by}
    f["A3 recipient rows"] = [f"CW {q1['CW']}, DDS {q1['DDS']}"]
    before = outcomes(subprocess.run(["git", "show", f"{BEFORE}:verification/g5/outcomes.jsonl"], cwd=ROOT,
                                     capture_output=True, text=True, check=True).stdout)
    moved = Counter(o["contract"] for i, o in out.items() if str(o["expected_total"]) != str(before[i]["expected_total"]))
    f["exports moved"] = f"{moved['CW'] + moved['DDS']} flagged totals (CW {moved['CW']}, DDS {moved['DDS']})"
    cats = sum(1 for i, o in out.items() if o["error_category"] != before[i]["error_category"])
    f["categories moved"] = f"moved {cats} drilling rows"
    x = out["MDS-00042"]
    f["MDS-00042"] = [f"{float(x['billed_total']):,.2f}", f"{float(x['expected_total']):,.2f}", f"{float(x['contract_total']):,.2f}"]
    de = json.loads((ROOT / "verification" / "g5" / "decision_effects.json").read_text())
    f["Q9 B"] = f"CW {de['Q9']['B_only_changed_total']['flags']['CW']} / DDS {de['Q9']['B_only_changed_total']['flags']['DDS']}"
    f["Q12 B"] = [f"reprice {de['Q12']['invoices_changed']['CW'] if isinstance(de['Q12'].get('invoices_changed'), dict) else de['Q12']['B']['invoices_changed']}",
                  f"flag {de['Q12']['B']['flags']['CW']} civil"]
    f["Q7C"] = f"{de['Q7C']['invoices']['DDS']} pairs"
    f["ground lines"] = f"{de['Q8-ground']['lines']} civil lines on {de['Q8-ground']['invoices']['CW']} applications"
    f["order rows"] = f"CW {len(de['order']['only Cl.30 wording (application number, then line)']['changed'])}"
    return f


def main() -> int:
    f = figures()
    docs = {"ERROR_ANALYSIS": ["CW invoices", "DDS invoices", "CW flagged", "DDS flagged", "CW flagged confidences",
                               "DDS flagged confidences", "CW unflagged confidences", "DDS unflagged confidences",
                               "total flagged", "CW top categories", "DDS top categories", "line cases", "histories",
                               "invoice sample", "drilling fact", "civil ground", "flagged fact 0.60", "MDS-00753",
                               "open CW rows", "open DDS rows", "exports moved", "categories moved", "MDS-00042"],
            "DECISION_LOG": ["Q9 B", "Q12 B", "Q7C", "ground lines", "A3 recipient rows", "order rows"]}
    errs = []
    for doc, keys in docs.items():
        md = " ".join((ROOT / f"{doc}.md").read_text().split())
        pdf = " ".join("".join(p.get_text() for p in pymupdf.open(str(ROOT / f"{doc}.pdf"))).split())
        for k in keys:
            for want in (f[k] if isinstance(f[k], list) else [f[k]]):
                for name, text in (("md", md), ("pdf", pdf)):
                    if want not in text:
                        errs.append(f"{doc}.{name}: '{want}' ({k}) not found")
    for e in errs:
        print("FAIL", e)
    print("REPORT NUMBERS OK" if not errs else f"REPORT NUMBERS: {len(errs)} not found")
    return 0 if not errs else 1


if __name__ == "__main__":
    sys.exit(main())
