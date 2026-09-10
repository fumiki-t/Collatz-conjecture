"""Check current claim scope without rewriting historical acceptance artifacts.

This is an integrity guard for an audited status transition, not a proof checker
for literature. The proof/review authority remains the ledger and audit report.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

from scripts.build_claim_index import build_index

BASE = "2da31e63c87f7c2225899f2d2c500629a0e5668d"
HISTORICAL = (
    "phase20_theory.json", "phase20_literature_audit.json", "phase20_verifier.json",
    "phase21_theory.json", "phase21_literature_audit.json", "phase21_obstruction_report.md",
    "phase21_verifier.json",
)


def audit_supersession(root: Path, record: dict) -> list[str]:
    errors = []
    expected = {
        "audit_id":"ext08-scope-audit", "repository_base":BASE,
        "proposal_base":"44430b21705bd69acb6cc29760ee27bdf2433b1f",
        "bundle_sha256":"e4d5692be68bbbe0e08e4380b87623b2e6ce61b78a564d2bb0aa6775074550aa",
        "primary_source":{"url":"https://arxiv.org/pdf/2101.12747v1",
                          "sha256":"e4c5bccec262d8fdb001d7970dee56c347c03d789796c165e79a18dc2d584b9a",
                          "printed_pages":[4,7,8,28,29,30]},
        "status_transition":{"claim":"EXT08","from":"EXTERNAL_THEOREM","to":"OPEN",
                             "reason":"Auxiliary real/2-adic bridge refuted; theorem statement not refuted"},
        "conditional_claims":["P119","P121","P123","P124","P128"],
        "independent_claims":["P118","P120","P122","P125","P126","P127","P219","P220","P221","P222","P242","P243"],
        "open_obligations":["H112","H72","H89","H133"],
        "historical_verification_is_current_theorem_acceptance":False,
        "EXT08_statement_refuted":False,"proves_collatz":False,
    }
    if not isinstance(record,dict):
        return ["scope supersession must be an object"]
    actual = {k:v for k,v in record.items() if k!="historical_files"}
    if json.dumps(actual,sort_keys=True)!=json.dumps(expected,sort_keys=True):
        errors.append("scope supersession boundary mismatch")
    rows = {r["id"]:r for r in build_index(root)["claims"]}
    for ids,status in ((["EXT08"],"OPEN"),(expected["conditional_claims"],"CONDITIONAL"),
                       (expected["independent_claims"],"VERIFIED_THEOREM"),(expected["open_obligations"],"OPEN")):
        for claim in ids:
            if rows.get(claim,{}).get("status")!=status:
                errors.append(f"scope supersession current ledger mismatch: {claim}")
    # P123/P124 retain their historical conditional routes; P127 is independent.
    closure = {"EXT08"}
    while True:
        next_set = closure | {c["id"] for c in rows.values() if closure.intersection(c["dependency_ids"])}
        if next_set==closure:
            break
        closure = next_set
    proved_dependents = [c for c in closure if rows[c]["status"]=="VERIFIED_THEOREM"]
    if proved_dependents:
        errors.append("unconditional theorem depends on quarantined EXT08: "+",".join(sorted(proved_dependents)))
    snapshots = []
    for filename in HISTORICAL:
        path = "artifacts/"+filename
        historical = subprocess.run(["git","show",f"{BASE}:{path}"],cwd=root,capture_output=True,check=False)
        if historical.returncode:
            errors.append(f"missing historical base object: {path}; fetch full history")
            continue
        digest = hashlib.sha256(historical.stdout).hexdigest()
        snapshots.append({"path":path,"sha256":digest})
        try:
            if hashlib.sha256((root/path).read_bytes()).hexdigest()!=digest:
                errors.append("historical evidence changed: "+path)
        except OSError:
            errors.append("historical evidence missing: "+path)
    if record.get("historical_files")!=snapshots:
        errors.append("historical snapshot manifest mismatch")
    return errors
