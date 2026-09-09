#!/usr/bin/env python3
"""Mechanical-capacity and signed-carry search; no infinite-orbit oracle."""
from __future__ import annotations

import argparse
import bisect
import hashlib
import itertools
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path

KINDS = ("capacity", "carry", "repeats", "regressions")
BITS = (8, 16, 32, 64, 128, 256, 512, 1024)
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def envelope(kind, **fields):
    return {"format": f"collatz-phase42-{kind}-v1", "proves_collatz": False, **fields}


def affine(word):
    if set(word) - {"0", "1"}:
        raise ValueError("nonbinary word")
    q = B = 0
    for i, bit in enumerate(word):
        if bit == "1":
            q, B = q+1, 3*B+(1 << i)
    return q, B


def safe(word):
    power = 1
    for L, bit in enumerate(word, 1):
        if bit == "1":
            power *= 3
        if bit not in "01" or power <= 1 << L:
            return False
    return True


def trace(S, word):
    states = [S]
    for bit in word:
        if states[-1] % 2 != int(bit):
            raise ValueError("nonliteral parity")
        n = states[-1]
        states.append((3*n+1)//2 if n % 2 else n//2)
    return states


def source(word):
    q, B = affine(word)
    return (-B*pow(3**q, -1, 1 << len(word))) % (1 << len(word)) or 1 << len(word)


def safe_prefix(S, limit=300):
    """Accelerated construction; stop before a repeated state or unsafe block."""
    if type(S) is not int or S <= 0 or S % 2 == 0 or limit < 0:
        raise ValueError("odd positive source and nonnegative limit required")
    x, P, E, exponents, states = S, 1, 0, [], [S]
    seen = {S}
    for _ in range(limit):
        value = 3*x+1
        e = (value & -value).bit_length()-1
        segment = [value >> t for t in range(1, e+1)]
        if 3*P <= 1 << (E+e) or len(set(segment)) < len(segment) or seen.intersection(segment):
            break
        exponents.append(e)
        states.extend(segment)
        seen.update(segment)
        x, P, E = segment[-1], 3*P, E+e
    return exponents, states


def capacity_row(S, limit=300):
    exponents, states = safe_prefix(S, limit)
    q = len(exponents)
    f = [(3**j).bit_length()-1 for j in range(q+1)]
    E = [0]
    for e in exponents:
        E.append(E[-1]+e)
    a = [fj-Ej for fj, Ej in zip(f, E)]
    assert min(a) >= 0 and len(states) == len(set(states))
    Y = Fraction((1 << E[-1])*states[-1], 3**q)
    K = 2
    while (1 << K)*Y.denominator < 3*Y.numerator:
        K += 1
    word = "".join("1"+"0"*(e-1) for e in exponents)
    blocks, start = [], 0
    for j in range(q):
        change = a[j+1]-a[j]
        if change:
            blocks.append([a[start], f[j+1]-f[start]-int(change > 0), E[start], f[start]])
            start = j+1
    blocks.append([a[start], f[q]-f[start], E[start], f[start]])
    H, D = max(a), sum(max(x-y, 0) for x, y in zip(a, a[1:]))
    assert sum(ell for _, ell, _, _ in blocks)+D == E[-1]
    J0 = H+2*D+1
    height_sum = sum(r for r, _, _, _ in blocks)
    assert len(blocks) <= J0 and height_sum <= H*(H+1)//2+2*H*D
    factors_checked = 0
    for h in range(2*H+K+1):
        n = h+K
        factors = [word[t:t+n] for r, ell, s, _ in blocks if r <= h
                   for t in range(s, s+ell-n+1)]
        assert len(factors) <= n+1 and len(set(factors)) == len(factors)
        factors_checked += len(factors)
    deltas = [max(ell-r-K+1, 0) for r, ell, _, _ in blocks]
    energy = sum(d*(d+1) for d in deltas)
    M = (2*H+K+1)*(2*H+3*K+2)
    assert energy <= M
    base = H*(H+1)//2+2*H*D+(K-1)*J0+D
    residual = E[-1]-base
    assert residual <= 0 or residual*residual <= J0*M
    return {"source": S, "q": q, "E": E[-1], "word_sha256": hashlib.sha256(word.encode()).hexdigest(),
            "Y": [Y.numerator, Y.denominator], "K": K, "H": H, "D": D,
            "blocks": blocks, "height_sum": height_sum, "energy": energy, "M": M,
            "variation_base": base, "variation_residual": residual,
            "capacity_levels": 2*H+K+1, "factor_occurrences": factors_checked}


def capacity_audit():
    rows = [capacity_row(S) for S in range(1, 4096, 2)]
    return envelope("capacity", maximum_source=4095, maximum_odd_steps=300,
                    positive_odd_sources=len(rows), odd_steps=sum(r["q"] for r in rows),
                    pure_blocks=sum(len(r["blocks"]) for r in rows),
                    capacity_levels=sum(r["capacity_levels"] for r in rows),
                    factor_occurrences=sum(r["factor_occurrences"] for r in rows),
                    rows_sha256=digest(rows), samples=[r for r in rows if r["source"] in (1, 3, 7, 27, 167, 4095)],
                    hypotheses=["positive odd source", "complete coefficient-safe odd prefix", "distinct full states"],
                    all_finite_checks=True)


def decode_B(L, q, B):
    """Leading-parity correction decoder; verifier instead realizes the forced source."""
    word = []
    for left in range(L, 0, -1):
        if B < 0 or not 0 <= q <= left:
            return None
        if B % 2:
            if q == 0 or B < 3**(q-1):
                return None
            word.append("1")
            B, q = (B-3**(q-1))//2, q-1
        else:
            word.append("0")
            B //= 2
    return "".join(word) if B == q == 0 else None


def Bmax(q):
    # Move each odd position as far right as full coefficient safety permits.
    B = 0
    for j in range(q):
        B = 3*B+(1 << ((3**j).bit_length()-1))
    return B


def carry_audit():
    small = [[q, Bmax(q), 5*3**q-4*2**q] for q in range(2, 21)]
    assert all(M < lower for _, M, lower in small)
    q, P = 21, 3**21
    f = [(3**j).bit_length()-1 for j in range(q)]
    allowance = Bmax(q)-5*P+4*2**q
    assert 0 <= 6*allowance < P and Bmax(q) < 9*P-8*2**q
    patterns = [(None, f)]
    for j in range(1, q):
        if f[j]-f[j-1] == 2:
            moved = f.copy()
            moved[j] -= 1
            patterns.append((j, moved))
    rows = []
    for moved, positions in patterns:
        for L in range(positions[-1]+1, P.bit_length()):
            w = "".join("1" if i in positions else "0" for i in range(L))
            assert safe(w)
            _, B = affine(w)
            for k, m in ((1, -3), (2, -1)):
                assert (B+m*P) % 2**k == 0
                Ba = (B+m*P)//2**k
                assert decode_B(L-k, q, Ba) is None
                rows.append([moved, L, k, m, Ba, False])
    d, a = "1101101101101011010110110110110101", "111111111111011101101011000100100"
    Sd, Sa, y = 29023002619, 14511501311, 53013941237
    qd, Bd = affine(d)
    qa, Ba = affine(a)
    assert safe(d) and safe(a) and qd == qa == 22
    assert trace(Sd, d)[-1] == trace(Sa, a)[-1] == y and Sd == 2*Sa-3
    assert 2*Ba-Bd == -3*3**22
    ps = [i for i, bit in enumerate(d) if bit == "1"]+[len(d)]
    return envelope("carry", minimum_odd_count=22, q_2_through_20=small,
                    q21_allowance=[allowance, P], q21_patterns=len(patterns),
                    q21_checks=rows, q21_other_k_m_lower=9*P-8*2**q,
                    witness={"target": d, "alternative": a, "target_source": Sd, "alternative_source": Sa,
                             "endpoint": y, "target_L_Q_B": [len(d), qd, Bd],
                             "alternative_L_Q_B": [len(a), qa, Ba], "carry": -3, "coefficient_gain": 2,
                             "target_exponents": [b-a for a, b in zip(ps, ps[1:])]},
                    scope="two positive literal coefficient-safe words, same q, shorter alternative, negative carry")


def square_word(steps):
    power, f, A, E = 1, 0, 0, 0
    parts, positions, boundaries = [], [0], [0]
    for j in range(steps):
        power *= 3
        fj = power.bit_length()-1
        inc = int(fj-f == 2 and A < isqrt(j+1))
        e = fj-f-inc
        assert e in (1, 2)
        parts.append("1"+"0"*(e-1))
        A, E, f = A+inc, E+e, fj
        assert isqrt(j+1)-1 <= A <= isqrt(j+1) and E == f-A
        positions.append(E)
        if inc:
            boundaries.append(E)
    return "".join(parts), positions, boundaries


def repeat_certificate(B):
    upper = (1 << B)+4
    K, steps = (3*upper-1).bit_length(), (B//2+60)**2
    word, positions, boundaries = square_word(steps)
    lengths = [b-a for a, b in zip(boundaries, boundaries[1:])]
    for h in range(len(lengths)):
        n = h+K
        clean = sum(max(ell-n+1, 0) for ell in lengths[:h+1])
        if clean > n+1:
            break
    else:
        raise ValueError("no capacity obstruction within explicit construction cap")
    seen, pair = {}, None
    for r in range(h+1):
        for j in range(boundaries[r], boundaries[r+1]-n+1):
            key = word[j:j+n]
            if key not in seen:
                seen[key] = j
                continue
            i, lcp = seen[key], n
            while j+lcp < len(word) and word[i+lcp] == word[j+lcp]:
                lcp += 1
            if j+lcp < len(word):
                pair = i, j, lcp
                break
        if pair is not None:
            break
    if pair is None:
        raise ValueError("repeat does not have a certified later split")
    i, j, lcp = pair
    qi, qj = bisect.bisect_left(positions, i), bisect.bisect_left(positions, j)
    assert 3**qi*upper < 1 << (i+n) and 3**qj*upper < 1 << (j+n)
    length = j+lcp+1
    return {"source_bits": B, "K": K, "h": h, "width": n, "clean_occurrences": clean,
            "capacity": n+1, "first_start": i, "second_start": j, "lcp": lcp,
            "split_bits": [word[i+lcp], word[j+lcp]], "odd_counts": [qi, qj],
            "prefix_length": length, "generated_odd_steps": steps,
            "covering_odd_steps": bisect.bisect_left(positions, length),
            "prefix_sha256": hashlib.sha256(word[:length].encode()).hexdigest()}


def repeats_audit():
    return envelope("repeats", source_bounds_bits=list(BITS),
                    model="Phase13 square-root u, not its finite-prefix extension w",
                    certificates=[repeat_certificate(B) for B in BITS],
                    finite_conclusion="no 0<S<=2^B realizes the certified finite prefix of u",
                    infinite_conclusion_requires_written_proof="P254/P255, not finite extrapolation")


def regressions_audit():
    source_rows = [[family, m, capacity_row(base**m-offset)]
                   for family, base, offset in ((FAMILIES[0], 2, 1), (FAMILIES[1], 8, 5))
                   for m in range(1, 13)]
    word_set = {"11101", "1100"}
    word_set.update("".join(bits) for n in range(1, 6) for bits in itertools.product(("110", "111"), repeat=n))
    word_set.update("11101"*r+"1100"*s for r in range(1, 5) for s in range(1, 5))
    words = []
    for w in sorted(word_set):
        q, B = affine(w)
        S = source(w)
        words.append([w, q, B, safe(w), S, trace(S, w)[-1], capacity_row(S)])
    controls = []
    for name, S, w in (
        ("NG28-q26-target", 310028220411, "1101101101110011100111011101010101101101"),
        ("NG28-q26-alternative", 155014110207, "111111111101111110101011110010001001100"),
        ("NG43-safe", 358030447, "1111"+"0110110110110110001101101"),
        ("NG43-unsafe", 179015223, "111"+"0011111111111111010000100"),
        ("source7", 7, "11101001000"),
        ("source167", 167, "11101101111110011110001010")):
        q, B = affine(w)
        st = trace(S, w)
        controls.append([name, S, w, q, B, safe(w), st[-1]])
    cycles = []
    for S, w in ((1, "10"), (-1, "1"), (-5, "110"), (-17, "11110111000")):
        st = trace(S, w)
        assert st[-1] == S
        cycles.append([S, w, safe(w), len(set(st)) == len(st), S > 0])
    w = "1101100"
    return envelope("regressions", families=FAMILIES, family_source_count=len(source_rows),
                    family_sources_sha256=digest(source_rows), family_word_count=len(words),
                    family_words_sha256=digest(words), controls=controls, cycles=cycles,
                    NG32={"word": w, "width": 2, "factors": sorted({w[i:i+2] for i in range(len(w)-1)}),
                          "safe": safe(w)},
                    AB={"word": "111011100", "q_B": list(affine("111011100")), "denominator": 512,
                        "fixed_point": [-817, 217]},
                    statuses={name: "OPEN" for name in ("H112", "H72", "H89", "H133")})


BUILDERS = dict(zip(KINDS, (capacity_audit, carry_audit, repeats_audit, regressions_audit)))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    for kind, build in BUILDERS.items():
        data = build()
        (args.artifact_dir/f"phase42_{kind}.json").write_text(json.dumps(data, indent=2, sort_keys=True)+"\n")
        print(f"generated phase42_{kind}.json", flush=True)


if __name__ == "__main__":
    main()
