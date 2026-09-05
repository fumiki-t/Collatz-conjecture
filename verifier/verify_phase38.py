#!/usr/bin/env python3
"""Independent exact verifier for Phase 38 evidence.

The verifier reconstructs every capacity row, finite translated-interval row,
renewal address, transfer valuation, and mandatory regression.  It deliberately
uses no project source module and treats the supplied private digest as a
non-acceptance diagnostic.
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


PRIVATE_TARGET = "82a7d14974ec02b3f030c895caf73e1564d92a5c003c00614bdf30bb65f5a60f"
FILES = (
    "phase38_capacity_certificate.json",
    "phase38_renewal_transfer.json",
    "phase38_regressions.json",
    "phase38_obstruction_report.md",
)
STATUSES = {
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
}
FAMILIES = ["2^m-1", "8^m-5", "(110|111)^*", "A=11101", "B=1100", "A^rB^s"]


class VerificationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise VerificationError(message)


def load_object(path: Path) -> dict[str, object]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise VerificationError(f"cannot read {path.name}: {exc}") from exc
    if not isinstance(value, dict):
        fail(f"{path.name} is not an object")
    return value


def file_digest(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def canonical_digest(value: object) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":")).encode("ascii")
    return hashlib.sha256(raw).hexdigest()


def encoded_fraction(value: Fraction) -> dict[str, str]:
    return {"numerator": str(value.numerator), "denominator": str(value.denominator)}


def binary_ceiling(value: int) -> int:
    if value <= 0:
        fail("nonpositive image count")
    exponent = 0
    capacity = 1
    while capacity < value:
        capacity *= 2
        exponent += 1
    return exponent


def image_integer_bound(length: int, weight: int, size: int) -> int:
    b_low = pow(3, weight) - pow(2, weight)
    b_high = pow(2, length - weight) * b_low
    real_span_numerator = pow(3, weight) * (size - 1) + b_high - b_low
    return real_span_numerator // pow(2, length) + 1


def reconstruct_capacity_rows(limit: int = 500) -> tuple[list[int], list[int], list[list[object]]]:
    all_sources = [1]
    odd_sources = [1]
    serialized: list[list[object]] = [[0, "1", "1"]]
    for length in range(1, limit + 1):
        next_all = 0
        next_odd = 0
        for weight in range(length + 1):
            y_value = image_integer_bound(length, weight, pow(2, length))
            smaller_length = binary_ceiling(y_value)
            vector_count = math.comb(length, weight)
            if smaller_length < length:
                next_all += min(vector_count, all_sources[smaller_length])
            else:
                next_all += vector_count
            if weight > 0:
                vector_count = math.comb(length - 1, weight - 1)
                if smaller_length < length:
                    next_odd += min(vector_count, all_sources[smaller_length])
                else:
                    next_odd += vector_count
        all_sources.append(next_all)
        odd_sources.append(next_odd)
        serialized.append([length, str(next_all), str(next_odd)])
    return all_sources, odd_sources, serialized


def affine_by_positions(word: str) -> tuple[int, int]:
    positions = [index for index, bit in enumerate(word) if bit == "1"]
    if any(bit not in "01" for bit in word):
        fail("nonbinary word")
    correction = 0
    for rank, position in enumerate(positions):
        correction += pow(2, position) * pow(3, len(positions) - rank - 1)
    return len(positions), correction


def residue_for_word(word: str) -> int:
    weight, correction = affine_by_positions(word)
    modulus = pow(2, len(word))
    return (-correction * pow(pow(3, weight), -1, modulus)) % modulus


def direct_orbit(source: int, steps: int) -> tuple[list[int], str]:
    values = [source]
    parity = []
    for _ in range(steps):
        current = values[-1]
        parity.append("1" if current % 2 else "0")
        values.append((3 * current + 1) // 2 if current % 2 else current // 2)
    return values, "".join(parity)


def interval_rows(limit: int = 10) -> dict[str, object]:
    rows: list[list[object]] = []
    cases = 0
    sources = 0
    groups = 0
    for length in range(1, limit + 1):
        modulus = pow(2, length)
        starts = [1, modulus + 3, pow(10, 24) + 37 * length, pow(2, 120) + 19 * length]
        widths = sorted(set([1, pow(2, length // 2), pow(2, length - 1), modulus]))
        all_words = [format(mask, f"0{length}b")[::-1] for mask in range(modulus)]
        for start in starts:
            for width in widths:
                buckets: dict[int, list[int]] = {}
                for word in all_words:
                    residue = residue_for_word(word)
                    source = start + ((residue - start) % modulus)
                    if source >= start + width:
                        continue
                    weight, correction = affine_by_positions(word)
                    endpoint_numerator = pow(3, weight) * source + correction
                    if endpoint_numerator % modulus:
                        fail("nonintegral parity-cylinder endpoint")
                    buckets.setdefault(weight, []).append(endpoint_numerator // modulus)
                    sources += 1
                for weight in sorted(buckets):
                    image_list = buckets[weight]
                    distinct = sorted(set(image_list))
                    bound = image_integer_bound(length, weight, width)
                    if len(distinct) > bound:
                        fail("translated image capacity")
                    rows.append([
                        length,
                        str(start),
                        width,
                        weight,
                        len(image_list),
                        len(distinct),
                        str(distinct[0]),
                        str(distinct[-1]),
                        str(bound),
                    ])
                    groups += 1
                cases += 1
    return {
        "maximum_N": limit,
        "cases": cases,
        "sources": sources,
        "fixed_weight_groups": groups,
        "rows_digest_sha256": canonical_digest(rows),
        "selected_rows": rows[:8] + rows[-8:],
    }


def expected_capacity() -> dict[str, object]:
    general, odd, rows = reconstruct_capacity_rows()
    finite_sum = Fraction()
    for length in range(49, 501):
        finite_sum += Fraction(odd[length], pow(2, length))
    tail = Fraction(1440 * pow(44, 501), pow(45, 501))
    combined = finite_sum + tail
    upper = Fraction(2079, 1000)
    logarithm_lower = Fraction(842, 1215)
    if not 2 * pow(44, 30) > pow(45, 30):
        fail("tail ratio inequality")
    if not combined < upper < 3 * logarithm_lower:
        fail("reciprocal inequality")
    chosen = [0, 1, 2, 3, 10, 20, 30, 40, 48, 49, 50, 100, 500]
    digest = canonical_digest(rows)
    return {
        "format": "collatz-phase38-capacity-certificate-v1",
        "claims": {name: STATUSES[name] for name in ("P227", "P228", "E54", "P229", "P230")},
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
        "rows_digest_sha256": digest,
        "selected_rows": [rows[index] for index in chosen],
        "private_digest_diagnostic": {
            "supplied_target_sha256": PRIVATE_TARGET,
            "reconstructed_canonical_sha256": digest,
            "matches": digest == PRIVATE_TARGET,
            "acceptance_role": "none; the supplied note did not define its serialization",
        },
        "translated_interval_audit": interval_rows(),
        "reciprocal_certificate": {
            "finite_sum_N49_to_N500": encoded_fraction(finite_sum),
            "tail_majorant": encoded_fraction(tail),
            "combined": encoded_fraction(combined),
            "combined_bound": encoded_fraction(upper),
            "log2_lower_bound": encoded_fraction(logarithm_lower),
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


def is_first_crossing(code: str) -> bool:
    ones = 0
    for position, bit in enumerate(code, 1):
        ones += bit == "1"
        if position != len(code) and pow(3, ones) > pow(2, position):
            return False
    return pow(3, ones) > pow(2, len(code))


def all_blocks(limit: int = 14) -> list[dict[str, object]]:
    blocks: list[dict[str, object]] = []
    for length in range(1, limit + 1):
        for mask in range(pow(2, length)):
            code = format(mask, f"0{length}b")
            if not is_first_crossing(code):
                continue
            forward = code[::-1]
            weight, correction = affine_by_positions(forward)
            c_value = Fraction(pow(3, weight), pow(2, length))
            r_value = Fraction(correction + pow(2, length) - pow(3, weight), pow(3, weight))
            numerator = correction + pow(2, length) - pow(3, weight)
            if numerator % 4:
                fail("block normalized numerator")
            run = 0
            for bit in forward:
                if bit != "1":
                    break
                run += 1
            if forward != "1" and r_value < Fraction(4, 9):
                fail("block threshold")
            blocks.append({
                "code": code,
                "forward": forward,
                "L": length,
                "q": weight,
                "B": correction,
                "c": c_value,
                "R": r_value + 1,
                "r": r_value,
                "Cw": numerator // 4,
                "initial_run": run,
            })
    return sorted(blocks, key=lambda item: (int(item["L"]), str(item["code"])))


def selected_addresses(blocks: Sequence[dict[str, object]]) -> list[tuple[str, ...]]:
    codes = [str(item["code"]) for item in blocks]
    result: set[tuple[str, ...]] = {(code,) for code in codes}
    for first in codes[:12]:
        for second in codes[:12]:
            result.add((first, second))
    for first in codes[:5]:
        for second in codes[:5]:
            for third in codes[:5]:
                result.add((first, second, third))
    return sorted(result, key=lambda item: (len(item), sum(len(code) for code in item), item))


def two_valuation(value: int) -> int:
    value = abs(value)
    count = 0
    while value % 2 == 0:
        value //= 2
        count += 1
    return count


def positive_source(word: str) -> int:
    residue = residue_for_word(word)
    return residue if residue else pow(2, len(word))


def expected_renewal() -> dict[str, object]:
    blocks = all_blocks()
    lookup = {str(block["code"]): block for block in blocks}
    addresses = selected_addresses(blocks)
    rows: list[list[object]] = []
    valuation_rows: list[list[object]] = []
    transitions = 0
    nonzero = 0

    for codes in addresses:
        chosen = [lookup[code] for code in codes]
        word = "".join(str(block["forward"]) for block in chosen)
        source = positive_source(word)
        full_trace, observed_word = direct_orbit(source, len(word))
        if observed_word != word:
            fail("address source parity")

        products = [Fraction(1)]
        terms = []
        for block in chosen:
            terms.append(Fraction(block["r"]) / products[-1])
            products.append(products[-1] * Fraction(block["c"]))
        h_start = sum(terms, Fraction()) + 1
        a_value = Fraction(source + 1)
        h_value = h_start
        total_length = 0
        total_weight = 0
        zeta_sum = Fraction()
        valuation_profile = []
        position = 0

        for index, block in enumerate(chosen):
            c_value = Fraction(block["c"])
            r_value = Fraction(block["r"])
            if not 0 <= r_value < h_value:
                fail("companion legality")
            a_next = c_value * (a_value + r_value)
            h_next = c_value * (h_value - r_value)
            segment = str(block["forward"])
            segment_trace, segment_word = direct_orbit(int(a_value) - 1, len(segment))
            if segment_word != segment or segment_trace[-1] + 1 != a_next:
                fail("block transition")
            before = h_value / (a_value + h_value)
            after = h_next / (a_next + h_next)
            mass = r_value / (a_value + h_value)
            if before - after != mass:
                fail("mass decrement")
            zeta_sum += mass

            term = terms[index]
            if term:
                if term.denominator % 2 == 0:
                    fail("even transfer denominator")
                wanted = total_length + int(block["initial_run"])
                actual = two_valuation(term.numerator)
                if actual != wanted:
                    fail("transfer valuation")
                valuation_profile.append(actual)
                valuation_rows.append([list(codes), index, total_length, int(block["initial_run"]), actual])
                nonzero += 1

            total_length += int(block["L"])
            total_weight += int(block["q"])
            normalized = a_next / products[index + 1]
            closed_form = Fraction(pow(2, total_length) * int(a_next), pow(3, total_weight))
            if normalized != closed_form:
                fail("normalized source")
            if two_valuation(normalized.numerator) < total_length or normalized.denominator % 2 == 0:
                fail("2-adic approximation")
            a_value = a_next
            h_value = h_next
            position += len(segment)
            transitions += 1

        if h_start / (Fraction(source + 1) + h_start) - h_value / (a_value + h_value) != zeta_sum:
            fail("finite mass telescope")
        if sum(terms, Fraction()) != h_start - h_value / products[-1]:
            fail("finite transfer telescope")
        if full_trace[-1] + 1 != a_value:
            fail("full address endpoint")
        rows.append([
            list(codes), word, str(source), str(full_trace[-1]),
            str(h_start.numerator), str(h_start.denominator),
            str(a_value.numerator), str(h_value.numerator), str(h_value.denominator),
            total_length, total_weight, valuation_profile,
        ])

    return {
        "format": "collatz-phase38-renewal-transfer-v1",
        "claims": {name: STATUSES[name] for name in ("P231", "P232", "P233", "P234", "H72")},
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
            "address_count": len(addresses),
            "transition_count": transitions,
            "nonzero_transfer_count": nonzero,
            "address_digest_sha256": canonical_digest(rows),
            "valuation_digest_sha256": canonical_digest(valuation_rows),
            "selected_addresses": rows[:8] + rows[-8:],
        },
        "what_this_result_does_not_prove": "The exact transfer and opposite summability regimes do not exclude an infinite permanent-safe positive orbit, prove P80, or prove H72.",
        "floating_point_used_for_acceptance": False,
        "proves_collatz": False,
    }


def expected_regressions() -> dict[str, object]:
    source_rows = []
    source_sets = [
        ("2^m-1", [pow(2, exponent) - 1 for exponent in range(2, 14)]),
        ("8^m-5", [pow(8, exponent) - 5 for exponent in range(1, 8)]),
    ]
    for family, sources in source_sets:
        for source in sources:
            trace, word = direct_orbit(source, 24)
            weight, correction = affine_by_positions(word)
            if trace[-1] * pow(2, 24) != pow(3, weight) * source + correction:
                fail("source regression affine identity")
            source_rows.append([family, str(source), word, str(trace[-1]), weight, str(correction)])

    words = {
        "A=11101": "11101",
        "B=1100": "1100",
        "W=AB": "111011100",
        "(110|111)^*-1": "110111110",
        "(110|111)^*-2": "111110111110",
    }
    for a_power in range(1, 5):
        for b_power in range(1, 5):
            words[f"A^{a_power}B^{b_power}"] = "11101" * a_power + "1100" * b_power
    word_rows = []
    for label, word in sorted(words.items()):
        weight, correction = affine_by_positions(word)
        source = positive_source(word)
        trace, observed = direct_orbit(source, len(word))
        if observed != word:
            fail("word regression parity")
        word_rows.append([
            label, word, len(word), weight, str(correction), str(source), str(trace[-1]),
            str(image_integer_bound(len(word), weight, pow(2, len(word)))),
        ])
    w_weight, w_correction = affine_by_positions("111011100")
    if (w_weight, w_correction) != (6, 817):
        fail("AB witness")
    if Fraction(-w_correction, pow(3, w_weight) - pow(2, 9)) != Fraction(-817, 217):
        fail("AB fixed point")
    trivial, parity = direct_orbit(1, 2)
    return {
        "format": "collatz-phase38-regressions-v1",
        "mandatory_families": FAMILIES,
        "source_rows_digest_sha256": canonical_digest(source_rows),
        "word_rows_digest_sha256": canonical_digest(word_rows),
        "source_row_count": len(source_rows),
        "word_row_count": len(word_rows),
        "selected_source_rows": source_rows[:4] + source_rows[-4:],
        "selected_word_rows": word_rows,
        "AB_witness": {
            "word": "111011100",
            "map": "(729*x+817)/512",
            "fixed_point": "-817/217",
            "role": "mandatory adversarial regression; it is not a renewal-transfer contradiction",
        },
        "trivial_cycle": {"source": 1, "word": parity, "trace": trivial, "critical": True},
        "scope_controls": [
            "NG22 remains valid: different real and 2-adic completion limits are not contradictory.",
            "One-orbit capacity does not imply P80 address anti-concentration.",
            "Negative and formal 2-adic sources are not positive-cycle witnesses.",
            "The private row digest is diagnostic only.",
        ],
        "proves_collatz": False,
    }


def expected_report(digest: str) -> str:
    return f"""# Phase 38 boundary and obstacle report

The finite-capacity recursion and the renewal-transfer identities survive the
independent mathematical audit.  The supplied formula line containing
`2079/1000 < < 842/405` has been read as the evident typographical correction
`2079/1000 < 842/405`; the exact integer comparison is certified.

## Private digest diagnostic

The supplied private target is `{PRIVATE_TARGET}`.  The repository now
defines a self-contained canonical row encoding and obtains
`{digest}`.  These values do not match.  Because the proposal did
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


def verify(directory: Path) -> dict[str, object]:
    capacity_path = directory / FILES[0]
    renewal_path = directory / FILES[1]
    regressions_path = directory / FILES[2]
    report_path = directory / FILES[3]
    stored_capacity = load_object(capacity_path)
    stored_renewal = load_object(renewal_path)
    stored_regressions = load_object(regressions_path)

    capacity = expected_capacity()
    if stored_capacity != capacity:
        fail("capacity artifact mismatch")
    renewal = expected_renewal()
    if stored_renewal != renewal:
        fail("renewal artifact mismatch")
    regressions = expected_regressions()
    if stored_regressions != regressions:
        fail("regression artifact mismatch")
    try:
        report = report_path.read_text(encoding="utf-8")
    except OSError as exc:
        raise VerificationError(f"cannot read obstruction report: {exc}") from exc
    if report != expected_report(str(capacity["rows_digest_sha256"])):
        fail("obstruction report mismatch")
    generator_names = ("src." + "phase38_" + "search", "phase38_" + "search")
    if any(name in sys.modules for name in generator_names):
        fail("generator imported")
    return {
        "format": "collatz-phase38-verifier-v1",
        "valid": True,
        "generator_imported": False,
        "claims": {name: STATUSES[name] for name in ("P227", "P228", "E54", "P229", "P230", "P231", "P232", "P233", "P234", "H72")},
        "capacity_rows": len(capacity["rows"]),
        "capacity_row_digest_sha256": capacity["rows_digest_sha256"],
        "private_digest_match": capacity["private_digest_diagnostic"]["matches"],
        "translated_interval_counts": capacity["translated_interval_audit"],
        "renewal_counts": {
            key: renewal["finite_audit"][key]
            for key in ("codeword_count", "address_count", "transition_count", "nonzero_transfer_count")
        },
        "mandatory_families": regressions["mandatory_families"],
        "input_sha256": {name: file_digest(directory / name) for name in FILES},
        "floating_point_used_for_acceptance": False,
        "proves_collatz": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    try:
        result = verify(args.artifact_dir)
    except VerificationError as exc:
        print(json.dumps({"valid": False, "error": str(exc), "proves_collatz": False}, sort_keys=True))
        return 1
    rendered = json.dumps(result, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.write_text(rendered, encoding="utf-8")
    print(json.dumps(result, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
