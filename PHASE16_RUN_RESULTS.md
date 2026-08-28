# Phase 16: critical geodesic / ultra-low-height dichotomy — run results

Branch: `feat/phase16-critical-dichotomy`

Base commit: `ba57e623f62e76a3d4bee0bcd55ee44afb023605`

Result commit: recorded by the accepted experiment manifest

Phase 16 treats the supplied v2 note as an untrusted proposal. It repairs its
q=1 strict inequality and the low-`t` packing domain, proves exact carry,
geodesic, local-merge, residue-packing, and finite-crossing dichotomy lemmas,
and preserves the periodic branch. It does not exclude either side of the new
dichotomy or prove the Collatz conjecture.

The detailed proofs and quantifiers are in
[`research/audits/critical-dichotomy/REPORT.md`](research/audits/critical-dichotomy/REPORT.md).

## Accepted results

- P97 `VERIFIED_THEOREM`: corrected safe-correction and signed carry bounds.
- P98 `VERIFIED_THEOREM`: exact normalized correction and prefix-closed
  same-Q geodesic criterion under P89.
- P99 `VERIFIED_THEOREM`: literal mod-3/mod-9, odd-even-even, and all-odd
  merge restrictions. Angeltveit is context only, not a dependency.
- P100 `VERIFIED_THEOREM`: exact mod-72 counts `6,9,15,20,24` and reciprocal
  packing bound for distinct odd inputs.
- P101 `VERIFIED_THEOREM`: for `N>=100000` and distinct odd inputs before
  crossing, either G250 is all-prefix geodesic or H250 has
  `N<q/250`, `X<q/125`, `Z<2q/125`.
- P102 `VERIFIED_THEOREM`: without distinctness, the valid fallback is the
  factor-3 geodesic/height split.
- P103 `CONDITIONAL`: the Phase 7 q0 critical word is all-prefix geodesic under
  P54's framework and X02.
- E27 `VERIFIED_FINITE`: exhaustive Q<=17 layer/carry audit and 68 adversarial
  rows.
- NG28 `REFUTED`: universal positive same-Q carry fails at Q=26 with carry
  -3.
- H97 and H98 remain `OPEN`; `proves_collatz=false`.

## Proposal corrections

The proposal stated `B/3^q<q/3` for every safe word. At q=1, word `1` has
equality. The accepted P97 statement is equality at q=1 and strict bounds for
q>=2. Every distinct-length same-Q pair has q>=2, so the carry conclusions are
unchanged.

The displayed `Phi(t)` begins at `t=133/576`. The G250 proof handles smaller
`t` directly with `Y_q<=N+q/3<2N`; it does not extrapolate `Phi` outside its
packing domain.

## Exact negative-carry obstruction

```text
a=111111111101111110101011110010001001100
d=1101101101110011100111011101010101101101
Q=26, L(a)=39, L(d)=40
S(a)=155014110207
S(d)=310028220411
common endpoint=716727426419
2B(a)-B(d)=-3*3^26
```

Both words and the common endpoint are reconstructed by the generator and the
independent verifier from literal parity traces.

## Q=17 finite layer

| classification | count |
|---|---:|
| safe words over all lengths | 663,535 |
| critical words | 312,455 |
| same-Q geodesic | 253,018 |
| all-prefix same-Q geodesic | 253,018 |
| contact-rich | 32,813 |
| contact-rich geodesic | 27,949 |

`contact-rich` is an explicit finite diagnostic:
`100*contacts>43*Q`. The exact equality between the two geodesic columns
independently checks prefix closure. Across all Q<=17 layers there are 225,943
same-Q endpoint pairs, no negative carry, and minimum carry 1. This is finite
and does not conflict with NG28 at Q=26.

## Exact logarithm certificate

The comparison

```text
Phi(250)+75/100000 < 3*log(2)
```

uses 12 rational terms of the positive atanh series and a geometric tail. The
large ratio is reduced by
`144299/324=2^8*(144299/82944)`. The stored rational margin is strictly
positive; no floating-point comparison decides acceptance.

## Reproduction

```bash
.venv/bin/python src/phase16_search.py \
  --artifact-dir artifacts --maximum-q 17
.venv/bin/python verifier/verify_phase16.py \
  --artifact-dir artifacts --output artifacts/phase16_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase16_properties.py tests/test_phase16_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

The verifier contains none of `phase16_search`, `from src`, or `import src`.
It enumerates literal strings in reverse frontier order and reconstructs each
affine constant as an explicit odd-position sum. Tamper tests alter carry,
the exact log margin, the periodic scope, finite counts, adversarial digest,
and the obstruction report.

Acceptance checks and the global manifest SHA-256 are recorded in
`research/experiments/phase16-critical-dichotomy.json` after the result commit.

```text
generator full Q<=17:             completed in 45.35s
independent verifier full Q<=17:  valid=true in 177.05s
focused Phase 16/health suite:    16 passed in 5.19s
complete repository suite:       258 passed in 318.81s
strict research health:           valid=true, untracked artifacts=0
```

## What this result does not prove

- H97/G250 or H98/H250;
- the repeated periodic/nontrivial-cycle branch;
- H89, H72, or an eventual lower bound for `M_star`;
- any asymptotic conclusion from Q<=17;
- the Collatz conjecture.

`proves_collatz=false`.
