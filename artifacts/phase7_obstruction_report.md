# Phase 7 boundary-defect obstruction report

This report does not claim a proof of the Collatz conjecture.

## VERIFIED_SYMBOLIC

- Under the least-counterexample and first-crossing assumptions, the independent algebra gives `S(a)>=3*N*delta` and `W(C)>=6*N*delta-S0`.
- This identity uses no external theorem. The substitution `N>V` is explicitly external computational evidence.

## EXACT_FINITE_CERTIFICATE

- Exact logarithm enclosures and Stern--Brocot parents certify the first necessary pair `(q,K)=(72057431991,114208327604)` without constructing giant powers.
- With the external inputs separated, the certified contact count is at least `31327720462`, exceeding 43 percent of q0.
- For h=12 the certified contact-pair lower bound is `889748829`.
- The exact 12-odd contact-return alphabet has `87015` macros across 13 mechanical factors.
- Fixed-(k,q) arithmetic layers q=1,3,5,17 reproduce the selected A100982 counts and have distinct 2-adic residues.

## EXTERNAL_MATH_INPUT

- `DENJOY_KOKSMA` is used for rotation sums and discrepancy. Its two consecutive continued-fraction denominator premises are checked exactly, but the theorem is not reproved here.
- Terras, Garner, Rozier--Terracol, Hikawa, A076227, and A100982 show substantial prior overlap. Tong Niu's 2026 preprint is withdrawn and is not used as authority.

## EXTERNAL_COMPUTATIONAL_INPUT

- `N>2392312122059207475200` is assumed only as the supplied external verification bound. Its provenance/global verification is not reproduced.

## FAILED_HYPOTHESIS

- every contact-return macro has multiplier < 1: smallest exact counterexample macro id `0`.
- every contact-return macro is a concatenation of the four Phase 5 dangerous words: smallest exact counterexample macro id `0`.
- contact-return macros are arithmetically unrealizable over positive integers: smallest exact counterexample macro id `0`.

## HEURISTIC / CONJECTURE

- Finite Pareto fronts suggest a high-B/small-r2 tension, but no q-uniform monotonicity or separation lemma was found.
- The contracting `A^rB^s` endpoint candidate has no counterexample in the exact bounded scope, but remains `OPEN` rather than a theorem.

## Main obstruction

The analytic argument forces many contacts and contact pairs, but the 87,015-macro alphabet contains noncontracting, non-dangerous-decomposable, and positively realizable macros. No theorem links high correction B to a sufficiently large least positive 2-adic representative for unbounded q.

## What this result does not prove

It does not exclude a least counterexample, prove an eventual lower bound for M(k), or prove the Collatz conjecture. All huge-q contact conclusions depend on the external N>V computation and the named Denjoy--Koksma theorem.
