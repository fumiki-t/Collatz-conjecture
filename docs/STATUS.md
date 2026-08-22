# Current research status

**Last updated:** 2026-08-22

**Problem status:** `OPEN` — the Collatz conjecture is neither proved nor
disproved by this repository.

## What is currently proved?

- `VERIFIED_THEOREM`: the exact affine-cylinder identities and the symbolic
  algebra used by the certificate rules can be reconstructed with integer or
  rational arithmetic.
- `CONDITIONAL`: P54 gives
  `M(K_q-1) <= N <= H_q` under the least-positive-counterexample and
  first-coefficient-crossing hypotheses.
- `VERIFIED_FINITE`: the exact modular graphs, return templates, certificate
  nodes, and finite ranges listed below were independently reconstructed.

No item above proves the Collatz conjecture.

## What is only computationally verified?

- Phase 1–2: depth 26 has 190,069 `DESCENT`, 1,227,442 `SPLIT`, and
  1,037,374 `OPEN` nodes. Literal shortcut iteration agrees for all 16,777,214
  starts with `2 <= n < 2^24`.
- Phase 3: 43,198 reverse-merge closures and 79,350 final mixed `OPEN` nodes;
  the exact boundary-gap audit reaches depth 36.
- Phase 4: 52 configured mod-9 templates, 10,335 closed certificate records,
  and 23,785 `OPEN` records; direct audit covers 1,864,135 section elements.
- Phase 5: 52 mod-27 first-return templates and 108 labeled simple cycles; four
  are noncontracting. The direct audit covers 2,485,513 section integers.
- Phase 6: all `H_q` through `q=200000` were scanned exactly, giving 37 record
  indices. Five certificates verify 14 barrier-record inequalities and cover
  every `94 <= q <= 4960`. Direct search determines `M(k)` through `k=223`.

These are `VERIFIED_FINITE`; none supplies an eventual statement.

## Strongest verified result

The strongest proof-oriented finite result is the Phase 6 certificate range:
every barrier case `94 <= q <= 4960` is excluded by exact
`M(K_q-1) > H_q` certificates and record monotonicity. The largest shared
certificate is `M(232) > 1358717` with 3,219 nodes.

The strongest exact structural result outside Phase 6 is the Phase 5 mod-27
audit: deleting `{1,11,20,26}` leaves a DAG, first returns have length at most
9, and exactly four of 108 labeled simple cycles are noncontracting.

## Strongest conditional route

`P54` (`CONDITIONAL`) is the current main route. A least positive
counterexample whose coefficient first crosses below one at the `q`-barrier
must satisfy

\[
M(K_q-1)\le N\le H_q.
\]

Thus an eventual proof of `M(K_q-1) > H_q`, plus the finite remainder, would
rule out such a counterexample and close the conjecture through this route.

## Current main bottleneck

No asymptotic lower bound is known for the least coefficient-safe
representative `M(k)`. Exact certificates can extend a finite boundary but do
not explain why unusually small admissible residues cannot recur forever.
The needed result must dominate `H_q`; the contextual estimate
`H_q = O(q^5.117)` depends on an external Diophantine estimate and is not an
input to current certificates.

## Secondary directions

- Prove anti-concentration for inverse parity residues with an effective least
  representative bound.
- Derive recursive or meet-in-the-middle lower bounds for `M(k)`.
- Explain small `M(k)` using moving rational shadows of unbounded height and
  simultaneous 2-adic/3-adic constraints.
- Extend exact certificates only when testing a precise structural conjecture.
- Revisit predecessor-tree density only with a bridge from global density to a
  single least counterexample.

## What was recently refuted?

- `REFUTED`: four fixed rational shadow centers are complete. The exact block
  `W=111011100` has map `(729x+817)/512` and fixed point `-817/217` outside the
  four centers.
- `REFUTED`: the quantified H5-A bounded surrogate; 2,141 bounded
  counterexamples were retained.
- `REFUTED`: fixed short-period dictionaries universally explain critical
  prefixes; the smallest depth-26 residual representative is 27.
- `REFUTED`: the tested constants-only Phase 4 ranking closes refill cycles.
- `REFUTED` as a standalone strategy: adding only bounded binary/ternary or
  modular refinements makes the tested frontier manageable asymptotically.
- `RETRACTED`: early strong numerical claims based on cycle-only assumptions,
  unchecked computations, or invalid equivalences.

## Next 3 concrete research questions

1. Can the inverse parity map yield a deterministic lower bound
   `M(k) >= k^{5.117+epsilon}` on all sufficiently large coefficient-safe
   prefixes, or can the mandatory adversarial families refute every proposed
   version quickly?
2. Do `H_q` record indices force a continued-fraction or discrepancy condition
   that makes the associated admissible residue unusually large?
3. Can a recursive decomposition of coefficient-safe words produce a
   certificate-composable lower bound for `M(k)`, rather than only an
   exponentially large word count?

## Codex tasks worth doing

- Formalize one precise candidate inequality for `M(k)` and search for its
  smallest exact counterexample before scaling.
- Build an independent verifier for any new lower-bound certificate format.
- Audit proof dependencies and claim statuses after each result.
- Maintain adversarial regressions for `2^m-1`, `8^m-5`, `(110|111)^*`,
  `A=11101`, `B=1100`, and `A^rB^s`.
- Replace external record minimality with compact internal certificates where
  feasible.

## Tasks not worth doing without a new idea

- Merely extend Phase 1–5 search depth or modulus.
- Add another fixed finite shadow dictionary.
- Infer an asymptotic law from high finite coverage or a beam search.
- Retry naive predecessor-density intersection without a theorem controlling
  the exceptional least counterexample.
- Use floating point to accept a certificate or a near-critical inequality.

## Immediate audit pointers

- Claim statuses: [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md)
- Negative results: [`FAILED_APPROACHES.md`](FAILED_APPROACHES.md)
- Prioritized program: [`ROADMAP.md`](ROADMAP.md)
- Reproduction and hashes: [`../PHASE6_RUN_RESULTS.md`](../PHASE6_RUN_RESULTS.md)
  and [`../artifacts/SHA256SUMS`](../artifacts/SHA256SUMS)
