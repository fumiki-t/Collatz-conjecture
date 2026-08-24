# Current research status

**Last updated:** 2026-08-24

**Problem status:** `OPEN` — the Collatz conjecture is neither proved nor
disproved by this repository.

## What is currently proved?

- `VERIFIED_THEOREM`: the exact affine-cylinder identities and the symbolic
  algebra used by the certificate rules can be reconstructed with integer or
  rational arithmetic.
- `VERIFIED_THEOREM`: C02 now proves exact descent for every positive integral
  contracting realization of the ordered family `A^rB^s`, using six internal
  CRT cases and the isolated external gap theorem EXT05.
- `VERIFIED_THEOREM`: P65 proves that `z=B/(2^K-3^q)` is the minimum of the
  formal rational affine cycle of every coefficient-safe first-crossing word,
  and `gcd(B,D)=gcd(d,D)`. It asserts no positive integral cycle.
- `CONDITIONAL`: P54 gives
  `M(K_q-1) <= N <= H_q` under the least-positive-counterexample and
  first-coefficient-crossing hypotheses.
- `CONDITIONAL`: P57 independently gives
  `S(a)>=3N delta` and `W(C)>=6N delta-S0` under the same least-counterexample
  framework.
- `CONDITIONAL`: Phase 9 verifies forced-contact closure, the exact endpoint
  displacement bound `d<=4142380786<2^32`, endpoint congruences, G4
  impossibility, and a reverse continued-fraction barrier inside that same
  least-counterexample first-crossing framework.
- `CONDITIONAL`: Phase 10 reduces the q0 endpoint pair to the single residue
  `rho=d`, proves `4|rho`, and proves renewal coefficient safety through
  `K0-1=114208327603` for every orbit point in `[N,N+W]` in that framework.
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
- Phase 7: the first post-bound crossing pair is certified as
  `(q0,K0)=(72057431991,114208327604)` after the external `N>2075*2^60` input.
  Under external Denjoy--Koksma, exact consequences force 31,327,720,462
  contacts and 889,748,829 genuine `h=12` pairs. The exact finite alphabet has
  87,015 macros, and selected fixed layers contain `1,2,7,312455` words.
- Phase 8: under P58, X02, EXT04, and the Phase 7 certificates, exact counting
  gives at most 5 octave exceptions, at least 31,327,720,457 first-octave odd
  iterates, 889,748,819 first-octave `h=12` pairs, and 7,308,576,455
  first-octave consecutive returns of odd gap at most 2. The C03 falsification
  search reconstructs all 79,184 contracting `{A,B}` words through block
  length 18 (79,166 mixed) and 12,265 first block-boundary crossings through
  length 22, with no counterexample.
- Phase 9: the exact denominator-at-most-256 contact dual selects
  `lambda=143/199`, giving 35,251,435,772 closure-aware contacts and
  16,848,437,652 first-octave short returns after exception damage. Independent
  enumeration rebuilds 22,475,497 coefficient-safe first-crossing words
  through `q=21`, all 287 contracting reverse coefficient pairs through
  `a=30`, 30 lower-mechanical reverse words, and every parity word through
  shortcut length 21. No nontrivial paradoxical first-crossing word occurs in
  the small layers; exactly five bounded paradoxical cylinders occur at length
  8 in the unrestricted tree.
- Phase 10: independent enumeration reconstructs 81,118 first-crossing words
  through `q=15`. Exact spacing for every `2<=n<=1,500,000` reaches
  `Delta_213=268416` at `(1126015,1394431)`; at `k=214` only one safe value
  remains in that finite prefix. The target at `H=2^72` was not evaluated.

These are `VERIFIED_FINITE`; none supplies an eventual statement.

## Strongest verified result

The strongest proof-oriented finite result is the Phase 6 certificate range:
every barrier case `94 <= q <= 4960` is excluded by exact
`M(K_q-1) > H_q` certificates and record monotonicity. The largest shared
certificate is `M(232) > 1358717` with 3,219 nodes.

The strongest exact structural result outside Phase 6 is the Phase 5 mod-27
audit: deleting `{1,11,20,26}` leaves a DAG, first returns have length at most
9, and exactly four of 108 labeled simple cycles are noncontracting.

Phase 7 adds the strongest large-`q` conditional consequence, but it depends
on external computational evidence and Denjoy--Koksma. It does not supersede
the internally verified Phase 6 finite barrier range.

Phase 8 closes C02 as a genuine theorem for the ordered contracting family
`A^rB^s`. This is the strongest new universal block result, but it covers only
one ordering family and therefore does not supersede the P54 barrier route.

Phase 9 gives the strongest current localization of the q0 conditional
endpoint: `0<=X-N<2^32`, `X=7 or 19 mod 36`, G4 is forbidden, and the first
reverse coefficient pair not eliminated by the uniform threshold is
`(a,L)=(615582794569,975675645481)`. These are conditional consequences, not
an existence or exclusion theorem for the endpoint.

Phase 10 gives the strongest renewal consequence of that localization: every
`S` in `[N,N+W]` is conditionally coefficient-safe through `K0-1`. Thus a
positive q0 gap would create two long-safe integers within distance `W`, but
the required global spacing lower bound C05 is still open.

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
representative `M(k)`. Phase 7 narrows the missing statement: no `q`-uniform
inequality is known that prevents a high affine correction `B` from coexisting
with an unusually small least positive inverse-parity residue.
Phase 8 shows that even many exact first-octave returns do not yet supply a
well-founded rank for arbitrary interleavings of the four short-return maps or
the block alphabet `{A,B}`; C03 remains `OPEN`.
Phase 9 further shows that contact closure and weighted pressure alone cannot
finish the argument: NG17 is refuted by the exact all-contact construction.
The remaining C04 bottleneck is a simultaneous Archimedean and 2-adic/3-adic
near-diagonal exclusion at q0. The reverse coefficient barrier does not yet
classify arbitrary exponent-word residues or prove that a valid path exists.
The needed result must dominate `H_q`; the contextual estimate
`H_q = O(q^5.117)` depends on an external Diophantine estimate and is not an
input to current certificates.
Phase 10 makes the same obstruction one-dimensional via
`rho=[B*P^(-1)]_D`, but neither determines this residue for the unknown q0 word
nor proves `Delta_(K0-1)(2^72)>W`. The finite neighbor-gap recursion does not
scale to the required depth and height.

## Secondary directions

- Prove anti-concentration for inverse parity residues with an effective least
  representative bound.
- Prove C04 by excluding the q0 near-diagonal canonical residue pair, with a
  lossless carry-aware recursion or meet-in-the-middle certificate.
- Prove or refute C05 with a recursive safe-pair cylinder/difference-state
  certificate that scales jointly in depth and ordinary integer height.
- Upgrade the finite mechanical reverse-residue audit to a recursive forbidden
  residue theorem for arbitrary positive exponent compositions.
- Derive recursive or meet-in-the-middle lower bounds for `M(k)`.
- Explain small `M(k)` using moving rational shadows of unbounded height and
  simultaneous 2-adic/3-adic constraints.
- Seek a common well-founded potential for the partial integer block system
  `A:32u->81u`, `B:16u+108->9u+108`, beginning with an adversarial audit of
  arbitrary interleavings rather than only `A^rB^s`.
- Extend exact certificates only when testing a precise structural conjecture.
- Revisit predecessor-tree density only with a bridge from global density to a
  single least counterexample.

## What was recently refuted?

- `REFUTED`: nested safe-set deletion forces strict spacing growth at every
  depth. The exact Phase 10 prefix has `Delta_2=Delta_3=4`; only nondecrease
  survives without a stronger state invariant.
- `REFUTED`: forced-contact closure plus weighted contact pressure alone is
  sufficient. With the required correction `c_0=1`, the exact all-contact
  construction still satisfies closure and pressure but carries no endpoint
  or least-residue exclusion.
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
- `REFUTED`: every 12-odd contact-return macro contracts, decomposes into the
  four Phase 5 dangerous words, or is locally unrealizable. Macro id 0,
  `1111111111110000000`, refutes all three candidate statements.
- `RETRACTED`: early strong numerical claims based on cycle-only assumptions,
  unchecked computations, or invalid equivalences.

## Next 3 concrete research questions

1. Can the gap residue `rho=[B*3^(-q)]_(2^K-3^q)`, `4|rho`, be excluded from
   `[0,W]` for every q0-critical word by a scalable exact recursion?
2. Can C05, `Delta_(K0-1)(2^72)>W`, be proved by a lossless cylinder or
   difference-state certificate rather than finite-prefix disappearance?
3. Can arbitrary reverse exponent compositions be summarized by a lossless
   recursive forbidden-residue state, rather than only the mechanical family?

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
- Retry contact closure plus weighted pressure without a new endpoint or
  least-residue invariant; NG17 is an exact no-go for that information set.
- Infer an asymptotic law from high finite coverage or a beam search.
- Retry naive predecessor-density intersection without a theorem controlling
  the exceptional least counterexample.
- Use floating point to accept a certificate or a near-critical inequality.

## Immediate audit pointers

- Claim statuses: [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md)
- Negative results: [`FAILED_APPROACHES.md`](FAILED_APPROACHES.md)
- Prioritized program: [`ROADMAP.md`](ROADMAP.md)
- Phase 6 acceptance: [`../PHASE6_RUN_RESULTS.md`](../PHASE6_RUN_RESULTS.md)
- Phase 7 acceptance: [`../PHASE7_RUN_RESULTS.md`](../PHASE7_RUN_RESULTS.md)
- Phase 8 acceptance: [`../PHASE8_RUN_RESULTS.md`](../PHASE8_RUN_RESULTS.md)
- Phase 9 acceptance: [`../PHASE9_RUN_RESULTS.md`](../PHASE9_RUN_RESULTS.md)
- Phase 10 acceptance: [`../PHASE10_RUN_RESULTS.md`](../PHASE10_RUN_RESULTS.md)
- Hashes: [`../artifacts/SHA256SUMS`](../artifacts/SHA256SUMS)
