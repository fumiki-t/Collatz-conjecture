# Phase 4 return-map obstruction report

This report does not claim a proof of the Collatz conjecture.

## Algebraically verified theorem (return map only)

- The mod-9 first-return code has the exact three parametric forms and two special words from the brief.
- The code is prefix-free and its exact Kraft sum is 1; concatenated excursions retain full binary entropy.
- Every stored return template satisfies the n-coordinate formula, z-coordinate formula, mod-3/mod-4 domain, first-return condition, and recurrence identity.
- The certificate verifier accepts only smaller values in S, never an unranked smaller value outside S.

## Exhaustive finite computation

- Direct n/formula/z comparison below 2^24: `all_direct_returns_equal_formula_and_z_coordinate`.
- Main exact cylinder bounds: `A=8`, return depth `3`.
- Depth-3 cylinders: `33696`; closed there: `9911`; OPEN: `23785`.
- Finite-dictionary survivor ratio at the last return: `23785/648`.
- The configured Phase 4 run leaves 23,785 OPEN families versus Phase 3's 79,350 mixed OPEN nodes, but the domains, depths, and cylinder coordinates differ; this is not evidence of an asymptotic reduction.
- Return templates compress individual excursions, but the Kraft identity and measured cylinder counts do not produce subcritical growth.
- Per-return survivor growth is supercritical/exponential-looking over the tested grid; asymptotics remain unresolved.

## Exact unresolved families

- Smallest exact unresolved source: `47+18432*t`, `t>=0`.
- Its tested endpoint: `155+59049*t` after `3` returns.
- Smallest unresolved family not tagged by a repeated branch shadow: `47+18432*t`.
- These are obstructions to the configured bounded rule dictionary, not infinite Collatz obstruction theorems.

## Failed ranking proposals and counterexamples

- Fixed return horizon: rejected by the exact negative fixed point `-7` and cycle `-61 -> -34 -> -25 -> -61`, and by the positive record-stopping-time table.
- Monotone one-return descent: rejected by `11 -> 20` and `47 -> 182`.
- Constants-only ranking on `1,5,21`: refill transitions in unresolved certificate histories keep producing positive-slope families; the smallest exact family above is a counterexample to closure under the tested ranking.
- Finite periodic-shadow dictionary: rejected as a universal explanation because the code has Kraft sum 1 and the smallest non-repeated-shadow family remains OPEN.

## Diagnostic and conjectural status

- Negative/rational shadows and mod-27 dangerous cycles are diagnostics only.
- No heuristic closure is included in the certificate.
- A future rule would need a well-founded ranking across refill cycles or a parametric repeated-return lemma; high finite closure percentages are insufficient.

## Search grid

| A | return depth | cylinders | closed | OPEN at bound |
|---:|---:|---:|---:|---:|
| 4 | 1 | 28 | 23 | 5 |
| 4 | 2 | 140 | 93 | 47 |
| 4 | 3 | 1316 | 780 | 536 |
| 6 | 1 | 40 | 29 | 11 |
| 6 | 2 | 440 | 222 | 218 |
| 6 | 3 | 8720 | 3725 | 4995 |
| 8 | 1 | 52 | 32 | 20 |
| 8 | 2 | 1040 | 392 | 648 |
| 8 | 3 | 33696 | 9911 | 23785 |
