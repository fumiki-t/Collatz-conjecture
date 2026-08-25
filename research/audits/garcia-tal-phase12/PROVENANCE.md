# Garcia--Tal / Phase 12 audit provenance

- Source `main`: `e1eb31bdf13c7084f3ac575ec0b9e3c1f09e6c0b`
- Research content commit: `55c86f538e195ce7d2dd94ebb04f8a904106cdfd`
- Audit branch: `codex/audit-garcia-tal-phase12`
- Date: 2026-08-25
- Repository conclusion: `proves_collatz=false`

## Independent verification

```bash
.venv/bin/python verifier/verify_garcia_tal_formal_obstruction.py \
  research/audits/garcia-tal-phase12/formal_obstruction.json \
  --output research/audits/garcia-tal-phase12/verifier_result.json
```

Recorded result: `valid=true`, `verified_depth=1026`,
`E21=VERIFIED_FINITE`, `NG22=REFUTED`, `proves_collatz=false`.

The verifier reconstructs the canonical residues from the inverse 2-adic
series and does not import the generator, which uses the prefix affine
constant recurrence.

## Tests and health checks

```text
.venv/bin/python -m pytest -q
210 passed in 254.84s

.venv/bin/python -m pytest -q \
  tests/test_garcia_tal_formal_obstruction.py \
  tests/test_research_health.py
12 passed

.venv/bin/python scripts/research_health.py
valid=true, claim_count=78, proves_collatz=false
```

The non-strict health check reported five pre-existing untracked files under
`artifacts/`. They were not staged, hashed, or used as evidence for this audit.

## Hash verification

From the repository root:

```bash
shasum -a 256 -c research/audits/garcia-tal-phase12/SHA256SUMS
```

The audit manifest is local to this supplemental audit and does not rewrite
the immutable Phase 12 acceptance manifest or global artifact manifest.

## What this record does not prove

This provenance record verifies a finite certificate and the repository state
at the named commit. It does not independently reprove the external Heppner
theorem, establish a positive ordinary source for NG22, or prove the Collatz
conjecture.
