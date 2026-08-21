# Phase 3 acceptance run

Branch: `feat/phase3-mixed-merge`

This is a finite mixed-modulus search with an unresolved frontier. It does not
prove the Collatz conjecture.

## Reproduction commands

```bash
.venv/bin/python -m pytest -q
.venv/bin/python src/phase3_search.py \
  --phase1-certificate artifacts/baseline_certificate.json \
  --binary-depth 20 --max-ternary 2 --boundary-depth 36
.venv/bin/python verifier/verify_phase3.py artifacts/phase3_certificate.json \
  --phase1-certificate artifacts/baseline_certificate.json \
  --output artifacts/phase3_verifier_result.json
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
```

## Tests

```text
129 passed in 35.49s
```

The tests include Hypothesis properties for both split types, exact Phase 3
preliminary counts, a naive-versus-meet-in-the-middle boundary comparison,
independent forward-path reconstruction, tamper rejection, `2^m-1`, `8^m-5`,
and long words in `(110|111)^*`.

## Independent verifier

```json
{
  "binary_depth": 20,
  "binary_frontier_nodes": 27328,
  "closed_by_reverse_merge": 43198,
  "coefficient_dp_valid": true,
  "mixed_open_nodes": 79350,
  "phase1_domain_zero_boundary_margins_checked": 190067,
  "phase1_positive_t_min_exceptions": 2,
  "proves_collatz": false,
  "records_by_ternary_level": {
    "0": 27328,
    "1": 47610,
    "2": 95220
  },
  "status": "verified_partial_phase3_certificate_with_mixed_open_frontier",
  "valid": true
}
```

The verifier independently reconstructs every `TERNARY_SPLIT`, reverse
divisibility step, strict family inequality, and forward affine path. It does
not import the search model.

## Exact finite results

- Coefficient-DP counts match `a_10=64`, `a_15=1295`, `a_20=27328`,
  `a_22=93222`, and `a_26=1037374`.
- `sum(a_0..a_25)=1227442`; first crossings including the trivial even root
  total 190,069.
- Stage A closes 11,458 of 27,328 binary parents.
- The independent preliminary ternary audit closes 50,244 of all 81,984
  one-split children.
- Actual unresolved-parent refinement leaves 31,740 children at level 1 and
  79,350 children at level 2, exact growth ratios `31740/15870` and
  `79350/31740`.
- All 43,198 accepted closures use `REVERSE_MERGE`; no periodic-substring
  dictionary is used.
- Boundary-gap exhaustive audit reaches boundary depth 36 with no `A_gap<=0`
  counterexample on the `t_min=0` domain. The minimum is 1 at boundary depth 5.
  This is a finite result, not a theorem.
- Boundary depth 27 independently reproduces `r=167`, `y=325`, `A_gap=9`.
- The smallest unresolved representative is 27, for the exact bounded-search
  obstruction family
  `n(t)=27+9437184*t`, `T^20(n(t))=395+129140163*t`, `t>=0`.
- Mixed unresolved growth is supercritical/exponential-looking over the tested
  two refinements; no asymptotic classification is claimed.

## Phase 3 SHA-256

```text
68a77ad9a1169a9db55e82423b8a337f18af7b357f29a4409f9948345ba5104d  boundary_gap_minima.json
4d44d2fc2bde7d75fac46c1d7ced6937654e2636ee205d5e40a9d4b4f4f42fd6  mixed_survivors.json
d3a7c06a78706f73b5f24759bcf5003285ec81bbeab05a8ee21216ac08993780  phase3_certificate.json
9fe09e4ed88b1c15bc24eb8a325a33d7eaeb6764e56efdb713eafea02d938afa  phase3_obstruction_report.md
d8f49e79f4a6c6aa119103a19c8ea465cae88a30a913fb343c6363a2d5639b8a  phase3_open_counts.csv
30cd4fa9de50a70a5e279c1b4cfa97bffe49eced303d7e0909effe8f727fca06  phase3_verifier_result.json
9398c4c4119b49c464742eb09d8653f554c7359117b3fc1c8403c2c0b930aaa4  reverse_merge_stats.csv
```

The complete manifest is `artifacts/SHA256SUMS`; its own SHA-256 is
`7ec5566f7a2a0c0083a5b1b6d4f48863329d65619324c63f51a7543e93c7507f`.
