# Phase 18 obstruction report

## NG30 — single-mountain SCC normal form (`REFUTED`)

The proposed statement that every long bounded-final-discrepancy safe path in
a graph without mixed SCCs is, modulo bounded connectors, one positive packet
followed by one negative packet is false.

Take a four-state chain whose successive loop signs are positive, negative,
positive, negative; label the positive loops and connecting edges by `1`, and
the negative loops by `0`.  For every `k>=2`, put

```text
n1 = floor(log2((3/2)^k))
R  = 4k+3
n2 = floor(log2((3/2)^R))-n1
w_k = 1^(2k+1) 0^n1 1^(2k+2) 0^n2.
```

Integer bit lengths compute both floors exactly.  Every prefix has multiplier
strictly greater than one, the final multiplier lies strictly between one and
two, and all four loop packets grow without bound.  Therefore the intervening
negative packet cannot be absorbed into a bounded connector.

What survives is P108's finite-stage normal form: paths traverse the acyclic
SCC condensation, with a graph-bounded number of sign-pure cycle packets and
bounded connectors.  A one-switch order is not guaranteed.

## Smallest stored witness

The generated theory artifact stores the exact `k=2` witness and larger
regressions.  This is a structural counterexample, not a Collatz orbit.

## Open applicability obstruction

The accepted project models are not a prefix-complete closed finite graph for
the full H72 language.  Phase 7/8 free concatenations are overapproximations;
Phase 10/11/13 use growing state; Phase 14 is not left-closed by NG24; Phase 16
is a local sieve; and Phase 17 is an expanding sublanguage.  The finite-state
theorems therefore do not close H72.

## What this result does not prove

It does not construct a positive ordinary Collatz source, exclude all paths in
a mixed SCC, prove H72, exclude cycles, or prove the Collatz conjecture.
`proves_collatz=false`.
