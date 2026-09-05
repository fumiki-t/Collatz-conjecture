"""Tamper rejection for the bounded Phase 39 independent reconstruction."""
from __future__ import annotations

import ast
import hashlib
import importlib.util
import json
import shutil
import subprocess
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
VERIFIER = ROOT / "verifier" / "verify_phase39.py"


@pytest.fixture(scope="module")
def independent():
    spec = importlib.util.spec_from_file_location("phase39_independent_test_module", VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copy_evidence(tmp_path: Path, independent) -> Path:
    target = tmp_path / "evidence"
    target.mkdir()
    for name in independent.FILES:
        shutil.copy2(ROOT / "artifacts" / name, target / name)
    return target


def change(value, path, replacement):
    for key in path[:-1]:
        value = value[key]
    value[path[-1]] = replacement


def test_independent_acceptance_and_input_hashes(independent) -> None:
    result = independent.verify(ROOT / "artifacts")
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["floating_point_used_for_acceptance"] is False
    assert result["proves_collatz"] is False
    assert result["carry_rows"] == 21844
    assert result["carry_relations"] == 172
    assert result["dag_vertices"] == 1938
    assert result["dag_rewrites"] == 10520
    assert result["capacity_rows"] == 500
    assert result["positive_endpoint_lifts"] == 24534
    assert result["rational_cycles"] == 1320
    assert result["direct_event_count"] == 32768
    assert result["claim_statuses"]["P240"] == "CONDITIONAL"
    assert {result["claim_statuses"][claim] for claim in ("H72", "H112", "H133")} == {"OPEN"}
    assert result["input_sha256"] == {
        name: hashlib.sha256((ROOT / "artifacts" / name).read_bytes()).hexdigest()
        for name in independent.FILES
    }


@pytest.mark.parametrize("name,path,replacement", [
    ("carry_audit", ["relations",0,4], "999"),
    ("carry_audit", ["maximum_word_length"], 7),
    ("carry_audit", ["row_count"], 21843),
    ("carry_audit", ["selected_rows",0,3], "0"),
    ("carry_audit", ["rows_sha256"], "0"*64),
    ("carry_audit", ["universal_rewrite_rows",0,1], "65"),
    ("carry_audit", ["fixed_relation_cutoffs",0,2], 0),
    ("jump_dag", ["vertices",0,1], "3"),
    ("jump_dag", ["vertices",0,2,0,1], 1),
    ("jump_dag", ["first_safe_gain","1",6], "0"),
    ("jump_dag", ["rewrite_count"], 10519),
    ("jump_dag", ["unsafe_candidate_count"], 1),
    ("jump_dag", ["maximum_suffix_length"], 12),
    ("jump_dag", ["tail_length_counts_initial_zero"], False),
    ("capacity_cycle", ["binomial_rows",499,1], "1"),
    ("capacity_cycle", ["entropy_certificate","theta_numerator"], 15),
    ("capacity_cycle", ["X1_bound"], True),
    ("capacity_cycle", ["positive_endpoint_lifts","selected_rows",0,2], "0"),
    ("capacity_cycle", ["positive_endpoint_lifts","selected_rows",0,3,1,1], "0"),
    ("capacity_cycle", ["rational_cycle_count"], 0),
    ("capacity_cycle", ["direct_event_rows_sha256"], "0"*64),
    ("capacity_cycle", ["conditional_reduction","uses_external_X02"], False),
    ("capacity_cycle", ["conditional_reduction","H112_status"], "VERIFIED_THEOREM"),
    ("capacity_cycle", ["conditional_reduction","cycle_exclusion_claimed"], True),
    ("capacity_cycle", ["conditional_reduction","reciprocal_includes_initial_odd_source"], False),
    ("regressions", ["mandatory_families"], ["2^m-1"]),
    ("regressions", ["NG22_formal_policy","last_row",3], "1"),
    ("regressions", ["NG22_formal_policy","ordinary_positive_source_claimed"], True),
    ("regressions", ["NG24_endpoint_residues",0,1], "0"),
    ("regressions", ["NG41_scalar_survivor","P207_margin"], 11),
    ("regressions", ["NG41_scalar_survivor","P208_margin"], 44),
    ("regressions", ["NG42_orientation","missed_position"], 3),
    ("regressions", ["negative_cycles",0,2], [-1,1]),
    ("regressions", ["AB_witness","fixed_point"], "817/217"),
])
def test_rejects_arithmetic_scope_and_status_tampering(tmp_path, independent, name, path, replacement):
    target = copy_evidence(tmp_path, independent)
    filename = target / f"phase39_{name}.json"
    value = json.loads(filename.read_text(encoding="utf-8"))
    change(value, path, replacement)
    filename.write_text(json.dumps(value), encoding="utf-8")
    with pytest.raises(independent.VerificationError, match="artifact mismatch"):
        independent.verify(target)


def test_rejects_collision_corpus_order_tamper(tmp_path, independent):
    target = copy_evidence(tmp_path, independent)
    path = target / "phase39_jump_dag.json"
    value = json.loads(path.read_text())
    collision = next(vertex for vertex in value["vertices"] if len(vertex[2]) > 1)
    collision[2].reverse()
    path.write_text(json.dumps(value))
    with pytest.raises(independent.VerificationError, match="artifact mismatch"):
        independent.verify(target)


@pytest.mark.parametrize("filename", [
    "phase39_carry_audit.json", "phase39_jump_dag.json",
    "phase39_capacity_cycle.json", "phase39_regressions.json",
])
def test_rejects_collatz_overclaim(tmp_path, independent, filename):
    target = copy_evidence(tmp_path, independent)
    path = target / filename
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    with pytest.raises(independent.VerificationError, match="artifact mismatch"):
        independent.verify(target)


@pytest.mark.parametrize("malformed", ["{", "[]", '{"format":1,"format":2}', '{"format":NaN}'])
def test_malformed_json_has_clean_rejection(tmp_path, independent, malformed):
    target = copy_evidence(tmp_path, independent)
    (target / "phase39_carry_audit.json").write_text(malformed)
    with pytest.raises(independent.VerificationError):
        independent.verify(target)


def test_rejects_missing_file(tmp_path, independent):
    target = copy_evidence(tmp_path, independent)
    (target / "phase39_jump_dag.json").unlink()
    with pytest.raises(independent.VerificationError, match="cannot read"):
        independent.verify(target)


def test_rejects_obstruction_boundary_tamper(tmp_path, independent):
    target = copy_evidence(tmp_path, independent)
    path = target / "phase39_obstruction_report.md"
    path.write_text(path.read_text().replace("H112 and H72 remain OPEN.", "H112 and H72 are proved."))
    with pytest.raises(independent.VerificationError, match="obstruction report"):
        independent.verify(target)


def test_verifier_has_no_generator_or_float_acceptance_dependency():
    tree = ast.parse(VERIFIER.read_text(encoding="utf-8"))
    allowed = {"__future__", "argparse", "hashlib", "itertools", "json", "sys",
               "collections", "fractions", "functools", "pathlib"}
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            assert all(alias.name.split(".")[0] in allowed for alias in node.names)
        if isinstance(node, ast.ImportFrom):
            assert node.module is not None and node.module.split(".")[0] in allowed
        if isinstance(node, ast.Constant):
            assert not isinstance(node.value, float)
        if isinstance(node, ast.Call) and isinstance(node.func, ast.Name):
            assert node.func.id not in {"eval", "exec", "__import__", "float"}


def test_cached_reconstruction_is_immutable_and_input_independent(independent):
    first = independent.reconstructed_payloads()
    assert isinstance(first, tuple) and all(isinstance(value, str) for value in first)
    decoded = json.loads(first[0])
    decoded["row_count"] = -1
    assert json.loads(independent.reconstructed_payloads()[0])["row_count"] == 21844


def test_cli_malformed_json_returns_nonzero_json_result(tmp_path, independent):
    target = copy_evidence(tmp_path, independent)
    (target / "phase39_jump_dag.json").write_text("{")
    completed = subprocess.run([sys.executable, str(VERIFIER), "--artifact-dir", str(target)],
                               capture_output=True, text=True, check=False)
    assert completed.returncode == 1
    result = json.loads(completed.stdout)
    assert result["valid"] is False and result["proves_collatz"] is False
    assert "cannot read" in result["error"]
    assert "Traceback" not in completed.stderr
