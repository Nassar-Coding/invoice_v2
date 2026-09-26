"""G3 correction round 2 (re-audit Phase3_G3_reaudit_Agent2.md): each item's probe is now handled correctly, the
check that guards it fails on the defect (negative controls), and a positive case shows the check is not simply off."""
import copy
import dataclasses
import datetime as dt
from pathlib import Path

import pytest
import yaml

import g3_case_compare as gcc
import verify_g3 as vg
from audit import build, g3_cw, g3_dds

ROOT = Path(__file__).resolve().parents[1]
FAMILIES = yaml.safe_load((ROOT / "spec/g3_code_families.yaml").read_text())


@pytest.fixture(scope="module")
def world():
    return build.build()


@pytest.fixture(scope="module")
def res(world):
    return {"CW": g3_cw.run(world), "DDS": g3_dds.run(world)}


@pytest.fixture(scope="module")
def cmp_():
    return gcc.run()


def _cw_input(world, ref):
    return next(x for x in g3_cw.inputs_from_world(world) if x[0]["line_ref"] == ref)


def _cited(world, ref, record_ref):
    """The line as billed, citing another record (the re-audit's probe)."""
    line, app, _rec, _ex = _cw_input(world, ref)
    line = {**line, "record_ref": record_ref}
    rec = world.cw[record_ref]
    return line, app, rec, True


# ---------------------------------------------------------------------------------------------------- B1 ground authority
def test_b1_probe_unrelated_record_does_not_settle_the_class(world):
    """PA-00031-06 (A.12.050, 30 Apr 2025, S-01) citing DX-00007 (25 Jan 2025, S-04, G5): not determined at 85.41."""
    line, app, rec, ex = _cited(world, "PA-00031-06", "DX-00007")
    assert (rec.date, rec.area, rec.ground) == (dt.date(2025, 1, 25), "S-04", "G5")
    r = g3_cw.evaluate(line, app, rec, ex)
    assert r.amount_status == "conditional" and r.amount is None and r.unit_rate is None
    assert {k: str(v["unit_rate"]) for k, v in r.alternatives.items()} == {
        "ground:G1": "49.26", "ground:G2": "52.40", "ground:G3": "58.69", "ground:G4": "72.05", "ground:G5": "85.41"}
    assert any(c["dimension"] == "ground" and c["owner"] == "G5" for c in r.conditions)
    why = next(x for x in r.readings if "does not apply to this work" in x)
    assert "dated 2025-01-25, work 2025-04-30" in why and "area S-04, work S-01" in why and "line bills A.12.050" in why
    assert "ground_differs_from_record" in r.unresolved and "ground_differs_from_record" not in r.findings


def test_b1_positive_applicable_record_settles_the_class():
    """CW-S64: A.12.020 (no Schedule 5 record needed) citing a record of the same day, area and trench work: G3."""
    r = gcc.engine_result(gcc.load_cases()["CW-S64"])
    assert r.amount_status == "determined" and not r.alternatives and not r.conditions
    assert [s["label"] for s in r.trace if s["label"].startswith("ground ")] == ["ground G3"]
    assert "ground_differs_from_record" in r.findings            # the application states G4


@pytest.mark.parametrize("cid, why", [("CW-S65", "dated 2025-06-09, work 2025-06-10"), ("CW-S66", "area S-04, work S-01"),
                                      ("CW-S67", "evidences ['A.12.030'], line bills A.12.020")])
def test_b1_each_mismatch_alone_keeps_every_class(cid, why):
    r = gcc.engine_result(gcc.load_cases()[cid])
    assert r.amount is None and vg._dim_values(r, "ground") == {"G1", "G2", "G3", "G4", "G5"}
    assert any(why in x for x in r.readings)


def test_b1_weekly_and_unparsed_area_branches(world):
    """Branches no real line exercises: a record for a week applies to a day in that week only; an unparsed area never
    applies. Engine and the independent X2 predicate agree on each."""
    line, app, rec, ex = _cw_input(world, "PA-00017-07")          # A.12.040 with its own record DX-00106
    code = line["item_code"]
    wk = dataclasses.replace(rec, week_beginning=line["work_date"] - dt.timedelta(days=6), date=None)
    late = dataclasses.replace(rec, week_beginning=line["work_date"] - dt.timedelta(days=7), date=None)
    noarea = dataclasses.replace(rec, area=None)
    for r, want in ((rec, True), (wk, True), (late, False), (noarea, False)):
        assert g3_cw.record_applies(r, line, code)[0] is want
        assert vg._applies_to_work(r, line) is want


def test_b1_engine_and_x2_predicate_agree_on_every_record(world):
    n = 0
    for line, app, rec, ex in g3_cw.inputs_from_world(world):
        if rec is not None:
            n += 1
            assert g3_cw.record_applies(rec, line, line["item_code"])[0] == vg._applies_to_work(rec, line), line["line_ref"]
            for other in ("DX-00007", "DX-00008"):
                o = world.cw[other]
                assert g3_cw.record_applies(o, line, line["item_code"])[0] == vg._applies_to_work(o, line)
    assert n > 1000


def _any_record(monkeypatch):
    """The defect: any referenced record with a ground class taken as the classification of this work."""
    monkeypatch.setattr(g3_cw, "record_applies", lambda rec, line, code: (True, ""))


def test_b1_control_x2_rejects_an_unrelated_record_as_authority(world, res, cmp_, monkeypatch):
    _any_record(monkeypatch)
    line, app, rec, ex = _cited(world, "PA-00031-06", "DX-00007")
    r = g3_cw.evaluate(line, app, rec, ex)
    assert r.amount_status == "determined" and str(r.unit_rate) == "85.41"      # the re-audit's defect, reproduced
    r.family = res["CW"]["PA-00031-06"].family
    w = copy.copy(world)
    w.claims = copy.deepcopy(world.claims)
    next(x for x in w.claims.rows["cw_lines"] if x.ident == "PA-00031-06").values["record_ref"] = "DX-00007"
    errs = vg.x2(w, {"CW": {"PA-00031-06": r}, "DDS": {}}, FAMILIES, cmp_)
    assert any("PA-00031-06" in e and "without every ground class" in e for e in errs)


def test_b1_control_x6_rejects_an_unrelated_record_as_authority(world, res, monkeypatch):
    only = set(sorted(r for r, x in res["CW"].items() if any(c["dimension"] == "ground" for c in x.conditions))[:60])
    ok_fwd = vg.evaluate_all(world, only=only)
    assert vg.x6(world, ok_fwd, mutate=vg.perturb_claim_classes, only=only) == []      # the corrected engine passes
    _any_record(monkeypatch)
    fwd = vg.evaluate_all(world, only=only)
    errs = vg.x6(world, fwd, mutate=vg.perturb_claim_classes, only=only)
    assert errs and all("claim-stated classification" in e for e in errs)


def test_b1_control_x2_rejects_ignoring_an_applicable_record(world, res, cmp_, monkeypatch):
    """The opposite defect (the check simply disabled): records never settle the class."""
    monkeypatch.setattr(g3_cw, "record_applies", lambda rec, line, code: (False, "ignored"))
    line, app, rec, ex = _cw_input(world, "PA-00017-07")
    r = g3_cw.evaluate(line, app, rec, ex)
    r.family = res["CW"]["PA-00017-07"].family
    errs = vg.x2(world, {"CW": {"PA-00017-07": r}, "DDS": {}}, FAMILIES, cmp_)
    assert any("PA-00017-07" in e and "an applicable record settles the class" in e for e in errs)


def test_b1_population_unchanged(res):
    cw = list(res["CW"].values())
    by = {s: sum(1 for r in cw if r.amount_status == s) for s in ("determined", "conditional", "not_payable")}
    assert by == {"determined": 6171, "conditional": 1560, "not_payable": 15}
    assert sum(1 for r in cw if any(c["dimension"] == "ground" for c in r.conditions)) == 649


# ---------------------------------------------------------------------------------------------------- B2 PD-210 domain
from decimal import Decimal  # noqa: E402
import itertools  # noqa: E402
import random  # noqa: E402

from audit import terms  # noqa: E402

DT = terms.dds()


def _case(cid, **line):
    c = copy.deepcopy(gcc.load_cases()[cid])
    c["line"].update(line)
    return gcc.engine_result(c)


def _allocs(r):
    return {tuple(Decimal(s["quantity"]) for s in a["trace"] if s["op"] == "part") for a in r.alternatives.values()}


def _x3(r):
    return vg.x3({"DDS": {"case": r}})


def test_b2_98_m_carries_every_allocation():
    r = _case("DDS-S72")
    assert r.amount is None and r.allowed_quantity == Decimal("98") and r.payable
    assert _allocs(r) == {(Decimal(48), Decimal(50)), (Decimal(49), Decimal(49)), (Decimal(50), Decimal(48))}
    assert sorted(str(a["amount"]) for a in r.alternatives.values()) == ["4908.70", "4924.50", "4940.30"]
    dom = next(c for c in r.conditions if c["dimension"] == "tolerance")
    assert dom["owner"] == "G5" and dom["domain"]["count"] == 3 and dom["domain"]["mode"] == "enumerated"
    assert _x3(r) == []


def test_b2_40_m_is_never_an_empty_payable_result():
    r = _case("DDS-S73")
    assert r.payable and r.allowed_quantity == Decimal("40") and r.alternatives        # was: no amount, no alternatives
    dom = next(c for c in r.conditions if c["dimension"] == "tolerance")["domain"]
    assert (dom["mode"], dom["count"], dom["listed"]) == ("bounds", 41, 2)
    assert [(p["min_m"], p["max_m"]) for p in dom["parts"]] == [("0", "40"), ("0", "40")]
    assert "39 allocations between the two listed extremes" in dom["not_listed"] and "G5" in dom["not_listed"]
    assert sorted(str(a["amount"]) for a in r.alternatives.values()) == ["1694.00", "2326.00"]
    assert _x3(r) == []


def _old_one_band_at_a_time(parts, allowed, step, r):
    """The round-1 engine: the whole difference moved into one band at a time (the re-audit's B2 defect)."""
    diff = allowed - sum(p[3] for p in parts)
    return {f"tolerance:{diff} m in band {band}": [p if j != i else (band, pa, pb, q + diff, rate) for j, p in enumerate(parts)]
            for i, (band, pa, pb, q, rate) in enumerate(parts) if q + diff >= 0}


def test_b2_control_x3_rejects_the_incomplete_domain(monkeypatch):
    monkeypatch.setattr(g3_dds, "_allocation_sets", _old_one_band_at_a_time)
    r = _case("DDS-S72")
    assert len(r.alternatives) == 2                                    # 49+49 missing (the re-audit's finding)
    assert any("allocation domain incomplete: 2 distinct allocation(s) listed, the domain holds 3" in e for e in _x3(r))


def test_b2_control_x3_rejects_a_payable_line_with_no_amount_or_alternatives():
    r = copy.deepcopy(_case("DDS-S73"))
    r.alternatives, r.conditions = {}, [c for c in r.conditions if c["dimension"] != "tolerance"]
    assert any("payable without an amount or alternatives" in e for e in _x3(r))


def test_b2_engine_guard_never_emits_an_empty_payable_result(monkeypatch):
    monkeypatch.setattr(g3_dds, "_allocation_sets", lambda *a: {})
    r = _case("DDS-S73")
    assert r.payable is None and r.amount_status == "unresolved" and "no_admissible_result" in r.unresolved
    assert _x3(r) == []


def test_b2_control_x3_rejects_one_missing_enumerated_allocation():
    r = copy.deepcopy(_case("DDS-S76"))
    r.alternatives.pop(next(iter(r.alternatives)))
    assert any("domain incomplete: 15 distinct allocation(s) listed, the domain holds 16" in e for e in _x3(r))


def test_b2_control_x3_rejects_bounds_that_are_not_the_extremes_or_hide_the_domain():
    r = _case("DDS-S75")
    wrong = copy.deepcopy(r)
    k = next(k for k in wrong.alternatives if "highest" in k)
    wrong.alternatives[k] = copy.deepcopy(wrong.alternatives[next(k2 for k2 in wrong.alternatives if "lowest" in k2)])
    assert any("are not the domain's lowest and highest amounts" in e for e in _x3(wrong))
    hidden = copy.deepcopy(r)
    next(c for c in hidden.conditions if c["dimension"] == "tolerance").pop("domain")
    assert any("bounds without the whole domain stated" in e for e in _x3(hidden))
    uncounted = copy.deepcopy(r)
    next(c for c in uncounted.conditions if c["dimension"] == "tolerance")["domain"]["count"] = 2
    assert any("bounds without the whole domain stated" in e for e in _x3(uncounted))


def test_b2_existing_controls_still_fail(monkeypatch):
    """The round-1 controls (a 999.00 part rate; parts pricing fewer metres than allowed) on a crossing charge."""
    r = copy.deepcopy(_case("DDS-S72"))
    k = next(iter(r.alternatives))
    part = next(s for s in r.alternatives[k]["trace"] if s["op"] == "part")
    part["rate"], part["value"] = "999.00", str(Decimal(part["quantity"]) * Decimal("999.00"))
    assert any("PD-210 part rate 999.00 is not band 1's 42.35" in e for e in _x3(r))
    r = copy.deepcopy(_case("DDS-S72"))
    part = next(s for s in r.alternatives[k]["trace"] if s["op"] == "part")
    part["quantity"], part["value"] = str(Decimal(part["quantity"]) - 1), str((Decimal(part["quantity"]) - 1) * Decimal(part["rate"]))
    assert any("trace quantity 97 != allowed quantity 98" in e for e in _x3(r))


def test_b2_decimal_metres_are_ascertained_in_cents_and_the_control_fails(monkeypatch):
    """DDS Cl.17 'Every amount is ascertained in cents': found by the round-2 reader on DDS-S76 (98.5 m)."""
    r = _case("DDS-S76")
    assert len(r.alternatives) == 16 and all(a["amount"] == a["amount"].quantize(Decimal("0.01")) for a in r.alternatives.values())
    assert {str(a["amount"]) for a in r.alternatives.values()} >= {"4937.78", "4961.48"}
    assert _x3(r) == []
    real_part = g3_dds.Trace.part
    monkeypatch.setattr(g3_dds.Trace, "part", lambda self, label, qty, rate, source, mode=None: real_part(self, label, qty, rate, source))
    bad = _case("DDS-S76")
    assert any("is not ascertained in cents (DDS Cl.17)" in e for e in _x3(bad))


def _brute(parts, allowed, step):
    """Independent of engine and X3: every allocation on the grid by direct product, then filtered."""
    lens = [p[3] for p in parts]
    short = allowed <= sum(lens)          # fewer metres: each band 0..its length; more: each band its length plus some excess
    span = [(Decimal(0), le) if short else (le, le + allowed - sum(lens)) for le in lens]
    ranges = [[a + Decimal(i) * step for i in range(int((b - a) / step) + 1)] for a, b in span]
    out = set()
    for qs in itertools.product(*ranges[:-1]):
        last = allowed - sum(qs, Decimal(0))
        if span[-1][0] <= last <= span[-1][1] and (last / step) % 1 == 0:
            out.add(qs + (last,))
    return out


SCENARIOS = (
    # two bands, short interval: reductions (whole and half metres)
    [("1490", "1510", str(20 - d)) for d in (1, 2, 5, 8)] + [("1495", "1505", "9.5"), ("1480", "1530", "42.5"), ("2990", "3006", "13")]
    # two bands, long interval: excess within 25A's 1% (whole and half metres) and a reduction beyond 25 allocations
    + [("1400", "1600", "201"), ("1400", "1600", "202"), ("1400", "1600", "200.5"), ("2800", "3100", "303"), ("4400", "4700", "301.5"),
       ("1400", "1600", "170")]
    # three bands: excesses and reductions (every one beyond 25 allocations except the smallest)
    + [("1497", "3003", str(1506 + d)) for d in (1, 2, 9, 15, -1, -3, -8)] + [("1480", "3020", "1530"), ("1480", "3020", "1525")]
)


@pytest.mark.parametrize("f, t, allowed", SCENARIOS)
def test_b2_falsification_crossing_charges(f, t, allowed):
    """Branches no reference case exercises: 2-3 bands, reductions and excesses, whole and decimal metres, listed and
    bounded domains. The engine's domain equals a brute-force enumeration (count, and the listed allocations or the
    extremes) and X3 accepts it."""
    f, t, allowed = Decimal(f), Decimal(t), Decimal(allowed)
    c = copy.deepcopy(gcc.load_cases()["DDS-S72"])
    c["line"].update(quantity=str(allowed), depth_from_m=str(f), depth_to_m=str(t))
    c["report"] = c["report"].replace("Depth start (m MD): 1450", f"Depth start (m MD): {f}").replace("Depth end (m MD): 1550", f"Depth end (m MD): {t}")
    r = gcc.engine_result(c)
    assert r.payable and r.allowed_quantity == allowed
    parts = [(b, pa, pb, pb - pa, rt) for b, pa, pb, rt in g3_dds.pd210_parts(f, t, DT)]
    every = _brute(parts, allowed, g3_dds.pd210_step(allowed, f, t))
    dom = next(x for x in r.conditions if x["dimension"] == "tolerance")["domain"]
    assert dom["count"] == len(every) and dom["mode"] == ("enumerated" if len(every) <= 25 else "bounds")
    if dom["mode"] == "enumerated":
        assert _allocs(r) == every
    else:
        amt = lambda qs: sum(((q * p[4]).quantize(Decimal("0.01"), rounding="ROUND_HALF_EVEN") for q, p in zip(qs, parts)), Decimal(0))  # noqa: E731
        assert sorted(a["amount"] for a in r.alternatives.values()) == [min(map(amt, every)), max(map(amt, every))]
    assert _x3(r) == []


def test_b2_scenarios_cover_every_branch():
    kinds = set()
    for f, t, a in SCENARIOS:
        f, t, a = Decimal(f), Decimal(t), Decimal(a)
        n = len(g3_dds.pd210_parts(f, t, DT))
        parts = [(b, pa, pb, pb - pa, rt) for b, pa, pb, rt in g3_dds.pd210_parts(f, t, DT)]
        big = len(_brute(parts, a, g3_dds.pd210_step(a, f, t))) > 25
        kinds.add((n, "excess" if a > t - f else "reduction", "decimal" if a % 1 else "whole", "bounds" if big else "listed"))
    assert {(2, "excess", "whole", "listed"), (2, "excess", "decimal", "listed"), (2, "reduction", "whole", "listed"),
            (2, "reduction", "decimal", "listed"), (2, "reduction", "whole", "bounds"), (3, "excess", "whole", "bounds"),
            (3, "reduction", "whole", "bounds"), (3, "reduction", "whole", "listed")} <= kinds


def test_b2_four_bands_checked_by_x3_independent_count():
    """1,400-4,600 m spans all four bands; brute force is too large here, so the engine's dynamic programme is checked
    against X3's inclusion-exclusion count and vertex extremes (independent methods)."""
    c = copy.deepcopy(gcc.load_cases()["DDS-S72"])
    c["line"].update(quantity="3195", depth_from_m="1400", depth_to_m="4600")
    c["report"] = c["report"].replace("Depth start (m MD): 1450", "Depth start (m MD): 1400").replace("Depth end (m MD): 1550", "Depth end (m MD): 4600")
    r = gcc.engine_result(c)
    dom = next(x for x in r.conditions if x["dimension"] == "tolerance")["domain"]
    assert (dom["mode"], dom["count"], len(dom["parts"])) == ("bounds", 56, 4)       # C(5 + 3, 3): 5 m short over 4 bands
    assert _x3(r) == []
    bad = copy.deepcopy(r)
    next(x for x in bad.conditions if x["dimension"] == "tolerance")["domain"]["count"] = 55
    assert any("bounds without the whole domain stated" in e for e in _x3(bad))


# ---------------------------------------------------------------------------------------------------- D8 record
import csv  # noqa: E402
import json  # noqa: E402
import re  # noqa: E402
import subprocess  # noqa: E402

from audit.common import SNAPSHOT  # noqa: E402


def _x4(**over):
    args = {"decisions": yaml.safe_load((ROOT / "spec/g3_decisions.yaml").read_text()),
            "scopes": json.loads((ROOT / "verification/g3/decision_scopes.json").read_text()),
            "questions": yaml.safe_load((ROOT / "spec/open_questions.yaml").read_text()),
            "carried": yaml.safe_load((ROOT / "spec/carried_items.yaml").read_text()),
            "comparison": json.loads((ROOT / "verification/g3/case_comparison.json").read_text())}
    for k, f in over.items():
        f(args[k])
    return vg.x4(**args)


def _d8(qs):
    return next(d for d in qs["decisions"] if d["id"] == "D8")


def test_d8_is_an_interpretation_with_the_broader_reading_live_and_weighted():
    d8 = _d8(yaml.safe_load((ROOT / "spec/open_questions.yaml").read_text()))
    it = next(i for i in d8["interpretations"] if i["id"] == "D8-I1")
    rd = {r["id"]: r for r in it["readings"]}
    assert set(rd) == {"broader", "narrower"} and it["status"] == "open" and it["owner"] == "G5"
    assert "Schedule 8 is a Schedule" in rd["broader"]["reading"] and rd["broader"]["weight"].startswith("greater")
    # the round-1 categorical statement is no longer the settled reading; operability only is settled
    assert "does not by its own terms rank" not in d8["settled_reading"] and "D8-I1" in d8["settled_reading"]
    assert "settles operability only" in d8["settled_reading"]
    q5 = next(d for d in yaml.safe_load((ROOT / "spec/g3_decisions.yaml").read_text())["decisions"] if d["id"] == "Q5")
    assert q5["status"] == "decided in part" and "D8-I1" in json.dumps(q5["basis"])
    assert _x4() == []


def test_d8_control_x4_rejects_dropping_the_broader_reading_or_its_weight():
    def drop(qs):
        it = _d8(qs)["interpretations"][0]
        it["readings"] = [r for r in it["readings"] if r["id"] != "broader"]
    assert any("D8/D8-I1: interpretation without two or more readings" in e for e in _x4(questions=drop))

    def unweighted(qs):
        next(r for r in _d8(qs)["interpretations"][0]["readings"] if r["id"] == "broader").pop("weight")
    assert any("D8/D8-I1: interpretation without two or more readings" in e for e in _x4(questions=unweighted))

    def settled(qs):
        _d8(qs)["interpretations"][0]["status"] = "decided"
    assert any("D8/D8-I1: interpretation not open with a later owner" in e for e in _x4(questions=settled))


def test_d8_control_x4_rejects_q5_decided_or_not_citing_the_interpretation():
    def uncited(ds):
        q5 = next(d for d in ds["decisions"] if d["id"] == "Q5")
        q5["basis"] = [b.replace("D8-I1", "D8") for b in q5["basis"]]
    assert any("decision Q5 does not cite the interpretation" in e for e in _x4(decisions=uncited))

    def decided(ds):
        next(d for d in ds["decisions"] if d["id"] == "Q5")["status"] = "decided"
    assert any("decision Q5 is fully decided although it depends on an open interpretation" in e for e in _x4(decisions=decided))


def test_q5_residual_still_carried_as_scoped_alternatives(res):
    q5 = {r.line_ref: r for r in res["DDS"].values() if any(c["dimension"].startswith("Q5-") for c in r.conditions)}
    assert {k: v.code for k, v in q5.items()} == {"MDS-00856-039": "RM-530", "MDS-01338-026": "RM-530", "MDS-01651-025": "DD-120"}
    assert all(v.amount is None and v.alternatives for v in q5.values())


SERVICE = re.compile(r"\b(?:[A-Z]{2}-\d{3})\b")
LINE = re.compile(r"\bMDS-\d{5}-\d{3}\b")


def report_identity_errors(text: str) -> list[str]:
    """Every drilling line named in a report sentence with a service code must be that service in the source invoice
    lines: each line reference is paired with the next service code on the same line of text (round 2: the round-1
    report swapped DD-120 and RM-530 in its Q5 summary)."""
    with (SNAPSHOT / "drilling_services/invoices/invoice_lines.csv").open(newline="") as fh:
        src = {r["line_ref"]: r["service_code"] for r in csv.DictReader(fh)}
    errs = []
    for ln in text.splitlines():
        pending = []
        for m in re.finditer(rf"{LINE.pattern}|{SERVICE.pattern}", ln):
            tok = m.group(0)
            if tok.startswith("MDS-"):
                pending.append(tok)
            elif pending:
                errs += [f"{ref} named as {tok}, source {src.get(ref)}" for ref in pending if src.get(ref) != tok]
                pending = []
    return errs


def test_report_line_identities_match_the_source():
    for name in ("Phase3_G3_corrections.md", "Phase3_G3_corrections_r2.md"):
        p = ROOT / name
        if p.exists():
            assert report_identity_errors(p.read_text()) == [], name


def test_report_identity_control_rejects_the_round1_text():
    old = subprocess.run(["git", "show", "83c4a61:Phase3_G3_corrections.md"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    errs = report_identity_errors(old)
    assert "MDS-00856-039 named as DD-120, source RM-530" in errs and "MDS-01651-025 named as RM-530, source DD-120" in errs
