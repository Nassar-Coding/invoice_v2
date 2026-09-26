"""G3 drilling (DDS-2025-118): local entitlement and pricing of one invoice line.

Line-level checks (plan §5 checks 1-8, local part): identity, term, submission window, period, unit (Cl.35; remedy is
Q11), report evidence (the quoted Daily Drilling Report for the well and day, signatures, the Schedule 5 part: Cl.37),
status and section as recorded (Cl.19, R7), quantities by service family (persons Cl.22, coordinator Q5, tool days
Cl.28, hours Cl.21/21A/P10 with Q4 alternatives, counts Cl.30, metres Cl.23-25/25A, run events Cl.26, well events
Cl.27, loss Cl.31/31A/P12), rate version by service date (instruments in issue order; 36A protection of invoices
submitted before a retrospective amendment's issue; D2), indexation (17A), build-up section -> class -> standby ->
S2/A2 discount (Cl.18, 17B) with half-even rounding at every step (Cl.17), and line arithmetic.

Not decided here (G4/G5): daily limits, duplicates, once-per-run and once-per-well counting, the A3 adjustment
posting, the DS-900 discount, VAT and totals. They are listed as g4_dependencies (or deferred for DS-900).
"""
from __future__ import annotations

import datetime as dt
from decimal import Decimal

from . import links, terms
from .g3_core import LineResult, Trace

CONTRACT_REF = "DDS-2025-118"
CONTRACTOR = "MERIDIAN DOWNHOLE SERVICES LTD"       # agreement particulars (p1)
ALWAYS_G4 = ["duplicate_scope (DDS-R16, Cl.29)"]
PERSONS = {"DD-101", "MW-301", "LW-401", "PD-201"}
COORDINATOR = "DD-102"
HOURLY = {"DD-120", "RM-530"}
COUNTS = {"DD-130": "Gyro surveys", "LW-413": "Pressure points", "HC-610": "Wiper trips", "HC-630": "Clean-out runs"}
METRE_TOOL = {"LW-410": "LW-410", "LW-411": "LW-411", "LW-412": "LW-412", "RM-510": "RM-511"}   # Cl.24; Cl.25 underreamer = App G 'hole opener'
PERFORMANCE_SECTIONS = {'12-1/4"', '8-1/2"'}                                         # App A (p29)
RUN_EVENTS = {"DD-111": ("last", "DD-110"), "LW-420": ("first", None)}              # Cl.26
WELL_EVENTS = {"DD-140", "MB-701", "MB-702", "LW-430"}                               # Cl.27
LOSS = {"LH-711", "LH-712", "LH-713", "LH-714"}
Q4_READINGS = ("A", "B", "C")
Q4_WORKING = None       # Q4 stays open: every reading is computed and carried (see spec/g3_decisions.yaml)


def _half(tr: Trace, label: str, src: str = "Cl.17 (p6): each step to the cent, half to even") -> Decimal:
    return tr.round(label, "half_even", src)


def base_rate(code, date, submitted, T, tr, readings):
    cands = T.rate_candidates(code, date, submitted)
    skipped = [i for i in T.instruments if i.retrospective and submitted is not None and submitted < i.issued
               and any(c == code and eff <= date for c, eff, _ in i.rate_rows)]
    if cands:
        order, eff, value, src = max(cands, key=lambda c: (c[0], c[1]))
        tr.start("base rate (latest-issued instrument applicable on the service date)", value, src + "; SoV p37 (issue order); D2")
    else:
        tr.start("base rate", T.sch1[code]["rate"], f"DDS.T01_SCH1 {code} (Sch 1 pp15-16)")
    for ins in skipped:
        tr.note(f"{ins.id} not applied: invoice submitted {submitted} before its issue {ins.issued}", "36A (p35); A3 (p42)")
        readings.append(f"36A protection ({ins.id})")
    if code in T.rsi_items:
        month = f"{date:%Y-%m}"
        tr.mul(f"x Rig Services Index {month} / base 100.00", T.rsi[month] / T.rsi_base, f"DDS.T05_RSI {month} (Sch 2C p18); 17A (p35)")
        _half(tr, "indexed rate, half to even", "17A (p35)")


def build_up(code, status, section, well_class, date, T, tr):
    """Cl.18 factors after the base: section (Operating only, 17B), class (not PD-210, 17B), standby %, discount."""
    if code in T.section_rated:
        if status == "Standby":
            tr.note("no hole-section factor on a Standby day", "17B (p35); OV-DDS-01")
        else:
            tr.mul(f"section {section}", T.section[section], "DDS.T08_SECTION_FACTORS (Sch 3 Part 1 p20); Cl.18 (p6)")
            _half(tr, "after section factor")
    if code in T.class_rated and code != "PD-210":
        tr.mul(f"well class {well_class} (invoice header; call-off not supplied, Q8 proxy)", T.class_factor[well_class],
               "DDS.T10_CLASS_FACTORS (Sch 3 Part 2 p20); P2, P3 (p11)")
        _half(tr, "after class factor")
    if status == "Standby" and code in T.standby and T.standby[code] is not None:
        tr.mul(f"standby {T.standby[code]}%", T.standby[code] / 100, "DDS.T12_STANDBY (Sch 3 Part 3 pp20-21); Cl.20 (p6); P13 (p11)")
        _half(tr, "after standby percentage")
    disc = T.discount(code, date)
    if disc:
        tr.mul(f"discount {disc.value}%", 1 - disc.value / 100, disc.source + "; S2/A2 last factor")
        _half(tr, "after discount")


def pd210_parts(start: Decimal, end: Decimal, T):
    """Split [start, end] at the depth-band boundaries; a boundary depth belongs to the shallower band (Cl.23)."""
    parts = []
    for lo, hi, rate, band in T.depth_bands:
        a, b = max(start, lo), min(end, hi) if hi is not None else end
        if b > a:
            parts.append((band, a, b, rate))
    return parts


def evaluate(line: dict, inv: dict, ddr, T=None, question_readings: dict | None = None) -> LineResult:
    T = T or terms.dds()
    qr = question_readings or {}
    code = line["service_code"]
    r = LineResult("DDS", line["line_ref"], code)
    tr, readings = Trace(), []
    sch = T.sch1.get(code)
    if code == "DS-900":
        r.add("identification", "n/a", "DDS-R20", "Cl.38 (p8); P11 (p11)", detail="invoice-level discount charge; valued with the invoice total (G5)")
        r.amount_status, r.payable = "deferred", None
        r.reasons.append("DS-900 is recomputed from the invoice's corrected service subtotal at G5 (Cl.38, P11)")
        return r
    if sch is None:
        r.add("identification", "unresolved", "DDS-R06", "Sch 1 (pp15-16)", "code_not_in_schedule_1")
        r.amount_status, r.payable = "unresolved", None
        return r
    sd = line["service_date"]
    payable, reasons = True, []
    # 1 identity --------------------------------------------------------------------------------------------
    if inv["contract_ref"] != CONTRACT_REF:
        r.add("identity", "finding", "DDS-R01", "p1 particulars; Cl.32 (p8)", "contract_ref_variant", inv["contract_ref"])
    elif (inv.get("contractor") or "").upper() != CONTRACTOR:
        r.add("identity", "finding", "DDS-R01", "p1 particulars", "contractor_mismatch", inv.get("contractor"))
    else:
        r.add("identity", "pass", "DDS-R01", "p1 particulars")
    if line.get("well_name") != inv.get("well_name"):
        r.add("identity", "finding", "DDS-R01", "Cl.32 (p8): each well invoiced separately", "line_well_differs_from_invoice",
              f"{line.get('well_name')} vs {inv.get('well_name')}")
    # 2 term ------------------------------------------------------------------------------------------------
    if not (T.commencement <= sd <= T.expiry):
        r.add("term", "finding", "DDS-R03", "p1 particulars; A2 2.1 (p41)", "out_of_term", f"{sd} outside {T.commencement}..{T.expiry}")
        payable = False
        reasons.append("service outside the term as extended is not chargeable (A1/A2)")
    else:
        r.add("term", "pass", "DDS-R03", "p1 particulars; A1 (p39); A2 (p41)")
    # 3 window and period -----------------------------------------------------------------------------------
    pe, idate = inv["period_end"], inv["invoice_date"]
    if idate < pe:
        r.add("window", "finding", "DDS-R04", "Cl.33 (p8)", "submitted_early", f"{idate} before period end {pe}")
    elif idate > pe + dt.timedelta(days=T.window_days):
        r.add("window", "finding", "DDS-R04", "Cl.33 (p8)", "submitted_late", f"{(idate - pe).days} days after period end")
    else:
        r.add("window", "pass", "DDS-R04", "Cl.33 (p8)")
    if not (inv["period_start"] <= sd <= pe):
        r.add("period", "finding", "DDS-R02", "Cl.32 (p8)", "outside_period", f"{sd} outside {inv['period_start']}..{pe}")
    else:
        r.add("period", "pass", "DDS-R02", "Cl.32 (p8)")
    # 4 unit (Cl.35; remedy Q11) ------------------------------------------------------------------------------
    wrong_unit = line["unit"] != sch["unit"]
    if wrong_unit:
        r.add("unit", "finding", "DDS-R08", "Cl.35 (p8)", "wrong_unit", f"billed {line['unit']}, Schedule 1 {sch['unit']}")
    else:
        r.add("unit", "pass", "DDS-R08", "Cl.35 (p8)")
    # 5 report evidence ---------------------------------------------------------------------------------------
    part_needed = T.sch5.get(code)
    if ddr is None:
        r.add("evidence", "finding", "DDS-R05", "Cl.15 (p5); 19A (p35)", "report_missing", f"no report {line.get('report_ref')}")
        return _finish(r, tr, readings, False, reasons + ["no Daily Drilling Report evidences the day"], None, None)
    a = ddr.parts.get("A", {})
    b = ddr.parts.get("B", {})
    if ddr.date != sd:
        r.add("evidence", "finding", "DDS-R05", "19A (p35); Cl.15 (p5)", "report_date_mismatch", f"report {ddr.report} is for {ddr.date}")
        payable = False
        reasons.append("the quoted report is for another day: nothing recorded for the charged day (Cl.19A)")
    if ddr.well != line.get("well_name"):
        r.add("evidence", "finding", "DDS-R05", "Cl.15 (p5)", "well_mismatch", f"report well {ddr.well}")
        payable = False
        reasons.append("the quoted report is for another well")
    unsigned = not (ddr.company_signed and ddr.driller_signed)
    if unsigned:
        r.add("evidence", "finding", "DDS-R05", "Cl.15 (p5); R8 (p14)", "report_unsigned", "a required signature is a placeholder")
    if part_needed:
        if part_needed not in ddr.parts:
            r.add("evidence", "finding", "DDS-R05", "Cl.37 (p8); Sch 5 (p24)", "required_part_missing", f"Part {part_needed} absent")
            payable = False
            reasons.append(f"Schedule 5 Part {part_needed} not completed: record not delivered, not payable (Cl.37; Q3 reading A)")
            r.readings.append("Q3:A")
        elif unsigned:
            payable = False
            reasons.append("Schedule 5 document not delivered in signed form (Cl.15, Cl.37; Q3 reading A)")
            r.readings.append("Q3:A")
    if not any(c.check == "evidence" and c.status == "finding" for c in r.checks):
        r.add("evidence", "pass", "DDS-R05", "Cl.15 (p5); Cl.37 (p8); Sch 5 (p24)")
    # 6 status and section as recorded (Cl.19, R7) --------------------------------------------------------------
    status, section = a.get("Status"), a.get("Hole section")
    if line.get("day_status") != status:
        r.add("status", "finding", "DDS-R05", "Cl.19 (p6); R7 (p14)", "status_mismatch", f"line {line.get('day_status')}, report {status}")
    if line.get("hole_section") != section:
        r.add("status", "finding", "DDS-R05", "Cl.19 (p6)", "section_mismatch", f"line {line.get('hole_section')}, report {section}")
    if status == "Standby" and code in T.standby and T.standby[code] is None:
        r.add("status", "finding", "DDS-R13", "Cl.20 (p6); Sch 3 Part 3 (pp20-21)", "not_chargeable_on_standby", f"{code} marked not chargeable")
        payable = False
        reasons.append("service not chargeable on a Standby day in any quantity (Cl.20)")
    if code == "DD-121" and status != "Standby":
        r.add("status", "finding", "DDS-R13", "Cl.21 (p6); Sch 3 Part 4 (p21)", "not_chargeable_on_operating", "DD-121 only on a Standby day")
        payable = False
        reasons.append("DD-121 is charged only on a Standby day (Sch 3 Part 4)")
    # 7 quantity ----------------------------------------------------------------------------------------------
    billed = line["quantity"]
    tools = {c for c in ddr.tools_in_hole.values() if c}
    run_tools = {c for c in ddr.tools_in_run.values() if c}
    q_alts = None
    supported, basis, qfind = billed, "", None
    if code in PERSONS or code == COORDINATOR:
        rec = Decimal(ddr.crew.get(code, 0))
        supported, basis = rec, f"{rec} persons recorded on the rig (Cl.22; App G)"
        if code == COORDINATOR:
            basis = f"{rec} coordinator(s) recorded ('night man', App G) per day (Sch 8 intro p27; Q5 reading A)"
            r.readings.append("Q5:A")
    elif code in links.TOOL_DAY_SERVICES:
        bcode = links.TOOL_BASIS.get(code)
        present = bcode in tools
        supported = Decimal("1") if present else Decimal("0")
        basis = f"tool of {bcode} {'recorded' if present else 'not recorded'} in the hole (Cl.28; App G)"
        if not present:
            r.add("quantity", "finding", "DDS-R06", "Cl.28 (p7); App G (p36)", "tool_not_in_hole", basis)
            payable = False
            reasons.append("a day rental is charged only where the report records the tool in the hole (Cl.28)")
    elif code in HOURLY:
        q_alts, supported, basis = _hours(code, a, b, ddr, tools, status, T, qr.get("Q4"))
        if supported is None:
            r.add("quantity", "finding", "DDS-R06", "Cl.21 (p6); Cl.28 (p7)", "tool_not_in_hole", basis)
            payable, supported = False, Decimal("0")
            reasons.append("DD-120 needs the rotary steerable in the hole")
    elif code in COUNTS:
        rec = Decimal(a.get(COUNTS[code]) or 0)
        supported, basis = rec, f"{COUNTS[code]}: {rec} recorded on the report (Cl.30)"
        if code == "HC-630":
            basis += " (Q5: counted as recorded, Cl.30)"
            r.readings.append("Q5:HC-630 counts (Cl.30)")
    elif code in METRE_TOOL or code == "PD-210":
        supported, basis, ok = _metres(code, line, a, tools, r, T, tr)
        if not ok:
            payable = False
            reasons.append(basis)
    elif code in RUN_EVENTS:
        which, tool = RUN_EVENTS[code]
        ok_tool = (tool in run_tools) if tool else (b.get("Radioactive source carried") is True)
        day = b.get("Run last day" if which == "last" else "Run first day")
        supported = Decimal("1") if ok_tool and day == sd else Decimal("0")
        basis = f"run {b.get('Run')}: {'motor in the run' if tool else 'source carried'}={ok_tool}; {which} day {day} (Cl.26)"
        if not ok_tool or day != sd:
            r.add("quantity", "finding", "DDS-R15", "Cl.26 (p7)", "run_event_not_supported", basis)
            payable = False
            reasons.append("per-run charge not supported on this day by the run record (Cl.26)")
        r.g4_dependencies.append("once_per_run (DDS-R15)")
    elif code in WELL_EVENTS:
        supported, basis = Decimal("1"), "once for the well (Cl.27); first/last day of the well is G4 state"
        r.g4_dependencies.append("once_per_well (DDS-R15): first/last day on the well")
    elif code in LOSS:
        supported, basis = Decimal("1"), "one unit on the day of the loss (Cl.31)"
    else:
        r.add("quantity", "unresolved", "DDS-R07", "Sch 8 (pp27-28)", "quantity_rule_missing", code)
        return _finish(r, tr, readings, None, reasons + ["no quantity rule"], None, None)
    if code not in METRE_TOOL and code != "PD-210":
        allowed = min(billed, supported)
        if wrong_unit:
            r.add("quantity", "n/a", "DDS-R08", "Cl.35 (p8)", detail=f"billed in {line['unit']}; supported {supported} {sch['unit']} (Q11)")
        elif billed > supported and not any(c.finding == "tool_not_in_hole" for c in r.checks) and code not in RUN_EVENTS:
            r.add("quantity", "finding", "DDS-R07", "Cl.21-22, 28, 30 (pp6-7)", "quantity_above_report", f"billed {billed}; {basis}")
        elif not any(c.check == "quantity" for c in r.checks):
            r.add("quantity", "pass", "DDS-R07", "Cl.21-31 (pp6-7)", detail=basis)
    else:
        allowed = supported
    # 8 rate --------------------------------------------------------------------------------------------------
    well_class = inv.get("well_class")
    if code == "PD-210":
        parts = [x for x in tr.steps if x["op"] == "part"]
        rate = Decimal(parts[0]["rate"]) if len(parts) == 1 else None
        tr.note("PD-210 priced by Schedule 2 depth band; annual footage band 100% (per-well records bound 10,002 m < 40,000 m, Q11)",
                "Sch 2 (p17); Cl.23 (p6); 17B (p35); spec/question_scopes.json Q11_DDS")
    elif code in LOSS:
        rate = _loss_value(code, sd, ddr, r, tr, T)
        if rate is None:
            payable = False
            reasons.append("loss not evidenced as this tool (Part E)")
    else:
        try:
            base_rate(code, sd, idate, T, tr, readings)
            build_up(code, status, section, well_class, sd, T, tr)
            rate = tr.value
        except KeyError as e:
            rate = None
            tr.note(f"not priced: no published index for {e} (outside the tables)", "Sch 2C (p18)")
    r.readings += readings
    r.unit_rate = rate
    if rate is not None and line["unit_rate"] != rate:
        r.add("rate", "finding", "DDS-R09", "Cl.17, Cl.18 (p6); instruments pp37-42", "rate_differs", f"billed {line['unit_rate']}, contract {rate}")
    elif rate is not None:
        r.add("rate", "pass", "DDS-R09", "Cl.17, Cl.18 (p6)")
    # 9 arithmetic --------------------------------------------------------------------------------------------
    if billed * line["unit_rate"] != line["amount"]:
        r.add("arithmetic", "finding", "DDS-R20", "Cl.18 (p6); Cl.36 (p8)", "amount_arithmetic",
              f"{billed} x {line['unit_rate']} = {billed * line['unit_rate']}, billed {line['amount']}")
    else:
        r.add("arithmetic", "pass", "DDS-R20", "Cl.18 (p6)")
    # G4 dependencies ----------------------------------------------------------------------------------------
    if code in T.limited:
        r.g4_dependencies.append("daily_limit (DDS-R14, D6)")
    if any("36A protection" in x for x in r.readings):
        r.g4_dependencies.append("a3_adjustment (DDS-R21): difference posted once on a later invoice")
    # wrong-unit remedy is Q11 (open): both readings carried
    if wrong_unit and payable:
        r.alternatives["Q11:A"] = {"question": "Q11", "reading": "unit breach recorded; value per supported quantity"}
        r.alternatives["Q11:B"] = {"question": "Q11", "reading": "charge unsupported", "allowed_quantity": Decimal("0"), "amount": Decimal("0.00")}
    if payable and allowed == 0 and not q_alts:
        payable = False
        reasons.append("nothing chargeable under the quantity rules")
    return _finish(r, tr, readings, payable, reasons, allowed, rate, q_alts, line, ddr, T)


def _finish(r, tr, readings, payable, reasons, allowed, rate, q_alts=None, line=None, ddr=None, T=None):
    r.payable, r.reasons = payable, reasons
    if payable is None:
        r.amount_status = "unresolved"
        r.trace = tr.steps
        return r
    if not payable:
        r.allowed_quantity, r.amount, r.amount_status = Decimal("0"), Decimal("0.00"), "not_payable"
        tr.note("not payable: " + "; ".join(reasons), "; ".join(sorted({c.clause for c in r.checks if c.status == 'finding'})))
        r.trace = tr.steps
        return r
    r.allowed_quantity = allowed
    if r.code == "PD-210":
        r.amount = tr.total("amount = sum of depth-band parts", "Cl.23 (p6): each band part priced at its own rate")
    else:
        r.amount = tr.amount(allowed, rate, "Cl.18 (p6): quantity x rate so built up")
    if q_alts:
        billed = line["quantity"]
        vals = {k: min(billed, v) for k, v in q_alts.items()}
        if len(set(vals.values())) > 1:
            for k, v in vals.items():
                r.alternatives[f"Q4:{k}"] = {"question": "Q4", "allowed_quantity": v, "amount": v * rate}
            r.amount_status = "alternatives"
            r.readings.append("Q4 open: readings differ on this line; no single amount")
            tr.note("Q4 alternatives (quantity x the rate above): " + ", ".join(f"{k}={v}" for k, v in vals.items()), "21A (p35); Cl.21 (p6); P10 (p11); spec/g3_decisions.yaml Q4")
            r.allowed_quantity, r.amount = None, None
            r.trace = [x for x in tr.steps if x["op"] != "amount"]
            return r
    if any(k.startswith("Q11:") for k in r.alternatives):
        r.alternatives["Q11:A"].update({"allowed_quantity": allowed, "amount": r.amount})
        r.amount_status = "alternatives"
    if r.amount_status == "determined" and r.code == "PD-210" and "Q8:performance-section nomination not supplied" in r.readings:
        r.amount_status = "conditional"
    r.trace = tr.steps
    return r


def _hours(code, a, b, ddr, tools, status, T, fixed=None):
    """Chargeable hours under each Q4 reading. None if DD-120's tool is not in the hole."""
    first_run_day = b.get("Run first day") == ddr.date
    if code == "DD-120":
        if "DD-120" not in tools:
            return None, None, "rotary steerable not recorded in the hole (Cl.21, Cl.28)"
        h = Decimal(a.get("Circulating hours") or 0)
        m = T.dd120_min
        alts = {"A": max(h - T.first_hour, m),                                   # deduct per day, then the minimum
                "B": max(h, m) - T.first_hour,                                   # minimum on hours run, then deduct
                "C": (max(h - T.first_hour, m) if first_run_day else max(h, m))}  # deduct once per run (first day)
        basis = (f"{h} circulating hours recorded; first day of run {first_run_day}; 6-hour minimum on an Operating day with the tool "
                 f"in the hole (Cl.21, P10); rig-up hour 21A: Q4 readings A={alts['A']} B={alts['B']} C={alts['C']}")
    else:
        h = Decimal(a.get("Back-reaming hours") or 0)
        alts = {"A": max(h - T.first_hour, Decimal("0")), "B": max(h - T.first_hour, Decimal("0")),
                "C": (max(h - T.first_hour, Decimal("0")) if first_run_day else h), "counts": h}
        basis = (f"{h} back-reaming hours recorded (Cl.30); 21A rig-up per period in the hole: Q4 readings A/B={alts['A']} "
                 f"C={alts['C']}; counted as recorded (Cl.30)={h}")
    reading = fixed or Q4_WORKING
    if reading:
        return None, alts[reading], basis + f"; reading {reading} applied"
    return alts, max(alts.values()), basis


def _metres(code, line, a, tools, r, T, tr):
    start, end = Decimal(a.get("Depth start (m MD)")), Decimal(a.get("Depth end (m MD)"))
    billed = line["quantity"]
    status = a.get("Status")
    if code == "PD-210":
        f, t = line.get("depth_from_m"), line.get("depth_to_m")
        section = a.get("Hole section")
        if section not in PERFORMANCE_SECTIONS:
            r.add("quantity", "finding", "DDS-R19", "Cl.23 (p6); App A (p29)", "not_performance_section", f"section {section}")
            return Decimal("0"), f"PD-210 only on a performance-drilled (12-1/4 or 8-1/2 inch) section; report section {section}", False
        r.readings.append("Q8:performance-section nomination not supplied")
        lo, hi = max(f, start), min(t, end)
        sup = max(hi - lo, Decimal("0"))
        allowed = billed if billed <= sup * (1 + T.metre_tolerance / 100) else sup
        if billed > sup * (1 + T.metre_tolerance / 100):
            r.add("quantity", "finding", "DDS-R07", "Cl.23 (p6); 25A (p35)", "quantity_above_report", f"billed {billed}; report supports {sup} m in {f}-{t}")
            f, t = lo, hi
        if t - f != billed and allowed == billed:
            r.add("quantity", "finding", "DDS-R07", "Cl.34 (p8)", "depths_differ_from_quantity", f"{f}-{t} vs {billed}")
        parts = pd210_parts(f, t, T)
        if len(parts) > 1:
            r.add("quantity", "finding", "DDS-R12", "Cl.23 (p6)", "band_crossing_not_split", f"{f}-{t} spans {len(parts)} bands")
        for band, pa, pb, rate in parts:
            tr.part(f"band {band}: {pa}-{pb} m", pb - pa, rate, f"DDS.T02_DEPTH_BANDS band {band} (Sch 2 p17); boundary to the shallower band")
        return allowed, f"report depths {start}-{end}; charged {f}-{t}", True
    tool = METRE_TOOL[code]
    present = tool in tools and status == "Operating"
    sup = (end - start) if present else Decimal("0")
    if not present:
        r.add("quantity", "finding", "DDS-R06", "Cl.24, Cl.25 (p6)", "tool_not_in_hole", f"tool of {tool} not in the hole on an Operating day")
    allowed = billed if billed <= sup * (1 + T.metre_tolerance / 100) else sup
    if present and billed > sup * (1 + T.metre_tolerance / 100):
        r.add("quantity", "finding", "DDS-R07", "Cl.24-25 (p6); 25A (p35)", "quantity_above_report", f"billed {billed}; drilled {sup}")
    elif present:
        r.add("quantity", "pass", "DDS-R07", "Cl.24-25 (p6); 25A (p35)", detail=f"drilled {sup} m; charged {billed} within 1%")
    if not present:
        return Decimal("0"), "metre charge needs its tool in the hole on an Operating day (Cl.24, Cl.25)", False
    return allowed, f"metres drilled {sup}", True


def _loss_value(code, sd, ddr, r, tr, T):
    e = ddr.parts.get("E", {})
    if ddr.lost_tool_code != code:
        r.add("identification", "finding", "DDS-R17", "Cl.31 (p7); App G (p36)", "lost_tool_mismatch", f"Part E tool {ddr.lost_tool_term} -> {ddr.lost_tool_code}")
        return None
    hours = Decimal(e.get("Circulating hours accumulated on the well"))
    month = f"{sd:%Y-%m}"
    tr.start(f"replacement value SAR ({code})", T.sar[code], f"DDS.T06_SAR_VALUES (Sch 2D p19); 31A (p35); OV-DDS-04")
    tr.div(f"/ SAR per USD for {month} (halalas per USD / 100)", T.fx[month] / 100, f"DDS.T07_FX {month} (Sch 2D p19); 31A")
    _half(tr, "converted value, half to even", "31A (p35)")
    steps = min((hours // T.lih_step_hours) * T.lih_pct_per_step, T.lih_cap_pct)
    tr.mul(f"less depreciation {steps}% ({hours} h as stated on the Lost in Hole Report; 1% per complete 25 h, max 50%)",
           1 - steps / 100, "Cl.31 (p7); P12 (p11); Sch 5 Part E (p24); Q13 reading A")
    _half(tr, "depreciated value, half to even", "Cl.31 (p7); Cl.17")
    r.readings.append("Q13:A (Part E hours; corroborated by the tool's own daily history)")
    return tr.value


def inputs_from_world(w):
    invs = {h.ident: h.values for h in w.claims.rows["dds_headers"]}
    for row in w.claims.rows["dds_lines"]:
        v = row.values
        yield v, invs[v["invoice_no"]], w.ddr.get(v["report_ref"]) if v.get("report_ref") else None


def run(w, T=None) -> dict[str, LineResult]:
    out = {}
    for line, inv, ddr in inputs_from_world(w):
        res = evaluate(line, inv, ddr, T=T)
        res.ctx = w.run_context["id"] if w.run_context else None
        out[res.line_ref] = res
    return out
