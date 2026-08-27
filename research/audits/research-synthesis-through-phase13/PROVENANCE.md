# Research synthesis provenance

## Git boundary

- Base: `origin/main` at
  `6a08972be1069cc00475b3e1bbb7a474527d2037`.
- Branch: `docs/research-synthesis-through-phase13`.
- Result commit: `RESULT_COMMIT_PENDING`.
- No force push, artifact regeneration, or mathematical verifier-output edit
  is part of this audit.

## Attached proposal

The attached proposal was treated as a requested scope and candidate
information architecture, not as mathematical authority:

```text
SHA-256 a46c24d0ff50c6d3b41b85241ef383da1868232ba5fcd7510ff8544f46e9d1eb
CODEX_COLLATZ_RESEARCH_SYNTHESIS_PROMPT.md
```

The audit deviated from it by not creating an experiment manifest. The exact
mathematics experiment schema does not honestly model a documentation-only
integration audit.

## Accepted sources

- canonical current status: `docs/CLAIMS_LEDGER.md`;
- machine control plane: `research/registry.json` and generated
  `research/claims-index.json`;
- phase reports: `RUN_RESULTS.md`, `PHASE3_RUN_RESULTS.md` through
  `PHASE13_RUN_RESULTS.md`, plus the branch-point and two-tail supplements;
- accepted audits:
  - Garcia--Tal report SHA-256
    `8528f82c122e0603fadfbfa4fb5552452cfecdea1f0cb2ccc64341a70f856f49`;
  - Phase 13 report SHA-256
    `41d4f173d79647c0897793dd355d441a04718a1411d3efef24b948d1aa3f3408`;
- global accepted artifact manifest SHA-256
  `65a762785fc2eeb0e795446d66997ccf2636eb639fef9e4b005a804718bf851d`.

No heavy historical generator was rerun. Their committed result reports,
verifier JSONs, hashes, current test suite, and source boundaries were audited.
The Phase 13 independent verifier is rerun as the latest mathematical check.

## Scratch inputs

Scratch files were inventory inputs only and were not staged:

| File | SHA-256 | Classification |
|---|---|---|
| `GARCIA_TAL_HEPPNER_PHASE12_INDEPENDENT_AUDIT.md` | `62e4d5874a919ffc73bf918e9133c972b9fb79610089c63b750050da7e84954e` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `GARCIA_TAL_SHORTCUT_COLLATZ_AUDIT.md` | `f28da1fe515f0b7fb51f379a138df32a7d25ba57be04d9c64c47d531f310d5ad` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `RENEWAL_CODE_COMPANION_CRITICAL_AUDIT.md` | `9791d27f5686d1a2397c92d983c9382653635cfb25dc8c50dffe4e7771f38bde` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `RENEWAL_PRESSURE_RESIDUE_AUDIT.md` | `2fdcd49c690aeb2f011b5301ccda7f68e60b761b618f472363264179f525f4e` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `renewal_code_critical_audit.py` | `861273870637a41f68f904fd28eaed7a9bc262b0e808623681cc31e203764d34` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `renewal_code_critical_finite.json` | `cf4a9dab5b435a5088b9cdca1564da81e8ceac6d17d87fb295fd1eb74193e0cd` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `renewal_pressure_residue_audit.py` | `d03cbbb6c10d15a3e1a44bced238cd6bd31f067fdcf19cc8ad4543871df3686d` | `SUPERSEDED_BY_ACCEPTED_RESULT` |
| `renewal_pressure_residue_finite.json` | `4bc3d982b3d19956c017b5301ccda7f68e60b761b618f472363264179f525f4e` | `SUPERSEDED_BY_ACCEPTED_RESULT` |

## External primary records rechecked

- Garcia and Tal, DOI `10.4064/aa-90-3-245-250`;
- Rozier and Terracol, arXiv `2502.00948`;
- Fernández and Ibáñez, arXiv `2607.24844`;
- Barina live verification status, `https://pcbarina.fit.vut.cz/`, and DOI
  `10.1007/s11227-025-07337-0`.

Remote pages supply metadata and external input boundaries only. They are not
accepted as internal proofs.

## Local large untracked artifacts

The five Phase 1–2 files were read only for path, size, and SHA-256. Their
hashes match `RUN_RESULTS.md`; they remain untracked and are excluded from this
audit manifest.

## Reproduction commands

```bash
.venv/bin/python -m compileall -q src verifier scripts
.venv/bin/python -m pytest -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/check_markdown_links.py
.venv/bin/python verifier/verify_phase13.py \
  --artifact-dir artifacts --output /tmp/collatz_phase13_synthesis_verify.json
.venv/bin/python scripts/research_health.py --strict
(cd artifacts && shasum -a 256 -c SHA256SUMS)
(cd research/audits/research-synthesis-through-phase13 && \
  shasum -a 256 -c SHA256SUMS)
git diff --check
```

Strict health is run in a clean temporary worktree so the user's preserved
local untracked artifacts are neither deleted nor mistaken for accepted
evidence.

## Generated and handwritten boundary

- `research/claims-index.json` is regenerated only by
  `scripts/build_claim_index.py --write`.
- Existing files under `artifacts/` and their global manifest are unchanged.
- `docs/RESEARCH_SYNTHESIS.md`, this report, and provenance are handwritten
  navigation/audit documents.
- `SHA256SUMS` is mechanically generated after the result commit is recorded.

`proves_collatz=false`.
