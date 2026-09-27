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


_CTX = {}


def _ctx(w, c):
    """G2's input context for the world (computed once per world and contract)."""
    if (id(w), c) not in _CTX:
        _CTX[(id(w), c)] = (g3_dds if c == "DDS" else g3_cw).input_context(w)
    return _CTX[(id(w), c)]


def dds_eval(w, ref, text_fn, engine=g3_dds, parser=records_dds):
    """The line evaluated on its report after text_fn(report text), re-parsed by `parser` with a fresh G2 queue."""
    line, inv, ddr = _dds_line(w, ref)
    q = Queue()
    d2 = parser.parse_file(ddr.path, text_fn(ns.doc_text(ddr)), q)
    mine = [u for u in q.items if u.ident == d2.file]
    indexed = d2 if d2.report == line.get("report_ref") else None       # G2 indexes reports by their Report number
    if engine is g3_dds:
        ctx = _ctx(w, "DDS")[ref]
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
        ctx = _ctx(w, "CW")[ref]
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


# ============================================================================================ FD04 required Parts
SCH5_LINES = {'DD-130': 'MDS-00001-013', 'DD-111': 'MDS-00001-021', 'RM-510': 'MDS-00018-026', 'LH-712': 'MDS-00018-033',
              'LW-410': 'MDS-00043-053', 'LW-411': 'MDS-00043-054', 'LW-412': 'MDS-00043-055', 'LW-413': 'MDS-00043-056',
              'LW-420': 'MDS-00043-057', 'LH-711': 'MDS-00251-033', 'LH-713': 'MDS-00282-016', 'LH-714': 'MDS-00383-050'}
FD04_CASES = [(code, ref, k) for code, ref in SCH5_LINES.items()
              for k in records_dds.part_keys(g3_dds.terms.dds().sch5[code])]


def _drop(key):
    return lambda t: "\n".join(x for x in t.split("\n") if not x.startswith(key + ":"))


@pytest.mark.parametrize("code, ref, key", FD04_CASES)
def test_fd04_every_required_content_line_missing_or_unreadable(world, code, ref, key):
    """Every Schedule 5 service, every content line of its Part (priced or not): missing -> unresolved; unreadable ->
    unresolved; the line's value is never kept on a Part that is not shown complete."""
    base, _ = dds_eval(world, ref, lambda t: t)
    assert base.payable is True and base.code == code
    part = g3_dds.terms.dds().sch5[code]
    for fn in (_drop(key), swap(key, "??")):
        r, q = dds_eval(world, ref, fn)
        assert r.amount_status == "unresolved" and r.amount is None and not r.alternatives, (code, key)
        assert any(c.check == "input" and c.detail.startswith(f"{part}.{key}") for c in r.checks)


def test_fd04_known_failure_takes_the_contractual_consequence(world):
    r, q = dds_eval(world, "MDS-00043-057", swap("Source handling certified", "No"))
    assert r.amount_status == "not_payable" and "source_handling_not_certified" in r.findings and not q.items


def test_fd04_unrelated_services_on_the_report_are_unaffected(world):
    """DD-101, DD-102, DD-120, HC-620, LW-401 on the same report as LW-420: Part D is not their condition of payment."""
    for ref in ("MDS-00043-048", "MDS-00043-049", "MDS-00043-050", "MDS-00043-051", "MDS-00043-052"):
        base, _ = dds_eval(world, ref, lambda t: t)
        for fn in (_drop("Sources handled"), swap("Source handling certified", "No"), swap("Source handling certified", "??")):
            r, _ = dds_eval(world, ref, fn)
            assert (r.amount_status, r.amount) == (base.amount_status, base.amount), ref


def test_fd04_control_gate3_r3_accepts_an_incomplete_or_negative_part(world, r3):
    for fn in (swap("Source handling certified", "No"), swap("Source handling certified", "??"),
               swap("Source handling certified", ""), _drop("Sources handled")):
        r, _ = dds_eval(world, "MDS-00043-057", fn, engine=r3.g3_dds, parser=r3.records_dds)
        assert (r.amount_status, r.amount, r.findings) == ("determined", Decimal("2746.55"), [])
    r, _ = dds_eval(world, "MDS-00001-021", _drop("Run circulating hours"), engine=r3.g3_dds, parser=r3.records_dds)
    assert (r.amount_status, r.amount) == ("determined", Decimal("3589.45"))
    r, _ = dds_eval(world, "MDS-00043-053", _drop("Run last day"), engine=r3.g3_dds, parser=r3.records_dds)
    assert r.amount_status == "conditional" and not any(c.check == "input" for c in r.checks)


# ============================================================================================ X8 evidence obligations
def test_x8_obligations_are_source_derived():
    """The obligation set comes from the specs (Sch 5 Part per code; the civil record layout), not from the engine."""
    ob = ns.obligations("DDS", "LW-420")
    assert {("doc", "D.Sources handled"), ("doc", "D.Source handling certified"), ("doc", "D.Source run"), ("part", "D")} <= ob
    assert ("doc", "B.Metres logged") in ns.obligations("DDS", "DD-111") and ns.obligations("DDS", "DD-101") == set()
    assert {("doc", "Date"), ("doc", "narrative"), ("doc", "Countersigned (Engineer's representative)")} <= ns.obligations("CW", "B.21.040")
    assert ns.obligations("CW", "A.12.020") == set()                     # no Schedule 5 record required


@pytest.fixture(scope="module")
def x8_r3_engine(world, r3):
    res = {"CW": g3_cw.run(world), "DDS": g3_dds.run(world)}
    return ns.x8(world, res, ns.Engines(r3.g3_cw, r3.g3_dds))


def test_x8_control_gate3_r3_engine_ignores_obligations(x8_r3_engine):
    """X8 on the gate3-r3 engines (G2 as now): required Part content removed or unreadable leaves a payable value -
    rejected as an ignored obligation (the audit's FD04 note: an engine-derived relevance test would have accepted it)."""
    errs, stats = x8_r3_engine
    assert stats["obligation_ignored"] > 50
    assert any("B.Run circulating hours" in e and "source evidence obligation" in e for e in errs)
    assert any("D.Sources handled" in e and "source evidence obligation" in e for e in errs)


# ============================================================================================ FD05 night work
import csv  # noqa: E402
import io  # noqa: E402

import test_g3_corrections_r3 as r3t  # noqa: E402

CW_LINES = "civilwork/invoices/application_lines.csv"
NIGHT = {"PA-00001-04": "??", "PA-00001-01": "yes", "PA-00001-06": "1", "PA-00001-10": "n", "PA-00007-07": "",
         "PA-00001-02": "??", "PA-00023-03": "??", "PA-00002-05": "", "PA-00004-01": "??"}
ELIGIBLE_UNKNOWN = ["PA-00001-04", "PA-00001-01", "PA-00001-06", "PA-00001-10", "PA-00007-07"]
NIGHT_IRRELEVANT = {"PA-00001-02": "item without a night uplift", "PA-00023-03": "zone factor above 1.10 suppresses it (27A)",
                    "PA-00002-05": "Z4 Escarpment: zone factor above 1.10 suppresses it (27A)",
                    "PA-00004-01": "Z3 in 2026: zone factor 1.145 suppresses it (27A)"}


def _night_csv(text):
    rows = list(csv.DictReader(io.StringIO(text)))
    for r in rows:
        r["night_work"] = NIGHT.get(r["line_ref"], r["night_work"])
    out = io.StringIO()
    wr = csv.DictWriter(out, fieldnames=list(rows[0]), lineterminator="\n")
    wr.writeheader()
    wr.writerows(rows)
    return out.getvalue()


@pytest.fixture(scope="module")
def night_world(tmp_path_factory):
    snap = r3t.snapshot_with(tmp_path_factory.mktemp("night"), CW_LINES, _night_csv)
    w = build.build(snap)
    return snap, w, g3_cw.run(w)


def test_fd05_unknown_night_statement_through_the_csv_loader(world, night_world):
    """Raw CSV -> G2 loader -> G3 batch: only Y or N states the fact. '??', 'yes', '1', 'n' and blank are queued by G2
    and handed over as None; where the night uplift changes the rate the line is unresolved and names night_work."""
    _snap, w, res = night_world
    base = g3_cw.run(world)
    queued = {u.ident for u in w.queue.items if u.kind == "cw_lines" and u.field == "night_work"}
    assert set(NIGHT) <= queued
    for ref in ELIGIBLE_UNKNOWN:
        r = res[ref]
        assert r.amount_status == "unresolved" and r.amount is None, ref
        assert any(c.detail.startswith("night_work") for c in r.checks) and any("night_work" in x for x in r.reasons)
        assert base[ref].amount_status == "determined"


def test_fd05_where_the_night_fact_cannot_change_the_value_it_stays_determined(world, night_world):
    _snap, w, res = night_world
    base = g3_cw.run(world)
    for ref, why in NIGHT_IRRELEVANT.items():
        assert (res[ref].amount_status, res[ref].amount) == (base[ref].amount_status, base[ref].amount), (ref, why)


def test_fd05_recognised_values_state_the_fact(world):
    line, app, rec = _cw_line(world, "PA-00001-04")
    y = g3_cw.evaluate({**line, "night_work": "Y"}, app, rec, True)
    n = g3_cw.evaluate({**line, "night_work": "N"}, app, rec, True)
    assert (y.amount, n.amount) == (Decimal("21631.15"), Decimal("17730.62"))


def test_fd05_control_gate3_r3_reads_unknown_as_daytime(night_world, r3):
    snap, _w, _res = night_world
    old_claims = r3_module("claims")
    c = old_claims.load(snap, Queue())
    line = next(x for x in c.rows["cw_lines"] if x.ident == "PA-00001-04").values
    app = next(h for h in c.rows["cw_headers"] if h.ident == line["application_no"]).values
    rec = build.build().cw[line["record_ref"]]
    assert line["night_work"] == "??" and not any(u.field == "night_work" and u.ident == "PA-00001-04" for u in c.queue.items)
    r = r3.g3_cw.evaluate(line, app, rec, True)
    assert (r.amount_status, r.amount) == ("determined", Decimal("17730.62"))
