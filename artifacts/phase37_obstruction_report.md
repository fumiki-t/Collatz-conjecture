# Phase 37 boundary report

The location-uniform recursion survives exact audit.  Its key operation is
legitimate because, at fixed odd count, every `T^N` image has the same slope
and all affine corrections occupy a translation-independent interval.  The
image of each low-count slice is itself equal-time collision-free.

The rational specialization closes with the fully explicit bound
`G(X)<32 X^(29/30)`.  The exact low-part threshold is `N0=135`; it fails at
`N=134`, so the finite base is not silently omitted.  The general limiting
exponent follows by the same strong-induction argument, not by extrapolating
the finite audit.

One quantifier from the supplied note needs to be made explicit: reciprocal
summability, `z_i -> 0`, and the cycle cutoff choose
`rho_* < rho < 1`.  This is possible because `rho_*<29/30<1` and does not
invalidate the candidate conclusions.

## Live obstruction

Uniform sparsity counts points on one equal-time collision-free set.  P80
requires control of multiplicity across many canonical renewal addresses.
Neither this theorem nor its improved density-one defect exponent supplies a
last-occurrence bound, a positive-source lift obstruction, or extinction of
the P81/P86 irreducible tree.  NG22 therefore remains valid.

The cycle consequence gives only an effective finite range for noncritical
minimum values.  It neither computes a practical optimized cutoff nor
excludes critical or arbitrary-area cycles.

## What this result does not prove

It does not prove H72, H133, or the Collatz conjecture.  Both the nontrivial
positive-cycle branch and the permanent-safe nonperiodic branch remain open.
`proves_collatz=false`.
