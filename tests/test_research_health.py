from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.build_claim_index import build_index
from scripts.research_health import load_registry, validate_experiment_manifest


def test_repository_research_health() -> None:
    completed = subprocess.run(
        [sys.executable, "scripts/research_health.py"],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr
    result = json.loads(completed.stdout)
    assert result["valid"] is True
    assert result["latest_phase"] == 12
    assert result["active_focus"]["C04"] == "OPEN"
    assert result["active_focus"]["C05"] == "OPEN"
    assert result["active_focus"]["P69"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P70"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["H70"] == "OPEN"
    assert result["active_focus"]["NG20"] == "REFUTED"
    assert result["active_focus"]["P72"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P73"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E20"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG21"] == "REFUTED"
    assert result["active_focus"]["H72"] == "OPEN"
    assert result["active_focus"]["EXT07"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["P74"] == "CONDITIONAL"
    assert result["active_focus"]["P75"] == "CONDITIONAL"
    assert result["active_focus"]["P76"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E21"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG22"] == "REFUTED"
    assert result["latest_supplemental_verifier"]["valid"] is True
    assert result["registry"] == "research/registry.json"
    assert result["claim_index"] == "research/claims-index.json"
    assert result["accepted_experiments"] == ["phase12-acceptance"]
    assert isinstance(result["warnings"], list)
    assert result["proves_collatz"] is False


def test_registry_matches_context_and_claim_sources() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = load_registry(root)
    assert registry["repository"]["status"] == "OPEN"
    assert registry["repository"]["proves_collatz"] is False
    assert registry["repository"]["claim_source"] == "docs/CLAIMS_LEDGER.md"
    obligations = registry["active_obligations"]
    assert {row["id"] for row in obligations} == {"H54", "H70", "H72", "C03", "C04", "C05"}
    for row in obligations:
        if "context" in row:
            assert (root / row["context"]).is_file()


def test_generated_claim_index_is_complete() -> None:
    root = Path(__file__).resolve().parents[1]
    generated = build_index(root)
    committed = json.loads((root / "research/claims-index.json").read_text(encoding="utf-8"))
    assert committed == generated
    assert committed["claim_count"] == 78
    rows = {row["id"]: row for row in committed["claims"]}
    assert rows["H72"]["status"] == "OPEN"
    assert set(rows["H72"]["dependency_ids"]) == {"P72", "P73", "P75", "NG21", "NG22"}


def test_experiment_contract_rejects_overclaim_and_missing_family() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = load_registry(root)
    manifest_path = root / "research/experiments/phase12-acceptance.json"
    manifest = json.loads(manifest_path.read_text(encoding="utf-8"))
    claim_map = {claim_id: "KNOWN" for claim_id in manifest["claim_ids"]}
    required = set(registry["mandatory_adversarial_families"])

    assert validate_experiment_manifest(root, manifest, claim_map, required) == []

    tampered = dict(manifest)
    tampered["proves_collatz"] = True
    tampered["adversarial_families"] = manifest["adversarial_families"][:-1]
    tampered["recorded_result"] = dict(manifest["recorded_result"])
    tampered["recorded_result"]["commit"] = "0" * 40
    errors = validate_experiment_manifest(root, tampered, claim_map, required)
    assert any("proves_collatz" in error for error in errors)
    assert any("mandatory adversarial family" in error for error in errors)
    assert any("commit is not available" in error for error in errors)
