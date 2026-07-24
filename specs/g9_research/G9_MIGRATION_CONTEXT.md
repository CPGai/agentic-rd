# G9 Migration Context — Domain G8 Handoff

**From Domain:** G8 (Secure Multi-Tenant Runtimes)  
**To Domain:** G9 (Autonomous Research Loops)  
**Handoff Date:** 2026-07-24  
**G8 Status:** APPROVED (`G8_MULTITENANT_APPROVED_v1`)  
**G8 Tag:** `multitenant-v1.0.0`  
**Overlay:** OPTION_2_STANDARD  

---

## 1. G8 Outputs (Locked Artifacts)

| Artifact | Size | Role |
|---|---|---|
| `specs/g8_multitenant/MULTI_TENANT_SECURITY_ARCHITECTURE.md` | 495 lines | Tiered isolation (ISO-1/2/3), SPIFFE identity, authorization envelopes, OWASP LLM06 controls, hybrid policy server, 7-pillar Effective Trust per-tenant, option matrix |
| `specs/g8_multitenant/CAPABILITY_DISCOVERY.yaml` | 397 lines | 5 sandbox runtimes (Docker, gVisor, Firecracker, GKE, Kata); 5 PII redaction middleware; SPIFFE/SPIRE sourcing; procurement T1-T4 + gaps |
| `specs/g8_multitenant/POLICY_DSL_SPEC.md` | 303 lines | Policy DSL grammar (EBNF), structural vs semantic rules, tenant risk-tier mapping, G7 hard bound enforcement, fail-closed default |
| `specs/g8_multitenant/tenant_policies.yaml` | 530 lines | 10 system-wide rules (G7 HBs); 4 tenant configurations (RT-1 to RT-4); per-tenant circuit breakers; cross-tenant guarantees |
| `specs/g8_multitenant/sandbox_templates.yaml` | 457 lines | 4 sandbox templates (Docker/gVisor/Firecracker/Kata); seccomp profiles; shared volume redaction; template selection matrix |
| `specs/g8_multitenant/authorization_envelopes.yaml` | 357 lines | SPIFFE SVID config; envelope schema (12 required fields); JIT downscoping (7-step pipeline); capability model (8 classes); identity guarantees |
| `specs/g8_multitenant/observability_pipelines.yaml` | 413 lines | PII-redacted OTEL routing; 3 deterministic filters + LLM advisory; per-tenant pipelines (RT-1 to RT-4); 6 dashboard panels; G5 inheritance per-tenant |
| `tests/test_g8_multitenant.py` | 480+ lines | 40 stdlib unittests (ST-G8-01 through ST-G8-40): architecture, capability discovery, tenant policies, sandbox templates, auth envelopes, observability, DSL, cross-tenant attack simulation (10 vectors, 0 breaches) |
| `scripts/verify_g8_multitenant.py` | 460+ lines | Standalone pack verifier (215 checks): file existence, YAML safe-load, MD section grep, structural content checks, cross-artifact consistency, secret scan, XML/HTML scan, cross-tenant attack simulation |

**Verification:**
- Unittest suite: 40/40 OK
- Pack verifier: 215/215 OK
- Cross-tenant breach count: 0 (10 attack vectors simulated)
- PII redaction coverage: 100%
- SPIFFE SVID validation: 100%
- Per-tenant circuit breaker independence: confirmed
- 0 secrets found across all artifacts

---

## 2. Key G8 Architecture Decisions for G9

### 2.1 Hybrid Policy Server (Non-Delegatable)
G8 wires the G4 `DECLARED_NOT_WIRED` policy intercept seat into a multi-tenant architecture. The policy server combines structural role validation (deterministic) and semantic PII/safety interception (deterministic filter + LLM advisory). The LLM never has final authority on privilege — it can only escalate (allow to hitl) or confirm (deny to deny).

**G9 impact:** Research loops must pass all tool calls through the policy server. Research agents operating across tenants must carry per-tenant SVIDs. Cross-tenant research requires HITL approval.

### 2.2 Tiered Isolation (ISO-1/ISO-2/ISO-3)
Standard tenants use Docker (ISO-1); regulated tenants use gVisor (ISO-2); high-risk tenants use Firecracker (ISO-3). Risk tier is assigned at registration by the human and is not auto-escalatable.

**G9 impact:** Research loops running in regulated or high-risk tenants will have stricter circuit breaker thresholds (0.70/0.80 vs 0.50), longer audit retention (90/365 days), and restricted self-improvement (S2 HITL only or S1 freeze only).

### 2.3 SPIFFE Identity with JIT Downscoping
Every tool call requires a SPIFFE JWT-SVID with 15-minute TTL. Capabilities are downscoped per call (zero ambient authority). SVID tenant_id is immutable.

**G9 impact:** Research agents must obtain SVIDs per tenant. Long-running research loops must handle SVID rotation (15-minute expiry). Cross-tenant research requires separate SVIDs per tenant.

### 2.4 Per-Tenant G5/G6/G7 Inheritance
All G5 evaluation mechanisms (trust score, circuit breaker, AgBOM, PII scrubbing, LLM-as-Judge, Red/Blue/Green), G6 vibe-environment rules (workspace mode, prototype dune, SDD), and G7 self-improvement bounds (loop budget, hard bounds, L4 disabled) are scoped per-tenant.

**G9 impact:** Research loops inherit per-tenant evaluation. A research loop in Tenant A cannot affect Tenant B's trust score, circuit breaker, or improvement loop.

### 2.5 Eight New Constraint IDs (C-MT-01 to C-MT-08)
G8 adds 8 new constraints to the constraint catalog:
- C-MT-01: Zero cross-tenant data leakage
- C-MT-02: Policy server is non-delegatable
- C-MT-03: Per-tenant circuit breaker isolation
- C-MT-04: Per-tenant trust score isolation
- C-MT-05: Per-tenant improvement loop budget
- C-MT-06: SPIFFE SVID required for all tool calls
- C-MT-07: Authorization envelope required for all tool calls
- C-MT-08: PII redaction before OTEL export

**G9 impact:** Research loops must comply with all C-MT-* constraints. Cross-tenant research data flows must pass through the policy server with full envelope validation.

---

## 3. Unresolved Risks Carried Forward to G9

| Risk | G8 Severity | G9 Relevance |
|---|---|---|
| KVM/nested virt support in WSL2 unconfirmed | MED | Firecracker/Kata (ISO-3) may not be deployable locally; G9 research loops may need cloud deployment for RT-4 tenants |
| Honcho multi-tenant auth not implemented (AUTH_USE_AUTH=false) | HIGH | Research loops using memory must have per-tenant Honcho namespaces; current Honcho is unauthenticated |
| Hermes profile is single-tenant | MED | Research agents across tenants need per-tenant profile isolation; current profile system does not support this |
| No per-tenant skill namespace in skills directory | MED | Research loops that generate skills must write to `skills/tenants/${tenant_id}/` which does not exist yet |
| Policy server is schema-only (DECLARED_NOT_WIRED in templates) | HIGH | G9 research loops cannot actually execute through the policy server until it is wired in Step E/F of G10 |
| SPIFFE/SPIRE not deployed | HIGH | SVID validation is declarative only; research loops cannot obtain real SVIDs until SPIRE is deployed |

---

## 4. G8 Pre-Conditions for G9

Before starting G9 autonomous research loops:

1. Verify G8 artifacts are intact: `python3 scripts/verify_g8_multitenant.py` must return 215/215
2. Verify G8 unit tests: `python -m unittest tests.test_g8_multitenant -v` must return 40/40 OK
3. Confirm G9 gate resume token from BLUE: `G9_RESEARCH_FLEET_LOCKED_v1`
4. The G9 domain cannot relax any G8 constraint — only tighten
5. Research loops must respect per-tenant isolation, policy server, and SPIFFE identity

---

## 5. AGENTS.md State (Post-G8)

Current state of key sections for G9:
- Section 6 HITL Gate Map: G8 marked with `G8_MULTITENANT_APPROVED_v1` GRANTED
- Section 9 Explicit Non-Actions: G8 APPROVED; G9 may proceed under OPTION_2_STANDARD overlays — still stop at G9's own HITL gate
- G9 is the next domain with its own HITL gate — G8 does NOT auto-unlock G9

---

## 6. Workflow Graph G8 to G9 Edge

```yaml
# From specs/workflow_graph.yaml
G8:
  state: APPROVED
  locked: true
  tag: multitenant-v1.0.0
  resume_token: G8_MULTITENANT_APPROVED_v1
  next_domain: G9
  next_resume_token_expected: G9_RESEARCH_FLEET_LOCKED_v1

G9:
  id: D_G9
  name: autonomous_research_loops
  state: READY_FOR_DOMAIN
  requires: [G1_HARNESS_APPROVED_v1]
  primary_harness_touch: [H_CONTEXT, H_EVAL]
  resume_token_expected: G9_RESEARCH_FLEET_LOCKED_v1
```

The G8 to G9 path: tenant isolation and policy enforcement must be in place before autonomous research loops are enabled — otherwise research agents could leak cross-tenant data or bypass privilege checks.

---

## 7. BLUE Section G9 Reference

```
Normalized domain: Autonomous research loops, synthesis agents, multi-step
reasoning over large corpora, citation grounding, ethics review for research
outputs, human-in-the-loop for research conclusions.

Ultimate engineering objective: Agents that can autonomously research,
synthesize, and cite findings while maintaining human oversight for
conclusions and ethical boundaries.

RESUME_TOKEN: G9_RESEARCH_FLEET_LOCKED_v1
RECOMMENDED_PATH: OPTION_2_STANDARD
```

---

*G9_MIGRATION_CONTEXT.md · Generated from G8 lock at `multitenant-v1.0.0` · 2026-07-24*
