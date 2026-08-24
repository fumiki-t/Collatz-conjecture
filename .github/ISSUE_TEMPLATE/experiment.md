---
name: Exact experiment
about: Define a bounded experiment and its independent verification
title: "experiment: "
labels: experiment
assignees: ""
---

## Hypothesis

State the precise claim being tested and its current claim ID/status.
Create `research/experiments/<experiment-id>.json` from the experiment schema
before a large run and link it here.

## Exact finite scope

Specify bounds, maps, parameter conventions, completeness assumptions, and
stop criteria. Mark sampling or beam search as `HEURISTIC`.

## Implementation

Describe the generator/search algorithm, exact arithmetic, deterministic
ordering, and reproduction command.

## Independent verifier

Explain how a separate verifier reconstructs all accepted arithmetic without
importing the search implementation. Include tamper-rejection tests.

## Adversarial regression

Cover `2^m-1`, `8^m-5`, `(110|111)^*`, `A=11101`, `B=1100`, `A^rB^s`, and
preserved minimal counterexamples where the hypothesis is universal.

## Expected artifact

Name the certificate/report files, verifier output, and SHA-256 manifest.
After acceptance, record the commit, manifest hash, and `proves_collatz=false`
boundary in the experiment manifest.

## Interpretation boundary

State what a pass, failure, or high coverage rate does **not** prove.
