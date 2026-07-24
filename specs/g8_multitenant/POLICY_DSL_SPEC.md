# Policy DSL Specification

**Domain:** G8 — Secure Multi-Tenant Runtimes  
**Tier:** Strong Coding (Step C)  
**Status:** DRAFT_PRE_GATE  
**Overlay:** OPTION_2_STANDARD  
**Upstream:** self-improvement-v1.0.0 (G7 LOCKED)  
**BLUE Resume Token:** `G8_MULTITENANT_APPROVED_v1`  
**Primary Harness Touch:** H_CONSTRAINT

**Anchors:**
- G8 MULTI_TENANT_SECURITY_ARCHITECTURE.md §5 (Hybrid Policy Server)
- G4 POLICY_INTERCEPT_SPEC.yaml (intercept classes inherited)
- G5 CIRCUIT_BREAKER_RULES.yaml (trust score, FM trip triggers)
- G7 oversight_boundaries.yaml (autonomy zones, hard bounds)
- WP-S4: "zero ambient authority", "contextual authorisation"
- OWASP LLM06: Sensitive Information Disclosure (non-delegatable controls)

---

## 1. Purpose

The Policy DSL is a declarative language for expressing per-tenant authorization rules. It bridges the gap between **structural role validation** (deterministic RBAC + capability checks) and **semantic PII/safety interception** (deterministic filter + LLM advisory). The DSL is designed for:

1. **Tenant risk-tier classification** — map tenants to isolation tiers and capability ceilings
2. **Rule authoring** — express allow/deny/hitl/rewrite decisions in a human-readable, machine-checkable format
3. **Non-delegatable enforcement** — the DSL compiles to deterministic policy server rules; the LLM never interprets policy at runtime

---

## 2. DSL Design Principles

| Principle | Description |
|---|---|
| **Declarative** | Rules describe *what* to enforce, not *how* to enforce it. The policy server implements the execution. |
| **Deterministic** | Rule evaluation is purely boolean logic — no LLM reasoning at evaluation time. The LLM may advise on PII but never on authorization. |
| **Tenant-scoped** | Every rule is evaluated within a tenant context. No rule can reference another tenant's data or identity. |
| **Composable** | Rules compose via AND/OR/NOT. Each rule produces one of: `allow`, `deny`, `hitl`, `rewrite_caps`. |
| **Auditable** | Every rule evaluation produces a decision envelope with rule_ids, reason_code, and trace binding. |
| **Fail-closed** | If no rule matches, the default decision is `deny`. No implicit allow. |

---

## 3. DSL Grammar (EBNF)

```
policy_file        = metadata, tenant_block+
tenant_block       = "tenant", tenant_id, "{", risk_tier, rule_block+, "}"
risk_tier          = "risk_tier", ":", ("RT-1" | "RT-2" | "RT-3" | "RT-4")

rule_block         = rule_category, "{", rule+
rule_category      = "structural" | "semantic" | "isolation" | "budget" | "improvement"

rule               = rule_id, ":", condition, "->", decision
rule_id            = "R-" , identifier
condition          = conjunction ( "|" conjunction )*
conjunction        = predicate ( "," predicate )*
predicate          = expr ( "==" | "!=" | "in" | "not_in" | ">" | "<" | ">=" | "<=" ) expr
expr               = field_access | literal | function_call
field_access       = identifier ("." identifier)*
decision           = "allow" | "deny" | "hitl" | "rewrite_caps" [ "with" cap_override ]
cap_override       = identifier "=" literal ( "," identifier "=" literal )*
function_call      = "matches" "(" expr "," expr ")" | "contains_pii" "(" expr ")" | "risk_of" "(" expr ")"
```

---

## 4. Structural Role Validation Rules

Structural rules are **deterministic RBAC + capability checks**. They evaluate in < 1ms. The LLM never participates in structural rule evaluation.

### 4.1 Rule Examples (Structural)

```yaml
# Tenant t-internal-dev (RT-1, ISO-1)
tenant t-internal-dev {
  risk_tier: RT-1

  structural {
    R-S01: tool.risk_tier in [T1, T2] -> allow
    R-S02: tool.risk_tier == T3 -> hitl
    R-S03: tool.risk_tier == T4 -> deny
    R-S04: agent.role == "root_executor", cap == "shell.exec" -> allow
    R-S05: agent.role == "specialist", cap == "shell.exec" -> deny
    R-S06: cap == "fs.write", path.startswith("specs/tenants/") -> allow
    R-S07: cap == "fs.write", path.startswith("AGENTS.md") -> deny
    R-S08: cap == "fs.write", path.startswith("HARNESS_SPEC.md") -> deny
    R-S09: cap == "mcp.call", mcp.server in [context7] -> allow
    R-S10: cap == "mcp.call", mcp.server not_in [context7] -> deny
    R-S11: cap == "a2a.delegate", card.option_2_enabled == true -> allow
    R-S12: cap == "a2a.delegate", card.option_2_enabled == false -> deny
  }
}
```

### 4.2 Structural Rule Categories

| Category | Purpose | Default Decision |
|---|---|---|
| `capability` | Check if requested cap is in tenant's allowed set | deny (fail-closed) |
| `role` | Verify agent role permits the action | deny |
| `path` | Check filesystem path against tenant's namespace | deny |
| `tool_class` | Verify tool risk tier against tenant's procurement allowlist | deny for T4, hitl for T3 |
| `identity` | Validate SVID tenant_id matches request tenant_id | deny (critical) |
| `network` | Check egress destination against tenant's network allowlist | deny (default) |

---

## 5. Semantic PII/Safety Interception Rules

Semantic rules involve **content-level analysis** — PII detection, safety scanning, secret detection. These rules use a two-phase approach:

1. **Deterministic phase** (always runs): regex PII filter, secret scanner, NER model
2. **Advisory phase** (may run): LLM evaluates content for implicit PII or safety concerns

The deterministic phase always has the final word. If the deterministic filter finds PII, the decision is `deny` regardless of the LLM's advisory verdict. If the LLM flags PII but the deterministic filter doesn't, the decision is `hitl` (escalate for human review), not `allow`.

### 5.1 Rule Examples (Semantic)

```yaml
tenant t-financial-services {
  risk_tier: RT-3

  semantic {
    R-SEM01: contains_pii(tool_call.output) == true -> deny
    R-SEM02: contains_pii(tool_call.output) == false, llm_advisory.pii_detected == true -> hitl
    R-SEM03: matches(tool_call.output, ".*\\b\\d{16}\\b.*") == true -> deny
    R-SEM04: matches(tool_call.output, ".*\\b[A-Z0-9]{20,}\\b.*") == true -> hitl
    R-SEM05: contains_secret(tool_call.output) == true -> deny
    R-SEM06: contains_secret(otel_span.attributes) == true -> deny
  }
}
```

### 5.2 Semantic Rule Decision Logic

```
                        Deterministic PII Filter
                               |
                    +----------+----------+
                    |                     |
                PII found            No PII found
                    |                     |
                deny                  LLM Advisory
                                        |
                             +----------+----------+
                             |                     |
                        PII detected           No PII detected
                             |                     |
                          hitl                   allow
```

**Critical invariant:** The LLM advisory can only escalate (allow → hitl) or confirm (deny → deny). It can **never** downgrade a deterministic deny to allow. This is the OWASP LLM06 non-delegatable guarantee.

---

## 6. Tenant Risk-Tier Classification Mapping

### 6.1 Risk Tier → DSL Configuration

| Risk Tier | Isolation | Structural Default | Semantic Default | Budget Ceiling | Self-Improvement | Circuit Breaker Trip |
|---|---|---|---|---|---|---|
| **RT-1** | ISO-1 | T1/T2 allow, T3 hitl, T4 deny | Regex PII filter only | Per-tenant default | S3/S4 auto-integrate | 0.50 (G5 default) |
| **RT-2** | ISO-1 | T1/T2 allow, T3 hitl, T4 deny | Regex + NER PII | Per-tenant ceiling | S3/S4 auto-integrate | 0.50 |
| **RT-3** | ISO-2 | T1/T2 allow, T3 hitl, T4 deny | Regex + NER + LLM advisory | Per-tenant + legal hold | S2 HITL only | 0.70 (enhanced) |
| **RT-4** | ISO-3 | T1/T2 allow, T3 hitl, T4 deny | Regex + NER + LLM advisory + human review | Per-tenant + legal cap | S1 freeze only | 0.80 (maximum) |

### 6.2 DSL Risk-Tier Template

```yaml
# RT-2 Standard Tenant Template
tenant ${tenant_id} {
  risk_tier: RT-2

  structural {
    # Capability defaults
    R-RT2-S01: tool.risk_tier in [T1, T2] -> allow
    R-RT2-S02: tool.risk_tier == T3 -> hitl
    R-RT2-S03: tool.risk_tier == T4 -> deny
    # Identity
    R-RT2-S04: svid.tenant_id != request.tenant_id -> deny
    # Filesystem
    R-RT2-S05: cap == "fs.write", path.startswith("specs/tenants/") -> allow
    R-RT2-S06: cap == "fs.write", path.startswith("AGENTS.md") -> deny
    R-RT2-S07: cap == "fs.write", path.startswith("HARNESS_SPEC.md") -> deny
    # Network
    R-RT2-S08: cap == "net.egress", dest not_in tenant_allowlist -> deny
    # Shell
    R-RT2-S09: cap == "shell.exec", interpreter == "host_python" -> deny
  }

  semantic {
    R-RT2-SEM01: contains_pii(output) == true -> deny
    R-RT2-SEM02: contains_secret(output) == true -> deny
    R-RT2-SEM03: matches(output, ".*\\b\\d{16}\\b.*") == true -> deny
  }

  budget {
    R-RT2-B01: session.tokens_used > tenant.token_ceiling -> deny
    R-RT2-B02: session.cost_usd > tenant.cost_ceiling -> deny
    R-RT2-B03: loop.proposals_this_session > 10 -> hitl
  }

  improvement {
    R-RT2-I01: improvement.severity == S1 -> deny
    R-RT2-I02: improvement.severity == S2 -> hitl
    R-RT2-I03: improvement.severity in [S3, S4], improvement.scope == "token_level" -> allow
    R-RT2-I04: improvement.severity in [S3, S4], improvement.scope == "behavioral" -> hitl
  }

  circuit_breaker {
    R-RT2-CB01: trust_score < 0.50 -> trip
    R-RT2-CB02: trust_score < 0.70 -> warning
  }
}
```

---

## 7. Rule Evaluation Pipeline

```
1. Parse tenant_policies.yaml → compile to in-memory rule tree
2. On each tool call:
   a. Extract: tenant_id, agent_id, svid, caps, tool_call, risk_tier
   b. Load tenant's compiled rule tree
   c. Evaluate structural rules (deterministic, < 1ms)
      - If any structural rule denies → deny (no further evaluation)
      - If any structural rule requires hitl → hitl (halt)
   d. Evaluate semantic rules (deterministic phase first)
      - If deterministic PII filter denies → deny
      - If deterministic filter passes → run LLM advisory (optional)
      - If LLM advisory flags PII → hitl
   e. Evaluate budget rules
      - If budget exceeded → deny or hitl
   f. Evaluate improvement rules (if improvement request)
      - If severity > tenant allows → deny or hitl
   g. Evaluate circuit breaker rules
      - If trust_score below trip threshold → trip + deny
   h. If all rules pass → allow (with trace)
3. Emit authorization envelope with decision, rule_ids, reason_code
```

---

## 8. Decision Vocabulary

| Decision | Meaning | Side Effects |
|---|---|---|
| `allow` | Proceed with the tool call | Emit trace, log decision |
| `deny` | Block the tool call | Log reason_code, emit deny trace, update audit log |
| `hitl` | Escalate to human review | Pause execution, emit HITL trace, notify human |
| `rewrite_caps` | Proceed with reduced capabilities | Emit new scoped token, log cap_delta |

---

## 9. Policy DSL vs G4 Policy Intercept Spec

| Aspect | G4 (Pre-G8) | G8 (Post-G8) |
|---|---|---|
| Scope | Single-tenant | Multi-tenant |
| Policy source | POLICY_INTERCEPT_SPEC.yaml (schema-only) | tenant_policies.yaml (per-tenant compiled rules) |
| Identity | `require_agentic_identity: true` | SPIFFE SVID per tenant + JIT downscope |
| PII | `class: pii, default: deny` | Deterministic + LLM advisory; LLM never final authority |
| Circuit breaker | System-wide | Per-tenant |
| Budget | Session-level | Per-tenant per-session |
| Self-improvement | Not scoped | Per-tenant severity gating |
| Seat status | `DECLARED_NOT_WIRED` | `WIRED_PER_TENANT` |

---

## 10. Cross-Reference: G7 Hard Bounds Enforcement in DSL

| G7 Hard Bound | DSL Rule | Enforcement |
|---|---|---|
| HB-01: L4 disabled | `improvement.type == "L4_enablement" -> deny` | System-wide (not per-tenant) |
| HB-02: No constraint self-mod | `cap == "constraint.modify" -> deny` | System-wide |
| HB-03: No circuit breaker bypass | `cap == "circuit_breaker.reset" -> hitl` | System-wide |
| HB-04: No prod code without SDD | `cap == "code.gen", workspace_mode != "agentic_engineering" -> deny` | Per-tenant |
| HB-05: No secret generation | `cap == "secret.gen" -> deny` | System-wide |
| HB-06: No cross-profile writes | `cap == "fs.write", path.startswith("/profiles/") -> deny` | System-wide |
| HB-07: No host-Windows execution | `cap == "shell.exec", interpreter == "host_python" -> deny` | System-wide |
| HB-08: Loop budget 10 | `loop.proposals_this_session > 10 -> hitl` | Per-tenant |
| HB-09: No G6 trigger relaxation | `cap == "transition_trigger.disable" -> deny` | System-wide |
| HB-10: No auto-merge S1/S2 | `improvement.severity in [S1, S2], auto_merge == true -> deny` | Per-tenant |

---

## 11. Validation and Testing (Post-Gate, Step E)

| Test Category | Description | PASS Criterion |
|---|---|---|
| Structural rule coverage | Every tool class has a matching structural rule | 100% coverage |
| Semantic rule coverage | Every PII pattern has a matching semantic rule | 100% coverage |
| Cross-tenant isolation test | Tenant A cannot access Tenant B's data/identity/network | 0 breaches |
| Fail-closed test | No rule matches → deny | All unmatched → deny |
| Non-delegatable test | LLM advisory cannot override deterministic deny | 0 LLM overrides |
| Budget enforcement test | Per-tenant budget ceiling enforced | 0 over-budget calls |
| Self-improvement gating test | Severity gating per risk tier | Correct per tier |

---

*POLICY_DSL_SPEC.md · Domain G8 Step C · Overlay: OPTION_2_STANDARD · Upstream: self-improvement-v1.0.0 · BLUE resume: G8_MULTITENANT_APPROVED_v1*
