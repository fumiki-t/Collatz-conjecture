#!/usr/bin/env python3
"""Independent finite reconstruction: exact rational dynamics and source lifting.

Does not import the generator. Infinity/aperiodicity are proved in the note,
not inferred from any finite nonrepetition test.
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

class InvalidCertificate(ValueError):
    pass

def require(test: bool, message: str) -> None:
    if not test:
        raise InvalidCertificate(message)

def fs(x: Fraction) -> str:
    return f"{x.numerator}/{x.denominator}"

def validate(data: dict) -> dict:
    require(isinstance(data,dict), "object required")
    require(type(data.get("format_version")) is int and data["format_version"] == 1, "format")
    require(data.get("repository_base") == "44430b21705bd69acb6cc29760ee27bdf2433b1f", "base")
    scope = {
        "canonical_collatz_form_series": True,
        "prescribed_real_branches_are_literal_collatz_orbits": False,
        "aperiodicity_and_limits_require_written_infinite_proofs": True,
        "counterexample_to_external_auxiliary_real_claims": True,
        "counterexample_to_EXT08_theorem_statement": False,
        "rationality_of_corresponding_2adic_sources_determined": False,
        "positive_integer_infinite_sources_claimed": False,
        "proves_collatz": False,
    }
    require(json.dumps(data.get("scope"),sort_keys=True) == json.dumps(scope,sort_keys=True), "scope/overclaim")
    N = data.get("steps_per_model")
    require(type(N) is int and 64 <= N <= 16384, "finite range")
    specs = (
        ("dyadic_real_minus_three_halves", Fraction(-3,2), "", 3, 1, 1, 0),
        ("integer_real_minus_two", Fraction(-2), "1", 3, 1, 0, 1),
        ("safe_repeated_real_minus_five", Fraction(-5), "110"*12+"0", 32, 4, 0, 37),
    )
    models = data.get("models")
    require(isinstance(models,list) and len(models)==3, "model list")
    points = set(range(51)) | {2**k for k in range(6,15) if 2**k <= N} | {N}
    total_literal_steps = 0
    summaries = []
    for entry, (name,x0,forced,deficit,a0,b,tail_begin) in zip(models,specs):
        require(all(type(entry.get(k)) is int for k in ("initial_u_numerator", "initial_u_denominator_exponent", "density_deficit", "q_final", "minimum_5q_minus_4n")), "integer metadata")
        require(entry.get("name")==name, "model order")
        require(entry.get("initial_u_numerator")==a0 and entry.get("initial_u_denominator_exponent")==b, "initial encoding")
        require(entry.get("forced_prefix")==forced and entry.get("density_deficit")==deficit, "schedule")
        require(entry.get("real_limit")==fs(x0), "real limit")
        word = entry.get("word")
        require(isinstance(word,str) and len(word)==N and set(word)<=set("01"), "word")
        # This implementation uses the actual rational x, not the A recurrence.
        x, partial, coefficient = x0, Fraction(0), Fraction(1)
        q = 0
        residue, lifted_endpoint, power3 = 0, 0, 1
        digest = hashlib.sha256()
        checkpoints = []
        first_mismatch = None
        min_margin = 0
        all_safe = True
        old_residue = 0
        states_early = []
        for n in range(N+1):
            require(partial > x0, f"real error sign {name}/{n}")
            require(partial - x0 == -x/coefficient, f"affine split {name}/{n}")
            require(partial.denominator & 1 == 1, "odd partial denominator")
            require(5*q >= 4*n-deficit, f"density {name}/{n}")
            min_margin = min(min_margin, 5*q-4*n)
            if n and coefficient <= 1:
                all_safe = False
            if n >= tail_begin:
                require(Fraction(-5,2) <= x < -1, f"invariant interval {name}/{n}")
                if name == "dyadic_real_minus_three_halves":
                    require(x.denominator == 1 << (n+1), "dyadic denominator")
                elif name == "integer_real_minus_two":
                    require(x.denominator == 1 << n, "integer denominator")
                else:
                    require(x.denominator == 1 << (n-36), "cycle escape denominator")
            if n:
                require((residue-old_residue) % (1 << (n-1)) == 0, "nested residues")
            old_residue = residue
            digest.update(f"{n}|{q}|{fs(x)}|{fs(partial)}\n".encode())
            if n < 5:
                states_early.append(fs(x))
            if n in points:
                require(0 <= residue < 1 << n, "canonical range")
                require((partial.numerator-residue*partial.denominator) % (1 << n) == 0, "2-adic partial relation")
                row = {"n":n,"q":q,"state":fs(x), "partial_real_series":fs(partial),
                       "canonical_source_mod_2n":str(residue)}
                checkpoints.append(row)
                # Independent literal replay from the positive finite source.
                if n:
                    z = residue
                    require(z > 0, "finite positive source")
                    for s in word[:n]:
                        require(z % 2 == int(s), "literal finite-prefix replay")
                        z = (3*z+1)//2 if z % 2 else z//2
                        total_literal_steps += 1
                    require(z == lifted_endpoint, "bit-lift endpoint")
            if n == N:
                break
            bit = int(word[n])
            expected = int(forced[n]) if n < len(forced) else int(x > -2)
            require(bit == expected, f"prescribed branch {name}/{n}")
            if x.denominator & 1 and first_mismatch is None and bit != x.numerator % 2:
                first_mismatch = {"time":n,"state":fs(x),"prescribed_bit":bit,"literal_bit":x.numerator%2}
            # Standard finite source lifting, independent of modular inverse.
            if lifted_endpoint % 2 != bit:
                residue += 1 << n
                lifted_endpoint += power3
            require(lifted_endpoint % 2 == bit, "lifting parity")
            lifted_endpoint = (3*lifted_endpoint+1)//2 if bit else lifted_endpoint//2
            if bit:
                # Positional Collatz series rather than affine-B recurrence.
                partial -= Fraction(1 << n, 3**(q+1))
                x = (3*x+1)/2
                coefficient *= Fraction(3,2)
                q += 1
                power3 *= 3
            else:
                x /= 2
                coefficient /= 2
        require(entry.get("q_final")==q, "odd count")
        require(entry.get("state_and_series_sha256")==digest.hexdigest(), "all-prefix digest")
        require(json.dumps(entry.get("checkpoints"),sort_keys=True)==json.dumps(checkpoints,sort_keys=True), "checkpoint rows")
        require(entry.get("first_literal_mismatch")==first_mismatch, "literal mismatch")
        require(entry.get("minimum_5q_minus_4n")==min_margin, "density minimum")
        require(entry.get("all_nonempty_finite_prefixes_coefficient_safe") is all_safe, "safety field")
        if name == "safe_repeated_real_minus_five":
            require(all_safe, "safe countermodel")
            require(states_early[0]==states_early[3]=="-5/1", "Lemma24 repeat")
            require(first_mismatch == {"time":36,"state":"-5/1","prescribed_bit":0,"literal_bit":1}, "first exit from literal cycle")
        summaries.append({"name":name,"checked_prefixes":N+1,"q":q,
                          "safe_in_checked_range":all_safe,"first_literal_mismatch":first_mismatch,
                          "all_prefix_digest":digest.hexdigest()})
    require(3**4 > 2**5, "strict density margin")
    require(9**12 > 4*8**12, "safe-prefix threshold")
    require(data.get("exact_constants") == {
        "block_growth":"81/32", "density_lower_bound":"4/5",
        "safe_prefix_margin_numerator":str(9**12-4*8**12),
        "safe_prefix_multiplier_after_two_zeros":fs(Fraction(9**12,4*8**12)),
    }, "exact constants")
    require(data.get("lemma24_repetition") == {"model":"safe_repeated_real_minus_five",
             "first_time":0,"second_time":3,"state":"-5/1"}, "repeat metadata")
    return {"valid":True, "generator_imported":False, "models":summaries,
            "checked_prefixes_total":3*(N+1), "literal_finite_prefix_steps":total_literal_steps,
            "infinite_proofs_machine_formalized":False,
            "EXT08_statement_refuted":False, "proves_collatz":False}


def verify_regressions(data: dict) -> int:
    words = {"0", "1", "110", "111", "11101", "1100", "111011100"}
    for m in range(2,13):
        for n in ((1<<m)-1,(1<<(3*m))-5):
            out = ""
            for _ in range(64):
                out += str(n%2)
                n = (n//2)*3+2 if n%2 else n//2
            words.add(out)
    for k in range(1,5):
        for bits in product("01",repeat=k):
            words.add("".join("110" if b=="0" else "111" for b in bits))
    words.update("11101"*r+"1100"*s for r in range(1,5) for s in range(1,5))
    rows = data.get("words",[])
    require([r["word"] for r in rows]==sorted(words,key=lambda w:(len(w),w)),"regression domain")
    for row in rows:
        w = row["word"]
        positions = [i for i,s in enumerate(w) if s=="1"]
        q = len(positions)
        B = sum(2**d*3**(q-1-j) for j,d in enumerate(positions))
        r, endpoint, power = 0,0,1
        for i,s in enumerate(w):
            if endpoint%2 != int(s):
                r += 2**i
                endpoint += power
            endpoint = (3*endpoint+1)//2 if s=="1" else endpoint//2
            power *= 3 if s=="1" else 1
        source = r or 2**len(w)
        x = source
        for s in w:
            require(x%2==int(s),"regression literal parity")
            x = (3*x+1)//2 if x%2 else x//2
        expected = {"word":w,"B":str(B),"q":q,"residue":str(r),"positive_source":str(source),"endpoint":str(x)}
        require(json.dumps(row,sort_keys=True)==json.dumps(expected,sort_keys=True),"regression arithmetic")
    controls = []
    for n,pattern in ((1,(1,2)),(-1,(-1,)),(-5,(-5,-7,-10))):
        controls.append({"source":n,"states":[pattern[i%len(pattern)] for i in range(96)],"endpoint":n})
    require(data.get("cycles")==controls,"cycle controls")
    require(data.get("proves_collatz") is False,"regression scope")
    return len(rows)


def audit(directory: Path, root: Path | None = None) -> dict:
    root = root or Path(__file__).resolve().parents[1]
    result = validate(json.loads((directory/"ext08_scope_models.json").read_text()))
    require(result["checked_prefixes_total"]==12291,"accepted finite range")
    result["regression_words"] = verify_regressions(json.loads((directory/"ext08_scope_regressions.json").read_text()))
    # The supersession record is a metadata contract, not a machine proof of
    # the infinite lemmas or of a defect in an external publication.
    from scripts.audit_claim_supersession import audit_supersession
    errors = audit_supersession(root, json.loads((directory/"ext08_scope_impact.json").read_text()))
    require(not errors,"supersession: "+"; ".join(errors))
    result["historical_files_preserved"] = 7
    result["current_EXT08_status"] = "OPEN"
    return result


def main() -> None:
    import sys
    sys.path.insert(0,str(Path(__file__).resolve().parents[1]))
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--artifact-dir",type=Path,default=Path("artifacts"))
    ap.add_argument("--output",type=Path)
    ns = ap.parse_args()
    try:
        result = audit(ns.artifact_dir)
    except (OSError,ValueError,TypeError,KeyError,ArithmeticError) as exc:
        result = {"valid":False,"error":str(exc),"proves_collatz":False}
    if ns.output:
        ns.output.write_text(json.dumps(result,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False))
    if not result["valid"]:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
