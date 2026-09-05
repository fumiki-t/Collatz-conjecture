"""Exact finite identities and scope falsifiers; no finite orbit is called nonperiodic."""
from collections import defaultdict
from fractions import Fraction
from itertools import product

from src.phase40_search import accelerated, affine, realize, safe, source


TARGET_TAIL = "0110110110110110001101101"
ALTERNATE_TAIL = "0011111111111111010000100"
VALLEY_SUFFIX = "11111111111111010000100"


def shortcut(n):
    return (3 * n + 1) // 2 if n % 2 else n // 2


def states_for_word(n, word):
    states = [n]
    for bit in word:
        assert states[-1] % 2 == int(bit)
        states.append(shortcut(states[-1]))
    return states


def coefficient_trace(word):
    coefficient = Fraction(1)
    trace = [coefficient]
    for bit in word:
        coefficient *= Fraction(3 if bit == "1" else 1, 2)
        trace.append(coefficient)
    return trace


def independent_tail_data(tail):
    """Use a positional sum and a rational prefix maximum, not the J recurrence."""
    weight = tail.count("1")
    correction = sum(
        (1 << j) * 3 ** tail[j + 1 :].count("1")
        for j, bit in enumerate(tail)
        if bit == "1"
    )
    jump = correction + (1 << len(tail)) - 3**weight
    q = 0
    barrier = Fraction(1)
    for length, bit in enumerate(tail, 1):
        q += bit == "1"
        barrier = max(barrier, Fraction(1 << length, 3**q))
    run = 0
    while Fraction(3, 2) ** run <= barrier:
        run += 1
    return jump, weight, run


def odd_window(start, count):
    """Literal arithmetic for the finite normalized product."""
    x = start
    total_exponent = 0
    beta = Fraction()
    product_value = Fraction(1)
    exponents = []
    states = [start]
    for j in range(count):
        beta += Fraction(1 << total_exponent, 3 ** (j + 1))
        product_value *= 1 + Fraction(1, 3 * x)
        raw = 3 * x + 1
        exponent = 0
        while raw % 2 == 0:
            raw //= 2
            exponent += 1
        assert accelerated(x) == (raw, exponent)
        total_exponent += exponent
        x = raw
        exponents.append(exponent)
        states.append(x)
        assert Fraction((1 << total_exponent) * x, 3 ** (j + 1)) == start + beta
        assert start * product_value == start + beta
    return states, exponents, start + beta


def test_length_25_witness_sources_and_exact_valley_suffix():
    assert len(TARGET_TAIL) == len(ALTERNATE_TAIL) == 25
    assert independent_tail_data(TARGET_TAIL) == (166692291, 15, 4)
    assert independent_tail_data(ALTERNATE_TAIL) == (166692291, 16, 4)
    target = "1111" + TARGET_TAIL
    alternate = "111" + ALTERNATE_TAIL
    assert affine(target) == (19, 3292467211)
    assert affine(alternate) == (19, 2227364339)
    assert source(target) == 358030447
    assert source(alternate) == 179015223
    assert safe(target) and not safe(alternate)
    assert realize(source(target), target) == realize(source(alternate), alternate) == 775093205
    assert source(target) + 1 == 2 * (source(alternate) + 1)
    coefficients = coefficient_trace(alternate)
    valley = min(range(len(coefficients)), key=coefficients.__getitem__)
    assert valley == 5 and alternate[:valley] == "11100"
    assert coefficients[valley] == Fraction(27, 32)
    assert sum(c == coefficients[valley] for c in coefficients) == 1
    assert alternate[valley:] == VALLEY_SUFFIX
    assert (len(VALLEY_SUFFIX), VALLEY_SUFFIX.count("1")) == (23, 16)
    assert safe(VALLEY_SUFFIX)
    actual_valley_source = states_for_word(source(alternate), alternate)[valley]
    assert actual_valley_source == 151044095
    assert realize(actual_valley_source, VALLEY_SUFFIX) == 775093205
    canonical_suffix_source = source(VALLEY_SUFFIX)
    assert canonical_suffix_source == 49151
    assert actual_valley_source == canonical_suffix_source + 18 * (1 << 23)
    assert realize(canonical_suffix_source, VALLEY_SUFFIX) == 252227
    assert 775093205 == 252227 + 18 * 3**16
    assert coefficient_trace(VALLEY_SUFFIX)[-1] > coefficient_trace(alternate)[-1]
    assert coefficient_trace(alternate)[-1] == 2 * coefficient_trace(target)[-1]


def test_lexicographically_first_length_25_pair_is_a_distinct_witness():
    target_tail = "0110110110110010110101101"
    alternate_tail = "0011111111111011100001100"
    assert independent_tail_data(target_tail) == (173991363, 15, 4)
    assert independent_tail_data(alternate_tail) == (173991363, 16, 4)
    assert target_tail < TARGET_TAIL
    target, alternate = "1111" + target_tail, "111" + alternate_tail
    assert safe(target) and not safe(alternate)
    n, smaller = source(target), source(alternate)
    assert n + 1 == 2 * (smaller + 1)
    assert realize(n, target) == realize(smaller, alternate)


def test_minimum_initial_run_matches_all_small_literal_safety_checks():
    for length in range(1, 10):
        for bits in product("01", repeat=length - 1):
            tail = "0" + "".join(bits)
            _, _, minimum_run = independent_tail_data(tail)
            assert minimum_run >= 2
            for run in range(minimum_run + 3):
                word = "1" * run + tail
                rational_safe = all(c > 1 for c in coefficient_trace(word)[1:])
                assert safe(word) == rational_safe == (run >= minimum_run)


def test_weight_threshold_criterion_covers_every_initial_run():
    # For fixed tails, safety changes only at these exact run thresholds.
    # The finite R loop crosses their largest threshold, then both paths stay safe.
    groups = defaultdict(list)
    for length in range(1, 10):
        for bits in product("01", repeat=length - 1):
            tail = "0" + "".join(bits)
            jump, weight, run = independent_tail_data(tail)
            groups[length, jump].append((tail, weight, run))
    # Include the audited failing vertex; do not infer length-25 minimality here.
    for tail in (TARGET_TAIL, ALTERNATE_TAIL):
        jump, weight, run = independent_tail_data(tail)
        groups[len(tail), jump].append((tail, weight, run))
    checked = failures = 0
    for rows in groups.values():
        for tail, weight, run in rows:
            for other, other_weight, other_run in rows:
                gain = other_weight - weight
                if gain <= 0:
                    continue
                predicted = weight + run < other_weight + other_run
                lower = max(run, gain + 1)
                upper = other_run + gain - 1
                assert predicted == (lower <= upper)
                observed = []
                for initial in range(1, max(run, other_run + gain) + 3):
                    if gain <= initial - 1 and safe("1" * initial + tail) and not safe("1" * (initial - gain) + other):
                        observed.append(initial)
                assert observed == list(range(lower, upper + 1))
                assert bool(observed) == predicted
                checked += 1
                failures += predicted
    assert checked > 1 and failures == 1


def test_finite_normalization_product_and_coalescence_scaling():
    for start in range(1, 128, 2):
        states, exponents, whole_height = odd_window(start, 10)
        split = 3
        _, _, suffix_height = odd_window(states[split], 10 - split)
        prefix_coefficient = Fraction(3**split, 1 << sum(exponents[:split]))
        assert whole_height == suffix_height / prefix_coefficient
    target = "1111" + TARGET_TAIL
    alternate = "111" + ALTERNATE_TAIL
    common_endpoint = realize(source(target), target)
    _, _, endpoint_height = odd_window(common_endpoint, 8)
    target_height = endpoint_height / coefficient_trace(target)[-1]
    alternate_height = endpoint_height / coefficient_trace(alternate)[-1]
    rescued_height = endpoint_height / coefficient_trace(VALLEY_SUFFIX)[-1]
    assert alternate_height == target_height / 2
    assert rescued_height < alternate_height
    # Safe gain one gives equality with half, not an unconditional strict halving.
    safe_a, safe_d = "11101", "111100"
    assert realize(7, safe_a) == 20
    _, _, odd_height = odd_window(5, 6)
    shared_height = 4 * odd_height  # The common endpoint first follows 20 -> 10 -> 5.
    assert shared_height / coefficient_trace(safe_a)[-1] == shared_height / coefficient_trace(safe_d)[-1] / 2


def test_cloud_positive_integral_exact_valuation_and_phase_offset():
    cloud_count = 0
    for x in range(1, 4096, 2):
        nxt, exponent = accelerated(x)
        original = [x]
        for _ in range(exponent):
            original.append(shortcut(original[-1]))
        assert original[-1] == nxt
        for r in range(1, (exponent - 1) // 2 + 1):
            numerator = 3 * x + 1 - 4**r
            denominator = 3 * 4**r
            assert numerator > 0 and numerator % denominator == 0
            z = numerator // denominator
            assert z > 0 and z % 2 == 1
            assert accelerated(z) == (nxt, exponent - 2 * r)
            assert 0 < 2 * r < exponent
            assert original[2 * r] == 3 * z + 1
            assert shortcut(z) == original[2 * r + 1]
            assert Fraction(z) < Fraction(x + 1, 4**r)
            cloud_count += 1
    assert cloud_count > 0


def test_direct_all_exponent_moment_and_geometric_sum_inequalities():
    # These are finite inequalities, not a test claiming convergence from samples.
    totals = {1: [Fraction(), Fraction(), Fraction()], 2: [Fraction(), Fraction(), Fraction()]}
    observed_exponents = set()
    for x in range(1, 4096, 2):
        nxt, exponent = accelerated(x)
        observed_exponents.add(exponent)
        factor = Fraction(1 << exponent, x + 1)
        assert factor == Fraction(3 * x + 1, (x + 1) * nxt)
        assert factor < Fraction(3, nxt)
        for p, sums in totals.items():
            geometric = sum((Fraction(4 ** (p * r), (x + 1) ** p)
                             for r in range(1, (exponent - 1) // 2 + 1)), Fraction())
            bound = Fraction(2**p, 4**p - 1) * factor**p
            assert geometric <= bound
            sums[0] += factor**p
            sums[1] += Fraction(3**p, nxt**p)
            sums[2] += geometric
    assert {1, 2, 3, 4, 5, 6} <= observed_exponents
    for p, (left, right, geometric) in totals.items():
        assert left < right
        assert geometric < Fraction(2**p, 4**p - 1) * right


def test_cloud_collisionfree_claim_requires_nonperiodicity():
    # The orbit of 21 reaches the known trivial cycle. Its cloud is not
    # equal-time collision-free, although all local predecessor identities hold.
    assert accelerated(21) == (1, 6)
    cloud = [(3 * 21 + 1 - 4**r) // (3 * 4**r) for r in (1, 2)]
    assert cloud == [5, 1]
    endpoints = []
    for z in cloud:
        for _ in range(4):
            z = shortcut(z)
        endpoints.append(z)
    assert endpoints == [1, 1]
    assert accelerated(1) == (1, 2)
    # Positive rational formal data do not supply positive integer cloud sources.
    rational_x = Fraction(1, 5)
    assert (3 * rational_x + 1) / 8 == rational_x
    assert (3 * rational_x + 1 - 4) / 12 == Fraction(-1, 5)


def test_mandatory_families_and_prior_obstruction_coordinates():
    literal_words = {"11101", "1100"}
    literal_words.update("11101" * r + "1100" * s for r in range(1, 4) for s in range(1, 4))
    literal_words.update("".join(bits) for length in range(1, 5)
                         for bits in product(("110", "111"), repeat=length))
    for word in literal_words:
        q, correction = affine(word)
        n = source(word)
        assert (1 << len(word)) * realize(n, word) == 3**q * n + correction
    assert affine("111011100") == (6, 817)
    assert Fraction(-817, 3**6 - 2**9) == Fraction(-817, 217)
    starts = [2**m - 1 for m in range(2, 10)] + [8**m - 5 for m in range(1, 7)] + [167]
    for n in starts:
        x = n
        word = ""
        for _ in range(32):
            word += str(x % 2)
            x = shortcut(x)
        q, correction = affine(word)
        assert 2**32 * x == 3**q * n + correction
    residues = []
    for word in ("11101", "111100", "11011101", "110111100"):
        q, _ = affine(word)
        residues.append(realize(source(word), word) % 3**q)
    assert residues == [20, 20, 263, 587]  # NG24: arbitrary left prefix is not congruent.
    assert affine("11100") == (3, 19)
    assert affine("11010") == (3, 23)  # NG42: decoder and cycle shifts have opposite signs.


def test_NG22_formal_policy_keeps_its_ordinary_source_boundary():
    companion = Fraction(3, 2)
    word = ""
    old_residue, old_modulus = 0, 1
    for _ in range(64):
        exponent = 1 if companion <= Fraction(5, 3) else 2
        companion = (3 * companion - 1) / (1 << exponent)
        assert 1 < companion <= 2
        word += "1" + "0" * (exponent - 1)
        residue = source(word)
        assert residue % old_modulus == old_residue % old_modulus
        old_residue, old_modulus = residue, 1 << len(word)
    # Finite nested residues establish no positive ordinary source for the whole word.
