# Machine-readable research control plane

This directory is an operational index for AI and automated checks. It is not
a second source of mathematical truth.

- `registry.json` identifies the current acceptance boundary, active proof
  obligations, scoped context packs, and mandatory adversarial families.
- `claims-index.json` is a deterministic, read-only JSON projection of every
  claims-ledger row. Regenerate it with `scripts/build_claim_index.py --write`;
  never edit it by hand.
- `schemas/experiment.schema.json` defines the contract for a reproducible
  experiment.
- `experiments/` stores one manifest per accepted or actively developed
  experiment. `phase12-acceptance.json` is the reference example.

The canonical statement and status of a claim remain in
[`../docs/CLAIMS_LEDGER.md`](../docs/CLAIMS_LEDGER.md). If a registry entry and
the ledger disagree, the health check must fail; do not choose one silently.
Long-form reasoning remains in the Phase result, status, failure, literature,
and history documents.

## AI start protocol

From a clean worktree:

```bash
.venv/bin/python scripts/research_health.py --strict
```

Then select exactly one entry from `active_obligations`, read its context pack
when present, and state the experiment contract before running a large search.
The contract must pin:

1. exact claim IDs and quantifiers;
2. finite bounds and completeness boundary;
3. exact acceptance arithmetic;
4. generator, verifier, and test commands;
5. independent reconstruction and tamper tests;
6. adversarial families;
7. stop conditions and artifact policy;
8. what every outcome does not prove.

An `ACCEPTED` manifest is provenance, not a new theorem. Its claim statuses
must already agree with the claims ledger and its artifacts must exist. Do not
edit an accepted manifest to rewrite history; add a superseding experiment and
preserve the previous file in Git.

After changing the ledger, regenerate and check the index:

```bash
.venv/bin/python scripts/build_claim_index.py --write
.venv/bin/python scripts/build_claim_index.py --check
```

## Why the ledger was not converted to JSON

The claim statements contain mathematical qualifications, citations, and
counterexamples that are easier to audit in prose. Duplicating all of them in
JSON would create two large sources that can drift. The registry therefore
contains only the small operational subset that automation can cross-check.
