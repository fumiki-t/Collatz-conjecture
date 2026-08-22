---
name: Claim audit
about: Audit a new claim or a proposed status transition
title: "audit: "
labels: claim-audit
assignees: ""
---

## Claim ID

Use an existing stable ID or propose a new non-recycled ID.

## Claim text

Write the exact quantified statement and proposed single status label.

## Dependencies

List repository lemmas/certificates and every external theorem with a primary
citation.

## Potential failure modes

Check quantifier changes, finite-to-asymptotic promotion, map convention,
positivity, carry behavior, external completeness, and hidden floating point.

## Counterexample search

Describe exact bounds and mandatory adversarial regressions. Record the
smallest counterexample if one is found.

## Proof audit

Provide a line-by-line proof review or independent verifier result, tamper
tests, reproduction commands, commit, and SHA-256 manifest as applicable.

## Status decision

Choose exactly one of `VERIFIED_THEOREM`, `VERIFIED_FINITE`, `CONDITIONAL`,
`EXTERNAL_THEOREM`, `EXTERNAL_EVIDENCE`, `HEURISTIC`, `CONJECTURE`, `REFUTED`,
`RETRACTED`, or `OPEN`. Explain every transition and update the canonical
documents.

## What this result does not prove

State the remaining gap to the original Collatz conjecture.
