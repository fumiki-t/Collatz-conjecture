"""Normalization-barrier proof search; Phase 41's bounded oracle is unchanged.

Finite rational certificates cover all positive starts and all finite lengths.
Work/candidate caps yield UNKNOWN. Universal termination is not established.
"""
from __future__ import annotations

import argparse
from collections import Counter
from fractions import Fraction
import hashlib
from itertools import product
import json
from math import comb, isqrt
from pathlib import Path

SCHEMA = "collatz-phase43-normalization-barrier-v1"
ROOT = Path(__file__).resolve().parents[1]
INHERITED = ("artifacts/phase33_descent_certificate.csv",
             "artifacts/phase33_descent_summary.json", "artifacts/phase33_verifier.json",
             "artifacts/phase38_capacity_certificate.json", "artifacts/phase38_verifier.json")


def integer(x, minimum=0):
    if type(x) is not int or x < minimum:
        raise ValueError("integer outside domain")
    return x


def step(x):
    return (3*x+1)//2 if x & 1 else x//2


def target_data(source, length):
    integer(source, 1)
    integer(length)
    x, p = source, 1
    for _ in range(length):
        if x & 1:
            p *= 3
        x = step(x)
    c = Fraction(p, 1 << length)
    H = Fraction(x)/c
    return x, c, H, (H.numerator-1)//H.denominator


def potential(vertices, endpoint):
    """Solve the stopped functional graph, with endpoint/x at open exits."""
    vertices = set(vertices) | {endpoint}
    f = {endpoint: Fraction(1)}
    for start in sorted(vertices):
        trail, index, x = [], {}, start
        while x in vertices and x not in f and x not in index:
            index[x] = len(trail)
            trail.append(x)
            x = step(x)
        if x in index:
            for v in trail[index[x]:]:
                f[v] = Fraction(0)
            trail = trail[:index[x]]
        for v in reversed(trail):
            nxt = step(v)
            f[v] = Fraction(3 if v & 1 else 1, 2) * f.get(nxt, Fraction(endpoint, nxt))
    return [[x, r.numerator, r.denominator] for x, r in sorted(f.items())]


def search(source, length, *, maximum_work=1000000, maximum_candidates=1000000):
    integer(maximum_work, 1)
    integer(maximum_candidates, 1)
    y, c, H, bound = target_data(source, length)
    # q is reconstructed exactly without a logarithm.
    q, p = 0, c * (1 << length)
    while p > 1:
        p /= 3
        q += 1
    common = dict(schema=SCHEMA, source=source, length=length, endpoint=y,
                  odd_count=q, source_bound=bound, proves_collatz=False)
    if bound > maximum_candidates:
        return dict(common, status="UNKNOWN", reason="candidate_work_budget")
    vertices, cuts, work, longest = set(), Counter(), 0, 0
    for seed in range(1, bound+1):
        x, two, three, k, q, seen = seed, 1, 1, 0, 0, set()
        while True:
            vertices.add(x)
            if two*x*H.denominator >= three*H.numerator:
                cuts["normalization_cut"] += 1
                break
            if x == y:
                return dict(common, status="IMPROVEMENT",
                            witness=dict(source=seed, length=k, odd_count=q))
            if x in seen:
                cuts["cycle_avoiding_endpoint"] += 1
                break
            if work >= maximum_work:
                return dict(common, status="UNKNOWN", reason="step_work_budget")
            seen.add(x)
            if x & 1:
                three *= 3
                q += 1
            two *= 2
            x, k, work = step(x), k+1, work+1
        longest = max(longest, k)
    rows = potential(vertices, y)
    return dict(common, status="CERTIFIED_NO_STRICT_IMPROVEMENT", potential=rows,
                diagnostics=dict(work=work, vertices=len(rows), maximum_branch_length=longest,
                                 cut_kinds=dict(sorted(cuts.items()))))


def closed_states(bound):
    states = set()
    for seed in range(1, bound+1):
        x, work = seed, 0
        while x not in states:
            states.add(x)
            x = step(x)
            work += 1
            if work > 100000:
                raise RuntimeError("reference closure budget exceeded; not a certificate")
    return sorted(states)


def capacities():
    A, O = [1], [1]
    for N in range(1, 49):
        a = o = 0
        for s in range(N+1):
            span = Fraction(3**s*((1 << N)-1) + ((1 << (N-s))-1)*(3**s-2**s), 1 << N)
            size = 1 + span.numerator//span.denominator
            m = 0
            while (1 << m) < size:
                m += 1
            a += min(comb(N, s), A[m]) if m < N else comb(N, s)
            if s:
                o += min(comb(N-1, s-1), A[m]) if m < N else comb(N-1, s-1)
        A.append(a)
        O.append(o)
    upper = Fraction(2079, 1000) + sum((Fraction(O[n], 1 << n) for n in range(19, 49)), Fraction())
    log2 = sum((Fraction(2, (2*k+1)*3**(2*k+1)) for k in range(3)), Fraction())
    three_log13 = 9*log2 + 3*Fraction(10, 21)
    pair = lambda x: [x.numerator, x.denominator]
    return dict(proves_collatz=False, rows=[[n, A[n], O[n]] for n in range(49)],
                reciprocal_upper=pair(upper), coarse_upper=[751,100],
                log2_lower=pair(log2), log13_over8_lower=[10,21],
                three_log13_lower=pair(three_log13),
                inherited_sha256={p: hashlib.sha256((ROOT/p).read_bytes()).hexdigest() for p in INHERITED},
                inherited_scope="E46 convergence below 583561 and E54 shell-49 tail are reused, not rerun")


def word_data(word, source=None):
    p, B, two = 1, 0, 1
    for b in word:
        if b == "1":
            p, B = 3*p, 3*B+two
        two *= 2
    residue = (-B*pow(p, -1, two)) % two
    z = (residue or two) if source is None else source
    x, states = z, [z]
    for b in word:
        if (x & 1) != int(b):
            raise ValueError("not a literal word")
        x = step(x)
        states.append(x)
    return dict(word=word, source=z, endpoint=x, q=word.count("1"), B=B, states=states)


def regressions():
    words = set("".join(bs) for k in range(1, 5) for bs in product(("110", "111"), repeat=k))
    words.update("11101"*r+"1100"*s for r in range(4) for s in range(4) if r+s)
    rows = [word_data(w) for w in sorted(words)]
    for m in range(1, 9):
        for source in (2**m-1, 8**m-5):
            x, word = source, ""
            for _ in range(20):
                word += str(x & 1)
                x = step(x)
            rows.append(word_data(word, source))
    controls = {
        "NG24_d": (15,"111100"), "NG24_a": (7,"11101"),
        "NG25_lower_d": (287,"111110100"), "NG25_lower_a": (273,"1"),
        "NG25_higher_d": (59,"110110"), "NG25_higher_a": (39,"1110110"),
        "NG26_d": (1874247,"11101011111111101000001"), "NG26_a": (937121,"1010110111111101011100"),
        "NG28_d": (310028220411,"1101101101110011100111011101010101101101"),
        "NG28_a": (155014110207,"111111111101111110101011110010001001100"),
        "q22_d": (29023002619,"1101101101101011010110110110110101"),
        "q22_a": (14511501311,"111111111111011101101011000100100"),
        "NG43_d": (358030447,"1111"+"0110110110110110001101101"),
        "NG43_a": (179015223,"111"+"0011111111111111010000100"),
        "source167": (167,"11101101111110011110001010"), "source7": (7,"11101001000"),
        "positive_cycle": (1,"10"), "negative1": (-1,"1"),
        "negative5": (-5,"110"), "negative17": (-17,"11110111000"),
    }
    named = {k: word_data(w,z) for k,(z,w) in controls.items()}
    # Formal critical model: separate inverse residues from ordinary sources.
    A, power3, E, odd_positions = 0, 1, 0, []
    for j in range(128):
        f = power3.bit_length()-1
        nxt = power3*3
        b = nxt.bit_length()-1-f
        inc = int(b == 2 and A < isqrt(j+1))
        odd_positions.append(E)
        E += b-inc
        A += inc
        power3 = nxt
    u = "".join("1" if k in set(odd_positions) else "0" for k in range(E))
    named["NG22_formal"] = word_data(u)
    named["NG45_formal"] = word_data("110111111"+u)
    # Finite 703 control: full safety through 80, odd boundaries through 52.
    x, q, odd = 703, 0, []
    for k in range(81):
        if x & 1:
            odd.append([q, x, k, (3**q).bit_length()-1-k])
        q += x & 1
        x = step(x)
    return dict(proves_collatz=False, families=rows, controls=named, odd_703=odd,
                formal_scope="finite canonical residues; P255 excludes these particular infinite ordinary sources; no general language exclusion",
                weight_hole_control=[14,24573,[1,2,5,6]])


def generate(directory):
    directory.mkdir(parents=True, exist_ok=True)
    cases = [(s,L) for s in range(1,128) for L in range(21)] + [(703,80)]
    records = [search(s,L) for s,L in cases]
    if any(r["status"] == "UNKNOWN" for r in records):
        raise RuntimeError("audit incomplete")
    bound = max(r["source_bound"] for r in records)
    falsifiers=[]
    for r in records:
        if r["status"] != "CERTIFIED_NO_STRICT_IMPROVEMENT" or r["source"] % 2 == 0:
            continue
        x,E,j,previous = r["source"],0,0,None
        while E <= r["length"]:
            row=[j,x,E,(3**j).bit_length()-1-E]
            if previous is not None and previous[3] > row[3]:
                falsifiers.append([r["source"],r["length"],previous,row])
                break
            previous=row
            t=3*x+1
            e=(t & -t).bit_length()-1
            x,E,j=t >> e,E+e,j+1
    files = {"queries": dict(proves_collatz=False, records=records, monotonicity_falsifiers=falsifiers),
             "certificate_7": next(r for r in records if (r["source"],r["length"]) == (7,4)),
             "certificate_703": records[-1],
             "reference": dict(proves_collatz=False, maximum_seed=bound, vertices=closed_states(bound)),
             "capacity": capacities(), "regressions": regressions()}
    for name,data in files.items():
        (directory/f"phase43_{name}.json").write_text(json.dumps(data, sort_keys=True, separators=(",", ":"))+"\n")
    return dict(queries=len(records), counts=dict(Counter(r["status"] for r in records)), proves_collatz=False)


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--artifact-dir", type=Path)
    p.add_argument("--source", type=int)
    p.add_argument("--length", type=int)
    p.add_argument("--maximum-work", type=int, default=1000000)
    p.add_argument("--maximum-candidates", type=int, default=1000000)
    p.add_argument("--output", type=Path)
    a = p.parse_args()
    if a.artifact_dir is not None:
        result = generate(a.artifact_dir)
    else:
        if a.source is None or a.length is None:
            p.error("use --artifact-dir, or both --source and --length")
        result = search(a.source, a.length, maximum_work=a.maximum_work, maximum_candidates=a.maximum_candidates)
    encoded = json.dumps(result, sort_keys=True, indent=2)+"\n"
    if a.output:
        a.output.write_text(encoded)
    else:
        print(encoded, end="")


if __name__ == "__main__":
    main()
