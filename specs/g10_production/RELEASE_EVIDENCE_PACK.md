# RELEASE_EVIDENCE_PACK.md
# G10 — Production AgentOps Final Release Evidence
# Status: LOCKED
# Resume token: G10_PRODUCTION_DEPLOY_v1
# Tag: production-v1.0.0
# Upstream: research-loop-v1.0.0 @ 6299812

---

## 1. Identity

| Field | Value |
|---|---|
| Domain | G10 Production AgentOps |
| Release tag | `production-v1.0.0` |
| Overlay | OPTION_2_STANDARD |
| Resume token | `G10_PRODUCTION_DEPLOY_v1` |
| Granted | 2026-07-25 |
| Upstream tag | `research-loop-v1.0.0` |
| Upstream lock commit | `6299812` |
| Final gate | true |

---

## 2. Genealogy (G1–G9)

| Domain | Token | Tag |
|---|---|---|
| G1 | G1_HARNESS_APPROVED_v1 | (constitution) |
| G2 | G2_TOOL_REGISTRY_LOCKED_v1 | tool-registry-v1.0.0 |
| G3 | G3_CONTEXT_LAYER_LOCKED_v1 | context-v1.0.0 |
| G4 | G4_TOPOLOGY_APPROVED_v1 | orchestration-v1.0.0 |
| G5 | G5_EVAL_FRAMEWORK_APPROVED_v1 | eval-v1.0.0 |
| G6 | G6_VIBE_ENV_LOCKED_v1 | vibecoding-v1.0.0 |
| G7 | G7_IMPROVEMENT_BOUNDS_v1 | self-improvement-v1.0.0 |
| G8 | G8_MULTITENANT_APPROVED_v1 | multitenant-v1.0.0 |
| G9 | G9_RESEARCH_FLEET_LOCKED_v1 | research-loop-v1.0.0 |
| G10 | G10_PRODUCTION_DEPLOY_v1 | production-v1.0.0 |

---

## 3. Spec Surface Digests (paths)

Durable artifacts (A–D):

- `specs/g10_production/PRODUCTION_AGENTOPS_BLUEPRINT.md`
- `specs/g10_production/CAPABILITY_DISCOVERY.yaml`
- `specs/g10_production/PRODUCTION_DSL_SPEC.md`
- `specs/g10_production/cicd_pipeline.yaml`
- `specs/g10_production/quality_gates.yaml`
- `specs/g10_production/doctor_checks.yaml`
- `specs/g10_production/fleet_management.yaml`
- Input handoff: `specs/g10_production/G10_MIGRATION_CONTEXT.md`

E/F machinery:

- `scripts/dry_run_g10.py`
- `scripts/verify_g10_production.py`
- `tests/test_g10_production.py`
- `specs/g10_production/chaos_dry_run_metrics.json`
- `specs/g10_production/RELEASE_EVIDENCE_PACK.md`

Principle: Gherkin/specs durable; generated code disposable (WP-S5).

---

## 4. Evaluation / Chaos Report

### Pack verifier
- Command: `python scripts/verify_g10_production.py`
- Result: **168/168 OK**

### Unit tests
- Command: `python -m unittest tests.test_g10_production -v`
- Result: **39/39 OK**

### Chaos dry-run (Step E)
- Command: `python scripts/dry_run_g10.py`
- Result: **5/5 scenarios PASS**
- LKG binding: `v0.9.0-previous`

| Scenario | Result | Notes |
|---|---|---|
| spec_surface_intact | PASS | 7 A–D artifacts present |
| policy_spike_llm06 | PASS | 8/8 LLM06 malicious denied; LLM cannot downgrade deny; surge rollback candidacy |
| pii_injection_redaction | PASS | 0 residual raw markers; 0 leaks |
| trust_decay_rollback | PASS | decay >15% → instant LKG (`v0.9.0-previous`), canary_pct=0 |
| doctor_critical_isolation | PASS | DOC-POL-01 CRITICAL → fleet ISOLATED_LKG |

Metrics artifact: `specs/g10_production/chaos_dry_run_metrics.json`

### Thresholds enforced
- Quality auto-flag **5%** / HITL stop **15%**
- Trust floors warning 0.85 / hitl 0.70 / trip 0.50
- Canary trust decay rollback **>15%**
- Canary schedule **1% → 5% → 25% → 100%**

---

## 5. Policy / Security

- OWASP LLM06-01…08: `non_delegatable=true`, `llm_can_bypass=false`
- Policy live-path intent: `WIRED_LIVE_PATH` (from G8 `DECLARED_NOT_WIRED`)
- PII egress leaks in chaos: **0**
- Cross-tenant breach target: **0** (inherited G8)
- Secret scan (pack): **0 hits**
- L4 AgentCreator: **disabled**

---

## 6. Doctor Pre-Promote

| Probe class | Representative IDs | Posture |
|---|---|---|
| SVID | DOC-IDENT-01/02/03 | CRITICAL fail-closed |
| Network boundary | DOC-NET-01/02 | CRITICAL; appendWindowsPath=false |
| Policy ping | DOC-POL-01/02 | CRITICAL |
| Memory bank | DOC-MEM-01/02 | CRITICAL (auth for prod tiers) |
| Supply chain | DOC-SUP-01 | CRITICAL pin concurrence |

Default production Doctor mode: **enforce**

---

## 7. Canary Plan

| Stage | Traffic | Default dwell |
|---|---:|---|
| C1 | 1% | 60 min |
| C2 | 5% | 120 min |
| C3 | 25% | 240 min |
| C4 | 100% | 24–72 h observation (OPTION_2) |

Auto-rollback: **enabled**  
Forbidden: stage skip, start >1%, disable auto-rollback, promote from `prototype/*` or `dune/*`

---

## 8. Rollback Wiring

Confirmed trigger IDs in `fleet_management.yaml`: RB-01 … RB-09  
Primary bindings exercised in chaos:

- RB-02 policy surge candidacy
- RB-03 trust decay >15% → `v0.9.0-previous`
- RB-04 Doctor CRITICAL → fleet isolation  
Max time to LKG (spec): ≤ 5 minutes

---

## 9. Accountability Sign-off

| Role | Decision |
|---|---|
| Systems Architect (HITL) | Approved `G10_PRODUCTION_DEPLOY_v1` |
| Release Officer | Evidence pack complete (this document) |
| Security | LLM06 non-delegatable pack verified in chaos |
| Platform | Verifier + unittest + dry-run green |

Cultural safeguards: max 3 approvals/officer/hour; no batch approve; cool-down after rollback = 1 full pipeline cycle.

---

## 10. Cost Projection Seat

- Monthly cost vs budget gate: QG-042  
- Token budgets by RT tier declared in `quality_gates.yaml`  
- Live $ projection requires environment binding post-tag (not simulated here)

---

## 11. Residual Risks (accepted under canary)

| Risk | Residual | Treatment |
|---|---|---|
| Policy/SPIRE not live-wired in cloud | MED–HIGH | Doctor fail-closed in enforce; post-tag platform wire |
| Honcho auth on prod tenants | MED–HIGH | DOC-MEM-02 |
| A2A load under real traffic | MED | Canary dwell 24–72 h |
| Unknown unknowns | MED | Auto-rollback + LKG |

---

## 12. Sign-off Statement

G1–G9 gates closed. G10 A–D declarative production console complete. Step E chaos dry-run clean. Pack verifier and unit suite green. Under OPTION_2_STANDARD, production entry is reversible via canary + automatic rollback.

**STATUS:** LOCKED — tag `production-v1.0.0`

---

*RELEASE_EVIDENCE_PACK.md · production-v1.0.0 · 2026-07-25*
