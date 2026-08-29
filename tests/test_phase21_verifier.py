from __future__ import annotations

import copy
import json
from pathlib import Path

import pytest

from verifier.verify_phase21 import expected_theory, verify_metadata


ROOT = Path(__file__).resolve().parents[1]


def write_metadata(root: Path, theory: dict[str, object]) -> None:
    root.mkdir(parents=True, exist_ok=True)
    (root / "phase21_theory.json").write_text(json.dumps(theory), encoding="utf-8")
    literature = json.loads((ROOT / "artifacts/phase21_literature_audit.json").read_text(encoding="utf-8"))
    (root / "phase21_literature_audit.json").write_text(json.dumps(literature), encoding="utf-8")


def test_recorded_verifier_result() -> None:
    report = json.loads((ROOT / "artifacts/phase21_verifier.json").read_text(encoding="utf-8"))
    assert report["valid"] is True
    assert report["proves_collatz"] is False
    assert report["direct_sources"] == 299999
    assert report["critical_totals"] == {
        "critical_words": 502523,
        "geodesic_words": 406353,
        "repetition_excluded": 160429,
        "geodesic_repetition_excluded": 120982,
    }


def mutate_weak(theory: dict[str, object]) -> None:
    claim = theory["claims"]["P126"]
    claim["statement"] = claim["statement"].replace(" < ", " <= ")


def mutate_periodic(theory: dict[str, object]) -> None:
    claim = theory["claims"]["P126"]
    claim["statement"] = claim["statement"].replace("non-eventually-periodic ", "")


def mutate_h_index(theory: dict[str, object]) -> None:
    claim = theory["claims"]["P126"]
    claim["statement"] = claim["statement"].replace("h(j)", "h(i)")


def mutate_beta(theory: dict[str, object]) -> None:
    claim = theory["claims"]["P127"]
    claim["statement"] = claim["statement"].replace("3/2", "4/3")


def mutate_proof_status(theory: dict[str, object]) -> None:
    theory["proves_collatz"] = True


@pytest.mark.parametrize("mutator", [mutate_weak, mutate_periodic, mutate_h_index, mutate_beta, mutate_proof_status])
def test_metadata_tamper_rejected(tmp_path: Path, mutator) -> None:
    theory = copy.deepcopy(expected_theory())
    mutator(theory)
    write_metadata(tmp_path, theory)
    with pytest.raises(ValueError):
        verify_metadata(tmp_path)
