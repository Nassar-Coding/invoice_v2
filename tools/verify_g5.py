"""G5 exit checks (plan §2, G5): full invoice outcomes.

Exit condition: "Every invoice has check coverage, findings, amount status and an evidence trail; monetary and procedural
outcomes remain distinct; independently reviewed complete invoices reconcile step by step." Checks:

  Z1 one outcome per template invoice: exactly the 2,806 template ids, each once; submission.csv has the six template
     columns in template order, binary flags, a category exactly when flagged, integer minor units, billed cents equal
     to 100 x the judged header field (application_total / invoice_total), confidence in [0, 1].
  Z2 check coverage: every invoice has a recorded status for each of the twelve checks, and its lines are exactly the
     claim lines that carry its number (every line through G3 and G4).
  Z3 findings and evidence trail: a flagged invoice names at least one established finding with its line or header, its
     category is exactly the root categories of those findings (every finding code mapped); an unflagged invoice has no
     finding under any scenario.
  Z4 monetary and procedural outcomes distinct: a flag resting only on procedural or payment-only findings keeps the
     contract value as its expected total (no blanket zero); and billing is never authority - changing every billed
     amount and header total changes no expected total.
  Z5 independent sample: every reader's flag and expected total agree with the engine or carry a live settlement
     (verification/g5/sample_dispositions.yaml); the comparison reproduces; packets committed before the readers'
     outputs and both before the G5 engine (git).
  Z6 reconciliation step by step (and G5-B04: the legal combinations, joined line by line without the engine's list of
     open dimensions, give exactly its formed totals): every expected total is recomputed from the outcome's line values (civil:
     their sum; drilling: services, DS-900 = -4% of the excess over 250,000, net, VAT 15%, total, rounding half-even with
     exact rational arithmetic) and every cents figure from its decimal.
  Z7 ambiguity rule: flag = 0 only when the invoice is correct under every scenario; a flag where scenarios disagree has
     confidence 0.50; the confidence follows the rubric (Q9-5) in every band; no row above 0.80 depends on an unsupplied
     fact.
  Z8 decisions and registers: every spec/g5_decisions.yaml entry has a computed effect; no question still blocks G5; every
     question G5 owned carries a g5_disposition; the owner's decisions are recorded as the owner's.
  Z9 reproduction and boundary: the committed verification/g5 outputs reproduce; G3 results and G4 state are unchanged by
     G5.

Usage::  python tools/verify_g5.py
"""
from __future__ import annotations

import copy
import csv
import io
import json
import subprocess
import sys
from decimal import Decimal
from fractions import Fraction
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))

import g5_sample_compare as SC  # noqa: E402
from audit import g4_run, g5_run  # noqa: E402
from audit.common import SNAPSHOT  # noqa: E402
from audit.g3_core import result_keys  # noqa: E402
from audit.g4_core import base  # noqa: E402
from audit.g5_outcomes import (CATEGORY, CATEGORY_ORDER, FACT_DIMS, PAYMENT_ONLY, PROCEDURAL, Engine, options,  # noqa: E402
                               template_ids)

OUT = ROOT / "verification" / "g5"
DECISIONS = ROOT / "spec" / "g5_decisions.yaml"
QUESTIONS = ROOT / "spec" / "open_questions.yaml"


def D(x):
    return None if x in (None, "") else Decimal(str(x))


def git_first_commit(path: str) -> str | None:
    out = subprocess.run(["git", "log", "--diff-filter=A", "--format=%H", "--", path], cwd=ROOT, capture_output=True, text=True)
    hs = out.stdout.split()
    return hs[-1] if hs else None


def strictly_before(a, b) -> bool:
    if not a or not b or a == b:
        return False
    return subprocess.run(["git", "merge-base", "--is-ancestor", a, b], cwd=ROOT).returncode == 0


# ============================================================================== Z1
def z1(out: dict, ids: list[str], headers: dict, sub_text: str) -> list[str]:
    errs = []
    if len(ids) != 2806 or len(set(ids)) != len(ids):
        errs.append(f"template has {len(ids)} ids ({len(set(ids))} unique), expected 2806 unique")
    missing = [i for i in ids if i not in out]
    extra = [i for i in out if i not in set(ids)]
    errs += [f"{i}: no outcome" for i in missing[:10]] + [f"{i}: outcome not in the template" for i in extra[:10]]
    rows = list(csv.DictReader(io.StringIO(sub_text)))
    head = sub_text.splitlines()[0].split(",") if sub_text else []
    if head != g5_run.COLUMNS:
        errs.append(f"submission columns {head} are not the template's {g5_run.COLUMNS}")
    if [r["invoice_id"] for r in rows] != ids:
        errs.append("submission rows are not the template ids in template order, each once")
    for r in rows:
        i = r["invoice_id"]
        if r["flagged"] not in ("0", "1"):
            errs.append(f"{i}: flagged {r['flagged']!r} is not binary")
            continue
        if (r["flagged"] == "1") != bool(r["error_category"]):
            errs.append(f"{i}: category {'missing on a flagged' if r['flagged'] == '1' else 'present on an unflagged'} row")
        for col in ("expected_total_cents", "billed_total_cents"):
            if not r[col].lstrip("-").isdigit():
                errs.append(f"{i}: {col} {r[col]!r} is not an integer")
        h = headers.get(i)
        if h is not None:
            field = "application_total" if i.startswith("PA-") else "invoice_total"
            if r["billed_total_cents"].lstrip("-").isdigit() and int(r["billed_total_cents"]) != int(D(h[field]) * 100):
                errs.append(f"{i}: billed_total_cents {r['billed_total_cents']} is not 100 x {field} {h[field]}")
        try:
            c = Decimal(r["confidence"])
            if not Decimal(0) <= c <= Decimal(1):
                errs.append(f"{i}: confidence {c} outside [0, 1]")
        except Exception:
            errs.append(f"{i}: confidence {r['confidence']!r} is not a number")
    return errs


# ============================================================================== Z2
def z2(out: dict, eng: Engine, w) -> list[str]:
    errs = []
    for lk, key in (("cw_lines", "application_no"), ("dds_lines", "invoice_no")):
        claim = {}
        for k, row in zip(result_keys(w.claims.rows[lk]), w.claims.rows[lk]):
            claim.setdefault(row.values.get(key), set()).add(k)
        c = "CW" if lk == "cw_lines" else "DDS"
        for no, inv in eng.inv[c].items():
            if {k for k, _v, _g in inv.lines} != claim.get(no, set()):
                errs.append(f"{no}: its lines are not the claim lines that carry its number")
    for i, o in out.items():
        cov = o.get("coverage") or {}
        for n in range(1, 13):
            if cov.get(str(n)) in (None, "not made", {}):
                errs.append(f"{i}: check {n} has no recorded status")
    return errs


# ============================================================================== Z3
def z3(out: dict) -> list[str]:
    errs = []
    for i, o in out.items():
        codes = [f.split("@")[0] for f in o["findings"]]
        unmapped = [c for c in codes if c not in CATEGORY]
        if unmapped:
            errs.append(f"{i}: finding(s) {unmapped} have no category")
        if o["flagged"]:
            if not o["findings"]:
                errs.append(f"{i}: flagged without a finding")
            cats = sorted({CATEGORY[c] for c in codes if c in CATEGORY}, key=CATEGORY_ORDER.index)
            if o["error_category"] != "; ".join(cats):
                errs.append(f"{i}: category {o['error_category']!r} is not the root categories of its findings {cats}")
        else:
            if o["wrong_under"]:
                errs.append(f"{i}: unflagged although wrong under {o['wrong_under'][:2]}")
            if o["findings"] or o["error_category"]:
                errs.append(f"{i}: unflagged with findings or a category")
    return errs


# ============================================================================== Z4
def z4(out: dict, perturbed: dict | None = None) -> list[str]:
    errs = []
    for i, o in out.items():
        codes = {f.split("@")[0] for f in o["findings"]}
        if o["flagged"] and codes and all(CATEGORY.get(c) in PROCEDURAL or c in PAYMENT_ONLY for c in codes):
            if D(o["expected_total"]) != D(o["billed_total"]) and not o["right_under"]:
                errs.append(f"{i}: a procedural/payment-only flag changed the expected total "
                            f"({o['billed_total']} -> {o['expected_total']})")
            if D(o["expected_total"]) == 0 and D(o["billed_total"]) != 0:
                errs.append(f"{i}: procedural breach valued at zero")
    if perturbed is not None:
        for i, o in out.items():
            p = perturbed.get(i)
            if p is None or D(p["expected_total"]) != D(o["expected_total"]):
                errs.append(f"{i}: the expected total moves with the billed figures ({o['expected_total']} -> "
                            f"{None if p is None else p['expected_total']})")
    return errs


def perturb_billing(w):
    """A copy of the world whose billed line amounts, rates and header totals are all changed."""
    w2 = copy.copy(w)
    w2.claims = copy.copy(w.claims)
    w2.claims.rows = {}
    for k, rows in w.claims.rows.items():
        new = []
        for r in rows:
            r2 = copy.copy(r)
            r2.values = dict(r.values)
            for f in ("amount", "rate_applied", "unit_rate", "application_total", "invoice_total", "net_amount", "vat_amount",
                      "retention", "net_payable"):
                if isinstance(r2.values.get(f), Decimal):
                    r2.values[f] = r2.values[f] * Decimal("1.37") + Decimal("11.11")
            new.append(r2)
        w2.claims.rows[k] = new
    return w2


# ============================================================================== Z5
def z5(result: dict, dispositions: dict, first_commit=git_first_commit, before=strictly_before) -> list[str]:
    errs = []
    live = set()
    for i, e in result.items():
        if not e["readers"]:
            errs.append(f"{i}: no independent result")
        for r, ds in e["readers"].items():
            for d in ds:
                k = f"{i}|{r}|{d}"
                live.add(k)
                if k not in dispositions:
                    errs.append(f"{k}: disagrees with the independent expected outcome and has no settlement")
                elif dispositions[k].get("settled") not in ("engine", "both", "presentation"):
                    errs.append(f"{k}: settlement {dispositions[k].get('settled')!r} is not a closed settlement")
    errs += [f"{k}: settlement no longer matches a disagreement (stale)" for k in dispositions if k not in live]
    packets = sorted(str(p.relative_to(ROOT)) for p in (OUT / "samples").glob("packet_*.jsonl"))
    readers = sorted(str(p.relative_to(ROOT)) for p in (OUT / "samples").glob("expected_*.jsonl"))
    engine = "audit/g5_outcomes.py"
    for p in packets:
        for x in readers + [engine]:
            if not before(first_commit(p), first_commit(x)):
                errs.append(f"{p} was not committed before {x}")
    for x in readers:
        if not before(first_commit(x), first_commit(engine)):
            errs.append(f"{x} was not committed before {engine}")
    return errs


# ============================================================================== Z6
def _half_even_frac(x: Fraction) -> Fraction:
    """Round to cents, half to even, in exact rational arithmetic (independent of decimal quantize)."""
    c = x * 100
    n, r = divmod(c.numerator, c.denominator)
    rem = Fraction(r, c.denominator)
    if rem > Fraction(1, 2) or (rem == Fraction(1, 2) and n % 2 == 1):
        n += 1
    return Fraction(n, 100)


def z6(out: dict) -> list[str]:
    errs = []
    for i, o in out.items():
        vals = o["line_values"]
        if any(v is None for v in vals.values()):
            continue
        s = sum((Fraction(Decimal(v)) for v in vals.values()), Fraction(0))
        if o["contract"] == "CW":
            tot = s
        else:
            ds = -_half_even_frac((s - 250000) * Fraction(4, 100)) if s > 250000 else Fraction(0)
            net = s + ds
            tot = net + _half_even_frac(net * Fraction(15, 100))
        exp = D(o["expected_total"])
        if o["formed"] and Fraction(exp) != tot:
            errs.append(f"{i}: expected total {exp} does not reconcile with its lines ({float(tot):.2f})")
        c = g5_run.cents(exp)
        if c != int(Fraction(exp) * 100):
            errs.append(f"{i}: cents {c} is not 100 x {exp}")
    return errs


def joint_errors(out: dict, eng: Engine) -> list[str]:
    """G5-B04, independent of the engine's collection of open dimensions: the legal combinations of an invoice are built
    by joining its lines' alternatives directly - two alternatives combine only where they agree on every dimension they
    share, so independent groups combine freely and one group's choice is never imposed on another. The readings the
    register decides, the owner's Q7 C choices and the invoice's facts under the adopted fact rule fix their
    dimensions. The joined totals (civil: the sum; drilling: services, DS-900, VAT) must be exactly the engine's
    formed totals, and the invoice formed exactly when every legal combination values every line."""
    errs = []
    p = eng.policy
    for i, o in out.items():
        inv = eng.inv[o["contract"]][i]
        states = {((), ())}
        for key, v, g in inv.lines:
            if inv.contract == "DDS" and g.g3.code == "DS-900":
                continue
            if g.r.payable is False:
                states = {(a, vals + (Decimal(0),)) for a, vals in states}
                continue
            fixed = dict(p.decided)
            if p.q7c == "earlier":
                fixed.update({d: s[0] for d, s in eng.stands.get(key, {}).items() if not s[1]})
            fixed.update(fact_values(eng, inv, key, v, g))
            # a civil line's ground class is its own fact (its own work area and day): local to the line in the join;
            # a well's class is one fact for all its services (joint)
            opts = [({(f"{k}@{key}" if k == "ground" else k): y for k, y in d.items()}, x) for d, x in options(g)
                    if all(fixed.get(k, y) == y for k, y in d.items())]
            new = set()
            for a, vals in states:
                ad = dict(a)
                for d, x in opts:
                    if all(ad.get(k, y) == y for k, y in d.items()):
                        amt = D(x.get("amount"))
                        new.add((tuple(sorted({**ad, **d}.items())), vals + (amt,)))
            states = new
        formed = bool(states) and all(None not in vals for _a, vals in states)
        totals = set()
        for _a, vals in states:
            if None in vals:
                continue
            s = sum(vals, Decimal(0))
            if inv.contract == "DDS":
                ds = -(((s - 250000) * Decimal("0.04")).quantize(Decimal("0.01"), rounding="ROUND_HALF_EVEN")) if s > 250000 else 0
                net = s + ds
                s = net + (net * Decimal("0.15")).quantize(Decimal("0.01"), rounding="ROUND_HALF_EVEN")
            totals.add(s)
        if formed != o["formed"]:
            errs.append(f"{i}: {'every' if formed else 'not every'} legal combination values every line, the engine says "
                        f"formed={o['formed']}")
        elif formed and totals != {D(t) for t in o["totals"]}:
            errs.append(f"{i}: legal combinations give totals {sorted(map(str, totals))[:6]}, the engine "
                        f"{o['totals'][:6]}")
    return errs


def fact_values(eng: Engine, inv, key, v, g) -> dict:
    """The fact dimensions the adopted fact rule fixes on this line (the rule itself is the engine's policy)."""
    return {d: x for d, x in eng.fixed_for(inv, key, v, g, {}).items() if base(d) in FACT_DIMS}


# ============================================================================== Z7
def z7(out: dict) -> list[str]:
    errs = []
    for i, o in out.items():
        wrong, right = o["wrong_under"], o["right_under"]
        c = D(o["confidence"])
        if o["flagged"] == 0 and wrong:
            errs.append(f"{i}: not flagged although wrong under {wrong[:2]}")
        if o["flagged"] == 1 and not wrong and not (o.get("fact_dependent") and c <= Decimal("0.30")):
            errs.append(f"{i}: flagged although correct under every scenario")
        if wrong and right and c != Decimal("0.50"):
            errs.append(f"{i}: scenarios disagree but confidence is {c}, not 0.50")
        if wrong and not right and len(o["totals"]) > 1 and c > Decimal("0.60"):
            errs.append(f"{i}: totals disagree across scenarios but confidence is {c}")
        if (o["fact_dependent"] or o["nomination_dependent"]) and c > Decimal("0.80"):
            errs.append(f"{i}: rests on an unsupplied fact but confidence is {c}")
        if not o["formed"] and c > Decimal("0.30"):
            errs.append(f"{i}: total not formed but confidence is {c}")
        if c not in {Decimal(x) for x in ("0.95", "0.80", "0.60", "0.50", "0.30")}:
            errs.append(f"{i}: confidence {c} is not a rubric value")
    return errs


# ============================================================================== Z8
def z8(decisions: dict, effects: dict, questions: dict) -> list[str]:
    errs = []
    keys = set(effects)
    for d in decisions["decisions"]:
        k = d.get("effect_key")
        if k not in keys:
            errs.append(f"{d['id']}: effect {k} not computed")
        if d["id"] in ("Q7C",) and d.get("decided_by") != "owner":
            errs.append(f"{d['id']}: the owner's decision is not recorded as the owner's")
    for k in ("Q6", "Q6-day0", "Q8-class", "PD210-nomination", "Q1", "Q2", "Q12", "Q9"):
        if k not in keys:
            errs.append(f"decision effect {k} not computed")
    if "q9_rule" not in decisions:
        errs.append("no Q9 rule")
    for q in questions["questions"]:
        if q.get("blocks") == "G5":
            errs.append(f"{q['id']}: still blocks G5")
        if q.get("originally_blocks") in ("G5", "G7") or q["id"] in ("Q1", "Q4", "Q5", "Q6", "Q7", "Q8", "Q11", "Q12", "Q14"):
            if not q.get("g5_disposition"):
                errs.append(f"{q['id']}: G5 item without a g5_disposition")
    q7 = next(q for q in questions["questions"] if q["id"] == "Q7")
    if "owner" not in str(q7.get("decided_by", "")):
        errs.append("Q7: the owner's decision is not recorded as the owner's")
    return errs


# ============================================================================== Z9
def z9(committed: dict, fresh: dict, g34_before: str | None = None, g34_after: str | None = None) -> list[str]:
    errs = [f"verification/g5/{k} does not reproduce from the current code and inputs" for k, v in fresh.items()
            if committed.get(k) != v]
    if g34_before is not None and g34_before != g34_after:
        errs.append("G3 results or G4 state changed while G5 ran")
    return errs


def g34_digest(res, st) -> str:
    import hashlib
    h = hashlib.sha256()
    for c in ("CW", "DDS"):
        for k in sorted(res[c]):
            h.update(json.dumps(res[c][k].to_json(), sort_keys=True, default=str).encode())
        for k in sorted(st[c].lines):
            g = st[c].lines[k]
            h.update(json.dumps(g.to_json(), sort_keys=True, default=str).encode())
    return h.hexdigest()


def fresh_outputs(w, st, eng, out, ids) -> dict:
    for o in out.values():
        o["coverage"] = g5_run.coverage(eng.inv[o["contract"]][o["invoice_id"]])
    return {"outcomes.jsonl": "".join(json.dumps(g5_run.serial(out[i]), sort_keys=True) + "\n"
                                      for i in ids + sorted(set(out) - set(ids)) if i in out),
            "summary.json": json.dumps(g5_run.summary(w, eng, out, ids), indent=1, default=str) + "\n",
            "submission.csv": g5_run.submission_csv(g5_run.submission_rows(out, ids)),
            "decision_effects.json": json.dumps(g5_run.decision_effects(w, st, out), indent=1, default=str) + "\n"}


def main() -> int:
    w, res, st = g4_run.run_g4()
    before = g34_digest(res, st)
    eng = Engine(w, st)
    out = eng.run()
    ids = template_ids(SNAPSHOT)
    fresh = fresh_outputs(w, st, eng, out, ids)
    after = g34_digest(res, st)
    serial = {i: g5_run.serial(o) for i, o in out.items()}
    headers = {h.values.get("application_no") or h.values.get("invoice_no"): h.values
               for k in ("cw_headers", "dds_headers") for h in w.claims.rows[k]}
    perturbed = {i: g5_run.serial(o) for i, o in Engine(perturb_billing(w), st).run().items()}
    cmp_ = SC.compare(serial)
    disp = (yaml.safe_load((OUT / "sample_dispositions.yaml").read_text()) or {}).get("dispositions", {})
    load = lambda p: yaml.safe_load(p.read_text())  # noqa: E731
    committed = {k: (OUT / k).read_text() if (OUT / k).exists() else None for k in fresh}
    checks = [
        ("Z1 one outcome per template invoice; submission.csv in the template format", lambda: z1(serial, ids, headers, fresh["submission.csv"])),
        ("Z2 every invoice has a status for each of the twelve checks over exactly its claim lines", lambda: z2(serial, eng, w)),
        ("Z3 findings and evidence trail: flag <-> findings, category = root categories", lambda: z3(serial)),
        ("Z4 monetary and procedural outcomes distinct; billing never authority for an expected total", lambda: z4(serial, perturbed)),
        ("Z5 independently reviewed invoices agree (or carry a live settlement); inputs before outputs (git)",
         lambda: z5(cmp_, disp) + ([] if json.loads((OUT / "sample_comparison.json").read_text()) ==
                                   json.loads(json.dumps(cmp_, sort_keys=True)) else ["verification/g5/sample_comparison.json does not reproduce"])),
        ("Z6 every expected total reconciles step by step with its lines (independent rational arithmetic); the legal "
         "combinations joined line by line give exactly the engine's formed totals", lambda: z6(serial) + joint_errors(out, eng)),
        ("Z7 ambiguity rule and confidence rubric", lambda: z7(serial)),
        ("Z8 decisions and registers: effects computed, no question blocks G5, owner decisions recorded",
         lambda: z8(load(DECISIONS), json.loads(fresh["decision_effects.json"]), load(QUESTIONS))),
        ("Z9 committed G5 outputs reproduce; G3/G4 untouched by G5", lambda: z9(committed, fresh, before, after)),
    ]
    ok = True
    s = json.loads(fresh["summary.json"])
    print(f"G5 population: {len(out)} outcomes for {len(ids)} template ids; flagged CW {s['contracts']['CW']['flagged']} / "
          f"DDS {s['contracts']['DDS']['flagged']}; run context {w.run_context['id']}")
    for name, fn in checks:
        e = fn()
        print(("PASS " if not e else "FAIL ") + name)
        for x in e[:20]:
            print("     -", x)
        if len(e) > 20:
            print(f"     ... {len(e) - 20} more")
        ok = ok and not e
    print("G5 VERIFY OK" if ok else "G5 VERIFY FAILED")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
