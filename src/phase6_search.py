#!/usr/bin/env python3
"""Generate exact Phase 6 critical-prefix barrier artifacts."""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from dataclasses import dataclass
from pathlib import Path


FORMAT = "collatz-phase6-critical-prefix-barrier-v1"
EXTERNAL_STARTS = (
    2,
    3,
    7,
    27,
    703,
    10087,
    35655,
    270271,
    362343,
    381727,
    626331,
    1027431,
    1126015,
    8088063,
    13421671,
    20638335,
    26716671,
    56924955,
    63728127,
    217740015,
    1200991791,
    1827397567,
    2788008987,
    12235060455,
    898696369947,
    2081751768559,
    13179928405231,
    31835572457967,
    70665924117439,
    739448869367967,
    1008932249296231,
    118303688851791519,
    180352746940718527,
    1236472189813512351,
    2602714556700227743,
)
EXTERNAL_DROPPING_TIMES = (
    1,
    4,
    7,
    59,
    81,
    105,
    135,
    164,
    165,
    173,
    176,
    183,
    224,
    246,
    287,
    292,
    298,
    308,
    376,
    395,
    398,
    433,
    447,
    547,
    550,
    606,
    688,
    712,
    722,
    728,
    886,
    902,
    966,
    990,
    1005,
)
SANITY_RECORD_Q = (1, 3, 5, 17, 29, 41, 94, 147, 200, 253, 306, 971)
MIXED_RECORD_PAIRS = ((1, 1), (2, 3), (5, 8), (18, 29), (31, 50), (44, 71), (57, 92), (184, 297))

if hasattr(sys, "set_int_max_str_digits"):
    sys.set_int_max_str_digits(0)


def shortcut_step(value: int) -> int:
    return value // 2 if value % 2 == 0 else (3 * value + 1) // 2


def stopping_times(start: int, *, limit: int = 20_000) -> tuple[int, int]:
    if start < 2:
        raise ValueError("stopping times require start >= 2")
    value = start
    odd_steps = 0
    dropping: int | None = None
    coefficient: int | None = None
    for depth in range(1, limit + 1):
        if value % 2:
            odd_steps += 1
        value = shortcut_step(value)
        if coefficient is None and pow(3, odd_steps) < (1 << depth):
            coefficient = depth
        if dropping is None and value < start:
            dropping = depth
        if dropping is not None and coefficient is not None:
            return dropping, coefficient
    raise RuntimeError(f"stopping-time limit reached for {start}")


def coefficient_stopping_time(start: int, *, limit: int = 20_000) -> int:
    value = start
    odd_power = 1
    for depth in range(1, limit + 1):
        if value % 2:
            odd_power *= 3
        value = shortcut_step(value)
        if odd_power < (1 << depth):
            return depth
    raise RuntimeError(f"coefficient-stopping limit reached for {start}")


def exact_decimal(numerator: int, denominator: int, places: int = 6) -> str:
    scale = 10**places
    scaled = numerator * scale // denominator
    return f"{scaled // scale}.{scaled % scale:0{places}d}"


@dataclass(frozen=True, slots=True)
class HRecord:
    q: int
    K: int
    B: int
    D: int

    @property
    def floor(self) -> int:
        return self.B // self.D

    def csv_row(self, scan_limit: int) -> dict[str, object]:
        return {
            "q": self.q,
            "K_q": self.K,
            "B_q_max": self.B,
            "D_q": self.D,
            "H_floor": self.floor,
            "H_decimal_truncated_6": exact_decimal(self.B, self.D),
            "scan_limit": scan_limit,
        }


def _fraction_greater(
    numerator: int, denominator: int, best_numerator: int, best_denominator: int
) -> bool:
    quotient, remainder = divmod(numerator, denominator)
    best_quotient, best_remainder = divmod(best_numerator, best_denominator)
    if quotient != best_quotient:
        return quotient > best_quotient
    return remainder * best_denominator > best_remainder * denominator


def assumed_external_m(k: int) -> int:
    for start, stopping in zip(EXTERNAL_STARTS, EXTERNAL_DROPPING_TIMES, strict=True):
        if stopping > k:
            return start
    raise ValueError("external record list does not cover this k")


def scan_hq(limit: int) -> tuple[list[HRecord], list[dict[str, object]]]:
    if limit < SANITY_RECORD_Q[-1]:
        raise ValueError(f"H_q scan limit must be at least {SANITY_RECORD_Q[-1]}")
    power_three = 1
    b_max = 0
    best_b = 0
    best_d = 1
    records: list[HRecord] = []
    external_comparisons: list[dict[str, object]] = []
    for q in range(1, limit + 1):
        floor_power = power_three.bit_length() - 1
        b_max = 3 * b_max + (1 << floor_power)
        power_three *= 3
        k_q = power_three.bit_length()
        d_q = (1 << k_q) - power_three
        if _fraction_greater(b_max, d_q, best_b, best_d):
            records.append(HRecord(q, k_q, b_max, d_q))
            best_b, best_d = b_max, d_q
        if k_q <= EXTERNAL_DROPPING_TIMES[-1]:
            m_value = assumed_external_m(k_q - 1)
            external_comparisons.append(
                {
                    "row_type": "BARRIER_COMPARISON",
                    "classification": "EXTERNAL_RECORD_EVIDENCE",
                    "q": q,
                    "K_q": k_q,
                    "assumed_M": m_value,
                    "H_numerator": b_max,
                    "H_denominator": d_q,
                    "barrier_holds": m_value * d_q > b_max,
                    "ratio_M_over_H_numerator": m_value * d_q,
                    "ratio_M_over_H_denominator": b_max,
                    "ratio_gt_4": m_value * d_q > 4 * b_max,
                }
            )
    if tuple(row.q for row in records[: len(SANITY_RECORD_Q)]) != SANITY_RECORD_Q:
        raise AssertionError("exact H_q sanity record indices changed")
    return records, external_comparisons


def external_record_rows() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for start, expected in zip(EXTERNAL_STARTS, EXTERNAL_DROPPING_TIMES, strict=True):
        dropping, coefficient = stopping_times(start)
        rows.append(
            {
                "row_type": "STOPPING_RECORD",
                "classification": "EXTERNAL_RECORD_EVIDENCE",
                "start": start,
                "provided_dropping_time": expected,
                "recomputed_dropping_time": dropping,
                "coefficient_stopping_time": coefficient,
                "times_equal": dropping == coefficient == expected,
                "minimality_verified": False,
            }
        )
    return rows


def direct_m_records(bound_inclusive: int) -> list[dict[str, object]]:
    if bound_inclusive < 2:
        raise ValueError("M search bound must be at least two")
    rows: list[dict[str, object]] = []
    best_stop = 0
    for start in range(2, bound_inclusive + 1):
        stopping = coefficient_stopping_time(start)
        if stopping > best_stop:
            best_stop = stopping
            rows.append(
                {
                    "start": start,
                    "coefficient_stopping_time": stopping,
                    "search_bound_inclusive": bound_inclusive,
                    "record_minimality": "EXACT_WITHIN_SCANNED_PREFIX",
                }
            )
    return rows


def minimum_in_cylinder(depth: int, residue: int) -> int:
    modulus = 1 << depth
    if not (0 <= residue < modulus):
        raise ValueError("invalid binary cylinder")
    if residue >= 2:
        return residue
    return residue + ((2 - residue + modulus - 1) // modulus) * modulus


def cylinder_count(depth: int, residue: int, bound: int) -> int:
    minimum = minimum_in_cylinder(depth, residue)
    return 0 if minimum > bound else 1 + (bound - minimum) // (1 << depth)


def _direct_leaf(depth: int, residue: int, bound: int, k: int) -> dict[str, object] | None:
    minimum = minimum_in_cylinder(depth, residue)
    modulus = 1 << depth
    digest = hashlib.sha256()
    maximum = 0
    count = 0
    for value in range(minimum, bound + 1, modulus):
        stopping = coefficient_stopping_time(value)
        if stopping > k:
            return None
        maximum = max(maximum, stopping)
        count += 1
        digest.update(f"{value}:{stopping}\n".encode("ascii"))
    return {
        "value_count": count,
        "maximum_coefficient_stopping_time": maximum,
        "sha256": digest.hexdigest(),
    }


def build_certificate(k: int, bound: int, direct_threshold: int) -> dict[str, object] | None:
    nodes: list[dict[str, object]] = []

    def visit(depth: int, residue: int, odd_steps: int, constant: int) -> int | None:
        node_id = len(nodes)
        nodes.append({})
        count = cylinder_count(depth, residue, bound)
        base = {
            "id": node_id,
            "depth": depth,
            "residue": residue,
            "odd_steps": odd_steps,
        }
        if count == 0:
            nodes[node_id] = {
                **base,
                "rule": "EMPTY_RANGE",
                "minimum_value": minimum_in_cylinder(depth, residue),
            }
            return node_id
        odd_power = pow(3, odd_steps)
        if odd_power < (1 << depth):
            nodes[node_id] = {
                **base,
                "rule": "COEFF_CROSS",
                "strict_gap": (1 << depth) - odd_power,
            }
            return node_id
        if count <= direct_threshold:
            direct = _direct_leaf(depth, residue, bound, k)
            if direct is None:
                nodes.pop()
                return None
            nodes[node_id] = {**base, "rule": "DIRECT", **direct}
            return node_id
        if depth >= k:
            nodes.pop()
            return None
        numerator = odd_power * residue + constant
        denominator = 1 << depth
        if numerator % denominator:
            raise AssertionError("cylinder affine value is non-integral")
        base_value = numerator // denominator
        children: list[int] = []
        for parameter_bit in (0, 1):
            parity = (base_value + parameter_bit) % 2
            child_residue = residue + parameter_bit * denominator
            child_odd = odd_steps + parity
            child_constant = 3 * constant + denominator if parity else constant
            child = visit(depth + 1, child_residue, child_odd, child_constant)
            if child is None:
                del nodes[node_id:]
                return None
            children.append(child)
        nodes[node_id] = {**base, "rule": "BINARY_SPLIT", "children": children}
        return node_id

    root = visit(0, 0, 0, 0)
    if root is None:
        return None
    counts: dict[str, int] = {}
    for node in nodes:
        rule = str(node["rule"])
        counts[rule] = counts.get(rule, 0) + 1
    return {
        "format": "collatz-M-lower-bound-certificate-v1",
        "claim": f"M({k})>{bound}",
        "k": k,
        "X": bound,
        "direct_threshold": direct_threshold,
        "root": root,
        "node_count": len(nodes),
        "rule_counts": dict(sorted(counts.items())),
        "nodes": nodes,
    }


def parity_residue(word: str) -> int:
    coefficient = 1
    constant = 0
    result = 0
    for index, raw in enumerate(word):
        bit = int(raw)
        modulus = 1 << (index + 1)
        result = ((bit << index) - constant) * pow(coefficient, -1, modulus) % modulus
        if bit:
            coefficient *= 3
            constant = 3 * constant + (1 << index)
    return result


def word_audit(name: str, word: str) -> dict[str, object]:
    odd_power = 1
    minimum_gap: int | None = None
    safe = True
    for depth, bit in enumerate(word, start=1):
        if bit == "1":
            odd_power *= 3
        gap = odd_power - (1 << depth)
        minimum_gap = gap if minimum_gap is None else min(minimum_gap, gap)
        safe = safe and gap >= 0
    residue = parity_residue(word)
    modulus = 1 << len(word)
    start = residue if residue >= 2 else residue + modulus
    return {
        "family": name,
        "word": word,
        "depth": len(word),
        "odd_steps": word.count("1"),
        "minimum_representative": start,
        "all_prefix_coefficients_at_least_one": safe,
        "terminal_coefficient_gap": odd_power - modulus,
        "minimum_prefix_gap": minimum_gap,
    }


def adversarial_family_audit() -> dict[str, object]:
    rows: list[dict[str, object]] = []
    for exponent in range(2, 21):
        start = (1 << exponent) - 1
        stopping = coefficient_stopping_time(start)
        rows.append(
            {
                "family": "2^m-1",
                "m": exponent,
                "start": start,
                "coefficient_stopping_time": stopping,
            }
        )
    for exponent in range(1, 9):
        start = pow(8, exponent) - 5
        rows.append(
            {
                "family": "8^m-5",
                "m": exponent,
                "start": start,
                "coefficient_stopping_time": coefficient_stopping_time(start),
            }
        )
    block_rows = []
    for blocks in range(1, 9):
        for mask in range(1 << blocks):
            word = "".join("111" if (mask >> index) & 1 else "110" for index in range(blocks))
            block_rows.append(word_audit("(110|111)^*", word))
    mixed_rows = [
        word_audit(f"A^{r}B^{s}", "11101" * r + "1100" * s)
        | {"r": r, "s": s}
        for r, s in MIXED_RECORD_PAIRS
    ]
    return {
        "classification": "EXACT_FINITE_ADVERSARIAL_AUDIT",
        "integer_families": rows,
        "block_language": {
            "maximum_blocks": 8,
            "words_checked": len(block_rows),
            "all_safe": all(row["all_prefix_coefficients_at_least_one"] for row in block_rows),
            "smallest_representative_by_depth": [
                min(
                    (row for row in block_rows if row["depth"] == 3 * blocks),
                    key=lambda row: int(row["minimum_representative"]),
                )
                for blocks in range(1, 9)
            ],
        },
        "mixed_blocks": {
            "A": word_audit("A", "11101"),
            "B": word_audit("B", "1100"),
            "records": mixed_rows,
            "all_record_words_safe": all(
                row["all_prefix_coefficients_at_least_one"] for row in mixed_rows
            ),
            "arbitrary_closeness_scope": {
                "exact_premises": "multiplier=3^(4*r+2*s)/2^(5*r+4*s) and log(81/32)/log(16/9) is irrational by unique factorization",
                "external_math_input": "density of positive linear combinations r*alpha-s*beta for irrational alpha/beta",
                "conclusion_with_external_input": "positive multipliers can approach one arbitrarily closely from above",
                "checker_boundary": "finite records and exact premises are checked; the density theorem is named, not reproved",
            },
        },
        "rejected_mechanisms": [
            {
                "candidate": "uniform positive coefficient margin on every safe prefix",
                "counterexample": "finite A^rB^s records shrink the margin below 2^-13; the arbitrary-margin no-go additionally uses the named density theorem",
            },
            {
                "candidate": "four canonical rational-shadow centers are complete",
                "counterexample": "W=111011100 has fixed point -817/217",
            },
            {
                "candidate": "bounded-depth finite-state testing establishes an eventual M lower bound",
                "counterexample": "(110|111)^* and A^rB^s remain safe at all tested depths; bounded survival is not an asymptotic certificate",
            },
        ],
        "eventual_polynomial_lower_bound_found": False,
        "proves_collatz": False,
    }


def write_csv(path: Path, rows: list[dict[str, object]], fieldnames: list[str]) -> None:
    with path.open("w", encoding="utf-8", newline="") as stream:
        writer = csv.DictWriter(
            stream, fieldnames=fieldnames, extrasaction="ignore", lineterminator="\n"
        )
        writer.writeheader()
        for row in rows:
            writer.writerow(row)


def certificate_bundle(
    records: list[HRecord], certificate_max_x: int, direct_threshold: int
) -> dict[str, object]:
    by_q = {record.q: record for record in records}
    certificates: list[dict[str, object]] = []
    claims: list[dict[str, object]] = []

    def add_certificate(identifier: str, k: int, bound: int, supported: list[int]) -> None:
        certificate = build_certificate(k, bound, direct_threshold)
        if certificate is None:
            raise AssertionError(f"failed to construct expected certificate {identifier}")
        certificate["id"] = identifier
        certificate["supported_barrier_record_q"] = supported
        certificates.append(certificate)

    for q in (1, 3, 5, 94):
        if q not in by_q or by_q[q].floor > certificate_max_x:
            continue
        record = by_q[q]
        add_certificate(f"record-q{q}", record.K - 1, record.floor, [q])

    grouped = [
        record
        for record in records
        if 147 <= record.q and record.floor <= certificate_max_x
    ]
    if grouped:
        add_certificate(
            f"records-q147-q{grouped[-1].q}",
            by_q[147].K - 1,
            grouped[-1].floor,
            [record.q for record in grouped],
        )

    covered = {
        q: str(certificate["id"])
        for certificate in certificates
        for q in certificate["supported_barrier_record_q"]
    }
    for record in records:
        if record.q in covered:
            claims.append(
                {
                    "q": record.q,
                    "K_q": record.K,
                    "H_numerator": record.B,
                    "H_denominator": record.D,
                    "H_floor": record.floor,
                    "status": "CERTIFIED",
                    "certificate_id": covered[record.q],
                }
            )
            continue
        witness = None
        if record.floor <= certificate_max_x:
            for start in range(2, record.floor + 1):
                stopping = coefficient_stopping_time(start)
                if stopping > record.K - 1:
                    witness = (start, stopping)
                    break
        if witness is not None:
            claims.append(
                {
                    "q": record.q,
                    "K_q": record.K,
                    "H_numerator": record.B,
                    "H_denominator": record.D,
                    "H_floor": record.floor,
                    "status": "EXACT_COUNTEREXAMPLE",
                    "safe_start": witness[0],
                    "coefficient_stopping_time": witness[1],
                }
            )
        else:
            claims.append(
                {
                    "q": record.q,
                    "K_q": record.K,
                    "H_numerator": record.B,
                    "H_denominator": record.D,
                    "H_floor": record.floor,
                    "status": "NOT_ATTEMPTED",
                }
            )
    last_covered = max((q for q in covered), default=0)
    record_qs = [record.q for record in records]
    next_record = min((q for q in record_qs if q > last_covered), default=None)
    eventual_start = 94 if 94 in covered else None
    return {
        "format": "collatz-M-lower-bound-certificate-bundle-v1",
        "certificate_language": ["COEFF_CROSS", "EMPTY_RANGE", "BINARY_SPLIT", "DIRECT"],
        "certificate_max_x": certificate_max_x,
        "direct_threshold": direct_threshold,
        "certificates": certificates,
        "barrier_record_claims": claims,
        "sparse_record_implication": {
            "certified_range_start_q": eventual_start,
            "last_certified_record_q": last_covered,
            "next_record_q": next_record,
            "certified_range_end_q": None if next_record is None else next_record - 1,
        },
        "adversarial_audit": adversarial_family_audit(),
        "universal_barrier_certified": False,
        "proves_collatz": False,
    }


def write_report(
    path: Path,
    hq_limit: int,
    records: list[HRecord],
    external_rows: list[dict[str, object]],
    comparisons: list[dict[str, object]],
    bundle: dict[str, object],
    m_records: list[dict[str, object]],
) -> None:
    failures = [row for row in comparisons if not row["barrier_holds"]]
    ranged = [row for row in comparisons if int(row["K_q"]) >= 66]
    minimum_ratio = ranged[0]
    for row in ranged[1:]:
        if int(row["ratio_M_over_H_numerator"]) * int(minimum_ratio["ratio_M_over_H_denominator"]) < int(
            minimum_ratio["ratio_M_over_H_numerator"]
        ) * int(row["ratio_M_over_H_denominator"]):
            minimum_ratio = row
    claims = bundle["barrier_record_claims"]
    assert isinstance(claims, list)
    certified = [row for row in claims if row["status"] == "CERTIFIED"]
    counterexamples = [row for row in claims if row["status"] == "EXACT_COUNTEREXAMPLE"]
    sparse = bundle["sparse_record_implication"]
    exact_m_k_limit = int(m_records[-1]["coefficient_stopping_time"]) - 1
    exact_ratio_rows: list[dict[str, object]] = []
    for comparison in comparisons:
        k = int(comparison["K_q"]) - 1
        if not (65 <= k <= exact_m_k_limit):
            continue
        exact_m = next(
            int(row["start"])
            for row in m_records
            if int(row["coefficient_stopping_time"]) > k
        )
        exact_ratio_rows.append(
            {
                **comparison,
                "exact_M": exact_m,
                "exact_ratio_numerator": exact_m * int(comparison["H_denominator"]),
                "exact_ratio_denominator": int(comparison["H_numerator"]),
            }
        )
    exact_minimum = exact_ratio_rows[0]
    for row in exact_ratio_rows[1:]:
        if int(row["exact_ratio_numerator"]) * int(exact_minimum["exact_ratio_denominator"]) < int(
            exact_minimum["exact_ratio_numerator"]
        ) * int(row["exact_ratio_denominator"]):
            exact_minimum = row
    lines = [
        "# Phase 6 critical-prefix barrier report",
        "",
        "This report does not claim a proof of the Collatz conjecture.",
        "",
        "## SYMBOLIC_THEOREM_VERIFIED",
        "",
        "- P54 is algebraically correct under its stated least-counterexample and first-crossing assumptions.",
        "- The independent verifier reconstructs the final-even argument, `K=bitlength(3^q)`, the odd-position bound, `B<=B_q^max`, and `D_q*N<=B`.",
        "- It also checks `H_q>q/6`, monotonicity of `M`, and the sparse barrier-record reduction.",
        "- These are conditional symbolic implications, not an existence proof for an eventual lower bound on `M(k)`.",
        "",
        "## EXACT_H_Q_RECORDS",
        "",
        f"- Every `q` through `{hq_limit}` was scanned using integer arithmetic; `{len(records)}` exact records were found.",
        f"- The last record in the requested scan is `q={records[-1].q}`, `K_q={records[-1].K}`, `floor(H_q)={records[-1].floor}`.",
        "- The twelve supplied sanity indices are reproduced exactly.",
        "",
        "## EXACT_FINITE_CERTIFICATES",
        "",
        f"- `{len(certified)}` barrier-record inequalities are independently certificate-checkable.",
        f"- Exact barrier coverage is `q={sparse['certified_range_start_q']}..{sparse['certified_range_end_q']}` by the sparse-record implication.",
        f"- Exact counterexamples at attempted failed records: `{[(row['q'], row['safe_start']) for row in counterexamples]}`.",
        "- No success rate is promoted to an asymptotic statement.",
        "",
        "## EXACT_DIRECT_M_SEARCH",
        "",
        f"- Direct exact prefix search ends at `{m_records[-1]['search_bound_inclusive']}` and found `{len(m_records)}` coefficient-stopping records.",
        f"- It determines `M(k)` exactly through `k={exact_m_k_limit}`.",
        f"- For `66<=K_q<={exact_m_k_limit + 1}`, the minimum is exact at `q={exact_minimum['q']}`, `K_q={exact_minimum['K_q']}`, `M={exact_minimum['exact_M']}` with ratio `{exact_minimum['exact_ratio_numerator']}/{exact_minimum['exact_ratio_denominator']}>4`.",
        "",
        "## EXTERNAL_RECORD_EVIDENCE",
        "",
        f"- All `{len(external_rows)}` supplied starts reproduce both listed dropping time and coefficient stopping time.",
        "- Their asserted record minimality is not verified and is used only in this section.",
        f"- Under that external assumption, the last failure is `q={failures[-1]['q']}, K_q={failures[-1]['K_q']}`.",
        f"- For `66<=K_q<=1005`, the minimum exact ratio occurs at `q={minimum_ratio['q']}`, `K_q={minimum_ratio['K_q']}`, assumed `M={minimum_ratio['assumed_M']}` and is greater than four.",
        "",
        "## ADVERSARIAL_AND_NO_GO_AUDIT",
        "",
        "- `2^m-1`, `8^m-5`, `(110|111)^*`, `A=11101`, `B=1100`, and the eight exact `A^rB^s` records are retained in the artifact.",
        "- Exact `A^rB^s` records shrink the terminal coefficient margin below `2^-13`; rejecting every fixed positive margin additionally uses the explicitly named density theorem from Phase 5.",
        "- `W=111011100` rejects completeness of the four canonical rational-shadow centers.",
        "- Bounded survival of the block languages rejects promotion of a bounded finite-state test to an eventual theorem.",
        "",
        "## HEURISTIC_AND_CONJECTURE",
        "",
        "- No rigorous eventual polynomial lower bound for `M(k)` was found.",
        "- Meet-in-the-middle anti-concentration, continued-fraction forcing, and a bound exceeding `H_q=O(q^5.117)` remain research directions, not verified results.",
        "- The Wu-Wang Diophantine estimate is not independently proved or used by any finite certificate here.",
        "",
    ]
    path.write_text("\n".join(lines), encoding="utf-8")


def generate(
    artifact_dir: Path,
    *,
    hq_limit: int = 200_000,
    m_search_bound: int = 1_500_000,
    certificate_max_x: int = 1_500_000,
    direct_threshold: int = 64,
) -> dict[str, object]:
    artifact_dir.mkdir(parents=True, exist_ok=True)
    records, comparisons = scan_hq(hq_limit)
    external_rows = external_record_rows()
    m_records = direct_m_records(m_search_bound)
    bundle = certificate_bundle(records, certificate_max_x, direct_threshold)

    write_csv(
        artifact_dir / "Hq_records.csv",
        [record.csv_row(hq_limit) for record in records],
        ["q", "K_q", "B_q_max", "D_q", "H_floor", "H_decimal_truncated_6", "scan_limit"],
    )
    external_fields = [
        "row_type",
        "classification",
        "start",
        "provided_dropping_time",
        "recomputed_dropping_time",
        "coefficient_stopping_time",
        "times_equal",
        "minimality_verified",
        "q",
        "K_q",
        "assumed_M",
        "H_numerator",
        "H_denominator",
        "barrier_holds",
        "ratio_M_over_H_numerator",
        "ratio_M_over_H_denominator",
        "ratio_gt_4",
    ]
    write_csv(artifact_dir / "external_record_audit.csv", external_rows + comparisons, external_fields)
    write_csv(
        artifact_dir / "M_search_records.csv",
        m_records,
        ["start", "coefficient_stopping_time", "search_bound_inclusive", "record_minimality"],
    )
    (artifact_dir / "M_lower_bound_certificates.json").write_text(
        json.dumps(bundle, indent=2, sort_keys=True) + "\n", encoding="utf-8"
    )
    write_report(
        artifact_dir / "phase6_obstruction_report.md",
        hq_limit,
        records,
        external_rows,
        comparisons,
        bundle,
        m_records,
    )
    result = {
        "format": FORMAT,
        "Hq_scan_limit": hq_limit,
        "Hq_record_count": len(records),
        "last_Hq_record": [records[-1].q, records[-1].K, records[-1].floor],
        "external_stopping_records_checked": len(external_rows),
        "M_search_bound_inclusive": m_search_bound,
        "M_search_record_count": len(m_records),
        "exact_certificates": len(bundle["certificates"]),
        "exact_record_claims": sum(
            row["status"] == "CERTIFIED" for row in bundle["barrier_record_claims"]
        ),
        "universal_barrier_certified": False,
        "proves_collatz": False,
    }
    print(json.dumps(result, indent=2, sort_keys=True))
    return result


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--artifact-dir", type=Path, default=Path("artifacts"))
    parser.add_argument("--hq-limit", type=int, default=200_000)
    parser.add_argument("--m-search-bound", type=int, default=1_500_000)
    parser.add_argument("--certificate-max-x", type=int, default=1_500_000)
    parser.add_argument("--direct-threshold", type=int, default=64)
    args = parser.parse_args()
    generate(
        args.artifact_dir,
        hq_limit=args.hq_limit,
        m_search_bound=args.m_search_bound,
        certificate_max_x=args.certificate_max_x,
        direct_threshold=args.direct_threshold,
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
