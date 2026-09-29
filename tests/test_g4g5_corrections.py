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


# ---------------------------------------------------------------------------------------------------------- G4-B03
def _hist(hid, blank=None, field="application_date"):
    import copy
    import g4_histories as H
    h = copy.deepcopy(next(x for x in H.CW_HISTORIES + H.DDS_HISTORIES if x["id"] == hid))
    for d in h["documents"]:
        if blank and (d["header"].get("application_no") == blank or d["header"].get("invoice_no") == blank):
            d["header"][field] = ""
    return h


def _cw_with(engine_cw, h):
    w, res, _st = F.run(h)
    _claims(w)
    vg4.load_heads(w)
    return w, res, {"CW": engine_cw.run(w, res["CW"]), "DDS": g4_dds.run(w, res["DDS"])}


def h_b03_band():
    h = _hist("CW-H01")
    h["documents"][0]["lines"][0]["work_date"] = ""          # the first 600 m2 B.22.010: work date not established
    return h


def test_b03_undated_band_measurement_is_a_possible_contributor():
    w, res, st = _cw_with(g4_cw, h_b03_band())
    L = F.by_ref(st, "CW")
    later = L["PA-91001-01"]                                  # 500 m2: 37,250.00 without the 600 before it, 36,356.00 with
    assert later.r.amount != D("37250.00") and later.r.amount_status == "unresolved" and later.r.payable is None
    assert "band_state_unknown" in later.state_unresolved
    # the 400 m2 of 10 March lies in band 1 whatever the undated 600 adds (0..600 + 400 <= 1,000): provably determined
    assert D("29800.00") in F.amounts(L["PA-91002-02"])
    assert vg4.y3(st["CW"], st["DDS"]) == [] and vg4.chronology_errors(st["CW"], st["DDS"]) == []


def test_b03_control_gate4_omits_the_undated_measurement():
    old = gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4")
    w, res, st = _cw_with(old, h_b03_band())
    later = F.by_ref(st, "CW")["PA-91001-01"]
    assert later.r.amount == D("37250.00") and later.r.amount_status == "determined"      # the audit's silent value
    st["CW"].undated = {}
    assert any("undated measurements" in e for e in vg4.chronology_errors(st["CW"], st["DDS"]))


def test_b03_release_with_an_undated_application_is_not_established():
    w, res, st = _cw_with(g4_cw, _hist("CW-H10", "PA-9A001"))
    rel = st["CW"].retention["release"]
    assert rel["recipient"]["not_established"] == ["PA-9A001", "PA-9A003"]
    assert rel["released"] == {"by_reading": {"": {"min": "96.15", "max": "192.49"}}}       # never the bare 96.15
    assert vg4.chronology_errors(st["CW"], st["DDS"]) == []
    w, res, st = _cw_with(g4_cw, _hist("CW-H10"))
    assert st["CW"].retention["release"]["recipient"] == "PA-9A003" and st["CW"].retention["release"]["released"] == "192.49"


def test_b03_control_gate4_release_omits_the_undated_application():
    old = gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4")
    w, res, st = _cw_with(old, _hist("CW-H10", "PA-9A001"))
    rel = st["CW"].retention["release"]
    assert rel["released"] == "96.15" and rel["not_established"] == [] and rel["recipient"] == "PA-9A003"
    st["CW"].undated = {}
    assert any("45A release recipient" in e for e in vg4.chronology_errors(st["CW"], st["DDS"]))


def _stands(o):
    return [k for k in o["open_readings"] if k.split("@")[0] == "stands"]


def _g5(mod, h, gate=False):
    w, res, st = F.run(h)
    if gate:            # the tagged pair: gate4's G4 state under gate5's G5
        st = {"CW": gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4").run(w, res["CW"]),
              "DDS": gate_module(GATE4, "audit/g4_dds.py", "g4_dds_gate4").run(w, res["DDS"])}
    e = mod.Engine(w, st)
    return {no: e.outcome(i) for no, i in e.inv["DDS"].items()}, e


def test_b03_undated_invoice_never_sorted_last_under_q7c():
    from audit import g5_outcomes
    out, e = _g5(g5_outcomes, _hist("DDS-H01", "MDS-90001", "invoice_date"))
    o = out["MDS-90002"]
    assert _stands(o) and o["confidence"] != D("0.80")
    # its own daily-limit breach makes it wrong whichever charge stands; the totals differ by the 4 March charge (Q9-5)
    assert o["flagged"] == 1 and o["confidence"] == D("0.60") and len(o["totals"]) == 2
    assert _stands(out["MDS-90001"]) and out["MDS-90001"]["confidence"] == D("0.50")
    assert all(t is True for v in e.stands.values() for d, (_f, t) in v.items() if d.startswith("stands@"))                          # open, not a keeper chosen by a sentinel date


def test_b03_control_gate5_sentinel_selects_a_keeper():
    old = gate_module(GATE5, "audit/g5_outcomes.py", "g5_outcomes_gate5")
    out, e = _g5(old, _hist("DDS-H01", "MDS-90001", "invoice_date"), gate=True)
    o = out["MDS-90002"]
    assert "stands" not in o["open_readings"] and o["confidence"] == D("0.80")      # the audit's definite keeper
    # the undated invoice's charge is treated as the later one: a definite repeat at 0.80
    assert out["MDS-90001"]["flagged"] == 1 and out["MDS-90001"]["confidence"] == D("0.80")
    assert "charged_twice@MDS-90001-002" in out["MDS-90001"]["findings"]
    assert all(v["stands"][1] is False for v in e.stands.values() if "stands" in v)


def test_b03_undated_civil_measurement_may_be_the_earlier_duplicate():
    w, res, st = _cw_with(g4_cw, h_b03_band())
    g = F.by_ref(st, "CW")["PA-91002-02"]
    assert D("0.00") in F.amounts(g) and "duplicate_measurement" in g.state_unresolved


def test_b03_undated_dds_charge_is_a_possible_repeat_and_well_event_not_a_finding():
    h = _hist("DDS-H01")
    h["documents"][1]["lines"][0]["service_date"] = ""                  # MDS-90002's 4 March DD-101: date not established
    w, res, st = F.run(h)
    L = F.by_ref(st, "DDS")
    assert L["MDS-90002-001"].g3.payable is None                        # G3: the undated charge is not valued
    # it may be for any of the well's dated DD-101 days: each dated charge stands only in the scenario it is the one kept
    for ref in ("MDS-90001-001", "MDS-90001-002", "MDS-90002-002"):
        assert F.amounts(L[ref]) == [D("0.00"), D("3694.70")] and "charged_twice" in L[ref].state_unresolved
    poss = [gr for gr in st["DDS"].groups if gr.get("possible")]
    assert len(poss) == 3 and all(gr["possible"] == ["MDS-90002-001"] for gr in poss)


def test_b03_control_gate4_ignores_the_undated_dds_charge():
    old = gate_module(GATE4, "audit/g4_dds.py", "g4_dds_gate4")
    h = _hist("DDS-H01")
    h["documents"][1]["lines"][0]["service_date"] = ""
    w, res, st = _with(old, h)
    assert F.amounts(F.by_ref(st, "DDS")["MDS-90001-002"]) == [D("3694.70")]     # determined: the possible repeat omitted



# ---------------------------------------------------------------------------------------------------------- G4-B04
def cw_hist(hid, lines, adate="2025-03-20"):
    """One civil application of B.22.010 lines (work date, quantity, displayed rate, amount), header consistent with the
    amounts (no header defect of its own); zone Z1, no records needed."""
    import g4_histories as H
    doc = H.cw_app("PA-97001", adate, [(d, "S-05", "B.22.010", q, r, "") for d, q, r, _a in lines])
    tot = D(0)
    for row, (_d, _q, _r, a) in zip(doc["lines"], lines):
        row["amount"] = a
        tot += D(a)
    ret = (tot * D("0.05")).quantize(D("0.01"), rounding="ROUND_DOWN")
    doc["header"].update({"application_total": f"{tot:.2f}", "retention": f"{ret:.2f}", "net_payable": f"{tot - ret:.2f}"})
    return {"id": hid, "documents": [doc], "records": {}, "given": []}


def _cw_outcome(h, g4mod=g4_cw, g5mod=None):
    from audit import g5_outcomes
    g5mod = g5mod or g5_outcomes
    w, res, _st = F.run(h)
    st = {"CW": g4mod.run(w, res["CW"]), "DDS": g4_dds.run(w, res["DDS"])}
    e = g5mod.Engine(w, st)
    return st, {no: e.outcome(i) for no, i in e.inv["CW"].items()}


def _state(st, ref, fam):
    return [(x.status, x.finding) for x in F.by_ref(st, "CW")[ref].state if x.family == fam]


def test_b04_wrong_rate_with_the_correct_amount_is_a_finding():
    # first-band B.22.010, 600 m2, no earlier history: rate 74.50, amount 44,700.00; the claim states 71.52 (band 2)
    st, out = _cw_outcome(cw_hist("CW-B04-1", [("2025-03-02", "600", "71.52", "44700.00")]))
    assert _state(st, "PA-97001-01", "band_rate") == [("finding", "rate_differs")]
    assert _state(st, "PA-97001-01", "band_arithmetic") == [("finding", "amount_arithmetic")]   # 600 x 71.52 = 42,912.00
    o = out["PA-97001"]
    assert o["flagged"] == 1 and "rate" in o["error_category"] and o["expected_total"] == D("44700.00")


def test_b04_control_gate4_leaves_the_wrong_rate_unresolved_and_g5_passes_it():
    old = gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4")
    old5 = gate_module(GATE5, "audit/g5_outcomes.py", "g5_outcomes_gate5")
    st, out = _cw_outcome(cw_hist("CW-B04-1", [("2025-03-02", "600", "71.52", "44700.00")]), old, old5)
    assert _state(st, "PA-97001-01", "band_rate") == [("unresolved", "rate_differs")]
    assert out["PA-97001"]["flagged"] == 0 and out["PA-97001"]["confidence"] == D("0.95")        # the audit's false pass


def test_b04_rate_and_amount_are_judged_independently():
    cases = {("74.50", "44700.00"): ("pass", "pass", 0), ("74.50", "44000.00"): ("pass", "finding", 1),
             ("71.52", "42912.00"): ("finding", "pass", 1), ("71.52", "44700.00"): ("finding", "finding", 1)}
    for (rate, amt), (rs, ars, flag) in cases.items():
        st, out = _cw_outcome(cw_hist("CW-B04-x", [("2025-03-02", "600", rate, amt)]))
        got_r = [s for s, _f in _state(st, "PA-97001-01", "band_rate")]
        got_a = [s for s, _f in _state(st, "PA-97001-01", "band_arithmetic")] or ["pass"]      # G3 passed it outright
        assert (got_r, got_a[0], out["PA-97001"]["flagged"]) == ([rs], ars, flag), (rate, amt)


def test_b04_a_valid_split_is_not_a_finding():
    # 1,000 m2 in band 1, then 400 m2 from 1,000: 200 at 74.50 + 200 at 71.52 = 29,204.00 (Cl.28 division)
    for rate in ("74.50", "71.52"):
        st, out = _cw_outcome(cw_hist("CW-B04-s", [("2025-03-02", "1000", "74.50", "74500.00"),
                                                ("2025-03-03", "400", rate, "29204.00")]))
        assert _state(st, "PA-97001-02", "band_rate") == [("pass", None)]
        assert _state(st, "PA-97001-02", "band_arithmetic") in ([("pass", None)], [])
        assert out["PA-97001"]["flagged"] == 0
    st, out = _cw_outcome(cw_hist("CW-B04-s2", [("2025-03-02", "1000", "74.50", "74500.00"),
                                             ("2025-03-03", "400", "72.00", "29204.00")]))
    assert _state(st, "PA-97001-02", "band_rate") == [("finding", "rate_differs")]        # no band's rate


def test_b04_genuinely_unresolved_band_stays_open_never_a_pass():
    h = cw_hist("CW-B04-u", [("2025-03-02", "1000", "74.50", "74500.00"), ("2025-03-03", "500", "71.52", "37250.00")])
    h["documents"][0]["lines"][0]["work_date"] = ""
    st, out = _cw_outcome(h)
    g = F.by_ref(st, "CW")["PA-97001-02"]
    assert g.r.amount_status == "unresolved" and ("pass", None) not in _state(st, "PA-97001-02", "band_rate")
    assert out["PA-97001"]["confidence"] != D("0.95")


def test_b04_reading_dependent_band_carries_the_breach_per_scenario():
    # 1,200 m2 in December 2025, then 100 m2 on 10 January 2026 at 74.50: band 1 after the Q12 A reset, band 2 under Q12 B
    h = cw_hist("CW-B04-q", [("2025-12-20", "1200", "74.50", "89400.00"), ("2026-01-10", "100", "74.50", "7450.00")],
                adate="2026-01-20")
    st, out = _cw_outcome(h)
    g = F.by_ref(st, "CW")["PA-97001-02"]
    assert _state(st, "PA-97001-02", "band_rate") == [("unresolved", "rate_differs")]
    br = {k: v.get("breaches") for k, v in g.r.alternatives.items()}
    assert any("rate_differs" in (b or []) for k, b in br.items() if "Q12:B" in k)
    assert all(not b for k, b in br.items() if "Q12:A" in k)
    assert out["PA-97001"]["flagged"] == 0                                 # Q12 A decided (upheld): right
    from audit import g5_outcomes
    w, res, _st = F.run(h)
    e = g5_outcomes.Engine(w, st, g5_outcomes.Policy(decided={**g5_outcomes.DECIDED, "Q12": "B"}))
    o = e.outcome(e.inv["CW"]["PA-97001"])
    assert o["flagged"] == 1 and "rate_differs@PA-97001-02" in o["findings"]


def test_b04_oracle_accepts_the_fixed_state_and_rejects_gate4():
    h = cw_hist("CW-B04-o", [("2025-03-02", "600", "71.52", "44700.00")])
    w, res, _st = F.run(h)
    _claims(w)
    assert vg4.deferred_rate_errors(g4_cw.run(w, res["CW"])) == []
    old = gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4")
    errs = vg4.deferred_rate_errors(old.run(w, res["CW"]))
    assert errs and "expected finding" in errs[0]


# ---------------------------------------------------------------------------------------------------------- G5-B04
def h_b04_witness():
    """The audit's raw-history witness: Z1, March 2025; two independent band-edge order groups (B.22.010 on 2 March,
    A.13.010 on 4 March), each of two measurements on two applications in different work areas (not duplicates)."""
    import g4_histories as H
    x1 = H.cw_app("PA-9X001", "2025-03-20", [("2025-03-01", "S-05", "B.22.010", "1100", "74.50", ""),
                                             ("2025-03-02", "S-05", "B.22.010", "150", "74.50", ""),
                                             ("2025-03-03", "S-05", "A.13.010", "4900", "18.90", ""),
                                             ("2025-03-04", "S-05", "A.13.010", "150", "18.90", "")])
    x2 = H.cw_app("PA-9X002", "2025-03-25", [("2025-03-02", "S-04", "B.22.010", "150", "74.50", ""),
                                             ("2025-03-04", "S-04", "A.13.010", "150", "18.90", "")], site="S-04")
    return {"id": "CW-G5B04", "documents": [x1, x2], "records": {}, "given": []}


def test_g5b04_independent_local_groups_combine_into_four_totals():
    st, out = _cw_outcome(h_b04_witness())
    assert [D(t) for t in out["PA-9X001"]["totals"]] == [D("187953.50"), D("188066.50"), D("188251.50"), D("188364.50")]
    assert [D(t) for t in out["PA-9X002"]["totals"]] == [D("13393.50"), D("13506.50"), D("13691.50"), D("13804.50")]
    for o in out.values():
        assert o["formed"] is True and o["scenarios"] >= 4 and len([k for k in o["open_readings"] if k.startswith("order@")]) == 2


def test_g5b04_control_gate4_gate5_merge_the_groups_into_one_order():
    old4 = gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4")
    old5 = gate_module(GATE5, "audit/g5_outcomes.py", "g5_outcomes_gate5")
    st, out = _cw_outcome(h_b04_witness(), old4, old5)
    o = out["PA-9X001"]
    assert o["formed"] is False and o["confidence"] == D("0.30") and len(o["totals"]) <= 1      # the audit's result


def test_g5b04_two_independent_tie_groups_and_q12():
    import g4_histories as H
    # two applications submitted the same day each measure A.11.010 on S-01 (3 June) and D.41.010 on S-02 (4 June):
    # two independent Cl.44 tie groups - each application is the earlier one in one scenario of EACH group
    a = H.cw_app("PA-9T001", "2025-06-10", [("2025-06-03", "S-01", "A.11.010", "100", "3.85", ""),
                                            ("2025-06-04", "S-02", "A.13.010", "50", "18.90", "")], site="S-01")
    b = H.cw_app("PA-9T002", "2025-06-10", [("2025-06-03", "S-01", "A.11.010", "100", "3.85", ""),
                                            ("2025-06-04", "S-02", "A.13.010", "50", "18.90", "")], site="S-01")
    st, out = _cw_outcome({"id": "CW-G5B04t", "documents": [a, b], "records": {}, "given": []})
    for o in out.values():
        groups = [k for k in o["open_readings"] if k.startswith("earlier@")]
        assert len(groups) == 2 and o["scenarios"] == 4 and o["formed"]
        # wrong where the other application's measurement is the earlier one in either group, right in one scenario
        assert len(o["right_under"]) == 1 and len(o["wrong_under"]) == 3 and o["confidence"] == D("0.50")
    # Q12 is a global reading: forcing B applies it to every group at once, never per group
    import g4cr_fixtures as F2
    from audit import g5_outcomes
    w, res, st2 = F2.run(_cw_order_q12())
    e = g5_outcomes.Engine(w, st2)
    o = e.outcome(e.inv["CW"]["PA-9Q001"])
    assert o["open_readings"] == {}                  # Q12 A (decided): CY2 restarts at zero, no edge, no order group
    eb = g5_outcomes.Engine(w, st2, g5_outcomes.Policy(decided={**g5_outcomes.DECIDED, "Q12": "B"}))
    ob = eb.outcome(eb.inv["CW"]["PA-9Q001"])
    assert list(ob["open_readings"]) == ["order@B.22.010/2026-01-10"] and len(ob["open_readings"]["order@B.22.010/2026-01-10"]) == 2


def _cw_order_q12():
    import g4_histories as H
    # a same-date order group on 10 January 2026 at the B.22.010 edge only under Q12 B (no reset): Q12 decided A
    x = H.cw_app("PA-9Q001", "2026-01-20", [("2025-12-20", "S-05", "B.22.010", "1150", "74.50", ""),
                                            ("2026-01-10", "S-05", "B.22.010", "100", "74.50", "")])
    y = H.cw_app("PA-9Q002", "2026-01-22", [("2026-01-10", "S-04", "B.22.010", "100", "74.50", "")], site="S-04")
    return {"id": "CW-G5B04q", "documents": [x, y], "records": {}, "given": []}


def test_g5b04_oracle_joins_combinations_and_rejects_the_gate_pair():
    import verify_g5 as vg5
    from audit import g5_outcomes
    w, res, st = F.run(h_b04_witness())
    e = g5_outcomes.Engine(w, st)
    out = {no: e.outcome(i) for no, i in e.inv["CW"].items()}
    assert vg5.joint_errors(out, e) == []
    old4 = gate_module(GATE4, "audit/g4_cw.py", "g4_cw_gate4")
    old5 = gate_module(GATE5, "audit/g5_outcomes.py", "g5_outcomes_gate5")
    st_old = {"CW": old4.run(w, res["CW"]), "DDS": g4_dds.run(w, res["DDS"])}
    e_old = old5.Engine(w, st_old)
    out_old = {no: e_old.outcome(i) for no, i in e_old.inv["CW"].items()}
    errs = vg5.joint_errors(out_old, e_old)
    assert any("PA-9X001" in x and "formed=False" in x for x in errs)
