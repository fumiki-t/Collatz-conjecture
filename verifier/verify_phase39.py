#!/usr/bin/env python3
"""Reconstruct Phase 39 finite evidence with independent exact algorithms.

Affine corrections use odd positions, parity residues use successive bit lifts,
jump vertices are regrouped from closed-form tail words, capacities use Pascal
rows, and rational cycles use rotated fixed-point formulae. No search module
or certificate-supplied derived value is an arithmetic input.
"""
from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import sys
from collections import defaultdict
from fractions import Fraction
from functools import lru_cache
from pathlib import Path


FILES = ("phase39_carry_audit.json", "phase39_jump_dag.json",
         "phase39_capacity_cycle.json", "phase39_regressions.json",
         "phase39_obstruction_report.md")
STATUSES = {**{f"P{n}": "VERIFIED_THEOREM" for n in (235, 236, 237, 238, 239, 241)},
            "P240": "CONDITIONAL", "E55": "VERIFIED_FINITE",
            "H72": "OPEN", "H112": "OPEN", "H133": "OPEN"}
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]
EXPECTED_OBSTRUCTION = """# Phase 39 obstruction record

The literal identity a=d=1 has k=s=m=0 and zero carry at every depth.
The accepted fixed-rewrite theorem excludes identity relations. The nonidentity
pair a=1,d=101 at S=1 has k=2,s=1,m=-1 and zero carry, with both endpoints 2;
this is the periodic exception. No finite-dictionary direct-lift theorem rules
out arbitrary compositions, prefix-changing rules, or other proof methods.

The tail DAG audit checks safe alternatives separately from their weights.
No failure of that safety condition was found through tail length 12 and
initial run 12; this is not an all-depth safety theorem or global confluence.
The smallest DAG collision is J=3 at tail length 2, from tails 0 and 1.

Positive rational event directions require care: e=3 fixes x=1/5,y=3/5.
The accepted strict direction theorem assumes positive ordinary odd integers.
NG22, NG24, NG41, NG42, source 167, and negative cycles remain retained controls.

## What this result does not prove

H112 and H72 remain OPEN. The macroscopic carry lower bound constructs no
ancestor. The X02/H112 reduction is conditional. Finite DAG collisions do not
exclude positive ordinary infinite geodesics. Event counts do not exclude
arbitrary-area critical cycles. proves_collatz=false.
"""


class VerificationError(RuntimeError):
    """Malformed, incomplete, or arithmetically invalid evidence."""


def require(condition: bool, message: str) -> None:
    if not condition:
        raise VerificationError(message)


def canonical(value: object) -> str:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), allow_nan=False)


def digest(value: object) -> str:
    return hashlib.sha256(canonical(value).encode("ascii")).hexdigest()


def envelope(kind: str, **fields: object) -> dict:
    return {"format": f"collatz-phase39-{kind}-v1", "proves_collatz": False, **fields}


def binary_words(limit: int, empty: bool = False):
    if empty:
        yield ""
    for size in range(1, limit + 1):
        for mask in range(2**size):
            yield format(mask, f"0{size}b")


@lru_cache(maxsize=None)
def positional_affine(word: str) -> tuple[int, int]:
    require(set(word) <= {"0", "1"}, "nonbinary word")
    positions = [j for j, bit in enumerate(word) if bit == "1"]
    q = len(positions)
    return q, sum(2**position * 3**(q-rank-1)
                  for rank, position in enumerate(positions))


@lru_cache(maxsize=None)
def prefix_safe(word: str) -> bool:
    positions = [j for j, bit in enumerate(word) if bit == "1"]
    return all(3**sum(position < size for position in positions) > 2**size
               for size in range(1, len(word)+1))


def shortcut(value: int) -> int:
    return (3*value+1)//2 if value % 2 else value//2


def traverse(source: int, word: str) -> int:
    current = source
    for symbol in word:
        require(current % 2 == int(symbol), "parity realization mismatch")
        current = shortcut(current)
    q, b = positional_affine(word)
    require(2**len(word)*current == 3**q*source+b, "affine endpoint mismatch")
    return current


@lru_cache(maxsize=None)
def least_positive_source(word: str) -> int:
    # Lifting the next source bit flips the next orbit parity because every
    # preceding multiplier has odd numerator. This uses no modular inverse.
    residue = 0
    for j, symbol in enumerate(word):
        endpoint = traverse(residue, word[:j])
        if endpoint % 2 != int(symbol):
            residue += 2**j
    result = residue or 2**len(word)
    traverse(result, word)
    return result


def rebuild_carry() -> dict:
    literals = [w for w in binary_words(8) if prefix_safe(w)]
    relations = []
    for a in literals:
        qa, ba = positional_affine(a)
        for d in literals:
            qd, bd = positional_affine(d)
            k, s = len(d)-len(a), qd-qa
            if a == d or k < 0 or s < 0:
                continue
            quot, rem = divmod(2**k*ba-bd, 3**qa)
            if not rem:
                relations.append([a, d, k, s, str(quot)])
    rows = []
    lifts = descents = macroscopic = 0
    for prefix in binary_words(6, empty=True):
        depth, bp = positional_affine(prefix)
        for a, d, k, s, encoded in relations:
            m, gamma = int(encoded), 2**k-3**s
            n = least_positive_source(prefix+d)
            state = traverse(n, prefix)
            common_endpoint = traverse(state, d)
            local_carry = gamma*state+m
            prefix_carry = gamma*bp+2**len(prefix)*m
            require(prefix_carry == 2**len(prefix)*local_carry-gamma*3**depth*n,
                    "current-state carry identity")
            lift = local_carry % 3**depth == 0
            require(lift == (prefix_carry % 3**depth == 0), "carry divisibility")
            ancestor = None
            if lift:
                lifts += 1
                rational = Fraction(3**s*n-prefix_carry//3**depth, 2**k)
                if rational > 0 and rational.denominator == 1:
                    ancestor = rational.numerator
                    require(traverse(ancestor, prefix+a) == common_endpoint, "ancestor endpoint")
                    if ancestor < n and prefix_safe(prefix+a) and prefix_safe(prefix+d):
                        descents += 1
            if gamma >= 0:
                bound = 2**k*(3*state+a.count("1")+d.count("1"))
                require(3*abs(local_carry) <= bound, "macroscopic carry upper bound")
                if lift and local_carry != 0:
                    require(3**(depth+1) <= bound, "macroscopic divisibility lower bound")
                    macroscopic += 1
            rows.append([prefix, a, d, str(n), str(state), str(prefix_carry),
                         str(local_carry), lift, None if ancestor is None else str(ancestor)])
    universal = []
    for run in range(4, 33):
        a, d = "1"*(run-1)+"01", "1"*run+"00"
        qa, ba = positional_affine(a)
        qd, bd = positional_affine(d)
        require(qa == qd == run and ba == 3**run-2**(run-1)
                and bd == 3**run-2**run and 2*ba-bd == 3**run,
                "universal rewrite correction")
        require(prefix_safe(a) and prefix_safe(d), "universal rewrite safety")
        n = least_positive_source(d)
        ancestor, remainder = divmod(n-1, 2)
        require(remainder == 0 and 0 < ancestor < n, "universal source descent")
        endpoint = traverse(n, d)
        require(traverse(ancestor, a) == endpoint, "universal coalescence")
        universal.append([run, str(ba), str(bd), str(n), str(ancestor), str(endpoint)])
    cutoffs = []
    for a, d, k, s, encoded in relations:
        gamma, m = abs(2**k-3**s), abs(int(encoded))
        depth = next(j for j in itertools.count()
                     if 2**j > 200*gamma and 3**j > 2*m)
        require(Fraction(100*gamma, 2**depth)+Fraction(m, 3**depth) < 1,
                "fixed-relation exact cutoff")
        cutoffs.append([a, d, depth])
    return envelope("carry", maximum_word_length=8, maximum_prefix_length=6,
                    relations=relations, row_count=len(rows), lift_count=lifts,
                    safe_descent_count=descents, macro_bound_count=macroscopic,
                    rows_sha256=digest(rows), selected_rows=rows[:3]+rows[-3:],
                    universal_rewrite_rows=universal, fixed_bound_constant=100,
                    fixed_relation_cutoffs=cutoffs)


def rebuild_jump() -> dict:
    vertices, levels, rewrites, first_gain = [], [], [], {}
    unsafe = 0
    for ell in range(1, 13):
        # Enumerate complete suffixes; do not use forward DAG transitions.
        tails = [format(mask, f"0{ell-1}b") if ell > 1 else ""
                 for mask in range(2**(ell-1))]
        by_jump = defaultdict(list)
        jump_for = {}
        for tail in tails:
            word = "10"+tail
            q, b = positional_affine(word)
            numerator = b+2**len(word)-3**q
            jump, remainder = divmod(numerator, 2)
            require(remainder == 0 and jump % 2 == 1 and jump > 0, "odd jump vertex")
            jump_for[tail] = jump
            by_jump[jump].append(tail)
        levels.append([ell, len(tails), len(by_jump), sum(len(group)>1 for group in by_jump.values())])
        for jump in sorted(by_jump):
            vertices.append([ell, str(jump), [[tail, tail.count("1")] for tail in by_jump[jump]]])
        for run in range(1, 13):
            for tail in tails:
                original = "1"*run+"0"+tail
                if not prefix_safe(original):
                    continue
                q, b = positional_affine(original)
                require(b+2**len(original)-3**q == 2**run*jump_for[tail], "shifted jump scaling")
                for alternative_tail in by_jump[jump_for[tail]]:
                    gain = alternative_tail.count("1")-tail.count("1")
                    if not 1 <= gain < run:
                        continue
                    alternative = "1"*(run-gain)+"0"+alternative_tail
                    alt_safe = prefix_safe(alternative)
                    unsafe += not alt_safe
                    n = least_positive_source(original)
                    quotient, rem = divmod(n+1, 2**gain)
                    ancestor = quotient-1
                    require(rem == 0 and 0 < ancestor < n, "jump source descent")
                    require(positional_affine(alternative)[0] == q
                            and len(original)-len(alternative) == gain, "jump dimensions")
                    require(traverse(n, original) == traverse(ancestor, alternative), "jump coalescence")
                    row = [ell, run, tail, alternative_tail, gain, alt_safe, str(n), str(ancestor)]
                    rewrites.append(row)
                    if alt_safe and str(gain) not in first_gain:
                        first_gain[str(gain)] = row
    return envelope("jump-dag", maximum_tail_length=12, maximum_initial_run=12,
                    tail_length_counts_initial_zero=True, maximum_suffix_length=11,
                    levels=levels, vertices=vertices, rewrite_count=len(rewrites),
                    unsafe_candidate_count=unsafe, maximum_gain=max(map(int, first_gain)),
                    first_safe_gain=first_gain, rewrite_rows_sha256=digest(rewrites),
                    ordering="ell, initial run, lexicographic original tail, lexicographic alternative tail",
                    safety_scope="Full word safety tested separately; no all-depth implication is inferred.")


def odd_step(value: int) -> tuple[int, int]:
    require(value % 2 == 1, "odd source required")
    endpoint, exponent = shortcut(value), 1
    while endpoint % 2 == 0:
        endpoint = shortcut(endpoint)
        exponent += 1
    return endpoint, exponent


def positive_lifts() -> dict:
    rows = []
    for word in binary_words(12):
        q, b = positional_affine(word)
        if q == 0:
            continue
        n = least_positive_source(word)
        endpoint = traverse(n, word)
        require(1 <= endpoint < 3**q, "canonical positive endpoint range")
        choices = []
        for t in (0, 1, 3):
            lifted = n+2**len(word)*t
            image = traverse(lifted, word)
            require(image == endpoint+3**q*t and lifted > 0, "ordinary source lift order")
            choices.append([t, str(lifted), str(image)])
        rows.append([word, str(n), str(endpoint), choices])
    return {"maximum_word_length": 12, "word_count": len(rows),
            "lift_count": 3*len(rows), "rows_sha256": digest(rows),
            "selected_rows": rows[:2]+rows[-2:]}


def rebuild_capacity_cycle() -> dict:
    binomial_rows, pascal = [], [1]
    for length in range(1, 501):
        count = sum(coefficient for weight, coefficient in enumerate(pascal, 1)
                    if 3**weight > 2**length)
        require(count**30 < 2**(29*length), "finite capacity exponent")
        binomial_rows.append([length, str(count)])
        pascal = [1]+[pascal[j]+pascal[j+1] for j in range(len(pascal)-1)]+[1]
    require(3**14 < 2**23, "rational entropy slope")
    require(23**690 < 2**667*14**420*9**270, "entropy power certificate")
    rows, integral_rows, rational_examples = [], [], []
    for q in range(1, 6):
        for exponents in itertools.product(range(1, 5), repeat=q):
            denominator = 2**sum(exponents)-3**q
            if denominator <= 0:
                continue
            values = []
            for index in range(q):
                rotated = exponents[index:]+exponents[:index]
                word = "".join("1"+"0"*(exponent-1) for exponent in rotated)
                values.append(Fraction(positional_affine(word)[1], denominator))
            minimum = min(values)
            product, directions = Fraction(1), []
            for index, (value, exponent) in enumerate(zip(values, exponents)):
                endpoint = values[(index+1)%q]
                require(2**exponent*endpoint == 3*value+1, "rotated rational cycle")
                y, next_y = (value+1)/2, (endpoint+1)/2
                correction = Fraction(2**(exponent-1)-1, 3*y)
                require(2**exponent*next_y == 3*y+2**(exponent-1)-1, "shifted event identity")
                require(0 <= correction < 1/minimum, "strict event increment")
                product *= 1+correction
                directions.append((next_y > y)-(next_y < y))
            require(product == Fraction(2**sum(exponents), 3**q), "cycle event product")
            integral = all(x.denominator == 1 and x.numerator % 2 == 1 for x in values)
            row = [list(exponents), str(values[0]), str(minimum),
                   sum(e >= 2 for e in exponents), str(product), integral, directions]
            rows.append(row)
            if integral:
                for value, e, direction in zip(values, exponents, directions):
                    require(direction == 1 if e == 1 else direction == -1 or (value == 1 and e == 2),
                            "ordinary integer event direction")
                integral_rows.append(row)
            elif q == 1:
                rational_examples.append(row)
    direct = []
    for source in range(1, 1025, 2):
        value = source
        for step in range(64):
            endpoint, e = odd_step(value)
            require(endpoint > value if e == 1 else endpoint < value or (value == 1 and e == 2),
                    "direct event direction")
            direct.append([source, step, str(value), e, str(endpoint)])
            value = endpoint
    return envelope("capacity-cycle", maximum_capacity_N=500, binomial_rows=binomial_rows,
                    entropy_certificate={"theta_numerator":14, "theta_denominator":23,
                                         "rho_numerator":29, "rho_denominator":30,
                                         "power_slope_valid":True, "power_entropy_valid":True},
                    X1_bound=1, positive_endpoint_lifts=positive_lifts(),
                    cycle_scope={"maximum_odd_count":5, "maximum_exponent":4},
                    rational_cycle_count=len(rows), cycle_rows_sha256=digest(rows),
                    positive_integral_cycles=integral_rows, rational_direction_exceptions=rational_examples,
                    direct_event_count=len(direct), direct_event_rows_sha256=digest(direct),
                    conditional_reduction={"uses_external_X02":True, "uses_phase38_E54":True,
                                           "H112_status":"OPEN", "H72_status":"OPEN",
                                           "cycle_exclusion_claimed":False,
                                           "reciprocal_includes_initial_odd_source":True})


def rebuild_regressions() -> dict:
    selected = {"11101", "1100"}
    selected.update("11101"*r+"1100"*s for r in range(1,5) for s in range(1,5))
    for count in range(1,5):
        selected.update("".join(t) for t in itertools.product(("110", "111"), repeat=count))
    word_rows = []
    for word in sorted(selected, key=lambda w:(len(w), w)):
        q, b = positional_affine(word)
        n = least_positive_source(word)
        word_rows.append([word, q, str(b), str(n), str(traverse(n, word)), prefix_safe(word)])
    source_rows = []
    cases = [("2^m-1", [2**m-1 for m in range(2,13)]),
             ("8^m-5", [8**m-5 for m in range(1,9)]), ("source 167", [167])]
    for label, sources in cases:
        for n in sources:
            value, bits = n, []
            for _ in range(32):
                bits.append(str(value % 2))
                value = shortcut(value)
            source_rows.append([label, str(n), "".join(bits), str(value)])
    residues = [[w, str(traverse(least_positive_source(w), w) % 3**positional_affine(w)[0])]
                for w in ("11101", "111100", "11011101", "110111100")]
    require(residues[0][1] == residues[1][1] and residues[2][1] != residues[3][1], "NG24 noncongruence")
    companion, word, formal = Fraction(3,2), "", []
    previous_residue, previous_modulus = 0, 1
    for step in range(128):
        exponent = 1 if companion <= Fraction(5,3) else 2
        companion = (3*companion-1)/2**exponent
        require(1 < companion <= 2, "NG22 companion invariant")
        word += "1"+"0"*(exponent-1)
        residue = least_positive_source(word)
        require((residue-previous_residue) % previous_modulus == 0, "NG22 coherent inverse source")
        previous_residue, previous_modulus = residue, 2**len(word)
        formal.append([step, exponent, str(companion), str(residue)])
    negative = []
    for initial, expected in ((-1,[1]), (-5,[1,2]), (-17,[1,1,1,2,1,1,4])):
        value, trace, exponents = initial, [initial], []
        for _ in expected:
            value, exponent = odd_step(value)
            trace.append(value)
            exponents.append(exponent)
        require(value == initial and exponents == expected, "negative cycle control")
        negative.append([initial, exponents, trace])
    q, length, area, height, components, surplus, exceptional, width, zeroes = 2301,3647,229,2,138,90,92,24,10
    factor = width+1+components*(width-1)+min(2*area, length*area//q+components)
    residual = area-components+exceptional
    span = min(2*residual, length*residual//q+exceptional)
    triple = ((components+2*exceptional)*(width+1)+3*span
              +(width+3)*(3+2*zeroes+zeroes*(zeroes-1)//2))
    require(factor-length == 10 and triple-3*length == 43, "NG41 scalar margins")
    mechanical = [(3**j).bit_length()-1 for j in range(3)]
    require(mechanical == [0,1,3] and 2 not in range(mechanical[2],5), "NG42 wrong orientation")
    qa, ba = positional_affine("1")
    qd, bd = positional_affine("101")
    require((qd-qa, len("101")-len("1"), (4*ba-bd)//3**qa) == (1,2,-1)
            and traverse(1,"1") == traverse(1,"101") == 2, "periodic zero carry")
    q_ab, b_ab = positional_affine("111011100")
    multiplier = Fraction(3**q_ab, 2**9)
    fixed = Fraction(b_ab, 2**9-3**q_ab)
    require((b_ab, multiplier, fixed) == (817, Fraction(729,512), Fraction(-817,217)), "AB witness")
    return envelope("regressions", mandatory_families=FAMILIES, word_rows=word_rows,
                    source_rows=source_rows, NG24_endpoint_residues=residues,
                    NG22_formal_policy={"steps":128,"rows_sha256":digest(formal),"last_row":formal[-1],
                                       "ordinary_positive_source_claimed":False},
                    NG41_scalar_survivor={"q":q,"L":length,"A":area,"h":height,"J":components,
                                         "Sigma":surplus,"E":exceptional,"n":width,"Z":zeroes,
                                         "P207_margin":factor-length,"P208_margin":triple-3*length,"actual_cycle":False},
                    NG42_orientation={"q":3,"K":5,"actual":[0,1,2],"mechanical":mechanical,"missed_position":2},
                    zero_carry_controls={"identity":{"a":"1","d":"1","k":0,"s":0,"m":0},
                                         "periodic":{"a":"1","d":"101","S":1,"k":2,"s":1,"m":-1,"endpoint":2}},
                    negative_cycles=negative,
                    AB_witness={"word":"111011100","B":b_ab,"multiplier":str(multiplier),"fixed_point":str(fixed)})


@lru_cache(maxsize=1)
def reconstructed_payloads() -> tuple[str, ...]:
    # Immutable, fixed-scope results only. Input artifacts never seed this cache.
    return tuple(canonical(builder()) for builder in
                 (rebuild_carry, rebuild_jump, rebuild_capacity_cycle, rebuild_regressions))


def load_payload(path: Path) -> dict:
    def reject_pairs(pairs):
        value = {}
        for key, item in pairs:
            require(key not in value, f"duplicate JSON key in {path.name}: {key}")
            value[key] = item
        return value
    try:
        value = json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=reject_pairs,
                           parse_constant=lambda token: (_ for _ in ()).throw(ValueError(token)))
        require(isinstance(value, dict), f"{path.name} must be an object")
        return value
    except (OSError, UnicodeError, ValueError, RecursionError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc


def verify(directory: Path) -> dict:
    directory = Path(directory)
    payloads = [load_payload(directory/name) for name in FILES[:4]]
    for name, value, rebuilt in zip(FILES, payloads, reconstructed_payloads()):
        try:
            matches = canonical(value) == rebuilt
        except (TypeError, ValueError, RecursionError) as exc:
            raise VerificationError(f"malformed {name}: {exc}") from exc
        require(matches, f"{name}: independently reconstructed artifact mismatch")
    try:
        report = (directory/FILES[-1]).read_text(encoding="utf-8")
    except (OSError, UnicodeError) as exc:
        raise VerificationError(f"cannot read obstruction report: {exc}") from exc
    require(report == EXPECTED_OBSTRUCTION, "obstruction report boundary mismatch")
    try:
        hashes = {name:hashlib.sha256((directory/name).read_bytes()).hexdigest() for name in FILES}
    except OSError as exc:
        raise VerificationError(f"cannot hash input: {exc}") from exc
    carry, jump, capacity, _ = payloads
    return {"valid":True, "generator_imported":False, "floating_point_used_for_acceptance":False,
            "input_sha256":hashes, "claim_statuses":STATUSES,
            "carry_rows":carry["row_count"], "carry_relations":len(carry["relations"]),
            "dag_vertices":len(jump["vertices"]), "dag_rewrites":jump["rewrite_count"],
            "capacity_rows":len(capacity["binomial_rows"]),
            "positive_endpoint_lifts":capacity["positive_endpoint_lifts"]["lift_count"],
            "rational_cycles":capacity["rational_cycle_count"],
            "direct_event_count":capacity["direct_event_count"], "proves_collatz":False}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except VerificationError as exc:
        result = {"valid":False, "error":str(exc), "proves_collatz":False}
    encoded = json.dumps(result, indent=2, sort_keys=True)+"\n"
    if args.output:
        args.output.write_text(encoded, encoding="utf-8")
    print(encoded, end="")
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    sys.exit(main())
