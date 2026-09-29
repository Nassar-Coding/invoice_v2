"""G4/G5 correction round (Phase3_G4_G5_audit_Agent2.md): each frozen blocker's demonstrated variants through the
production pipeline, the corrected result, and a negative control - the tagged gate4/gate5 code, loaded from git, run on
the same input and rejected by the corrected oracle for the blocker's reason."""
import importlib.util
import subprocess
import sys
import types
from decimal import Decimal
from pathlib import Path

import pytest

import g4cr_fixtures as F
import verify_g4 as vg4
from audit import g3_cw, g3_dds, g4_cw, g4_dds
from audit.g3_core import result_keys

ROOT = Path(__file__).resolve().parents[1]
GATE4 = "9fa5514a88af49b9daf9c982c7c4352dc8ef984b"
GATE5 = "13eb7684a52dc9634c364bf9d9b3ba3087f882c1"
D = Decimal
W = "NGP-ZZ-951"


def gate_module(sha: str, path: str, name: str) -> types.ModuleType:
    """The tagged version of an audit module, loaded under the audit package (its relative imports resolve to the
    current G3 layer, which the correction round does not change)."""
    src = subprocess.run(["git", "show", f"{sha}:{path}"], cwd=ROOT, capture_output=True, text=True, check=True).stdout
    spec = importlib.util.spec_from_loader(f"audit.{name}", loader=None)
    mod = importlib.util.module_from_spec(spec)
    mod.__package__ = "audit"
    sys.modules[f"audit.{name}"] = mod
    exec(compile(src, f"{sha[:7]}:{path}", "exec"), mod.__dict__)
    return mod


def _claims(w):
    for lk in ("cw_lines", "dds_lines"):
        for k, row in zip(result_keys(w.claims.rows[lk]), w.claims.rows[lk]):
            vg4._CLAIMS[k] = row.values


def _with(engine_dds, h):
    w, res, _st = F.run(h)
    _claims(w)
    return w, res, {"DDS": engine_dds.run(w, res["DDS"])}


# ---------------------------------------------------------------------------------------------------------- G4-B01
def h_b01_v1():
    return F.pd210_history("B01-1", W, [("2025-07-01", 4500, 44490), ("2025-07-02", 44490, 44510)],
                           [("MDS-95101", "2025-07-01", 4500, 44490), ("MDS-95102", "2025-07-02", 44490, 44510),
                            ("MDS-95103", "2025-07-02", 44490, 44510)])


def h_b01_v2():
    return F.pd210_history("B01-2", W, [("2025-07-01", 4500, 44450), ("2025-07-02", 44450, 44470), ("2025-07-03", 44470, 44490)],
                           [("MDS-95201", "2025-07-01", 4500, 44450), ("MDS-95202", "2025-07-02", 44450, 44470),
                            ("MDS-95203", "2025-07-02", 44450, 44470), ("MDS-95204", "2025-07-03", 44470, 44490)])


def test_b01_duplicate_interval_counted_once_and_allocation_kept():
    w, res, st = _with(g4_dds, h_b01_v1())
    L = F.by_ref(st, "DDS")
    a, b = L["MDS-95102-001"], L["MDS-95103-001"]
    # 39,990 prior; 44,490-44,510: 10 m at 98.70 + 10 m at 94.75 (96%) = 1,934.50, kept by ONE of the two charges
    assert F.amounts(a) == [D("0.00"), D("1934.50")] and F.amounts(b) == [D("0.00"), D("1934.50")]
    for k, v in a.r.alternatives.items():
        other = b.r.alternatives[k]
        assert v["amount"] + other["amount"] == D("1934.50")
    assert vg4.footage_reset_errors(st["DDS"]) == [] and vg4.pd210_coverage_errors(st["DDS"]) == []


def test_b01_later_interval_uses_unique_prior_metres():
    w, res, st = _with(g4_dds, h_b01_v2())
    # unique prior 39,950 + 20 = 39,970: the last 20 m lie wholly below 40,000 -> 20 x 98.70 = 1,974.00
    assert F.amounts(F.by_ref(st, "DDS")["MDS-95204-001"]) == [D("1974.00")]
    assert vg4.footage_reset_errors(st["DDS"]) == []


def test_b01_replay_after_removing_the_earlier_duplicate():
    h = h_b01_v2()
    h["documents"] = [d for d in h["documents"] if d["header"]["invoice_no"] != "MDS-95203"]
    w, res, st = _with(g4_dds, h)
    L = F.by_ref(st, "DDS")
    assert F.amounts(L["MDS-95202-001"]) == [D("1974.00")] and F.amounts(L["MDS-95204-001"]) == [D("1974.00")]


def test_b01_control_gate4_counts_the_duplicate_twice():
    old = gate_module(GATE4, "audit/g4_dds.py", "g4_dds_gate4")
    w, res, st = _with(old, h_b01_v1())
    L = F.by_ref(st, "DDS")
    # the tagged code restores both charges to the full 1,934.50 - the metres are charged twice
    assert F.amounts(L["MDS-95102-001"]) == [D("1934.50")] and F.amounts(L["MDS-95103-001"]) == [D("1934.50")]
    w2, res2, st2 = _with(old, h_b01_v2())
    last = F.by_ref(st2, "DDS")["MDS-95204-001"].r.alternatives
    assert last["Q11:A"]["amount"] == D("1934.50")          # adopted Q11 A used 39,990 prior, not 39,970: 1,974.00 absent


# ---------------------------------------------------------------------------------------------------------- G4-B02
def h_b02(extra=()):
    return F.pd210_history("B02", W, [("2025-07-01", 1500, 1700)],
                           [("MDS-95301", "2025-07-01", 1500, 1600), ("MDS-95302", "2025-07-01", 1550, 1650),
                            ("MDS-95303", "2025-07-01", 1600, 1700), *extra])


def test_b02_three_interval_chain_complete_joint_domain():
    w, res, st = _with(g4_dds, h_b02())
    L = F.by_ref(st, "DDS")
    assert F.amounts(L["MDS-95302-001"]) == [D("0.00"), D("2907.50"), D("5815.00")]     # zero, one half, whole
    assert len(L["MDS-95302-001"].r.alternatives) == 4
    for k in L["MDS-95301-001"].r.alternatives:
        assert sum(L[r].r.alternatives[k]["amount"] for r in ("MDS-95301-001", "MDS-95302-001", "MDS-95303-001")) == D("11630.00")
    assert vg4.pd210_coverage_errors(st["DDS"]) == []


def test_b02_contained_and_exact_duplicate():
    w, res, st = _with(g4_dds, h_b02(extra=[("MDS-95304", "2025-07-01", 1500, 1700), ("MDS-95305", "2025-07-01", 1500, 1600)]))
    assert vg4.pd210_coverage_errors(st["DDS"]) == []
    L = F.by_ref(st, "DDS")
    for k in L["MDS-95304-001"].r.alternatives:
        tot = sum(L[r].r.alternatives[k]["allowed_quantity"] for r in L if r.startswith("MDS-953"))
        assert tot == D("200")


def test_b02_control_gate4_pairwise_allocation_fails_the_metre_oracle():
    old = gate_module(GATE4, "audit/g4_dds.py", "g4_dds_gate4")
    w, res, st = _with(old, h_b02())
    L = F.by_ref(st, "DDS")
    assert D("0.00") not in F.amounts(L["MDS-95302-001"])            # the admissible zero outcome is missing
    st["DDS"].footage = {}                                             # old footage format: the coverage oracle alone
    assert vg4.pd210_coverage_errors(st["DDS"]) != []


def test_b02_band_interaction_duplicate_at_the_annual_edge():
    # the B01 fixture is also a contested segment at the annual edge: allocation and footage compose
    w, res, st = _with(g4_dds, h_b01_v1())
    assert vg4.pd210_coverage_errors(st["DDS"]) == []
