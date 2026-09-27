"""G3 correction round 3 (re-audit Phase3_G3_reaudit_r2_Agent2.md, section 6): a PD-210 charge without its depths - start
only, end only, or both - returns an explicit missing-depth finding and an owned unresolved result, through the case
path, the typed G2 handoff (the real claims loader on a CSV with the cells blank) and the batch; the batch carries on;
the unguarded engine of gate3-r2 (3c308ab) fails the same controls."""
import copy
import csv
import io
import subprocess
import types
from decimal import Decimal
from pathlib import Path

import pytest

import g3_case_compare as gcc
import verify_g3 as vg
from audit import build, g3_dds
from audit.common import SNAPSHOT

ROOT = Path(__file__).resolve().parents[1]
OLD = "3c308ab"                                  # gate3-r2: the audited, unguarded engine
LINES = "drilling_services/invoices/invoice_lines.csv"
PROBES = {"MDS-00018-023": ("depth_from_m",), "MDS-00018-039": ("depth_to_m",), "MDS-00018-054": ("depth_from_m", "depth_to_m")}


def old_module(name: str):
    """The module as committed at gate3-r2, executed inside the audit package (its relative imports resolve)."""
    src = subprocess.run(["git", "show", f"{OLD}:audit/{name}.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType(f"audit._old_{name}")
    mod.__package__ = "audit"
    exec(compile(src, f"{OLD}:audit/{name}.py", "exec"), mod.__dict__)
    return mod


def snapshot_with(root: Path, rel: str, edit) -> Path:
    """A copy of the pinned snapshot (symlinks) in which one file is replaced by edit(text)."""
    for p in SNAPSHOT.rglob("*"):
        r = p.relative_to(SNAPSHOT)
        if ".git" in r.parts:
            continue
        dst = root / r
        if p.is_dir():
            dst.mkdir(parents=True, exist_ok=True)
            continue
        dst.parent.mkdir(parents=True, exist_ok=True)
        if str(r) == rel:
            dst.write_text(edit(p.read_text(encoding="utf-8")), encoding="utf-8")
        else:
            dst.symlink_to(p)
    return root


def blank_depths(text: str) -> str:
    rows = list(csv.DictReader(io.StringIO(text)))
    for r in rows:
        for f in PROBES.get(r["line_ref"], ()):
            r[f] = ""
    out = io.StringIO()
    w = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    w.writeheader()
    w.writerows(rows)
    return out.getvalue()


@pytest.fixture(scope="module")
def base():
    w = build.build()
    return w, g3_dds.run(w)


@pytest.fixture(scope="module")
def blanked(tmp_path_factory):
    snap = snapshot_with(tmp_path_factory.mktemp("snap"), LINES, blank_depths)
    w = build.build(snap)
    return w, g3_dds.run(w)


def _case(**line):
    c = copy.deepcopy(gcc.load_cases()["DDS-S72"])
    c["line"].update(line)
    return c


def _explicit_unresolved(r, gone):
    assert r.amount_status == "unresolved" and r.payable is None
    assert r.amount is None and r.allowed_quantity is None and not r.alternatives          # no value guessed, no zero
    assert not [s for s in r.trace if s["op"] in ("part", "amount", "sum_parts")]
    assert "depths_missing" in r.findings
    named = {c.detail.split(":")[0] for c in r.checks if c.check == "input" and c.finding == "depths_missing"}
    assert named == set(gone)
    assert any(c["dimension"] == "input" and c["owner"] == "G5" and "Cl.34" in c["basis"] for c in r.conditions)
    assert any("not guessed from the report, not zero" in x for x in r.reasons)


# ---------------------------------------------------------------------------------------------------- case path
@pytest.mark.parametrize("gone", [("depth_from_m",), ("depth_to_m",), ("depth_from_m", "depth_to_m")])
def test_missing_depths_case_path(gone):
    """The re-audit's probe (DDS-S72 with depth_from_m = None) and its end-only and both-missing companions."""
    r = gcc.engine_result(_case(**{g: None for g in gone}))
    _explicit_unresolved(r, gone)
    # what holds for every interval inside the report's 1,450-1,550 m is kept
    assert any("the report measures 1450-1550 m, 100 m drilled on the day" in x for x in r.readings)
    assert vg.x3({"DDS": {"case": r}}) == []


def test_missing_depths_keeps_findings_that_hold_for_every_interval():
    """A charge above the day's metres is above the report whatever depths it would state (25A); a report inside one band
    fixes the rate whatever the interval (Cl.23). Both stay findings although the value is unresolved."""
    c = copy.deepcopy(gcc.load_cases()["DDS-S68"])                     # report 2,900-3,000 m: band 2 only
    c["line"].update(depth_from_m=None, quantity="150", unit_rate="76.45", amount="11467.50")
    r = gcc.engine_result(c)
    _explicit_unresolved(r, ("depth_from_m",))
    assert {"quantity_above_report", "rate_differs"} <= set(r.findings)
    ok = copy.deepcopy(gcc.load_cases()["DDS-S68"])
    ok["line"].update(depth_to_m=None, quantity="100", unit_rate="58.15", amount="5815.00")
    r2 = gcc.engine_result(ok)
    _explicit_unresolved(r2, ("depth_to_m",))
    assert not {"quantity_above_report", "rate_differs"} & set(r2.findings)


def test_missing_depths_established_consequences_still_stand():
    """Not a performance section: not payable whatever the depths (Cl.23; App A) - an established fact, not a guess."""
    c = _case(depth_from_m=None)
    c["report"] = c["report"].replace('Hole section: 12-1/4"', 'Hole section: 17-1/2"')
    c["line"]["hole_section"] = '17-1/2"'
    r = gcc.engine_result(c)
    assert r.amount_status == "not_payable" and "not_performance_section" in r.findings


# ---------------------------------------------------------------------------------------------------- typed G2 handoff + batch
def test_missing_depths_through_the_g2_loader_and_the_batch(base, blanked):
    """The CSV cells blanked in a copy of the snapshot: the real G2 loader types them None and queues them ('required field
    blank', CW/DDS plan §4); the production batch g3_dds.run carries on and gives each probe line an explicit owned
    unresolved result with its source line; every other drilling line is unchanged."""
    w0, res0 = base
    w1, res1 = blanked
    queued = {(u.ident, u.field) for u in w1.queue.items if u.kind == "dds_lines"}
    for ref, gone in PROBES.items():
        row = next(x for x in w1.claims.rows["dds_lines"] if x.ident == ref)
        assert all(row.values[g] is None for g in gone)
        assert all((ref, g) in queued for g in gone)
        r = res1[ref]
        _explicit_unresolved(r, gone)
        src = f"{LINES}:{row.source.line}"
        assert all(src in c.detail for c in r.checks if c.check == "input")                 # provenance
    assert len(res1) == len(res0) == 91244
    changed = [ref for ref in res0 if ref not in PROBES and
               {k: v for k, v in res0[ref].to_json().items() if k != "ctx"} != {k: v for k, v in res1[ref].to_json().items() if k != "ctx"}]
    assert changed == []
    assert vg.x3({"DDS": {ref: res1[ref] for ref in PROBES}}) == []


def test_mds_00018_023_start_depth_none_in_the_population_batch(base):
    """The re-audit's second probe exactly: the typed start depth of MDS-00018-023 set to None in memory, then the
    production batch."""
    w, res0 = base
    row = next(x for x in w.claims.rows["dds_lines"] if x.ident == "MDS-00018-023")
    keep = row.values["depth_from_m"]
    row.values["depth_from_m"] = None
    try:
        res = g3_dds.run(w)
    finally:
        row.values["depth_from_m"] = keep
    _explicit_unresolved(res["MDS-00018-023"], ("depth_from_m",))
    assert len(res) == len(res0)


# ---------------------------------------------------------------------------------------------------- controls
@pytest.mark.parametrize("gone", [("depth_from_m",), ("depth_to_m",), ("depth_from_m", "depth_to_m")])
def test_control_the_old_engine_fails_the_case_path(gone, monkeypatch):
    old = old_module("g3_dds")
    monkeypatch.setattr(gcc, "g3_dds", old)
    with pytest.raises(TypeError):
        gcc.engine_result(_case(**{g: None for g in gone}))


def test_control_the_old_engine_stops_the_batch(blanked):
    w1, _ = blanked
    with pytest.raises(TypeError):
        old_module("g3_dds").run(w1)


def test_control_x3_rejects_a_contained_engine_error(base):
    w, _ = base
    line = next(x for x in w.claims.rows["dds_lines"] if x.ident == "MDS-00018-023").values
    r = g3_dds.engine_error(line, "MDS-00018-023", TypeError("boom"))
    assert any("engine error: TypeError: boom" in e for e in vg.x3({"DDS": {"MDS-00018-023": r}}))


def test_batch_contains_an_engine_error_and_carries_on(base, monkeypatch):
    """A defect on one line never stops the others: the batch records it as an explicit engine_error (which X3 rejects)."""
    w, res0 = base
    real = g3_dds.evaluate

    def broken(line, inv, ddr, **kw):
        if line["line_ref"] == "MDS-00018-023":
            raise TypeError("injected")
        return real(line, inv, ddr, **kw)
    monkeypatch.setattr(g3_dds, "evaluate", broken)
    res = g3_dds.run(w)
    assert res["MDS-00018-023"].amount_status == "unresolved" and "engine_error" in res["MDS-00018-023"].unresolved
    assert len(res) == len(res0) and res["MDS-00018-039"].amount == res0["MDS-00018-039"].amount


# ---------------------------------------------------------------------------------------------------- X8 nullable sweep
import yaml  # noqa: E402

import null_sweep as ns  # noqa: E402
from audit import g3_cw  # noqa: E402


@pytest.fixture(scope="module")
def both(base):
    w, dds = base
    return w, {"CW": g3_cw.run(w), "DDS": dds}


@pytest.fixture(scope="module")
def old_x8(both):
    w, res = both
    return ns.x8(w, res, ns.Engines(old_module("g3_cw"), old_module("g3_dds")))


def test_x8_passes_on_every_code_family(both):
    w, res = both
    stats = {}
    assert vg.x8(w, res, stats=stats) == []
    fams = yaml.safe_load((ROOT / "spec/g3_code_families.yaml").read_text())["contracts"]
    want = {f"{c} family {f['id']}" for c, fs in fams.items() for f in fs}
    assert want == {k for k in stats if " family " in k}                      # all 18 families, incl. no-billed-line ones
    assert stats["mutations"] > 9000 and stats["batch_runs"] > 190
    assert stats["explicit_unresolved"] > 1000 and stats["registered"] > 100 and stats["irrelevant_unchanged"] > 5000


def test_x8_control_the_gate3_r2_engine_fails(old_x8):
    """The engine the re-audit tested: exceptions (the PD-210 depths among them), rejections without a contract rule,
    and a batch that stops."""
    errs, stats = old_x8
    assert stats["exceptions"] > 900 and stats["silent"] > 1000
    assert any("depth_from_m" in e and "exception TypeError" in e for e in errs)
    assert any("CW" in e and " unit=" in e and "not payable without the contract's own rule" in e for e in errs)
    assert any(e.startswith("DDS batch with line depth_from_m empty: exception TypeError") for e in errs)


def _cw_variant(evaluate, run=None):
    m = types.SimpleNamespace(evaluate=evaluate, input_context=g3_cw.input_context, inputs_from_world=g3_cw.inputs_from_world)

    def default_run(w):
        ctx, out = g3_cw.input_context(w), {}
        for row, (line, app, rec, ex) in zip(w.claims.rows["cw_lines"], g3_cw.inputs_from_world(w)):
            r = evaluate(line, app, rec, ex, inputs=ctx[row.ident])
            out[r.line_ref or row.ident] = r
        return out
    m.run = run or default_run
    return m


def _x8_with(both, cw_mod):
    w, res = both
    return ns.x8(w, res, ns.Engines(cw_mod, g3_dds))[0]


def test_x8_control_a_silently_defaulted_zone(both):
    def zone_z1(line, app, record, exists, band_pct=None, T=None, inputs=None):
        if not (line.get("site_zone") or "").strip():
            line = {**line, "site_zone": "Z1 Compound"}                          # the default X8 must catch
        return g3_cw.evaluate(line, app, record, exists, band_pct=band_pct, T=T, inputs=inputs)
    errs = _x8_with(both, _cw_variant(zone_z1))
    assert any("site_zone" in e and "does not name it (silent)" in e for e in errs)


def test_x8_control_a_named_default_is_still_a_default(both):
    def zone_z1_named(line, app, record, exists, band_pct=None, T=None, inputs=None):
        blank = not (line.get("site_zone") or "").strip()
        r = g3_cw.evaluate({**line, "site_zone": "Z1 Compound"} if blank else line, app, record, exists, band_pct=band_pct, T=T, inputs=inputs)
        if blank:
            r.readings.append("site_zone not stated: taken as Z1")
        return r
    errs = _x8_with(both, _cw_variant(zone_z1_named))
    assert any("site_zone" in e and "fixes a value" in e for e in errs)


def test_x8_control_an_overcautious_engine_loses_a_known_value(both):
    def overcautious(line, app, record, exists, band_pct=None, T=None, inputs=None):
        r = g3_cw.evaluate(line, app, record, exists, band_pct=band_pct, T=T, inputs=inputs)
        if app is not None and not (app.get("contract_ref") or "").strip():
            r.amount_status, r.payable, r.amount, r.allowed_quantity, r.unit_rate, r.alternatives = "unresolved", None, None, None, None, {}
        return r
    errs = _x8_with(both, _cw_variant(overcautious))
    assert any("contract_ref" in e and "a known value lost" in e for e in errs)


def test_x8_control_a_batch_that_drops_lines(both):
    def dropping_run(w):
        return {k: r for k, r in g3_cw.run(w).items()
                if next(x for x in w.claims.rows["cw_lines"] if x.ident == k).values.get("quantity") is not None}
    errs = _x8_with(both, _cw_variant(g3_cw.evaluate, dropping_run))
    assert any("CW batch with line quantity empty" in e and "results for" in e for e in errs)


def test_x8_control_a_batch_that_is_not_the_direct_evaluation(both):
    def provenance_lost_run(w):
        out = {}
        for row, (line, app, rec, ex) in zip(w.claims.rows["cw_lines"], g3_cw.inputs_from_world(w)):
            r = g3_cw.evaluate(line, app, rec, ex)                               # G2's provenance dropped on the way
            out[r.line_ref or row.ident] = r
        return out
    errs = _x8_with(both, _cw_variant(g3_cw.evaluate, provenance_lost_run))
    assert any("differs from its direct evaluation" in e for e in errs)
