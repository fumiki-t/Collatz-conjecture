# Phase 1–2 acceptance run

Run on Python 3.13.0 (the implementation requires Python 3.12 or later).

## Commands

```bash
.venv/bin/python -m pytest -q
.venv/bin/python src/search.py --depth 26 --output artifacts/baseline_certificate.json
.venv/bin/python verifier/verify_certificate.py artifacts/baseline_certificate.json
.venv/bin/python src/mine_obstructions.py --certificate artifacts/baseline_certificate.json
.venv/bin/python scripts/hash_artifacts.py artifacts --write artifacts/SHA256SUMS
```

## Test and verifier results

```text
117 passed in 4.98s
```

The independent verifier returned:

```json
{
  "max_depth": 26,
  "open_nodes": 1037374,
  "proves_collatz": false,
  "rule_counts": {
    "DESCENT": 190069,
    "OPEN": 1037374,
    "SPLIT": 1227442
  },
  "status": "verified_partial_certificate_with_open_frontier",
  "valid": true
}
```

The exhaustive finite audit checked 16,777,214 integers in
`2 <= n < 2^24`, comprising 54,413,413 literal shortcut steps. Every checked
direct value equaled its affine-cylinder value. Its ordered-chunk audit digest
is `5e9121d37babdab4b34998a6222e0fd3da5f78abe0d1ffe2ad2e89538aefa599`.

## Phase 2 finite observations

- Depth-26 OPEN survivors: 1,037,374.
- Short-shadow dictionary coverage: 913,466/1,037,374.
- Unexplained by that dictionary: 123,908.
- Smallest represented unexplained integer: 27.
- Exact parity word: `11011111010110111011110100`.
- Finite-range survivor and unexplained counts look exponential; asymptotic
  growth is unresolved.
- A non-vanishing asymptotic macro-coverage fraction is unresolved.

These are computational observations, not a proof of the Collatz conjecture.

## SHA-256

```text
51929cf76c267cbda0d29c3823505c78024b382d6580abf049d45916e6e31eb0  baseline_certificate.json
b1fda6bbd1d3fdf5c36d351b9c751ab1768b81eb52071f0c817106c55173c115  canonical_signatures.json
1549f24b8290b0eb0cd4ffa3391ae83cbd77688a42cc105e6da003ceda7a6a95  obstruction_report.md
52d108a10a87047e780b38f46f926ca54ccd087bc549ae638c4c84c68289365e  repeated_blocks.json
fada38f361eb93ffc777afcfa9fc12a75168c8bc81057b0dd190ab3f7b3cf679  survivor_stats.csv
```

`artifacts/SHA256SUMS` itself has SHA-256
`2084ee2546a5c64cf8c11af5d5e55510b5220f63175fcaea2e28cacf23abd4d8`.
