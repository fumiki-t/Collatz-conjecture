#!/usr/bin/env python3
"""Independent Phase 42 verifier: full iteration, positional sums, closed defects.

Does not import or invoke the search. Repeat witnesses are checked as finite
proofs, not accepted by comparing a stored 'valid' flag or a search digest.
"""
from __future__ import annotations

import argparse
import bisect
import hashlib
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path

KINDS = ("capacity", "carry", "repeats", "regressions")
BITS = (8, 16, 32, 64, 128, 256, 512, 1024)
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


class VerificationError(ValueError):
    pass


def require(ok, message):
    if not ok:
        raise VerificationError(message)


def canonical(value):
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value):
    return hashlib.sha256(canonical(value).encode()).hexdigest()


def same(actual, expected, name):
    # JSON equality also distinguishes true from 1, and false from 0.
    require(canonical(actual) == canonical(expected), f"{name}: reconstructed data mismatch")


def envelope(kind, **fields):
    return {"format": f"collatz-phase42-{kind}-v1", "proves_collatz": False, **fields}


def load_certificate(text):
    def pairs(entries):
        out = {}
        for k, v in entries:
            require(k not in out, "duplicate JSON key")
            out[k] = v
        return out
    def nonfinite(value):
        raise VerificationError(f"nonfinite JSON: {value}")
    try:
        return json.loads(text, object_pairs_hook=pairs, parse_constant=nonfinite)
    except (TypeError, json.JSONDecodeError) as exc:
        raise VerificationError("invalid JSON") from exc


def positions(word):
    require(set(word) <= {"0", "1"}, "nonbinary word")
    ps = [i for i, bit in enumerate(word) if bit == "1"]
    q = len(ps)
    return q, sum((1 << p)*3**(q-1-j) for j, p in enumerate(ps))


def forward(S, L):
    states, bits = [S], []
    for _ in range(L):
        bit = states[-1] & 1
        bits.append(str(bit))
        states.append((3*states[-1]+1)//2 if bit else states[-1]//2)
    return "".join(bits), states


def literal(S, word):
    actual, states = forward(S, len(word))
    require(actual == word, "nonliteral path")
    q, B = positions(word)
    require((1 << len(word))*states[-1] == 3**q*S+B, "affine endpoint")
    return states


def safe(word):
    return all(3**word[:L].count("1") > 1 << L for L in range(1, len(word)+1))


def residue(word):
    # Lifting one bit of the actual starting value is independent of B decoding.
    r = 0
    for i, bit in enumerate(word):
        actual, st = forward(r, i)
        if st[-1] % 2 != int(bit):
            r += 1 << i
    return r or 1 << len(word)


def finite_prefix(S, limit=300):
    require(type(S) is int and S > 0 and S % 2 == 1, "odd positive source")
    require(type(limit) is int and limit >= 0, "nonnegative block cap")
    bits, states, seen = [], [S], {S}
    P, completed, last_E = 1, 0, 0
    while completed < limit:
        n = states[-1]
        bit = n & 1
        nxt = (3*n+1)//2 if bit else n//2
        Pnext = P*(3 if bit else 1)
        if Pnext <= 1 << (len(bits)+1) or nxt in seen:
            break
        P = Pnext
        bits.append(str(bit))
        states.append(nxt)
        seen.add(nxt)
        if nxt % 2:
            completed += 1
            last_E = len(bits)
    return "".join(bits[:last_E]), states[:last_E+1]


def capacity_row(S, limit=300):
    word, states = finite_prefix(S, limit)
    E = [i for i, b in enumerate(word) if b == "1"]+[len(word)]
    q = len(E)-1
    f = [(3**j).bit_length()-1 for j in range(q+1)]
    a = [f[j]-E[j] for j in range(q+1)]
    require(a[0] == 0 and min(a) >= 0, "origin/safety defect")
    require(len(set(states)) == len(states), "distinctness premise")
    Y = Fraction((1 << E[-1])*states[-1], 3**q)
    K = max(2, (3*Y.numerator // Y.denominator).bit_length()-1)
    while (1 << K)*Y.denominator < 3*Y.numerator:
        K += 1
    # Build the pure intervals by deleting the extra trailing zeros of each
    # individual accelerated segment. This also verifies orientation literally.
    reference = ["0"]*(f[-1]+1)
    for pos in f:
        reference[pos] = "1"
    reference = "".join(reference)
    blocks, run_start, run_length, D = [], 0, 0, 0
    for j in range(q):
        e, b = E[j+1]-E[j], f[j+1]-f[j]
        require(b in (1, 2) and a[j+1]-a[j] <= 1, "defect step")
        pure_length = min(e, b)
        D += e-pure_length
        require(word[E[j]:E[j]+pure_length] == reference[f[j]:f[j]+pure_length], "mechanical segment")
        require(set(word[E[j]+pure_length:E[j+1]]) <= {"0"}, "excluded suffix must be zero")
        run_length += pure_length
        if a[j+1] != a[j]:
            blocks.append([a[run_start], run_length, E[run_start], f[run_start]])
            run_start, run_length = j+1, 0
    blocks.append([a[run_start], run_length, E[run_start], f[run_start]])
    for r, ell, start, mechanical in blocks:
        require(word[start:start+ell] == reference[mechanical:mechanical+ell], "pure factor alignment")
        for t in range(start, start+ell):
            require(states[t]*Y.denominator < 3*(1 << r)*Y.numerator, "strict state height")
            require(states[t] < 1 << (r+K), "power-of-two state bound")
    H, J0 = max(a), max(a)+2*D+1
    height_sum = sum(r for r, _, _, _ in blocks)
    require(sum(ell for _, ell, _, _ in blocks)+D == E[-1], "length conservation")
    require(D == sum(max(x-y, 0) for x, y in zip(a, a[1:])), "downward variation")
    require(len(blocks) <= J0 and height_sum <= H*(H+1)//2+2*H*D, "run-count/height variation")
    factor_occurrences = 0
    for h in range(2*H+K+1):
        n, factors, residues = h+K, [], []
        for r, ell, start, _ in blocks:
            if r <= h:
                for t in range(start, start+ell-n+1):
                    factors.append(word[t:t+n])
                    residues.append(states[t] % (1 << n))
                    require(states[t] < 1 << n, "counted state height")
        require(len(factors) == len(set(factors)) == len(set(residues)), "parity separation")
        require(len(factors) <= n+1, "simultaneous mechanical capacity")
        factor_occurrences += len(factors)
    energy = sum(d*(d+1) for r, ell, _, _ in blocks for d in [max(ell-r-K+1, 0)])
    M = (2*H+K+1)*(2*H+3*K+2)
    require(energy <= M, "integrated capacity")
    base = H*(H+1)//2+2*H*D+(K-1)*J0+D
    residual = E[-1]-base
    require(residual <= 0 or residual**2 <= J0*M, "integer variation inequality")
    return {"source": S, "q": q, "E": E[-1], "word_sha256": hashlib.sha256(word.encode()).hexdigest(),
            "Y": [Y.numerator, Y.denominator], "K": K, "H": H, "D": D,
            "blocks": blocks, "height_sum": height_sum, "energy": energy, "M": M,
            "variation_base": base, "variation_residual": residual,
            "capacity_levels": 2*H+K+1, "factor_occurrences": factor_occurrences}


def capacity_expected():
    rows = [capacity_row(S) for S in range(1, 4096, 2)]
    return envelope("capacity", maximum_source=4095, maximum_odd_steps=300,
                    positive_odd_sources=len(rows), odd_steps=sum(r["q"] for r in rows),
                    pure_blocks=sum(len(r["blocks"]) for r in rows),
                    capacity_levels=sum(r["capacity_levels"] for r in rows),
                    factor_occurrences=sum(r["factor_occurrences"] for r in rows),
                    rows_sha256=digest(rows), samples=[r for r in rows if r["source"] in (1, 3, 7, 27, 167, 4095)],
                    hypotheses=["positive odd source", "complete coefficient-safe odd prefix", "distinct full states"],
                    all_finite_checks=True)


def forced_word(L, q, B):
    if min(L, q, B) < 0:
        return None
    r = (-B*pow(3**q, -1, 1 << L)) % (1 << L) or 1 << L
    w, _ = forward(r, L)
    return w if positions(w) == (q, B) else None


def carry_expected():
    def maximum(q):
        return sum(2**((3**j).bit_length()-1)*3**(q-j-1) for j in range(q))
    small = [[q, maximum(q), 5*3**q-4*2**q] for q in range(2, 21)]
    require(all(M < lower for _, M, lower in small), "q<=20 complete bound")
    q, P = 21, 3**21
    allowance = maximum(q)-5*P+4*2**q
    require(0 <= 6*allowance < P and maximum(q) < 9*P-8*2**q, "q21 complete pruning")
    original = [(3**j).bit_length()-1 for j in range(q)]
    rows, pattern_count = [], 0
    for shift in range(-1, q):
        ps = [p-int(j == shift) for j, p in enumerate(original)]
        if ps[0] < 0 or any(b <= a for a, b in zip(ps, ps[1:])):
            continue
        pattern_count += 1
        for L in range(ps[-1]+1, P.bit_length()):
            w = "".join(str(int(i in ps)) for i in range(L))
            require(safe(w), "q21 candidate target safety")
            Bd = positions(w)[1]
            for k, m in ((1, -3), (2, -1)):
                require((Bd+m*P) % 2**k == 0, "candidate divisibility")
                Ba = (Bd+m*P)//2**k
                require(forced_word(L-k, q, Ba) is None, "q21 unexpected literal alternative")
                rows.append([None if shift == -1 else shift, L, k, m, Ba, False])
    require(pattern_count == 12 and len(rows) == 48, "complete q21 scope")
    d, a = "1101101101101011010110110110110101", "111111111111011101101011000100100"
    Sd, Sa, y = 29023002619, 14511501311, 53013941237
    qd, Bd = positions(d)
    qa, Ba = positions(a)
    require(qd == qa == 22 and safe(d) and safe(a), "q22 witness coefficient safety")
    require(Sd == 2*Sa-3 and 2*Ba-Bd == -3*3**22, "negative carry identity")
    require(literal(Sd, d)[-1] == literal(Sa, a)[-1] == y and y % 2 == 1, "positive common odd endpoint")
    ps = [i for i, bit in enumerate(d) if bit == "1"]+[len(d)]
    return envelope("carry", minimum_odd_count=22, q_2_through_20=small,
                    q21_allowance=[allowance, P], q21_patterns=pattern_count,
                    q21_checks=rows, q21_other_k_m_lower=9*P-8*2**q,
                    witness={"target": d, "alternative": a, "target_source": Sd, "alternative_source": Sa,
                             "endpoint": y, "target_L_Q_B": [len(d), qd, Bd],
                             "alternative_L_Q_B": [len(a), qa, Ba], "carry": -3, "coefficient_gain": 2,
                             "target_exponents": [b-a for a, b in zip(ps, ps[1:])]},
                    scope="two positive literal coefficient-safe words, same q, shorter alternative, negative carry")


def closed_model(steps):
    """Only a square reached on a b=1 step can lag, and only for that step."""
    power, previous_f = 1, 0
    positions, defects = [0], [0]
    for j in range(1, steps+1):
        power *= 3
        f = power.bit_length()-1
        m = isqrt(j)
        A = m-int(j == m*m and f-previous_f == 1)
        positions.append(f-A)
        defects.append(A)
        previous_f = f
    word = bytearray(b"0"*positions[-1])
    for i, j in zip(positions, positions[1:]):
        require(j-i in (1, 2), "closed model exponent")
        word[i] = ord("1")
    boundaries = [0]+[positions[j] for j in range(1, steps+1) if defects[j] > defects[j-1]]
    return word.decode(), positions, boundaries


def verify_repeat(row):
    integer_fields = {"source_bits", "K", "h", "width", "clean_occurrences", "capacity", "first_start",
                      "second_start", "lcp", "prefix_length", "generated_odd_steps", "covering_odd_steps"}
    require(type(row) is dict and set(row) == integer_fields | {"split_bits", "odd_counts", "prefix_sha256"}, "repeat schema")
    require(all(type(row[k]) is int and row[k] >= 0 for k in integer_fields), "repeat integer fields")
    B = row["source_bits"]
    require(B in BITS and row["generated_odd_steps"] == (B//2+60)**2, "fixed construction scope")
    word, odd_positions, boundaries = closed_model(row["generated_odd_steps"])
    i, j, n, h, K = (row[k] for k in ("first_start", "second_start", "width", "h", "K"))
    require(K == (3*((1 << B)+4)-1).bit_length() and n == h+K, "exact width enclosure")
    require(0 <= h < len(boundaries)-1 and 0 <= i < j < len(word), "repeat range")
    lengths = [b-a for a, b in zip(boundaries, boundaries[1:])]
    clean = sum(max(ell-n+1, 0) for ell in lengths[:h+1])
    same([clean, n+1], [row["clean_occurrences"], row["capacity"]], "capacity metadata")
    require(clean > n+1, "nonvacuous capacity obstruction")
    require(all(sum(max(ell-t-K+1, 0) for ell in lengths[:t+1]) <= t+K+1 for t in range(h)), "first obstructed height")
    for start in (i, j):
        require(any(boundaries[r] <= start and start+n <= boundaries[r+1] for r in range(h+1)), "pure interval occurrence")
    lcp = row["lcp"]
    require(n <= lcp and j+lcp < len(word), "finite split range")
    require(word[i:i+lcp] == word[j:j+lcp] and word[i+lcp] != word[j+lcp], "equal prefix and later split")
    same(row["split_bits"], [word[i+lcp], word[j+lcp]], "split bits")
    length = j+lcp+1
    require(row["prefix_length"] == length, "exact required prefix")
    same(row["prefix_sha256"], hashlib.sha256(word[:length].encode()).hexdigest(), "model prefix digest")
    same(row["covering_odd_steps"], bisect.bisect_left(odd_positions, length), "odd covering scope")
    # The search uses a loose normalized-height envelope. Verification instead
    # reconstructs the actual affine numerator at both repeated starts.
    q, C, P, counts = 0, 0, 1, []
    for t in range(length+1):
        if t in (i, j):
            require(P*(1 << B)+C < 1 << (t+n), "exact affine upper bound at repeat")
            counts.append(q)
        if t < length and word[t] == "1":
            C, P, q = 3*C+(1 << t), 3*P, q+1
    same(row["odd_counts"], counts, "odd counts before starts")
    if B <= 128:
        mod = 1 << length
        r = (-C*pow(P, -1, mod)) % mod or mod
        require(r > 1 << B, "direct canonical finite-prefix exclusion")
    return length


def verify_repeats(data):
    require(type(data) is dict and type(data.get("certificates")) is list, "repeat collection")
    same(data, envelope("repeats", source_bounds_bits=list(BITS),
                        model="Phase13 square-root u, not its finite-prefix extension w",
                        certificates=data["certificates"],
                        finite_conclusion="no 0<S<=2^B realizes the certified finite prefix of u",
                        infinite_conclusion_requires_written_proof="P254/P255, not finite extrapolation"), "repeat envelope")
    require(len(data["certificates"]) == len(BITS), "eight required bounds")
    for B, row in zip(BITS, data["certificates"]):
        require(type(row) is dict and type(row.get("source_bits")) is int and row["source_bits"] == B, "ordered exact source scope")
        verify_repeat(row)


def regressions_expected():
    source_rows = [[family, m, capacity_row(base**m-offset)]
                   for family, base, offset in ((FAMILIES[0], 2, 1), (FAMILIES[1], 8, 5))
                   for m in range(1, 13)]
    ws = {"11101", "1100"}
    for n in range(1, 6):
        for code in range(1 << n):
            ws.add("".join("111" if code & (1 << j) else "110" for j in range(n)))
    ws.update("11101"*r+"1100"*s for r in range(1, 5) for s in range(1, 5))
    words = []
    for w in sorted(ws):
        q, B = positions(w)
        S = residue(w)
        words.append([w, q, B, safe(w), S, literal(S, w)[-1], capacity_row(S)])
    controls = []
    for name, S, w in (
        ("NG28-q26-target", 310028220411, "1101101101110011100111011101010101101101"),
        ("NG28-q26-alternative", 155014110207, "111111111101111110101011110010001001100"),
        ("NG43-safe", 358030447, "1111"+"0110110110110110001101101"),
        ("NG43-unsafe", 179015223, "111"+"0011111111111111010000100"),
        ("source7", 7, "11101001000"),
        ("source167", 167, "11101101111110011110001010")):
        q, B = positions(w)
        st = literal(S, w)
        controls.append([name, S, w, q, B, safe(w), st[-1]])
    require(controls[0][-1] == controls[1][-1] and controls[0][1] == 2*controls[1][1]-3, "old NG28 retained")
    require(controls[2][-1] == controls[3][-1] and controls[2][-2] and not controls[3][-2], "NG43 retained")
    cycles = []
    for S, w in ((1, "10"), (-1, "1"), (-5, "110"), (-17, "11110111000")):
        st = literal(S, w)
        require(st[-1] == S, "cycle control")
        cycles.append([S, w, safe(w), len(set(st)) == len(st), S > 0])
    w = "1101100"
    return envelope("regressions", families=FAMILIES, family_source_count=len(source_rows),
                    family_sources_sha256=digest(source_rows), family_word_count=len(words),
                    family_words_sha256=digest(words), controls=controls, cycles=cycles,
                    NG32={"word": w, "width": 2, "factors": sorted({w[i:i+2] for i in range(len(w)-1)}),
                          "safe": safe(w)},
                    AB={"word": "111011100", "q_B": list(positions("111011100")), "denominator": 512,
                        "fixed_point": [-817, 217]},
                    statuses={name: "OPEN" for name in ("H112", "H72", "H89", "H133")})


BUILDERS = {"capacity": capacity_expected, "carry": carry_expected, "regressions": regressions_expected}


def verify_section(kind, data, expected=None):
    require(kind in KINDS, "unknown section")
    if kind == "repeats":
        verify_repeats(data)
    else:
        same(data, BUILDERS[kind]() if expected is None else expected, kind)


def verify_directory(directory):
    data = {kind: load_certificate((directory/f"phase42_{kind}.json").read_text()) for kind in KINDS}
    for kind in KINDS:
        verify_section(kind, data[kind])
    return {"valid": True, "generator_imported": False,
            "artifact_sha256": {kind: hashlib.sha256((directory/f"phase42_{kind}.json").read_bytes()).hexdigest() for kind in KINDS},
            "positive_odd_sources": 2048,
            "capacity_levels": data["capacity"]["capacity_levels"],
            "finite_capacity_factor_occurrences": data["capacity"]["factor_occurrences"],
            "negative_carry_minimum_q": 22, "q21_rejections": 48, "repeat_certificates": 8,
            "maximum_source_bits": 1024, "maximum_repeat_prefix": max(r["prefix_length"] for r in data["repeats"]["certificates"]),
            "infinite_claims_require_written_proof": True, "proves_collatz": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify_directory(args.artifact_dir)
    except (VerificationError, OSError, ValueError, TypeError, KeyError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}))
        raise SystemExit(1) from exc
    rendered = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(rendered)
    print(rendered, end="")


if __name__ == "__main__":
    main()
