from __future__ import annotations

import json
import subprocess
import sys
from pathlib import Path

import pytest

from src.garcia_tal_formal_obstruction import generate
from verifier.verify_garcia_tal_formal_obstruction import verify


def write_certificate(path: Path, data: dict[str, object]) -> None:
    path.write_text(json.dumps(data, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def test_generator_and_independent_verifier(tmp_path: Path) -> None:
    certificate = tmp_path / "certificate.json"
    write_certificate(certificate, generate())
    result = verify(certificate)
    assert result["valid"] is True
    assert result["NG22"] == "REFUTED"
    assert result["E21"] == "VERIFIED_FINITE"
    assert result["proves_collatz"] is False

    completed = subprocess.run(
        [sys.executable, "verifier/verify_garcia_tal_formal_obstruction.py", str(certificate)],
        check=False,
        capture_output=True,
        text=True,
    )
    assert completed.returncode == 0, completed.stdout + completed.stderr


@pytest.mark.parametrize(
    ("mutator", "message"),
    [
        (lambda data: data.__setitem__("proves_collatz", True), "proves_collatz"),
        (lambda data: data["parameters"]["initial_h"].__setitem__("numerator", 4), "policy parameters"),
        (lambda data: data["parameters"].__setitem__("policy", "e=1 always"), "policy parameters"),
        (lambda data: data["classification"].__setitem__("NG22", "VERIFIED_THEOREM"), "NG22"),
        (
            lambda data: data["finite_certificate"]["checkpoints"][1].__setitem__(
                "canonical_residue_sha256_big_endian", "0" * 64
            ),
            "stored checkpoint",
        ),
        (lambda data: data["finite_certificate"].__setitem__("residue_delta_formula", "0"), "delta formula"),
    ],
)
def test_tampered_certificates_are_rejected(tmp_path: Path, mutator, message: str) -> None:
    certificate = tmp_path / "certificate.json"
    data = generate()
    mutator(data)
    write_certificate(certificate, data)
    with pytest.raises(ValueError, match=message):
        verify(certificate)


def test_verifier_does_not_import_generator() -> None:
    source = Path("verifier/verify_garcia_tal_formal_obstruction.py").read_text(encoding="utf-8")
    assert "garcia_tal_formal_obstruction" not in source
    assert "from src" not in source
