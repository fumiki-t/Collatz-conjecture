# Phase 27 obstruction report

## Rotation alignment is false for positive rational shadows

The lexicographically first complete-corpus obstruction is

```text
q=2, L=4, e=(1, 3)
odd orbit: 5/7 -> 11/7 -> 5/7
least-value offset: 0
discrepancy-minimum offset: 1
```

Thus P133's least-value coordinates cannot be combined with P156's
nonnegative reduced profile without an additional alignment theorem.  The
counterexample is positive rational but not integral; alignment for a
hypothetical positive integer cycle remains open.

## The critical external constant is effective but impractical

Matveev's theorem is specialized with the safe integer majorant
`K=1564920000`.  It proves a polynomial gap and hence the asymptotic theorem,
but its finite scalar envelope is far weaker than Phase 26's EXT05 bound in
the ranges of practical interest.  Effectiveness is not practical exclusion.

## The exponent boundary is structural, not a cycle construction

The synthetic tall and diffuse rows are valid reduced profiles only.  They
show why P156/P157 plus a polynomial gap naturally meet at area exponent
`2/3` and support exponent `1/2`; they are not positive integer cycles and do
not prove those exponents optimal for actual Collatz cycles.

## What this result does not prove

Phase 27 does not exclude critical area six, large noncritical area, either
tall or diffuse profiles, arbitrary primitive positive cycles, nonperiodic
counterexamples, or the Collatz conjecture. `proves_collatz=false`.
