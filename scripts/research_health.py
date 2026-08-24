#!/usr/bin/env python3
"""Audit repository navigation, claim labels, and tracked evidence hashes."""

from __future__ import annotations

import hashlib
import json
import re
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
FOCUS_IDS = ("P54", "H54", "C04", "C05", "P63", "P64", "P66", "P67", "P68", "NG19", "E17")
NAVIGATION_FILES = (Path("README.md"), Path("docs/INDEX.md"), Path("docs/HANDOFF.md"), Path("docs/AI_RESEARCH_GUIDE.md"))


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
    for claim_id in FOCUS_IDS:
        if claim_id not in result:
            errors.append(f"active focus claim missing: {claim_id}")
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


def run(root: Path) -> dict[str, object]:
    phase, reports = latest_phase(root)
    claim_map, claim_errors = claims(root)
    manifest_hash, tracked_count, manifest_errors = manifest_audit(root)
    errors = claim_errors + manifest_errors + navigation_audit(root, phase)
    verifier_path = root / "artifacts/two_tail_verifier.json"
    if not verifier_path.exists():
        errors.append("latest supplemental verifier artifact missing")
        verifier = None
    else:
        verifier = json.loads(verifier_path.read_text(encoding="utf-8"))
        if verifier.get("valid") is not True or verifier.get("proves_collatz") is not False:
            errors.append("latest supplemental verifier boundary mismatch")
    counts = Counter(claim_map.values())
    return {
        "valid": not errors,
        "latest_phase": phase,
        "phase_reports": reports,
        "claim_count": len(claim_map),
        "claim_status_counts": dict(sorted(counts.items())),
        "active_focus": {claim_id: claim_map.get(claim_id) for claim_id in FOCUS_IDS},
        "tracked_artifact_count": tracked_count,
        "manifest_sha256": manifest_hash,
        "latest_supplemental_verifier": verifier,
        "errors": errors,
        "proves_collatz": False,
    }


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    result = run(root)
    print(json.dumps(result, indent=2, sort_keys=True))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
