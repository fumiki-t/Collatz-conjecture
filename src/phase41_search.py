#!/usr/bin/env python3
"""Exact shifted decoding and bounded all-Q ancestor search (not a stopping oracle)."""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from fractions import Fraction
from math import isqrt
from pathlib import Path

FILES = ("decoder", "mixed", "formal", "ancestors", "regressions")
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


def digest(rows):
    return hashlib.sha256(json.dumps(rows, sort_keys=True, separators=(",", ":")).encode()).hexdigest()


def envelope(kind, **fields):
    return {"format": f"collatz-phase41-{kind}-v1", "proves_collatz": False, **fields}


def affine(word):
    if set(word) - {"0", "1"}:
        raise ValueError("nonbinary word")
    q = B = 0
    for i, bit in enumerate(word):
        if bit == "1":
            B = 3 * B + (1 << i)
            q += 1
    return q, B, B + (1 << len(word)) - 3**q


def decode(L, q, D):
    """Complete leading-parity decoder; O(L) integer operations, not bits."""
    if any(type(x) is not int for x in (L, q, D)) or L < 0 or not 0 <= q <= L or D < 0:
        return None
    word, power = [], 3**q
    for remaining in range(L, 0, -1):
        if not 0 <= q <= remaining or D < 0:
            return None
        if D % 2:
            if D < power:
                return None
            word.append("0")
            D = (D - power) // 2
        else:
            if q == 0:
                return None
            word.append("1")
            D //= 2
            q -= 1
            power //= 3
    return "".join(word) if q == D == 0 else None


def trace(source, word):
    if type(source) is not int or source <= 0:
        raise ValueError("positive ordinary source required")
    states = [source]
    for bit in word:
        if bit not in "01" or states[-1] % 2 != int(bit):
            raise ValueError("nonliteral parity")
        n = states[-1]
        states.append((3*n+1)//2 if n % 2 else n//2)
    return states


def safe(word):
    q = 0
    for L, bit in enumerate(word, 1):
        q += int(bit)
        if 3**q < 2**L:
            return False
    return True


def source(word):
    q, B, _ = affine(word)
    modulus = 1 << len(word)
    return (-B * pow(3**q, -1, modulus)) % modulus or modulus


def words(L, zero=False):
    for bits in itertools.product("01", repeat=L-int(zero)):
        yield ("0" if zero else "") + "".join(bits)


def fiber(ell, J):
    # Every zero-prefixed tail of weight t has J >= 3^t.
    out, t, power = [], 0, 1
    while t < ell and power <= J:
        word = decode(ell, t, J)
        if word is not None and word.startswith("0"):
            out.append((t, word))
        t, power = t+1, 3*power
    return out


def decoder_audit():
    layers, fibers, count = [], [], 0
    for L in range(15):
        rows = []
        for word in words(L):
            q, B, D = affine(word)
            assert decode(L, q, D) == word
            rows.append([word, q, B, D])
        layers.append({"L": L, "count": len(rows), "sha256": digest(rows)})
        count += len(rows)
        if L:
            vertices = sorted({affine(w)[2] for w in words(L, True)})
            records = [[J, fiber(L, J)] for J in vertices]
            gaps = [[J, [q for q, _ in f], [w for _, w in f]] for J, f in records
                    if any(b[0]-a[0] > 1 for a, b in zip(f, f[1:]))]
            fibers.append({"ell": L, "vertices": len(vertices), "sha256": digest(records), "holes": gaps})
    invalid, valid = [], []
    for L in range(8):
        for q in range(-1, L+2):
            for D in range(-1, max(1, 3**max(0, L-1))+2):
                w = decode(L, q, D)
                (invalid if w is None else valid).append([L, q, D, w])
    return envelope("decoder", maximum_length=14, word_count=count, layers=layers,
                    fibers=fibers, boundary_scope="0<=L<=7,-1<=q<=L+1,-1<=D<=max(1,3^(max(0,L-1)))+1",
                    rejected_count=len(invalid), accepted_count=len(valid),
                    boundary_sha256=digest([valid, invalid]))


def mixed_rewrite(S, R, tail, alternate, h):
    if any(type(x) is not int for x in (S, R, h)) or R < 0:
        raise ValueError("invalid run or source")
    if len(tail) != len(alternate) or not tail.startswith("0") or not alternate.startswith("0"):
        raise ValueError("zero-prefixed equal-length tails required")
    t, _, J = affine(tail)
    tp, _, Jp = affine(alternate)
    k = tp-t
    if J != Jp or k <= 0 or not 0 <= h <= min(R, k):
        raise ValueError("invalid mixed vertex or run budget")
    target = "1"*R + tail
    endpoint = trace(S, target)[-1]
    g = 2**h * 3**(k-h)
    if (S+1) % g:
        raise ValueError("nonintegral mixed source")
    z = (S+1)//g - 1
    other = "1"*(R-h) + alternate
    if z <= 0 or trace(z, other)[-1] != endpoint:
        raise ValueError("nonpositive source or failed literal coalescence")
    return {"source": S, "R": R, "tail": tail, "alternate": alternate, "h": h,
            "k": k, "gain": g, "z": z, "endpoint": endpoint,
            "target_safe": safe(target), "alternate_safe": safe(other)}


def mixed_audit():
    rows, cap_rows, even, unsafe, zero = [], 0, 0, 0, 0
    examples = {}
    for ell in range(1, 9):
        for tail in words(ell, True):
            t, _, J = affine(tail)
            for tp, alternate in fiber(ell, J):
                k = tp-t
                if k <= 0:
                    continue
                for R in range(7):
                    word = "1"*R + tail
                    base = source(word) % (1 << (R+ell))
                    a0 = (base+1) >> R
                    for V in range(3):
                        b = a0 * pow(3**V, -1, 1 << ell) % (1 << ell)
                        while b % 3 == 0 or 2**R * 3**V * b <= 1:
                            b += 1 << ell
                        S = 2**R * 3**V * b - 1
                        for h in range(min(R, k)+1):
                            if k-h > V:
                                continue
                            if (S+1)//(2**h * 3**(k-h)) == 1:
                                zero += 1
                                continue
                            row = mixed_rewrite(S, R, tail, alternate, h)
                            rows.append(row)
                            if row["z"] % 2 == 0:
                                even += 1
                                examples.setdefault("even_h_equals_R", row)
                                if R > 0:
                                    examples.setdefault("even_positive_run", row)
                            if row["target_safe"]:
                                assert 3**(k+1) * 2**R < 3**R * (R+t)
                                cap_rows += 1
                                if not row["alternate_safe"]:
                                    unsafe += 1
                            if h < k:
                                examples.setdefault("ternary_factor", row)
    return envelope("mixed", maximum_tail_length=8, maximum_run=6, maximum_v3=2,
                    row_count=len(rows), rows_sha256=digest(rows), even_rows=even,
                    safe_gain_cap_rows=cap_rows, unsafe_from_safe_rows=unsafe,
                    excluded_zero_sources=zero, examples=examples)


def formal_audit(steps=512):
    A, f, power, u = 0, 0, 1, ""
    checkpoints, exponent_rows = [], []
    for j in range(steps):
        power *= 3
        nf = power.bit_length()-1
        b = nf-f
        na = A + int(b == 2 and A < isqrt(j+1))
        e = b - (na-A)
        u += "1" + "0"*(e-1)
        A, f = na, nf
        assert isqrt(j+1)-1 <= A <= isqrt(j+1)
        exponent_rows.append([j+1, f, A, e])
        if j+1 in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
            w = "110111111" + u
            checkpoints.append({"odd_steps_u": j+1, "L": len(w), "source": source(w)})
    C = Fraction(0)
    q = 0
    for i, bit in enumerate(u):
        if bit == "0":
            C += Fraction(2**i, 3**q)
        q += int(bit)
    w, tail = "110111111" + u, "0111111" + u
    assert safe(w) and C <= 8
    ratios, J, t = [], 0, 0
    for i, bit in enumerate(tail):
        if bit == "0":
            J += 2**i
        else:
            J *= 3
            t += 1
        ratio = Fraction(J, 3**t)
        assert ratio <= Fraction(1753, 729) < 3
        ratios.append([i+1, t, J])
    return envelope("formal", odd_steps=steps, word=w, word_sha256=hashlib.sha256(w.encode()).hexdigest(),
                    exponent_sha256=digest(exponent_rows), tail_prefix_sha256=digest(ratios),
                    correction=[C.numerator, C.denominator], bound=[1753, 729],
                    final_tail=[len(tail), t, J], checkpoints=checkpoints,
                    positive_ordinary_source="OPEN", all_Q_maximality="OPEN", H112="OPEN")


def candidate(z, L, q, endpoint):
    if type(z) is not int or type(endpoint) is not int or z <= 0 or endpoint <= 0:
        return None
    if type(L) is not int or type(q) is not int or L < 0 or not 0 <= q <= L:
        return None
    D = 2**L*(endpoint+1)-3**q*(z+1)
    w = decode(L, q, D)
    if w is None:
        return None
    return w if trace(z, w)[-1] == endpoint else None


def ancestor_hits(y, target_L, target_q, maximum_length):
    """Complete only for the explicit length cap, not a full geodesic certificate."""
    if any(type(v) is not int for v in (y, target_L, target_q, maximum_length)) or y <= 0 or target_L < 0 or not 0 <= target_q <= target_L or maximum_length < 0:
        raise ValueError("invalid target or explicit search cap")
    bound = (y*2**target_L-1)//3**target_q
    hits = []
    for z in range(1, bound+1):
        for L in range(maximum_length+1):
            for q in range(L+1):
                if 3**q * 2**target_L <= 3**target_q * 2**L:
                    continue
                w = candidate(z, L, q, y)
                if w is not None:
                    hits.append([z, L, q, w])
    return hits


def actual_prefix(S, L):
    n, w = S, ""
    for _ in range(L):
        bit = n % 2
        w += str(bit)
        n = (3*n+1)//2 if bit else n//2
    return w, n


def ancestors_audit():
    targets = [[y, 0, 0] for y in range(1, 64)]
    for S in range(1, 32):
        for L in (3, 6):
            w, y = actual_prefix(S, L)
            targets.append([y, L, w.count("1")])
    rows, count = [], 0
    for y, L, q in targets:
        hits = ancestor_hits(y, L, q, 10)
        count += len(hits)
        rows.append({"target": [y, L, q], "source_upper_bound": (y*2**L-1)//3**q,
                     "hit_count": len(hits), "hits_sha256": digest(hits)})
    return envelope("ancestors", maximum_length=10, target_count=len(rows), hit_count=count,
                    rows=rows, all_Q_geodesic_certificate=False)


def path_record(S, word):
    q, B, D = affine(word)
    states = trace(S, word)
    return {"source": S, "word": word, "L": len(word), "q": q, "B": B, "D": D,
            "endpoint": states[-1], "safe": safe(word)}


def regressions_audit():
    pairs = [
        ("longer_cross_Q", 31, "", 27, "110"),
        ("NG25_lower_Q", 287, "111110100", 273, "1"),
        ("NG25_higher_Q", 59, "110110", 39, "1110110"),
        ("NG26", 1874247, "11101011111111101000001", 937121, "1010110111111101011100"),
        ("NG28", 310028220411, "1101101101110011100111011101010101101101", 155014110207, "111111111101111110101011110010001001100"),
        ("NG43_original", 358030447, "1111"+"0110110110110110001101101", 179015223, "111"+"0011111111111111010000100"),
        ("NG43_lex_first", 328539247, "1111"+"0110110110110010110101101", 164269623, "111"+"0011111111111011100001100"),
        ("mixed_3_unsafe_target", 83, "1100", 27, "1101"),
        ("NG24", 15, "111100", 7, "11101")]
    pair_rows = []
    for name, S, d, z, a in pairs:
        target, other = path_record(S, d), path_record(z, a)
        assert target["endpoint"] == other["endpoint"]
        assert 3**other["q"]*2**target["L"] > 3**target["q"]*2**other["L"]
        assert candidate(z, len(a), other["q"], target["endpoint"]) == a
        valley = min(range(len(a)+1), key=lambda i: Fraction(3**a[:i].count("1"), 2**i))
        pair_rows.append({"name": name, "target": target, "competitor": other,
                          "valley_time": valley, "valley_source": trace(z, a)[valley]})
    controls = []
    for name, starts in (("2^m-1", [2**m-1 for m in range(2, 11)]),
                         ("8^m-5", [8**m-5 for m in range(1, 7)])):
        for S in starts:
            w, _ = actual_prefix(S, 24)
            controls.append({"family": name, **path_record(S, w)})
    symbolic = [("(110|111)^*", "".join(p)) for r in range(1, 5)
                for p in itertools.product(("110", "111"), repeat=r)]
    symbolic += [("A=11101", "11101"), ("B=1100", "1100")]
    symbolic += [("A^rB^s", "11101"*r+"1100"*s) for r in range(1, 5) for s in range(1, 5)]
    for name, w in symbolic:
        controls.append({"family": name, **path_record(source(w), w)})
    source167 = []
    for L in range(1, 31):
        w, y = actual_prefix(167, L)
        source167.append([L, w.count("1"), source(w), y, safe(w)])
    clocks = []
    for S in (1, 3, 7):
        n, w = S, ""
        while n != 1:
            b = n % 2
            w += str(b)
            n = (3*n+1)//2 if b else n//2
        clocks.append({"source": S, "word_to_one": w, "chi": len(w)-2*w.count("1")})
    return envelope("regressions", families=FAMILIES, pairs=pair_rows, controls=controls,
                    source167=source167, source7_clocks=clocks,
                    preserved=["NG22", "NG24", "NG25", "NG26", "NG28", "NG43"],
                    statuses={"H112": "OPEN", "H72": "OPEN", "H89": "OPEN", "H133": "OPEN"})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path)
    parser.add_argument("--endpoint", type=int)
    parser.add_argument("--target-word", default="")
    parser.add_argument("--maximum-length", type=int,
                        help="Explicit competitor-length cap; never an all-Q stopping certificate")
    args = parser.parse_args()
    if args.endpoint is not None:
        if args.artifact_dir is not None or args.maximum_length is None:
            parser.error("a query requires --maximum-length and no --artifact-dir")
        q, B, _ = affine(args.target_word)
        numerator = 2**len(args.target_word)*args.endpoint-B
        if numerator <= 0 or numerator % 3**q:
            parser.error("target word has no positive ordinary source at that endpoint")
        trace(numerator//3**q, args.target_word)
        hits = ancestor_hits(args.endpoint, len(args.target_word), q, args.maximum_length)
        print(json.dumps({"endpoint": args.endpoint, "target_word": args.target_word,
                          "maximum_length": args.maximum_length,
                          "hits": hits, "all_Q_geodesic_certificate": False,
                          "proves_collatz": False}, sort_keys=True))
        return
    if args.artifact_dir is None or args.maximum_length is not None or args.target_word:
        parser.error("supply --artifact-dir for the fixed audit or --endpoint for a bounded query")
    args.artifact_dir.mkdir(parents=True, exist_ok=True)
    for kind, generate in zip(FILES, (decoder_audit, mixed_audit, formal_audit, ancestors_audit, regressions_audit)):
        data = generate()
        path = args.artifact_dir / f"phase41_{kind}.json"
        path.write_text(json.dumps(data, sort_keys=True, indent=2)+"\n", encoding="utf-8")
        print(json.dumps({"artifact": path.name, "sha256": hashlib.sha256(path.read_bytes()).hexdigest()}), flush=True)


if __name__ == "__main__":
    main()
