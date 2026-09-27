"""X8 (G3 correction round 3): every input G2 can leave empty or unresolved, through both engines and the batch.

The field inventory is G2's own, never a hand list: every column of the four claim files (audit.claims.FILES), every key
of the civil record layout and of the drilling report (spec/evidence_cw.yaml, spec/evidence_dds.yaml), whole report
parts and part headings, keys written twice, and list entries G2 cannot recognise (tool terms, crew entries, days
worked). Evidence documents are mutated as TEXT and re-parsed by the real G2 parsers, so every empty value and every
queue entry is exactly what G2 would hand over; a mutation after which G2 holds an ordinary value (a garbled free-text
'Well: ??' that G2 accepts as a well name) is out of scope and counted as such. Claim fields are emptied as the G2
loader leaves them: typed fields None, text fields blank ('') or None (a short CSV row); the join key also as a header
G2 does not have.

Sample: in every civil and drilling code family of spec/g3_code_families.yaml, the first line of every billed code
(line_ref order), plus the first line showing each input-sensitive feature (night work, each zone, rest day, a
protected submission, a record, each status and hole section, a protected invoice); a family with no billed line (codes
outside Schedule 1) gets a line built from a real one with its code replaced. For each (line, input, empty value):
  1. an explicit result - no exception and never an engine_error;
  2. no silent default - where the input matters to this line's value (an admissible other value of it changes the
     value: the relevance probe; for an unrecognised list entry, each recognised entry), the result names the input and
     either leaves the value unresolved, or carries every value the input could take (alternatives covering the line
     as billed and each probe), or is not payable by the contract's own rule for that input (REGISTERED);
  3. nothing lost - where the input does not matter to the value, the value is unchanged;
  4. the batch - the production run() over a sub-world holding every sample line, with the input emptied on all of
     them (claim field, header field or document), completes, gives every line a result, no engine_error, and each
     result equals the direct evaluation of the same inputs.
"""
from __future__ import annotations

import copy
import csv
import datetime as dt
import inspect
import sys
from collections import defaultdict
from dataclasses import replace
from decimal import Decimal
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from audit import claims, records_cw, records_dds  # noqa: E402
from audit.common import SNAPSHOT, Queue, Unresolved  # noqa: E402
from audit.g3_core import Inputs  # noqa: E402

# the contract's own rule for an absent input (anything else that matters must stay unresolved or carry every value)
REGISTERED = {
    ("CW", "line", "record_ref"): {"record_missing"},
    ("CW", "doc", "Signed (foreman)"): {"record_unsigned"},
    ("CW", "doc", "Countersigned (Engineer's representative)"): {"record_unsigned"},
    ("DDS", "line", "report_ref"): {"report_missing"},
    ("DDS", "doc", "Signed (Company Representative)"): {"report_unsigned"},
    ("DDS", "doc", "Signed (lead directional driller)"): {"report_unsigned"},
    ("DDS", "part", "B"): {"required_part_missing"},
    ("DDS", "part", "C"): {"required_part_missing"},
    ("DDS", "part", "D"): {"required_part_missing"},
    ("DDS", "part", "E"): {"required_part_missing"},
}
KINDS = {"CW": ("cw_lines", "cw_headers"), "DDS": ("dds_lines", "dds_headers")}
HKEY = {"CW": "application_no", "DDS": "invoice_no"}
REF = {"CW": "record_ref", "DDS": "report_ref"}
UNSCHEDULED = {"CW": ("item_code", "Z.99.999"), "DDS": ("service_code", "ZZ-999")}
DAYS = ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"]


def claim_fields(kind: str) -> list[str]:
    with (SNAPSHOT / claims.FILES[kind]).open(newline="", encoding="utf-8") as fh:
        return next(csv.reader(fh))


def empties(kind: str, field: str) -> list:
    return [None] if field in claims.TYPES[kind] else ["", None]


def value_of(r) -> tuple:
    """The value of a result: status, payability, rate, quantity, amount and each alternative's - not its wording or trace."""
    alts = tuple(sorted((str(k), str(a.get("unit_rate")), str(a.get("allowed_quantity")), str(a.get("amount")))
                        for k, a in r.alternatives.items()))
    return (r.amount_status, r.payable, str(r.unit_rate), str(r.allowed_quantity), str(r.amount), alts, r.family)


def names(r) -> str:
    """Everything a result says in words: where an empty input must be named."""
    parts = [f"{c.check} {c.finding} {c.detail}" for c in r.checks] + list(r.reasons) + list(r.readings)
    parts += [f"{c.get('dimension')} {c.get('basis')}" for c in r.conditions]
    return " | ".join(str(x) for x in parts)


def _pairs(r) -> set:
    if r.alternatives:
        return {(str(a.get("allowed_quantity")), str(a.get("amount"))) for a in r.alternatives.values()}
    return {(str(r.allowed_quantity), str(r.amount))}


def covers(m, others) -> bool:
    """A conditional result carries the missing input's admissible values rather than defaulting it when every value it
    could take (the line as billed and each probe) is among its alternatives - and it has more than one."""
    got = _pairs(m)
    return len(got) > 1 and all(_pairs(o) <= got for o in others if o.amount_status not in ("unresolved", "deferred"))


# ----------------------------------------------------------------------------------------------- engine adapters
class Engines:
    """The engines under test (the current modules, or an earlier version for the negative control)."""

    def __init__(self, cw, dds):
        self.mod = {"CW": cw, "DDS": dds}
        self.takes_inputs = {c: "inputs" in inspect.signature(m.evaluate).parameters for c, m in self.mod.items()}

    def evaluate(self, contract, line, header, doc, exists, inputs):
        kw = {"inputs": inputs} if self.takes_inputs[contract] else {}
        if contract == "CW":
            return self.mod["CW"].evaluate(line, header, doc, exists, **kw)
        return self.mod["DDS"].evaluate(line, header, doc, **kw)

    def context(self, contract, w) -> dict:
        m = self.mod[contract]
        return m.input_context(w) if hasattr(m, "input_context") else {}


# ----------------------------------------------------------------------------------------------- sample
def sample(w, res) -> tuple[dict[str, list[str]], dict[str, list]]:
    """Per contract: the first line of every billed code in every family and of every input-sensitive feature; and
    synthetic rows for the families with no billed line (a real row with a code outside Schedule 1)."""
    out, extra = {"CW": [], "DDS": []}, {"CW": [], "DDS": []}
    for c, (lk, _hk) in KINDS.items():
        lines = {r.ident: r.values for r in w.claims.rows[lk]}
        first = {}
        for ref in sorted(res[c]):
            first.setdefault((res[c][ref].family, res[c][ref].code), ref)
        picks = set(first.values())
        feats = {}
        for ref in sorted(res[c]):
            v, r = lines[ref], res[c][ref]
            if c == "CW":
                keys = [("night", v.get("night_work")), ("zone", v.get("site_zone")),
                        ("rest", v["work_date"].strftime("%A") if v.get("work_date") else None),
                        ("31A", any("31A protection" in x for x in r.readings)), ("record", bool(v.get("record_ref")))]
            else:
                keys = [("status", (v.get("day_status"), r.family)), ("section", v.get("hole_section")),
                        ("36A", any("36A protection" in x for x in r.readings))]
            for k in keys:
                feats.setdefault(k, ref)
        picks |= set(feats.values())
        out[c] = sorted(picks)
        field, code = UNSCHEDULED[c]
        base = next(r for r in w.claims.rows[lk] if r.ident == out[c][0])
        syn = copy.copy(base)
        syn.ident = f"{base.ident}#unscheduled"
        syn.values = {**base.values, field: code, "line_ref": syn.ident}
        extra[c].append(syn)
    return out, extra


# ----------------------------------------------------------------------------------------------- documents
def doc_text(doc) -> str:
    return (SNAPSHOT / doc.path).read_text(encoding="utf-8")


def _other(pools, contract, key, value) -> str:
    vals = pools.doc_values(contract, key, value)
    return vals[0] if vals else "??"


def cw_doc_mutations(text: str, doc, pools) -> list[tuple]:
    """(kind, field, variant, new text, probe texts or None): each record line dropped, garbled and written twice with
    another value; the narrative; the title; an unreadable day worked (probed by each real day of that week)."""
    lines = text.split("\n")
    out = [("doc", "title", "garble", "\n".join(["??"] + lines[1:]), [])]
    body_idx = [i for i, ln in enumerate(lines) if i and ln.strip() and ":" not in ln]
    for i, ln in enumerate(lines):
        if i == 0 or not ln.strip():
            continue
        key = ln.split(":", 1)[0] if i not in body_idx else "narrative"
        out.append(("doc", key, "drop", "\n".join(lines[:i] + lines[i + 1:]), None))
        out.append(("doc", key, "garble", "\n".join(lines[:i] + [("??" if key == "narrative" else f"{key}: ??")] + lines[i + 1:]), None))
        if key == "narrative":
            out.append(("doc", key, "twice", "\n".join(lines[:i + 1] + [ln] + lines[i + 1:]), None))
        else:
            out.append(("doc", key, "twice", "\n".join(lines[:i + 1] + [f"{key}: {_other(pools, 'CW', key, ln.split(':', 1)[1].strip())}"]
                                                      + lines[i + 1:]), None))
        if key == "Days on" and doc.week_beginning:
            days = [doc.week_beginning + dt.timedelta(days=k) for k in range(7)]
            probes = ["\n".join(lines[:i] + [ln + f", {DAYS[d.weekday()]} {d:%d/%m}"] + lines[i + 1:]) for d in days
                      if d not in doc.days_on]
            out.append(("doc", key, "append", "\n".join(lines[:i] + [ln + ", Xyz 99/99"] + lines[i + 1:]), probes))
    return out


def dds_doc_mutations(text: str, pools) -> list[tuple]:
    """Each header/part key dropped, garbled and (part keys) written twice with another value; each part dropped and its
    heading garbled; an unrecognisable tool term and crew entry (probed by each Appendix G term); each signature dropped
    and made a placeholder."""
    lines = text.split("\n")
    out = []
    part = None
    for i, ln in enumerate(lines):
        if i == 0 or not ln.strip():
            continue
        if ln.startswith("PART "):
            part = records_dds.PART_BY_TITLE.get(ln.strip())
            out.append(("heading", part, "garble", "\n".join(lines[:i] + ["PART ?? — ??"] + lines[i + 1:]), []))
            continue
        key = ln.split(":", 1)[0]
        sig = key in records_dds.SIG.values()
        name = key if (part is None or sig) else f"{part}.{key}"
        out.append(("doc", name, "drop", "\n".join(lines[:i] + lines[i + 1:]), None))
        out.append(("doc", name, "garble", "\n".join(lines[:i] + [f"{key}: ____" if sig else f"{key}: ??"] + lines[i + 1:]), None))
        if part is not None and not sig:
            other = _other(pools, "DDS", name, ln.split(":", 1)[1].strip())
            out.append(("doc", name, "twice", "\n".join(lines[:i + 1] + [f"{key}: {other}"] + lines[i + 1:]), None))
        if key in ("In the hole", "Tools in run"):
            probes = ["\n".join(lines[:i] + [ln + f", {t}"] + lines[i + 1:]) for t in sorted(records_dds.TOOL_TERMS)]
            out.append(("doc", name, "append", "\n".join(lines[:i] + [ln + ", unknown tool"] + lines[i + 1:]), probes))
        if key == "Crew on tour":
            probes = ["\n".join(lines[:i] + [ln + f", 3 {t}"] + lines[i + 1:]) for t in sorted(records_dds.CREW)]
            out.append(("doc", name, "append", "\n".join(lines[:i] + [ln + ", 3 unknown hands"] + lines[i + 1:]), probes))
    for p, spec in records_dds.SPEC["parts"].items():
        if spec["title"] in text:
            keep, skip = [], False
            for ln in lines:
                if ln.startswith("PART "):
                    skip = ln.strip() == spec["title"]
                elif ln.startswith("Signed"):
                    skip = False
                if not skip:
                    keep.append(ln)
            out.append(("part", p, "drop", "\n".join(keep), []))
    return out


def reparse(contract: str, doc, text: str):
    """The real G2 parser on the mutated text: (document, queued fields, fields written twice, unindexable, queue)."""
    q = Queue()
    if contract == "CW":
        d = records_cw.parse_file(doc.path, text, q)
        mine = [u for u in q.items if u.ident == d.ticket]
        return d, frozenset(u.field for u in mine), frozenset(u.field for u in mine if u.reason == "key repeated"), False, q
    d = records_dds.parse_file(doc.path, text, q)
    mine = [u for u in q.items if u.ident == d.file]
    return d, frozenset(u.field for u in mine), frozenset(u.field for u in mine if u.reason == "key repeated"), d.report is None, q


def left_empty(contract: str, d, gaps: frozenset, where: str, field: str) -> bool:
    """Whether G2 left the mutated field empty or unresolved (in scope); a garbled free-text value G2 accepts as a value
    (a report 'Well: ??', a record 'Job: ??') is neither."""
    if where in ("part", "heading") or field in gaps:
        return True
    if contract == "DDS":
        if field in records_dds.SIG.values():
            return not (d.company_signed if field == records_dds.SIG["company"] else d.driller_signed)
        if "." in field:
            part, key = field.split(".", 1)
            return d.parts.get(part, {}).get(key) is None
        return getattr(d, {"Report": "report", "Contract": "contract", "Well": "well", "Rig": "rig", "Date": "date"}[field]) is None
    if field in ("Signed (foreman)", "Countersigned (Engineer's representative)"):
        return not (d.foreman_signed if field == "Signed (foreman)" else d.engineer_signed)
    if field == "Days on":
        return not d.days_on
    attr = {"Area": "area", "Date": "date", "Week beginning": "week_beginning", "Ground": "ground", "narrative": "rule",
            "title": "family", "Job": "job"}.get(field)
    return attr is not None and getattr(d, attr) in (None, [], "")


# ----------------------------------------------------------------------------------------------- relevance probe
class Pools:
    """Other admissible values of each input, as the population itself shows them (no invented values)."""

    def __init__(self, w):
        self.claim = defaultdict(list)
        for kind, rows in w.claims.rows.items():
            for row in rows[:4000]:
                for k, v in row.values.items():
                    if v not in (None, "") and v not in self.claim[(kind, k)] and len(self.claim[(kind, k)]) < 6:
                        self.claim[(kind, k)].append(v)
        self.doc = defaultdict(list)
        for d in list(w.ddr.values())[:600]:
            part = None
            for ln in doc_text(d).split("\n")[1:]:
                if ln.startswith("PART "):
                    part = records_dds.PART_BY_TITLE.get(ln.strip())
                elif ":" in ln:
                    k, v = ln.split(":", 1)
                    k = f"{part}.{k}" if part and k not in records_dds.SIG.values() else k
                    if v.strip() not in self.doc["DDS " + k] and len(self.doc["DDS " + k]) < 6:
                        self.doc["DDS " + k].append(v.strip())
        for r in list(w.cw.values())[:600]:
            for ln in doc_text(r).split("\n")[1:]:
                if ":" in ln:
                    k, v = ln.split(":", 1)
                    if v.strip() not in self.doc["CW " + k] and len(self.doc["CW " + k]) < 6:
                        self.doc["CW " + k].append(v.strip())

    def claim_values(self, kind, field, current):
        vals = [v for v in self.claim[(kind, field)] if v != current][:3]
        if isinstance(current, dt.date):
            vals += [current + dt.timedelta(days=d) for d in (1, 35, -200, -400, 400)]
        if isinstance(current, Decimal):
            vals += [current * 2, current + 1, current / 2, Decimal(0)]
        return vals

    def doc_values(self, contract, key, current):
        vals = [v for v in self.doc[f"{contract} {key}"] if v != current][:3]
        bare = key.split(".", 1)[-1]
        if current is not None and str(current).isdigit():
            vals += [str(int(current) // 2), str(int(current) * 2 + 1), "0"]
        if bare == "Crew on tour":
            vals += [f"1 {t}" for t in sorted(records_dds.CREW)]
        if "hours" in bare:
            vals += ["24"]
        if bare.startswith(("Signed", "Countersigned")):
            vals += ["____"]
        if bare in ("In the hole", "Tools in run"):
            vals += sorted(records_dds.TOOL_TERMS)
        return vals


def _swap_value(text: str, key: str, value: str) -> str:
    return "\n".join(f"{key}: {value}" if ":" in ln and ln.split(":", 1)[0] == key else ln for ln in text.split("\n"))


# ----------------------------------------------------------------------------------------------- the sweep
def sweep(w, res, eng: Engines) -> tuple[list[str], dict]:
    """Direct evaluation of every (sample line, input, empty value), with G2's provenance for the line."""
    pools = Pools(w)
    errs, stats = [], defaultdict(int)
    picks, extra = sample(w, res)
    for c, (lk, hk) in KINDS.items():
        ctx = eng.context(c, w)
        rows = {r.ident: r for r in w.claims.rows[lk]} | {r.ident: r for r in extra[c]}
        hdrs = {r.ident: r for r in w.claims.rows[hk]}
        hkey = HKEY[c]
        for ref in picks[c] + [r.ident for r in extra[c]]:
            row = rows[ref]
            line = row.values
            header = hdrs[line[hkey]].values
            doc = (w.cw if c == "CW" else w.ddr).get(line.get(REF[c]) or "")
            inputs = ctx.get(ref.split("#")[0]) if eng.takes_inputs[c] else None
            base = eng.evaluate(c, line, header, doc, doc is not None, inputs)
            family = base.family
            stats[f"{c} family {family}"] += 1

            def judge(where, field, empty_val, mutated_fn, probes):
                stats["mutations"] += 1
                tag = f"{c} {ref} ({family}) {where} {field}={empty_val!r}"
                try:
                    m = mutated_fn()
                except Exception as e:  # noqa: BLE001
                    errs.append(f"{tag}: exception {type(e).__name__}: {e}")
                    stats["exceptions"] += 1
                    return
                if any(ch.finding == "engine_error" for ch in m.checks):
                    errs.append(f"{tag}: engine_error")
                    return
                try:
                    others = [p() for p in probes]
                except Exception as e:  # noqa: BLE001
                    errs.append(f"{tag}: exception on an admissible other value: {type(e).__name__}: {e}")
                    stats["exceptions"] += 1
                    return
                relevant = any(value_of(o) != value_of(base) for o in others)
                changed = value_of(m) != value_of(base)
                token = field.split(".", 1)[-1] if where == "doc" else field
                said = token in names(m) or (where in ("part", "heading") and (f"Part {field}" in names(m) or "part heading" in names(m)))
                registered = m.amount_status == "not_payable" and bool(set(m.findings) & REGISTERED.get((c, where, field), set()))
                informative = [o for o in others if o is not None] and not (len(probes) == 1 and where == "line" and field == hkey)
                if changed and not relevant and informative and not registered:
                    # no admissible value of the input changes the value, yet emptying it did: a known value lost
                    errs.append(f"{tag}: no admissible value of it changes the value, but the empty input changed it "
                                f"({m.amount_status}): a known value lost")
                    stats["lost"] += 1
                elif relevant or changed:
                    if not said:
                        errs.append(f"{tag}: the value depends on it but the result does not name it (silent)")
                        stats["silent"] += 1
                    elif m.amount_status == "determined" or (m.amount_status in ("conditional", "alternatives")
                                                             and not covers(m, [base] + others)):
                        errs.append(f"{tag}: the value depends on it but the result fixes a value ({m.amount_status}): a default")
                        stats["silent"] += 1
                    elif m.amount_status == "not_payable" and not (set(m.findings) & REGISTERED.get((c, where, field), set())):
                        errs.append(f"{tag}: not payable without the contract's own rule for this input ({m.findings})")
                        stats["silent"] += 1
                    else:
                        stats[{"unresolved": "explicit_unresolved", "not_payable": "registered"}.get(m.amount_status, "all_values_carried")] += 1
                else:
                    stats["irrelevant_unchanged"] += 1

            for ev in empties(lk, hkey):          # the join key: the line's header is not found
                judge("line", hkey, ev, lambda ev=ev: eng.evaluate(c, {**line, hkey: ev}, None, doc, doc is not None, inputs),
                      [lambda: eng.evaluate(c, line, header, doc, doc is not None, inputs)])
            for where, kind, cur in (("line", lk, line), ("header", hk, header)):
                for field in claim_fields(kind):
                    if field == hkey and where == "line":
                        continue
                    for ev in empties(kind, field):
                        if where == "line":
                            fn = lambda ev=ev, field=field: eng.evaluate(c, {**line, field: ev}, header, doc, doc is not None, inputs)  # noqa: E731
                            probes = [lambda v=v, field=field: eng.evaluate(c, {**line, field: v}, header, doc, doc is not None, inputs)
                                      for v in pools.claim_values(kind, field, cur.get(field))]
                        else:
                            fn = lambda ev=ev, field=field: eng.evaluate(c, line, {**header, field: ev}, doc, doc is not None, inputs)  # noqa: E731
                            probes = [lambda v=v, field=field: eng.evaluate(c, line, {**header, field: v}, doc, doc is not None, inputs)
                                      for v in pools.claim_values(kind, field, cur.get(field))]
                        judge(where, field, ev, fn, probes)
            if doc is None:
                continue
            text = doc_text(doc)

            def run_text(t, _doc=doc, _line=line, _header=header, _inputs=inputs):
                dd, gg, rr, uu, _q = reparse(c, _doc, t)
                inp = replace(_inputs or Inputs(), doc_gaps=gg, doc_repeated=rr, unindexed_reports=uu) if eng.takes_inputs[c] else None
                if c == "DDS" and (uu or dd.report != _line.get("report_ref")):
                    return eng.evaluate(c, _line, _header, None, False, inp)      # G2's index does not give it to this line
                return eng.evaluate(c, _line, _header, dd, True, inp)
            muts = cw_doc_mutations(text, doc, pools) if c == "CW" else dds_doc_mutations(text, pools)
            for where, field, variant, new, probe_texts in muts:
                d2, gaps, _rr, _uu, _q = reparse(c, doc, new)
                if not left_empty(c, d2, gaps, where, field):
                    stats["out_of_scope_value_accepted_by_G2"] += 1
                    continue
                if probe_texts is None:
                    probe_texts = []
                    if where == "doc" and field not in ("title", "narrative"):
                        key = field.split(".", 1)[-1] if c == "DDS" else field
                        current = next((ln.split(":", 1)[1].strip() for ln in text.split("\n")
                                        if ":" in ln and ln.split(":", 1)[0] == key), None)
                        probe_texts = [_swap_value(text, key, v) for v in pools.doc_values(c, field, current)]
                        if c == "DDS" and key in ("Run first day", "Run last day") and doc.date:
                            probe_texts.append(_swap_value(text, key, f"{doc.date:%d-%b-%Y}"))
                        if c == "CW" and field == "Days on" and doc.days_on:
                            probe_texts.append(_swap_value(text, key, ", ".join(f"{DAYS[d.weekday()]} {d:%d/%m}" for d in doc.days_on[:2])))
                judge(where, field, variant, lambda new=new: run_text(new), [lambda t=t: run_text(t) for t in probe_texts])
    return errs, dict(stats)


# ----------------------------------------------------------------------------------------------- the batch
def _sub_world(w, c, rows, docs=None, queue_items=(), unindex=()):
    """A copy of the world whose claim lines are `rows` (every other line of that contract left out), with documents
    replaced by `docs` and G2 queue entries added, as G2 would hand them over."""
    lk = KINDS[c][0]
    sub = copy.copy(w)
    sub.claims = copy.copy(w.claims)
    sub.claims.rows = {**w.claims.rows, lk: rows}
    sub.queue = copy.copy(w.queue)
    sub.queue.items = list(w.queue.items) + list(queue_items)
    if c == "CW":
        sub.cw = {**w.cw, **(docs or {})}
    else:
        sub.ddr = {k: v for k, v in {**w.ddr, **(docs or {})}.items() if k not in unindex}
    return sub


def _batch_once(eng: Engines, c, sub, label: str, errs: list) -> None:
    mod = eng.mod[c]
    lk, hk = KINDS[c]
    rows = sub.claims.rows[lk]
    try:
        out = mod.run(sub)
    except Exception as e:  # noqa: BLE001
        errs.append(f"{c} batch {label}: exception {type(e).__name__}: {e}")
        return
    if len(out) != len(rows):
        errs.append(f"{c} batch {label}: {len(out)} results for {len(rows)} lines")
    bad = [k for k, r in out.items() if any(ch.finding == "engine_error" for ch in r.checks)]
    if bad:
        errs.append(f"{c} batch {label}: engine_error on {bad[:3]}")
        return
    ctx = eng.context(c, sub)
    hdrs = {h.ident: h.values for h in sub.claims.rows[hk]}
    for row in rows:
        v = row.values
        ref = v.get(REF[c])
        doc = (sub.cw if c == "CW" else sub.ddr).get(ref) if ref else None
        direct = eng.evaluate(c, v, hdrs.get(v.get(HKEY[c])), doc, doc is not None, ctx.get(row.ident) if eng.takes_inputs[c] else None)
        got = out.get(v.get("line_ref") or row.ident)
        a = {k: x for k, x in direct.to_json().items() if k != "ctx"}
        b = {k: x for k, x in got.to_json().items() if k != "ctx"} if got is not None else None
        if a != b:
            errs.append(f"{c} batch {label}: {row.ident} differs from its direct evaluation")
            return


def batch(w, res, eng: Engines) -> tuple[list[str], int]:
    """The production run() over a sub-world of the sample lines, once per input: each claim field and header field
    emptied on every sample line, the header missing, and each document mutation applied to every sample document it
    fits. Returns (errors, number of batch runs)."""
    errs, runs = [], 0
    picks, extra = sample(w, res)
    pools = Pools(w)
    for c, (lk, hk) in KINDS.items():
        keep = set(picks[c])
        base_rows = [r for r in w.claims.rows[lk] if r.ident in keep] + extra[c]
        hkey = HKEY[c]
        # claim line fields, the join key, and a header G2 does not have
        for field in claim_fields(lk) + ["<header missing>"]:
            rows = []
            for row in base_rows:
                r2 = copy.copy(row)
                r2.values = dict(row.values)
                if field == "<header missing>":
                    r2.values[hkey] = f"NO-SUCH-{r2.values[hkey]}"
                elif field != "line_ref":
                    r2.values[field] = empties(lk, field)[-1]
                rows.append(r2)
            _batch_once(eng, c, _sub_world(w, c, rows), f"with line {field} empty", errs)
            runs += 1
        # header fields: emptied on the headers of the sample lines
        hids = {r.values[hkey] for r in base_rows}
        for field in claim_fields(hk):
            if field == hkey:
                continue
            sub = _sub_world(w, c, base_rows)
            hrows = []
            for h in w.claims.rows[hk]:
                if h.ident in hids:
                    h2 = copy.copy(h)
                    h2.values = {**h.values, field: empties(hk, field)[-1]}
                    hrows.append(h2)
                else:
                    hrows.append(h)
            sub.claims.rows = {**sub.claims.rows, hk: hrows}
            _batch_once(eng, c, sub, f"with header {field} empty", errs)
            runs += 1
        # documents: each mutation (field, variant) applied to every sample document it fits
        store = w.cw if c == "CW" else w.ddr
        docs = {}
        for row in base_rows:
            ref = row.values.get(REF[c])
            if ref and ref in store:
                docs[ref] = store[ref]
        by_key = defaultdict(dict)
        for ref, doc in docs.items():
            text = doc_text(doc)
            muts = cw_doc_mutations(text, doc, pools) if c == "CW" else dds_doc_mutations(text, pools)
            for where, field, variant, new, _p in muts:
                d2, gaps, _rr, unidx, q = reparse(c, doc, new)
                if left_empty(c, d2, gaps, where, field):
                    by_key[(where, field, variant)].setdefault(ref, (d2, q.items, unidx))
        for (where, field, variant), changed in sorted(by_key.items(), key=lambda kv: str(kv[0])):
            new_docs = {ref: d2 for ref, (d2, _q, unidx) in changed.items() if not unidx}
            unindex = {ref for ref, (_d, _q, unidx) in changed.items() if unidx}
            items = [u for _r, (_d, q, _u) in changed.items() for u in q]
            items += [Unresolved("ddr", store[ref].file, "Report", "no report number; not indexable") for ref in unindex]
            _batch_once(eng, c, _sub_world(w, c, base_rows, new_docs, items, unindex), f"with {where} {field} {variant}", errs)
            runs += 1
    return errs, runs


def x8(w, res, eng: Engines) -> tuple[list[str], dict]:
    errs, stats = sweep(w, res, eng)
    b, runs = batch(w, res, eng)
    stats["batch_runs"] = runs
    return errs + b, stats
