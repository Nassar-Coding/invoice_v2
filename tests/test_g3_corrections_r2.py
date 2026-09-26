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
