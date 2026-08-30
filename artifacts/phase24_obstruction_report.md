# Phase 24 obstruction report

## Exact result at area two

The sparse circular-arc certificate and the exact residue-profile recurrence
exclude every coprime area-two positive cycle profile.  The critical large-q
step uses EXT05; the critical `q<=60` and noncritical `L<=21` remainders are
independently exhaustive.

## Smallest next obstruction

At area three the reduced polynomial can have seven nonzero terms.  The generic
largest-gap estimate gives only `W/q<=6/7`, while
`3^6*25^7 > 64^7`; cardinality alone therefore misses the EXT05 exponent.

The bounded diagnostic through `q<=100` reconstructed
`521154` valid critical coprime area-three
profiles.  Its worst one-sided q-arc ratio is
`35/41`.  Allowing the diagnostic
q/L symmetric choice gives worst effective ratio
`80/94`.  There were
`0` failures of the exact comparison
`3^W*25^d<64^d` in this finite scope.

This is a finite diagnostic only (`VERIFIED_FINITE`), not an all-q theorem.
The missing step is a uniform
paired-support gap for the valid area-three shapes, followed by a mechanism for
arbitrary area.  General noncoprime profiles remain outside the coprime slope
root bijection.

## What this result does not prove

It does not exclude area-three or arbitrary-area coprime cycles, noncoprime
cycles, any nonperiodic counterexample branch, or the Collatz conjecture.
`proves_collatz=false`.
