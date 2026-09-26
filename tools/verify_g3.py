"""G3 exit checks (plan §2, G3): local entitlement and pricing.

Exit condition: "Independently calculated clause-based cases pass, including exceptions and boundaries; all billed code
families are implemented or explicitly marked unresolved; each amount has an explainable calculation trace." Checks:

  X1 independent cases: every reference case agrees with the readers' expected values or carries a disposition bound
     to both values; every item of the G3 scope has a case per contract that exercises it (boundary pairs included, and
     the rounding cases sit on an exact half where the two modes differ); inputs were committed before the readers'
     outputs, and the first case set before the pricing code (git order).
  X2 code families: every billed code is in exactly one family of spec/g3_code_families.yaml (membership from the
     verified tables); the engine valued every line under that family; implemented families have a value or a reason on
     every line and an agreeing reference case; deferred/unresolved families carry that status and an owner; every
     pricing table that applies to a line (FX, index, zone, ground, bands, uplifts, discount, section, class, standby,
     depth band, loss value) appears in its trace.
  X3 traces: every trace replays with independent arithmetic (every step's value, every rounding), starts from a figure
     of the verified tables, cites a source on every step, ends at the line's rate and amount (every alternative too),
     and follows the contract's rounding: CW one half-up rounding last, half-even only after FX (26A) or index (29A);
     DDS half-even after every step (Cl.17).
  X4 decisions: every entry of spec/g3_decisions.yaml has basis with pages, alternatives, known cases that pass, and a
     computed scope giving lines decided and the effect of the adopted reading and of every alternative; the question
     and carried-item registers agree with it; no question still blocks G3.
  X5 boundary: no line's result depends on any other line (evaluation in reverse order gives identical results), and
     the G3 modules produce no classification, flag, invoice total or submission.
  X6 billing independence: changing every billed rate and amount changes no contract value (rate, quantity, amount,
     payability, alternatives); billed figures only produce findings.
  X7 reproduction and context: the committed verification/g3 outputs reproduce; every result and output carries the
     current run context (code + reviewed inputs + snapshot).

Usage::  python tools/verify_g3.py
"""
from __future__ import annotations

import copy
import json
import re
import subprocess
import sys
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import g3_case_compare as gcc  # noqa: E402
import spec_lib as sl  # noqa: E402
from audit import build, g3_cw, g3_dds, g3_run, terms  # noqa: E402

OUT = ROOT / "verification" / "g3"
FAMILIES = ROOT / "spec" / "g3_code_families.yaml"
DECISIONS = ROOT / "spec" / "g3_decisions.yaml"
QUESTIONS = ROOT / "spec" / "open_questions.yaml"
CARRIED = ROOT / "spec" / "carried_items.yaml"
G3_MODULES = ["audit/terms.py", "audit/g3_core.py", "audit/g3_cw.py", "audit/g3_dds.py", "audit/g3_run.py"]
MODES = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}
CENT = Decimal("0.01")


def D(x) -> Decimal:
    return Decimal(str(x))


# ============================================================================== X1 independent cases
# G3 scope item -> (case, what the engine result must show). Pairs are boundaries: both sides must be present.
SCOPE = {
    "identity": [("CW-S56", "finding:contract_ref_variant"), ("CW-S57", "finding:subcontractor_mismatch"),
                 ("DDS-S57", "finding:contract_ref_variant"), ("DDS-S58", "finding:contract_ref_variant"),
                 ("DDS-S59", "finding:contractor_mismatch"), ("DDS-S60", "finding:line_well_differs_from_invoice")],
    "period": [("CW-S47", "finding:outside_period"), ("DDS-S47", "finding:outside_period")],
    "term (both ends)": [("CW-S41", "no:out_of_term"), ("CW-S42", "finding:out_of_term"), ("CW-S43", "finding:out_of_term"),
                         ("DDS-S41", "no:out_of_term"), ("DDS-S42", "finding:out_of_term"), ("DDS-S43", "finding:out_of_term")],
    "submission window (boundary day)": [("CW-S44", "no:submitted_late"), ("CW-S45", "finding:submitted_late"),
                                         ("CW-S46", "finding:submitted_early"), ("DDS-S44", "no:submitted_late"),
                                         ("DDS-S45", "finding:submitted_late"), ("DDS-S46", "finding:submitted_early")],
    "evidence and signatures": [("CW-S48", "finding:record_missing"), ("CW-S49", "finding:record_unsigned"),
                                ("CW-S50", "finding:record_wrong_series"), ("CW-S52", "finding:item_not_supported_by_record"),
                                ("CW-S55", "finding:record_date_mismatch"), ("CW-S58", "finding:record_area_mismatch"),
                                ("DDS-S48", "finding:required_part_missing"), ("DDS-S49", "finding:required_part_missing"),
                                ("DDS-S50", "finding:report_unsigned"), ("DDS-S61", "finding:well_mismatch"),
                                ("DDS-S62", "finding:report_date_mismatch"), ("DDS-S63", "finding:report_missing")],
    "quantity: first hour": [("CW-S31", "not_payable"), ("CW-S32", "allowed:6"), ("DDS-S28", "allowed:6")],
    "quantity: 2% survey tolerance (boundary)": [("CW-S35", "allowed:102"), ("CW-S36", "allowed:100")],
    "quantity: 1% metre tolerance (boundary)": [("DDS-S32", "allowed:101"), ("DDS-S33", "allowed:100")],
    "quantity: five-day week (boundary)": [("CW-S33", "finding:week_not_measurable"), ("CW-S34", "allowed:1")],
    "quantity: six-hour minimum": [("DDS-S29", "allowed:6"), ("DDS-S30", "allowed:5")],
    "unit: civil Cl.26 full rejection": [("CW-S39", "finding:wrong_unit"), ("CW-S39", "not_payable"), ("CW-R16", "not_payable")],
    "unit: drilling Cl.35 (remedy Q11 open)": [("DDS-S53", "finding:wrong_unit")],
    "rate version by work date (boundary pairs)": [("CW-S01|CW-S02", "rates_differ"), ("CW-S03|CW-S04", "rates_differ"),
                                                   ("CW-S05|CW-S06", "rates_differ"), ("CW-S07|CW-S08", "rates_differ"),
                                                   ("DDS-S01|DDS-S02", "rates_differ"), ("DDS-S03|DDS-S04", "rates_differ")],
    "retrospective amendment and its protection": [("CW-S15", "reading:31A protection"), ("CW-S16", "no_reading:31A protection"),
                                                   ("DDS-S05", "reading:36A protection"), ("DDS-S06", "no_reading:36A protection")],
    "civil FX half-even (26A)": [("CW-S19", "rounds_after:26A:half_even"), ("CW-R01", "rounds_after:26A:half_even")],
    "civil indexation half-even (29A)": [("CW-S20", "rounds_after:29A:half_even"), ("CW-R02", "rounds_after:29A:half_even")],
    "civil one half-up rounding, on an exact half": [("CW-S29", "mode_at_half:half_up"), ("CW-S30", "mode_at_half:half_up")],
    "drilling half-even every step, on an exact half": [("DDS-S26", "mode_at_half:half_even"), ("DDS-S27", "mode_at_half:half_even")],
    "build-up order and exceptions": [("CW-S21", "trace:CW.T08_GROUND_FACTORS"), ("CW-S22", "trace:night uplift not payable"),
                                      ("CW-S24", "reading:P11 rest-day alone"), ("DDS-S13", "trace:DDS.T08_SECTION_FACTORS"),
                                      ("DDS-S19", "trace:no hole-section factor on a Standby day")],
}


def _show(res, want: str, results: dict) -> bool:
    kind, _, arg = want.partition(":")
    if kind == "finding":
        return arg in res.findings
    if kind == "no":
        return arg not in res.findings
    if kind == "not_payable":
        return res.payable is False
    if kind == "allowed":
        return res.allowed_quantity == D(arg)
    if kind == "reading":
        return any(arg in x for x in res.readings)
    if kind == "no_reading":
        return not any(arg in x for x in res.readings)
    if kind == "trace":
        return any(arg in (s.get("label", "") + " " + s.get("source", "")) for s in res.trace)
    if kind == "rounds_after":
        clause, mode = arg.split(":")
        st = res.trace
        return any(st[i]["op"] == "mul" and clause in st[i]["source"] and st[i + 1]["op"] == "round" and st[i + 1]["mode"] == mode
                   for i in range(len(st) - 1))
    if kind == "mode_at_half":
        # a rounding in the stated mode applied to a value on an exact half cent, where half-up and half-even differ
        st = [s for s in res.trace if s["op"] != "note"]
        return any(st[i]["op"] == "round" and st[i]["mode"] == arg and (D(st[i - 1]["value"]) * 100) % 1 == Decimal("0.5")
                   and D(st[i - 1]["value"]).quantize(CENT, ROUND_HALF_UP) != D(st[i - 1]["value"]).quantize(CENT, ROUND_HALF_EVEN)
                   for i in range(1, len(st)))
    raise ValueError(want)


def git_first_commit(path: str) -> str | None:
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", path], cwd=ROOT, capture_output=True, text=True)
    lines = out.stdout.split()
    return lines[-1] if out.returncode == 0 and lines else None


def strictly_before(a: str | None, b: str | None) -> bool:
    if not a or not b or a == b:
        return False
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=ROOT).returncode == 0


def x1(comparison: dict, cases: dict, results: dict, first_commit=git_first_commit, before=strictly_before) -> list[str]:
    errs = list(comparison["failures"])
    bad_case = {x["id"] for x in comparison["rows"] if not x["agree"] and "disposition" not in x}
    for item, wants in SCOPE.items():
        for cid, want in wants:
            ids = cid.split("|")
            if any(i not in results for i in ids):
                errs.append(f"scope '{item}': case {cid} missing")
                continue
            if set(ids) & bad_case:
                errs.append(f"scope '{item}': case {cid} does not agree with its independent expected value")
            if want == "rates_differ":
                a, b = (results[i] for i in ids)
                if a.unit_rate is None or b.unit_rate is None or a.unit_rate == b.unit_rate:
                    errs.append(f"scope '{item}': boundary pair {cid} does not change the rate")
            elif not _show(results[ids[0]], want, results):
                errs.append(f"scope '{item}': case {cid} does not show {want}")
    # provenance: inputs committed before outputs; the first case set before the pricing code
    for f in sorted((ROOT / "verification" / "g3" / "cases").glob("packet_*.jsonl")):
        exp = f.with_name(f.name.replace("packet_", "expected_"))
        pc, ec = first_commit(str(f.relative_to(ROOT))), first_commit(str(exp.relative_to(ROOT)))
        if not before(pc, ec):
            errs.append(f"{f.name}: inputs not committed strictly before the readers' output {exp.name}")
        if "identity" not in f.name:
            for mod in ("audit/g3_cw.py", "audit/g3_dds.py"):
                if not before(pc, first_commit(mod)):
                    errs.append(f"{f.name}: not committed before the pricing code {mod}")
    return errs


# ============================================================================== X2 code families
def family_of(contract: str, code: str, fams: list[dict], tables: dict) -> list[str]:
    """Families whose rule the code satisfies, in registry order (membership from the verified tables)."""
    sch1 = {r[0]: r for r in tables[f"{contract}.T01_SCH1"]["rows"]}
    sch8 = {r[0]: r[1] for r in tables.get("DDS.T23_SCH8", {}).get("rows", [])} if contract == "DDS" else {}
    col = lambda t: {r[0] for r in tables[t]["rows"]}  # noqa: E731
    out = []
    for f in fams:
        rule, ok = f["rule"], True
        if "table" in rule:
            ok &= code in col(rule["table"])
        if "also_table" in rule:
            ok &= code in col(rule["also_table"])
        if "sch1_unit" in rule:
            ok &= code in sch1 and sch1[code][2] == rule["sch1_unit"]
        if "codes" in rule:
            ok &= code in rule["codes"]
        if "sch8_contains" in rule:
            ok &= rule["sch8_contains"] in sch8.get(code, "") or code in rule.get("or_codes", [])
        if rule.get("not_in_sch1"):
            ok &= code not in sch1
        if ok:
            out.append(f["id"])
    return out


FEATURES = {
    "CW": {"FX (26A)": "CW.T07_FX", "index (29A)": "CW.T05_SMI", "ground (27A, S4)": "CW.T08_GROUND_FACTORS",
           "zone (Cl.27)": "CW.T02_ZONES", "rest-day uplift": "CW.T11_REST", "night uplift": "CW.T10_NIGHT",
           "annual band": "CW.T12_BANDS", "discount (S2/A2)": "discount "},
    "DDS": {"index (17A)": "DDS.T05_RSI", "section (Cl.18)": "DDS.T08_SECTION_FACTORS", "class (Cl.18)": "DDS.T10_CLASS_FACTORS",
            "standby (Cl.20)": "DDS.T12_STANDBY", "depth band (Sch 2)": "DDS.T02_DEPTH_BANDS", "loss value (Sch 2D)": "DDS.T06_SAR_VALUES",
            "loss FX (Sch 2D)": "DDS.T07_FX", "discount (S2/A2)": "discount "},
}


def applicable_features(contract: str, r, line: dict, ctx: dict, T) -> set[str]:
    """Pricing tables that the verified terms apply to this priced line (independent of the engine's own branching)."""
    f = set()
    if contract == "CW":
        code, wd = line["item_code"], line["work_date"]
        series = code[0]
        zone = (line.get("site_zone") or "").split(" ")[0]
        zf = T.zones.get(zone) if series in T.zone_series and zone else None
        rest = wd.strftime("%A") in T.rest_days and code in T.rest
        f |= {"FX (26A)"} if code in T.usd_items else set()
        f |= {"index (29A)"} if code in T.smi_items else set()
        f |= {"ground (27A, S4)"} if code in T.ground_items else set()
        f |= {"zone (Cl.27)"} if zf is not None else set()
        f |= {"rest-day uplift"} if rest else set()
        if line.get("night_work") == "Y" and code in T.night and not rest and not (zf is not None and zf > T.night_suppressed_above):
            f.add("night uplift")
        f |= {"annual band"} if code in T.banded else set()
        f |= {"discount (S2/A2)"} if T.discount(code, wd) else set()
    else:
        code, sd, status = line["service_code"], line["service_date"], ctx.get("status")
        if code in g3_dds.LOSS:
            return {"loss value (Sch 2D)", "loss FX (Sch 2D)"}
        if code == "PD-210":
            return {"depth band (Sch 2)"}
        f |= {"index (17A)"} if code in T.rsi_items else set()
        f |= {"section (Cl.18)"} if code in T.section_rated and status != "Standby" else set()
        f |= {"class (Cl.18)"} if code in T.class_rated else set()
        f |= {"standby (Cl.20)"} if status == "Standby" and T.standby.get(code) is not None else set()
        f |= {"discount (S2/A2)"} if T.discount(code, sd) else set()
    return f


def _traces(r) -> list[list[dict]]:
    alts = [a["trace"] for a in r.alternatives.values() if isinstance(a, dict) and a.get("trace")]
    return alts or [r.trace]


def x2(w, results: dict, families: dict, comparison: dict, T=None) -> list[str]:
    errs = []
    tables = {**sl.load_terms("CW")["tables"], **sl.load_terms("DDS")["tables"]}
    T = T or {"CW": terms.cw(), "DDS": terms.dds()}
    bad_case = {x["id"] for x in comparison["rows"] if not x["agree"] and "disposition" not in x}
    cases = {x["id"] for x in comparison["rows"]}
    lines = {"CW": {r.ident: r.values for r in w.claims.rows["cw_lines"]}, "DDS": {r.ident: r.values for r in w.claims.rows["dds_lines"]}}
    for contract, fams in families["contracts"].items():
        byid = {f["id"]: f for f in fams}
        for f in fams:
            if f["status"] == "implemented":
                if not f.get("cases"):
                    errs.append(f"{f['id']}: implemented family without a reference case")
                for c in f.get("cases", []):
                    if c not in cases:
                        errs.append(f"{f['id']}: reference case {c} does not exist")
                    elif c in bad_case:
                        errs.append(f"{f['id']}: reference case {c} does not agree")
            elif not re.fullmatch(r"G[4-7]", str(f.get("owner", ""))):
                errs.append(f"{f['id']}: {f['status']} family names no owning gate (G4-G7)")
        codes = sorted({r.code for r in results[contract].values()})
        member = {}
        for code in codes:
            m = family_of(contract, code, fams, tables)
            if not m:
                errs.append(f"{contract} {code}: billed code in no family")
            else:
                member[code] = m[0]
        for ref, r in results[contract].items():
            fam = member.get(r.code)
            if fam is None:
                continue
            if r.family != fam:
                errs.append(f"{ref} {r.code}: valued as {r.family}, registry family {fam}")
                continue
            st = byid[fam]["status"]
            if st == "implemented":
                if r.amount_status in ("deferred", "unresolved"):
                    errs.append(f"{ref} {r.code}: {r.amount_status} in implemented family {fam}")
                elif r.payable and r.amount is None and not any(isinstance(a, dict) and a.get("amount") is not None
                                                                for a in r.alternatives.values()):
                    errs.append(f"{ref} {r.code}: payable with neither an amount nor alternatives")
                elif r.payable is False and not r.reasons:
                    errs.append(f"{ref} {r.code}: not payable without a reason")
            elif r.amount_status != st:
                errs.append(f"{ref} {r.code}: family {fam} is {st} but the line is {r.amount_status}")
            # pricing features that apply must appear in the trace(s)
            if not any(s["op"] == "start" for s in r.trace):
                continue
            if any(s["op"] == "note" and s["label"].startswith("not priced") for s in r.trace):
                if r.payable:
                    errs.append(f"{ref} {r.code}: payable although it could not be priced")
                continue                    # an explicit 'not priced' (no published month) on a non-payable line
            line = lines[contract][ref]
            ctx = {}
            if contract == "DDS":
                ddr = w.ddr.get(line.get("report_ref") or "")
                ctx["status"] = ddr.parts.get("A", {}).get("Status") if ddr else None
                if r.code == "PD-210" and ddr and ddr.parts.get("A", {}).get("Hole section") not in g3_dds.PERFORMANCE_SECTIONS:
                    continue
            for feat in applicable_features(contract, r, line, ctx, T[contract]):
                marker = FEATURES[contract][feat]
                for tr in _traces(r):
                    if not any(marker in (s.get("source", "") if marker != "discount " else s.get("label", "")) for s in tr):
                        errs.append(f"{ref} {r.code}: {feat} applies but its table is not in the trace")
                        break
    return errs


# ============================================================================== X3 traces
def replay(steps: list[dict]) -> tuple[list[str], dict]:
    """Recompute every step with independent arithmetic. Returns (errors, {rate, amount, parts})."""
    errs, v, parts, out = [], None, [], {"rate": None, "amount": None, "quantity": None}
    for i, s in enumerate(steps):
        op = s["op"]
        if op == "note":
            continue
        if not re.search(r"\d", s.get("source", "")):
            errs.append(f"step {i} ({op}) cites no clause, table or page")
        if op == "start":
            v = D(s["value"])
        elif op == "mul":
            v = v * D(s["factor"])
        elif op == "div":
            v = v / D(s["divisor"])
        elif op == "round":
            v = v.quantize(CENT, rounding=MODES[s["mode"]])
        elif op in ("amount", "part"):
            x = D(s["quantity"]) * D(s["rate"])
            if op == "amount":
                if v is not None and D(s["rate"]) != v:
                    errs.append(f"step {i}: amount uses rate {s['rate']}, the trace built {v}")
                out.update(amount=x, quantity=D(s["quantity"]))
            else:
                parts.append(x)
            if D(s["value"]) != x:
                errs.append(f"step {i} ({op}): recorded {s['value']}, replayed {x}")
            continue
        elif op == "sum_parts":
            x = sum(parts, Decimal(0))
            if D(s["value"]) != x:
                errs.append(f"step {i} (sum_parts): recorded {s['value']}, replayed {x}")
            out["amount"] = x
            continue
        else:
            errs.append(f"step {i}: unknown op {op}")
            continue
        if D(s["value"]) != v:
            errs.append(f"step {i} ({op} {s.get('label', '')}): recorded {s['value']}, replayed {v}")
            v = D(s["value"])
    out["rate"] = v
    out["parts"] = parts
    return errs, out


def rounding_errors(contract: str, steps: list[dict]) -> list[str]:
    ops = [s for s in steps if s["op"] in ("mul", "div", "round")]
    errs = []
    if contract == "CW":
        ups = [i for i, s in enumerate(ops) if s["op"] == "round" and s["mode"] == "half_up"]
        if len(ups) != 1:
            errs.append(f"{len(ups)} half-up roundings (Cl.28: the built-up rate is rounded once)")
        elif ups[0] != len(ops) - 1:
            errs.append("a factor is applied after the Cl.28 rounding")
        for i, s in enumerate(ops):
            if s["op"] == "round" and s["mode"] == "half_even":
                prev = ops[i - 1] if i else None
                if not (prev and prev["op"] == "mul" and ("26A" in prev["source"] or "29A" in prev["source"])):
                    errs.append("a half-even rounding not directly after an FX (26A) or index (29A) step")
    else:
        for i, s in enumerate(ops):
            if s["op"] in ("mul", "div") and not (i + 1 < len(ops) and ops[i + 1]["op"] == "round" and ops[i + 1]["mode"] == "half_even"):
                errs.append(f"step '{s.get('label')}' not rounded half to even at once (Cl.17)")
            if s["op"] == "round" and s["mode"] != "half_even":
                errs.append(f"rounding '{s.get('label')}' is {s['mode']} (Cl.17: half to even)")
    return errs


def table_figures(T, contract: str, code: str) -> set[Decimal]:
    vals = set()
    s = T.sch1.get(code)
    if s and s.get("rate") is not None:
        vals.add(s["rate"])
    for ins in T.instruments:
        vals |= {to for c, _e, to in ins.rate_rows if c == code}
        if ins.monthly_code == code:
            vals |= {v for _m, v in ins.monthly}
    if contract == "DDS" and code in T.sar:
        vals.add(T.sar[code])
    return vals


def x3(results: dict, T=None) -> list[str]:
    errs = []
    T = T or {"CW": terms.cw(), "DDS": terms.dds()}
    for contract, rs in results.items():
        for ref, r in rs.items():
            e = []
            tr_errs, rep = replay(r.trace)
            e += tr_errs
            starts = [s for s in r.trace if s["op"] == "start"]
            if starts and D(starts[0]["value"]) not in table_figures(T[contract], contract, r.code):
                e.append(f"trace starts at {starts[0]['value']}, not a figure of the verified tables for {r.code}")
            priced = starts and r.code != "PD-210"
            if priced:
                e += rounding_errors(contract, [s for s in r.trace if s["op"] != "amount"])
            band_alts = {k: a for k, a in r.alternatives.items() if isinstance(a, dict) and a.get("trace")}
            if r.amount_status in ("determined", "conditional", "alternatives") and r.payable:
                if r.amount is not None:
                    if rep["amount"] != r.amount:
                        e.append(f"trace amount {rep['amount']} != result amount {r.amount}")
                    if rep["quantity"] is not None and rep["quantity"] != r.allowed_quantity:
                        e.append(f"trace quantity {rep['quantity']} != allowed {r.allowed_quantity}")
                elif not band_alts and not any(k.startswith("Q4:") for k in r.alternatives):
                    e.append("payable without an amount, a traced alternative or a Q4 alternative")
                if r.unit_rate is not None and r.code != "PD-210" and rep["rate"] != r.unit_rate:
                    e.append(f"trace rate {rep['rate']} != unit_rate {r.unit_rate}")
                if r.code == "PD-210" and r.unit_rate is not None and len(rep["parts"]) != 1:
                    e.append("PD-210 single rate given for a charge in several bands")
                for k, a in band_alts.items():
                    ae, arep = replay(a["trace"])
                    e += [f"{k}: {x}" for x in ae + rounding_errors(contract, [s for s in a["trace"] if s["op"] != "amount"])]
                    if arep["amount"] != a["amount"] or arep["rate"] != a["unit_rate"] or arep["quantity"] != a["allowed_quantity"]:
                        e.append(f"{k}: alternative amount/rate/quantity do not follow its trace")
                for k, a in r.alternatives.items():
                    if k.startswith("Q4:") and a["amount"] != a["allowed_quantity"] * rep["rate"]:
                        e.append(f"{k}: {a['amount']} != {a['allowed_quantity']} x {rep['rate']}")
            elif r.payable is False:
                if r.amount != Decimal("0.00") or r.allowed_quantity != 0 or not r.reasons:
                    e.append("not payable without a 0.00 amount, 0 quantity and a reason")
            elif r.amount_status in ("deferred", "unresolved"):
                if r.amount is not None or not (r.reasons or any(c.status == "unresolved" for c in r.checks)):
                    e.append(f"{r.amount_status} line with an amount or without a reason")
            else:
                e.append(f"amount status {r.amount_status} with payable {r.payable}")
            errs += [f"{contract} {ref} {r.code}: {x}" for x in e]
    return errs


# ============================================================================== X4 decisions
def x4(decisions: dict, scopes: dict, questions: dict, carried: dict, comparison: dict) -> list[str]:
    errs = []
    cases = {x["id"] for x in comparison["rows"]}
    bad_case = {x["id"] for x in comparison["rows"] if not x["agree"] and "disposition" not in x}
    ids = set()
    for d in decisions["decisions"]:
        i = d["id"]
        ids.add(i)
        if d.get("status") not in ("decided", "decided in part", "open"):
            errs.append(f"{i}: status {d.get('status')!r}")
        if not d.get("reading"):
            errs.append(f"{i}: no reading")
        if not d.get("basis") or any(not re.search(r"\bpp?\d+", b) for b in d["basis"]):
            errs.append(f"{i}: basis missing or without a page reference")
        alts = d.get("alternatives") or {}
        if not alts:
            errs.append(f"{i}: no recorded alternative")
        for c in d.get("cases", []):
            if c not in cases:
                errs.append(f"{i}: case {c} does not exist")
            elif c in bad_case:
                errs.append(f"{i}: case {c} does not agree with its independent expected value")
        if not d.get("cases"):
            errs.append(f"{i}: no discriminating case")
        sc = scopes.get(d.get("scope_key"))
        if sc is None:
            errs.append(f"{i}: scope {d.get('scope_key')} not computed")
            continue
        n, eff = sc.get("lines_decided"), sc.get("effect_by_reading") or {}
        if not isinstance(n, int):
            errs.append(f"{i}: lines decided not computed")
            continue
        need = set(alts) | ({"adopted"} if d["status"] != "open" else set())   # open: every recorded reading
        missing = sorted(k for k in need if k not in eff)
        if missing:
            errs.append(f"{i}: no effect computed for reading(s) {missing}")
        if n >= 100:
            for k, e in eff.items():
                if not isinstance(e, dict) or not isinstance(e.get("lines"), int) or not ({"value", "note"} & set(e) or
                                                                                         any(x.startswith("value") for x in e)):
                    errs.append(f"{i}: decides {n} lines but reading {k} reports no lines/value")
    # registers agree with the decisions
    by = {d["id"]: d for d in decisions["decisions"]}
    for q in questions["questions"]:
        owned = q.get("blocks") == "G3" or q.get("originally_blocks") == "G3"
        if not owned:
            continue
        d = by.get(q["id"])
        if d is None:
            errs.append(f"{q['id']}: owned by G3 but no G3 decision entry")
            continue
        if q["status"] != d["status"]:
            errs.append(f"{q['id']}: register status {q['status']!r} vs decision {d['status']!r}")
        if q["status"] == "open" and q.get("blocks") == "G3":
            errs.append(f"{q['id']}: still open and still blocks G3")
        if q["status"] != "open" and q.get("decided_at") != "G3":
            errs.append(f"{q['id']}: decided without decided_at G3")
    listed = {c for d in decisions["decisions"] for c in d.get("carried_items", [])}
    for it in carried.get("items", []):
        if it.get("owner_gate") == "G3":
            if it.get("status") != "decided at G3" or not it.get("g3_treatment"):
                errs.append(f"{it['id']}: owned by G3 but not decided with a treatment")
            if it["id"] not in listed:
                errs.append(f"{it['id']}: not referenced by any G3 decision")
    for it in carried.get("resolved", []):
        if it.get("resolved_at") == "G3" and it["id"] not in listed:
            errs.append(f"{it['id']}: resolved at G3 but not referenced by any G3 decision")
    return errs


# ============================================================================== X5 boundary
FORBIDDEN = ["submission.csv", "expected_total", "invoice_total", "flagged", "def classify", "is_flagged", "apparent_pass"]


def x5_text(paths=None) -> list[str]:
    errs = []
    for p in paths or [ROOT / m for m in G3_MODULES]:
        t = p.read_text().lower()
        errs += [f"{p.name}: '{w}' (G5+ construct)" for w in FORBIDDEN if w in t]
    return errs


def evaluate_all(w, order=1, cw_eval=None, dds_eval=None, mutate=None) -> dict:
    """Evaluate every line one by one (order=-1: reverse), optionally mutating the claim inputs first."""
    cw_eval, dds_eval = cw_eval or g3_cw.evaluate, dds_eval or g3_dds.evaluate
    out = {"CW": {}, "DDS": {}}
    cw_in = list(g3_cw.inputs_from_world(w))[::order]
    for line, app, rec, exists in cw_in:
        line = mutate("CW", line) if mutate else line
        r = cw_eval(line, app, rec, exists)
        out["CW"][r.line_ref] = r
    for line, inv, ddr in list(g3_dds.inputs_from_world(w))[::order]:
        line = mutate("DDS", line) if mutate else line
        r = dds_eval(line, inv, ddr)
        out["DDS"][r.line_ref] = r
    return out


def _value(r) -> dict:
    j = r.to_json()
    return {k: j[k] for k in ("unit_rate", "allowed_quantity", "amount", "payable", "amount_status", "alternatives", "family")}


def x5_order(w, forward: dict, **kw) -> list[str]:
    rev = evaluate_all(w, order=-1, **kw)
    errs = []
    for c in forward:
        for ref, r in forward[c].items():
            a, b = r.to_json(), rev[c][ref].to_json()
            a.pop("ctx"), b.pop("ctx")
            if a != b:
                errs.append(f"{c} {ref}: result depends on evaluation order (cross-line state)")
    return errs


# ============================================================================== X6 billing independence
def _perturb(contract: str, line: dict) -> dict:
    line = dict(line)
    rk = "rate_applied" if contract == "CW" else "unit_rate"
    line[rk] = (line[rk] or Decimal(0)) * Decimal("1.37") + Decimal("0.01")
    line["amount"] = (line["amount"] or Decimal(0)) + Decimal("12345.67")
    return line


def x6(w, forward: dict, **kw) -> list[str]:
    pert = evaluate_all(w, mutate=_perturb, **kw)
    errs = []
    for c in forward:
        for ref, r in forward[c].items():
            if _value(r) != _value(pert[c][ref]):
                errs.append(f"{c} {ref}: a contract value changes with the billed rate/amount")
    return errs


# ============================================================================== X7 reproduction and context
def x7(w, res: dict, committed: dict | None = None) -> list[str]:
    errs = []
    ctx = w.run_context["id"]
    fresh = {
        "summary.json": json.dumps(g3_run.summary(w, res), indent=1, default=str) + "\n",
        "decision_scopes.json": json.dumps(g3_run.decision_scopes(w, res), indent=1, default=str) + "\n",
        "trace_sample.jsonl": "".join(json.dumps(x, default=str) + "\n" for x in g3_run.trace_sample(res)),
    }
    committed = committed if committed is not None else {k: (OUT / k).read_text() if (OUT / k).exists() else None for k in fresh}
    for k, v in fresh.items():
        if committed.get(k) != v:
            errs.append(f"verification/g3/{k} does not reproduce from the current code and inputs")
    if json.loads(fresh["summary.json"])["run_context"] != ctx:
        errs.append("summary run context is not the current run context")
    for c, rs in res.items():
        stale = [ref for ref, r in rs.items() if r.ctx != ctx]
        if stale:
            errs.append(f"{c}: {len(stale)} results without the current run context (e.g. {stale[0]})")
    return errs


def comparison_reproduces(comparison: dict) -> list[str]:
    committed = (OUT / "case_comparison.json").read_text() if (OUT / "case_comparison.json").exists() else None
    fresh = json.dumps(comparison, indent=1, default=str) + "\n"
    return [] if committed == fresh else ["verification/g3/case_comparison.json does not reproduce"]


# ============================================================================== main
def main() -> int:
    w = build.build()
    res = {"CW": g3_cw.run(w), "DDS": g3_dds.run(w)}
    comparison = gcc.run()
    cases = gcc.load_cases()
    case_results = {cid: gcc.engine_result(c) for cid, c in cases.items()}
    by_contract = {c: {cid: r for cid, r in case_results.items() if cases[cid]["contract"] == c} for c in ("CW", "DDS")}
    load = lambda p: yaml.safe_load(p.read_text())  # noqa: E731
    checks = [
        ("X1 independent clause-based cases pass, incl. exceptions and boundaries; inputs before outputs (git)",
         lambda: x1(comparison, cases, case_results) + comparison_reproduces(comparison)),
        ("X2 every billed code family implemented or explicitly deferred/unresolved; pricing tables applied where they apply",
         lambda: x2(w, res, load(FAMILIES), comparison)),
        ("X3 every amount's trace replays independently, cites its sources and follows the contract's rounding",
         lambda: x3(res) + x3(by_contract)),
        ("X4 decisions and open questions: basis, alternatives, cases and lines affected under every reading",
         lambda: x4(load(DECISIONS), json.loads((OUT / "decision_scopes.json").read_text()), load(QUESTIONS), load(CARRIED), comparison)),
        ("X5 boundary: no cross-line state (reverse-order evaluation identical); no classification/flag/total/submission",
         lambda: x5_order(w, res) + x5_text()),
        ("X6 billed rate and amount never change a contract value (diagnostic only)", lambda: x6(w, res)),
        ("X7 committed G3 outputs reproduce; every result carries the current run context", lambda: x7(w, res)),
    ]
    ok = True
    n_lines = sum(len(v) for v in res.values())
    print(f"G3 population: {n_lines} lines (CW {len(res['CW'])}, DDS {len(res['DDS'])}); cases {comparison['cases']}; "
          f"run context {w.run_context['id']}")
    for name, fn in checks:
        e = fn()
        print(("PASS " if not e else "FAIL ") + name)
        for x in e[:20]:
            print("     -", x)
        if len(e) > 20:
            print(f"     ... {len(e) - 20} more")
        ok &= not e
    print("G3 VERIFY " + ("OK" if ok else "FAILED"))
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
