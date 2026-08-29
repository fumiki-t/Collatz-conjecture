# Phase 20: parity-complexity barriers — run results

Branch: `feat/phase20-parity-complexity`

Base: `2fbcad3fbcfb8ecabc4522ec3acfb81467daf8df`

Repository status: `OPEN`; `proves_collatz=false`.

## Accepted scope

Phase 20 treats the supplied note as an untrusted proposal. The detailed
proof/dependency audit is in
[`research/audits/parity-complexity/REPORT.md`](research/audits/parity-complexity/REPORT.md).

| Claim | Status | Accepted statement |
|---|---|---|
| EXT08--EXT13 | `EXTERNAL_THEOREM` | Critical `liminf` density and the exact external word/transcendence inputs are isolated rather than reproved. |
| P117 | `VERIFIED_THEOREM` | P72 excludes bounded discrepancy and every global envelope below `(8/9)log j`. |
| P118 | `VERIFIED_THEOREM` | `ln(2)/ln(3)` is transcendental, using EXT09. |
| P119 | `CONDITIONAL` | Under EXT08 and class-specific inputs, algebraic-frequency morphic, pure binary morphic, primitive substitutive, and automatic parity words are excluded. |
| P120 | `VERIFIED_THEOREM` | Bounded binary balance gives a natural frequency and uniform factor discrepancy. |
| P121 | `CONDITIONAL` | Under EXT08, a positive permanent-safe nonperiodic candidate has unbounded balance and abelian complexity. |
| P122 | `VERIFIED_THEOREM` | A non-erasing morphic Sturmian image has bounded prefix discrepancy about its output frequency. |
| P123/P124 | `CONDITIONAL` | Under EXT08/EXT12, quasi-Sturmian tails are excluded and `p(n)-n -> infinity`. |
| E32 | `VERIFIED_FINITE` | Thirteen 512-bit prefixes, 832 factor rows, 38 source-family rows, and 64 `A^rB^s` rows are independently reconstructed. |
| H112/H72 | `OPEN` | No nonzero-lift, ordinary-height, or full infinite-tail exclusion is proved. |

## Literature audit

The López--Stoll arXiv e-print TeX was inspected through Theorem `aperiodic`
and its proof. The result is exactly a `liminf` statement for rational 2-adic
infinite shortcut orbits. The map and input-parity convention agree with the
repository. It is retained as EXT08, not promoted to an internal theorem.

The Cassaigne, Allouche--Shallit/Saari, Bell, primitive-substitution, and
Gelfond--Schneider inputs are separately recorded in
[`docs/LITERATURE.md`](docs/LITERATURE.md) and
`artifacts/phase20_literature_audit.json`.

## Exact finite audit

- Prefix length: 512 bits.
- Factor lengths: every `1<=n<=64`.
- Sequences: 13.
- Factor rows: 832.
- Mandatory source rows: 38 (`m=2..20` for both source families).
- `A^rB^s` rows: 64 (`1<=r,s<=8`).
- Source 167 loses strict coefficient safety at shortcut step 29; the finite
  profile is not an H112 candidate.
- The all-contact, both NG22, and P109 formal words remain explicit
  falsification controls. No positive ordinary source is inferred.

The generator uses rolling integer factor encodings and affine recurrence.
The verifier imports no generator implementation and instead uses direct
substring sets and the closed odd-position affine sum.

## Reproduction

```bash
.venv/bin/python src/phase20_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase20.py \
  --artifact-dir artifacts --write-report artifacts/phase20_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase20_properties.py tests/test_phase20_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

Recorded acceptance results and commit/hash provenance are stored in
`research/experiments/phase20-parity-complexity.json`.

Observed verification results before acceptance:

- focused Phase 20/control-plane tests: `15 passed in 12.20s`;
- full regression suite: `299 passed in 676.45s`;
- independent verifier: `valid=true`, `proves_collatz=false`;
- strict research health: `valid=true`, no errors or warnings;
- SHA-256 of `artifacts/SHA256SUMS`:
  `1bc6f3bdae759ca5403d57787877555baf0317b9cb93b12987c86ef78ca97530`.

## Tamper rejection

The tests require rejection after:

- changing a generated factor-complexity count;
- replacing EXT08's `liminf` statement by a plain limit;
- changing `proves_collatz` to true;
- introducing a generator import into the independent verifier.

## What this result does not prove

- Finite factor profiles do not prove an infinite word morphic, automatic,
  balanced, quasi-Sturmian, or high-entropy.
- `p(n)-n -> infinity` does not imply linear excess or positive entropy.
- The external theorems are not internally reproved.
- No theorem forces a nonzero P115 source lift or excludes all positive
  ordinary permanent-safe sources.
- H112, H72, the nontrivial-cycle branch, and the Collatz conjecture remain
  open.

`proves_collatz=false`.
