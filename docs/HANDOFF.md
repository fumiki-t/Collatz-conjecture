# Research handoff

Read this file first. It is a compact orientation for a technically competent
researcher or AI continuing the project without the original chat.

## 1. Safety boundary

The Collatz conjecture remains `OPEN`. This repository contains exact finite
certificates, some internally checked algebra, external theorems, failed
mechanisms, and conjectural directions. Keep those categories separate using
the taxonomy in [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md) and the protocol in
[`../AGENTS.md`](../AGENTS.md).

Do not edit generated artifacts manually. Do not infer an eventual theorem
from finite coverage. Any proof candidate moves to an
`audit/proof-candidate-*` branch and receives adversarial human review before
README language changes.

## 2. Mathematical setup

The shortcut map is

\[
T(n)=n/2\quad(n\text{ even}),\qquad
T(n)=(3n+1)/2\quad(n\text{ odd}).
\]

For a parity prefix of length `k` with `q_k` odd steps,

\[
T^k(n)=\frac{3^{q_k}n+B_k}{2^k}.
\]

A prefix is coefficient-safe when `3^{q_j} >= 2^j` for every prefix
`1 <= j <= k`. Define `M(k)` as the least positive integer at least 2 with a
coefficient-safe prefix of length `k`.

For each `q`, Phase 6 defines

\[
K_q=\lceil q\log_2 3\rceil,\qquad
H_q=B_q^{\max}/(2^{K_q}-3^q),
\]

with `B_q^max` given explicitly in the Phase 6 result and verifier.

## 3. What the six phases established

- Phase 1–2 built exact affine cylinders and an independent verifier. The
  depth-26 frontier has 1,037,374 unresolved nodes. A short-period dictionary
  leaves 123,908 unexplained; representative 27 is the smallest residual.
- Phase 3 added ternary refinement and exact reverse merges. It closes 43,198
  records but leaves 79,350 mixed `OPEN` records. Bounded refinement alone is
  not subcritical in the tested range.
- Phase 4 used the strongly sufficient section `2 mod 9` and an exact
  prefix-free first-return code. Refill constants `1,5,21` defeat the tested
  finite rankings; 23,785 records remain open.
- Phase 5 used `{1,11,20,26} mod 27`, where complement acyclicity bounds first
  returns. It found 52 templates, 108 labeled simple cycles, and four
  noncontracting cycles. Fixed four-shadow completeness fails.
- The adversarial words `A=11101`, `B=1100`, and
  `W=AB=111011100` matter: `W` has affine map `(729x+817)/512` and fixed point
  `-817/217`. Exact `A^rB^s` records approach multiplier one; the universal
  arbitrary-closeness conclusion uses an external density theorem.
- Phase 6 derived the current critical-prefix barrier and added exact lower
  bound certificates for `M(k)`.

The chronological details and exact counts are in
[`../RESEARCH_HISTORY.md`](../RESEARCH_HISTORY.md).

## 4. Current strongest route

P54 is `CONDITIONAL`. If `N` is a least positive counterexample and its affine
coefficient first crosses below one at the `q`-barrier, the independently
audited algebra gives

\[
M(K_q-1)\le N\le H_q.
\]

Therefore `M(K_q-1) > H_q` excludes that first-crossing configuration. If the
inequality holds eventually and all remaining finite cases are checked, this
route would prove the original conjecture.

What is already finite and exact:

- 37 `H_q` records through `q=200000`; last record
  `q=190537`, `K_q=301994`, `floor(H_q)=710220447737`;
- five independently checked certificates covering every `94 <= q <= 4960`;
- direct exact determination of `M(k)` through `k=223`;
- early barrier failures `(q,N)=(17,27),(29,27),(41,703)`.

What is missing: any eventual lower bound for `M(k)`.

## 5. Where to work next

Start with [`ROADMAP.md`](ROADMAP.md), priority P0/P1. A useful new proposal
should answer all of these before a large computation:

1. What precise inequality about `M(k)` is proposed?
2. Why would it dominate `H_q`?
3. What is the fastest exact falsification test?
4. Does it survive every mandatory adversarial family?
5. What certificate can an implementation-independent verifier reconstruct?

Good near-term work includes inverse-parity anti-concentration, recursive
lower bounds, and arithmetic structure at `H_q` records. Certificate extension
is useful when it tests such structure; raw depth extension is secondary.

## 6. Reproduce and audit

From the repository root:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python verifier/verify_phase6.py \
  --artifact-dir artifacts \
  --output /tmp/collatz_phase6_verifier.json
shasum -a 256 artifacts/SHA256SUMS
```

The manifest hash is
`1f7d1b4c564a01c9af7ea82abaa949df3444ed757bfc09faad00a526e2487653`.
For regeneration commands and individual artifact hashes, use the phase result
files linked from [`INDEX.md`](INDEX.md).

Before changing a claim status, read its row in
[`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md), its failure history in
[`FAILED_APPROACHES.md`](FAILED_APPROACHES.md), and any external dependency in
[`LITERATURE.md`](LITERATURE.md).

## If you only remember one thing

The current bottleneck is not finite verification. It is proving an eventual
asymptotic lower bound on the least coefficient-safe representative `M(k)`,
strong enough to dominate `H_q`.
