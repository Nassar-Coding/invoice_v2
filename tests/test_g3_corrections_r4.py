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
    indexed = d2 if d2.report == line.get("report_ref") else None       # G2 indexes reports by their Report number
    if engine is g3_dds:
        ctx = g3_dds.input_context(w)[ref]
        inp = replace(ctx, doc_gaps=frozenset(u.field for u in mine), unindexed_reports=d2.report is None,
                      doc_repeated=frozenset(u.field for u in mine if u.reason == "key repeated"))
        return engine.evaluate(line, inv, indexed, inputs=inp), q
    return engine.evaluate(line, inv, indexed), q


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


# ============================================================================================ FD02 repeated evidence
def _insert_before(key, line):
    return lambda t: t.replace(f"\n{key}:", f"\n{line}\n{key}:", 1)


def _insert_after(key, line):
    def f(t):
        ls = t.split("\n")
        i = next(j for j, x in enumerate(ls) if x.startswith(key + ":"))
        return "\n".join(ls[:i + 1] + [line] + ls[i + 1:])
    return f


def _dup_part(p, mutate=lambda x: x):
    """The report with Part p written a second time (the copy passed through `mutate`, line by line)."""
    def f(t):
        ls = t.split("\n")
        i = next(j for j, x in enumerate(ls) if x.startswith(f"PART {p} "))
        j = i + 1
        while j < len(ls) and ls[j].strip() and not ls[j].startswith(("PART", "Signed")):
            j += 1
        return "\n".join(ls[:j] + [""] + [mutate(x) for x in ls[i:j]] + ls[j:])
    return f


ONE_HAND = lambda t: t.replace("2 directional hands", "1 directional hands", 1)  # noqa: E731


@pytest.mark.parametrize("order", [_insert_before, _insert_after])
def test_fd02_conflicting_header_date_is_unresolved_in_either_order(world, order):
    r, q = dds_eval(world, "MDS-00001-013", order("Date", "Date: 03-Jan-2025"))
    assert r.amount_status == "unresolved" and "report_date_mismatch" not in r.findings
    assert any(u.field == "Date" and u.reason == "key repeated" for u in q.items)


@pytest.mark.parametrize("key, other", [("Report", "DDR-194-20250103"), ("Well", "NGP-BD-195")])
def test_fd02_other_conflicting_header_keys(world, key, other):
    r, q = dds_eval(world, "MDS-00001-013", _insert_before(key, f"{key}: {other}"))
    assert r.amount_status == "unresolved" and any(u.field == key and u.reason == "key repeated" for u in q.items)


@pytest.mark.parametrize("order", [_insert_before, _insert_after])
@pytest.mark.parametrize("key", DDS_SIGS)
def test_fd02_conflicting_signature_lines_are_unknown(world, order, key):
    r, q = dds_eval(world, "MDS-00001-013", order(key, f"{key}: ____________________"))
    assert r.amount_status == "unresolved" and "report_unsigned" not in r.findings


@pytest.mark.parametrize("order", [_insert_before, _insert_after])
@pytest.mark.parametrize("key", CW_SIGS)
def test_fd02_conflicting_civil_signature_lines_are_unknown(world, order, key):
    r, q = cw_eval(world, "PA-00001-04", order(key, f"{key}: ____________________"))
    assert r.amount_status == "unresolved" and "record_unsigned" not in r.findings


def test_fd02_identical_repeats_are_read_once(world):
    """An identical repeated header line, signature or whole Part states one fact once: the value is the single copy's."""
    base, _ = dds_eval(world, "MDS-00001-013", lambda t: t)
    sig = next(x for x in ns.doc_text(_dds_line(world, "MDS-00001-013")[2]).split("\n") if x.startswith(DDS_SIGS[0]))
    for fn in (_insert_after("Date", "Date: 02-Jan-2025"), _insert_after(DDS_SIGS[0], sig),
               _dup_part("A"), _dup_part("B")):
        r, q = dds_eval(world, "MDS-00001-013", fn)
        assert (r.amount_status, r.amount) == (base.amount_status, base.amount) and not q.items


def test_fd02_repeated_part_a_does_not_count_the_crew_twice(world):
    """The audit's MDS-00001-010: Part A stating one directional hand supports quantity 1 (USD 1,847.35, the two-person
    claim above the record); the same Part A repeated identically is still one hand; a copy stating a different crew
    leaves the crew unresolved in either order."""
    one, _ = dds_eval(world, "MDS-00001-010", ONE_HAND)
    assert (one.allowed_quantity, one.amount) == (Decimal("1"), Decimal("1847.35")) and "quantity_above_report" in one.findings
    twice, q = dds_eval(world, "MDS-00001-010", lambda t: _dup_part("A")(ONE_HAND(t)))
    assert (twice.allowed_quantity, twice.amount, twice.findings) == (one.allowed_quantity, one.amount, one.findings)
    for fn in (lambda t: _dup_part("A", lambda x: x.replace("1 directional", "2 directional"))(ONE_HAND(t)),
               _dup_part("A", lambda x: x.replace("2 directional", "1 directional"))):
        r, q = dds_eval(world, "MDS-00001-010", fn)
        assert r.amount_status == "unresolved" and any(u.field == "A.Crew on tour" and u.reason == "key repeated" for u in q.items)


def test_fd02_civil_conflicting_key_in_either_order_and_identical_repeat(world):
    base, _ = cw_eval(world, "PA-00001-04", lambda t: t)
    date = next(x for x in ns.doc_text(_cw_line(world, "PA-00001-04")[2]).split("\n") if x.startswith("Date:"))
    for fn in (_insert_before("Date", "Date: 01/01/2025"), _insert_after("Date", "Date: 01/01/2025")):
        r, q = cw_eval(world, "PA-00001-04", fn)
        assert r.amount_status == "unresolved" and any(u.field == "Date" and u.reason == "key repeated" for u in q.items)
    r, q = cw_eval(world, "PA-00001-04", _insert_after("Date", date))
    assert (r.amount_status, r.amount) == (base.amount_status, base.amount) and not q.items


def test_fd02_control_gate3_r3(world, r3):
    """gate3-r3: a conflicting date prepended (original last) is silently resolved to the last - the line stays payable
    at USD 4,892.30 with no queue item; an unsigned line followed by a named one is signed; an identical Part A repeated
    doubles the crew (quantity 2, USD 3,694.70, no finding)."""
    r, q = dds_eval(world, "MDS-00001-013", _insert_before("Date", "Date: 03-Jan-2025"), engine=r3.g3_dds, parser=r3.records_dds)
    assert r.amount == Decimal("4892.30") and not q.items
    k = DDS_SIGS[0]
    r, q = dds_eval(world, "MDS-00001-013", _insert_before(k, f"{k}: ____________________"), engine=r3.g3_dds, parser=r3.records_dds)
    assert r.amount == Decimal("4892.30") and not q.items
    r, q = dds_eval(world, "MDS-00001-010", lambda t: _dup_part("A")(ONE_HAND(t)), engine=r3.g3_dds, parser=r3.records_dds)
    assert (r.allowed_quantity, r.amount, r.findings) == (Decimal("2"), Decimal("3694.70"), [])


# ============================================================================================ FD03 civil item attributes
# (claim, record narrative text in the record, attribute text, a different valid value, an unreadable value)
FD03 = [
    ("PA-00002-07", "1800 dia", "1200 dia", "?? dia"),                    # PT1 precast chamber diameter, C.32.030
    ("PA-00002-09", "400 ductile", "600 ductile", "4OO ductile"),         # PT2 ductile main diameter, C.31.020
    ("PA-00001-10", "32/40 mix", "20/25 mix", "32/?? mix"),               # PR1 wall mix, B.21.040
    ("PA-00003-07", "A393 mesh", "A142 mesh", "A3?3 mesh"),               # JS1 mesh, B.23.020
    ("PA-00008-06", "of Type 1", "of Type 2", "of Type ?"),               # CT4 sub-base type, D.41.010
]


def _narrative(w, ref, old, new):
    rec = _cw_line(w, ref)[2]
    assert old in ns.doc_text(rec), (ref, old)
    return lambda t: t.replace(old, new, 1)


@pytest.mark.parametrize("ref, same, other, unreadable", FD03)
def test_fd03_each_attribute_role_matching_different_unreadable(world, ref, same, other, unreadable):
    base, _ = cw_eval(world, ref, lambda t: t)
    r, q = cw_eval(world, ref, _narrative(world, ref, same, same))
    assert (r.amount_status, r.amount, r.findings) == (base.amount_status, base.amount, base.findings) and not q.items
    r, q = cw_eval(world, ref, _narrative(world, ref, same, other))       # a different valid specification
    assert r.amount_status == "not_payable" and "item_not_supported_by_record" in r.findings and not q.items
    assert "Schedule 1" in next(c.detail for c in r.checks if c.finding == "item_not_supported_by_record")
    assert not r.alternatives                                            # never repriced as another item
    r, q = cw_eval(world, ref, _narrative(world, ref, same, unreadable))  # unreadable: the narrative is not established
    assert r.amount_status == "unresolved" and any(u.field == "narrative" for u in q.items)


# every PR template variant: the concrete grade of each pour record form
PR_VARIANTS = [("wall pour 12 m3, 32/40 mix", "B.21.040"), ("slab pour 12 m3, 32/40", "B.21.030"),
               ("poured 12 m3 into the foundations, 32/40 mix", "B.21.020"), ("poured the slab, 12 cube of C32/40", "B.21.030"),
               ("foundation pour 12 cube, C32/40 off the truck", "B.21.020")]


@pytest.mark.parametrize("narrative, item", PR_VARIANTS)
@pytest.mark.parametrize("grade, ok", [("32/40", True), ("20/25", False), ("40/50", False)])
def test_fd03_every_pour_record_variant(narrative, item, grade, ok):
    text = f"CONCRETE POUR RECORD\nTicket: PR-99999\nJob: J\nArea: S-01 Platform North\nDate: 01/02/2025\n\n" \
           f"{narrative.replace('32/40', grade)}\n\nSigned (foreman): A. Foreman\nCountersigned (Engineer's representative): B. Engineer\n"
    q = Queue()
    r = records_cw.parse_file("civilwork/records/PR-99999.txt", text, q)
    assert not q.items and r.rule and (r.candidates == [item]) == ok and bool(r.spec_mismatch) != ok


def test_fd03_control_gate3_r3_ignores_the_specification(world, r3):
    """The audit's table: on gate3-r3 each changed specification keeps its candidate and its value."""
    for ref, same, other, _u in FD03:
        base, _ = cw_eval(world, ref, lambda t: t, engine=r3.g3_cw, parser=r3.records_cw)
        r, q = cw_eval(world, ref, _narrative(world, ref, same, other), engine=r3.g3_cw, parser=r3.records_cw)
        assert (r.amount_status, r.amount, r.findings) == (base.amount_status, base.amount, base.findings) and not q.items
