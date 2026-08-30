# AGENTS.md

## Mission

The sole final objective of this repository is to prove or disprove the
Collatz conjecture.

Partial results, computational experiments, reformulations, and new lemmas are
useful only as progress toward that objective.

No AI agent, script, or collaborator may state that the Collatz conjecture has
been proved unless a complete proof has been independently audited.

## 1. Source-of-truth hierarchy

Use the following hierarchy.

1. Machine-verifiable certificate and independent verifier.
2. Mathematical proof written in the repository.
3. Published external theorem with an exact citation.
4. Reproducible exhaustive finite computation.
5. External finite dataset.
6. Heuristic computation.
7. Conjecture.

A lower-level source must never silently be promoted to a higher-level claim.

## 2. Required claim labels

Use exactly one of:

- `VERIFIED_THEOREM`
- `VERIFIED_FINITE`
- `CONDITIONAL`
- `EXTERNAL_THEOREM`
- `EXTERNAL_EVIDENCE`
- `HEURISTIC`
- `CONJECTURE`
- `REFUTED`
- `RETRACTED`
- `OPEN`

When a claim changes status, preserve the old state in Git history and record
the transition in `docs/CLAIMS_LEDGER.md`.

## 3. No-overclaim rule

Never infer:

- asymptotic truth from a large finite range;
- universality from high coverage percentage;
- proof from absence of counterexamples;
- independence from separate-looking source files;
- a Collatz proof from a reformulation unless both directions are proved;
- divergence/cycle elimination unless all alternatives are covered.

Always include a section:

```text
What this result does not prove
```

for any major computational result.

## 4. Exact arithmetic

Proof decisions must use:

- arbitrary-precision integers;
- exact rational arithmetic;
- symbolic inequalities.

Floating point may be used for:

- plotting;
- ranking search candidates;
- heuristics;
- approximate reporting.

Floating point must never determine whether a mathematical certificate is
accepted.

## 5. Independent verification

For any computational theorem or certificate:

- search/generator code and verifier code must be logically independent;
- the verifier must reconstruct arithmetic rather than trust stored derived
  values;
- tampered certificates must be rejected by tests;
- the verifier must not import the corresponding search implementation.

Record:

- command;
- test count;
- verifier result;
- Git commit;
- SHA-256 manifest.

## 6. Experimental workflow

Every new research phase should follow:

```text
hypothesis
-> exact mathematical formulation
-> adversarial search
-> implementation
-> independent verifier
-> obstruction mining
-> interpretation
-> documentation
```

Run counterexample searches before investing heavily in a proof attempt.

Before a large or acceptance-bound computation, create or update a manifest
under `research/experiments/` conforming to
`research/schemas/experiment.schema.json`. The manifest is an operational
contract, not mathematical evidence: the exact claim statement and status
remain canonical in `docs/CLAIMS_LEDGER.md`.

Use `research/registry.json` to select an active obligation and scoped context
pack. Run `scripts/research_health.py --strict` from a clean worktree before
acceptance. A registry/ledger mismatch or an unexplained untracked file under
`artifacts/` must be resolved rather than ignored.

`research/claims-index.json` is generated from the ledger for AI retrieval.
After changing the ledger, run `scripts/build_claim_index.py --write`; never
edit the generated index by hand or treat it as a second claim authority.

## 7. Mandatory adversarial regression set

All universal mechanisms should be tested against:

```text
2^m - 1
8^m - 5
(110|111)^*
A = 11101
B = 1100
A^r B^s
```

Also preserve every previously found minimal counterexample to a failed
hypothesis.

Add new adversarial families rather than replacing old ones.

## 8. Research documentation

After every accepted phase or meaningful theoretical result, update:

```text
docs/STATUS.md
docs/CLAIMS_LEDGER.md
RESEARCH_HISTORY.md
docs/FAILED_APPROACHES.md
docs/ROADMAP.md
```

Update `docs/LITERATURE.md` whenever a new external theorem materially affects
the research.

## 9. Claims ledger format

Every important claim should have an ID.

Examples:

```text
P54   CONDITIONAL
H20   CONJECTURE
NG07  REFUTED
E06   VERIFIED_FINITE
EXT04 EXTERNAL_THEOREM
```

Each entry records:

```text
ID
status
statement
assumptions
proof / verifier / source
first introduced
last audited
counterexample if any
dependencies
implication for Collatz
```

Never recycle IDs.

## 10. Failed approaches are research assets

Do not delete failed approaches.

For every failure record:

- exact hypothesis;
- why it looked plausible;
- smallest counterexample;
- whether failure is local or fundamental;
- what weaker statement survived;
- which future approaches it rules out.

The repository should make it difficult for a future researcher or AI to
rediscover the same false shortcut.

## 11. Literature policy

Prefer:

1. peer-reviewed paper;
2. author-hosted manuscript;
3. arXiv;
4. reputable mathematical database.

Record:

- authors;
- title;
- year;
- journal;
- DOI/arXiv;
- theorem actually used;
- whether it is an input to a proof or only context.

Do not cite an AI-generated summary as mathematical authority.

## 12. Branching and commits

Use branches such as:

```text
research/<topic>
feat/phase<N>-<topic>
audit/<claim-id>
docs/<topic>
```

Each research commit should answer one coherent question.

Do not mix theoretical documentation, unrelated refactors, or generated
artifacts in the same commit unless necessary for reproducibility.

## 13. Generated artifacts

Treat `artifacts/` as generated evidence.

Do not manually edit generated JSON/CSV/certificates.

Every acceptance artifact set should have a SHA-256 manifest.

Large disposable exploratory outputs should not be committed unless they are
needed to reproduce a published claim.

Exploratory files must not be left beside accepted evidence without an
explicit ignore, quarantine, or experiment-manifest decision. The strict
research-health check treats unexplained untracked artifact files as errors.

## 14. Human/AI handoff

Before ending a major research session, ensure `docs/STATUS.md` answers:

```text
What is currently proved?
What is only computationally verified?
What was recently refuted?
What is the current strongest route to the full conjecture?
What exact mathematical bottleneck remains?
What should be attempted next?
What should not be attempted again without new information?
```

A new researcher should not need the original ChatGPT conversation.

For a primary obligation with a context pack under `docs/context/`, update the
pack when its target, dependencies, fastest falsifier, or acceptance boundary
changes. Context packs are scoped caches; they never override the claims
ledger or phase proof record.

## 15. Current strategic rule

The current primary target is the Phase 6 critical-prefix barrier.

Do not spend large compute budgets merely extending Phase 1–5 search depth
unless the experiment is designed to test a precise new asymptotic hypothesis.

Priority should be given to mechanisms capable of proving a lower bound for

\[
M(k),
\]

or otherwise proving

\[
M(K_q-1)>H_q
\]

eventually.

Phase 11 adds `H70` as a secondary exact target for the finite-crossing
renewal-ladder branch. Work on H70 must retain ordinary height, explicitly
survive NG19/NG20, and seek cross-cylinder structure beyond P71. Even a proof
of H70 does not eliminate the separate nontrivial-cycle or infinite
coefficient-safe-tail branches of P69.

Phase 12 adds `H72` as a secondary exact target for the infinite-safe-tail
branch. Any improvement of P72's `1/9` packing exponent must use actual orbit
transition information and explicitly survive NG21; mod-6 packing alone is
sharp. Ruling out the all-contact mechanical word must not be promoted to an
exclusion of the full coefficient-safe language.

Phase 26 closes the cycle-side `H147` area-three obligation by the stronger
all-gcd theorem P158: every critical primitive positive nontrivial cycle has
reduced-slope area at least six. Do not extend the former area-three search.
The next H133 target is critical area six. Every proposed continuation must
reproduce NG34's `q=63322`, `L=100363` paired-arc falsifier and NG35's exact
coefficient reversal `75^7>3*64^7`. Prefer support/height-transition,
correction-loss, radial-energy, or resultant mechanisms that retain P156's
reduced-slope structure. P159's noncritical `A_*>100000` lower bound is not a
cycle exclusion and must not be promoted to an arbitrary-area contradiction.

## 16. Proof-claim emergency protocol

If any agent believes it has proved or disproved the Collatz conjecture:

1. stop feature development;
2. create a dedicated `audit/proof-candidate-*` branch;
3. write the proof without relying on computational intuition;
4. enumerate every external theorem used;
5. construct independent checks for every finite component;
6. actively search for counterexamples to every new lemma;
7. request adversarial human review;
8. do not modify README to say “proved” until the audit is complete.

The default assumption for a surprising proof is that an error exists until
every dependency has been checked.
