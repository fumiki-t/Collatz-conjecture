#!/usr/bin/env python3
"""Independent Phase 41 reconstruction: positional sums and forward trajectories.

No leading-bit shifted recursion and no search-module import are used here.
The complete finite word image is the decoder-independent acceptance oracle.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path

KINDS = ("decoder", "mixed", "formal", "ancestors", "regressions")
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


class VerificationError(ValueError):
    pass


def require(ok, why):
    if not ok:
        raise VerificationError(why)


def digest(value):
    return hashlib.sha256(json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False).encode()).hexdigest()


def envelope(kind, **values):
    return {"format": f"collatz-phase41-{kind}-v1", "proves_collatz": False, **values}


@lru_cache(maxsize=65536)
def positions(word):
    ones = [i for i, bit in enumerate(word) if bit == "1"]
    require(len(ones)+word.count("0") == len(word), "nonbinary word")
    q = len(ones)
    B = sum(2**i * 3**(q-j-1) for j, i in enumerate(ones))
    D = sum(2**i * 3**sum(p > i for p in ones) for i, bit in enumerate(word) if bit == "0")
    require(D == B+2**len(word)-3**q, "independent position sums disagree")
    return q, B, D


def forward(n, L):
    require(type(n) is int and n > 0, "positive ordinary input")
    states, bits = [n], []
    for _ in range(L):
        bit = n & 1
        bits.append(str(bit))
        n = (3*n+1)//2 if bit else n//2
        states.append(n)
    return "".join(bits), states


def check_path(n, word):
    actual, states = forward(n, len(word))
    require(actual == word, "literal trajectory mismatch")
    q, B, _ = positions(word)
    require(2**len(word)*states[-1] == 3**q*n+B, "endpoint affine mismatch")
    return states


def safe(word):
    return all(3**word[:i].count("1") >= 2**i for i in range(1, len(word)+1))


def residue(word):
    # Lift one source bit by executing its actual parity, not by inverting B.
    r = 0
    for i, bit in enumerate(word):
        n = r
        for _ in range(i):
            n = (3*n+1)//2 if n % 2 else n//2
        if n % 2 != int(bit):
            r += 2**i
    return r or 2**len(word)


@lru_cache(maxsize=32)
def level(L):
    return [(format(i, f"0{L}b") if L else "") for i in range(2**L)]


@lru_cache(maxsize=16)
def tail_map(L):
    vertices = defaultdict(list)
    for w in level(L):
        if w.startswith("0"):
            q, _, D = positions(w)
            vertices[D].append((q, w))
    return {J: sorted(rows) for J, rows in vertices.items()}


def decoder_expected():
    layers, fibers, count, images = [], [], 0, {}
    for L in range(15):
        rows = [[w, *positions(w)] for w in level(L)]
        layers.append({"L": L, "count": len(rows), "sha256": digest(rows)})
        count += len(rows)
        if L <= 7:
            images[L] = {(q, D): w for w, q, _, D in rows}
            require(len(images[L]) == 2**L, "nonunique shifted image")
        if L:
            vertices = tail_map(L)
            records = [[J, vertices[J]] for J in sorted(vertices)]
            holes = [[J, [q for q, _ in f], [w for _, w in f]] for J, f in records
                     if any(b[0] > a[0]+1 for a, b in zip(f, f[1:]))]
            fibers.append({"ell": L, "vertices": len(vertices), "sha256": digest(records), "holes": holes})
    valid, invalid = [], []
    for L in range(8):
        for q in range(-1, L+2):
            for D in range(-1, max(1, 3**max(0, L-1))+2):
                w = images[L].get((q, D))
                (invalid if w is None else valid).append([L, q, D, w])
    return envelope("decoder", maximum_length=14, word_count=count, layers=layers, fibers=fibers,
                    boundary_scope="0<=L<=7,-1<=q<=L+1,-1<=D<=max(1,3^(max(0,L-1)))+1",
                    rejected_count=len(invalid), accepted_count=len(valid), boundary_sha256=digest([valid, invalid]))


def valuation(n, p):
    require(n > 0, "valuation of nonpositive integer")
    v = 0
    while n % p == 0:
        n //= p
        v += 1
    return v


def mixed_expected():
    rows, examples, even, cap, unsafe, zero = [], {}, 0, 0, 0, 0
    for ell in range(1, 9):
        for tail in level(ell):
            if tail[0] != "0":
                continue
            t, _, J = positions(tail)
            for tp, alternate in tail_map(ell)[J]:
                k = tp-t
                if k <= 0:
                    continue
                for R in range(7):
                    word = "1"*R + tail
                    minimum = residue(word)
                    for V in range(3):
                        # Ordinary lifts scanned in order; no generator CRT construction.
                        S = minimum
                        while valuation(S+1, 3) != V:
                            S += 2**len(word)
                        require(valuation(S+1, 2) == R, "initial-run valuation")
                        for h in range(min(R, k)+1):
                            if k-h > V:
                                continue
                            g = 2**h * 3**(k-h)
                            require((S+1) % g == 0, "mixed divisibility")
                            z = (S+1)//g-1
                            if z == 0:
                                zero += 1
                                continue
                            other = "1"*(R-h)+alternate
                            y = check_path(S, word)[-1]
                            require(check_path(z, other)[-1] == y, "mixed endpoint")
                            qa, _, _ = positions(other)
                            require(3**qa*2**len(word) == g*3**(R+t)*2**len(other), "mixed coefficient gain")
                            require(0 < z < S, "ordinary source descent")
                            row = {"source": S, "R": R, "tail": tail, "alternate": alternate, "h": h,
                                   "k": k, "gain": g, "z": z, "endpoint": y,
                                   "target_safe": safe(word), "alternate_safe": safe(other)}
                            rows.append(row)
                            if z % 2 == 0:
                                even += 1
                                examples.setdefault("even_h_equals_R", row)
                                if R > 0:
                                    examples.setdefault("even_positive_run", row)
                            if row["target_safe"]:
                                require(3**(k+1)*2**R < 3**R*(R+t), "gain cap")
                                cap += 1
                                unsafe += int(not row["alternate_safe"])
                            if h < k:
                                examples.setdefault("ternary_factor", row)
    return envelope("mixed", maximum_tail_length=8, maximum_run=6, maximum_v3=2,
                    row_count=len(rows), rows_sha256=digest(rows), even_rows=even,
                    safe_gain_cap_rows=cap, unsafe_from_safe_rows=unsafe,
                    excluded_zero_sources=zero, examples=examples)


def formal_expected():
    bits, exponent_rows, A, f, floor_root, E = [], [], 0, 0, 0, 0
    checkpoints = []
    for j in range(512):
        old_f = f
        while 2**(f+1) <= 3**(j+1):
            f += 1
        while (floor_root+1)**2 <= j+1:
            floor_root += 1
        change = int(f-old_f == 2 and A < floor_root)
        A += change
        e = f-old_f-change
        E += e
        require(e in (1, 2) and floor_root-1 <= A <= floor_root and E == f-A, "formal recurrence")
        bits.extend("1" + "0"*(e-1))
        exponent_rows.append([j+1, f, A, e])
        if j+1 in (1, 2, 4, 8, 16, 32, 64, 128, 256, 512):
            word = "110111111"+"".join(bits)
            r = residue(word)
            check_path(r, word)
            checkpoints.append({"odd_steps_u": j+1, "L": len(word), "source": r})
    u = "".join(bits)
    q, _, D = positions(u)
    C = Fraction(D, 3**q)
    require(C <= 8, "zero correction sum")
    word, tail = "110111111"+u, "0111111"+u
    require(safe(word), "full formal safety")
    ratios = []
    for L in range(1, len(tail)+1):
        t, _, J = positions(tail[:L])
        require(729*J <= 1753*3**t and 1753 < 3*729, "uniform tail correction bound")
        ratios.append([L, t, J])
    for a, b in zip(checkpoints, checkpoints[1:]):
        require((b["source"]-a["source"]) % 2**a["L"] == 0, "nested source cylinders")
    return envelope("formal", odd_steps=512, word=word, word_sha256=hashlib.sha256(word.encode()).hexdigest(),
                    exponent_sha256=digest(exponent_rows), tail_prefix_sha256=digest(ratios),
                    correction=[C.numerator, C.denominator], bound=[1753, 729],
                    final_tail=ratios[-1], checkpoints=checkpoints,
                    positive_ordinary_source="OPEN", all_Q_maximality="OPEN", H112="OPEN")


def forward_hits(y, target_L, target_q, maximum_length):
    hits = []
    for z in range(1, (y*2**target_L-1)//3**target_q+1):
        word, states = forward(z, maximum_length)
        for L, endpoint in enumerate(states):
            q = word[:L].count("1")
            if endpoint == y and 3**q*2**target_L > 3**target_q*2**L:
                hits.append([z, L, q, word[:L]])
    return hits


def ancestors_expected():
    targets = [[y, 0, 0] for y in range(1, 64)]
    for S in range(1, 32):
        for L in (3, 6):
            word, states = forward(S, L)
            targets.append([states[-1], L, word.count("1")])
    rows, count = [], 0
    for y, L, q in targets:
        hits = forward_hits(y, L, q, 10)
        count += len(hits)
        rows.append({"target": [y, L, q], "source_upper_bound": (y*2**L-1)//3**q,
                     "hit_count": len(hits), "hits_sha256": digest(hits)})
    return envelope("ancestors", maximum_length=10, target_count=len(rows), hit_count=count,
                    rows=rows, all_Q_geodesic_certificate=False)


def record(S, w):
    q, B, D = positions(w)
    return {"source": S, "word": w, "L": len(w), "q": q, "B": B, "D": D,
            "endpoint": check_path(S, w)[-1], "safe": safe(w)}


def regressions_expected():
    specs = [("longer_cross_Q", 31, 0, 27, 3), ("NG25_lower_Q", 287, 9, 273, 1),
             ("NG25_higher_Q", 59, 6, 39, 7), ("NG26", 1874247, 23, 937121, 22),
             ("NG28", 310028220411, 40, 155014110207, 39),
             ("NG43_original", 358030447, 29, 179015223, 28),
             ("NG43_lex_first", 328539247, 29, 164269623, 28),
             ("mixed_3_unsafe_target", 83, 4, 27, 4), ("NG24", 15, 6, 7, 5)]
    pairs = []
    for name, S, L, z, La in specs:
        d, _ = forward(S, L)
        a, states = forward(z, La)
        target, other = record(S, d), record(z, a)
        require(target["endpoint"] == other["endpoint"], "regression coalescence")
        require(3**other["q"]*2**L > 3**target["q"]*2**La, "regression dominance")
        v = min(range(La+1), key=lambda i: Fraction(3**a[:i].count("1"), 2**i))
        pairs.append({"name": name, "target": target, "competitor": other,
                      "valley_time": v, "valley_source": states[v]})
    controls = []
    for name, starts in (("2^m-1", [2**m-1 for m in range(2, 11)]),
                         ("8^m-5", [8**m-5 for m in range(1, 7)])):
        for S in starts:
            w, _ = forward(S, 24)
            controls.append({"family": name, **record(S, w)})
    symbolic = [("(110|111)^*", "".join("111" if bit == "1" else "110" for bit in w))
                for r in range(1, 5) for w in level(r)]
    symbolic += [("A=11101", "11101"), ("B=1100", "1100")]
    symbolic += [("A^rB^s", "11101"*r+"1100"*s) for r in range(1, 5) for s in range(1, 5)]
    for name, w in symbolic:
        controls.append({"family": name, **record(residue(w), w)})
    rows167 = []
    for L in range(1, 31):
        w, states = forward(167, L)
        rows167.append([L, w.count("1"), residue(w), states[-1], safe(w)])
    clocks = []
    for S in (1, 3, 7):
        w, states = forward(S, 100)
        L = states.index(1)
        w = w[:L]
        clocks.append({"source": S, "word_to_one": w, "chi": L-2*w.count("1")})
    return envelope("regressions", families=FAMILIES, pairs=pairs, controls=controls,
                    source167=rows167, source7_clocks=clocks,
                    preserved=["NG22", "NG24", "NG25", "NG26", "NG28", "NG43"],
                    statuses={"H112": "OPEN", "H72": "OPEN", "H89": "OPEN", "H133": "OPEN"})


BUILDERS = dict(zip(KINDS, (decoder_expected, mixed_expected, formal_expected, ancestors_expected, regressions_expected)))


def verify_section(kind, data, expected=None):
    require(kind in BUILDERS, "unknown artifact kind")
    require(type(data) is dict and data.get("proves_collatz") is False, "proof flag or artifact type")
    reconstructed = BUILDERS[kind]() if expected is None else expected
    # Canonical byte equality also rejects bool/int swaps, NaN, omissions, extras.
    require(digest(data) == digest(reconstructed), f"{kind}: independent reconstruction mismatch")


def verify(artifact_dir):
    output = {}
    for kind in KINDS:
        path = artifact_dir / f"phase41_{kind}.json"
        data = load_certificate(path.read_text(encoding="utf-8"))
        verify_section(kind, data)
        output[kind] = hashlib.sha256(path.read_bytes()).hexdigest()
    return {"valid": True, "generator_imported": False, "word_count": 32767,
            "mixed_rows": 4192, "even_rows": 658, "formal_odd_steps": 512,
            "ancestor_targets": 125, "artifact_sha256": output, "proves_collatz": False}


def load_certificate(text):
    def unique_fields(pairs):
        result = {}
        for key, value in pairs:
            require(key not in result, "duplicate JSON field")
            result[key] = value
        return result

    def reject_constant(value):
        raise VerificationError(f"nonfinite JSON constant: {value}")

    return json.loads(text, object_pairs_hook=unique_fields, parse_constant=reject_constant)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, required=True)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}))
        raise SystemExit(1) from exc
    text = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if args.output:
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")


if __name__ == "__main__":
    main()
