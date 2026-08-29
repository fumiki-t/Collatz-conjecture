#!/usr/bin/env python3
"""Independent exact verifier for Phase 22 cycle-resultant artifacts.

This file deliberately does not import the Phase 22 generator.  Resultants are
reconstructed as Sylvester determinants, whereas production uses a
multiplication matrix in Z[X]/(X^q-2).
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import sys
from fractions import Fraction
from pathlib import Path


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)

V = 300_000
FILES = (
    "phase22_theory.json",
    "phase22_finite_profiles.json",
    "phase22_regressions.json",
    "phase22_literature_audit.json",
    "phase22_obstruction_report.md",
)


def fail(message: str) -> None:
    raise ValueError(message)


def load(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        fail(f"cannot load {path.name}: {exc}")
    if not isinstance(value, dict):
        fail(f"{path.name} must contain an object")
    return value


def save(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def digest(rows: object) -> str:
    raw = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def decode_fraction(value: object) -> Fraction:
    if not isinstance(value, dict) or set(value) != {"numerator", "denominator"}:
        fail("malformed fraction")
    try:
        return Fraction(int(value["numerator"]), int(value["denominator"]))
    except (TypeError, ValueError, ZeroDivisionError):
        fail("malformed fraction integers")


def positive_compositions(total: int, count: int):
    def visit(remaining: int, slots: int, prefix: tuple[int, ...]):
        if slots == 1:
            yield prefix + (remaining,)
            return
        for first in range(1, remaining - slots + 2):
            yield from visit(remaining - first, slots - 1, prefix + (first,))
    yield from visit(total, count, ())


def turns(values: tuple[int, ...]):
    size = len(values)
    for start in range(size):
        yield tuple(values[(start + index) % size] for index in range(size))


def least_cyclic(values: tuple[int, ...]) -> tuple[int, ...]:
    return min(turns(values))


def height_walk(values: tuple[int, ...]) -> tuple[int, ...]:
    q, L = len(values), sum(values)
    current = 0
    result = []
    for value in values:
        result.append(current)
        current += q * value - L
    if current:
        fail("height walk does not close")
    return tuple(result)


def canonical_turn(values: tuple[int, ...]) -> tuple[int, ...]:
    choices = [candidate for candidate in turns(values) if min(height_walk(candidate)) == 0]
    if not choices:
        fail("no minimum-height turn")
    if math.gcd(len(values), sum(values)) == 1 and len(choices) != 1:
        fail("coprime turn is not unique")
    return min(choices)


def residue_profile(values: tuple[int, ...]) -> tuple[int, ...]:
    q, L = len(values), sum(values)
    if math.gcd(q, L) != 1:
        fail("profile used at noncoprime slope")
    output: list[int | None] = [None] * q
    for height in height_walk(canonical_turn(values)):
        residue = height - q * (height // q)
        output[residue] = height // q
    if any(value is None or value < 0 for value in output) or output[0] != 0:
        fail("canonical residue profile")
    return tuple(int(value) for value in output)


def recover_word(q: int, L: int, profile: tuple[int, ...]) -> tuple[int, ...] | None:
    if len(profile) != q or profile[0] != 0 or any(value < 0 for value in profile) or math.gcd(q, L) != 1:
        return None
    path = [((-L * j) % q) + q * profile[(-L * j) % q] for j in range(q)]
    exponents = []
    for j, height in enumerate(path):
        following = path[j + 1] if j + 1 < q else 0
        delta = following - height + L
        quotient, remainder = divmod(delta, q)
        if remainder or quotient <= 0:
            return None
        exponents.append(quotient)
    answer = tuple(exponents)
    if residue_profile(answer) != profile:
        return None
    return answer


def correction(values: tuple[int, ...]) -> int:
    q = len(values)
    cumulative = 0
    answer = 0
    for position in range(q):
        answer += pow(3, q - position - 1) * pow(2, cumulative)
        cumulative += values[position]
    return answer


def two_valuation(value: int) -> int:
    if value == 0:
        fail("zero valuation")
    value = abs(value)
    answer = 0
    while value % 2 == 0:
        answer += 1
        value //= 2
    return answer


def literal(source: int, values: tuple[int, ...]) -> tuple[bool, list[int]]:
    trace = [source]
    current = source
    for exponent in values:
        numerator = 3 * current + 1
        if two_valuation(numerator) != exponent:
            return False, trace
        current = numerator // pow(2, exponent)
        trace.append(current)
    return current == source, trace


def determinant(matrix: list[list[int]]) -> int:
    data = [row[:] for row in matrix]
    n = len(data)
    if n == 0:
        return 1
    sign = 1
    denominator = 1
    for column in range(n - 1):
        selected = None
        for row in range(column, n):
            if data[row][column] != 0:
                selected = row
                break
        if selected is None:
            return 0
        if selected != column:
            data[column], data[selected] = data[selected], data[column]
            sign = -sign
        pivot = data[column][column]
        next_data = [row[:] for row in data]
        for row in range(column + 1, n):
            for col in range(column + 1, n):
                numerator = data[row][col] * pivot - data[row][column] * data[column][col]
                quotient, remainder = divmod(numerator, denominator)
                if remainder:
                    fail("Sylvester determinant division")
                next_data[row][col] = quotient
            next_data[row][column] = 0
        data = next_data
        denominator = pivot
    return sign * data[-1][-1]


def sylvester_resultant(profile: tuple[int, ...]) -> int:
    q = len(profile)
    f = [1] + [0] * (q - 1) + [-2]
    g = list(reversed([pow(2, entry) for entry in profile]))
    m, n = q, q - 1
    size = m + n
    matrix: list[list[int]] = []
    for shift in range(n):
        matrix.append([0] * shift + f + [0] * (size - shift - len(f)))
    for shift in range(m):
        matrix.append([0] * shift + g + [0] * (size - shift - len(g)))
    return determinant(matrix)


def egcd(a: int, b: int) -> tuple[int, int, int]:
    if b == 0:
        return a, 1, 0
    gcd, x, y = egcd(b, a % b)
    return gcd, y, x - (a // b) * y


def signed_mod_power(base: int, exponent: int, modulus: int) -> int:
    if exponent < 0:
        base = pow(base, -1, modulus)
        exponent = -exponent
    return pow(base, exponent, modulus)


def gamma_for(q: int, L: int, modulus: int) -> int:
    gcd, u, v = egcd(q, L)
    if gcd != 1 or modulus <= 1:
        fail("gamma domain")
    return signed_mod_power(2, u, modulus) * signed_mod_power(3, v, modulus) % modulus


def radial_coefficients(profile: tuple[int, ...]) -> tuple[int, ...]:
    shifted = [pow(2, value) - 1 for value in profile]
    answer = [1 + 2 * shifted[-1]]
    answer.extend(shifted[index - 1] - shifted[index] for index in range(1, len(shifted)))
    return tuple(answer)


def upper_root(q: int, precision: int = 48) -> Fraction:
    scale = pow(2, precision)
    a, b = scale, 4 * scale
    target = 4 * pow(scale, q)
    while a + 1 < b:
        candidate = (a + b) // 2
        if pow(candidate, q) >= target:
            b = candidate
        else:
            a = candidate
    upper = Fraction(b, scale)
    if pow(b, q) < target or pow(b - 1, q) >= target:
        fail("root enclosure")
    return upper


def energy_bound(profile: tuple[int, ...], D: int) -> tuple[Fraction, bool]:
    x = upper_root(len(profile))
    total = Fraction()
    power = Fraction(1)
    for coefficient in radial_coefficients(profile):
        total += coefficient * coefficient * power
        power *= x
    return total, pow(total, len(profile)) < D * D


def row_for_profile(q: int, L: int, profile: tuple[int, ...]) -> list[object]:
    values = recover_word(q, L, profile)
    if values is None:
        fail("invalid finite profile")
    D = pow(2, L) - pow(3, q)
    B = correction(values)
    cmin = min(correction(candidate) for candidate in turns(values))
    energy, excluded = energy_bound(profile, D)
    return [q, L, list(profile), list(values), sum(profile), B, D, B % D == 0, cmin, cmin < V * D, excluded, str(energy.numerator), str(energy.denominator)]


def weak_profiles(q: int, area: int):
    if q == 1:
        if area == 0:
            yield (0,)
        return
    for choices in itertools.combinations_with_replacement(tuple(range(1, q)), area):
        row = [0] * q
        for choice in choices:
            row[choice] += 1
        yield tuple(row)


def rebuild_finite(stored: dict[str, object]) -> dict[str, int]:
    if stored.get("format") != "collatz-phase22-finite-profiles-v1" or stored.get("proves_collatz") is not False:
        fail("finite metadata or Collatz boundary")
    if stored.get("full_composition_scope") != {"q_maximum": 8, "q_lt_L_le_2q": True, "D_positive": True}:
        fail("full composition scope")
    full = []
    raw_count = 0
    coprime_count = 0
    noncoprime_count = 0
    integral = []
    keys: set[tuple[int, int, tuple[int, ...]]] = set()
    full_keys: set[tuple[int, int, tuple[int, ...]]] = set()
    for q in range(1, 9):
        for L in range(q + 1, 2 * q + 1):
            if pow(2, L) <= pow(3, q):
                continue
            classes = set()
            for values in positive_compositions(L, q):
                raw_count += 1
                classes.add(least_cyclic(values))
            for values in sorted(classes):
                D = pow(2, L) - pow(3, q)
                distinct_turns = tuple(dict.fromkeys(turns(values)))
                B_values = [correction(candidate) for candidate in distinct_turns]
                divisible = any(B % D == 0 for B in B_values)
                if divisible:
                    witnesses = []
                    for candidate, B in zip(distinct_turns, B_values):
                        if B % D == 0:
                            source = B // D
                            legal, trace = literal(source, candidate)
                            witnesses.append([list(candidate), source, legal, trace])
                    integral.append([q, L, list(values), witnesses])
                if math.gcd(q, L) == 1:
                    profile = residue_profile(values)
                    keys.add((q, L, profile))
                    full_keys.add((q, L, profile))
                    coprime_count += 1
                    full.append([q, L, list(values), list(profile), sum(profile), min(B_values), D, divisible])
                else:
                    noncoprime_count += 1
                    full.append([q, L, list(values), None, None, min(B_values), D, divisible])
    expected_full = {
        "full_raw_compositions": raw_count,
        "full_cyclic_classes": len(full),
        "full_coprime_classes": coprime_count,
        "full_noncoprime_classes": noncoprime_count,
        "full_integral_classes": integral,
        "full_row_digest_sha256": digest(full),
    }
    for key, expected in expected_full.items():
        if stored.get(key) != expected:
            fail(f"full finite audit: {key}")

    if stored.get("area_scope") != {"q_maximum": 22, "maximum_area": 2, "q_lt_L_le_2q": True, "D_positive": True, "coprime_only": True}:
        fail("area scope")
    area_rows = []
    counters: dict[int, dict[str, int]] = {}
    for q in range(1, 23):
        for L in range(q + 1, 2 * q + 1):
            if pow(2, L) <= pow(3, q) or math.gcd(q, L) != 1:
                continue
            for area in range(3):
                for profile in weak_profiles(q, area):
                    if recover_word(q, L, profile) is None:
                        continue
                    keys.add((q, L, profile))
                    row = row_for_profile(q, L, profile)
                    area_rows.append(row)
                    count = counters.setdefault(area, {"valid": 0, "energy_excluded": 0, "source_excluded": 0, "combined_excluded": 0, "uncovered": 0, "integral": 0})
                    count["valid"] += 1
                    count["energy_excluded"] += int(row[10])
                    count["source_excluded"] += int(row[9])
                    count["combined_excluded"] += int(row[9] or row[10])
                    count["uncovered"] += int(not row[9] and not row[10])
                    count["integral"] += int(row[7])
    area_rows.sort(key=lambda row: (row[0], row[1], row[4], row[2]))
    uncovered = [row for row in area_rows if not row[9] and not row[10]]
    checks = {
        "area_profile_count": len(area_rows),
        "area_counts": {str(key): value for key, value in sorted(counters.items())},
        "area_row_digest_sha256": digest(area_rows),
        "smallest_combined_uncovered_profile": uncovered[0] if uncovered else None,
        "combined_uncovered_count": len(uncovered),
    }
    for key, expected in checks.items():
        if stored.get(key) != expected:
            fail(f"area finite audit: {key}")

    larger = sorted(keys - full_keys)
    sample_keys = sorted(full_keys) + list(dict.fromkeys(larger[:256] + larger[-256:]))
    samples = stored.get("resultant_samples")
    if not isinstance(samples, list) or len(samples) != len(sample_keys) or stored.get("resultant_sample_count") != len(sample_keys):
        fail("resultant sample count")
    expected_samples = []
    for q, L, profile in sample_keys:
        values = recover_word(q, L, profile)
        if values is None:
            fail("sample reconstruction")
        B = correction(values)
        D = pow(2, L) - pow(3, q)
        resultant = sylvester_resultant(profile)
        root_data = None
        if D > 1:
            gamma = gamma_for(q, L, D)
            polynomial = sum(pow(2, value) * pow(gamma, index, D) for index, value in enumerate(profile)) % D
            root_data = [gamma, pow(gamma, q, D), pow(gamma, L, D), polynomial]
            if root_data[1] != 2 % D or root_data[2] != 3 % D or ((polynomial == 0) != (B % D == 0)):
                fail("modular slope root")
        if B % D == 0 and resultant % D:
            fail("resultant divisibility")
        expected_samples.append([q, L, list(profile), B, D, resultant, root_data])
    if samples != expected_samples:
        fail("independent Sylvester resultants")
    return {"full_classes": len(full), "area_profiles": len(area_rows), "resultant_samples": len(sample_keys), "survivors": len(uncovered)}


def log_interval(x: Fraction, terms: int = 24) -> tuple[Fraction, Fraction]:
    if x < 1:
        fail("log interval domain")
    z = (x - 1) / (x + 1)
    square = z * z
    term = z
    partial = Fraction()
    for k in range(terms):
        partial += term / (2 * k + 1)
        term *= square
    low = 2 * partial
    high = low + 2 * term / ((2 * terms + 1) * (1 - square))
    return low, high


def verify_theory(value: dict[str, object]) -> None:
    if value.get("format") != "collatz-phase22-theory-v1" or value.get("proves_collatz") is not False:
        fail("theory Collatz boundary")
    expected_statuses = {"P133": "VERIFIED_THEOREM", "P134": "VERIFIED_THEOREM", "P135": "VERIFIED_THEOREM", "P136": "VERIFIED_THEOREM", "P137": "VERIFIED_THEOREM", "P138": "VERIFIED_THEOREM", "P139": "CONDITIONAL", "P140": "VERIFIED_THEOREM", "H133": "OPEN"}
    claims = value.get("claims")
    if not isinstance(claims, dict) or {key: row.get("status") if isinstance(row, dict) else None for key, row in claims.items()} != expected_statuses:
        fail("theory claim statuses")
    checks = value.get("exact_checks")
    if not isinstance(checks, dict):
        fail("theory exact checks")
    ln2_low, ln2_high = log_interval(Fraction(2))
    _, ratio_high = log_interval(Fraction(511, 256))
    margin = ln2_low - Fraction(1, V) - (8 * ln2_high + ratio_high) / 9
    if margin <= 0 or decode_fraction(checks.get("g170_log_margin")) != margin:
        fail("G170 logarithm certificate")
    if decode_fraction(checks.get("ln2_lower")) != ln2_low or decode_fraction(checks.get("ln2_upper")) != ln2_high or decode_fraction(checks.get("ln_511_over_256_upper")) != ratio_high:
        fail("logarithm enclosure metadata")
    if checks.get("critical_root_check") is not True or not (4 * pow(8, 13) < pow(9, 13)):
        fail("area-one root check")
    if checks.get("critical_resultant_check") is not True or not (4 * pow(115625, 13) < pow(131072, 13)):
        fail("area-one critical comparison")
    if checks.get("noncritical_q4_check") is not True or not (2 * pow(11, 2) < pow(18, 2)):
        fail("area-one noncritical comparison")


def verify_regressions(value: dict[str, object]) -> None:
    if value.get("format") != "collatz-phase22-regressions-v1" or value.get("proves_collatz") is not False:
        fail("regression Collatz boundary")
    rows = value.get("named_cycle_words")
    if not isinstance(rows, list) or len(rows) != 30:
        fail("named regression count")
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("exponents"), list):
            fail("regression row")
        exponents = tuple(int(item) for item in row["exponents"])
        q, L = len(exponents), sum(exponents)
        D = pow(2, L) - pow(3, q)
        B = correction(exponents)
        source = B // D if D and B % D == 0 else None
        legal = trace = None
        if source is not None:
            legal, trace = literal(source, exponents)
        profile = result = divides = None
        if math.gcd(q, L) == 1:
            profile_tuple = residue_profile(canonical_turn(exponents))
            profile = list(profile_tuple)
            result = sylvester_resultant(profile_tuple)
            divides = result % abs(D) == 0 if D else None
        expected = {"q": q, "L": L, "D": D, "B": B, "integral_source": source, "literal_legal": legal, "orbit_values": trace, "coprime_profile": profile, "resultant": result, "D_divides_resultant": divides}
        for key, item in expected.items():
            if row.get(key) != item:
                fail(f"regression arithmetic: {row.get('name')} {key}")
    names = [row.get("name") for row in rows]
    if names[:5] != ["trivial-positive", "negative-q2-L3", "negative-q7-L11-D-139", "A=11101", "B=1100"]:
        fail("mandatory named regressions")
    for required in ("legacy-macro-id0", "legacy-NG28-short", "legacy-NG28-long", "legacy-NG30-k2", "legacy-NG30-k3", "legacy-NG30-k4"):
        if required not in names:
            fail(f"missing legacy regression: {required}")
    q7 = rows[2]
    if q7.get("D") != -139 or q7.get("integral_source") != -17 or q7.get("literal_legal") is not True or q7.get("D_divides_resultant") is not True:
        fail("negative-cycle falsifier")
    numeric = value.get("numeric_prefix_controls")
    if not isinstance(numeric, list) or len(numeric) != 22:
        fail("numeric controls")
    for stored in numeric:
        family, m, source, _, _, _ = stored
        expected_source = pow(2, m) - 1 if family == "2^m-1" else pow(8, m) - 5
        if source != expected_source:
            fail("numeric family source")
        current = source
        visited = set()
        steps = 0
        while steps < 256 and current not in visited and current != 1:
            visited.add(current)
            current = current // 2 if current % 2 == 0 else (3 * current + 1) // 2
            steps += 1
        if stored != [family, m, source, steps, current, current == 1]:
            fail("numeric family trajectory")


def verify_literature(value: dict[str, object]) -> None:
    if value.get("format") != "collatz-phase22-literature-v1" or value.get("proves_collatz") is not False:
        fail("literature boundary")
    if value.get("claims") != {"EXT15": "EXTERNAL_THEOREM", "EXT16": "EXTERNAL_THEOREM", "EXT05": "EXTERNAL_THEOREM"}:
        fail("literature statuses")
    sources = value.get("sources")
    if not isinstance(sources, list) or len(sources) != 4:
        fail("literature source list")
    serialized = json.dumps(sources, sort_keys=True)
    for required in ("arXiv:2607.24844v1", "Theorem 7.3", "10.1016/j.disc.2025.114812", "Lemma B.1", "q>12", "Eisenstein"):
        if required not in serialized:
            fail(f"literature source boundary: {required}")


def verify_obstruction(path: Path, counts: dict[str, int]) -> None:
    text = path.read_text(encoding="utf-8")
    for required in ("q<=8", "q<=22", "area at most two", "not a cycle", "proves_collatz=false"):
        if required not in text:
            fail(f"obstruction report boundary: {required}")
    if str(counts["full_classes"]) not in text or str(counts["area_profiles"]) not in text or str(counts["survivors"]) not in text:
        fail("obstruction report finite counts")


def verify(directory: Path) -> dict[str, object]:
    for name in FILES:
        if not (directory / name).is_file():
            fail(f"missing {name}")
    theory = load(directory / FILES[0])
    finite = load(directory / FILES[1])
    regressions = load(directory / FILES[2])
    literature = load(directory / FILES[3])
    verify_theory(theory)
    counts = rebuild_finite(finite)
    verify_regressions(regressions)
    verify_literature(literature)
    verify_obstruction(directory / FILES[4], counts)
    return {
        "valid": True,
        "claims": {"P133": "VERIFIED_THEOREM", "P134": "VERIFIED_THEOREM", "P135": "VERIFIED_THEOREM", "P136": "VERIFIED_THEOREM", "P137": "VERIFIED_THEOREM", "P138": "VERIFIED_THEOREM", "P139": "CONDITIONAL", "P140": "VERIFIED_THEOREM", "E34": "VERIFIED_FINITE", "H133": "OPEN"},
        "finite": counts,
        "resultant_method": "independent Sylvester determinant",
        "generator_imported": False,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--write-report", type=Path)
    args = parser.parse_args()
    try:
        report = verify(args.artifact_dir)
    except (OSError, ValueError) as exc:
        print(f"phase22 verification failed: {exc}", file=sys.stderr)
        return 1
    if args.write_report:
        save(args.write_report, report)
    print(json.dumps(report, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
