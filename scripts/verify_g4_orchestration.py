#!/usr/bin/env python3
"""Standalone G4 orchestration pack verifier (repo source of truth after lock).

Run:
  cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate \
    && python scripts/verify_g4_orchestration.py
"""
from __future__ import annotations

import json
import re
import sys
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent.parent
G4 = ROOT / "specs" / "g4_orchestration"

errors: list[str] = []
checks = 0


def check(cond: bool, msg: str) -> None:
    global checks
    checks += 1
    status = "OK " if cond else "ERR"
    print(f"  {status}  {msg}")
    if not cond:
        errors.append(msg)


# ---------------------------------------------------------------------------
# 1. Required files
# ---------------------------------------------------------------------------
print("=== G4 Pack Verification ===")
required_files = [
    "MULTI_AGENT_TOPOLOGY.md",
    "workflow_graph.yaml",
    "GHERKIN_DECOMPOSITION_TEMPLATES.md",
    "POLICY_INTERCEPT_SPEC.yaml",
    "FAILURE_MODE_MATRIX.yaml",
    "G4_MIGRATION_CONTEXT.md",
    "agent_cards/README.md",
]
for rel in required_files:
    p = G4 / rel
    check(p.is_file() and p.stat().st_size > 0, f"exists {rel}")

cards = sorted((G4 / "agent_cards").glob("*.card.json"))
check(len(cards) >= 8, f"card_count={len(cards)}")

# ---------------------------------------------------------------------------
# 2. YAML parse
# ---------------------------------------------------------------------------
wg = yaml.safe_load((G4 / "workflow_graph.yaml").read_text(encoding="utf-8"))
pol = yaml.safe_load((G4 / "POLICY_INTERCEPT_SPEC.yaml").read_text(encoding="utf-8"))
fm = yaml.safe_load((G4 / "FAILURE_MODE_MATRIX.yaml").read_text(encoding="utf-8"))
check(True, "yaml_parse_all")

# ---------------------------------------------------------------------------
# 3. Topology caps
# ---------------------------------------------------------------------------
caps = wg.get("caps") or {}
check(caps.get("max_concurrent_children") == 3, "caps.max_concurrent_children=3")
check(caps.get("max_spawn_depth") == 1, "caps.max_spawn_depth=1")
check(wg.get("l4_enabled") is False, "l4_enabled=false")
check(
    wg.get("primary_topology") == "hierarchical_coordinator_specialists",
    "primary_topology",
)
check(wg.get("recommended_path") == "OPTION_2_STANDARD", "recommended_path")
check(
    wg.get("resume_token_expected") == "G4_TOPOLOGY_APPROVED_v1",
    "resume_token",
)
check(caps.get("lro_threshold_ms") == 10000, "lro_threshold=10000")

# ---------------------------------------------------------------------------
# 4. Agent cards
# ---------------------------------------------------------------------------
required_card_keys = {
    "id", "name", "version", "description", "url",
    "capabilities", "skills", "security", "risk_tier",
    "policy", "lifecycle", "interaction", "option_2",
}
card_ids = set()
remote_disabled = False
for cp in cards:
    data = json.loads(cp.read_text(encoding="utf-8"))
    missing = required_card_keys - set(data.keys())
    check(not missing, f"card_keys:{cp.name}")
    check(data.get("lifecycle") in {"schema_only", "mock", "wired"}, f"lifecycle:{cp.name}")
    card_ids.add(data.get("id"))
    if data.get("id") == "card.remote.billing_specialist_example":
        remote_disabled = (data.get("option_2") or {}).get("enabled") is False
check(remote_disabled, "remote_billing_disabled")
check("card.root.orchestrator" in card_ids, "root_card_present")
check(len(card_ids) == len(cards), "card_ids_unique")

# ---------------------------------------------------------------------------
# 5. Failure matrix
# ---------------------------------------------------------------------------
modes = fm.get("failure_modes") or []
check(len(modes) == 15, f"failure_modes=15 got={len(modes)}")
check(all(m.get("recovery_declared") for m in modes), "all_recovery_declared")
cov = fm.get("blue_required_coverage") or {}
check(cov.get("timeout") == "FM-TIMEOUT", "blue_timeout")
check(cov.get("region_collision") == "FM-REGION-COLLISION", "blue_region_collision")
check(cov.get("spending_limit_exceed") == "FM-BUDGET-CEILING", "blue_budget_ceiling")
mode_ids = [m["id"] for m in modes]
check(len(mode_ids) == len(set(mode_ids)), "mode_ids_unique")
crit = [m for m in modes if m.get("severity") == "CRITICAL"]
check(len(crit) >= 2, f"critical_modes>={2} got={len(crit)}")

# ---------------------------------------------------------------------------
# 6. Edge classification
# ---------------------------------------------------------------------------
edges = wg.get("edges") or []
kinds = {}
for e in edges:
    k = e.get("kind", "?")
    kinds[k] = kinds.get(k, 0) + 1
check(kinds.get("deterministic", 0) > 0, f"edges.deterministic={kinds.get('deterministic', 0)}")
check(kinds.get("dynamic", 0) > 0, f"edges.dynamic={kinds.get('dynamic', 0)}")
check(kinds.get("hitl", 0) > 0, f"edges.hitl={kinds.get('hitl', 0)}")
check(len(edges) >= 20, f"edge_count={len(edges)}")

db = wg.get("decision_boundaries") or {}
check(len(db.get("deterministic") or []) >= 5, f"boundary.deterministic={len(db.get('deterministic') or [])}")
check(len(db.get("llm_driven") or []) >= 3, f"boundary.llm_driven={len(db.get('llm_driven') or [])}")
check(len(db.get("hitl_required") or []) >= 5, f"boundary.hitl_required={len(db.get('hitl_required') or [])}")

# ---------------------------------------------------------------------------
# 7. Policy gateway
# ---------------------------------------------------------------------------
check(pol.get("status") == "DECLARED_NOT_WIRED", "policy.status=DECLARED_NOT_WIRED")
check(pol.get("seat_id") == "POLICY_SEAT", "policy.seat_id")
check("payment" in (pol.get("intercept_classes") or {}), "policy.payment_class")
check(len(pol.get("rules") or []) >= 5, f"policy.rules={len(pol.get('rules') or [])}")
check(pol.get("mode") == "fail_closed_when_invoked", "policy.fail_closed_mode")

# ---------------------------------------------------------------------------
# 8. Topology doc sections
# ---------------------------------------------------------------------------
topo = (G4 / "MULTI_AGENT_TOPOLOGY.md").read_text(encoding="utf-8")
for section in [
    "## 3. Pattern catalog",
    "## 4. Hierarchical root orchestrator",
    "## 6. A2A discovery handshake",
    "## 8. AP2 micro-payment ledger semantics",
]:
    check(section in topo, f"topo:{section[:30]}")
check("G4_TOPOLOGY_APPROVED_v1" in topo, "topo:resume_token")
check("OPTION_2_STANDARD" in topo, "topo:option2")

# ---------------------------------------------------------------------------
# 9. Gherkin templates
# ---------------------------------------------------------------------------
gher = (G4 / "GHERKIN_DECOMPOSITION_TEMPLATES.md").read_text(encoding="utf-8")
for token in ["Task envelope", "@agent:", "@payment", "Feature:", "@risk:"]:
    check(token in gher, f"gherkin:{token}")

# ---------------------------------------------------------------------------
# 10. Handshake states
# ---------------------------------------------------------------------------
states = set(wg.get("a2a_handshake_states") or [])
required_states = {
    "CARD_RESOLVE", "SECURITY_EVAL", "POLICY_CHECK",
    "TASK_OFFER", "ACCEPTED", "RUNNING",
    "COMPLETED", "FAILED", "TIMED_OUT", "CANCELLED",
    "DENY_TERMINAL", "AGGREGATE",
}
check(required_states.issubset(states), f"handshake_states (missing: {required_states - states})")

# ---------------------------------------------------------------------------
# 11. Secret scan
# ---------------------------------------------------------------------------
secret_rx = re.compile(
    r"(api[_-]?key\s*[:=]\s*['\"][^'\"]{8,}['\"]|"
    r"Bearer\s+[A-Za-z0-9\-._~+/]{20,}={0,2}|"
    r"sk-[A-Za-z0-9]{20,})",
    re.I,
)
scanned = 0
secret_hits = 0
for p in G4.rglob("*"):
    if not p.is_file() or p.suffix.lower() not in {".md", ".yaml", ".yml", ".json"}:
        continue
    scanned += 1
    if secret_rx.search(p.read_text(encoding="utf-8", errors="replace")):
        secret_hits += 1
        errors.append(f"secret:{p.relative_to(G4)}")
check(secret_hits == 0, f"secret_scan (files={scanned}, hits={secret_hits})")

# ---------------------------------------------------------------------------
# Result
# ---------------------------------------------------------------------------
print()
print(f"=== RESULT: {'PASS' if not errors else 'FAIL'} ===")
print(f"checks={checks}  errors={len(errors)}")
print(f"cards={len(cards)}  modes={len(modes)}  edges={len(edges)}  rules={len(pol.get('rules') or [])}")
if errors:
    for e in errors:
        print(f"  ERR  {e}")
    sys.exit(1)
sys.exit(0)
