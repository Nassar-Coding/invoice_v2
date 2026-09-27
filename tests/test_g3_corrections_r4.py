"""G3 correction round 4 (final discovery audit Phase3_G3_final_discovery_audit_Agent2.md, FD01-FD08).

Every test runs the real G2 parsers on mutated source text (records, reports, claim CSV rows) and the G3 engines on
what G2 hands over. Each negative control runs the gate3-r3 code (6885224) - its G2 parsers with their own helpers and
its engines - on the same input and shows the defect the audit reproduced."""
import copy
import subprocess
import sys
import types
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

import pytest

import g3_case_compare as gcc
import null_sweep as ns
from audit import build, g3_cw, g3_dds, records_cw, records_dds
from audit.common import Queue

ROOT = Path(__file__).resolve().parents[1]
R3 = "6885224"                                    # gate3-r3: the audited code


def r3_module(name: str, patch: dict | None = None):
    """audit/<name>.py as committed at gate3-r3, executed inside the audit package; `patch` replaces module globals
    (the gate3-r3 helpers it imported from modules this round changed)."""
    src = subprocess.run(["git", "show", f"{R3}:audit/{name}.py"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    mod = types.ModuleType(f"audit._r3_{name}")
    mod.__package__ = "audit"
    mod.__file__ = str(ROOT / "audit" / f"{name}.py")
    sys.modules[mod.__name__] = mod                                  # dataclasses resolve their module
    exec(compile(src, f"{R3}:audit/{name}.py", "exec"), mod.__dict__)
    mod.__dict__.update(patch or {})
    return mod


@pytest.fixture(scope="module")
def r3():
    common = r3_module("common")
    rec_dds = r3_module("records_dds", {"is_signature": common.is_signature})
    rec_cw = r3_module("records_cw", {"is_signature": common.is_signature})
    return types.SimpleNamespace(common=common, records_dds=rec_dds, records_cw=rec_cw,
                                 g3_dds=r3_module("g3_dds"), g3_cw=r3_module("g3_cw"))


@pytest.fixture(scope="module")
def world():
    return build.build()


def _dds_line(w, ref):
    row = next(x for x in w.claims.rows["dds_lines"] if x.ident == ref)
    inv = {h.ident: h.values for h in w.claims.rows["dds_headers"]}[row.values["invoice_no"]]
    return row.values, inv, w.ddr[row.values["report_ref"]]


def _cw_line(w, ref):
    row = next(x for x in w.claims.rows["cw_lines"] if x.ident == ref)
    app = {h.ident: h.values for h in w.claims.rows["cw_headers"]}[row.values["application_no"]]
    return row.values, app, w.cw[row.values["record_ref"]]


def dds_eval(w, ref, text_fn, engine=g3_dds, parser=records_dds):
    """The line evaluated on its report after text_fn(report text), re-parsed by `parser` with a fresh G2 queue."""
    line, inv, ddr = _dds_line(w, ref)
    q = Queue()
    d2 = parser.parse_file(ddr.path, text_fn(ns.doc_text(ddr)), q)
    mine = [u for u in q.items if u.ident == d2.file]
    if engine is g3_dds:
        ctx = g3_dds.input_context(w)[ref]
        inp = replace(ctx, doc_gaps=frozenset(u.field for u in mine),
                      doc_repeated=frozenset(u.field for u in mine if u.reason == "key repeated"))
        return engine.evaluate(line, inv, d2, inputs=inp), q
    return engine.evaluate(line, inv, d2), q


def cw_eval(w, ref, text_fn, engine=g3_cw, parser=records_cw, line_patch=None):
    line, app, rec = _cw_line(w, ref)
    line = {**line, **(line_patch or {})}
    q = Queue()
    r2 = parser.parse_file(rec.path, text_fn(ns.doc_text(rec)), q)
    mine = [u for u in q.items if u.ident == r2.ticket]
    if engine is g3_cw:
        ctx = g3_cw.input_context(w)[ref]
        inp = replace(ctx, doc_gaps=frozenset(u.field for u in mine),
                      doc_repeated=frozenset(u.field for u in mine if u.reason == "key repeated"))
        return engine.evaluate(line, app, r2, True, inputs=inp), q
    return engine.evaluate(line, app, r2, True), q


def swap(key, value):
    return lambda t: ns._swap_value(t, key, value)


# ============================================================================================ FD01 signatures
DDS_SIGS = ["Signed (Company Representative)", "Signed (lead directional driller)"]
CW_SIGS = ["Signed (foreman)", "Countersigned (Engineer's representative)"]
UNKNOWN = ["??", "illegible", "12345", "x", "Signed", "Pending Review"]
UNSIGNED = ["unsigned", "N/A", "pending", "not signed", "TBC", "____________________", ""]


@pytest.mark.parametrize("key", DDS_SIGS)
@pytest.mark.parametrize("token", UNKNOWN)
def test_fd01_dds_unreadable_signature_is_unresolved(world, key, token):
    r, q = dds_eval(world, "MDS-00001-013", swap(key, token))
    assert r.amount_status == "unresolved" and r.amount is None and r.payable is None
    assert any(c.check == "input" and c.detail.startswith(key) for c in r.checks)
    assert any(u.field == key and "does not establish a signature" in u.reason for u in q.items)
    assert "report_unsigned" not in r.findings


@pytest.mark.parametrize("key", DDS_SIGS)
@pytest.mark.parametrize("token", UNSIGNED)
def test_fd01_dds_non_signing_text_is_unsigned(world, key, token):
    r, _ = dds_eval(world, "MDS-00001-013", swap(key, token))
    assert r.amount_status == "not_payable" and "report_unsigned" in r.findings


@pytest.mark.parametrize("key", CW_SIGS)
@pytest.mark.parametrize("token", UNKNOWN)
def test_fd01_cw_unreadable_signature_is_unresolved(world, key, token):
    r, q = cw_eval(world, "PA-00001-04", swap(key, token))
    assert r.amount_status == "unresolved" and r.amount is None
    assert any(u.field == key and "does not establish a signature" in u.reason for u in q.items)
    assert "record_unsigned" not in r.findings


@pytest.mark.parametrize("key", CW_SIGS)
@pytest.mark.parametrize("token", UNSIGNED)
def test_fd01_cw_non_signing_text_is_unsigned(world, key, token):
    r, _ = cw_eval(world, "PA-00001-04", swap(key, token))
    assert r.amount_status == "not_payable" and "record_unsigned" in r.findings


def test_fd01_real_names_still_sign(world):
    r, q = dds_eval(world, "MDS-00001-013", swap(DDS_SIGS[0], "M. Al-Harbi"))
    assert r.amount == Decimal("4892.30") and not q.items
    r, q = cw_eval(world, "PA-00001-04", swap(CW_SIGS[1], "N. Basri"))
    assert r.amount == Decimal("17730.62")


def _s64_with_countersignature(value):
    c = copy.deepcopy(gcc.load_cases()["CW-S64"])
    c["record"] = ns._swap_value(c["record"], "Countersigned (Engineer's representative)", value)
    return c


def test_fd01_ground_authority_needs_an_established_countersignature():
    """CW-S64 (A.12.020, no Schedule 5 record needed, citing a record of the same day, area and work): a countersignature
    that is a name settles G3; '??' does not establish the Engineer's classification - every class is carried, named."""
    assert gcc.engine_result(_s64_with_countersignature("N. Basri")).amount_status == "determined"
    r = gcc.engine_result(_s64_with_countersignature("??"))
    assert r.amount is None and {k.split(":")[1] for k in r.alternatives} == {"G1", "G2", "G3", "G4", "G5"}
    assert any("does not establish a countersignature" in x for x in r.readings)


def test_fd01_control_gate3_r3_promotes_unreadable_text_to_approval(world, r3):
    """The audit's reproductions on the gate3-r3 parser and engine: '??' in either required signature leaves MDS-00001-013
    payable at USD 4,892.30 and PA-00001-04 at SAR 17,730.62, with no finding, condition or queue item."""
    for key in DDS_SIGS:
        r, q = dds_eval(world, "MDS-00001-013", swap(key, "??"), engine=r3.g3_dds, parser=r3.records_dds)
        assert r.amount == Decimal("4892.30") and r.amount_status == "determined" and not q.items
    r, q = cw_eval(world, "PA-00001-04", swap(CW_SIGS[1], "??"), engine=r3.g3_cw, parser=r3.records_cw)
    assert r.amount == Decimal("17730.62") and not q.items
    c = _s64_with_countersignature("??")
    rec = r3.records_cw.parse_file(f"civilwork/records/{c['line']['record_ref']}.txt", c["record"], Queue())
    assert rec.engineer_signed                                        # gate3-r3: '??' is the Engineer's approval
