# Research handoff

Read [`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md) first for the complete
map. This file is the compact ten-minute orientation for a technically
competent researcher or AI continuing the project without the original chat.

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

## 3. What the thirteen phases established

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
- Phase 7 derives exact boundary-defect contact pressure. With external
  `N>2075*2^60` and Denjoy--Koksma separated, it certifies the first crossing
  `(q0,K0)`, 31,327,720,462 contacts, and 889,748,829 genuine `h=12` pairs.
  Its 87,015 exact macros contain immediate counterexamples to uniform descent,
  compulsory four-word decomposition, and local unrealizability.
- Phase 8 proves C02 for every contracting ordered `A^rB^s` realization,
  localizes almost all conditional q0 contacts to the first octave, and leaves
  arbitrary contracting `{A,B}*` interleavings C03 `OPEN`.
- Phase 9 strengthens contact and short-return counts, confines the conditional
  endpoint to `0<=d<=4,142,380,786` with `X=7 or 19 mod 36`, and creates a
  large reverse coefficient barrier. Contact-only closure is refuted; C04 is
  the remaining two-sided residue obstruction.
- Phase 10 reduces C04 to one gap residue `rho`, proves `4|rho`, and derives a
  conditional renewal barrier: every point in `[N,N+W]` is coefficient-safe
  through `K0-1=114,208,327,603`. The exact finite spacing target C05 remains
  `OPEN`. P65 proves only a formal rational-cycle minimum, not an integer cycle.
- The Phase 10 branch supplement proves P66 and conditionally reduces every
  positive q0 gap to 30 cases `2<=v2(d)<=31`. E16's finite branch profile peaks
  at joint-safe depth 213 for `h=7`; it supplies falsification data, not a q0
  bound.
- The two-tail supplement proves P68: the next L steps are exactly determined
  by `(h,a,u,orientation,y mod 2^L)`. E17 finds, for every `b<12`, a minimal
  safe/non-safe collision when that residue is shortened to b bits. Thus the
  literal fixed-window compression NG19 is refuted; C05 remains open.
- Phase 11 proves the unconditional P69 counterexample trichotomy. Its
  finite-crossing branch is an infinite ladder of `3 mod 4` tail minima with
  exact height and gap bounds. P70 reduces that branch to H70, an eventual
  dropping-safe pair spacing inequality. E18 finds exactly six failures through
  q=4961, while NG20 proves height-free spacing impossible. P71 closes exact
  affine margins inside each fixed pair cylinder but not across cylinders.
- Phase 12 proves P72 for P69's infinite-safe-tail branch: exact normalized
  odd-orbit growth is at most `j^(1/9)` up to constants, and
  `a_i>(8/9-epsilon)log2(i)` on a density-one index set. P73 rules out the
  all-contact critical mechanical word. NG21 shows the `1/9` exponent cannot
  be improved from distinctness and mod-6 packing alone; H72 remains open.
- The Garcia--Tal audit isolates EXT07 as an external interval-sparsity input.
  Assuming it, P74 gives reciprocal summability and a permanent-safe odd tail
  minimum for every nonperiodic positive orbit, so the renewal ladder is
  conditionally bypassed rather than H70 being proved. P75 strengthens octave
  defects, and P76 gives real/2-adic moving shadows. NG22 shows these analytic
  conditions plus a general odd 2-adic source are still consistent; positivity
  and effective ordinary height are now the H72 boundary.
- Phase 13 proves the renewal first-upcrossing code P77, exact weighted
  pressure bounds P78, and the `13/9` threshold plus valuation-conditioned
  positive-source transfer P79. P80 isolates two sufficient but unproved
  canonical-residue anti-concentration estimates. NG23 refutes substituting
  raw Haar volume for deterministic least positive representatives at the
  minimum word `u=1,H=2`; H72 remains open.

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

What is missing: a `q`-uniform high-correction/least-positive-residue
separation strong enough to imply an eventual lower bound for `M(k)`.

The closest q0 subroute is now:

```text
P63 single gap residue
  -> P64 two long-safe endpoints
  -> P66/P67 thirty first-divergence cases
  -> P68 exact finite-horizon two-tail state
  -> C05 two-tail spacing certificate (OPEN).
```

The logically exhaustive Phase 11 route is:

```text
P69 counterexample trichotomy
  -> exclude nontrivial cycles (OPEN)
  -> EXT07/P74 conditional permanent-safe reduction
  -> P72/P75/P76/P77/P78/P79
  -> P80 canonical-residue anti-concentration (CONDITIONAL)
  -> H72 (OPEN)
  -> H70 eventual dropping-safe spacing via P70 (OPEN).
```

H70 would settle only its third branch through P70, so it must never be described as a
complete proof route by itself.

## 5. Where to work next

Start with [`AI_RESEARCH_GUIDE.md`](AI_RESEARCH_GUIDE.md) and
[`ROADMAP.md`](ROADMAP.md), priority P0/P1. A useful new proposal
should answer all of these before a large computation:

1. What precise inequality about `M(k)`, dropping-safe pair spacing, or
   odd-orbit transition packing is proposed?
2. Why would it dominate the relevant `H_q` height and gap allowance?
3. What is the fastest exact falsification test?
4. Does it survive every mandatory adversarial family?
5. What certificate can an implementation-independent verifier reconstruct?

For H54, H70, or H72, use the scoped pack under [`context/`](context/README.md)
and confirm its status against `CLAIMS_LEDGER.md`. Register a large experiment
under `research/experiments/`; `research/registry.json` is the machine-readable
entry point and is audited against the ledger.

Good near-term work includes inverse-parity anti-concentration, recursive
lower bounds, a cross-cylinder quotient/carry state extending P71, and a
positive ordinary-integrality or effective shadow-height obstruction extending
P75--P79. Start from the stored NG19 collisions, universal NG20 pair, both
NG22 formal 2-adic sources, and NG23's raw-volume obstruction: any proposed
merge must distinguish them or prove a sound dominance relation. Certificate
extension is useful when it tests such structure; raw depth extension is
secondary.

## 6. Reproduce and audit

From the repository root:

```bash
.venv/bin/python -m pytest -q
.venv/bin/python verifier/verify_phase10.py \
  --artifact-dir artifacts --output /tmp/collatz_phase10_verifier.json
.venv/bin/python verifier/verify_branch_point.py \
  --artifact-dir artifacts --output /tmp/collatz_branch_verifier.json
.venv/bin/python verifier/verify_two_tail.py \
  --artifact-dir artifacts --output /tmp/collatz_two_tail_verifier.json
.venv/bin/python verifier/verify_phase11.py \
  --artifact-dir artifacts --output /tmp/collatz_phase11_verifier.json
.venv/bin/python verifier/verify_phase12.py \
  --artifact-dir artifacts --output /tmp/collatz_phase12_verifier.json
.venv/bin/python verifier/verify_phase13.py \
  --artifact-dir artifacts --output /tmp/collatz_phase13_verifier.json
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python scripts/research_health.py
shasum -a 256 artifacts/SHA256SUMS
```

Use `scripts/research_health.py --strict` in a clean acceptance worktree. The
non-strict command deliberately reports local untracked artifacts as warnings
without treating them as accepted evidence.

The current manifest hash is recorded in
[`../PHASE13_RUN_RESULTS.md`](../PHASE13_RUN_RESULTS.md).
For regeneration commands and individual artifact hashes, use the phase result
files linked from [`INDEX.md`](INDEX.md).

Before changing a claim status, read its row in
[`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md), its failure history in
[`FAILED_APPROACHES.md`](FAILED_APPROACHES.md), and any external dependency in
[`LITERATURE.md`](LITERATURE.md).

The current local `scratch/` inventory is superseded by the accepted
Garcia--Tal and Phase 13 audits; it is not accepted evidence. No post-Phase-13
unverified mathematical candidate was found by the 2026-08-27 synthesis
audit. See the scratch index in
[`RESEARCH_SYNTHESIS.md`](RESEARCH_SYNTHESIS.md#10-scratch-index).

## If you only remember one thing

The current bottleneck is not finite verification or contact density. It is a
rigorous asymptotic link from high affine correction to ordinary height, or a
cross-cylinder spacing theorem. P71 solves exact margins only inside a fixed
finite cylinder; NG19 prevents literal truncation, and NG20 prevents discarding
height. EXT07/P74 conditionally collapses the nonperiodic alternatives to a
permanent-safe tail, but P75/P76 do not exclude it: NG22 satisfies their
analytic consequences at the formal/2-adic level. P77--P79 expose exact
renewal pressure and valuation structure, while NG23 shows Haar volume alone
cannot control an ordinary representative. The remaining distinction is a
deterministic positive-height anti-concentration theorem. Collatz remains open.
