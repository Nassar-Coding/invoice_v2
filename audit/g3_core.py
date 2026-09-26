"""G3 shared core: calculation traces, rounding, check results and the per-line result (both contracts).

A Trace is a list of steps, each recording the operation, its operand(s), the result and the source it relies on.
tools/verify_g3.py replays every trace with its own arithmetic, so each amount's explanation is checked rather than
trusted. Only local entitlement is decided here; anything needing other lines or invoices is listed as a G4
dependency on the result, never applied.
"""
from __future__ import annotations

from dataclasses import dataclass, field
from decimal import ROUND_HALF_EVEN, ROUND_HALF_UP, Decimal

CENT = Decimal("0.01")
ROUNDING = {"half_up": ROUND_HALF_UP, "half_even": ROUND_HALF_EVEN}


def q(x: Decimal, mode: str) -> Decimal:
    return x.quantize(CENT, rounding=ROUNDING[mode])


class Trace:
    """Exact, replayable calculation steps. `value` after each step is the running result."""

    def __init__(self):
        self.steps: list[dict] = []
        self.value: Decimal | None = None

    def start(self, label: str, value: Decimal, source: str) -> Decimal:
        self.value = value
        self.steps.append({"op": "start", "label": label, "value": str(value), "source": source})
        return value

    def mul(self, label: str, factor: Decimal, source: str) -> Decimal:
        self.value = self.value * factor
        self.steps.append({"op": "mul", "label": label, "factor": str(factor), "value": str(self.value), "source": source})
        return self.value

    def div(self, label: str, divisor: Decimal, source: str) -> Decimal:
        self.value = self.value / divisor
        self.steps.append({"op": "div", "label": label, "divisor": str(divisor), "value": str(self.value), "source": source})
        return self.value

    def round(self, label: str, mode: str, source: str) -> Decimal:
        self.value = q(self.value, mode)
        self.steps.append({"op": "round", "label": label, "mode": mode, "value": str(self.value), "source": source})
        return self.value

    def note(self, label: str, source: str, **facts) -> None:
        self.steps.append({"op": "note", "label": label, "source": source, **{k: str(v) for k, v in facts.items()}})

    def amount(self, quantity: Decimal, rate: Decimal, source: str) -> Decimal:
        v = quantity * rate
        self.steps.append({"op": "amount", "label": "amount = quantity x rate", "quantity": str(quantity), "rate": str(rate),
                           "value": str(v), "source": source})
        return v

    def part(self, label: str, quantity: Decimal, rate: Decimal, source: str) -> Decimal:
        v = quantity * rate
        self.steps.append({"op": "part", "label": label, "quantity": str(quantity), "rate": str(rate), "value": str(v), "source": source})
        return v

    def total(self, label: str, source: str) -> Decimal:
        parts = [Decimal(s["value"]) for s in self.steps if s["op"] == "part"]
        v = sum(parts, Decimal("0"))
        self.steps.append({"op": "sum_parts", "label": label, "value": str(v), "source": source})
        return v


@dataclass
class Check:
    check: str                  # identity | term | window | period | unit | evidence | identification | quantity | rate | arithmetic | status
    status: str                 # pass | finding | unresolved | n/a
    rule: str
    clause: str
    finding: str | None = None
    detail: str = ""


@dataclass
class LineResult:
    contract: str
    line_ref: str
    code: str
    family: str | None = None             # the quantity route the engine valued it under (spec/g3_code_families.yaml)
    checks: list[Check] = field(default_factory=list)
    unit_rate: Decimal | None = None
    allowed_quantity: Decimal | None = None
    amount: Decimal | None = None
    payable: bool | None = None
    amount_status: str = "determined"      # determined | not_payable | alternatives | conditional | deferred | unresolved
    reasons: list[str] = field(default_factory=list)
    alternatives: dict = field(default_factory=dict)   # reading -> {allowed_quantity, amount, question}
    g4_dependencies: list[str] = field(default_factory=list)
    readings: list[str] = field(default_factory=list)   # decisions / question readings applied
    trace: list[dict] = field(default_factory=list)
    ctx: str | None = None

    @property
    def findings(self) -> list[str]:
        return sorted({c.finding for c in self.checks if c.status == "finding" and c.finding})

    def add(self, check, status, rule, clause, finding=None, detail=""):
        self.checks.append(Check(check, status, rule, clause, finding, str(detail)))

    def to_json(self) -> dict:
        s = lambda v: None if v is None else str(v)  # noqa: E731
        return {"contract": self.contract, "line_ref": self.line_ref, "code": self.code, "family": self.family, "unit_rate": s(self.unit_rate),
                "allowed_quantity": s(self.allowed_quantity), "amount": s(self.amount), "payable": self.payable,
                "amount_status": self.amount_status, "findings": self.findings, "reasons": self.reasons,
                "alternatives": {k: {kk: s(vv) if isinstance(vv, Decimal) else vv for kk, vv in v.items()} for k, v in self.alternatives.items()},
                "g4_dependencies": self.g4_dependencies, "readings": self.readings,
                "checks": [c.__dict__ for c in self.checks], "trace": self.trace, "ctx": self.ctx}
