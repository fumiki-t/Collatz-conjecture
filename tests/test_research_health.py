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
    assert result["latest_phase"] == 44
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
    assert result["active_focus"]["EXT08"] == "OPEN"
    assert result["active_focus"]["P268"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["NG47"] == "REFUTED"
    assert result["active_focus"]["E61"] == "VERIFIED_FINITE"
    assert result["active_focus"]["P269"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P270"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E62"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG48"] == "REFUTED"
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
    assert result["active_focus"]["P151"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P152"] == "CONDITIONAL"
    assert result["active_focus"]["P153"] == "CONDITIONAL"
    assert result["active_focus"]["P154"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P155"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E37"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG34"] == "REFUTED"
    assert result["active_focus"]["P156"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P157"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P158"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P159"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P160"] == "CONDITIONAL"
    assert result["active_focus"]["P161"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E38"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG35"] == "REFUTED"
    assert result["active_focus"]["EXT17"] == "EXTERNAL_THEOREM"
    assert result["active_focus"]["P162"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P163"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P164"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P165"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E39"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG36"] == "REFUTED"
    assert result["active_focus"]["P166"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P167"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P168"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P169"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P170"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P171"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E40"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG37"] == "REFUTED"
    assert result["active_focus"]["NG38"] == "REFUTED"
    assert result["active_focus"]["H172"] == "OPEN"
    assert result["active_focus"]["P173"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P174"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P175"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P176"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P177"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P178"] == "CONDITIONAL"
    assert result["active_focus"]["E41"] == "VERIFIED_FINITE"
    assert result["active_focus"]["P179"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P180"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P181"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P182"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P183"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P184"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E42"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG39"] == "REFUTED"
    assert result["active_focus"]["P185"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P186"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P187"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P188"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P189"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P190"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E43"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG40"] == "REFUTED"
    assert result["active_focus"]["P191"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P192"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P193"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P194"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E44"] == "VERIFIED_FINITE"
    assert result["active_focus"]["P195"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P196"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P197"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P198"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P199"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["H200"] == "RETRACTED"
    assert result["active_focus"]["E45"] == "VERIFIED_FINITE"
    assert result["active_focus"]["P200"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E46"] == "VERIFIED_FINITE"
    assert result["active_focus"]["E47"] == "VERIFIED_FINITE"
    assert result["active_focus"]["P201"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P202"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P203"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P204"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P205"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E48"] == "VERIFIED_FINITE"
    assert result["active_focus"]["P206"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P207"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P208"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P209"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P210"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E49"] == "VERIFIED_FINITE"
    assert result["active_focus"]["E50"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG41"] == "REFUTED"
    assert result["active_focus"]["P211"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P212"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P213"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P214"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P215"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P216"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P217"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P218"] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E51"] == "VERIFIED_FINITE"
    assert result["active_focus"]["E52"] == "VERIFIED_FINITE"
    assert result["active_focus"]["NG42"] == "REFUTED"
    for claim in ("P219", "P220", "P221", "P222", "P223", "P224", "P225", "P226"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E53"] == "VERIFIED_FINITE"
    for claim in ("P227", "P228", "P229", "P231", "P232", "P233", "P234"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P230"] == "CONDITIONAL"
    assert result["active_focus"]["E54"] == "VERIFIED_FINITE"
    assert result["active_focus"]["H147"] == "VERIFIED_THEOREM"
    assert result["latest_supplemental_verifier"]["valid"] is True
    assert result["latest_supplemental_verifier"]["generator_imported"] is False
    assert result["latest_supplemental_verifier"]["model_odd_steps"] == 1000000
    assert result["latest_supplemental_verifier"]["shortcut_bits"] == 1584925
    assert result["latest_supplemental_verifier"]["low_edit_occurrences"] == 590784
    assert result["latest_supplemental_verifier"]["distinct_low_edit_words"] == 966
    assert result["latest_supplemental_verifier"]["edit_capacity_r1_excess"] == 269665
    assert result["latest_supplemental_verifier"]["actual_prefix_queries"] == 5090
    historical_phase43 = json.loads(Path("artifacts/phase43_verifier.json").read_text(encoding="utf-8"))
    assert historical_phase43["query_count"] == 2668
    assert historical_phase43["certified_no_improvement"] == 185
    assert historical_phase43["improvements"] == 2483
    assert historical_phase43["reference_vertices"] == 1189
    assert historical_phase43["certificate_703_vertices"] == 1188
    assert historical_phase43["minimal_monotonicity_query"] == [7, 4]
    for claim in ("P262", "P263", "P264", "P265", "P266", "P267"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E60"] == "VERIFIED_FINITE"
    for claim in ("P257", "P258", "P259", "P260", "P261"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["NG46"] == "REFUTED"
    assert result["active_focus"]["E59"] == "VERIFIED_FINITE"
    historical_phase42 = json.loads(Path("artifacts/phase42_verifier.json").read_text(encoding="utf-8"))
    assert historical_phase42["positive_odd_sources"] == 2048
    assert historical_phase42["finite_capacity_factor_occurrences"] == 0
    assert historical_phase42["negative_carry_minimum_q"] == 22
    assert historical_phase42["q21_rejections"] == 48
    assert historical_phase42["repeat_certificates"] == 8
    assert historical_phase42["maximum_repeat_prefix"] == 391004
    historical_phase41 = json.loads(Path("artifacts/phase41_verifier.json").read_text(encoding="utf-8"))
    assert historical_phase41["word_count"] == 32767
    assert historical_phase41["mixed_rows"] == 4192
    assert historical_phase41["even_rows"] == 658
    assert historical_phase41["ancestor_targets"] == 125
    historical_phase40 = json.loads(Path("artifacts/phase40_verifier.json").read_text(encoding="utf-8"))
    assert historical_phase40["bellman_rows"] == 1024
    assert historical_phase40["total_tail_count"] == 33554431
    assert historical_phase40["cloud_rows"] == 12954
    assert result["latest_supplemental_verifier"]["proves_collatz"] is False
    for claim in ("P235", "P236", "P237", "P238", "P239", "P241"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["P240"] == "CONDITIONAL"
    assert result["active_focus"]["E55"] == "VERIFIED_FINITE"
    historical_phase39 = json.loads(Path("artifacts/phase39_verifier.json").read_text(encoding="utf-8"))
    assert historical_phase39["capacity_rows"] == 500
    assert historical_phase39["carry_rows"] == 21844
    assert historical_phase39["dag_rewrites"] == 10520
    assert historical_phase39["positive_endpoint_lifts"] == 24534
    assert historical_phase39["direct_event_count"] == 32768
    for claim in ("P242", "P243", "P244", "P245", "P246"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["NG43"] == "REFUTED"
    assert result["active_focus"]["E56"] == "VERIFIED_FINITE"
    for claim in ("P247", "P248", "P249", "P250", "P251"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["NG44"] == result["active_focus"]["NG45"] == "REFUTED"
    assert result["active_focus"]["E57"] == "VERIFIED_FINITE"
    for claim in ("P252", "P253", "P254", "P255", "P256"):
        assert result["active_focus"][claim] == "VERIFIED_THEOREM"
    assert result["active_focus"]["E58"] == "VERIFIED_FINITE"
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
    phase25 = json.loads(Path("research/experiments/phase25-hamming-resonance.json").read_text(encoding="utf-8"))
    assert ("phase25-hamming-resonance" in result["accepted_experiments"]) == (phase25["status"] == "ACCEPTED")
    phase26 = json.loads(Path("research/experiments/phase26-cycle-area-barrier.json").read_text(encoding="utf-8"))
    assert ("phase26-cycle-area-barrier" in result["accepted_experiments"]) == (phase26["status"] == "ACCEPTED")
    phase27 = json.loads(Path("research/experiments/phase27-asymptotic-cycle-area.json").read_text(encoding="utf-8"))
    assert ("phase27-asymptotic-cycle-area" in result["accepted_experiments"]) == (phase27["status"] == "ACCEPTED")
    phase28 = json.loads(Path("research/experiments/phase28-transport-dispersion.json").read_text(encoding="utf-8"))
    assert ("phase28-transport-dispersion" in result["accepted_experiments"]) == (phase28["status"] == "ACCEPTED")
    phase29 = json.loads(Path("research/experiments/phase29-arc-nonvanishing.json").read_text(encoding="utf-8"))
    assert ("phase29-arc-nonvanishing" in result["accepted_experiments"]) == (phase29["status"] == "ACCEPTED")
    phase30 = json.loads(Path("research/experiments/phase30-direct-transport.json").read_text(encoding="utf-8"))
    assert ("phase30-direct-transport" in result["accepted_experiments"]) == (phase30["status"] == "ACCEPTED")
    phase31 = json.loads(Path("research/experiments/phase31-double-hit-transport.json").read_text(encoding="utf-8"))
    assert ("phase31-double-hit-transport" in result["accepted_experiments"]) == (phase31["status"] == "ACCEPTED")
    phase31_v2 = json.loads(Path("research/experiments/phase31-short-leaf-double-hit.json").read_text(encoding="utf-8"))
    assert ("phase31-short-leaf-double-hit" in result["accepted_experiments"]) == (phase31_v2["status"] == "ACCEPTED")
    phase32 = json.loads(Path("research/experiments/phase32-triple-hit-cofactor.json").read_text(encoding="utf-8"))
    assert ("phase32-triple-hit-cofactor" in result["accepted_experiments"]) == (phase32["status"] == "ACCEPTED")
    phase35 = json.loads(Path("research/experiments/phase35-full-decoder-joint-scalar.json").read_text(encoding="utf-8"))
    assert ("phase35-full-decoder-joint-scalar" in result["accepted_experiments"]) == (phase35["status"] == "ACCEPTED")
    phase36 = json.loads(Path("research/experiments/phase36-root-event-polynomial.json").read_text(encoding="utf-8"))
    assert ("phase36-root-event-polynomial" in result["accepted_experiments"]) == (phase36["status"] == "ACCEPTED")
    phase37 = json.loads(Path("research/experiments/phase37-internal-uniform-sparsity.json").read_text(encoding="utf-8"))
    assert ("phase37-internal-uniform-sparsity" in result["accepted_experiments"]) == (phase37["status"] == "ACCEPTED")
    phase38 = json.loads(Path("research/experiments/phase38-finite-capacity-renewal-transfer.json").read_text(encoding="utf-8"))
    assert ("phase38-finite-capacity-renewal-transfer" in result["accepted_experiments"]) == (phase38["status"] == "ACCEPTED")
    phase39 = json.loads(Path("research/experiments/phase39-macroscopic-carry-jump-geodesic.json").read_text(encoding="utf-8"))
    assert ("phase39-macroscopic-carry-jump-geodesic" in result["accepted_experiments"]) == (phase39["status"] == "ACCEPTED")
    phase40 = json.loads(Path("research/experiments/phase40-normalized-height-bellman.json").read_text(encoding="utf-8"))
    assert ("phase40-normalized-height-bellman" in result["accepted_experiments"]) == (phase40["status"] == "ACCEPTED")
    phase43 = json.loads(Path("research/experiments/phase43-normalization-barrier.json").read_text(encoding="utf-8"))
    assert ("phase43-normalization-barrier" in result["accepted_experiments"]) == (phase43["status"] == "ACCEPTED")
    phase44 = json.loads(Path("research/experiments/phase44-edit-capacity.json").read_text(encoding="utf-8"))
    assert ("phase44-edit-capacity" in result["accepted_experiments"]) == (phase44["status"] == "ACCEPTED")
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
    assert {row["id"] for row in obligations} == {"H54", "H70", "H72", "H89", "H104", "H105", "H112", "H133", "H141", "H172", "C03", "C04", "C05"}
    for row in obligations:
        if "context" in row:
            assert (root / row["context"]).is_file()


def test_generated_claim_index_is_complete() -> None:
    root = Path(__file__).resolve().parents[1]
    generated = build_index(root)
    committed = json.loads((root / "research/claims-index.json").read_text(encoding="utf-8"))
    assert committed == generated
    assert committed["claim_count"] == 359
    rows = {row["id"]: row for row in committed["claims"]}
    assert rows["H72"]["status"] == "OPEN"
    assert rows["H112"]["status"] == "OPEN"
    assert rows["P115"]["status"] == "VERIFIED_THEOREM"
    assert rows["NG31"]["status"] == "REFUTED"
    for claim in ("P242", "P243", "P244", "P245", "P246"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["P240"]["status"] == "CONDITIONAL"
    assert rows["NG43"]["status"] == "REFUTED"
    assert rows["E56"]["status"] == "VERIFIED_FINITE"
    for claim in ("P252", "P253", "P254", "P255", "P256"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["E58"]["status"] == "VERIFIED_FINITE"
    for claim in ("P257", "P258", "P259", "P260", "P261"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["E59"]["status"] == "VERIFIED_FINITE"
    assert rows["NG46"]["status"] == "REFUTED"
    for claim in ("P262", "P263", "P264", "P265", "P266", "P267"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["E60"]["status"] == "VERIFIED_FINITE"
    assert rows["P117"]["status"] == "VERIFIED_THEOREM"
    assert rows["P124"]["status"] == "CONDITIONAL"
    assert rows["E32"]["status"] == "VERIFIED_FINITE"
    assert rows["P127"]["status"] == "VERIFIED_THEOREM"
    assert rows["P132"]["status"] == "VERIFIED_THEOREM"
    assert rows["E33"]["status"] == "VERIFIED_FINITE"
    assert rows["P195"]["status"] == "VERIFIED_THEOREM"
    assert rows["P199"]["status"] == "VERIFIED_THEOREM"
    assert rows["H200"]["status"] == "RETRACTED"
    assert rows["E45"]["status"] == "VERIFIED_FINITE"
    assert rows["P200"]["status"] == "VERIFIED_THEOREM"
    assert rows["E46"]["status"] == "VERIFIED_FINITE"
    assert rows["E47"]["status"] == "VERIFIED_FINITE"
    assert rows["P201"]["status"] == "VERIFIED_THEOREM"
    assert rows["P202"]["status"] == "VERIFIED_THEOREM"
    assert rows["P203"]["status"] == "VERIFIED_THEOREM"
    assert rows["P204"]["status"] == "VERIFIED_THEOREM"
    assert rows["P205"]["status"] == "VERIFIED_THEOREM"
    assert rows["E48"]["status"] == "VERIFIED_FINITE"
    assert rows["P206"]["status"] == "VERIFIED_THEOREM"
    assert rows["P207"]["status"] == "VERIFIED_THEOREM"
    assert rows["P208"]["status"] == "VERIFIED_THEOREM"
    assert rows["P209"]["status"] == "VERIFIED_THEOREM"
    assert rows["P210"]["status"] == "VERIFIED_THEOREM"
    assert rows["E49"]["status"] == "VERIFIED_FINITE"
    assert rows["E50"]["status"] == "VERIFIED_FINITE"
    assert rows["NG41"]["status"] == "REFUTED"
    for claim in ("P211", "P212", "P213", "P214", "P215", "P216", "P217", "P218"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["E51"]["status"] == "VERIFIED_FINITE"
    assert rows["E52"]["status"] == "VERIFIED_FINITE"
    assert rows["NG42"]["status"] == "REFUTED"
    for claim in ("P219", "P220", "P221", "P222", "P223", "P224", "P225", "P226"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["E53"]["status"] == "VERIFIED_FINITE"
    for claim in ("P227", "P228", "P229", "P231", "P232", "P233", "P234"):
        assert rows[claim]["status"] == "VERIFIED_THEOREM"
    assert rows["P230"]["status"] == "CONDITIONAL"
    assert rows["E54"]["status"] == "VERIFIED_FINITE"
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
    assert rows["P156"]["status"] == "VERIFIED_THEOREM"
    assert rows["P157"]["status"] == "VERIFIED_THEOREM"
    assert rows["P158"]["status"] == "VERIFIED_THEOREM"
    assert rows["P159"]["status"] == "VERIFIED_THEOREM"
    assert rows["P160"]["status"] == "CONDITIONAL"
    assert rows["P161"]["status"] == "VERIFIED_THEOREM"
    assert rows["E38"]["status"] == "VERIFIED_FINITE"
    assert rows["NG35"]["status"] == "REFUTED"
    assert rows["EXT17"]["status"] == "EXTERNAL_THEOREM"
    assert rows["P162"]["status"] == "VERIFIED_THEOREM"
    assert rows["P163"]["status"] == "VERIFIED_THEOREM"
    assert rows["P164"]["status"] == "VERIFIED_THEOREM"
    assert rows["P165"]["status"] == "VERIFIED_THEOREM"
    assert rows["E39"]["status"] == "VERIFIED_FINITE"
    assert rows["NG36"]["status"] == "REFUTED"
    assert rows["P166"]["status"] == "VERIFIED_THEOREM"
    assert rows["P167"]["status"] == "VERIFIED_THEOREM"
    assert rows["P168"]["status"] == "VERIFIED_THEOREM"
    assert rows["P169"]["status"] == "VERIFIED_THEOREM"
    assert rows["P170"]["status"] == "VERIFIED_THEOREM"
    assert rows["P171"]["status"] == "VERIFIED_THEOREM"
    assert rows["E40"]["status"] == "VERIFIED_FINITE"
    assert rows["NG37"]["status"] == "REFUTED"
    assert rows["NG38"]["status"] == "REFUTED"
    assert rows["H172"]["status"] == "OPEN"
    assert rows["P173"]["status"] == "VERIFIED_THEOREM"
    assert rows["P174"]["status"] == "VERIFIED_THEOREM"
    assert rows["P175"]["status"] == "VERIFIED_THEOREM"
    assert rows["P176"]["status"] == "VERIFIED_THEOREM"
    assert rows["P177"]["status"] == "VERIFIED_THEOREM"
    assert rows["P178"]["status"] == "CONDITIONAL"
    assert rows["E41"]["status"] == "VERIFIED_FINITE"
    assert rows["P179"]["status"] == "VERIFIED_THEOREM"
    assert rows["P180"]["status"] == "VERIFIED_THEOREM"
    assert rows["P181"]["status"] == "VERIFIED_THEOREM"
    assert rows["P182"]["status"] == "VERIFIED_THEOREM"
    assert rows["P183"]["status"] == "VERIFIED_THEOREM"
    assert rows["P184"]["status"] == "VERIFIED_THEOREM"
    assert rows["E42"]["status"] == "VERIFIED_FINITE"
    assert rows["NG39"]["status"] == "REFUTED"
    assert rows["P185"]["status"] == "VERIFIED_THEOREM"
    assert rows["P186"]["status"] == "VERIFIED_THEOREM"
    assert rows["P187"]["status"] == "VERIFIED_THEOREM"
    assert rows["P188"]["status"] == "VERIFIED_THEOREM"
    assert rows["P189"]["status"] == "VERIFIED_THEOREM"
    assert rows["P190"]["status"] == "VERIFIED_THEOREM"
    assert rows["E43"]["status"] == "VERIFIED_FINITE"
    assert rows["NG40"]["status"] == "REFUTED"
    assert rows["P191"]["status"] == "VERIFIED_THEOREM"
    assert rows["P192"]["status"] == "VERIFIED_THEOREM"
    assert rows["P193"]["status"] == "VERIFIED_THEOREM"
    assert rows["P194"]["status"] == "VERIFIED_THEOREM"
    assert rows["E44"]["status"] == "VERIFIED_FINITE"
    assert rows["H147"]["status"] == "VERIFIED_THEOREM"
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
        "P219",
        "P220",
        "P221",
        "P222",
        "P223",
        "P224",
        "P225",
        "P227",
        "P228",
        "P231",
        "P232",
        "P233",
        "P234",
        "P235",
        "P236",
        "P237",
        "P238",
        "P239",
        "P240",
        "E55",
        "P242",
        "P243",
        "P244",
        "P245",
        "P246",
        "NG43",
        "E56",
        "P247",
        "P248",
        "P249",
        "P250",
        "P251",
        "NG44",
        "NG45",
        "E57",
        "P252",
        "P253",
        "P254",
        "P255",
        "P256",
        "E58",
        "P257",
        "P258",
        "P259",
        "P260",
        "P261",
        "E59",
        "NG46",
        "P262",
        "P263",
        "P264",
        "P265",
        "P266",
        "P267",
        "E60",
        "EXT08",
        "E23",
        "E24",
        "E30",
        "E31",
        "E32",
        "E33",
        "E53",
        "E54",
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
