"""Independent reconstruction and adversarial certificate rejection for Phase40."""
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
VERIFIER = ROOT/"verifier"/"verify_phase40.py"
CPP = ROOT/"verifier"/"phase40_minimality.cpp"


@pytest.fixture(scope="module")
def independent():
    spec = importlib.util.spec_from_file_location("phase40_independent_test_module",VERIFIER)
    assert spec is not None and spec.loader is not None
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def copied(tmp_path,independent):
    destination = tmp_path/"evidence"
    destination.mkdir()
    for name in independent.FILES:
        shutil.copy2(ROOT/"artifacts"/name,destination/name)
    return destination


def test_complete_independent_acceptance(independent):
    result = independent.verify(ROOT/"artifacts")
    assert result["valid"] is True
    assert result["generator_imported"] is False
    assert result["floating_point_used_for_acceptance"] is False
    assert result["bellman_rows"] == 1024
    assert result["total_tail_count"] == 33554431
    assert result["first_failure_length"] == 25
    assert result["failing_pairs_at_length25"] == 4
    assert result["cloud_rows"] == 12954
    assert result["cloud_transitions"] == 65536
    assert result["uses_X02_in_new_reduction"] is False
    assert result["H112_proved"] is False and result["proves_collatz"] is False
    assert result["claim_statuses"]["NG43"] == "REFUTED"
    assert result["claim_statuses"]["E56"] == "VERIFIED_FINITE"
    assert all(result["claim_statuses"][f"P{n}"] == "VERIFIED_THEOREM" for n in range(242,247))
    assert all(result["claim_statuses"][claim] == "OPEN" for claim in ("H72","H112","H133"))
    assert result["input_sha256"] == {
        name:hashlib.sha256((ROOT/"artifacts"/name).read_bytes()).hexdigest()
        for name in independent.FILES
    }


@pytest.mark.parametrize("name,path,replacement",[
    ("bellman",["rows",0,4],0),
    ("bellman",["rows",0,6],"1"),
    ("bellman",["row_count"],1023),
    ("bellman",["maximum_source"],253),
    ("bellman",["rows_sha256"],"0"*64),
    ("bellman",["scaling_sha256"],"0"*64),
    ("bellman",["half_factor_control","normalization_ratio"],"1/3"),
    ("bellman",["half_factor_control","competitor","safe"],False),
    ("bellman",["reduction","uses_X02"],True),
    ("bellman",["reduction","uses_capacity_2_to_49"],True),
    ("bellman",["reduction","H112_status"],"VERIFIED_THEOREM"),
    ("bellman",["reduction","effective_stabilization_index_claimed"],True),
    ("safety_minimality",["maximum_tail_length"],24),
    ("safety_minimality",["initial_run_bound"],12),
    ("safety_minimality",["threshold_table",0,0],1),
    ("safety_minimality",["total_tail_count"],33554430),
    ("safety_minimality",["first_failure_length"],24),
    ("safety_minimality",["levels",23,"failing_pair_count"],1),
    ("safety_minimality",["levels",24,"weight_gain_pair_count"],13488483),
    ("safety_minimality",["levels",24,"failing_pair_count"],3),
    ("safety_minimality",["levels",24,"first_failure","J"],"166692291"),
    ("safety_minimality",["levels",24,"first_failure","Rhi"],5),
    ("safety_minimality",["witness","target","source"],"1"),
    ("safety_minimality",["witness","competitor","safe"],True),
    ("safety_minimality",["witness","valley_index"],4),
    ("safety_minimality",["witness","rescued_suffix","source"],"1"),
    ("safety_minimality",["witness","suffix_source_lift"],0),
    ("cloud",["selected_rows",0,6],"0"),
    ("cloud",["selected_rows",0,8],0),
    ("cloud",["row_count"],12953),
    ("cloud",["transition_sha256"],"0"*64),
    ("cloud",["periodic_control","traces",0,4],2),
    ("cloud",["proof_scope","nonperiodicity_required_for_cloud_injectivity"],False),
    ("cloud",["proof_scope","finite_orbits_claimed_nonperiodic"],True),
    ("cloud",["proof_scope","new_independent_obstruction_claimed"],True),
    ("regressions",["mandatory_families"],["2^m-1"]),
    ("regressions",["NG22","source_residue"],"1"),
    ("regressions",["NG22","ordinary_positive_infinite_source_claimed"],True),
    ("regressions",["NG24","prefixed_endpoints",0,1],"0"),
    ("regressions",["NG41","P207_margin"],11),
    ("regressions",["NG41","P208_margin"],44),
    ("regressions",["NG42","missed_position"],3),
    ("regressions",["source167","trailing_zero_lifts"],12),
    ("regressions",["source167","first_coefficient_failure_length"],30),
    ("regressions",["source167","infinite_safe_stabilization_claimed"],True),
    ("regressions",["AB","fixed_point"],"817/217"),
    ("regressions",["cycle_exclusion_claimed"],True),
])
def test_rejects_arithmetic_scope_order_and_logical_tampering(tmp_path,independent,name,path,replacement):
    target = copied(tmp_path,independent)
    filename = target/f"phase40_{name}.json"
    value = json.loads(filename.read_text())
    selected = value
    for key in path[:-1]:
        selected = selected[key]
    assert selected[path[-1]] != replacement
    selected[path[-1]] = replacement
    filename.write_text(json.dumps(value))
    with pytest.raises(independent.VerificationError,match="artifact mismatch"):
        independent.verify(target)


def test_rejects_row_order_tamper(tmp_path,independent):
    target = copied(tmp_path,independent)
    path = target/"phase40_bellman.json"
    value = json.loads(path.read_text())
    value["rows"][0],value["rows"][1] = value["rows"][1],value["rows"][0]
    value["rows_sha256"] = independent.digest(value["rows"])
    path.write_text(json.dumps(value))
    with pytest.raises(independent.VerificationError,match="artifact mismatch"):
        independent.verify(target)


@pytest.mark.parametrize("name",["bellman","safety_minimality","cloud","regressions"])
def test_rejects_collatz_overclaim(tmp_path,independent,name):
    target = copied(tmp_path,independent)
    path = target/f"phase40_{name}.json"
    value = json.loads(path.read_text())
    value["proves_collatz"] = True
    path.write_text(json.dumps(value))
    with pytest.raises(independent.VerificationError,match="artifact mismatch"):
        independent.verify(target)


@pytest.mark.parametrize("malformed",["{","[]",'{"format":1,"format":2}','{"format":NaN}'])
def test_malformed_json_is_cleanly_rejected(tmp_path,independent,malformed):
    target = copied(tmp_path,independent)
    (target/"phase40_bellman.json").write_text(malformed)
    with pytest.raises(independent.VerificationError):
        independent.verify(target)


def test_rejects_bool_as_integer(tmp_path,independent):
    target = copied(tmp_path,independent)
    path = target/"phase40_safety_minimality.json"
    value = json.loads(path.read_text())
    value["levels"][0]["ell"] = True
    path.write_text(json.dumps(value))
    with pytest.raises(independent.VerificationError,match="artifact mismatch"):
        independent.verify(target)


def test_rejects_missing_input(tmp_path,independent):
    target = copied(tmp_path,independent)
    (target/"phase40_cloud.json").unlink()
    with pytest.raises(independent.VerificationError,match="cannot read"):
        independent.verify(target)


def test_source_independence_and_no_floating_acceptance():
    tree = ast.parse(VERIFIER.read_text())
    allowed = {"__future__","argparse","hashlib","itertools","json","subprocess","sys",
               "tempfile","collections","fractions","functools","pathlib"}
    for node in ast.walk(tree):
        if isinstance(node,ast.Import):
            assert all(alias.name.split(".")[0] in allowed for alias in node.names)
        if isinstance(node,ast.ImportFrom):
            assert node.module is not None and node.module.split(".")[0] in allowed
        if isinstance(node,ast.Constant):
            assert not isinstance(node.value,float)
        if isinstance(node,ast.Call) and isinstance(node.func,ast.Name):
            assert node.func.id not in {"eval","exec","__import__","float"}
    cpp_text = CPP.read_text()
    assert '#include "' not in cpp_text
    assert "double " not in cpp_text and "float " not in cpp_text
    assert "overflow_error" in cpp_text


def test_internal_cache_is_immutable(independent):
    expected = independent.reconstructed_payloads()
    assert isinstance(expected,tuple) and all(isinstance(value,str) for value in expected)
    modified = json.loads(expected[0])
    modified["row_count"] = 0
    assert json.loads(independent.reconstructed_payloads()[0])["row_count"] == 1024


@pytest.fixture(scope="module")
def cpp_binary(tmp_path_factory):
    binary = tmp_path_factory.mktemp("phase40-independent-cli")/"minimality"
    result = subprocess.run(["c++","-O3","-std=c++17",str(CPP),"-o",str(binary)],
                            capture_output=True,text=True,check=False)
    assert result.returncode == 0,result.stderr
    return binary


@pytest.mark.parametrize("bound",["0","26","4294967297","-1","wrong"])
def test_cpp_rejects_out_of_domain_scope(cpp_binary,bound):
    result = subprocess.run([str(cpp_binary),"--max-tail-length",bound],capture_output=True,text=True,check=False)
    assert result.returncode != 0
    assert "finite domain" in result.stderr or "invalid exact" in result.stderr


def test_cpp_small_scope_against_direct_literal_safety(cpp_binary,independent):
    result = subprocess.run([str(cpp_binary),"--max-tail-length","9"],capture_output=True,text=True,check=True)
    value = json.loads(result.stdout)
    assert value["threshold_table"] == independent.threshold_table(9)
    assert value["levels"] == independent.direct_small_levels(9)


def test_cli_malformed_input_returns_structured_failure(tmp_path,independent):
    target = copied(tmp_path,independent)
    (target/"phase40_bellman.json").write_text("{")
    result = subprocess.run([sys.executable,str(VERIFIER),"--artifact-dir",str(target)],
                            capture_output=True,text=True,check=False)
    assert result.returncode == 1
    value = json.loads(result.stdout)
    assert value["valid"] is False and value["proves_collatz"] is False
    assert "cannot read" in value["error"] and "Traceback" not in result.stderr
