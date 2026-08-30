# Phase 25 run results — Hamming support and resonant area three

**Date:** 2026-08-30
**Branch:** `feat/phase25-hamming-resonance`
**Repository status:** `OPEN`
**`proves_collatz=false`**

The supplied Phase 25 note was treated as an untrusted proposal.  Its Hamming
lemmas and exact seven-grid resultant mechanism survive independent audit.
Its proposed universal two-arc gap is false, and its displayed L-arc residue
list for the falsifier contained arithmetic errors.

## Accepted claim boundary

- `P151 VERIFIED_THEOREM`: changing `H` positions in equal-length words adds
  at most `nH` linear or cyclic length-`n` factors.  Hence critical defect
  support `s` gives `p_w(n)<=(2s+1)n+2`, and coprime cycle support gives
  `p_cyc(n)<=(2s+1)n+1`.
- `P152 CONDITIONAL`: under P54 and pairwise-distinct critical states,
  `q<=(2n_q+1)s+2n_q+2`.  Reusing the explicitly labelled Phase 7 EXT04
  enclosure gives `n_q0=73` and `s>=490186612`.
- `P153 CONDITIONAL`: every positive defect loses more than `1/4` normalized
  correction, so P54 implies `s<4(S0-3N delta_q)`.  At q0, X02 gives only
  `s<=49708569439`; the two exact bounds do not contradict one another.
- `P154 VERIFIED_THEOREM`: an integral coprime resonant-grid profile forces a
  nonzero integer resultant divisible by `D`, with an exact conjugate-product
  magnitude bound.
- `P155 VERIFIED_THEOREM`: the critical coprime area-three family with roots
  `Q,2Q,3Q` and `q=7Q` is impossible.  `Q>=11` uses EXT05; every smaller
  coprime row is checked directly.
- `E37 VERIFIED_FINITE`: the bounded Hamming, profile, q0 interval,
  falsifier, interval, and finite resultant audits were independently rebuilt.
- `NG34 REFUTED`: it is false that every valid critical Type-C profile meets
  at least one of the two Phase 24 arc thresholds.
- `H147 OPEN`: exact low-denominator resonance is only one subfamily;
  near-resonant Type-C profiles, the collapsed Type-A/B families, arbitrary
  area, and noncoprime slopes remain open.

## Exact finite audit

The generator and independent verifier agree on:

- 502,523 critical first-crossing words through `q<=17`;
- 82,227 literal critical factor checks through `q<=12`;
- 33,577 critical coprime area-three profiles through `q<=50`;
- area-three type counts `133`, `5,472`, and `27,972` for doubled-root,
  root-child-plus-root, and three-root profiles;
- 167,884 selected cyclic factor checks;
- `|Res(Z^7-2,Z+Z^2+Z^3-1)|=209`;
- the first exact analytic threshold `Q=11`;
- direct gcd one for every coprime `1<=Q<=10` seven-grid row.

The mandatory large falsifier is

```text
q=63322, L=100363, roots=(9046,18092,27138)
q points=(0,9046,17997,27138,36089,45230,54181), Wq=54181
L points=(0,14338,28525,43013,57200,71688,85875), WL=85875
gcd(Q_a(gamma),D)=1
```

Both exact comparisons `3^W*25^d>=64^d` hold, so it refutes the naive paired
arc threshold.  The supplied note instead listed
`0,14488,28675,43163,57350,71838,86025`; that list was not accepted.  The
correct width remains 85875, and the profile is nonintegral.

## Independence and tamper rejection

The generator uses classified Phase 23/24 objects and a seven-dimensional
quotient-ring norm.  The verifier imports no production search module.  It
instead enumerates weak profiles, reconstructs literal exponent words, uses a
shifted Bezout root, independently encloses logarithms and conjugates, and
computes resultants from Sylvester matrices.  Tests reject altered claim
status, q0 width, and `proves_collatz` metadata.

## Reproduction

```bash
.venv/bin/python src/phase25_search.py --artifact-dir artifacts
.venv/bin/python verifier/verify_phase25.py \
  --artifact-dir artifacts --output artifacts/phase25_verifier.json
.venv/bin/python -m pytest -q \
  tests/test_phase25_properties.py tests/test_phase25_verifier.py \
  tests/test_research_health.py
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
.venv/bin/python scripts/research_health.py --strict
git diff --check
```

Acceptance commit, test totals, verifier result, and manifest SHA-256 are
filled into the experiment manifest after the clean acceptance run.

## What this result does not prove

Phase 25 does not exclude all area-three coprime cycles, arbitrary-area or
noncoprime cycles, H89, H133, H147, H72, or the Collatz conjecture.
`proves_collatz=false`.
