# Phase 14 obstruction report

Phase 14 does not prove or disprove the Collatz conjecture.

## Quotient obstruction

Coalescent equivalence is preserved by appending the same renewal suffix, but
not by prepending an arbitrary renewal block.  The minimum collision
`11101 ~ 111100` has common endpoint residue 20 modulo `3^4`; prepending
`110` gives endpoint residues 263 and 587 modulo `3^6`.  Therefore a quotient
that remembers only the coalescent class is not a two-sided block transfer
operator.  This is NG24.

## Finite pressure boundary

The exhaustive `Q<=13` graph has unique finite normal forms and fewer
irreducible addresses at every audited block depth.  This is finite evidence.
Right-ideal closure of a finite rewrite list changes only a prefix mass; no
closed all-depth recursion or asymptotic irreducible pressure was proved.

## Moving-shadow boundary

The proposed reduced-denominator and gcd bounds are proved once `a_n>=1`,
and hence eventually under P76's reciprocal-summability hypothesis.  The
unqualified small-index case `a_n=0` is not accepted.

## What this result does not prove

- global rewrite confluence or a unique normal form at every `Q`;
- either anti-concentration premise in P80;
- exclusion of every positive permanent-safe source;
- H72 or exclusion of nontrivial cycles;
- the Collatz conjecture.

`proves_collatz=false`.
