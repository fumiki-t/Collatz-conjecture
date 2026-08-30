# Phase 23 obstruction report

## Exact finite audit

- critical first-crossing words through `q<=17`: `502523`;
- area-only rejections in that range: `31`;
- direct factor-width checks through `q<=12`: `82227`;
- bounded coprime cycle profiles: `4786`;
- cyclic factor-width checks: `156178`.

These are exact bounded computations.  They do not imply an eventual area
lower bound beyond the proved conditional inequalities.

## Proposal repairs

1. The critical repetition certificate explicitly retains P54 and pairwise
   state distinctness.  It is not applied to a periodic branch.
2. The cycle edit identity is proved only after converting the residue-indexed
   Phase 22 profile back to time order and then to the literal expanded word.
3. The cycle height/separation result is restricted to primitive positive
   integer cycles.  Rational noninteger fixed points and both stored negative
   cycles are regression controls, not theorem inputs.
4. No exact `n_q0` was certified from the existing Phase 7 symbolic inputs.
   The proposed giant q0 area number therefore remains conditional rather than
   being replaced by floating-point logarithms.
5. The suggested Wu--Wang/polynomial-height and polynomial cycle-minimum inputs
   were not accepted.  P143 and P146 preserve them as explicit hypotheses.

## Remaining obstruction

Area may be concentrated in a small number of deep excursions.  Neither the
linear factor bound nor the triangular height bound forces the correction sum
to be small.  H141 is the exact missing optimization/ordinary-source bridge;
H89 and H133 remain open.

## What this result does not prove

It does not prove the q0 candidate impossible, exclude every nontrivial cycle,
prove H89, H133, H112, H72, or prove the Collatz conjecture.
`proves_collatz=false`.
