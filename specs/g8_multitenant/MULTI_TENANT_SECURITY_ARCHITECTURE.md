# Multi-Tenant Security Architecture

**Domain:** G8 — Secure Multi-Tenant Runtimes  
**Tier:** Premium Frontier (Step A)  
**Status:** DRAFT_PRE_GATE  
**Overlay:** OPTION_2_STANDARD  
**Upstream:** self-improvement-v1.0.0 (G7 LOCKED)  
**BLUE Resume Token:** `G8_MULTITENANT_APPROVED_v1`  
**Primary Harness Touch:** H_CONSTRAINT

**Anchors:**
- BLUE §G8 L414–443: Ephemeral sandboxing, enterprise policy server, tenant isolation, authorization envelopes
- WP-S4: 7-pillar Effective Trust (ephemeral sandbox, slopsquatting defense, Red/Blue/Green, OTEL, dynamic resolvers, structural roles, semantic safety)
- WP-S1: Factory Model — harness correctness-by-construction
- WP-F1: L0–L4 taxonomy; L3 MAS coordinator patterns
- WP-F2: MCP host/client/server; confused deputy risk
- G4 POLICY_INTERCEPT_SPEC.yaml: DECLARED_NOT_WIRED policy seat — G8 wires it
- G5 CIRCUIT_BREAKER_RULES.yaml: Trust score decay, 15 FM trip triggers, 6 quarantine states
- G5 OBSERVABILITY_PILLARS_SPEC.yaml: OTEL tracing, PII scrubbing pipeline
- G7 oversight_boundaries.yaml: 4 autonomy zones, HB-06 (no cross-profile writes)

---

## 1. Executive Summary

Every tenant operates inside an ephemeral sandbox governed by tenant-specific policies. Zero cross-tenant data leakage is the non-negotiable security invariant. All tool calls — whether MCP, A2A, shell, or filesystem — pass through a **Hybrid Policy Server** that performs structural role validation and semantic PII/safety interception. The policy server **never delegates privilege checks to the LLM**; the LLM may propose, but the deterministic policy engine disposes.

**Ultimate Engineering Objective (BLUE §G8):** *Every tenant runs in an ephemeral environment governed by tenant-specific policies; zero cross-tenant data leakage; all tool calls pass a hybrid policy server that never delegates privilege checks to the LLM.*

---

## 2. Tiered Isolation Models

Three isolation tiers map to tenant risk classifications. OPTION_2_STANDARD selects a hybrid: logical isolation for standard tenants, hardware-backed isolation for regulated tenants.

### 2.1 Isolation Tier Matrix

| Tier | Isolation Model | Boundary Mechanism | Tenant Risk Class | Overhead | Use Case |
|---|---|---|---|---|---|
| **ISO-1** | Logical (Docker/namespaces) | Linux namespaces + cgroups + seccomp | standard | Low | Internal dev teams, low-risk PII |
| **ISO-2** | gVisor (kernel syscall filter) | User-space kernel interceptor | regulated | Medium | PII-heavy, compliance-bound, financial |
| **ISO-3** | Firecracker microVM | KVM hypervisor + minimal kernel | high-risk | High | Regulated industries, cross-org, legal hold |

### 2.2 OPTION_2 Standard Allocation

- **Standard tenants** → ISO-1 (Docker logical isolation)
- **Regulated tenants** → ISO-2 (gVisor) or ISO-3 (Firecracker) based on risk-tier classification (see §6)
- **Cross-tenant communication** → always through policy server; never direct
- **Shared resources** → model inference (stateless), policy server (stateless decisions), OTEL collector (redacted); never shared memory, filesystem, or network namespace

### 2.3 Isolation Boundary Guarantees

| Boundary | Guarantee | Enforcement |
|---|---|---|
| Compute | No cross-tenant CPU/memory sharing | cgroup isolation (ISO-1), syscall filter (ISO-2), hypervisor (ISO-3) |
| Data | No cross-tenant filesystem visibility | Per-tenant mount namespaces; shared volumes read-only + redacted |
| Identity | No cross-tenant identity assumption | SPIFFE workload identities scoped per tenant; JWT claims include `tenant_id` |
| Network | No cross-tenant network reachability | Per-tenant network namespaces; egress through policy server only |
| Observability | No cross-tenant telemetry leakage | Per-tenant trace context; PII redaction before OTEL export |

---

## 3. SPIFFE Identity Mapping

### 3.1 Workload Identity Model

Each tenant agent receives a **SPIFFE ID** (SPIFFE Workload Identity, per the SPIFFE/SPIRE specification) scoped to the tenant:

```
spiffe://${trust_domain}/tenant/${tenant_id}/agent/${agent_id}
```

- **Trust domain:** `agentic-rd.local` (workspace-level; configurable per deployment)
- **tenant_id:** ULID assigned at tenant registration
- **agent_id:** ULID assigned per agent session within the tenant

### 3.2 Identity Lifecycle

| Phase | Action | Token Lifetime | Scoping |
|---|---|---|---|
| **Provision** | Tenant registration creates SPIFFE trust bundle | Per-tenant CA cert | Tenant-scoped only |
| **Attest** | Agent startup requests SVID (SPIFFE Verifiable Identity Document) via Workload API | 15 min TTL (JWKS rotation) | Bound to agent_id + tenant_id |
| **Authorize** | Policy server validates SVID + tenant_id + capability scope | Per-request | JIT downscope on each tool call |
| **Revoke** | Trust bundle rotation invalidates SVID | Immediate on revocation | All tokens for tenant_id/agent_id invalidated |

### 3.3 JIT Token Downscoping (WP-S4)

Every tool call triggers a **just-in-time capability downscope**:
1. Agent presents SVID + requested capability set
2. Policy server validates SVID, checks tenant policy, checks tool allowlist
3. Policy server issues a **scoped token** with:
   - `tenant_id` (immutable)
   - `agent_id` (immutable)
   - `caps`: intersection of requested + tenant-allowed + role-permitted
   - `exp`: min(requested_exp, tenant_max_exp, 15min_hard_cap)
4. Agent uses scoped token for the single tool call
5. Token is not reusable; next call requires new downscope

**Zero ambient authority:** No agent carries a persistent credential. Every action is individually authorized. (WP-S4: "zero ambient authority")

---

## 4. Authorization Envelope Schema

### 4.1 Envelope Structure

Every tool call (MCP, A2A, shell, filesystem) is wrapped in an **authorization envelope** before execution:

```
AuthorizationEnvelope {
  envelope_id:     ULID                    # unique per call
  tenant_id:       string                  # SPIFFE tenant scope
  agent_id:        string                  # SPIFFE agent scope
  trace_id:        W3C traceparent         # OTEL correlation
  span_id:         W3C span_id             # this call's span
  svid:            SPIFFE_SVID             # workload identity proof
  caps:            [Capability]            # downscoped capability set
  tool_call:       ToolCallDescriptor      # tool name, args_hash, class
  risk_tier:       T1|T2|T3|T4             # procurement risk tier
  policy_decision: allow|deny|hitl|rewrite # policy server verdict
  reason_code:     string                  # machine-readable denial reason
  rule_ids:        [string]                # policy rules that fired
  ts:              ISO8601                 # decision timestamp
  exp:             ISO8601                 # token expiry
}
```

### 4.2 Capability Model

Capabilities are granular, composable, and tenant-scoped:

| Capability Class | Example Caps | Scoping |
|---|---|---|
| `fs.read` | `fs.read:tenant_scope` | Read within tenant's mounted namespace |
| `fs.write` | `fs.write:tenant_scope` | Write within tenant's mounted namespace |
| `net.egress` | `net.egress:policy_proxied` | Network egress through policy server only |
| `shell.exec` | `shell.exec:wsl2_routed` | Shell execution in WSL2 substrate |
| `mcp.call` | `mcp.call:T1_T2_allowlist` | MCP tool calls within T1/T2 allowlist |
| `a2a.delegate` | `a2a.delegate:card_option2` | A2A delegation per agent card constraints |
| `memory.read` | `memory.read:tenant_scope` | Read from tenant's isolated memory store |
| `memory.write` | `memory.write:tenant_scope` | Write to tenant's isolated memory store |
| `skill.gen` | `skill.gen:tenant_scope` | Generate skills in tenant's namespace |
| `budget.spend` | `budget.spend:tenant_ceiling` | Spend up to tenant's token/cost ceiling |

### 4.3 Envelope Validation Pipeline

```
Agent Request
    │
    ▼
┌──────────────────┐
│ 1. SVID Verify    │  ← SPIFFE trust bundle validation
└────────┬─────────┘
         │ valid
         ▼
┌──────────────────┐
│ 2. Tenant Lookup  │  ← tenant_id → tenant policy + risk tier
└────────┬─────────┘
         │ found
         ▼
┌──────────────────┐
│ 3. Cap Intersect  │  ← requested ∩ tenant_allowed ∩ role_permitted
└────────┬─────────┘
         │ non-empty
         ▼
┌──────────────────┐
│ 4. Structural     │  ← role-based validation (deterministic)
│    Role Check     │
└────────┬─────────┘
         │ pass
         ▼
┌──────────────────┐
│ 5. Semantic PII   │  ← PII/safety content scan (deterministic + LLM-assist)
│    Safety Check   │
└────────┬─────────┘
         │ pass
         ▼
┌──────────────────┐
│ 6. Risk Tier      │  ← T1/T2 allow; T3 HITL; T4 deny (OPTION_2)
│    Gate           │
└────────┬─────────┘
         │ pass
         ▼
   allow / rewrite_caps
```

**Critical:** Steps 1–4 and 6 are **purely deterministic**. Step 5 (semantic PII check) may use an LLM as an *advisor* — but the policy server applies a deterministic redaction filter regardless of the LLM's verdict. The LLM never has the authority to allow a PII-bearing egress. (OWASP LLM06: Sensitive Information Disclosure)

---

## 5. Hybrid Policy Server Architecture

### 5.1 Architecture Overview

The Hybrid Policy Server is the **non-delegatable privilege authority** for all tenants. It combines:

1. **Structural role validation** (deterministic) — RBAC + capability checks
2. **Semantic PII/safety interception** (deterministic filter + LLM-assisted advisory)

The LLM is never the final authority on privilege. The policy server always renders the binding decision.

### 5.2 Policy Server Components

```
                    ┌─────────────────────────────────────┐
                    │       HYBRID POLICY SERVER            │
                    │                                       │
  Tool Request ──── │  ┌─────────────┐  ┌──────────────┐  │ ──── Decision
       │            │  │ Structural  │  │ Semantic PII │  │       │
       │            │  │ Role Engine │→ │ Safety Engine│  │       │
       │            │  │ (deterministic)│ (filter+advise)│  │       │
       │            │  └──────┬──────┘  └──────┬───────┘  │       │
       │            │         │                │           │       │
       │            │  ┌──────┴────────────────┴───────┐  │       │
       │            │  │   Decision Combinator          │  │       │
       │            │  │   (deterministic final call)  │  │       │
       │            │  └───────────────────────────────┘  │       │
                    │                                       │
                    │  ┌───────────────────────────────┐    │
                    │  │  Tenant Policy Cache           │    │
                    │  │  (per-tenant YAML → in-memory)  │    │
                    │  └───────────────────────────────┘    │
                    │                                       │
                    │  ┌───────────────────────────────┐    │
                    │  │  Audit Log (OTEL + structured)  │    │
                    │  └───────────────────────────────┘    │
                    └─────────────────────────────────────┘
```

### 5.3 OWASP LLM06 Non-Delegatable Controls

Never delegate privilege checks to the LLM. The following controls must never be delegated to the LLM for evaluation:

| Control ID | Control | Why Non-Delegatable | Enforcement |
|---|---|---|---|
| **LLM06-01** | PII detection before egress | LLM may hallucinate "no PII" to satisfy user intent | Deterministic regex + NER pipeline; LLM advisory only |
| **LLM06-02** | Tenant boundary enforcement | LLM cannot be trusted to self-enforce isolation | Deterministic tenant_id check on every envelope |
| **LLM06-03** | Capability scope verification | LLM may over-grant caps to complete the task | Deterministic cap intersection (request ∩ tenant ∩ role) |
| **LLM06-04** | Secret redaction in logs/traces | LLM may echo secrets in reasoning traces | Deterministic secret scanner pre-OTEL-export |
| **LLM06-05** | Risk-tier enforcement | LLM cannot self-assess procurement risk | Deterministic T1–T4 classification from tool registry |
| **LLM06-06** | Budget ceiling enforcement | LLM may overspend to complete task | Deterministic counter in policy server |
| **LLM06-07** | Cross-tenant write prevention | LLM cannot verify tenant_id correctness | Deterministic path prefix check + SPIFFE SVID validation |
| **LLM06-08** | Confused deputy prevention | LLM may act on user-ambient authority | Require agentic identity; forbid user-ambient delegation as final authz |

### 5.4 Policy Server Placement

The policy server sits **between** the agent and every side-effecting tool:

```
Agent ──→ Policy Server ──→ MCP Server / Shell / FS / A2A / Network
         (all calls pass through; no direct agent→tool path)
```

**Fail-closed mode:** If the policy server is unreachable, all tool calls are denied. No bypass path exists. (G4 POLICY_INTERCEPT_SPEC.yaml precedent: `mode: fail_closed_when_invoked`)

### 5.5 Relationship to G4 Policy Intercept Seat

G4 declared the policy intercept seat as `DECLARED_NOT_WIRED`. G8 **wires** it into the tenant-aware architecture:

- G4 seat: single-tenant, schema-only, deferred to G8
- G8 wiring: multi-tenant, per-tenant policy cache, deterministic decision combinator, OTEL audit trail
- G8 inherits all G4 intercept classes (orchestration, delegation, mcp_call, workspace_write, shell, payment, budget) and adds: `tenant_isolation`, `pii_redaction`, `cross_tenant_check`

---

## 6. Tenant Risk-Tier Classification

### 6.1 Risk Tier Matrix

| Risk Tier | Label | Isolation | PII Handling | Budget Ceiling | Self-Improvement | Circuit Breaker | Example |
|---|---|---|---|---|---|---|---|
| **RT-1** | Internal Dev | ISO-1 (Docker) | Standard redaction | Per-tenant default | S3/S4 auto-integrate | Per-tenant, standard | Internal tooling team |
| **RT-2** | Standard | ISO-1 (Docker) | Enhanced redaction | Per-tenant ceiling | S3/S4 auto-integrate | Per-tenant, standard | Product team |
| **RT-3** | Regulated | ISO-2 (gVisor) | Mandatory PII redaction + audit | Per-tenant + legal hold | S2 HITL only | Per-tenant, enhanced | Financial services |
| **RT-4** | High-Risk | ISO-3 (Firecracker) | Full PII redaction + legal hold + DPA | Per-tenant + legal cap | S1 freeze + HITL | Per-tenant, maximum | Healthcare, legal |

### 6.2 Risk Tier Determination

Risk tier is assigned at **tenant registration** by the human Systems Architect and is **not auto-escalatable** by any agent. De-escalation requires HITL approval. The policy server enforces the tier on every request.

### 6.3 Tier-Specific Controls

**RT-1/RT-2 (Standard):**
- Logical isolation sufficient
- Standard PII redaction pipeline (G5 OBSERVABILITY_PILLARS_SPEC.yaml inherited)
- Self-improvement S3/S4 auto-integration per G7 bounds
- Circuit breaker with 15 FM triggers (G5 inherited)

**RT-3 (Regulated):**
- gVisor syscall filtering (no direct kernel access)
- Enhanced PII redaction: deterministic NER + regex + LLM advisory
- Self-improvement restricted to S2 (HITL before any integration)
- Circuit breaker: enhanced — 15 FM triggers + tenant-specific additional triggers
- Audit log retention: 90 days minimum

**RT-4 (High-Risk):**
- Firecracker microVM (hardware-enforced isolation)
- Full PII redaction: NER + regex + LLM advisory + human review for any PII-bearing output
- Self-improvement: S1 freeze only; no auto-integration under any severity
- Circuit breaker: maximum — all FM triggers + trip at 0.80 trust (vs 0.50 default)
- Audit log retention: 1 year minimum + legal hold capability
- DPA (Data Processing Agreement) flag required at registration

---

## 7. Zero Cross-Tenant Data Leakage Guarantees

### 7.1 Five-Pillar Isolation Guarantee

| Pillar | Guarantee | Enforcement Layer | Verification |
|---|---|---|---|
| **Compute** | No shared execution context | cgroup/namespace (ISO-1), gVisor (ISO-2), hypervisor (ISO-3) | Process list per tenant; no PID overlap |
| **Data** | No shared filesystem visibility | Per-tenant mount namespaces; no shared writable volumes | `mount` output per tenant; no cross-tenant paths |
| **Identity** | No cross-tenant identity assumption | SPIFFE SVID with tenant_id; JWT claims verified per request | Token decode shows only own tenant_id |
| **Network** | No cross-tenant network reachability | Per-tenant network namespaces; egress through policy server only | `ip netns` per tenant; no direct routes |
| **Observability** | No cross-tenant telemetry leakage | Per-tenant trace context; PII redaction before OTEL export | OTEL attributes show only own tenant_id |

### 7.2 Cross-Tenant Attack Surface (Threat Model)

| Attack Vector | Mitigation | Control ID |
|---|---|---|
| Tenant A reads Tenant B's memory | Process isolation (cgroups/namespaces/microVM) | LLM06-02 |
| Tenant A writes to Tenant B's filesystem | Path prefix check + mount namespace | LLM06-07 |
| Tenant A assumes Tenant B's identity | SPIFFE SVID validation; JWT tenant_id immutable | LLM06-02 |
| Tenant A reaches Tenant B's network | Network namespace isolation; no direct routes | LLM06-02 |
| Tenant A sees Tenant B's traces/logs | Per-tenant OTEL trace context; redaction before export | LLM06-04 |
| Tenant A's self-improvement affects Tenant B | Per-tenant improvement loop budget; per-tenant skill namespace | G7 HB-06 (inherited) |
| Tenant A's circuit breaker trips affects Tenant B | Per-tenant circuit breaker state; per-tenant quarantine | G5 inherited |
| LLM hallucinates "no PII" to allow egress | Deterministic PII filter; LLM advisory only | LLM06-01 |
| LLM over-grants capabilities | Deterministic cap intersection; LLM cannot modify caps | LLM06-03 |
| Confused deputy: LLM acts on user-ambient authority | Require agentic identity; forbid ambient delegation | LLM06-08 |

---

## 8. 7-Pillar Effective Trust Integration (WP-S4)

G8 inherits all 7 pillars from G5 and scopes each to per-tenant enforcement:

| Pillar | G5 Definition | G8 Per-Tenant Scoping |
|---|---|---|
| **P1: Ephemeral Sandbox** | Agents run in isolated sandboxes | Per-tenant sandbox allocation (ISO-1/2/3 by risk tier) |
| **P2: Slopsquatting Defense** | Detect malicious/fake packages in tool registry | Per-tenant tool allowlist; package hash verification per tenant |
| **P3: Red/Blue/Green** | Continuous adversarial testing | Per-tenant Red team; Blue team tests per-tenant policy; Green team refactors scoped to tenant |
| **P4: OTEL Observability** | Full trajectory tracing | Per-tenant trace context; tenant_id in every span; redacted before export |
| **P5: Dynamic Context Resolvers** | Context injected at runtime, not prompt-time | Per-tenant context resolver; tenant-specific knowledge/memory/skills loaded |
| **P6: Structural Roles** | RBAC enforced deterministically | Per-tenant role assignments; policy server enforces per tenant |
| **P7: Semantic Safety** | PII/safety content scanning | Per-tenant PII policy; deterministic filter + LLM advisory; LLM never final authority |

---

## 9. G5/G6/G7 Inheritance for Multi-Tenancy

### 9.1 G5 Inheritance (Per-Tenant Scoping)

| G5 Mechanism | Single-Tenant (G5) | Multi-Tenant (G8) |
|---|---|---|
| Trust score [0.0, 1.0] | Per-session | Per-tenant per-session; no cross-tenant trust contamination |
| Circuit breaker (15 FM) | System-wide | Per-tenant; trip in one tenant does not affect others |
| Checkpoint protocol | Per-session | Per-tenant; rollback isolated to tenant scope |
| AgBOM drift detection | Per-session | Per-tenant AgBOM; cross-tenant tool access detected as drift |
| PII scrubbing | Mandatory | Mandatory for all tenants; tenant-specific PII policies (RT-3/RT-4 enhanced) |
| LLM-as-Judge | Shared judge model | Judge model shared but results isolated per tenant |
| Red/Blue/Green | System-wide | Per-tenant teams; cross-tenant red team only with HITL |

### 9.2 G6 Inheritance

| G6 Mechanism | Multi-Tenant Adaptation |
|---|---|
| Workspace mode | Per-tenant workspace mode; tenant may be in vibe/structured/agentic independently |
| Prototype dune | Per-tenant dune isolation; no cross-tenant dune access |
| SDD | Shared spec format; tenant-specific specs in tenant-scoped directories (`specs/tenants/${tenant_id}/`) |
| Slash commands | Per-tenant command surface; dangerous commands disabled for RT-3/RT-4 |
| Hooks | Per-tenant hook registration; shared hooks (pre_commit, pre_tool) enforced globally |

### 9.3 G7 Inheritance

| G7 Mechanism | Multi-Tenant Adaptation |
|---|---|
| Improvement loop budget (10/session) | Per-tenant per-session; one tenant's loop does not consume another's |
| Hard bounds (HB-01 to HB-10) | System-wide (not per-tenant); no tenant can relax any HB |
| HB-05 (no secret generation) | System-wide; all tenants must comply |
| HB-07 (no host-Windows execution) | System-wide; all tenants must comply |
| L4 AgentCreator | System-wide disabled; no tenant can enable independently |
| Generated skills | Per-tenant skill namespace (`skills/tenants/${tenant_id}/`); no cross-tenant skill visibility |
| Improvement ledger | Per-tenant ledger; cross-tenant improvement proposals forbidden |
| SDD compliance | Tenant-specific spec modifications only; shared specs (AGENTS.md, HARNESS_SPEC.md) immutable by tenants |

---

## 10. Authorization Envelope Token Lifecycle

```
 Registration          Attestation            Authorization          Execution          Revocation
 ┌─────────┐          ┌──────────┐          ┌──────────────┐      ┌──────────┐      ┌──────────┐
 │ Tenant   │          │ Agent     │          │ Policy Server │      │ Scoped    │      │ Trust     │
 │ creates  │──────── │ requests  │──────── │ validates     │──── │ Token     │──── │ Bundle    │
 │ SPIFFE   │          │ SVID via  │          │ SVID + caps  │      │ (JIT,     │      │ Rotation  │
 │ trust    │          │ Workload  │          │ + tenant     │      │  per-call,│      │ invalidates│
 │ bundle   │          │ API       │          │ policy       │      │  15min    │      │ all SVIDs │
 └─────────┘          └──────────┘          └──────────────┘      │  max TTL) │      │ for      │
                                                                  └──────────┘      │ tenant   │
                                                                                    └──────────┘
```

**Key properties:**
- Zero ambient authority (no persistent credentials)
- JIT downscope per tool call
- 15-minute hard cap on token TTL
- Revocation via trust bundle rotation (immediate)
- Tenant_id immutable in all tokens

---

## 11. Dynamic Context Resolvers (WP-S4 Pillar 5)

Context is resolved at runtime per tenant — never embedded in prompts:

| Context Type | Resolver | Tenant Scoping |
|---|---|---|
| Instructions | AGENTS.md + tenant-specific overlay | `specs/tenants/${tenant_id}/AGENTS.md` (tightens root only) |
| Knowledge | `specs/` + tenant-scoped specs | `specs/tenants/${tenant_id}/specs/` |
| Memory | Honcho per-directory sessions | Per-tenant Honcho session namespace |
| Examples | Eval goldens + tenant-specific | Per-tenant example registry |
| Tools | G2 registry + tenant allowlist | Tenant-specific tool allowlist (subset of T1/T2) |
| Guardrails | Constraint catalog + tenant policies | `tenant_policies.yaml` per-tenant rules |

---

## 12. Red/Blue/Green Per Tenant

| Team | Role | Per-Tenant Scope |
|---|---|---|
| **Red** | Attempts cross-tenant breach, PII exfiltration, policy bypass | Per-tenant red team; cross-tenant red team only with HITL |
| **Blue** | Tests policy server responses, circuit breaker trips, PII redaction | Per-tenant blue team; tests tenant's own policy rules |
| **Green** | Proposes refactors, skill improvements, spec augmentations | Per-tenant green team; improvements scoped to tenant namespace only |

**Step E (post-gate, deferred):** Cross-tenant attack simulation suite must report **zero successful breaches** across all isolation tiers.

---

## 13. Decision-Support Option Matrix

| Option | Isolation | Policy Server | Identity | Self-Improvement | PII Redaction | Risk |
|---|---|---|---|---|---|---|
| **OPTION_1_CONSERVATIVE** | Fully single-tenant; no multi-tenancy | Optional (G4 schema-only) | Single identity | G7 bounds (single-tenant) | Standard (G5) | Lowest — no multi-tenant risk but blocks G10 multi-tenant production |
| **OPTION_2_STANDARD ★** | Logical (ISO-1) for standard + gVisor/Firecracker (ISO-2/3) for regulated | Central, non-optional, non-delegatable | SPIFFE per-tenant + JIT downscope | Per-tenant bounded (G7 inherited) | Per-tenant PII policy (RT-1 standard → RT-4 full) | Medium — proven isolation primitives; policy server is single point of authority |
| **OPTION_3_CREATIVE** | Full physical isolation (every agent in own Firecracker) | Distributed policy mesh | SPIFFE + per-agent trust domain | Per-tenant + L4 auto-agent-creation | Maximum (per-agent redaction) | Highest — maximum isolation but extreme operational overhead; Firecracker per-agent is resource-intensive |

**Selected Path:** `OPTION_2_STANDARD`  
**Rationale:** Meets production multi-tenancy requirements with proven isolation primitives (Docker namespaces, gVisor syscall filter, Firecracker microVM) and keeps the policy server non-optional and non-delegatable. ISO-1 for standard tenants minimizes overhead; ISO-2/ISO-3 for regulated tenants provides defense-in-depth. SPIFFE + JIT downscope provides zero-ambient-authority identity. Per-tenant scoping of G5/G6/G7 mechanisms prevents cross-contamination without re-architecting the harness.

---

## 14. Required Telemetry (for HITL Gate)

| Telemetry Item | Source | PASS Criterion |
|---|---|---|
| Cross-tenant breach count | Step E attack simulation suite | Must be 0 |
| Policy server false-positive rate | Step E simulation + audit log | Report (design finding for calibration) |
| PII redaction coverage | PII filter audit | 100% of egress calls scanned |
| Per-tenant trust score isolation | G5 circuit breaker audit | No cross-tenant trust contamination |
| Per-tenant circuit breaker isolation | G5 circuit breaker audit | Trip in one tenant does not affect others |
| Per-tenant AgBOM isolation | AgBOM drift detection audit | No cross-tenant tool access |
| Per-tenant improvement loop budget | G7 ledger audit | Per-tenant budget enforced |
| SPIFFE SVID validation rate | Policy server audit log | 100% of tool calls SVID-validated |
| Authorization envelope coverage | Policy server audit log | 100% of tool calls enveloped |

---

## 15. Constraint IDs Enforced (Inherited + New)

| Constraint | Source | G8 Enforcement |
|---|---|---|
| C-ARCH-01 | G1 | WSL2 routing mandatory (all tenants) |
| C-ARCH-02 | G1 | appendWindowsPath=false (all tenants) |
| C-ARCH-03 | G1 | No raw secrets (all tenants) |
| C-ARCH-04 | G1 | Side-effecting tools require Constraint pre-hooks (all tenants) |
| C-SEC-01 | G1 | OWASP Top-10 posture (all tenants) |
| C-SEC-02 | G1 | Least-privilege toolscopes per agent role (per-tenant) |
| C-SEC-03 | G1 | No cross-profile writes (system-wide; no tenant can relax) |
| C-LOOP-02 | G1 | No infinite improvement loops (per-tenant budget) |
| **C-MT-01** | G8 (new) | Zero cross-tenant data leakage (all isolation tiers) |
| **C-MT-02** | G8 (new) | Policy server is non-delegatable privilege authority |
| **C-MT-03** | G8 (new) | Per-tenant circuit breaker isolation |
| **C-MT-04** | G8 (new) | Per-tenant trust score isolation |
| **C-MT-05** | G8 (new) | Per-tenant improvement loop budget |
| **C-MT-06** | G8 (new) | SPIFFE SVID required for all tool calls |
| **C-MT-07** | G8 (new) | Authorization envelope required for all tool calls |
| **C-MT-08** | G8 (new) | PII redaction before OTEL export (all tenants, all tiers) |

---

*MULTI_TENANT_SECURITY_ARCHITECTURE.md · Domain G8 Step A · Overlay: OPTION_2_STANDARD · Upstream: self-improvement-v1.0.0 · BLUE resume: G8_MULTITENANT_APPROVED_v1*
