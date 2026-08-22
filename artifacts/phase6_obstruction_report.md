# Phase 6 critical-prefix barrier report

This report does not claim a proof of the Collatz conjecture.

## SYMBOLIC_THEOREM_VERIFIED

- P54 is algebraically correct under its stated least-counterexample and first-crossing assumptions.
- The independent verifier reconstructs the final-even argument, `K=bitlength(3^q)`, the odd-position bound, `B<=B_q^max`, and `D_q*N<=B`.
- It also checks `H_q>q/6`, monotonicity of `M`, and the sparse barrier-record reduction.
- These are conditional symbolic implications, not an existence proof for an eventual lower bound on `M(k)`.

## EXACT_H_Q_RECORDS

- Every `q` through `200000` was scanned using integer arithmetic; `37` exact records were found.
- The last record in the requested scan is `q=190537`, `K_q=301994`, `floor(H_q)=710220447737`.
- The twelve supplied sanity indices are reproduced exactly.

## EXACT_FINITE_CERTIFICATES

- `14` barrier-record inequalities are independently certificate-checkable.
- Exact barrier coverage is `q=94..4960` by the sparse-record implication.
- Exact counterexamples at attempted failed records: `[(17, 27), (29, 27), (41, 703)]`.
- No success rate is promoted to an asymptotic statement.

## EXACT_DIRECT_M_SEARCH

- Direct exact prefix search ends at `1500000` and found `13` coefficient-stopping records.
- It determines `M(k)` exactly through `k=223`.
- For `66<=K_q<=224`, the minimum is exact at `q=46`, `K_q=73`, `M=703` with ratio `409001776799012900018489/98878719971867038884317>4`.

## EXTERNAL_RECORD_EVIDENCE

- All `35` supplied starts reproduce both listed dropping time and coefficient stopping time.
- Their asserted record minimality is not verified and is used only in this section.
- Under that external assumption, the last failure is `q=41, K_q=65`.
- For `66<=K_q<=1005`, the minimum exact ratio occurs at `q=46`, `K_q=73`, assumed `M=703` and is greater than four.

## ADVERSARIAL_AND_NO_GO_AUDIT

- `2^m-1`, `8^m-5`, `(110|111)^*`, `A=11101`, `B=1100`, and the eight exact `A^rB^s` records are retained in the artifact.
- Exact `A^rB^s` records shrink the terminal coefficient margin below `2^-13`; rejecting every fixed positive margin additionally uses the explicitly named density theorem from Phase 5.
- `W=111011100` rejects completeness of the four canonical rational-shadow centers.
- Bounded survival of the block languages rejects promotion of a bounded finite-state test to an eventual theorem.

## HEURISTIC_AND_CONJECTURE

- No rigorous eventual polynomial lower bound for `M(k)` was found.
- Meet-in-the-middle anti-concentration, continued-fraction forcing, and a bound exceeding `H_q=O(q^5.117)` remain research directions, not verified results.
- The Wu-Wang Diophantine estimate is not independently proved or used by any finite certificate here.
