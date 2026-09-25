"""G0/G1 gate: the real specification passes, and each class of defect makes it fail (negative controls)."""
import shutil

import pytest
import yaml

import spec_lib as sl
import verify_spec


def test_real_spec_passes(capsys):
    assert verify_spec.main() == 0
    out = capsys.readouterr().out
    assert out.count("PASS ") == 9 and "FAIL" not in out


@pytest.fixture
def sandbox(tmp_path, monkeypatch):
    spec = tmp_path / "spec"
    verif = tmp_path / "verification"
    shutil.copytree(sl.SPEC, spec)
    verif.mkdir()
    shutil.copy(sl.VERIF / "second_pass_log.yaml", verif / "second_pass_log.yaml")
    monkeypatch.setattr(sl, "SPEC", spec)
    monkeypatch.setattr(sl, "VERIF", verif)
    return spec


def edit(path, fn):
    data = yaml.safe_load(path.read_text())
    fn(data)
    path.write_text(yaml.safe_dump(data, sort_keys=False, allow_unicode=True))


def run(capsys):
    rc = verify_spec.main()
    return rc, capsys.readouterr().out


def test_changed_rate_invalidates_verification_and_pricing_gate(sandbox, capsys):
    def f(d):
        d["tables"]["CW.T01_SCH1"]["rows"][0][4] = "3.86"   # A.11.010 3.85 -> 3.86
    edit(sandbox / "terms_cw.yaml", f)
    rc, out = run(capsys)
    assert rc == 1
    assert "CW.T01_SCH1: content changed since verification" in out
    assert "CW.T01_SCH1 feeds pricing but is not verified" in out


def test_changed_instrument_rate_is_caught(sandbox, capsys):
    def f(d):
        d["instruments"][-1]["rate_rows"][0]["to"] = "406.00"   # DDS A3 DD-120 416.00 -> 406.00
    edit(sandbox / "instruments.yaml", f)
    rc, out = run(capsys)
    assert rc == 1 and "DDS.A3: content changed since verification" in out


def test_section_without_owner_fails(sandbox, capsys):
    def f(d):
        d["sections"] = [x for x in d["sections"] if x["pages"] != [27]]
    edit(sandbox / "sections_cw.yaml", f)
    rc, out = run(capsys)
    assert rc == 1 and "pages without any section entry [27]" in out


def test_guideline_check_without_owner_fails(sandbox, capsys):
    def f(d):
        d["checks"][9]["DDS"] = []
    edit(sandbox / "guideline_checks.yaml", f)
    rc, out = run(capsys)
    assert rc == 1 and "check 10 has no DDS owner" in out


def test_missing_audit_correction_fails(sandbox, capsys):
    def f(d):
        d["corrections"] = [c for c in d["corrections"] if c["id"] != "P2-B-P3"]
    edit(sandbox / "corrections.yaml", f)
    rc, out = run(capsys)
    assert rc == 1 and "missing correction P2-B-P3" in out


def test_open_question_needs_two_alternatives_and_scope(sandbox, capsys):
    def f(d):
        d["questions"][0]["alternatives"] = d["questions"][0]["alternatives"][:1]
        d["questions"][1]["scope_ref"] = []
    edit(sandbox / "open_questions.yaml", f)
    rc, out = run(capsys)
    assert rc == 1 and "Q1: fewer than two bounded alternatives" in out and "Q2: no affected scope" in out


def test_rule_without_page_reference_fails(sandbox, capsys):
    def f(d):
        d["rules"][0]["sources"] = ["somewhere"]
    edit(sandbox / "rules.yaml", f)
    rc, out = run(capsys)
    assert rc == 1 and "CW-R01: source without page/clause reference" in out


def test_unverified_log_entry_blocks_pricing(sandbox, capsys):
    path = sl.VERIF / "second_pass_log.yaml"
    d = yaml.safe_load(path.read_text())
    d["entries"]["DDS.T12_STANDBY"]["status"] = "pending"
    path.write_text(yaml.safe_dump(d, sort_keys=False))
    rc, out = run(capsys)
    assert rc == 1 and "DDS.T12_STANDBY feeds pricing but is not verified" in out


def test_regenerating_log_never_recertifies_a_changed_table(sandbox, monkeypatch, capsys):
    import sys
    import record_verification
    for sub in ("blind", "ocr"):
        shutil.copytree(sl.ROOT / "verification" / sub, sl.VERIF / sub, ignore=shutil.ignore_patterns("crops_*"))
    shutil.copy(sl.ROOT / "verification" / "reading_comparison.json", sl.VERIF / "reading_comparison.json")

    def f(d):
        d["tables"]["DDS.T05_RSI"]["rows"][5][1] = "103.70"
    edit(sandbox / "terms_dds.yaml", f)
    monkeypatch.setattr(sys, "argv", ["record_verification.py"])
    assert record_verification.main() == 0
    log = yaml.safe_load((sl.VERIF / "second_pass_log.yaml").read_text())["entries"]
    assert log["DDS.T05_RSI"]["status"] == "pending"
    assert log["DDS.T01_SCH1"]["status"] == "verified"
    capsys.readouterr()
    rc, out = run(capsys)
    assert rc == 1 and "DDS.T05_RSI feeds pricing but is not verified" in out
