#!/usr/bin/env python3
"""Exact finite witnesses for real prescribed-branch / 2-adic scope audit.

This generator does not prove infinite statements; their proofs are in the note.
No Collatz counterexample or counterexample to EXT08's statement is asserted.
"""
from __future__ import annotations

# Adapted from the supplied EXT08 audit bundle after source/math review.
# Independence is representational, not a claim of separate human authorship.
import argparse
from fractions import Fraction
import hashlib
import json
from pathlib import Path
from itertools import product

BASE = "44430b21705bd69acb6cc29760ee27bdf2433b1f"
MODELS = (
    # name, u_0=A_0/2^b, forced initial word, deficit in 5q >= 4n-deficit
    ("dyadic_real_minus_three_halves", 1, 1, "", 3),
    ("integer_real_minus_two", 1, 0, "1", 3),
    ("safe_repeated_real_minus_five", 4, 0, "110" * 12 + "0", 32),
)

def fstr(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"

def build(steps: int = 4096) -> dict:
    if type(steps) is not int or not 64 <= steps <= 16384:
        raise ValueError("steps must be an integer between 64 and 16384")
    points = set(range(51)) | {2**k for k in range(6, 15) if 2**k <= steps} | {steps}
    models = []
    for name, a0, b, forced, deficit in MODELS:
        a, q, B, power3 = a0, 0, 0, 1
        x0 = -1 - Fraction(a0, 1 << b)
        bits: list[str] = []
        digest = hashlib.sha256()
        checkpoints = []
        all_safe = True
        min_density_margin = 0
        first_literal_mismatch = None
        for n in range(steps + 1):
            x = Fraction(-((1 << (n+b)) + a), 1 << (n+b))
            partial = Fraction(-B, power3)
            assert partial > x0
            assert partial - x0 == -x * Fraction(1 << n, power3)
            assert 5*q >= 4*n - deficit
            min_density_margin = min(min_density_margin, 5*q-4*n)
            if n and power3 <= 1 << n:
                all_safe = False
            digest.update(f"{n}|{q}|{fstr(x)}|{fstr(partial)}\n".encode())
            if n in points:
                residue = 0 if n == 0 else (-B * pow(power3, -1, 1 << n)) % (1 << n)
                checkpoints.append({"n": n, "q": q, "state": fstr(x),
                                    "partial_real_series": fstr(partial),
                                    "canonical_source_mod_2n": str(residue)})
            if n == steps:
                break
            bit = int(forced[n]) if n < len(forced) else int(a < 1 << (n+b))
            # Literal parity is meaningful for a rational with odd denominator.
            if x.denominator & 1 and first_literal_mismatch is None:
                parity = x.numerator & 1
                if bit != parity:
                    first_literal_mismatch = {"time": n, "state": fstr(x),
                                              "prescribed_bit": bit, "literal_bit": parity}
            bits.append(str(bit))
            if bit:
                a = 3*a
                B = 3*B + (1 << n)
                q += 1
                power3 *= 3
            else:
                a -= 1 << (n+b)
            assert a > 0
        models.append({"name": name, "initial_u_numerator": a0,
                       "initial_u_denominator_exponent": b,
                       "forced_prefix": forced, "density_deficit": deficit,
                       "real_limit": fstr(x0), "word": "".join(bits),
                       "q_final": q, "state_and_series_sha256": digest.hexdigest(),
                       "all_nonempty_finite_prefixes_coefficient_safe": all_safe,
                       "minimum_5q_minus_4n": min_density_margin,
                       "first_literal_mismatch": first_literal_mismatch,
                       "checkpoints": checkpoints})
    return {
        "format_version": 1, "repository_base": BASE, "steps_per_model": steps,
        "scope": {
            "canonical_collatz_form_series": True,
            "prescribed_real_branches_are_literal_collatz_orbits": False,
            "aperiodicity_and_limits_require_written_infinite_proofs": True,
            "counterexample_to_external_auxiliary_real_claims": True,
            "counterexample_to_EXT08_theorem_statement": False,
            "rationality_of_corresponding_2adic_sources_determined": False,
            "positive_integer_infinite_sources_claimed": False,
            "proves_collatz": False,
        },
        "models": models,
        "exact_constants": {
            "block_growth": "81/32", "density_lower_bound": "4/5",
            "safe_prefix_margin_numerator": str(9**12-4*8**12),
            "safe_prefix_multiplier_after_two_zeros": fstr(Fraction(9**12,4*8**12)),
        },
        "lemma24_repetition": {"model": "safe_repeated_real_minus_five",
                              "first_time": 0, "second_time": 3, "state": "-5/1"},
    }


def regressions() -> dict:
    words = {"1", "0", "110", "111", "11101", "1100", "111011100"}
    for m in range(2, 13):
        for source in (2**m-1, 8**m-5):
            x, bits = source, []
            for _ in range(64):
                b = x & 1
                bits.append(str(b))
                x = (3*x+1)//2 if b else x//2
            words.add("".join(bits))
    for k in range(1, 5):
        words.update("".join(p) for p in product(("110", "111"), repeat=k))
    words.update("11101"*r+"1100"*s for r in range(1, 5) for s in range(1, 5))
    rows = []
    for w in sorted(words, key=lambda w:(len(w),w)):
        b, q = 0, 0
        for k, s in enumerate(w):
            if s == "1":
                b, q = 3*b+2**k, q+1
        n = len(w)
        residue = (-b*pow(3**q,-1,2**n)) % 2**n
        source = residue or 2**n
        rows.append({"word":w, "B":str(b), "q":q, "residue":str(residue),
                     "positive_source":str(source), "endpoint":str((3**q*source+b)//2**n)})
    cycles = []
    for source in (1, -1, -5):
        x, states = source, []
        for _ in range(96):
            states.append(x)
            x = (3*x+1)//2 if x&1 else x//2
        cycles.append({"source":source,"states":states,"endpoint":x})
    return {"words":rows,"cycles":cycles,"proves_collatz":False}


def impact(root: Path) -> dict:
    paths = ["phase20_theory.json", "phase20_literature_audit.json", "phase20_verifier.json",
             "phase21_theory.json", "phase21_literature_audit.json", "phase21_obstruction_report.md",
             "phase21_verifier.json"]
    return {
        "audit_id":"ext08-scope-audit", "repository_base":"2da31e63c87f7c2225899f2d2c500629a0e5668d",
        "proposal_base":BASE,
        "bundle_sha256":"e4d5692be68bbbe0e08e4380b87623b2e6ce61b78a564d2bb0aa6775074550aa",
        "primary_source":{"url":"https://arxiv.org/pdf/2101.12747v1",
                          "sha256":"e4c5bccec262d8fdb001d7970dee56c347c03d789796c165e79a18dc2d584b9a",
                          "printed_pages":[4,7,8,28,29,30]},
        "status_transition":{"claim":"EXT08","from":"EXTERNAL_THEOREM","to":"OPEN",
                             "reason":"Auxiliary real/2-adic bridge refuted; theorem statement not refuted"},
        "conditional_claims":["P119","P121","P123","P124","P128"],
        "independent_claims":["P118","P120","P122","P125","P126","P127","P219","P220","P221","P222","P242","P243"],
        "open_obligations":["H112","H72","H89","H133"],
        "historical_files":[{"path":"artifacts/"+p,"sha256":hashlib.sha256((root/"artifacts"/p).read_bytes()).hexdigest()} for p in paths],
        "historical_verification_is_current_theorem_acceptance":False,
        "EXT08_statement_refuted":False, "proves_collatz":False}


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artifact-dir",type=Path,default=Path("artifacts"))
    ns = ap.parse_args()
    ns.artifact_dir.mkdir(parents=True,exist_ok=True)
    root = Path(__file__).resolve().parents[1]
    for name, data in (("models",build()),("regressions",regressions()),("impact",impact(root))):
        (ns.artifact_dir/f"ext08_scope_{name}.json").write_text(json.dumps(data,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps({"generated":3,"proves_collatz":False}))


if __name__ == "__main__":
    main()
