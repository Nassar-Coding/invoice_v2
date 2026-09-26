"""Compare the G3 engines with the independent expected values for every reference case.

Inputs: verification/g3/cases/packet_*.jsonl (inputs, written before the pricing code) and expected_*.jsonl (the
independent readers' results from the contract scans, prompts/phase3/g3_expected_cases_v1.md). The engine is run on
exactly the packet inputs (record/report text parsed by the G2 parser). Compared per case:
payable, allowed_quantity, amount, the findings in the readers' vocabulary (as sets), and unit_rate where both sides
give one on a payable line. Where the engine carries open-question alternatives, the reader's value must equal one
of them. A disagreement passes only with a recorded disposition (verification/g3/case_dispositions.yaml) that names
both values and the clause that settles it.

Usage::  python tools/g3_case_compare.py [--check]   (prints the summary; writes verification/g3/case_comparison.json,
                                                     or with --check only compares with it)
"""
from __future__ import annotations

import datetime as dt
import json
import sys
from decimal import Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit import g3_cw, g3_dds, records_cw, records_dds  # noqa: E402
from audit.common import Queue  # noqa: E402

DIR = ROOT / "verification" / "g3" / "cases"
OUT = ROOT / "verification" / "g3" / "case_comparison.json"
DISPOSITIONS = ROOT / "verification" / "g3" / "case_dispositions.yaml"
VOCAB_V1 = {
    "CW": {"out_of_term", "submitted_early", "submitted_late", "outside_period", "wrong_unit", "record_missing",
           "record_wrong_series", "record_unsigned", "record_date_mismatch", "record_area_mismatch",
           "item_not_supported_by_record", "quantity_above_record", "week_not_measurable", "rate_differs", "amount_arithmetic"},
    "DDS": {"out_of_term", "submitted_early", "submitted_late", "outside_period", "wrong_unit", "rate_differs",
            "amount_arithmetic", "report_missing", "report_unsigned", "report_date_mismatch", "well_mismatch",
            "required_part_missing", "status_mismatch", "section_mismatch", "not_chargeable_on_standby",
            "not_chargeable_on_operating", "tool_not_in_hole", "quantity_above_report", "band_crossing_not_split"},
}
VOCAB_V2 = {"CW": VOCAB_V1["CW"] | {"contract_ref_variant", "subcontractor_mismatch"},
            "DDS": VOCAB_V1["DDS"] | {"contract_ref_variant", "contractor_mismatch", "line_well_differs_from_invoice"}}
VOCAB_V3 = {"CW": VOCAB_V2["CW"] | {"ground_differs_from_record"}, "DDS": VOCAB_V2["DDS"] | {"depths_differ_from_quantity"}}
VOCAB = VOCAB_V3                     # the union; each expected file is compared in its own prompt's vocabulary


def vocab_for(expected_file: str, contract: str) -> set:
    if "_correction" in expected_file or "_reread" in expected_file:
        return VOCAB_V3[contract]
    if "_identity" in expected_file:
        return VOCAB_V2[contract]
    return VOCAB_V1[contract]


FACTUAL = ("class", "ground", "band")    # alternatives over facts the case does not give; others are readings


def _d(x):
    return None if x in (None, "") else Decimal(str(x).replace(",", ""))


def _date(s):
    s = str(s)
    return dt.date.fromisoformat(s) if s[:4].isdigit() else dt.datetime.strptime(s, "%d-%b-%Y").date()


def load_cases() -> dict[str, dict]:
    out = {}
    for f in sorted(DIR.glob("packet_*.jsonl")):
        for ln in f.read_text().splitlines():
            if ln.strip():
                c = json.loads(ln)
                out[c["id"]] = c
    return out


def load_expected() -> dict[str, dict]:
    """Every reader's result; a v3 re-reading (expected_*_reread.jsonl) replaces the earlier result for its case, which
    is kept under `_superseded` (the earlier files are never edited)."""
    out = {}
    files = sorted(DIR.glob("expected_*.jsonl"), key=lambda f: ("_reread" in f.name, f.name))
    for f in files:
        for ln in f.read_text().splitlines():
            if ln.strip():
                e = json.loads(ln)
                e["_file"] = f.name
                if e["id"] in out:
                    e["_superseded"] = {"file": out[e["id"]]["_file"], "amount": out[e["id"]].get("amount"),
                                        "payable": out[e["id"]].get("payable")}
                out[e["id"]] = e
    return out


def engine_result(case: dict):
    if case["contract"] == "CW":
        a, l = case["application"], case["line"]
        app = {"contract_ref": a["contract_ref"], "subcontractor": a["subcontractor"], "period_from": _date(a["period_from"]),
               "period_to": _date(a["period_to"]), "application_date": _date(a["application_date"])}
        line = {"line_ref": l["line_ref"], "item_code": l["item_code"], "unit": l["unit"], "quantity": _d(l["quantity"]),
                "rate_applied": _d(l["rate_applied"]), "amount": _d(l["amount"]), "work_date": _date(l["work_date"]),
                "site": l["site"], "site_zone": l["site_zone"], "ground_class": l.get("ground_class") or None,
                "night_work": l["night_work"], "record_ref": l.get("record_ref") or None}
        rec = None
        if case.get("record"):
            rec = records_cw.parse_file(f"civilwork/records/{line['record_ref']}.txt", case["record"], Queue())
        band = _d(case.get("state", {}).get("band_pct", "100"))      # null = the band state is not known (G4)
        return g3_cw.evaluate(line, app, rec, rec is not None, band_pct=band)
    i, l = case["invoice"], case["line"]
    inv = {"contract_ref": i["contract_ref"], "contractor": i["contractor"], "well_name": i["well_name"], "well_class": i["well_class"],
           "period_start": _date(i["period_start"]), "period_end": _date(i["period_end"]), "invoice_date": _date(i["invoice_date"])}
    line = {"line_ref": l["line_ref"], "service_code": l["service_code"], "unit": l["unit"], "quantity": _d(l["quantity"]),
            "unit_rate": _d(l["unit_rate"]), "amount": _d(l["amount"]), "service_date": _date(l["service_date"]),
            "well_name": l["well_name"], "hole_section": l["hole_section"], "day_status": l["day_status"],
            "depth_from_m": _d(l.get("depth_from_m")), "depth_to_m": _d(l.get("depth_to_m")), "report_ref": l["report_ref"]}
    ddr = None
    if case.get("report"):
        ddr = records_dds.parse_file(f"drilling_services/records/{l['report_ref']}.txt", case["report"], Queue())
    return g3_dds.evaluate(line, inv, ddr, question_readings=case.get("question_readings") or {})


def _split(label: str | None):
    parts = [x for x in (label or "").split("|") if x]
    fact = "|".join(sorted(x for x in parts if x.split(":", 1)[0] in FACTUAL))
    return fact


def _alt_table(alts: dict) -> dict:
    """factual key (class/ground/band) -> sorted set of (allowed, amount) over the reading variants"""
    t = {}
    for k, v in alts.items():
        t.setdefault(_split(k), set()).add((str(_d(v.get("allowed_quantity"))), str(_d(v.get("amount")))))
    return {k: sorted(v) for k, v in sorted(t.items())}


def compare(case: dict, exp: dict | None, res) -> list[dict]:
    cid, contract = case["id"], case["contract"]
    if exp is None:
        return [{"id": cid, "field": "annotation", "reader": None, "engine": "present", "agree": False}]
    out = []

    def add(field, rv, ev, agree=None):
        out.append({"id": cid, "field": field, "reader": rv, "engine": ev, "agree": (rv == ev) if agree is None else agree})

    ealts = {k: v for k, v in res.alternatives.items() if "amount" in v}
    if not any(v.get("allowed_quantity") == 0 for v in ealts.values()):
        add("payable", exp.get("payable"), res.payable)    # else payability itself depends on an open reading (Q11 B)
    ralts = exp.get("alternatives") or {}
    ra, rq = _d(exp.get("amount")), _d(exp.get("allowed_quantity"))
    if ealts or ralts:
        if ralts:
            et, rt = _alt_table(ealts) if ealts else {"": [(str(res.allowed_quantity), str(res.amount))]}, _alt_table(ralts)
            if any(c["dimension"] == "nomination" for c in res.conditions):
                # the engine's nomination condition (Cl.23: PD-210 only on a nominated section; no call-off supplied) means
                # the stated amount if nominated and nothing otherwise - the same content as a 0.00 alternative
                et = {k: sorted(set(v) | {("0", "0.00")}) for k, v in et.items()}
            add("alternatives", rt, et)
        else:
            # a reader who gave one value: it agrees only where the engine's alternatives are readings of text the
            # contract does not settle (the reader then applied one of them); over facts the case does not give
            # (class, ground, band) a single value means the reader took an input the case does not establish
            factual = any(_split(k) for k in ealts)
            match = [k for k, v in ealts.items() if _d(v["amount"]) == ra and _d(v["allowed_quantity"]) == rq]
            add("amount|allowed_quantity (alternatives)", f"{rq} / {ra}",
                {k: f"{v['allowed_quantity']} / {v['amount']}" for k, v in ealts.items()}, agree=bool(match) and not factual)
    else:
        add("allowed_quantity", str(rq) if rq is not None else None, str(res.allowed_quantity) if res.allowed_quantity is not None else None,
            agree=(rq == res.allowed_quantity))
        add("amount", str(ra) if ra is not None else None, str(res.amount) if res.amount is not None else None, agree=(ra == res.amount))
    rr = _d(exp.get("unit_rate"))
    if rr is not None and res.unit_rate is not None and (res.payable or exp.get("payable")):
        add("unit_rate", str(rr), str(res.unit_rate), agree=(rr == res.unit_rate))
    vocab = vocab_for(exp.get("_file", ""), contract)
    add("findings", sorted(set(exp.get("findings") or []) & vocab), sorted(set(res.findings) & vocab))
    if "unresolved" in exp:
        add("unresolved", sorted(set(exp.get("unresolved") or []) & vocab), sorted(set(res.unresolved) & vocab))
    return out


def run(dispositions: dict | None = None) -> dict:
    cases, exps = load_cases(), load_expected()
    disp = dispositions if dispositions is not None else (
        (yaml.safe_load(DISPOSITIONS.read_text()) or {}).get("dispositions", {}) if DISPOSITIONS.exists() else {})
    rows, failures = [], []
    for cid, case in cases.items():
        res = engine_result(case)
        for x in compare(case, exps.get(cid), res):
            if not x["agree"]:
                d = disp.get(f"{cid}|{x['field']}")
                if d and json.dumps(d.get("reader"), default=str) == json.dumps(x["reader"], default=str) \
                        and json.dumps(d.get("engine"), default=str) == json.dumps(x["engine"], default=str):
                    x["disposition"] = d["disposition"]
                else:
                    failures.append(f"{cid} {x['field']}: reader {x['reader']!r} engine {x['engine']!r}")
            rows.append(x)
    extra = sorted(set(exps) - set(cases))
    failures += [f"{e}: expected value for an unknown case" for e in extra]
    by = lambda pred: sum(1 for x in rows if pred(x))  # noqa: E731
    return {"cases": len(cases), "expected": len(exps), "comparisons": len(rows), "agree": by(lambda x: x["agree"]),
            "disposed": by(lambda x: "disposition" in x), "failures": failures,
            "categories": sorted({c["tests"] for c in cases.values()}),
            "superseded": {k: v["_superseded"] for k, v in sorted(exps.items()) if "_superseded" in v}, "rows": rows}


def main() -> int:
    res = run()
    text = json.dumps({k: v for k, v in res.items()}, indent=1, default=str) + "\n"
    if "--check" in sys.argv:                  # read-only: compare with the committed file
        same = OUT.exists() and OUT.read_text() == text
        print("case comparison " + ("reproduces" if same else "DOES NOT reproduce") + " the committed file")
        if not same:
            return 1
    else:
        OUT.write_text(text)
    print(f"cases {res['cases']}, expected {res['expected']}, comparisons {res['comparisons']}, agree {res['agree']}, "
          f"disposed {res['disposed']}, failing {len(res['failures'])}")
    for f in res["failures"]:
        print("  DISAGREE", f)
    return 1 if res["failures"] else 0


if __name__ == "__main__":
    sys.exit(main())
