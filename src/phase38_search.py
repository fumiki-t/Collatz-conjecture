#!/usr/bin/env python3
"""Generate exact Phase 38 finite-capacity and renewal-transfer evidence.

The Phase 38 note is an untrusted proposal.  This generator emits exact
integer/rational certificates and bounded convention checks; theorem proofs
are written separately and are reconstructed by an implementation-independent
verifier.  Floating point is not used for any acceptance decision.
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
from typing import Sequence


if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


MAX_CAPACITY_N = 500
RECIPROCAL_START_N = 49
PRIVATE_ROW_DIGEST = "82a7d14974ec02b3f030c895caf73e1564d92a5c003c00614bdf30bb65f5a60f"
MANDATORY_FAMILIES = (
    "2^m-1",
    "8^m-5",
    "(110|111)^*",
    "A=11101",
    "B=1100",
    "A^rB^s",
)

CLAIMS = {
    "P227": "VERIFIED_THEOREM",
    "P228": "VERIFIED_THEOREM",
    "E54": "VERIFIED_FINITE",
    "P229": "VERIFIED_THEOREM",
    "P230": "CONDITIONAL",
    "P231": "VERIFIED_THEOREM",
    "P232": "VERIFIED_THEOREM",
    "P233": "VERIFIED_THEOREM",
    "P234": "VERIFIED_THEOREM",
    "H72": "OPEN",
    "H133": "OPEN",
}


def write_json(path: Path, value: object) -> None:
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def stable_hash(rows: object) -> str:
    payload = json.dumps(rows, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(payload).hexdigest()


def fraction_row(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def ceil_log2(value: int) -> int:
    if value < 1:
        raise ValueError("positive integer required")
    return (value - 1).bit_length()


def fixed_weight_capacity(length: int, weight: int, interval_size: int | None = None) -> int:
    """Return Y_(N,s)(X) from the exact affine-extrema span."""
    if not 0 <= weight <= length:
        raise ValueError("weight outside word")
    size = 1 << length if interval_size is None else interval_size
    if not 1 <= size <= 1 << length:
        raise ValueError("interval size outside [1,2^N]")
    power_three = 3**weight
    power_two_weight = 1 << weight
    span_numerator = (
        power_three * (size - 1)
        + ((1 << (length - weight)) - 1) * (power_three - power_two_weight)
    )
    return 1 + span_numerator // (1 << length)


def capacity_rows(maximum_n: int = MAX_CAPACITY_N) -> tuple[list[int], list[int], list[list[object]]]:
    """Compute the general and odd-source recursive upper capacities exactly."""
    general = [1]
    odd = [1]
    rows: list[list[object]] = [[0, "1", "1"]]
    for length in range(1, maximum_n + 1):
        general_total = 0
        odd_total = 0
        for weight in range(length + 1):
            image_capacity = fixed_weight_capacity(length, weight)
            image_scale = ceil_log2(image_capacity)
            word_count = math.comb(length, weight)
            general_total += (
                min(word_count, general[image_scale])
                if image_scale < length
                else word_count
            )
            if weight:
                odd_word_count = math.comb(length - 1, weight - 1)
                odd_total += (
                    min(odd_word_count, general[image_scale])
                    if image_scale < length
                    else odd_word_count
                )
        general.append(general_total)
        odd.append(odd_total)
        rows.append([length, str(general_total), str(odd_total)])
    return general, odd, rows


def word_affine(word: str) -> tuple[int, int]:
    """Return (odd count, B) for a literal full-shortcut parity word."""
    correction = 0
    odd_count = 0
    for position, bit in enumerate(word):
        if bit == "1":
            correction = 3 * correction + (1 << position)
            odd_count += 1
        elif bit != "0":
            raise ValueError("binary word required")
    return odd_count, correction


def canonical_source(word: str) -> int:
    odd_count, correction = word_affine(word)
    modulus = 1 << len(word)
    residue = (-correction * pow(3**odd_count, -1, modulus)) % modulus
    return residue or modulus


def realize_word(source: int, word: str) -> tuple[bool, int]:
    value = source
    for bit in word:
        if str(value & 1) != bit:
            return False, value
        value = (3 * value + 1) // 2 if bit == "1" else value // 2
    return True, value


def shortcut_trace(source: int, steps: int) -> tuple[list[int], str]:
    values = [source]
    bits = []
    for _ in range(steps):
        bit = values[-1] & 1
        bits.append(str(bit))
        values.append((3 * values[-1] + 1) // 2 if bit else values[-1] // 2)
    return values, "".join(bits)


def translated_interval_audit(maximum_n: int = 10) -> dict[str, object]:
    rows: list[list[object]] = []
    source_count = 0
    group_count = 0
    case_count = 0
    for length in range(1, maximum_n + 1):
        modulus = 1 << length
        starts = (1, modulus + 3, 10**24 + 37 * length, (1 << 120) + 19 * length)
        widths = sorted({1, 1 << (length // 2), 1 << (length - 1), modulus})
        for start, width in itertools.product(starts, widths):
            buckets: dict[int, list[int]] = {}
            for source in range(start, start + width):
                trace, word = shortcut_trace(source, length)
                buckets.setdefault(word.count("1"), []).append(trace[-1])
                source_count += 1
            for weight in sorted(buckets):
                images = buckets[weight]
                distinct = sorted(set(images))
                bound = fixed_weight_capacity(length, weight, width)
                b_min = 3**weight - 2**weight
                b_max = (1 << (length - weight)) * b_min
                lower = 3**weight * start + b_min
                upper = 3**weight * (start + width - 1) + b_max
                if any(not lower <= image * modulus <= upper for image in distinct):
                    raise AssertionError("fixed-weight image left the exact affine interval")
                if len(distinct) > bound:
                    raise AssertionError("fixed-weight integer image capacity exceeded")
                rows.append([
                    length,
                    str(start),
                    width,
                    weight,
                    len(images),
                    len(distinct),
                    str(distinct[0]),
                    str(distinct[-1]),
                    str(bound),
                ])
                group_count += 1
            case_count += 1
    return {
        "maximum_N": maximum_n,
        "cases": case_count,
        "sources": source_count,
        "fixed_weight_groups": group_count,
        "rows_digest_sha256": stable_hash(rows),
        "selected_rows": rows[:8] + rows[-8:],
    }


def capacity_certificate() -> dict[str, object]:
    general, odd, rows = capacity_rows()
    partial = sum((Fraction(odd[length], 1 << length) for length in range(49, 501)), Fraction())
    tail = Fraction(1440 * 44**501, 45**501)
    total = partial + tail
    stated_bound = Fraction(2079, 1000)
    log_lower = Fraction(842, 1215)
    if not total < stated_bound < 3 * log_lower:
        raise AssertionError("reciprocal certificate failed")
    if not 2 * 44**30 > 45**30:
        raise AssertionError("geometric-tail comparison failed")

    selected_indices = (0, 1, 2, 3, 10, 20, 30, 40, 48, 49, 50, 100, 500)
    row_digest = stable_hash(rows)
    return {
        "format": "collatz-phase38-capacity-certificate-v1",
        "claims": {
            "P227": CLAIMS["P227"],
            "P228": CLAIMS["P228"],
            "E54": CLAIMS["E54"],
            "P229": CLAIMS["P229"],
            "P230": CLAIMS["P230"],
        },
        "fixed_weight_formula": {
            "Y_N_s_X": "1+floor((3^s*(X-1)+(2^(N-s)-1)*(3^s-2^s))/2^N)",
            "domain": "N>=0, 0<=s<=N, 1<=X<=2^N",
            "meaning": "number of integers in the common affine image interval; an upper bound, not a claim of attainability",
        },
        "recurrences": {
            "A_0": 1,
            "O_0_convention": 1,
            "m_N_s": "ceil(log2(Y_N_s(2^N)))",
            "A_N": "sum_s min(binomial(N,s),A_m) when m<N, otherwise binomial(N,s)",
            "O_N": "sum_(s>=1) min(binomial(N-1,s-1),A_m) when m<N, otherwise binomial(N-1,s-1)",
            "odd_image_recursion_uses": "A_m, because time-N images need not be odd",
        },
        "rows": rows,
        "row_encoding": "UTF-8 compact JSON of rows [N,decimal(A_N),decimal(O_N)] with decimal values stored as strings, separators ',' and ':' and no trailing newline",
        "rows_digest_sha256": row_digest,
        "selected_rows": [rows[index] for index in selected_indices],
        "private_digest_diagnostic": {
            "supplied_target_sha256": PRIVATE_ROW_DIGEST,
            "reconstructed_canonical_sha256": row_digest,
            "matches": row_digest == PRIVATE_ROW_DIGEST,
            "acceptance_role": "none; the supplied note did not define its serialization",
        },
        "translated_interval_audit": translated_interval_audit(),
        "reciprocal_certificate": {
            "finite_sum_N49_to_N500": fraction_row(partial),
            "tail_majorant": fraction_row(tail),
            "combined": fraction_row(total),
            "combined_bound": fraction_row(stated_bound),
            "log2_lower_bound": fraction_row(log_lower),
            "geometric_comparison": "2*44^30>45^30",
            "relations": [
                "combined<2079/1000",
                "2079/1000<842/405",
                "842/405=3*(842/1215)<3*log(2)",
            ],
        },
        "cycle_consequences": {
            "unconditional": "every primitive positive noncritical cycle has minimum m<2^49",
            "conditional_on_X02": "every primitive positive cycle is critical, L=ceil(q*log2(3))",
            "X02_status": "EXTERNAL_EVIDENCE",
            "trivial_cycle": "critical and not excluded",
        },
        "floating_point_used_for_acceptance": False,
        "proves_collatz": False,
    }


def first_upcrossing(code: str) -> bool:
    odd_count = 0
    for length, bit in enumerate(code, 1):
        odd_count += bit == "1"
        if length < len(code) and 3**odd_count > 1 << length:
            return False
    return 3**odd_count > 1 << len(code)


def renewal_blocks(maximum_length: int = 14) -> list[dict[str, object]]:
    blocks = []
    for length in range(1, maximum_length + 1):
        for bits in itertools.product("01", repeat=length):
            code = "".join(bits)
            if first_upcrossing(code):
                forward = code[::-1]
                odd_count, correction = word_affine(forward)
                coefficient = Fraction(3**odd_count, 1 << length)
                threshold = Fraction(correction + (1 << length), 3**odd_count)
                remainder = threshold - 1
                normalized_numerator = correction + (1 << length) - 3**odd_count
                if normalized_numerator % 4:
                    raise AssertionError("normalized correction is not integral")
                normalized = normalized_numerator // 4
                initial_run = len(forward) - len(forward.lstrip("1"))
                if forward == "1":
                    if remainder or normalized:
                        raise AssertionError("one-block threshold")
                elif remainder < Fraction(4, 9):
                    raise AssertionError("universal companion threshold")
                blocks.append({
                    "code": code,
                    "forward": forward,
                    "L": length,
                    "q": odd_count,
                    "B": correction,
                    "c": coefficient,
                    "R": threshold,
                    "r": remainder,
                    "Cw": normalized,
                    "initial_run": initial_run,
                })
    return sorted(blocks, key=lambda block: (int(block["L"]), str(block["code"])))


def v2(value: int) -> int:
    if value == 0:
        raise ValueError("v2(0) is not used")
    value = abs(value)
    return (value & -value).bit_length() - 1


def address_specs(blocks: Sequence[dict[str, object]]) -> list[tuple[str, ...]]:
    codes = [str(block["code"]) for block in blocks]
    first_twelve = codes[:12]
    first_five = codes[:5]
    specs = [(code,) for code in codes]
    specs.extend(itertools.product(first_twelve, repeat=2))
    specs.extend(itertools.product(first_five, repeat=3))
    return sorted(set(specs), key=lambda item: (len(item), sum(map(len, item)), item))


def renewal_transfer_audit() -> dict[str, object]:
    blocks = renewal_blocks()
    by_code = {str(block["code"]): block for block in blocks}
    specs = address_specs(blocks)
    rows: list[list[object]] = []
    valuation_rows: list[list[object]] = []
    transition_count = 0
    nontrivial_count = 0

    for codes in specs:
        chosen = [by_code[code] for code in codes]
        forward = "".join(str(block["forward"]) for block in chosen)
        source = canonical_source(forward)
        valid, endpoint = realize_word(source, forward)
        if not valid:
            raise AssertionError("canonical address source does not realize its word")

        cumulative = [Fraction(1)]
        transfer_terms = []
        for block in chosen:
            transfer_terms.append(Fraction(block["r"]) / cumulative[-1])
            cumulative.append(cumulative[-1] * Fraction(block["c"]))
        initial_h = sum(transfer_terms, Fraction()) + 1

        current_a = Fraction(source + 1)
        current_h = initial_h
        cumulative_length = 0
        cumulative_weight = 0
        zeta_mass = Fraction()
        valuation_profile = []
        offset = 0
        for index, block in enumerate(chosen):
            coefficient = Fraction(block["c"])
            remainder = Fraction(block["r"])
            if not 0 <= remainder < current_h:
                raise AssertionError("finite companion legality")
            next_a = coefficient * (current_a + remainder)
            next_h = coefficient * (current_h - remainder)
            if next_a.denominator != 1 or next_h <= 0:
                raise AssertionError("renewal transition integrality/positivity")
            segment = str(block["forward"])
            segment_source = int(current_a) - 1
            segment_valid, segment_endpoint = realize_word(segment_source, segment)
            if not segment_valid or segment_endpoint + 1 != next_a:
                raise AssertionError("renewal block affine transition")
            zeta_now = current_h / (current_a + current_h)
            zeta_next = next_h / (next_a + next_h)
            mass = remainder / (current_a + current_h)
            if zeta_now - zeta_next != mass:
                raise AssertionError("threshold-mass identity")
            zeta_mass += mass

            term = transfer_terms[index]
            if remainder:
                if term.denominator % 2 == 0:
                    raise AssertionError("transfer term has even denominator")
                expected_valuation = cumulative_length + int(block["initial_run"])
                observed_valuation = v2(term.numerator)
                if observed_valuation != expected_valuation:
                    raise AssertionError("transfer valuation rule")
                valuation_profile.append(observed_valuation)
                valuation_rows.append([
                    list(codes), index, cumulative_length,
                    int(block["initial_run"]), observed_valuation,
                ])
                nontrivial_count += 1

            cumulative_length += int(block["L"])
            cumulative_weight += int(block["q"])
            normalized_a = next_a / cumulative[index + 1]
            expected_normalized = Fraction((1 << cumulative_length) * int(next_a), 3**cumulative_weight)
            if normalized_a != expected_normalized:
                raise AssertionError("normalized source identity")
            if v2(normalized_a.numerator) < cumulative_length or normalized_a.denominator % 2 == 0:
                raise AssertionError("2-adic source approximation")
            current_a, current_h = next_a, next_h
            offset += len(segment)
            transition_count += 1

        final_zeta = current_h / (current_a + current_h)
        initial_zeta = initial_h / (Fraction(source + 1) + initial_h)
        if initial_zeta - final_zeta != zeta_mass:
            raise AssertionError("finite telescoping identity")
        transfer_sum = sum(transfer_terms, Fraction())
        if transfer_sum != initial_h - current_h / cumulative[-1]:
            raise AssertionError("block transfer series identity")
        if endpoint + 1 != current_a:
            raise AssertionError("address endpoint mismatch")

        rows.append([
            list(codes),
            forward,
            str(source),
            str(endpoint),
            str(initial_h.numerator),
            str(initial_h.denominator),
            str(current_a.numerator),
            str(current_h.numerator),
            str(current_h.denominator),
            cumulative_length,
            cumulative_weight,
            valuation_profile,
        ])

    return {
        "format": "collatz-phase38-renewal-transfer-v1",
        "claims": {
            "P231": CLAIMS["P231"],
            "P232": CLAIMS["P232"],
            "P233": CLAIMS["P233"],
            "P234": CLAIMS["P234"],
            "H72": CLAIMS["H72"],
        },
        "coordinates": {
            "A": "S+1",
            "H": "h-1",
            "r": "R-1",
            "transition": ["A'=c(A+r)", "H'=c(H-r)"],
            "legality": "0<=r<H",
            "total": "A'+H'=c(A+H)",
        },
        "theorem_statements": {
            "threshold_mass": "zeta_i-zeta_(i+1)=r_i/(A_i+H_i), and zeta_i=sum_(k>=i) r_k/(A_k+H_k)",
            "source_weights": "sum 1/A_i<infinity, sum r_i/A_i<infinity, and sum R_i/(S_i+1)<infinity",
            "companion_weights": "sum r_i/H_i=infinity",
            "real_transfer": "sum r_i/C_i=H_0 and A_i/C_i tends to A_0+H_0 over the reals",
            "two_adic_transfer": "sum r_i/C_i=-A_0 in Q_2 and A_i/C_i tends to zero in Q_2",
            "renewal_defect": "a_(n_i)>=(30/29)log2(i+1)-O_(S_0)(1) at every renewal boundary",
        },
        "proof_dependencies": {
            "all_scale": ["P76", "P77", "P79", "P220", "P222", "P224"],
            "two_adic_term_valuation": "v2(r_i/C_i)=L_<i+initial_one_run_i for each nontrivial block",
            "completion_warning": "real and Q_2 limits are taken in different completions and need not agree",
        },
        "finite_audit": {
            "maximum_code_length": 14,
            "codeword_count": len(blocks),
            "address_count": len(specs),
            "transition_count": transition_count,
            "nonzero_transfer_count": nontrivial_count,
            "address_digest_sha256": stable_hash(rows),
            "valuation_digest_sha256": stable_hash(valuation_rows),
            "selected_addresses": rows[:8] + rows[-8:],
        },
        "what_this_result_does_not_prove": "The exact transfer and opposite summability regimes do not exclude an infinite permanent-safe positive orbit, prove P80, or prove H72.",
        "floating_point_used_for_acceptance": False,
        "proves_collatz": False,
    }


def regression_artifact() -> dict[str, object]:
    source_rows = []
    for family, values in (
        ("2^m-1", [(1 << exponent) - 1 for exponent in range(2, 14)]),
        ("8^m-5", [8**exponent - 5 for exponent in range(1, 8)]),
    ):
        for source in values:
            steps = 24
            trace, word = shortcut_trace(source, steps)
            odd_count, correction = word_affine(word)
            if trace[-1] * (1 << steps) != 3**odd_count * source + correction:
                raise AssertionError("adversarial affine trace")
            source_rows.append([family, str(source), word, str(trace[-1]), odd_count, str(correction)])

    words = {
        "A=11101": "11101",
        "B=1100": "1100",
        "W=AB": "111011100",
        "(110|111)^*-1": "110111110",
        "(110|111)^*-2": "111110111110",
    }
    for r in range(1, 5):
        for s in range(1, 5):
            words[f"A^{r}B^{s}"] = "11101" * r + "1100" * s
    word_rows = []
    for label, word in sorted(words.items()):
        odd_count, correction = word_affine(word)
        source = canonical_source(word)
        valid, endpoint = realize_word(source, word)
        if not valid or endpoint * (1 << len(word)) != 3**odd_count * source + correction:
            raise AssertionError("adversarial word reconstruction")
        minimum = 3**odd_count - 2**odd_count
        maximum = (1 << (len(word) - odd_count)) * minimum
        if not minimum <= correction <= maximum:
            raise AssertionError("adversarial affine extremum")
        word_rows.append([
            label, word, len(word), odd_count, str(correction), str(source), str(endpoint),
            str(fixed_weight_capacity(len(word), odd_count)),
        ])

    w_word = "111011100"
    w_q, w_b = word_affine(w_word)
    if (len(w_word), w_q, w_b) != (9, 6, 817):
        raise AssertionError("A/B mandatory counterexample convention")
    if Fraction(-w_b, 3**w_q - (1 << len(w_word))) != Fraction(-817, 217):
        raise AssertionError("A/B fixed point")

    trivial_trace, trivial_word = shortcut_trace(1, 2)
    if trivial_trace != [1, 2, 1] or trivial_word != "10":
        raise AssertionError("trivial cycle convention")

    return {
        "format": "collatz-phase38-regressions-v1",
        "mandatory_families": list(MANDATORY_FAMILIES),
        "source_rows_digest_sha256": stable_hash(source_rows),
        "word_rows_digest_sha256": stable_hash(word_rows),
        "source_row_count": len(source_rows),
        "word_row_count": len(word_rows),
        "selected_source_rows": source_rows[:4] + source_rows[-4:],
        "selected_word_rows": word_rows,
        "AB_witness": {
            "word": w_word,
            "map": "(729*x+817)/512",
            "fixed_point": "-817/217",
            "role": "mandatory adversarial regression; it is not a renewal-transfer contradiction",
        },
        "trivial_cycle": {"source": 1, "word": trivial_word, "trace": trivial_trace, "critical": True},
        "scope_controls": [
            "NG22 remains valid: different real and 2-adic completion limits are not contradictory.",
            "One-orbit capacity does not imply P80 address anti-concentration.",
            "Negative and formal 2-adic sources are not positive-cycle witnesses.",
            "The private row digest is diagnostic only.",
        ],
        "proves_collatz": False,
    }


def obstruction_report(canonical_digest: str) -> str:
    return f"""# Phase 38 boundary and obstacle report

The finite-capacity recursion and the renewal-transfer identities survive the
independent mathematical audit.  The supplied formula line containing
`2079/1000 < < 842/405` has been read as the evident typographical correction
`2079/1000 < 842/405`; the exact integer comparison is certified.

## Private digest diagnostic

The supplied private target is `{PRIVATE_ROW_DIGEST}`.  The repository now
defines a self-contained canonical row encoding and obtains
`{canonical_digest}`.  These values do not match.  Because the proposal did
not specify the private serialization and explicitly said the digest was not
acceptance evidence, no encoding or row values were altered to force a match.
The independent verifier reconstructs every row and the exact inequality
instead.

## Live obstacles

The explicit cutoff `m<2^49` covers only noncritical primitive positive
cycles.  The statement that every positive cycle is critical still depends on
X02, which remains `EXTERNAL_EVIDENCE`; the critical arbitrary-area branch is
open.

On the nonperiodic side, the same positive threshold digits are summable on
the ordinary-source scale and nonsummable on the companion scale.  Their
rational partial sums converge to different values over the reals and over
`Q_2`, but this is a completion split, not a contradiction.  A proof of H72
still needs a carry, denominator, ancestry, or ordinary-height mechanism.

## What this result does not prove

This phase does not prove P80, H72, H133, or the Collatz conjecture.  It does
not turn X02 into an internal theorem, exclude critical cycles, or show that a
formal/2-adic source is a positive ordinary integer.  `proves_collatz=false`.
"""


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    args = parser.parse_args()
    args.artifact_dir.mkdir(parents=True, exist_ok=True)

    capacity = capacity_certificate()
    renewal = renewal_transfer_audit()
    regressions = regression_artifact()
    write_json(args.artifact_dir / "phase38_capacity_certificate.json", capacity)
    write_json(args.artifact_dir / "phase38_renewal_transfer.json", renewal)
    write_json(args.artifact_dir / "phase38_regressions.json", regressions)
    (args.artifact_dir / "phase38_obstruction_report.md").write_text(
        obstruction_report(str(capacity["rows_digest_sha256"])), encoding="utf-8"
    )
    print(json.dumps({
        "valid": True,
        "capacity_rows": len(capacity["rows"]),
        "row_digest_sha256": capacity["rows_digest_sha256"],
        "private_digest_match": capacity["private_digest_diagnostic"]["matches"],
        "renewal_addresses": renewal["finite_audit"]["address_count"],
        "renewal_transitions": renewal["finite_audit"]["transition_count"],
        "proves_collatz": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
