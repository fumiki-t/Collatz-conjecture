# Safe-root-frontier supplement — run record

Date: 2026-09-12. Branch: `codex/safe-root-frontier`.
Base main: `20907aad336a9634abca9f5bc467659559307af6`.
Latest numbered phase remains 44; `proves_collatz=false`.

## Outcome

P281/P282 audit the earlier B1 fixed-Q safe ancestor window, including exact
extrema, the smaller-source tie, and the distinction between global and
same-source safety reduction. P283 provides a separate all-length/all-Q
safe-root certificate mode. P284 proves completeness only at each prefix of
a hypothetical global LEX height minimizer, with a non-effective finite
minimum-height unresolved set. E65 certifies finite arithmetic. NG51 records
the minimum empty-target short-hit omission at source 14. H112/H72/H89/H133
and EXT08 remain OPEN; no older status or evidence changes.

Read the [proof audit](research/audits/safe-root-frontier/REPORT.md),
[archived proposal](research/audits/safe-root-frontier/PROPOSAL.md), and
[input provenance](research/audits/safe-root-frontier/PROVENANCE.md).
B2--B6 and the separate 31-ratio exploratory dyadic computation are not
accepted by this supplement. Phase 41/43 implementations remain untouched.

## Exact finite results

| Check | Reconstructed result |
|---|---:|
| Words through length 18 / safe extrema pairs | 524287 / 72 |
| Fixed-Q query sets / direct source-length prefixes | 10240 / 4864 |
| Integer decoder candidates / safe witness occurrences | 16865 / 2744 |
| All-length target queries | 2668 |
| No-LEX certificates / improving witness certificates | 185 / 2483 |
| First-return reference sources / distinct states | 705 / 1189 |
| Aggregate tree vertices / root traces / trace steps | 5455 / 1195 / 38313 |
| (703,80): vertices / leaves / roots / steps | 181 / 91 / 44 / 1156 |
| (703,80): crossing / normalization cuts | 43 / 1 |
| Mandatory family words | 72 |

Some fixed-Q queries have no candidates; some all-length improvements are
immediate empty paths when the target coefficient is <1. Occurrences,
sources, certificates and steps are different counting domains. The
independent verifier also enumerates through length 19 (1048575 nodes) to
reconstruct the small-Q oracle's extrema; this is an auxiliary finite scope,
not an additional asymptotic result. Large controls include nonzero hits at
2^p+7 for p=80,256,1024, alongside potentially vacuous all-ones queries.

All five core supplied mathematical result components and all 185 supplied
no-improvement certificates match exactly as parsed JSON. We additionally
store complete per-query witness sets and all positive certificates, validate
types and diagnostics, and verify old formal/potential controls independently.
The source-14 obstruction is regenerated, not taken as an axiom.

## Reproduction

From the repository root (the module invocation is intentional):

```sh
.venv/bin/python -m src.safe_root_frontier_search --artifact-dir artifacts
.venv/bin/python -m verifier.verify_safe_root_frontier --artifact-dir artifacts --output artifacts/safe_root_frontier_verifier.json
.venv/bin/python -m pytest -q tests/test_safe_root_frontier.py tests/test_safe_root_boundaries.py
.venv/bin/python -O -m unittest tests.test_safe_root_boundaries -q
.venv/bin/python scripts/build_claim_index.py --check
.venv/bin/python scripts/research_health.py --strict
.venv/bin/python scripts/check_markdown_links.py
(cd artifacts && shasum -a 256 -c SHA256SUMS)
```

For nondestructive reproduction, use an empty temporary directory for both
programs and put verifier output there; compare all four JSON files byte for
byte. The verifier reads old reference evidence from the checkout without
modifying it. Its implementation imports neither search module. Numerical
proof decisions use only integers/rationals; elapsed timing is not evidence.

The [experiment manifest](research/experiments/safe-root-frontier.json) will
record clean-worktree acceptance and the implementation commit. Artifact
digests are in [SHA256SUMS](artifacts/SHA256SUMS).

## Issues found and repaired during audit

- Strengthened the supplied certificate checker: exact field/type checking,
  reconstructed diagnostics, duplicate-key rejection and full query binding.
- An initially proposed smaller obstruction S=11 used incorrect literal
  parity. The independent check rejected it: 7 begins 1110, not 1100.
  The accepted minimum is S=14, ancestor 9, word 1, then crossing word 10.
  The supplied S=17/11 example retains its correct word 11010.
- A test originally demanded rejection after removing the final even step
  of target (703,80). The reused certificate remains mathematically valid
  at (703,79), so that test expectation was wrong. The corrected tests
  distinguish invalid parity from a valid certificate for a different query.
- The first clean dependency run exposed a stale control-plane test count
  (373 rather than 379 after six new claims). The count and new claim-status
  assertions were updated; this was not an arithmetic/certificate failure.
- No fatal flaw was found in R1--R6. We retain their essential restrictions:
  global source-set reduction, every short hit, z<S normalization equality,
  hypothetical-minimizer completeness and no future-trace complexity bound.

## What this result does not prove

No fixed-Q no-hit is promoted to all-Q. All-Q conclusions come from the
separate cover/trace certificate. The initial frontier bound does not bound
trace time or guarantee termination. P284 does not decide the hypothetical
minimum set or show it empty. No ancestor-supply theorem, H112/H72/H89
solution, positive-cycle exclusion or Collatz proof is claimed. Next require
ordinary-source/carry/lift arithmetic that forces a LEX improvement or
contradicts compatible all-prefix certificates, not just deeper enumeration.
