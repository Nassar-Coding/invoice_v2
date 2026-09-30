"""G6 independent review samples (plan §2 G6: 'review ... samples of apparent passes'; §10 population review).

Two seeded random samples drawn from the COMPLETE population, stratified by the exported flag: unflagged invoices (the
search for false negatives - apparent passes) and flagged invoices (the search for false positives). The flag is used
only to choose the stratum; the packets carry nothing from the implementation: each gives the invoice as billed, every
record or report its lines cite, the raw cross-invoice context (tools/g5_samples.py cw_packet / dds_packet) and the
adopted decisions as premises. Isolated readers (prompts/phase3/g6_independent_review_v1.md) decide each invoice from the
contract scans and records alone; tools/g6_sample_compare.py compares them with the exported outcomes.

Usage::  python tools/g6_samples.py      (writes verification/g6/samples/packet_*.jsonl, meta.yaml)
"""
from __future__ import annotations

import json
import random
import sys
from collections import defaultdict
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "tools"))
import g5_samples as S5  # noqa: E402

OUT = ROOT / "verification" / "g6" / "samples"
SEED = 6606
N = {("CW", 0): 12, ("CW", 1): 6, ("DDS", 0): 8, ("DDS", 1): 4}
MAX_DDS_LINES = 30          # a reader can work through at most this many drilling lines with their reports

PREMISES = [
    "Flag semantics: an invoice is wrong when any of the twelve checks fails on it - a line whose contract value differs "
    "from its billed value, a header whose arithmetic does not reconcile, an established breach with no monetary effect "
    "(identity/contract reference, term, period, submission window, missing/unsigned/mismatched evidence), or a payment "
    "defect the contract makes this invoice carry (an adjustment or retention release omitted, wrong or unsupported). "
    "flagged = 1 when wrong, 0 when every check passes.",
    "Judged total: civil application_total = the measured total (sum of line amounts; the A3 adjustment and retention are "
    "payment fields outside it, 45A p32); drilling invoice_total = net + VAT, net = charges incl. DS-900 (Cl.36-40 p8).",
    "Readings adopted from the contract text: civil Contract Year resets on 5 January 2026; drilling on its anniversary; "
    "a measurement unpaid for want of its record still counts as measured for bands; for civil duplicates (Cl.44) 'the "
    "later measurement' is the one on the later-submitted application, within one application the later line; a weekly "
    "item is measured by the week; only what the contract requires is added (no unbilled events added).",
    "Owner decisions: (Q7 C) of two admissible charges of one drilling service for one well-day, run, well or loss, the "
    "charge on the earlier-submitted invoice stands and the later one is the repeat; (Q6 D) whether the day of the "
    "A.14.010 measurement itself is excluded for A.14.020 is left open - report both.",
    "Readings left open (report each alternative that changes the outcome in `alternatives`): the A3 adjustment "
    "recipient ('on or after' 31A/36A vs 'after' A3, same-day ties); the hour readings of 21A and Schedule 8 "
    "(DD-120/RM-530/HC-630); the order of civil measurements of one date at a band edge.",
    "Facts assigned to documents NOT supplied: the drilling well class (call-off, Cl.4), the civil ground class of a line no "
    "supplied record classifies (S4, Cl.5), the PD-210 section nomination (Cl.23). The invoice's own statement of such a "
    "fact is a claim, not evidence. Decide whether the invoice is right under SOME admissible value of the missing "
    "document (then it is not wrong for that reason) or wrong under every admissible value; say which values you tried.",
    "Accepted as stated: the civil zone of execution and night working stated on the line. Procedural breaches "
    "(submission window, period, contract reference) are findings that do not remove a line's value. An unsigned Daily "
    "Drilling Report makes the Schedule 5 services it evidences not payable. A charge whose required record or Schedule 5 "
    "part is not delivered is not payable in the invoice that carries it.",
]


def main() -> int:
    s = S5.build()
    s["wd"] = defaultdict(list)
    for r in s["dl"]:
        s["wd"][(r["well_name"], r["service_date"], r["service_code"])].append(r)
    outcomes = {}
    for line in (ROOT / "verification" / "g5" / "outcomes.jsonl").read_text().splitlines():
        o = json.loads(line)
        outcomes[o["invoice_id"]] = o["flagged"]
    rnd = random.Random(SEED)
    pick = {}
    for (c, f), n in N.items():
        pool = sorted(i for i, fl in outcomes.items() if fl == f and (i.startswith("PA-") if c == "CW" else i.startswith("MDS-")))
        if c == "DDS":
            pool = [i for i in pool if len(s["dby"][i]) <= MAX_DDS_LINES]
        for i in rnd.sample(pool, n):
            pick[i] = f"random {'unflagged' if f == 0 else 'flagged'} {c} (seed {SEED}" + \
                      (f", at most {MAX_DDS_LINES} lines" if c == "DDS" else "") + ")"
    S5.PREMISES[:] = PREMISES
    idx = S5.report_index()
    cw = [S5.cw_packet(a, why, s) for a, why in pick.items() if a.startswith("PA-")]
    dds = [S5.dds_packet(i, why, s, idx) for i, why in pick.items() if i.startswith("MDS-")]
    for p in cw + dds:
        p["given"] = PREMISES
    packets = {"packet_cw_a.jsonl": cw[0::3], "packet_cw_b.jsonl": cw[1::3], "packet_cw_c.jsonl": cw[2::3],
               "packet_dds_a.jsonl": dds[0::3], "packet_dds_b.jsonl": dds[1::3], "packet_dds_c.jsonl": dds[2::3]}
    OUT.mkdir(parents=True, exist_ok=True)
    for name, ps in packets.items():
        (OUT / name).write_text("".join(json.dumps(p, ensure_ascii=False) + "\n" for p in ps))
    (OUT / "meta.yaml").write_text(yaml.safe_dump({"seed": SEED, "strata": {f"{c}/{'flagged' if f else 'unflagged'}": n
                                                                            for (c, f), n in N.items()},
                                                   "why": pick, "packets": {k: [p["id"] for p in v] for k, v in packets.items()}},
                                                  sort_keys=False, width=140))
    print({k: [(p["id"], len(p["lines"])) for p in v] for k, v in packets.items()})
    return 0


if __name__ == "__main__":
    sys.exit(main())
