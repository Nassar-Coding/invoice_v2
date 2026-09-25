"""Join claims to evidence (G2). Reference validity and semantic facts are separate objects.

reference: does the line cite a record, does that record exist, and is it the kind of reference the line
           needs? This is a join fact only; a successful join proves only that a file exists (plan §4).
semantic:  what the resolved record says relative to the line (dates, area/well, rig, activity, unit,
           quantity, signatures, parts). Facts for G3; no consequence, rejection or price is decided here.
A reference that fails leaves the semantic facts empty rather than guessed.
"""
from __future__ import annotations

import datetime as dt
from collections import Counter
from dataclasses import dataclass, field

from .common import spec_lib

CW_TERMS = spec_lib.load_terms("CW")["tables"]
DDS_TERMS = spec_lib.load_terms("DDS")["tables"]
SCH5_CW = {r[0]: r[2] for r in CW_TERMS["CW.T16_RECORDS"]["rows"]}          # item -> record series
SCH5_DDS = {r[0]: r[1] for r in DDS_TERMS["DDS.T18_SCH5_CODES"]["rows"]}   # service -> DDR part
PERSONNEL = {"DD-101", "DD-102", "MW-301", "LW-401", "PD-201"}
TOOL_DAY_SERVICES = {r[0] for r in DDS_TERMS["DDS.T23_SCH8"]["rows"] if "records the tool in the hole" in r[1]}

CW_REFERENCE_STATES = {"resolved", "wrong_series", "present_not_required", "not_found", "blank_required", "blank_not_required"}
DDS_REFERENCE_STATES = {"resolved", "not_found", "blank_required", "blank_invoice_level"}
RESOLVED_STATES = {"resolved", "wrong_series", "present_not_required"}


@dataclass
class Link:
    line_ref: str
    reference: str
    record: str | None = None
    semantic: dict = field(default_factory=dict)


def link_cw(lines, records) -> dict[str, Link]:
    use = Counter(r.values["record_ref"] for r in lines if r.values["record_ref"])
    out = {}
    for row in lines:
        v = row.values
        ref, item = v["record_ref"], v["item_code"]
        series = SCH5_CW.get(item)
        if not ref:
            out[row.ident] = Link(row.ident, "blank_required" if series else "blank_not_required")
            continue
        if ref not in records:
            out[row.ident] = Link(row.ident, "not_found", ref)
            continue
        rec = records[ref]
        status = "resolved" if series and ref.startswith(series + "-") else ("present_not_required" if not series else "wrong_series")
        s = {
            "record_family": rec.family, "required_series": series,
            "area_match": rec.area == (v["site"] or "").split(" ")[0], "record_area": rec.area,
            "signed_foreman": rec.foreman_signed, "signed_engineer": rec.engineer_signed,
            "extraction_rule": rec.rule, "activity_candidates": rec.candidates,
            "activity_includes_item": item in rec.candidates,
            "record_unit": rec.unit, "unit_equal": rec.unit == v["unit"],
            "record_quantity": rec.quantity, "quantity_relation": _rel(v["quantity"], rec.quantity),
            "record_ground": rec.ground,
            "ground_match": (rec.ground == (v["ground_class"] or "").split(" ")[0]) if rec.ground else None,
            "reference_use_count": use[ref],
        }
        if rec.family == "DW":
            wb, wd = rec.week_beginning, v["work_date"]
            s.update({"week_beginning": wb, "days_on": rec.days_on, "days_on_count": len(rec.days_on),
                      "work_date_in_week": bool(wb and wd and wb <= wd <= wb + dt.timedelta(days=6)),
                      "work_date_is_day_on": wd in rec.days_on})
        else:
            s.update({"record_date": rec.date, "date_match": rec.date == v["work_date"]})
        out[row.ident] = Link(row.ident, status, ref, s)
    return out


def _rel(billed, recorded):
    if billed is None or recorded is None:
        return None
    return "equal" if billed == recorded else ("above_record" if billed > recorded else "below_record")


def link_dds(lines, headers, ddrs) -> dict[str, Link]:
    hdr = {h.ident: h.values for h in headers}
    out = {}
    for row in lines:
        v = row.values
        code, ref = v["service_code"], v["report_ref"]
        if not ref:
            out[row.ident] = Link(row.ident, "blank_invoice_level" if code == "DS-900" else "blank_required")
            continue
        d = ddrs.get(ref)
        if d is None:
            out[row.ident] = Link(row.ident, "not_found", ref)
            continue
        a = d.parts.get("A", {})
        h = hdr.get(v["invoice_no"], {})
        s = {
            "report_date": d.date, "date_match": d.date == v["service_date"],
            "report_well": d.well, "well_match": d.well == v["well_name"],
            "line_well_matches_header": v["well_name"] == h.get("well_name"),
            "report_rig": d.rig, "rig_matches_header": d.rig == h.get("rig"),
            "report_contract": d.contract,
            "report_status": a.get("Status"), "status_match": a.get("Status") == v["day_status"],
            "report_section": a.get("Hole section"), "section_match": a.get("Hole section") == v["hole_section"],
            "parts_present": sorted(d.parts),
            "signed_company": d.company_signed, "signed_driller": d.driller_signed,
        }
        part = SCH5_DDS.get(code)
        if part:
            s["required_part"], s["required_part_present"] = part, part in d.parts
        if code in PERSONNEL:
            s["crew_recorded"] = d.crew.get(code, 0)
        if code in TOOL_DAY_SERVICES:
            s["tool_in_hole"] = code in {c for c in d.tools_in_hole.values() if c}
        if code.startswith("LH-"):
            s["lost_tool_code"] = d.lost_tool_code
        out[row.ident] = Link(row.ident, "resolved", ref, s)
    return out


def accounting(links: dict[str, Link], record_ids) -> dict:
    """Every record file is either cited by at least one line or listed as unreferenced."""
    cited = {l.record for l in links.values() if l.reference in RESOLVED_STATES}
    ids = set(record_ids)
    return {"records": len(ids), "cited": len(cited & ids), "unreferenced": sorted(ids - cited)}
