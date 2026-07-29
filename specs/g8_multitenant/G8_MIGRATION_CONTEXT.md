# G8 Migration Context — Domain G7 Handoff

**From Domain:** G7 (Self-Improving Agents)  
**To Domain:** G8 (Secure Multi-Tenant Runtimes)  
**Handoff Date:** 2026-07-24  
**G7 Status:** APPROVED (`G7_IMPROVEMENT_BOUNDS_v1`)  
**G7 Tag:** `self-improvement-v1.0.0`  
**Overlay:** OPTION_2_STANDARD  

---

## 1. G7 Outputs (Locked Artifacts)

| Artifact | Size | Role |
|---|---|---|
| `specs/g7_self_improve/SELF_IMPROVEMENT_ARCHITECTURE.md` | 487 lines | Closed-loop detect-acquire-validate-integrate-measure; severity S1-S4; Pivot/Refine; L4 gating; hard bounds; option matrix |
| `specs/g7_self_improve/CAPABILITY_DISCOVERY.yaml` | 359 lines | Skills inventory (93 profile, 5 workspace); 10 self-improvement skills; 8 Hermes native mechanisms; Honcho status; procurement summary |
| `specs/g7_self_improve/TAXONOMY_AND_BOUNDS.md` | 152 lines | 10 improvement types (IT-01 to IT-10); 10 hard bounds (HB-01 to HB-10); 10 conditional bounds; operator mapping |
| `specs/g7_self_improve/triggers.yaml` | 334 lines | 24 triggers across 6 categories (trajectory, trust score, evaluation, failure mode, pattern, human); cooldown rules |
| `specs/g7_self_improve/oversight_boundaries.yaml` | 270 lines | 4 autonomy zones; 6 HITL gates (HG-01 to HG-06); 10 forbidden actions; workspace mode overrides |
| `specs/g7_self_improve/PIVOT_REFINE_TREE.md` | 253 lines | Master decision tree; 5 operator specs (DRAFT/DEBUG/IMPROVE/PIVOT/REFINE); state machine; rollback protocol |
| `specs/g7_self_improve/skill_gen_templates/README.md` | 136 lines | Skill generation process; 8 quality gates; template variable reference |
| `specs/g7_self_improve/skill_gen_templates/gap_filling_skill.tmpl.md` | 55 lines | Declarative SKILL.md template with placeholders |
| `specs/g7_self_improve/dry_run_metrics.json` | — | 10-cycle dry-run simulation results (audit trail) |
| `tests/test_g7_self_improve.py` | 145 lines | 15 stdlib unittests (ST-G7-01 through ST-G7-15) |
| `scripts/verify_g7_self_improve.py` | 400+ lines | Standalone pack verifier (179 checks) |
| `scripts/dry_run_g7.py` | 440+ lines | Dry-run simulation script (10 cycles) |

**Verification:**
- Unittest suite: 15/15 OK
- Pack verifier: 179/179 OK
- Dry-run: 10/10 cycles completed; metrics reported
- 0 secrets found across all artifacts

---

## 2. Key G7 Architecture Decisions for G8

### 2.1 Bounded Self-Improvement Loop
G7 defines a closed-loop detect-acquire-validate-integrate-measure cycle with severity classes (S1-S4) governing autonomy. S1 (Critical) triggers freeze + HITL; S2 (High) requires HITL before integration; S3 (Medium) allows auto-integrate for token-level changes; S4 (Low) logs only.

**G8 impact:** Multi-tenant isolation must ensure that improvement proposals from one tenant do not affect another. The improvement loop's AgBOM drift detection and circuit breaker must be tenant-scoped.

### 2.2 L4 AgentCreator Still Disabled
G7 grants bounded self-improvement (S3/S4 auto-integration for prompt/token changes). L4 AgentCreator (creating new agents autonomously) remains explicitly disabled — it requires a separate explicit enablement beyond the G7 token.

**G8 impact:** Multi-tenant environments must not allow any tenant to enable L4 independently. The L4 gate is system-wide, not per-tenant.

### 2.3 Hard Bounds (HB-01 to HB-10)
Ten non-negotiable bounds that cannot be relaxed under OPTION_2. Key bounds for G8:
- **HB-05:** No secret/credential generation — generated skills/prompts must not create or store credentials
- **HB-06:** No cross-profile writes — improvements target current profile only (G8 must enforce per-tenant isolation)
- **HB-07:** No host-Windows execution — all validation runs in WSL2 substrate

### 2.4 Improvement Loop Budget
Max 10 improvement proposals per session; pause + HITL to continue. This prevents infinite loops.

**G8 impact:** Per-tenant loop budgets must be enforced. One tenant's improvement loop must not consume resources needed by another tenant.

### 2.5 SDD Compliance (G6 Inheritance)
Self-improvement operates on SPECS, not directly on code. All production improvements follow spec → human review → codegen → eval → HITL.

**G8 impact:** Tenant-specific spec modifications must be isolated. Shared specs (AGENTS.md, HARNESS_SPEC.md) cannot be modified by any tenant's improvement loop.

---

## 3. G5/G6 Inheritance (Active for G8)

All G5 evaluation mechanisms and G6 vibe-environment rules are inherited by G7 and must be respected by G8:

| Mechanism | G8 Requirement |
|---|---|
| Trust score [0.0, 1.0] | Per-tenant trust scores; no cross-tenant trust contamination |
| Circuit breaker (15 FM triggers) | Per-tenant circuit breaker; trip in one tenant does not affect others |
| Checkpoint protocol | Per-tenant checkpoints; rollback isolated to tenant scope |
| AgBOM drift detection | Per-tenant AgBOM; cross-tenant tool access detected as drift |
| PII scrubbing | Mandatory for all tenants; tenant-specific PII policies |
| LLM-as-Judge | Judge model shared but results isolated per tenant |
| Prototype dune | Per-tenant dune isolation; no cross-tenant dune access |
| SDD | Shared spec format; tenant-specific specs in tenant-scoped directories |

---

## 4. Unresolved Risks Carried Forward to G8

| Risk | G7 Severity | G8 Relevance |
|---|---|---|
| Honcho AUTH_USE_AUTH=false | MED | G8 must address: multi-tenant auth required; no shared unauthenticated memory |
| Cross-profile write guard is system-wide, not per-tenant | MED | G8 must implement per-tenant isolation boundaries |
| Improvement loop budget is per-session, not per-tenant | MED | G8 must scope loop budgets to tenants |
| Generated skills go to profile directory (shared) | HIGH | G8 must isolate generated skills per tenant |
| Circuit breaker is system-wide, not per-tenant | HIGH | G8 must scope circuit breaker to tenant sessions |
| AgBOM is per-session, not per-tenant | MED | G8 must maintain per-tenant AgBOM |
| L4 enablement is system-wide | LOW | G8 must enforce: no tenant can enable L4 independently |
| Dry-run FP rate (30%) exceeds 20% threshold | MED | G8 should not activate auto-integration until detection accuracy improves |

---

## 5. G8 Pre-Conditions from G7

Before starting G8 multi-tenant work:

1. Verify G7 artifacts are intact: `python3 scripts/verify_g7_self_improve.py` must return 179/179
2. Verify G7 unit tests: `python -m unittest tests.test_g7_self_improve -v` must return 15/15 OK
3. Confirm L4 AgentCreator is still disabled in `specs/workflow_graph.yaml` (`l4_agentcreator: false`)
4. Confirm G8 gate resume token from BLUE: `G8_MULTITENANT_APPROVED_v1`
5. The G8 domain cannot relax any G7 constraint — only tighten
6. Review dry-run metrics in `specs/g7_self_improve/dry_run_metrics.json` for FP/degradation baseline

---

## 6. AGENTS.md State (Post-G7)

Current state of key sections for G8:
- §6 HITL Gate Map: G7 marked with `G7_IMPROVEMENT_BOUNDS_v1`
- §9 Explicit Non-Actions: G7 APPROVED; L4 AgentCreator still disabled (separate enablement required)
- G8 is the next domain with its own HITL gate — G7 does NOT auto-unlock G8

---

## 7. Workflow Graph G7→G8 Edge

```yaml
# From specs/workflow_graph.yaml
G7:
  state: APPROVED
  locked: true
  tag: self-improvement-v1.0.0
  resume_token: G7_IMPROVEMENT_BOUNDS_v1
  next_domain: G8
  next_resume_token_expected: G8_MULTITENANT_APPROVED_v1

G8:
  id: D_G8
  name: multitenant_policy
  state: READY_FOR_DOMAIN
  requires: [G1_HARNESS_APPROVED_v1]
  primary_harness_touch: [H_CONSTRAINT]
  resume_token_expected: G8_MULTITENANT_APPROVED_v1
```

The G7→G8 path (E120) is: `self_improve_bounds_before_multitenant`. G7's bounded loop must be in place before multi-tenant isolation is added — otherwise, one tenant's self-improvement could destabilize others.

---

## 8. BLUE §G8 Reference

```
Normalized domain: Ephemeral sandboxing (containers/gVisor/Firecracker),
enterprise policy server (structural role + semantic PII safety), dynamic
context resolvers, tenant isolation (compute/data/identity/network/observability),
Red/Blue/Green per tenant, authorization envelopes.

Ultimate engineering objective: Every tenant runs in an ephemeral environment
governed by tenant-specific policies; zero cross-tenant data leakage; all tool
calls pass a hybrid policy server that never delegates privilege checks to the LLM.

RESUME_TOKEN: G8_MULTITENANT_APPROVED_v1
RECOMMENDED_PATH: OPTION_2_STANDARD
```

---

*G8_MIGRATION_CONTEXT.md · Generated from G7 lock at `self-improvement-v1.0.0` · 2026-07-24*
