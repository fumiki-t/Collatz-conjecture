# Collatz research and experiment ledger

This file is the cumulative index for the repository. It records what was
checked exactly, what failed, which inputs remain external, and what is still
conjectural. None of the completed phases proves the Collatz conjecture.

## Status vocabulary

- **Exact finite certificate:** a bounded claim reconstructed with integer or
  rational arithmetic by an independent verifier.
- **Conditional symbolic implication:** an algebraic implication checked under
  explicitly stated assumptions; it does not establish those assumptions.
- **External evidence:** supplied data or a named theorem whose provenance or
  proof is outside the repository.
- **Heuristic:** a bounded search or ranking experiment with no universal
  conclusion.
- **Open:** an unresolved frontier or missing asymptotic argument.

## Phase timeline

| Phase | Branch / commit | Main verified result | Principal obstruction | Status |
|---|---|---|---|---|
| 1–2 | `main` / `42dc629` | Depth-26 affine certificate and literal audit of all `2 <= n < 2^24` | 1,037,374 `OPEN` nodes; short-block dictionary leaves 123,908 unexplained | Exact finite, open frontier |
| 3 | `feat/phase3-mixed-merge` / `d7bb6d9` | Exact binary/ternary splits, 43,198 reverse-merge closures, boundary-gap audit through depth 36 | 79,350 mixed open nodes after two refinements; smallest family starts at 27 | Exact finite, open frontier |
| 4 | `feat/phase4-return9` / `909fad1` | Prefix-free mod-9 return code with Kraft sum 1; 52 finite templates | 23,785 open depth-3 cylinders, `a>8` overflow, and refill constants defeat the tested ranking | Exact finite, open frontier |
| 5 | `feat/phase5-dangerous-cycles` / `39c90b4`, `4444d7c` | 52 section returns, 108 simple cycles, four noncontracting words, return-20 domination | H5-A surrogate fails; H5-B bounded candidates persist; no universal rank synthesized | Exact algebra plus bounded heuristics |
| 6 | `feat/phase6-critical-prefix-barrier` / `8684d53` | Conditional P54 audit, 37 exact `H_q` records through 200,000, five `M(k)>X` certificates | No eventual lower bound for `M`; exact coverage currently ends at `q=4960` | Conditional symbolic plus exact finite |

The branch history is linear: each phase branch contains every earlier phase.
Separate branches are retained as reproducible milestones, while `main` is the
cumulative research record.

## Exact results worth reusing

### Affine and return structures

- Phase 1 directly matches literal shortcut iteration to the affine-cylinder
  model for 16,777,214 starts below `2^24`.
- Phase 4 independently reconstructs the exact prefix-free mod-9 first-return
  code and all configured compositions.
- Phase 5 proves within its exact finite graph model that deleting
  `{1,11,20,26}` from the unit graph modulo 27 leaves an acyclic graph, so
  first returns have length at most 9.
- The mod-27 graph has 108 labeled simple cycles. Exactly `1`, `101`, `1101`,
  and `011101` are noncontracting; every other simple cycle has multiplier at
  most `27/32`.
- For positive 20-to-20 paths with no internal 20 or 26, `101` is the unique
  noncontracting simple path. Every other path obeys
  `R(x) <= (27x+46)/32 < x`.

### Critical-prefix barrier

- Under the least-counterexample and first-coefficient-crossing assumptions,
  the P54 algebra gives
  `M(K_q-1) <= N <= H_q`. This is a conditional symbolic implication.
- Every `H_q` record through `q=200000` was selected with exact arithmetic.
  There are 37; the last is
  `q=190537, K_q=301994, floor(H_q)=710220447737`.
- Five independently verified binary-cylinder certificates establish 14
  barrier-record inequalities. Sparse-record monotonicity extends the exact
  continuous range to every `94 <= q <= 4960`.
- The largest shared certificate is `M(232)>1358717` and has 3,219 nodes.
- Direct exact search through 1,500,000 determines `M(k)` through `k=223`.
  The smallest exact post-failure ratio is at `q=46`, where `M(72)=703` and
  `M/H_q>4`.

## Counterexamples and failed mechanisms

- A fixed short-block dictionary is not complete at depth 26; the smallest
  unexplained representative is 27.
- Mixed reverse merges close many Phase 3 branches but do not stop the tested
  frontier from growing.
- The Phase 4 recurrence constants `1`, `5`, and `21` refill the tested rank;
  negative diagnostic cycles cannot be used as positive closure rules.
- The quantified Phase 5 H5-A surrogate has 2,141 bounded counterexamples. The
  bounded H5-B test retains 80 candidates; neither result settles the original
  unquantified statements.
- `A=11101`, `B=1100`, and `W=AB=111011100` are mandatory adversarial blocks.
  `W` has map `(729x+817)/512` and fixed point `-817/217`, outside the four
  canonical shadow centers.
- Eight exact `A^rB^s` records reduce `multiplier-1` below `2^-13` without a
  long aligned repetition of one canonical dangerous word. The general
  arbitrary-closeness conclusion additionally uses a named density theorem.
- The Phase 6 barrier inequality has exact early failures at
  `(q,N)=(17,27),(29,27),(41,703)`. No rigorous eventual polynomial lower
  bound for `M(k)` has been found.

## External inputs kept separate

- The 35 supplied dropping-time record holders reproduce their stated
  dropping and coefficient stopping times. Their global record minimality is
  not proved in this repository.
- Under that external record-list assumption, the last barrier failure is
  `q=41,K_q=65`, and every possible crossing with `66<=K_q<=1005` passes.
- The irrational-rotation density theorem used for arbitrary closeness of
  `A^rB^s` multipliers is named but not reproved.
- The Wu–Wang Diophantine estimate and the contextual bound
  `H_q=O(q^5.117)` are not inputs to any current finite certificate.

## Current research frontier

1. Prove an effective eventual lower bound for `M(k)` strong enough to exceed
   `H_q`, or find an exact obstruction to each proposed mechanism.
2. Extend binary-cylinder certificates beyond the next uncovered barrier
   record `q=4961` without relying on external record minimality.
3. Replace external dropping-time record evidence with independently checkable
   minimality certificates.
4. Test every finite-state, shadow, meet-in-the-middle, or recursive lower-bound
   proposal against `2^m-1`, `8^m-5`, `(110|111)^*`, and `A^rB^s` at arbitrary
   depth.
5. Preserve failures and counterexamples as first-class outputs; do not turn a
   high bounded success rate into an asymptotic claim.

## Reproduction and artifact index

- Phase 1–2: [`RUN_RESULTS.md`](RUN_RESULTS.md)
- Phase 3: [`PHASE3_RUN_RESULTS.md`](PHASE3_RUN_RESULTS.md)
- Phase 4: [`PHASE4_RUN_RESULTS.md`](PHASE4_RUN_RESULTS.md)
- Phase 5: [`PHASE5_RUN_RESULTS.md`](PHASE5_RUN_RESULTS.md)
- Phase 6: [`PHASE6_RUN_RESULTS.md`](PHASE6_RUN_RESULTS.md)
- Current hashes: [`artifacts/SHA256SUMS`](artifacts/SHA256SUMS)

Each phase result file contains its acceptance commands, independent verifier
result, interpretation boundary, and artifact hashes.
