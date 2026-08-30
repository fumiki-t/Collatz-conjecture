# Phase 25 obstruction report

## Naive paired-arc threshold is false

The exact valid Type-C row `q=63322`, `L=100363` with
roots `[9046, 18092, 27138]` has q-arc width
`54181` and L-arc width `85875`.
Both exact EXT05 threshold comparisons fail.  Direct modular evaluation has
gcd `1` with `D`, so this is not an integral
cycle witness.  It refutes only the proposed uniform two-arc gap.

The proposal's displayed L-arc residue list was not exact.  The independently
reconstructed list is `[0, 14338, 28525, 43013, 57200, 71688, 85875]`; the width remains
`85875`, so the falsification itself survives.

## Exact resonance covers one family, not a neighbourhood

The resultant certificate excludes the exact seven-grid coprime family.  It
does not provide an inverse theorem saying that every two-arc failure is an
exact or controlled near-grid.  Near-resonant Type-C triples are the smallest
remaining H147 obstruction.

## Critical support squeeze remains open

Under its explicit P54/distinct-state/EXT04 assumptions, the q0 lower bound is
`490186612`.  The X02 correction upper bound is
`49708569439`, so the exact squeeze does not
exclude q0.

## What this result does not prove

It does not exclude all area-three coprime cycles, noncoprime or arbitrary-area
cycles, a least counterexample, or the Collatz conjecture.
`proves_collatz=false`.
