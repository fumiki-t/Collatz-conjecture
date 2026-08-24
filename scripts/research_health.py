#!/usr/bin/env python3
"""Audit research metadata, claim labels, and accepted evidence boundaries."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import shlex
import subprocess
import sys
from collections import Counter
from pathlib import Path


ALLOWED_STATUSES = {
    "VERIFIED_THEOREM",
    "VERIFIED_FINITE",
    "CONDITIONAL",
    "EXTERNAL_THEOREM",
    "EXTERNAL_EVIDENCE",
    "HEURISTIC",
    "CONJECTURE",
    "REFUTED",
    "RETRACTED",
    "OPEN",
}
NAVIGATION_FILES = (Path("README.md"), Path("docs/INDEX.md"), Path("docs/HANDOFF.md"), Path("docs/AI_RESEARCH_GUIDE.md"))
REGISTRY_PATH = Path("research/registry.json")
EXPERIMENT_REQUIRED_KEYS = {
    "schema_version",
    "id",
    "status",
    "claim_ids",
    "objective",
    "exact_scope",
    "arithmetic",
    "commands",
    "independence",
    "adversarial_families",
    "artifacts",
    "stop_conditions",
    "interpretation_boundary",
    "proves_collatz",
}
EXPERIMENT_STATUSES = {"DRAFT", "RUNNING", "ACCEPTED", "FAILED", "ABANDONED"}


def digest(path: Path) -> str:
    result = hashlib.sha256()
    with path.open("rb") as stream:
        for block in iter(lambda: stream.read(1 << 20), b""):
            result.update(block)
    return result.hexdigest()


def latest_phase(root: Path) -> tuple[int, list[str]]:
    reports = [path.name for path in root.glob("PHASE*_RUN_RESULTS.md")]
    phases = [int(match.group(1)) for name in reports if (match := re.fullmatch(r"PHASE(\d+)_RUN_RESULTS\.md", name))]
    if not phases:
        raise ValueError("no phase result files found")
    return max(phases), sorted(reports, key=lambda name: int(re.search(r"\d+", name).group()))


def claims(root: Path) -> tuple[dict[str, str], list[str]]:
    ledger = (root / "docs/CLAIMS_LEDGER.md").read_text(encoding="utf-8")
    result: dict[str, str] = {}
    errors = []
    for line in ledger.splitlines():
        match = re.match(r"^\| ([A-Z][A-Z0-9-]*) \| `([A-Z_]+)` \|", line)
        if not match:
            continue
        claim_id, status = match.groups()
        if claim_id in result:
            errors.append(f"duplicate claim ID: {claim_id}")
        if status not in ALLOWED_STATUSES:
            errors.append(f"invalid status {status} for {claim_id}")
        result[claim_id] = status
    return result, errors


def tracked_artifacts(root: Path) -> set[str]:
    completed = subprocess.run(
        ["git", "ls-files", "artifacts"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return {Path(line).name for line in completed.stdout.splitlines() if line and not line.endswith("SHA256SUMS")}


def untracked_artifacts(root: Path) -> list[str]:
    completed = subprocess.run(
        ["git", "ls-files", "--others", "--exclude-standard", "artifacts"],
        cwd=root,
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted(line for line in completed.stdout.splitlines() if line)


def is_tracked(root: Path, relative: str) -> bool:
    completed = subprocess.run(
        ["git", "ls-files", "--error-unmatch", relative],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def commit_exists(root: Path, commit: str) -> bool:
    completed = subprocess.run(
        ["git", "cat-file", "-e", f"{commit}^{{commit}}"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    return completed.returncode == 0


def manifest_audit(root: Path) -> tuple[str, int, list[str]]:
    manifest = root / "artifacts/SHA256SUMS"
    rows = {}
    errors = []
    for line in manifest.read_text(encoding="ascii").splitlines():
        match = re.fullmatch(r"([0-9a-f]{64})  (.+)", line)
        if not match:
            errors.append(f"invalid manifest row: {line}")
            continue
        expected, name = match.groups()
        rows[name] = expected
    tracked = tracked_artifacts(root)
    for name in sorted(set(rows) - tracked):
        errors.append(f"untracked artifact listed in manifest: {name}")
    for name in sorted(tracked):
        path = root / "artifacts" / name
        if name not in rows:
            errors.append(f"tracked artifact missing from manifest: {name}")
        elif digest(path) != rows[name]:
            errors.append(f"artifact hash mismatch: {name}")
    return digest(manifest), len(tracked), errors


def navigation_audit(root: Path, phase: int) -> list[str]:
    errors = []
    marker = f"Phase {phase}"
    for relative in NAVIGATION_FILES:
        path = root / relative
        if not path.exists():
            errors.append(f"navigation file missing: {relative}")
        elif marker not in path.read_text(encoding="utf-8"):
            errors.append(f"{relative} does not mention {marker}")
    return errors


def load_registry(root: Path) -> dict[str, object]:
    return json.loads((root / REGISTRY_PATH).read_text(encoding="utf-8"))


def registry_audit(
    root: Path, phase: int, claim_map: dict[str, str]
) -> tuple[dict[str, object], dict[str, str | None], list[str]]:
    errors: list[str] = []
    try:
        registry = load_registry(root)
    except (OSError, json.JSONDecodeError) as exc:
        return {}, {}, [f"cannot load {REGISTRY_PATH}: {exc}"]

    repository = registry.get("repository")
    if not isinstance(repository, dict):
        return registry, {}, ["registry repository section missing"]
    if repository.get("latest_phase") != phase:
        errors.append("registry latest_phase does not match result reports")
    if repository.get("status") != "OPEN":
        errors.append("registry must retain repository status OPEN until proof audit")
    if repository.get("proves_collatz") is not False:
        errors.append("registry proves_collatz boundary mismatch")
    claim_source = repository.get("claim_source")
    if not isinstance(claim_source, str) or not (root / claim_source).is_file():
        errors.append("registry claim_source missing")

    documents = registry.get("canonical_documents")
    if not isinstance(documents, list) or not documents:
        errors.append("registry canonical_documents missing")
    else:
        for name in documents:
            if not isinstance(name, str) or not (root / name).is_file():
                errors.append(f"registry canonical document missing: {name}")

    active_focus: dict[str, str | None] = {}
    obligations = registry.get("active_obligations")
    if not isinstance(obligations, list) or not obligations:
        errors.append("registry active_obligations missing")
        obligations = []
    seen: set[str] = set()
    for entry in obligations:
        if not isinstance(entry, dict):
            errors.append("invalid active obligation entry")
            continue
        claim_id = entry.get("id")
        status = entry.get("status")
        if not isinstance(claim_id, str):
            errors.append("active obligation without claim ID")
            continue
        if claim_id in seen:
            errors.append(f"duplicate active obligation: {claim_id}")
        seen.add(claim_id)
        ledger_status = claim_map.get(claim_id)
        active_focus[claim_id] = ledger_status
        if ledger_status is None:
            errors.append(f"active obligation missing from ledger: {claim_id}")
        elif status != ledger_status:
            errors.append(f"registry status mismatch for {claim_id}: {status} != {ledger_status}")
        context = entry.get("context")
        if context is not None and (not isinstance(context, str) or not (root / context).is_file()):
            errors.append(f"active obligation context missing for {claim_id}: {context}")
        dependencies = entry.get("depends_on")
        if not isinstance(dependencies, list):
            errors.append(f"active obligation dependencies missing for {claim_id}")
        else:
            for dependency in dependencies:
                if dependency not in claim_map:
                    errors.append(f"unknown dependency {dependency} for {claim_id}")

    watch_claims = registry.get("watch_claims")
    if not isinstance(watch_claims, list):
        errors.append("registry watch_claims missing")
    else:
        for claim_id in watch_claims:
            active_focus[str(claim_id)] = claim_map.get(str(claim_id))
            if claim_id not in claim_map:
                errors.append(f"watch claim missing from ledger: {claim_id}")

    acceptance = registry.get("latest_acceptance")
    if not isinstance(acceptance, dict):
        errors.append("registry latest_acceptance missing")
    else:
        if acceptance.get("phase") != phase:
            errors.append("registry latest acceptance phase mismatch")
        for key in ("report", "verifier_artifact", "experiment_manifest"):
            relative = acceptance.get(key)
            if not isinstance(relative, str) or not (root / relative).is_file():
                errors.append(f"registry latest acceptance {key} missing: {relative}")

    return registry, active_focus, errors


def claim_index_audit(root: Path, claim_map: dict[str, str]) -> list[str]:
    errors: list[str] = []
    target = root / "research/claims-index.json"
    if not target.is_file():
        return ["machine-readable claims index missing"]
    completed = subprocess.run(
        [sys.executable, "scripts/build_claim_index.py", "--check"],
        cwd=root,
        check=False,
        capture_output=True,
        text=True,
    )
    if completed.returncode != 0:
        errors.append(completed.stderr.strip() or "machine-readable claims index is stale")
        return errors
    try:
        index = json.loads(target.read_text(encoding="utf-8"))
    except json.JSONDecodeError as exc:
        return [f"machine-readable claims index invalid: {exc}"]
    rows = index.get("claims")
    if not isinstance(rows, list):
        return ["machine-readable claims index rows missing"]
    indexed = {row.get("id"): row.get("status") for row in rows if isinstance(row, dict)}
    if indexed != claim_map:
        errors.append("machine-readable claims index does not match ledger IDs/statuses")
    for row in rows:
        if not isinstance(row, dict):
            errors.append("machine-readable claims index contains a non-object row")
            continue
        for dependency in row.get("dependency_ids", []):
            if dependency not in claim_map:
                errors.append(f"claims index contains unknown dependency {dependency} for {row.get('id')}")
    return errors


def verifier_source_from_command(root: Path, command: str) -> Path | None:
    for token in shlex.split(command):
        if token.startswith("verifier/") and token.endswith(".py"):
            return root / token
    return None


def validate_experiment_manifest(
    root: Path,
    manifest: dict[str, object],
    claim_map: dict[str, str],
    mandatory_families: set[str],
) -> list[str]:
    experiment_id = manifest.get("id", "<unknown>")
    errors = [
        f"experiment {experiment_id} missing key: {key}"
        for key in sorted(EXPERIMENT_REQUIRED_KEYS - set(manifest))
    ]
    if manifest.get("schema_version") != 1:
        errors.append(f"experiment {experiment_id} schema_version mismatch")
    if manifest.get("status") not in EXPERIMENT_STATUSES:
        errors.append(f"experiment {experiment_id} has invalid status")
    if manifest.get("proves_collatz") is not False:
        errors.append(f"experiment {experiment_id} proves_collatz must be false")

    claim_ids = manifest.get("claim_ids")
    if not isinstance(claim_ids, list) or not claim_ids:
        errors.append(f"experiment {experiment_id} has no claim IDs")
    else:
        for claim_id in claim_ids:
            if claim_id not in claim_map:
                errors.append(f"experiment {experiment_id} references unknown claim {claim_id}")

    arithmetic = manifest.get("arithmetic")
    if not isinstance(arithmetic, dict) or arithmetic.get("proof_decisions") != "exact":
        errors.append(f"experiment {experiment_id} does not require exact proof decisions")

    families = manifest.get("adversarial_families")
    if not isinstance(families, list) or not mandatory_families.issubset(set(families)):
        errors.append(f"experiment {experiment_id} omits a mandatory adversarial family")

    commands = manifest.get("commands")
    if not isinstance(commands, dict):
        errors.append(f"experiment {experiment_id} commands missing")
    else:
        generators = commands.get("generator")
        verifiers = commands.get("verifier")
        tests = commands.get("tests")
        if not all(isinstance(rows, list) and rows for rows in (generators, verifiers, tests)):
            errors.append(f"experiment {experiment_id} generator/verifier/tests commands incomplete")
        elif set(generators) & set(verifiers):
            errors.append(f"experiment {experiment_id} reuses a generator command as verifier")

    independence = manifest.get("independence")
    if not isinstance(independence, dict):
        errors.append(f"experiment {experiment_id} independence section missing")
    else:
        forbidden = independence.get("forbidden_imports")
        tamper_tests = independence.get("tamper_tests")
        if not isinstance(forbidden, list) or not forbidden:
            errors.append(f"experiment {experiment_id} forbidden imports missing")
        if not isinstance(tamper_tests, list) or not tamper_tests:
            errors.append(f"experiment {experiment_id} tamper tests missing")
        else:
            for test in tamper_tests:
                if not isinstance(test, str) or not (root / test).is_file():
                    errors.append(f"experiment {experiment_id} tamper test missing: {test}")
        if isinstance(forbidden, list) and isinstance(commands, dict):
            for command in commands.get("verifier", []):
                source_path = verifier_source_from_command(root, command)
                if source_path is None or not source_path.is_file():
                    errors.append(f"experiment {experiment_id} verifier source not found in command")
                    continue
                source = source_path.read_text(encoding="utf-8")
                for needle in forbidden:
                    if isinstance(needle, str) and needle in source:
                        errors.append(f"experiment {experiment_id} verifier contains forbidden import text: {needle}")

    if manifest.get("status") == "ACCEPTED":
        if not isinstance(manifest.get("recorded_result"), dict):
            errors.append(f"accepted experiment {experiment_id} recorded_result missing")
        artifacts = manifest.get("artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            errors.append(f"accepted experiment {experiment_id} artifacts missing")
        else:
            for artifact in artifacts:
                if not isinstance(artifact, str) or not (root / artifact).is_file():
                    errors.append(f"accepted experiment {experiment_id} artifact missing: {artifact}")
                elif not is_tracked(root, artifact):
                    errors.append(f"accepted experiment {experiment_id} artifact is not Git-tracked: {artifact}")
        result = manifest.get("recorded_result")
        if isinstance(result, dict):
            recorded_hash = result.get("manifest_sha256")
            manifest_path = root / "artifacts/SHA256SUMS"
            if recorded_hash != digest(manifest_path):
                errors.append(f"accepted experiment {experiment_id} manifest hash mismatch")
            commit = result.get("commit")
            if not isinstance(commit, str) or not commit_exists(root, commit):
                errors.append(f"accepted experiment {experiment_id} commit is not available: {commit}")
    return errors


def experiment_audit(
    root: Path, claim_map: dict[str, str], registry: dict[str, object]
) -> tuple[list[str], list[str]]:
    errors: list[str] = []
    accepted: list[str] = []
    schema = root / "research/schemas/experiment.schema.json"
    if not schema.is_file():
        errors.append("experiment JSON schema missing")
    else:
        try:
            json.loads(schema.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"experiment JSON schema invalid: {exc}")
    families = registry.get("mandatory_adversarial_families", [])
    mandatory_families = set(families) if isinstance(families, list) else set()
    if not mandatory_families:
        errors.append("registry mandatory_adversarial_families missing")
    paths = sorted((root / "research/experiments").glob("*.json"))
    if not paths:
        errors.append("no experiment manifests found")
    for path in paths:
        try:
            manifest = json.loads(path.read_text(encoding="utf-8"))
        except json.JSONDecodeError as exc:
            errors.append(f"invalid experiment manifest {path.name}: {exc}")
            continue
        if not isinstance(manifest, dict):
            errors.append(f"experiment manifest {path.name} must contain a JSON object")
            continue
        errors.extend(validate_experiment_manifest(root, manifest, claim_map, mandatory_families))
        if manifest.get("status") == "ACCEPTED":
            accepted.append(str(manifest.get("id")))
    return accepted, errors


def run(root: Path, strict: bool = False) -> dict[str, object]:
    phase, reports = latest_phase(root)
    claim_map, claim_errors = claims(root)
    manifest_hash, tracked_count, manifest_errors = manifest_audit(root)
    registry, active_focus, registry_errors = registry_audit(root, phase, claim_map)
    accepted_experiments, experiment_errors = experiment_audit(root, claim_map, registry)
    untracked = untracked_artifacts(root)
    warnings = [f"untracked artifact outside accepted manifest: {path}" for path in untracked]
    errors = (
        claim_errors
        + manifest_errors
        + navigation_audit(root, phase)
        + registry_errors
        + claim_index_audit(root, claim_map)
        + experiment_errors
    )
    if strict:
        errors.extend(f"strict mode: {warning}" for warning in warnings)

    acceptance = registry.get("latest_acceptance", {})
    verifier_name = acceptance.get("verifier_artifact") if isinstance(acceptance, dict) else None
    verifier_path = root / verifier_name if isinstance(verifier_name, str) else None
    if verifier_path is None or not verifier_path.exists():
        errors.append("latest acceptance verifier artifact missing")
        verifier = None
    else:
        verifier = json.loads(verifier_path.read_text(encoding="utf-8"))
        expected = acceptance.get("expected_verifier_fields", {})
        if not isinstance(expected, dict):
            errors.append("latest acceptance expected verifier fields missing")
        else:
            for key, value in expected.items():
                if verifier.get(key) != value:
                    errors.append(f"latest acceptance verifier mismatch: {key}")
    counts = Counter(claim_map.values())
    return {
        "valid": not errors,
        "strict": strict,
        "latest_phase": phase,
        "phase_reports": reports,
        "claim_count": len(claim_map),
        "claim_status_counts": dict(sorted(counts.items())),
        "claim_index": "research/claims-index.json",
        "active_focus": active_focus,
        "tracked_artifact_count": tracked_count,
        "untracked_artifacts": untracked,
        "manifest_sha256": manifest_hash,
        "latest_supplemental_verifier": verifier,
        "accepted_experiments": accepted_experiments,
        "registry": str(REGISTRY_PATH),
        "warnings": warnings,
        "errors": errors,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="treat untracked files under artifacts/ as acceptance errors",
    )
    args = parser.parse_args()
    root = Path(__file__).resolve().parents[1]
    result = run(root, strict=args.strict)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
