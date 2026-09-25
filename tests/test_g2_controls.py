"""G2 negative and structural controls: the unresolved queue and conflict list fire on bad input; nothing is
defaulted; reference validity and semantic facts stay separate; repeated run metadata is one fact."""
import csv
import datetime as dt
import shutil
import sys
from decimal import Decimal
from pathlib import Path

import pytest

from audit import build, claims, events, links, records_cw, records_dds
from audit.common import SNAPSHOT, Queue

ROOT = Path(__file__).resolve().parents[1]


@pytest.fixture(scope="module")
def world():
    return build.build()


def test_every_row_and_file_accounted_for(world):
    assert {k: len(v) for k, v in world.claims.rows.items()} == {"cw_headers": 900, "cw_lines": 7746, "dds_headers": 1906, "dds_lines": 91244}
    assert all(world.claims.assertions.values())
    assert len(world.cw) == 2169 and len(world.ddr_by_file) == 8151 and len(world.ddr) == 8151
    assert len(world.cw_links) == 7746 and len(world.dds_links) == 91244
    assert links.accounting(world.cw_links, world.cw)["unreferenced"] == []
    assert links.accounting(world.dds_links, world.ddr)["unreferenced"] == []


def test_queue_empty_on_corpus_but_contradictions_visible(world):
    assert world.queue.items == []
    checks = {c.check for c in world.queue.conflicts}
    assert checks == {"gyro_surveys_without_part_C", "part_E_hours_vs_well_daily_sum"}


def test_civil_bad_input_is_queued_not_defaulted():
    q = Queue()
    bad = ("DAILY EXCAVATION RECORD\nTicket: DX-99998\nJob: J\nArea: S-09 Nowhere\nDate: 31/02/2025\nGround: G9 Mud\n\n"
           "dug a big hole\nand another\n\nSigned (foreman): A\n")
    r = records_cw.parse_file("civilwork/records/DX-99999.txt", bad, q)
    got = {(u.field, u.reason.split(" ")[0]) for u in q.items}
    assert ("Area", "not") in got and ("Date", "unparseable") in got and ("Ground", "not") in got
    assert ("narrative", "expected") in got and ("Countersigned (Engineer's representative)", "required") in got
    assert r.area is None and r.date is None and r.ground is None and r.quantity is None and r.candidates == []
    assert {c.check for c in q.conflicts} == {"ticket_vs_filename"}
    q = Queue()
    r = records_cw.parse_file("civilwork/records/XX-00001.txt", "SITE DIARY\nTicket: XX-00001\n\nsomething\n", q)
    assert r.family is None and any(u.field == "title" for u in q.items)
    q = Queue()
    records_cw.parse_file("civilwork/records/CT-99999.txt",
                          "COMPACTION TEST CERTIFICATE\nTicket: CT-99999\nJob: J\nArea: S-01 Platform North\nDate: 01/02/2025\n\n"
                          "rolled some stone\n\nSigned (foreman): A\nCountersigned (Engineer's representative): B\n", q)
    assert [u.reason.split(" ")[0] for u in q.items] == ["no"]                # unmatched narrative never defaulted


def test_weekly_day_list_checks():
    q = Queue()
    days = records_cw.reconstruct_days(dt.date(2025, 1, 27), "Mon 27/01, Wed 28/01, Mon 03/02, Xyz 01/01", q, "DW-X", None)
    assert days == [dt.date(2025, 1, 27), dt.date(2025, 1, 28), dt.date(2025, 2, 3)]
    assert {c.check for c in q.conflicts} == {"weekday_name", "day_outside_week"}
    assert [u.reason.split(" ")[0] for u in q.items] == ["unparseable"]
    q = Queue()
    assert records_cw.reconstruct_days(dt.date(2026, 12, 28), "Thu 31/12, Fri 01/01", q, "DW-Y", None) == [dt.date(2026, 12, 31), dt.date(2027, 1, 1)]


def test_ddr_bad_input_is_queued():
    q = Queue()
    bad = ("DAILY DRILLING REPORT\nReport: DDR-999-20250101\nContract: DDS-2025-118\nWell: NGP-BD-999\nRig: R\nDate: 01-Jan-2025\n\n"
           "PART A — OPERATIONS SUMMARY\nHole section: 7\"\nStatus: Sleeping\nDepth start (m MD): ten\nIn the hole: sky hook, mud motor\n"
           "Crew on tour: 3 wizards\nMystery: 1\n\nPART Z — EXTRAS\n\nSigned (Company Representative): X\n")
    d = records_dds.parse_file("drilling_services/records/DDR_NGP-BD-999_20250101.txt", bad, q)
    reasons = " | ".join(f"{u.field}: {u.reason}" for u in q.items)
    for needle in ("A.Hole section: unparseable", "A.Status: unparseable", "A.Depth start (m MD): unparseable",
                   "'sky hook' is not an Appendix G tool term", "unrecognised crew entry '3 wizards'", "A.Mystery: unknown key",
                   "unknown part heading", "Part B missing", "signature line missing", "A.Circulating hours: key missing"):
        assert needle in reasons, needle
    assert d.tools_in_hole == {"sky hook": None, "mud motor": "DD-110"}
    assert d.parts["A"]["Depth start (m MD)"] is None                         # not zero


def test_ddr_internal_contradictions_become_conflicts():
    q = Queue()
    txt = ("DAILY DRILLING REPORT\nReport: DDR-998-20250102\nContract: DDS-2025-181\nWell: NGP-BD-999\nRig: R\nDate: 02-Jan-2025\n\n"
           "PART A — OPERATIONS SUMMARY\nHole section: 6\"\nStatus: Standby\nDepth start (m MD): 100\nDepth end (m MD): 90\nCirculating hours: 25\n"
           "BHA run: 2\nIn the hole: mud motor\nCrew on tour: 2 directional hands\nGyro surveys: 0\nPressure points: 0\nWiper trips: 0\n"
           "Back-reaming hours: 0\nClean-out runs: 0\n\nPART B — BHA RUN RECORD\nRun: 3\nRun first day: 05-Jan-2025\nRun last day: 06-Jan-2025\n"
           "Tools in run: MWD collar\nRun circulating hours: 5\nMetres logged: 0\nMetres reamed: 0\nRadioactive source carried: No\n\n"
           "PART D — RADIOACTIVE SOURCE HANDLING\nSource run: 3\nSources handled: x\nSource handling certified: Yes\n\n"
           "PART E — LOST IN HOLE\nLost in hole run: 2\nLost in hole tool: gamma tool\nCirculating hours accumulated on the well: 5\n\n"
           "Signed (Company Representative): ____\nSigned (lead directional driller): Y\n")
    d = records_dds.parse_file("drilling_services/records/DDR_NGP-BD-999_20250101.txt", txt, q)
    checks = {c.check for c in q.conflicts}
    assert {"filename_vs_header", "report_number_vs_well_date", "A_run_vs_B_run", "A_tools_vs_B_tools", "report_date_outside_run",
            "depth_decreases", "standby_with_depth_change", "Circulating hours_over_24", "part_D_but_no_source_carried",
            "E_run_vs_B_run", "lost_tool_not_in_run", "contract_reference"} <= checks
    assert d.lost_tool_code == "LH-714" and not d.company_signed and d.driller_signed


def test_claims_loader_queues_blank_and_unparseable(tmp_path):
    for rel in list(claims.FILES.values()) + ["submission_template.csv"]:
        (tmp_path / rel).parent.mkdir(parents=True, exist_ok=True)
        shutil.copy(SNAPSHOT / rel, tmp_path / rel)

    def corrupt(rel, fn):
        path = tmp_path / rel
        rows = list(csv.DictReader(path.open(newline="")))
        cols = list(rows[0])
        fn(rows)
        with path.open("w", newline="") as fh:
            w = csv.DictWriter(fh, cols)
            w.writeheader()
            w.writerows(rows)

    def dds(rows):
        rows[0]["report_ref"] = ""                 # MDS-00001-001 DD-101: needs its report
        rows[1]["quantity"] = "abc"                # MDS-00001-002
        rows[2]["service_date"] = "2025-01-01"     # wrong format for drilling
    def cw(rows):
        rows[0]["amount"] = ""                     # PA-00001-01
        rows[1]["quantity"] = "0"                  # PA-00001-02: a real zero stays zero
    corrupt(claims.FILES["dds_lines"], dds)
    corrupt(claims.FILES["cw_lines"], cw)
    c = claims.load(tmp_path)
    got = {(u.ident, u.field, u.reason.split(" ")[0]) for u in c.queue.items}
    assert ("MDS-00001-001", "report_ref", "required") in got
    assert ("MDS-00001-002", "quantity", "unparseable") in got
    assert ("MDS-00001-003", "service_date", "unparseable") in got
    assert ("PA-00001-01", "amount", "required") in got
    rows = {r.ident: r for r in c.rows["cw_lines"]}
    assert rows["PA-00001-01"].values["amount"] is None and rows["PA-00001-02"].values["quantity"] == Decimal("0")
    assert not any(u.field == "report_ref" and u.ident != "MDS-00001-001" for u in c.queue.items)   # DS-900 exempt
    assert len(c.queue.items) == 4


def test_reference_and_semantic_are_separate(world):
    for l in list(world.cw_links.values()) + list(world.dds_links.values()):
        if l.reference in links.RESOLVED_STATES:
            assert l.semantic and "reference" not in l.semantic
        else:
            assert l.semantic == {}
    l = world.dds_links["MDS-00164-050"]                       # plan §4: mismatch is not a duplicate
    assert (l.reference, l.semantic["date_match"], l.semantic["well_match"]) == ("resolved", False, True)
    assert {l.reference for l in world.cw_links.values()} <= links.CW_REFERENCE_STATES
    assert {l.reference for l in world.dds_links.values()} <= links.DDS_REFERENCE_STATES


def test_repeated_run_metadata_is_one_fact(world):
    r = world.runs[("NGP-BD-011", 1)]
    assert len(r.reports) >= 2 and r.all_days_reported
    assert r.metadata["Run circulating hours"] == 59 == r.daily_circulating_hours   # run total, not per report


def test_run_metadata_disagreement_and_loss_hours_are_conflicts():
    def mk(rid, date, run_hours, a_hours, loss=None):
        d = records_dds.Ddr(file=rid + ".txt", path="x", report=rid, well="W-1", date=date)
        d.parts = {"A": {"Circulating hours": a_hours, "Depth start (m MD)": 0, "Depth end (m MD)": 10},
                   "B": {"Run": 1, "Run first day": dt.date(2025, 1, 1), "Run last day": dt.date(2025, 1, 2), "Tools in run": ["mud motor"],
                         "Run circulating hours": run_hours, "Metres logged": 0, "Metres reamed": 0, "Radioactive source carried": False}}
        if loss is not None:
            d.parts["E"] = {"Circulating hours accumulated on the well": loss}
            d.lost_tool_term, d.lost_tool_code = "mud motor", "LH-711"
        return d
    q = Queue()
    ddrs = {"R1": mk("R1", dt.date(2025, 1, 1), 20, 10), "R2": mk("R2", dt.date(2025, 1, 2), 21, 10, loss=15)}
    runs, _ = events.identify(ddrs, q)
    checks = {c.check for c in q.conflicts}
    assert "part_B_Run circulating hours_differs" in checks
    assert "part_E_hours_vs_well_daily_sum" in checks
    loss = runs[("W-1", 1)].losses[0]
    assert (loss["well_daily_hours_through_loss_day"], loss["run_daily_hours_through_loss_day"]) == (20, 20)


def test_blind_comparator_detects_planted_errors(world, tmp_path, monkeypatch):
    sys.path.insert(0, str(ROOT / "tools"))
    import json
    import compare_blind_g2 as cb
    src = ROOT / "verification" / "g2" / "blind"
    rows = [json.loads(x) for x in (src / "cw_annotations.jsonl").read_text().splitlines()]
    rows[0]["quantity"] = "99999"
    (tmp_path / "cw_annotations.jsonl").write_text("\n".join(json.dumps(x) for x in rows))
    drows = [json.loads(x) for x in (src / "dds_annotations.jsonl").read_text().splitlines()]
    drows[0]["B"]["Metres logged"] = "12345"
    (tmp_path / "dds_annotations.jsonl").write_text("\n".join(json.dumps(x) for x in drows))
    monkeypatch.setattr(cb, "BLIND", tmp_path)
    bad = [x for x in cb.compare_cw(world.cw) + cb.compare_dds(world.ddr_by_file) if not x["agree"]]
    assert [(x["field"]) for x in bad] == ["quantity", "B.Metres logged"]


def test_fixture_coverage_check_detects_a_missing_branch(world):
    """E4 negative control: dropping the only reviewed example of a branch leaves that branch uncovered."""
    import verify_g2 as vg
    conflicts = {}
    for c in world.queue.conflicts:
        conflicts.setdefault(c.ident, set()).add(c.check)
    corpus = set().union(*(vg.ddr_branches(d, conflicts) for d in world.ddr_by_file.values()))
    fixtures = [f for f in vg.yaml.safe_load(vg.FIXTURES.read_text())["drilling_reports"] if f != "DDR_NGP-WS-009_20251211.txt"]
    covered = set().union(*(vg.ddr_branches(world.ddr_by_file[f], conflicts) for f in fixtures))
    assert "ddr.conflict:gyro_surveys_without_part_C" in corpus - covered


def test_boundary_no_pricing_or_outcomes():
    """G2 stops at evidence: the audit package defines no valuation, flag, total or submission output."""
    text = " ".join(p.read_text() for p in (ROOT / "audit").glob("*.py")).lower()
    for word in ("submission.csv", "expected_total", "flagged", "load_instruments", "rate_version", "def price"):
        assert word not in text, word
