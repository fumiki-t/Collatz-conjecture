from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

from scripts.build_claim_index import build_index
from scripts.check_markdown_links import audit_markdown
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
    assert result["latest_phase"] == 24
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
    assert result["active_focus"]["P77"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P78"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P79"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P80"] == "CONDITIONAL"
    assert result["active_focus"]["E22"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG23"] == "REFUTED"
    assert result["active_focus"]["P81"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P82"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P83"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P84"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P85"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E23"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG24"] == "REFUTED"
    assert result["active_focus"]["P86"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P87"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P88"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E24"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG25"] == "REFUTED"
    assert result["active_focus"]["NG26"] == "REFUTED"
    assert result["active_focus"]["P89"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P90"] == "CONDITIONAL"
    assert result["active_focus"]["H89"] == "OPEN"
    assert result["active_focus"]["P96"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E25"] == "VERIFIED_FINITE"
    assert result["active_focus"]["E26"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG27"] == "REFUTED"
    assert result["active_focus"]["P97"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P101"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P103"] == "CONDITIONAL"
    assert result["active_focus"]["E27"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG28"] == "REFUTED"
    assert result["active_focus"]["H97"] == "OPEN"
    assert result["active_focus"]["H98"] == "OPEN"
    assert result["active_focus"]["P104"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P105"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P106"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E28"] == "VERIFIED_FINITE"
    assert result["active_focus"]["E29"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG29"] == "REFUTED"
    assert result["active_focus"]["H104"] == "OPEN"
    assert result["active_focus"]["H105"] == "OPEN"
    assert result["active_focus"]["P107"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P108"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P109"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P110"] == "CONDITIONAL"
    assert result["active_focus"]["P111"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E30"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG30"] == "REFUTED"
    assert result["active_focus"]["P112"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P113"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P114"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P115"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P116"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E31"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG31"] == "REFUTED"
    assert result["active_focus"]["H112"] == "OPEN"
    assert result["active_focus"]["EXT08"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["EXT09"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["P117"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P118"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P119"] == "CONDITIONAL"
    assert result["active_focus"]["P120"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P121"] == "CONDITIONAL"
    assert result["active_focus"]["P122"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P123"] == "CONDITIONAL"
    assert result["active_focus"]["P124"] == "CONDITIONAL"
    assert result["active_focus"]["E32"] == "VERIFIED_FINITE"
    assert result["active_focus"]["EXT14"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["P125"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P126"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P127"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P128"] == "CONDITIONAL"
    assert result["active_focus"]["P129"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P130"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P131"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P132"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E33"] == "VERIFIED_FINITE"
    assert result["active_focus"]["EXT15"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["EXT16"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["P133"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P138"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P139"] == "CONDITIONAL"
    assert result["active_focus"]["P140"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E34"] == "VERIFIED_FINITE"
    assert result["active_focus"]["H133"] == "OPEN"
    assert result["active_focus"]["P141"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P142"] == "CONDITIONAL"
    assert result["active_focus"]["P144"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P145"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E35"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG32"] == "REFUTED"
    assert result["active_focus"]["H141"] == "OPEN"
    assert result["active_focus"]["P147"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P148"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P149"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P150"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E36"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG33"] == "REFUTED"
    assert result["active_focus"]["H147"] == "OPEN"
    assert result["latest_supplemental_verifier"]["valid"] is True
    assert result["latest_supplemental_verifier"]["generator_imported"] is False
    assert result["latest_supplemental_verifier"]["finite_counts"] == {
        "critical": 7057,
        "direct": 544073,
        "noncritical": 204,
    }
    assert result["registry"] == "research/registry.json"
    assert result["claim_index"] == "research/claims-index.json"
    required_accepted = {
        "phase12-acceptance",
        "phase13-renewal-code-pressure",
        "phase14-coalescent-rewrite",
        "phase15-surplus-dominance",
        "phase15b-ancestral-frontier",
    }
    assert required_accepted.issubset(result["accepted_experiments"])
    phase16 = json.loads(Path("research/experiments/phase16-critical-dichotomy.json").read_text(encoding="utf-8"))
    assert ("phase16-critical-dichotomy" in result["accepted_experiments"]) == (phase16["status"] == "ACCEPTED")
    phase17 = json.loads(Path("research/experiments/phase17-predecessor-pressure.json").read_text(encoding="utf-8"))
    assert ("phase17-predecessor-pressure" in result["accepted_experiments"]) == (phase17["status"] == "ACCEPTED")
    phase18 = json.loads(Path("research/experiments/phase18-affine-trichotomy.json").read_text(encoding="utf-8"))
    assert ("phase18-affine-trichotomy" in result["accepted_experiments"]) == (phase18["status"] == "ACCEPTED")
    phase19 = json.loads(Path("research/experiments/phase19-affine-lift.json").read_text(encoding="utf-8"))
    assert ("phase19-affine-lift" in result["accepted_experiments"]) == (phase19["status"] == "ACCEPTED")
    phase20 = json.loads(Path("research/experiments/phase20-parity-complexity.json").read_text(encoding="utf-8"))
    assert ("phase20-parity-complexity" in result["accepted_experiments"]) == (phase20["status"] == "ACCEPTED")
    phase21 = json.loads(Path("research/experiments/phase21-repetition-complexity.json").read_text(encoding="utf-8"))
    assert ("phase21-repetition-complexity" in result["accepted_experiments"]) == (phase21["status"] == "ACCEPTED")
    phase22 = json.loads(Path("research/experiments/phase22-cycle-resultant.json").read_text(encoding="utf-8"))
    assert ("phase22-cycle-resultant" in result["accepted_experiments"]) == (phase22["status"] == "ACCEPTED")
    phase23 = json.loads(Path("research/experiments/phase23-defect-area.json").read_text(encoding="utf-8"))
    assert ("phase23-defect-area" in result["accepted_experiments"]) == (phase23["status"] == "ACCEPTED")
    phase24 = json.loads(Path("research/experiments/phase24-sparse-arc-resultants.json").read_text(encoding="utf-8"))
    assert ("phase24-sparse-arc-resultants" in result["accepted_experiments"]) == (phase24["status"] == "ACCEPTED")
    assert isinstance(result["warnings"], list)
    assert result["proves_collatz"] is False


def test_registry_matches_context_and_claim_sources() -> None:
    root = Path(__file__).resolve().parents[1]
    registry = load_registry(root)
    assert registry["repository"]["status"] == "OPEN"
    assert registry["repository"]["proves_collatz"] is False
    assert registry["repository"]["claim_source"] == "docs/CLAIMS_LEDGER.md"
    assert "docs/RESEARCH_SYNTHESIS.md" in registry["canonical_documents"]
    obligations = registry["active_obligations"]
    assert {row["id"] for row in obligations} == {"H54", "H70", "H72", "H89", "H104", "H105", "H112", "H133", "H141", "H147", "C03", "C04", "C05"}
    for row in obligations:
        if "context" in row:
            assert (root / row["context"]).is_file()


def test_generated_claim_index_is_complete() -> None:
    root = Path(__file__).resolve().parents[1]
    generated = build_index(root)
    committed = json.loads((root / "research/claims-index.json").read_text(encoding="utf-8"))
    assert committed == generated
    assert committed["claim_count"] == 196
    rows = {row["id"]: row for row in committed["claims"]}
    assert rows["H72"]["status"] == "OPEN"
    assert rows["H112"]["status"] == "OPEN"
    assert rows["P115"]["status"] == "VERIFIED_THEOREM"
    assert rows["NG31"]["status"] == "REFUTED"
    assert rows["P117"]["status"] == "VERIFIED_THEOREM"
    assert rows["P124"]["status"] == "CONDITIONAL"
    assert rows["E32"]["status"] == "VERIFIED_FINITE"
    assert rows["P127"]["status"] == "VERIFIED_THEOREM"
    assert rows["P132"]["status"] == "VERIFIED_THEOREM"
    assert rows["E33"]["status"] == "VERIFIED_FINITE"
    assert rows["P137"]["status"] == "VERIFIED_THEOREM"
    assert rows["P139"]["status"] == "CONDITIONAL"
    assert rows["E34"]["status"] == "VERIFIED_FINITE"
    assert rows["H133"]["status"] == "OPEN"
    assert rows["P141"]["status"] == "VERIFIED_THEOREM"
    assert rows["P142"]["status"] == "CONDITIONAL"
    assert rows["P144"]["status"] == "VERIFIED_THEOREM"
    assert rows["P145"]["status"] == "VERIFIED_THEOREM"
    assert rows["E35"]["status"] == "VERIFIED_FINITE"
    assert rows["NG32"]["status"] == "REFUTED"
    assert rows["H141"]["status"] == "OPEN"
    assert rows["P147"]["status"] == "VERIFIED_THEOREM"
    assert rows["P148"]["status"] == "VERIFIED_THEOREM"
    assert rows["P149"]["status"] == "VERIFIED_THEOREM"
    assert rows["P150"]["status"] == "VERIFIED_THEOREM"
    assert rows["E36"]["status"] == "VERIFIED_FINITE"
    assert rows["NG33"]["status"] == "REFUTED"
    assert rows["H147"]["status"] == "OPEN"
    assert set(rows["H72"]["dependency_ids"]) == {
        "P72",
        "P73",
        "P75",
        "P76",
        "P77",
        "P78",
        "P79",
        "P80",
        "P81",
        "P82",
        "P83",
        "P84",
        "P85",
        "P86",
        "P87",
        "P88",
        "P107",
        "P108",
        "P109",
        "P110",
        "P111",
        "P112",
        "P113",
        "P114",
        "P115",
        "P116",
        "P117",
        "P119",
        "P120",
        "P121",
        "P122",
        "P123",
        "P124",
        "P125",
        "P126",
        "P127",
        "P128",
        "P129",
        "P130",
        "P131",
        "EXT08",
        "E23",
        "E24",
        "E30",
        "E31",
        "E32",
        "E33",
        "NG21",
        "NG22",
        "NG23",
        "NG24",
        "NG25",
        "NG26",
        "NG30",
        "NG31",
    }


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

    bad_hash = dict(manifest)
    bad_hash["recorded_result"] = dict(manifest["recorded_result"])
    bad_hash["recorded_result"]["manifest_sha256"] = "0" * 64
    errors = validate_experiment_manifest(root, bad_hash, claim_map, required)
    assert any("manifest hash mismatch" in error for error in errors)


def test_markdown_audit_rejects_missing_and_private_targets(tmp_path: Path) -> None:
    good = tmp_path / "good.md"
    target = tmp_path / "target.md"
    target.write_text("# Target\n", encoding="utf-8")
    good.write_text("[target](target.md)\n", encoding="utf-8")
    assert audit_markdown(tmp_path, [good]) == []

    bad = tmp_path / "bad.md"
    bad.write_text("[missing](nope.md)\n`/Users/example/private`\n", encoding="utf-8")
    errors = audit_markdown(tmp_path, [bad])
    assert any("missing local link target" in error for error in errors)
    assert any("private or local-only path" in error for error in errors)
