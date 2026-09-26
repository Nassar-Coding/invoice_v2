"""G3 population run: every line of both contracts through the local engines (diagnostic, not a classification).

Writes verification/g3/:
  summary.json          per contract and code: lines, amount status, findings, G4 dependencies, billed-vs-contract
                        rate agreement (a DIAGNOSTIC only: billing is never the truth criterion), run context id
  decision_scopes.json  for every G3 decision and open question, the lines it decides and the amount under each
                        alternative (computed here, never taken from billing)
  trace_sample.jsonl    one full result with trace per code and amount status (reproducible choice: first line_ref)
With --dump also writes build/g3_results.jsonl (every line result with its trace; gitignored).
Nothing here flags an invoice, totals an invoice or writes a submission.

Usage::  python -m audit.g3_run [--dump]
"""
from __future__ import annotations

import argparse
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal

from . import build, g3_cw, g3_dds
from .common import ROOT

OUT = ROOT / "verification" / "g3"
# G3-D1 scope: breaches of the submission rules (window, period, identity, one well per invoice) that the contract states
# no consequence for; spec/g3_decisions.yaml G3-D1.
PROCEDURAL = {"submitted_late", "submitted_early", "outside_period", "contract_ref_variant", "subcontractor_mismatch",
              "contractor_mismatch", "line_well_differs_from_invoice"}
CW_Q3 = {"record_missing", "record_wrong_series", "record_unsigned", "record_date_mismatch", "record_area_mismatch",
         "record_area_unresolved", "item_not_supported_by_record"}


def run_all(w=None):
    w = w or build.build()
    return w, {"CW": g3_cw.run(w), "DDS": g3_dds.run(w)}


def _s(x):
    return None if x is None else str(x)


def summary(w, res) -> dict:
    lines = {"CW": {r.ident: r.values for r in w.claims.rows["cw_lines"]},
             "DDS": {r.ident: r.values for r in w.claims.rows["dds_lines"]}}
    rate_key = {"CW": "rate_applied", "DDS": "unit_rate"}
    out = {"run_context": w.run_context["id"], "contracts": {}}
    for c, rs in res.items():
        codes = defaultdict(lambda: {"lines": 0, "amount_status": Counter(), "findings": Counter(), "g4": Counter(),
                                     "rate_agree": 0, "rate_differs": 0, "rate_not_single": 0, "billed_rate_is_a_band_rate": 0})
        for ref, r in rs.items():
            e = codes[r.code]
            e["lines"] += 1
            e["amount_status"][r.amount_status] += 1
            e["findings"].update(r.findings)
            e["g4"].update(x.split(" ")[0] for x in r.g4_dependencies)
            if r.unit_rate is None:
                e["rate_not_single"] += 1
                if any(c.check == "rate" and c.status == "unresolved" and "band" in c.detail for c in r.checks):
                    e["billed_rate_is_a_band_rate"] += 1
            elif r.unit_rate == lines[c][ref][rate_key[c]]:
                e["rate_agree"] += 1
            else:
                e["rate_differs"] += 1
        out["contracts"][c] = {
            "lines": len(rs),
            "amount_status": dict(sorted(Counter(r.amount_status for r in rs.values()).items())),
            "findings": dict(sorted(Counter(f for r in rs.values() for f in r.findings).items())),
            "always_g4": (g3_cw if c == "CW" else g3_dds).ALWAYS_G4,
            "codes": {k: {**v, "amount_status": dict(v["amount_status"]), "findings": dict(v["findings"]), "g4": dict(v["g4"])}
                      for k, v in sorted(codes.items())},
            "note": "rate_agree/rate_differs compare the billed rate with the contract rate as a diagnostic only (billing is "
                    "never the truth criterion). CW band-rated items have no single rate before G4 supplies the band: they "
                    "count as rate_not_single, and billed_rate_is_a_band_rate counts those billed at one band's rate.",
        }
    return out


def decision_scopes(w, res) -> dict:
    cw, dds = res["CW"], res["DDS"]
    dl = {r.ident: r.values for r in w.claims.rows["dds_lines"]}
    sc = {}

    def val(r):  # the line's value if the reading that made it not payable were reversed: allowed (billed-capped) x rate
        return None if r.unit_rate is None else str(r.unit_rate)

    q3cw = [r for r in cw.values() if set(r.findings) & CW_Q3]
    q3dds = [r for r in dds.values() if "Q3:A" in r.readings]
    sc["Q3"] = {"decided": "A", "cw_lines": sorted(r.line_ref for r in q3cw), "dds_lines": sorted(r.line_ref for r in q3dds),
                "under_A": "not payable in this valuation/invoice (amount 0.00)",
                "under_B": {"cw": {r.line_ref: {"unit_rate": val(r)} for r in q3cw},
                            "dds": {r.line_ref: {"unit_rate": val(r)} for r in q3dds},
                            "note": "the line keeps its value in its own application/invoice; CW P23 deducts it from the next valuation (G4 event)"}}
    q4 = {r.line_ref: {k: {"allowed_quantity": _s(v["allowed_quantity"]), "amount": _s(v["amount"])} for k, v in r.alternatives.items()
                       if k.startswith("Q4:")} for r in dds.values() if any(k.startswith("Q4:") for k in r.alternatives)}
    hourly = [r for r in dds.values() if r.code in g3_dds.HOURLY]
    sc["Q4"] = {"status": "open", "hourly_lines": len(hourly), "lines_where_readings_differ": q4,
                "lines_where_all_readings_agree": sum(1 for r in hourly if r.line_ref not in q4)}
    dd102 = [r for r in dds.values() if r.code == "DD-102"]
    hc630 = [r for r in dds.values() if r.code == "HC-630"]
    dd120_br = [r for r in dds.values() if r.code == "DD-120" and w.ddr.get(dl[r.line_ref]["report_ref"]) and
                (w.ddr[dl[r.line_ref]["report_ref"]].parts["A"].get("Back-reaming hours") or 0) > 0]
    sc["Q5"] = {"decided": {"DD-102": "A (per coordinator recorded, Sch 8 intro p27, App G 'night man')",
                            "HC-630": "counted as recorded (Cl.30)", "DD-120": "circulating hours only (Cl.21)"},
                "DD-102": {"lines": len(dd102), "under_A_payable": sum(1 for r in dd102 if r.payable),
                           "under_A_quantity": dict(Counter(str(r.allowed_quantity) for r in dd102)),
                           "under_B": "no tool term exists for DD-102: tool-in-hole unestablishable on all lines (0 chargeable)"},
                "HC-630": {"lines": len(hc630), "recorded_clean_out_runs_not_1": sum(
                    1 for r in hc630 if w.ddr[dl[r.line_ref]["report_ref"]].parts["A"].get("Clean-out runs") != 1),
                    "under_per_BHA_run": "one per run on a run day (run lifecycle is G4 state)"},
                "DD-120_back_reaming_days": {"lines": len(dd120_br), "note": "lines whose day records back-reaming hours; "
                                             "including them in DD-120 would raise the chargeable hours on these days"}}
    cls = [r for r in dds.values() if any("well class" in (s.get("label") or "") for s in r.trace)]
    pd210 = [r for r in dds.values() if r.code == "PD-210"]
    both = [r for r in cw.values() if any("P11 rest-day alone" in x for x in r.readings)]
    sc["Q8"] = {"decided": "A (explicit defaults and disclosed proxies)",
                "class_factor_from_invoice_header": {"lines": len(cls), "non_standard": sum(
                    1 for r in cls if any("Standard" not in (s.get("label") or "") and "well class" in (s.get("label") or "") for s in r.trace))},
                "pd210_nomination_not_supplied": {"lines": len(pd210), "conditional": sum(1 for r in pd210 if r.amount_status == "conditional"),
                                                  "not_performance_section": sum(1 for r in pd210 if "not_performance_section" in r.findings)},
                "cw_night_and_rest_day_rest_alone": {"lines": len(both), "line_refs": sorted(r.line_ref for r in both)}}
    wu = [r for r in dds.values() if "wrong_unit" in r.findings]
    sc["Q11"] = {"accumulator": "no effect on the pinned data: records bound 10,002 m < 40,000 m per well (spec/question_scopes.json)",
                 "tolerance": "25A applied per charge against the metres the report supports for its interval",
                 "wrong_unit_remedy": {"status": "open", "dds_lines_billed_in_another_unit": sorted(r.line_ref for r in wu)},
                 "pd210_quantity_above_report": sum(1 for r in pd210 if "quantity_above_report" in r.findings)}
    lh = [r for r in dds.values() if r.code in g3_dds.LOSS]
    losses = {l["report"]: l for run in w.runs.values() for l in run.losses}
    sc["Q13"] = {"decided": "A (Part E hours, Cl.31 'as stated on the Lost in Hole Report'; corroborated by P12 tool history)",
                 "lh_lines": len(lh), "part_e_equals_tool_history": sum(1 for l in losses.values() if l["hours_on_well"] == l["tool_daily_hours_through_loss_day"]),
                 "losses": len(losses)}
    for c, rs in res.items():
        proc = [r for r in rs.values() if set(r.findings) & PROCEDURAL]
        det = [r for r in proc if r.payable and r.amount is not None]
        bounded = [r for r in proc if r.payable and r.amount is None]
        amts = lambda r: [v["amount"] for v in r.alternatives.values() if v.get("amount") is not None]  # noqa: E731
        sc.setdefault("G3-D1", {})[c] = {
            "lines": len(proc), "payable_under_D1": len(det) + len(bounded),
            "value_under_D1_single_amount_lines": {"lines": len(det), "value": str(sum((r.amount for r in det), Decimal(0)))},
            "value_under_D1_lines_without_single_amount": {
                "lines": len(bounded), "min": str(sum((min(amts(r)) for r in bounded), Decimal(0))),
                "max": str(sum((max(amts(r)) for r in bounded), Decimal(0))),
                "note": "band-conditional (CW) or Q4 alternatives (DDS): bounded by the smallest and largest carried amount"},
            "under_alternative": "not payable now: value 0.00 on these lines"}
    uns = [r for r in dds.values() if "report_unsigned" in r.findings]
    sc["G3-D2"] = {"lines": len(uns), "schedule5_not_payable": sum(1 for r in uns if r.code in g3_dds.terms.dds().sch5),
                   "others_payable_under_D2": sum(1 for r in uns if r.payable),
                   "under_alternative": "every line on an unsigned report not payable"}
    _effects(w, res, sc, locals())
    return sc


def _tot(rs) -> str:
    return str(sum((r.amount for r in rs if r.amount is not None), Decimal(0)))


def _effects(w, res, sc, v) -> None:
    """Uniform block per decision (checked by tools/verify_g3.py X4): lines_decided and, for the adopted reading and
    every recorded alternative, the lines affected and their value. Values are computed from the contract (engine
    results and the contract formula under the alternative), never taken from billed amounts; the billed QUANTITY
    enters only where the contract makes it the cap ('payable as charged' up to the supported quantity)."""
    cw, dds = res["CW"], res["DDS"]
    cl = {r.ident: r.values for r in w.claims.rows["cw_lines"]}
    dl = {r.ident: r.values for r in w.claims.rows["dds_lines"]}
    T = g3_dds.terms.dds()
    # Q3 ---------------------------------------------------------------------------------------------------------
    q3 = v["q3cw"] + v["q3dds"]
    qty = lambda r: (cl if r.contract == "CW" else dl)[r.line_ref]["quantity"]  # noqa: E731
    single = [r for r in q3 if r.unit_rate is not None]
    sc["Q3"].update(lines_decided=len(q3), effect_by_reading={
        "adopted": {"reading": "A", "lines": len(q3), "payable": sum(1 for r in q3 if r.payable), "value": _tot(q3)},
        "B": {"lines": len(q3), "value_kept_on_single_rate_lines": str(sum((qty(r) * r.unit_rate for r in single), Decimal(0))),
              "lines_without_single_rate": len(q3) - len(single),
              "note": "no record caps the quantity, so the billed quantity at the contract rate; CW P23 would deduct it from the next valuation"}})
    # Q4 ---------------------------------------------------------------------------------------------------------
    q4 = [r for r in dds.values() if any(k.startswith("Q4:") for k in r.alternatives)]
    eff = {}
    for r in q4:
        for k, a in r.alternatives.items():
            if k.startswith("Q4:"):
                e = eff.setdefault(k.split(":")[1], {"lines": 0, "value": Decimal(0)})
                e["lines"] += 1
                e["value"] += a["amount"]
    sc["Q4"].update(lines_decided=len(q4), effect_by_reading={k: {"lines": e["lines"], "value": str(e["value"])} for k, e in sorted(eff.items())})
    # Q5 ---------------------------------------------------------------------------------------------------------
    dd102, hc630, br = v["dd102"], v["hc630"], v["dd120_br"]
    hc_diff = [r for r in hc630 if w.ddr[dl[r.line_ref]["report_ref"]].parts["A"].get("Clean-out runs") != 1]
    br_up = []
    for r in br:
        billed = dl[r.line_ref]["quantity"]
        if r.allowed_quantity is not None and r.unit_rate is not None and billed > r.allowed_quantity:
            extra = Decimal(w.ddr[dl[r.line_ref]["report_ref"]].parts["A"].get("Back-reaming hours") or 0)
            br_up.append(min(billed - r.allowed_quantity, extra) * r.unit_rate)
    sc["Q5"].update(lines_decided=len(dd102) + len(hc630) + len(br), effect_by_reading={
        "adopted": {"reading": "DD-102 A; HC-630 counts (Cl.30); DD-120 circulating only", "lines": len(dd102) + len(hc630) + len(br),
                    "value": str(sum((Decimal(x) for x in (_tot(dd102), _tot(hc630), _tot(br))), Decimal(0))),
                    "DD-102": {"lines": len(dd102), "value": _tot(dd102)}, "HC-630": {"lines": len(hc630), "value": _tot(hc630)},
                    "DD-120 on back-reaming days": {"lines": len(br), "value": _tot(br)}},
        "B_DD102": {"lines": len(dd102), "chargeable": 0, "value": "0.00",
                    "note": "the Sch 8 row's 'tool in the hole' has no tool for DD-102: not establishable on any line"},
        "HC630_per_run": {"lines": len(hc630), "lines_that_could_differ": len(hc_diff),
                          "note": "one charge per BHA run needs the run lifecycle (G4); lines recording other than one clean-out run could differ"},
        "DD120_back_reaming": {"lines": len(br), "lines_whose_allowed_hours_would_rise": len(br_up),
                               "value_increase_at_most": str(sum(br_up, Decimal(0)))}})
    # Q8 ---------------------------------------------------------------------------------------------------------
    cls, pd210 = v["cls"], v["pd210"]
    sc["Q8"].update(lines_decided=len(cls) + len(pd210), effect_by_reading={
        "adopted": {"reading": "A", "lines": len(cls) + len(pd210), "class_proxy_lines": len(cls), "value_class_proxy_lines": _tot(cls),
                    "pd210_conditional_lines": sum(1 for r in pd210 if r.amount_status == "conditional"),
                    "value_pd210_if_nominated": _tot([r for r in pd210 if r.amount_status == "conditional"])},
        "B": {"lines": len(cls) + len(pd210), "value": None,
              "note": "every amount depending on the unsupplied call-off (class, nomination) unresolved: no value on these lines"}})
    # Q11 --------------------------------------------------------------------------------------------------------
    wu = v["wu"]
    sc["Q11"].update(lines_decided=len(wu), effect_by_reading={
        "adopted": {"reading": "accumulator and tolerance decided; wrong-unit remedy open", "lines": len(wu), "value": _tot(wu)},
        "wrong_unit_A": {"lines": len(wu), "note": "value per supported quantity"},
        "wrong_unit_B": {"lines": len(wu), "value": "0.00"}})
    # Q13 --------------------------------------------------------------------------------------------------------
    losses = {l["report"]: l for run in w.runs.values() for l in run.losses}
    lh = [r for r in v["lh"] if r.payable]
    b_val, b_diff = Decimal(0), 0
    for r in lh:
        ln = dl[r.line_ref]
        loss = losses[ln["report_ref"]]
        amt = r.allowed_quantity * g3_dds.loss_value(r.code, ln["service_date"], Decimal(loss["well_daily_hours_through_loss_day"]), T,
                                                      g3_dds.Trace(), "whole-well daily sum", "Q13 reading B")
        b_val += amt
        b_diff += amt != r.amount
    sc["Q13"].update(lines_decided=len(v["lh"]), effect_by_reading={
        "adopted": {"reading": "A", "lines": len(v["lh"]), "payable": len(lh), "value": _tot(lh)},
        "B": {"lines": len(lh), "lines_whose_amount_differs": b_diff, "value": str(b_val)},
        "C": {"lines": len(lh), "note": "a query bounded by A and B: no longer needed (Part E equals the tool history on every loss)"}})
    # G3-D1, G3-D2 -----------------------------------------------------------------------------------------------
    d1 = {c: [r for r in rs.values() if set(r.findings) & PROCEDURAL] for c, rs in res.items()}
    n1 = sum(len(x) for x in d1.values())
    sc["G3-D1"].update(lines_decided=n1, effect_by_reading={
        "adopted": {"lines": n1, "payable": sum(1 for x in d1.values() for r in x if r.payable),
                    "value_single_amount_lines": str(sum((Decimal(_tot(x)) for x in d1.values()), Decimal(0)))},
        "not_payable_now": {"lines": n1, "value": "0.00"}})
    uns = v["uns"]
    sc["G3-D2"].update(lines_decided=len(uns), effect_by_reading={
        "adopted": {"lines": len(uns), "not_payable": sum(1 for r in uns if not r.payable), "value": _tot(uns)},
        "all_lines": {"lines": len(uns), "value": "0.00"}})


def trace_sample(res) -> list[dict]:
    seen, out = set(), []
    for c, rs in res.items():
        for ref in sorted(rs):
            r = rs[ref]
            key = (c, r.code, r.amount_status)
            if key not in seen:
                seen.add(key)
                out.append(r.to_json())
    return out


def write(dump=False) -> dict:
    w, res = run_all()
    OUT.mkdir(parents=True, exist_ok=True)
    s = summary(w, res)
    (OUT / "summary.json").write_text(json.dumps(s, indent=1, default=str) + "\n")
    (OUT / "decision_scopes.json").write_text(json.dumps(decision_scopes(w, res), indent=1, default=str) + "\n")
    (OUT / "trace_sample.jsonl").write_text("".join(json.dumps(x, default=str) + "\n" for x in trace_sample(res)))
    if dump:
        b = ROOT / "build"
        b.mkdir(exist_ok=True)
        with (b / "g3_results.jsonl").open("w") as fh:
            for rs in res.values():
                for r in rs.values():
                    fh.write(json.dumps(r.to_json(), default=str) + "\n")
    return s


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dump", action="store_true")
    s = write(ap.parse_args().dump)
    for c, v in s["contracts"].items():
        print(c, v["lines"], v["amount_status"])
    return 0


if __name__ == "__main__":
    sys.exit(main())
