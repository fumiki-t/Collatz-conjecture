# Phase 16 obstruction report

## NG28 — positive same-Q carry

`REFUTED`.  The stored Q=26 pair is coefficient-safe, shares canonical
endpoint 716727426419, and has carry -3.  Thus positivity cannot be used as a
prefix recursion invariant.  P97 retains the sharp elementary lower bounds;
in particular a negative carry requires `2^k<q`.

## G250 — contact-rich all-prefix geodesic branch

`OPEN`.  Phase 16 proves geodesicity when `q<=250N`, but high contact density
plus geodesicity is consistent with finite prefixes of the formal all-contact
2-adic word.  A successful exclusion must retain one fixed positive ordinary
source and survive NG17, P73, NG24--NG28, and the mandatory families.

## H250 — ultra-low two-sided height branch

`OPEN`.  When `q>250N`, the exact packing argument gives `X<q/125` and
`Z<2q/125`.  No accepted automaton, transducer, pumping, or meet-in-the-middle
certificate currently proves this two-sided box empty.

## Periodic branch

`OPEN`.  The 250 packing uses distinct odd orbit values.  Without distinctness
Phase 16 retains only `Y_q<N+q/3`, hence the `q<3N` geodesic alternative or
the bounds `N<=q/3`, `X<2q/3`.  It does not eliminate a nontrivial cycle.

## What this result does not prove

It does not exclude G250, H250, the periodic branch, H89, H72, or any Collatz
counterexample.  The Q<=17 layer table is finite.  `proves_collatz=false`.
