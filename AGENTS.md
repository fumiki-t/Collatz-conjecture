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
