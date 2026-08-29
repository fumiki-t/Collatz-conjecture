# Phase 17: predecessor pressure and the 270 dichotomy — run results

Branch: `feat/phase17-predecessor-pressure`

Base commit: `464d74ce1acc5628d892170576847b34abf83931`

Result commit: recorded by the accepted experiment manifest

Phase 17 treats the supplied note as an untrusted proposal. It accepts the
exact r<=4 predecessor sieve, finite-crossing 270 dichotomy, exponent-code
pressure identity, and suffix-decodable r=4 code after repairing the equality,
overlapping-cylinder, and finite-pressure boundaries. Neither dichotomy
branch is excluded, and the Collatz conjecture remains open.

The detailed proof and quantifiers are in
[`research/audits/predecessor-pressure/REPORT.md`](research/audits/predecessor-pressure/REPORT.md).

## Accepted results

- P104 `VERIFIED_THEOREM`: under the least-counterexample, finite-crossing,
  distinct-odd-input hypotheses and E28, either G270 has `Y_q<2N` and every
  safe prefix is same-Q geodesic, or H270 has
  `N<q/270`, `Y_q,X<q/135`, `Z<2q/135`.
- P105 `VERIFIED_THEOREM`: the first-passage exponent code satisfies
  `sum 3^-r c^2=1` and `4/(9t^2)<sum 3^-r<=1/t^2`.
- P106 `VERIFIED_THEOREM`: the 11-word r=4 code is suffix-decodable at every
  block count; its exact `s=2` moment is `1539/2048`.
- E28 `VERIFIED_FINITE`: every `1<=n<300000` reaches 1 under the shortcut map.
- E29 `VERIFIED_FINITE`: all 23 supercritical exponent words at r<=4, the
  mod-81/mod-648 tables, exact 270 log certificate, three-block code audit,
  and 62 adversarial rows are independently reconstructed.
- NG29 `REFUTED`: the precisely scoped coefficient-only summed-Haar envelope
  cannot drive its normalized cutoff beyond `360.469`.
- H104 and H105 remain `OPEN`; `proves_collatz=false`.

## Proposal corrections

The exact inverse formula has positive affine correction, so a predecessor is
forbidden at `y/N=c` as well as below it. The stored threshold table admits a
class at equality and is therefore a safe right-continuous upper envelope,
not an exact boundary classification.

First-passage exponent cylinders are disjoint in exponent-sequence space, but
their 3-adic endpoint cylinders may collide. The exact word-mass identity
therefore supplies only an upper union-measure bound. It is not an ordinary
representative count.

The r=4 code proves suffix decodability. No monotonicity or convergence of
finite pressure roots is inferred from its one finite moment.

## Exact finite data

```text
supercritical exponent words, r<=4: 23
mod-648 allowed counts:              51,66,72,117,129,172,192,204,212,216
continuous capacity:                 23093/20736
reciprocal error coefficient:        18344/27
U(270):                              5610619/6912
direct sources checked:              299999
maximum shortcut steps:              278 at least source 230631
maximum peak:                        12324038948 at least source 270271
direct row digest:                   573dba321ea39a77547fe3202a74d26b
                                      f37b988628fd7567b9ae2924f6d62ed2
r=4 suffix code size:                11
finite concatenations:               11,121,1331 with no endpoint collision
```

The 270 logarithm comparison uses 12 rational atanh-series terms plus an exact
geometric tail. No floating-point value decides acceptance.

## Reproduction

```bash
.venv/bin/python src/phase17_search.py \
  --artifact-dir artifacts --direct-bound 300000
.venv/bin/python verifier/verify_phase17.py \
  --artifact-dir artifacts --write-report artifacts/phase17_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase17_properties.py tests/test_phase17_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier contains none of `phase17_search`, `from src`, or `import src`.
It reconstructs affine constants by an explicit sum, enumerates compositions
recursively, scans the finite Collatz range in descending order, and checks
the stored report and scope boundaries. Tamper tests alter the CRT count,
exact log margin, equality convention, direct digest, Haar union boundary,
suffix digest, adversarial digest, and obstruction report.

The result commit, test counts, timings, and manifest hash are fixed in
`research/experiments/phase17-predecessor-pressure.json`.

```text
generator full n<300000:           completed in 1.90s
independent verifier full range:   valid=true in 2.03s
focused Phase 17/health suite:     15 passed in 7.13s
complete repository suite:        268 passed in 335.16s
strict research health:           valid=true, untracked artifacts=0
global SHA-256 manifest:           ea932e96e56ef2692de6879b411b0efa
                                      638c3cb0783ddbc20bd4722d8f1e8d1c
```

## What this result does not prove

- H104/G270 or H105/H270;
- the repeated periodic/nontrivial-cycle branch;
- H89, H72, or an eventual lower bound for `M_star`;
- an asymptotic result from r<=4, three blocks, or `n<300000`;
- the Collatz conjecture.

`proves_collatz=false`.
