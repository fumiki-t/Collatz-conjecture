# Phase 7 boundary-defect arithmetic: run results

Branch: `feat/phase7-boundary-defect-arithmetic`

Phase 7 does not prove or disprove the Collatz conjecture. It converts the
least-counterexample first-crossing scenario into exact boundary-defect
constraints, then records where the analytic and finite-macro routes stop.

## Acceptance commands

```bash
.venv/bin/python src/phase7_search.py \
  --artifact-dir artifacts --mixed-bound 128
.venv/bin/python verifier/verify_phase7.py \
  --artifact-dir artifacts
.venv/bin/python -m pytest -q
.venv/bin/python scripts/hash_artifacts.py artifacts \
  --write artifacts/SHA256SUMS
```

The search and verifier share no implementation import. The verifier rebuilds
the logarithm enclosures, Stern--Brocot certificate, contact bounds, all 87,015
macro rows, every selected fixed layer, and the bounded mixed-block audit. A
test changes one stored affine constant and requires rejection.

Acceptance result: `154 passed in 137.78s`. The focused Phase 7 set contributes
five tests, including the full independent-verifier and tamper-rejection run.

## VERIFIED_SYMBOLIC

Under the explicitly stated least-positive-counterexample and first-crossing
assumptions, direct affine expansion gives

```text
B/3^(q-1) = S(a)
S(a) >= 3*N*delta
S(a) <= (S0+W(C))/2
W(C) >= 6*N*delta-S0.
```

This algebra does not use Denjoy--Koksma or the external verification bound.
It is a conditional implication: it does not establish that a counterexample
exists.

The fixed-`(k,q)` inverse-parity calculation also independently reconstructs
the 2-adic rigidity statement: parity words that first differ at bit `i`
choose different lifts modulo `2^(i+1)`, and hence different residues modulo
`2^k`.

## EXACT_FINITE_CERTIFICATE

Exact rational log enclosures place the first admissible rational between
`log2(3)` and `log2(3+1/V)` at

```text
q0 = 72,057,431,991
K0 = 114,208,327,604.
```

Its Stern--Brocot parents are

```text
103,768,467,013 / 65,470,613,321
10,439,860,591 / 6,586,818,670.
```

They are Farey neighbors and consecutive certified continued-fraction
convergents; their numerator and denominator sums give `K0/q0`. Therefore the
Farey-neighbor denominator lemma establishes minimality without constructing
`3^q0` or `2^K0`.

After substituting the separated external inputs, the exact certificates give:

| quantity | rigorous lower bound |
|---|---:|
| contacts `|C|` | 31,327,720,462 |
| contact density | greater than 43% |
| nonwrapped pairs, `h=12` | 889,748,829 |
| nonwrapped pairs, `h=41` | 1,098,696,479 |
| nonwrapped pairs, `h=53` | 2,053,484,375 |
| nonwrapped pairs, `h=306` | 2,163,774,115 |
| nonwrapped pairs, `h=665` | 2,265,341,609 |

For autocorrelation the certificate first proves a cyclic weighted-overlap
bound. The cyclic variation includes an exact `h/2` endpoint-wrap allowance;
the displayed genuine `0 <= j < j+h < q0` counts then remove at most `h`
cyclic pairs. In particular, the approximately `8.9e8` sanity value is a
derived result, not an input.

The exact 12-odd contact-return enumeration independently found 13 mechanical
intercept classes and the following class sizes:

```text
2652, 2862, 3387, 3733, 4072, 5033, 5393,
8045, 8640, 9690, 10642, 11433, 11433
```

Their sum is 87,015. Every artifact row includes its defect path, parity word,
affine map, multiplier/intercept/fixed point, exact power-of-two residue,
mod-9/mod-27 endpoint data, and Phase 5 dangerous-word decomposition.

The arithmetic-frontier enumeration reproduced the selected A100982 layer
counts `1, 2, 7, 312455` at `q=1,3,5,17`. The corresponding exact Pareto
fronts contain `1,1,3,13` records. These remain finite-layer certificates.

The mandatory `A=11101`, `B=1100`, `A^rB^s` audit checked all 16,384 pairs
with `1 <= r,s <= 128`; 5,051 have total multiplier below one and none has a
positive integral realization whose endpoint exceeds its source.

## EXTERNAL_MATH_INPUT

`DENJOY_KOKSMA` is used, without being reproved, for bounded-variation rotation
sums. The certificate exactly checks

```text
q0 = 6,586,818,670 + 65,470,613,321
```

and that the summands are consecutive continued-fraction denominators. It then
uses the two-block error bound
`|S0-q0/(2*ln(2))| <= 2`. No theorem conclusion is accepted through floating
point arithmetic.

## EXTERNAL_COMPUTATIONAL_INPUT

`N > V`, where `V=2075*2^60`, is used only as supplied external evidence. This
repository does not reproduce the global computation or certify its minimal
provenance. All consequences after the substitution are checked exactly.

## Literature and overlap audit

- Terras's 1976 coefficient-stopping/admissible-vector formulation already
  contains the classical parity-prefix setting. Phase 6 safe prefixes are the
  complementary unconverged-prefix language, not a newly discovered counting
  sequence.
- Garner (1981) already uses convergents of `log2(3)` with a verified search
  bound. The Phase 7 contribution is the repository's exact enclosure and
  certificate composition, not the continued-fraction idea.
- Rozier--Terracol (2026) studies paradoxical finite Collatz sequences in the
  same coefficient-safe region. Tong Niu's arXiv:2605.13886 was withdrawn
  after acknowledging that the relevant enumeration was already present in
  Rozier--Terracol v4, so it is not used as authority.
- Hikawa's 2026 preprint discusses finite-dimensional parity-vector arithmetic
  and explicitly identifies its counting sequences with OEIS A100982 and
  A076227. Its rigidity theme overlaps the independently reconstructed
  fixed-layer calculation here.
- A076227 is the Phase 1/6 safe-prefix count, including `a(26)=1,037,374`.
  A100982 supplies the fixed-odd-order admissible counts reproduced above.
- The Phase 6 obstruction `q=4961` is continued-fraction structured:
  `4961=4296+665`, and `665` is the denominator of the convergent `1054/665`
  to `log2(3)`. It is the next `H_q` record after `q=4296`, consistent with the
  Garner mechanism rather than an independent new phenomenon.

Primary references are recorded in `docs/LITERATURE.md`; machine-readable
overlap labels are also included in `phase7_boundary_defect.json`.

## FAILED_HYPOTHESIS

Three natural universal macro shortcuts fail at exact macro id 0, whose word
is `1111111111110000000` and whose multiplier is `3^12/2^19 > 1`:

1. Every contact-return macro contracts.
2. Every contact-return macro decomposes into the four Phase 5 dangerous words.
3. Every contact-return macro is arithmetically unrealizable over positive
   integers.

Thus the finite alphabet supplies no uniform descent theorem, compulsory
dangerous-family theorem, or arithmetic incompatibility.

## HEURISTIC / CONJECTURE / OPEN

The finite Pareto fronts suggest tension between high correction `B` and a
small positive 2-adic representative `r2`, but no monotonicity, separation
inequality, or `q`-uniform tradeoff was found. This is the main exact
obstruction left by Phase 7.

The bounded `A^rB^s` result supports the candidate statement that a contracting
positive integral realization cannot have a paradoxical endpoint, but it does
not prove it for arbitrary `r,s`; the universal claim remains `OPEN`.

## What this result does not prove

Phase 7 does not exclude a least counterexample, prove an eventual lower bound
for `M(k)`, turn finite-layer correlation into an asymptotic theorem, or prove
the Collatz conjecture. Its huge-`q` contact conclusions depend explicitly on
the external `N>V` computation and Denjoy--Koksma theorem.

## SHA-256

The complete repository manifest is `artifacts/SHA256SUMS`. Phase 7 entries:

```text
adfb7a2c6a4766020fcd103a29e75702b7fe9348bdae5d3337f44ff9cea22107  phase7_arithmetic_frontier.json
44c6ab7c6d58314e59b3d8d2000d376b44c835b001be64f9468de94ece5ea252  phase7_boundary_defect.json
eb96fef01b7e09b8ee9551e3ae1b9736d07b0aa1a8cf93b9ac16ff3b820cdae5  phase7_contact_autocorrelation.json
1f6722d4db1aa2acc2d1cd5fda538af4cf1b4e34a7ed20e80b6cbf3614caa379  phase7_macro12.json
5fd7471952aab4302a338c03570fa9ac82c86230eaef6274e465b80fb0a0e3c8  phase7_obstruction_report.md
a902d726a1779dc4abc1d67c19f2ea30cc0ea82516dd665271092c0777b35ea7  phase7_symbolic_certificate.json
687e28e2f52385a1090b43dc2bed64b75db898205046cc6c50b9a14cae3a3000  phase7_symbolic_verifier.json
```
