# Research documentation index

This is the canonical map of the research archive. Start with
[`HANDOFF.md`](HANDOFF.md) for a short orientation or [`STATUS.md`](STATUS.md)
for the current state.

## Canonical layer

| Document | Role | Update trigger |
|---|---|---|
| [`STATUS.md`](STATUS.md) | Current proved/finite/open/refuted state and next questions | Every meaningful result |
| [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md) | Stable claim IDs, exact status, dependencies, evidence, and counterexamples | Any claim introduction or status change |
| [`FAILED_APPROACHES.md`](FAILED_APPROACHES.md) | Negative results and retracted shortcuts | Any counterexample or retraction |
| [`LITERATURE.md`](LITERATURE.md) | Primary-source bibliography and actual use | Any new external dependency |
| [`ROADMAP.md`](ROADMAP.md) | Ranked proof-oriented program with falsification tests | Any strategic change |
| [`HANDOFF.md`](HANDOFF.md) | Ten-minute onboarding for a new researcher or AI | End of a major session |
| [`AI_RESEARCH_GUIDE.md`](AI_RESEARCH_GUIDE.md) | Active dependency graph, exact next experiments, and machine health check | Every strategic or workflow change |
| [`../RESEARCH_HISTORY.md`](../RESEARCH_HISTORY.md) | Chronological cumulative narrative | Every accepted phase |
| [`../AGENTS.md`](../AGENTS.md) | Mandatory research and proof-claim protocol | Protocol changes |

## Phase evidence

| Phase | Result record | Main obstruction report | Milestone |
|---|---|---|---|
| 1–2 | [`../RUN_RESULTS.md`](../RUN_RESULTS.md) | Generated Phase 2 report; its hash is recorded in the result file | `42dc629` |
| 3 | [`../PHASE3_RUN_RESULTS.md`](../PHASE3_RUN_RESULTS.md) | [`../artifacts/phase3_obstruction_report.md`](../artifacts/phase3_obstruction_report.md) | `d7bb6d9` |
| 4 | [`../PHASE4_RUN_RESULTS.md`](../PHASE4_RUN_RESULTS.md) | [`../artifacts/phase4_obstruction_report.md`](../artifacts/phase4_obstruction_report.md) | `909fad1` |
| 5 | [`../PHASE5_RUN_RESULTS.md`](../PHASE5_RUN_RESULTS.md) | [`../artifacts/phase5_obstruction_report.md`](../artifacts/phase5_obstruction_report.md) | `39c90b4`, `4444d7c` |
| 6 | [`../PHASE6_RUN_RESULTS.md`](../PHASE6_RUN_RESULTS.md) | [`../artifacts/phase6_obstruction_report.md`](../artifacts/phase6_obstruction_report.md) | `8684d53` |
| 7 | [`../PHASE7_RUN_RESULTS.md`](../PHASE7_RUN_RESULTS.md) | [`../artifacts/phase7_obstruction_report.md`](../artifacts/phase7_obstruction_report.md) | `0d58dd1` |
| 8 | [`../PHASE8_RUN_RESULTS.md`](../PHASE8_RUN_RESULTS.md) | [`../artifacts/phase8_obstruction_report.md`](../artifacts/phase8_obstruction_report.md) | `ad4f884` |
| 9 | [`../PHASE9_RUN_RESULTS.md`](../PHASE9_RUN_RESULTS.md) | [`../artifacts/phase9_obstruction_report.md`](../artifacts/phase9_obstruction_report.md) | `d101798` |
| 10 | [`../PHASE10_RUN_RESULTS.md`](../PHASE10_RUN_RESULTS.md) | [`../artifacts/phase10_obstruction_report.md`](../artifacts/phase10_obstruction_report.md) | `b3ab86a` |

Research supplements:

| Topic | Result record | Evidence | Main contribution |
|---|---|---|---|
| Phase 10 branch points | [`../BRANCH_POINT_RUN_RESULTS.md`](../BRANCH_POINT_RUN_RESULTS.md) | `artifacts/branch_point_decomposition.json`; independent verifier | P66 first-divergence theorem, P67 thirty q0 cases, E16 finite profile |
| Two-tail state collisions | [`../TWO_TAIL_RUN_RESULTS.md`](../TWO_TAIL_RUN_RESULTS.md) | `artifacts/two_tail_state_collisions.json`; independent verifier | P68 finite-horizon state, NG19 exact compression failures, E17 finite scan |

The phase branches are reproducible milestones. Main contains the canonical
documentation through Phase 10 and both the branch-point and two-tail
supplements after their independent acceptance checks.

## Evidence boundaries

- `VERIFIED_THEOREM`: proof is present or reconstructible here.
- `VERIFIED_FINITE`: an exact bounded computation was independently checked.
- `CONDITIONAL`: the implication is checked but a hypothesis is missing.
- `EXTERNAL_THEOREM`: published input, not reproved here.
- `EXTERNAL_EVIDENCE`: external finite data without an internal completeness
  certificate.
- `HEURISTIC`, `CONJECTURE`, `OPEN`: no proof claim.
- `REFUTED`, `RETRACTED`: preserve the failure and its reason.

See [`CLAIMS_LEDGER.md`](CLAIMS_LEDGER.md) for the full single-label taxonomy.
Generated JSON/CSV/certificates under `artifacts/` are evidence, not editable
documentation.

## Collaboration entry points

- New mathematical question: use the `research-question` issue template.
- New bounded computation: use the `experiment` issue template.
- Proposed status change or proof claim: use the `claim-audit` issue template.
- Before implementation: read [`../AGENTS.md`](../AGENTS.md) and identify the
  claim ID, exact scope, independent verifier, adversarial set, and stop
  criterion.
