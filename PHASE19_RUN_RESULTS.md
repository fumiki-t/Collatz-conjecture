# Phase 19: affine valleys and source lifts — run results

Branch: `feat/phase19-affine-lift`

Base commit: `e6743026c1958974c226cf8bcc5a92d8800c920c`

Result commit: recorded by the accepted experiment manifest

Phase 19 treats the supplied note as an untrusted proposal.  It accepts the
affine-valley, tilted-martingale, occupation, source-lift, and periodic-rational
mechanisms after repairing their finite/infinite and all-zero boundaries.
It also refutes finite-mean bookkeeping for the first-passage affine
correction.  H112, H72, and the Collatz conjecture remain open.

The proof, exact quantifiers, and proposal repairs are in
[`research/audits/affine-lift/REPORT.md`](research/audits/affine-lift/REPORT.md).

## Accepted results

- P112 `VERIFIED_THEOREM`: a positive predecessor below `N` either exposes a
  smaller strictly coefficient-safe valley suffix or satisfies the exact
  affine-only length bound `n>3N(1-c/u)`.
- P113 `VERIFIED_THEOREM`: the source/endpoint exponent tilts give exact
  bounded-stopping duality; the first-passage affine correction has infinite
  first moment and explicit finite fractional moments of every order below
  one.
- P114 `VERIFIED_THEOREM`: P72 implies only `O(j^(1/9))` visits to every fixed
  discrepancy strip.  This excludes the particular fixed-packet balanced
  P109 itinerary from positive ordinary realization without EXT07.
- P115 `VERIFIED_THEOREM`: canonical source representatives have exact lift
  digits, and a positive ordinary source is equivalent to eventual zero
  lifts.  Exact valuations require realization of the whole infinite tail.
- P116 `VERIFIED_THEOREM`: a rational periodic source that is not a positive
  integer has an effective exponential lower bound on canonical residues.
- E31 `VERIFIED_FINITE`: the declared finite products, stopped trees, all
  geodesic critical words through `Q=17`, periodic samples, and 63 adversarial
  rows are independently reconstructed.
- NG31 `REFUTED`: the endpoint-tilted affine correction cannot be treated as a
  finite-mean average-small error.
- H112 remains `OPEN`: every infinite coefficient-safe all-prefix same-Q
  geodesic branch should have infinitely many nonzero lifts.
- H72 remains `OPEN`; `proves_collatz=false`.

## Proposal corrections

- A finite terminal zero lift proves a divisibility congruence, not the exact
  valuation; exactness follows only after a positive integer realizes the
  entire infinite exponent tail.
- The periodic claim requires an odd step.  The all-zero block fixes zero and
  is not a positive odd-cycle candidate.
- Source 167 has eleven terminal zero exponent lifts at `Q=17` and still
  crosses coefficient safety three shortcut steps later.  Finite zero runs
  therefore cannot be promoted to eventual stabilization.
- Finite stopped means are diagnostics only.  The infinite-mean theorem comes
  from bounded stopping, exact change of measure, Doob's inequality, and
  monotone convergence—not a tail fit.

## Exact finite data

```text
P112 eligible rows, n<=6 and e_i<=4:       136
safe-valley / affine-length alternatives:  104 / 32
T_2 audit depths:                           1..12
R=12 active nodes / ordinary leaves:        11,433 / 3,330
all geodesic critical rows through Q=17:    406,353
Q=17 critical / geodesic words:             312,455 / 253,018
maximum trailing zero exponent lifts:       11
periodic samples:                            8 x 16 repeats
mandatory/adversarial rows:                  63
```

## Reproduction

```bash
.venv/bin/python src/phase19_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase19.py \
  --artifact-dir artifacts --write-report artifacts/phase19_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase19_properties.py tests/test_phase19_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier imports no generator code.  It uses an explicit affine sum,
reverse stopped-tree traversal with independently aggregated geometric tails,
string-based safe-word recursion, direct source congruences, and reduced
rational periodic bounds.  Tamper tests cover every evidence class.

The accepted experiment manifest records final commit, timings, test counts,
and manifest hash.

## What this result does not prove

- H112 or a general nonzero-lift theorem;
- that P112's near-diagonal affine-only band is empty;
- exclusion of every aperiodic escaping-discrepancy itinerary;
- H72, H89, H104, H105, nontrivial cycles, or Collatz.

`proves_collatz=false`.
