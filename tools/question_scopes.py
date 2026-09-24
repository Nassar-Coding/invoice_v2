"""Affected scopes for the open-question and decision register (G1), from read-only CSV counts.

These are populations a question CAN affect (lines/invoices whose outcome depends on the reading), not
findings: no record is parsed, no line is priced, and nothing is classified. Output:
spec/question_scopes.json, referenced by spec/open_questions.yaml.

Usage::

    python tools/question_scopes.py
"""
from __future__ import annotations

import csv
import datetime as dt
import json
import sys
from collections import Counter, defaultdict
from decimal import Decimal
from pathlib import Path

import snapshot
import spec_lib as sl


def read(rel: str) -> list[dict]:
    with (snapshot.DEFAULT_SNAPSHOT / rel).open(newline="", encoding="utf-8") as fh:
        return list(csv.DictReader(fh))


def ddate(s: str) -> dt.date:
    return dt.datetime.strptime(s, "%d-%b-%Y").date()


def idate(s: str) -> dt.date:
    return dt.date.fromisoformat(s)


def main() -> int:
    ch = read("civilwork/invoices/applications.csv")
    cl = read("civilwork/invoices/application_lines.csv")
    dh = read("drilling_services/invoices/invoices.csv")
    dl = read("drilling_services/invoices/invoice_lines.csv")
    c_date = {r["application_no"]: idate(r["application_date"]) for r in ch}
    d_date = {r["invoice_no"]: ddate(r["invoice_date"]) for r in dh}
    d_well = {r["invoice_no"]: r["well_name"] for r in dh}
    d_class = {r["invoice_no"]: r["well_class"] for r in dh}
    terms_cw = sl.load_terms("CW")["tables"]
    out: dict = {}

    # ---- Q1/Q2: retrospective A3 populations and candidate receiving submissions -------------------
    cw_issue, cw_eff = dt.date(2026, 5, 12), dt.date(2025, 11, 1)
    a3_cw = [r for r in cl if r["item_code"] in ("C.32.010", "A.14.010") and idate(r["work_date"]) >= cw_eff]
    pre = [r for r in a3_cw if c_date[r["application_no"]] < cw_issue]
    on_or_after = sorted((d, a) for a, d in c_date.items() if d >= cw_issue)
    first_day = on_or_after[0][0]
    strictly_after = sorted((d, a) for a, d in c_date.items() if d > cw_issue)
    out["Q1_Q2_CW"] = {
        "a3_lines_work_on_or_after_effective": len(a3_cw),
        "a3_lines_in_applications_submitted_before_issue": len(pre),
        "a3_applications_submitted_before_issue": len({r["application_no"] for r in pre}),
        "receiving_candidates_on_or_after_issue_first_date": str(first_day),
        "receiving_candidates_on_first_date": sorted(a for d, a in on_or_after if d == first_day),
        "receiving_candidates_strictly_after_first_date": str(strictly_after[0][0]),
        "receiving_candidates_strictly_after": sorted(a for d, a in strictly_after if d == strictly_after[0][0]),
    }
    ds_issue, ds_eff = dt.date(2026, 8, 17), dt.date(2026, 2, 1)
    a3_dd = [r for r in dl if r["service_code"] in ("DD-120", "DD-101") and ddate(r["service_date"]) >= ds_eff]
    dpre = [r for r in a3_dd if d_date[r["invoice_no"]] < ds_issue]
    d_on = sorted((d, i) for i, d in d_date.items() if d >= ds_issue)
    d_after = sorted((d, i) for i, d in d_date.items() if d > ds_issue)
    wells_pre = {d_well[r["invoice_no"]] for r in dpre}
    per_well_first = {}
    for w in sorted(wells_pre):
        cands = sorted((d, i) for i, d in d_date.items() if d_well[i] == w and d >= ds_issue)
        per_well_first[w] = cands[0][1] if cands else None
    out["Q1_Q2_DDS"] = {
        "a3_lines_service_on_or_after_effective": len(a3_dd),
        "a3_lines_in_invoices_submitted_before_issue": len(dpre),
        "a3_invoices_submitted_before_issue": len({r["invoice_no"] for r in dpre}),
        "wells_with_pre_issue_a3_lines": len(wells_pre),
        "receiving_candidates_on_or_after_issue_first_date": str(d_on[0][0]),
        "receiving_candidates_on_first_date": sorted(i for d, i in d_on if d == d_on[0][0]),
        "receiving_candidates_strictly_after_first_date": str(d_after[0][0]),
        "receiving_candidates_strictly_after": sorted(i for d, i in d_after if d == d_after[0][0]),
        "per_well_variant_wells_without_any_later_invoice": sum(1 for v in per_well_first.values() if v is None),
        "dd120_lines_apr_dec_2026_where_s2_monthly_rate_exists": sum(
            1 for r in dl if r["service_code"] == "DD-120" and ddate(r["service_date"]) >= dt.date(2026, 4, 1)),
    }

    # ---- Q3: Schedule 5 record-required lines without a resolvable record ---------------------------
    req = {r[0]: r[2] for r in terms_cw["CW.T16_RECORDS"]["rows"]}
    rec_names = {Path(p).stem for p in (snapshot.DEFAULT_SNAPSHOT / "civilwork/records").iterdir()}
    sch5 = [r for r in cl if r["item_code"] in req]
    out["Q3_CW"] = {
        "record_required_lines": len(sch5),
        "blank_record_ref": sum(1 for r in sch5 if not r["record_ref"]),
        "ref_without_file": sum(1 for r in sch5 if r["record_ref"] and r["record_ref"] not in rec_names),
        "ref_wrong_series_prefix": sum(1 for r in sch5 if r["record_ref"] and not r["record_ref"].startswith(req[r["item_code"]] + "-")),
        "record_ref_on_non_schedule5_lines": sum(1 for r in cl if r["item_code"] not in req and r["record_ref"]),
    }

    # ---- Q4/Q5: DDS hourly and Schedule 8 conflict populations -------------------------------------
    cnt = Counter(r["service_code"] for r in dl)
    out["Q4_DDS"] = {
        "dd120_lines": cnt["DD-120"],
        "dd120_lines_quantity_exactly_6": sum(1 for r in dl if r["service_code"] == "DD-120" and Decimal(r["quantity"]) == 6),
        "dd120_lines_quantity_below_6": sum(1 for r in dl if r["service_code"] == "DD-120" and Decimal(r["quantity"]) < 6),
        "rm530_lines": cnt["RM-530"],
    }
    out["Q5_DDS"] = {"dd102_lines": cnt["DD-102"], "hc630_lines": cnt["HC-630"], "dd120_lines": cnt["DD-120"],
                     "rm530_lines": cnt["RM-530"]}

    # ---- Q6/Q12: civil state populations ----------------------------------------------------------------
    band_codes = {r[0] for r in terms_cw["CW.T12_BANDS"]["rows"]}
    cap_codes = {r[0] for r in terms_cw["CW.T13_DAILY_LIMITS"]["rows"]}
    band_lines = [r for r in cl if r["item_code"] in band_codes]
    out["Q6_CW"] = {
        "band_item_lines": len(band_lines),
        "cap_item_lines": sum(1 for r in cl if r["item_code"] in cap_codes),
        "exclusion_pair_lines_A14020": cnt_c(cl, "A.14.020"),
        "exclusion_pair_lines_E51020": cnt_c(cl, "E.51.020"),
        "same_item_area_date_groups_with_more_than_one_line": sum(
            1 for v in Counter((r["item_code"], r["site"], r["work_date"]) for r in cl).values() if v > 1),
    }
    out["Q12_CW_contract_year"] = {
        "band_item_lines_on_or_after_2026_01_05": sum(1 for r in band_lines if idate(r["work_date"]) >= dt.date(2026, 1, 5)),
        "band_item_lines_before_2026_01_05": sum(1 for r in band_lines if idate(r["work_date"]) < dt.date(2026, 1, 5)),
    }
    # ---- Q7: repeated references / repeated service-days ------------------------------------------
    by_ref = defaultdict(set)
    for r in cl:
        if r["record_ref"]:
            by_ref[r["record_ref"]].add(r["work_date"])
    dkey = Counter((d_well[r["invoice_no"]], r["service_date"], r["service_code"]) for r in dl if r["service_code"] != "DS-900")
    out["Q7"] = {
        "cw_record_refs_used_on_more_than_one_work_date": sum(1 for v in by_ref.values() if len(v) > 1),
        "cw_dw_refs_used_on_more_than_one_work_date": sum(1 for k, v in by_ref.items() if k.startswith("DW-") and len(v) > 1),
        "dds_well_date_code_groups_with_more_than_one_line": sum(1 for v in dkey.values() if v > 1),
        "of_which_pd210": sum(1 for k, v in dkey.items() if v > 1 and k[2] == "PD-210"),
    }
    # ---- Q8: background documents -----------------------------------------------------------------
    both = {"B.21.020", "B.21.030", "D.41.030", "B.21.040"}
    out["Q8"] = {
        "cw_night_lines_on_rest_day_for_items_in_both_uplift_lists": sum(
            1 for r in cl if r["item_code"] in both and r["night_work"] == "Y" and idate(r["work_date"]).weekday() in (4, 5)),
        "dds_pd210_lines_performance_section_nomination_not_supplied": cnt["PD-210"],
    }
    # ---- Q9: identity variants and payment-only fields ---------------------------------------------
    out["Q9"] = {
        "cw_contract_ref_variants": sorted(r["application_no"] for r in ch if r["contract_ref"] != "CW-2025-0417-CIV"),
        "dds_contract_ref_variants": sorted(r["invoice_no"] for r in dh if r["contract_ref"] != "DDS-2025-118"),
        "cw_applications_after_extended_completion_candidates_for_45A_release": sum(1 for d in c_date.values() if d > dt.date(2026, 9, 30)),
    }
    # ---- Q10: invoice-discount obligation (billed-based diagnostic only) -----------------------------
    svc = defaultdict(Decimal)
    has_ds = set()
    for r in dl:
        if r["service_code"] == "DS-900":
            has_ds.add(r["invoice_no"])
        else:
            svc[r["invoice_no"]] += Decimal(r["amount"])
    out["Q10_DDS"] = {
        "invoices_billed_services_above_250000": sum(1 for v in svc.values() if v > 250000),
        "of_which_without_ds900": sum(1 for i, v in svc.items() if v > 250000 and i not in has_ds),
        "invoices_with_ds900_at_or_below_250000": sum(1 for i in has_ds if svc[i] <= 250000),
    }
    # ---- Q11: annual footage reachability (billed PD-210 metres per well and calendar year) ----------
    foot = defaultdict(Decimal)
    for r in dl:
        if r["service_code"] == "PD-210":
            foot[(d_well[r["invoice_no"]], ddate(r["service_date"]).year)] += Decimal(r["quantity"])
    out["Q11_DDS"] = {
        "pd210_lines": cnt["PD-210"],
        "max_billed_pd210_metres_per_well_and_year": str(max(foot.values())),
        "well_years_at_or_above_40000": sum(1 for v in foot.values() if v >= 40000),
    }
    # ---- Settled decisions with recorded alternatives ---------------------------------------------
    out["D_scopes"] = {
        "dds_pd210_lines_on_non_standard_wells": sum(1 for r in dl if r["service_code"] == "PD-210" and d_class[r["invoice_no"]] != "Standard"),
        "cw_c31010_lines": cnt_c(cl, "C.31.010"),
        "dds_mw310_lines": cnt["MW-310"],
        "cw_lines_after_2026_09_30": sum(1 for r in cl if idate(r["work_date"]) > dt.date(2026, 9, 30)),
        "dds_lines_after_2026_12_31": sum(1 for r in dl if r["service_date"] and ddate(r["service_date"]) > dt.date(2026, 12, 31)),
        "cw_lines_before_2025_01_05": sum(1 for r in cl if idate(r["work_date"]) < dt.date(2025, 1, 5)),
        "cw_ground_lines_after_2025_09_27_not_G2": sum(
            1 for r in cl if idate(r["work_date"]) > dt.date(2025, 9, 27) and r["ground_class"] not in ("", "G2")),
        "dds_lh_lines": sum(cnt[c] for c in ("LH-711", "LH-712", "LH-713", "LH-714")),
    }
    path = sl.SPEC / "question_scopes.json"
    path.write_text(json.dumps(out, indent=1) + "\n")
    print(json.dumps(out, indent=1))
    return 0


def cnt_c(rows, code):
    return sum(1 for r in rows if r["item_code"] == code)


if __name__ == "__main__":
    sys.exit(main())
