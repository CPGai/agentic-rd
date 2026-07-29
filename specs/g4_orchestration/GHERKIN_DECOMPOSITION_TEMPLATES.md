# GHERKIN_DECOMPOSITION_TEMPLATES.md

**Domain:** G4 — Multi-Agent Orchestration  
**Status:** DRAFT_PRE_GATE  
**Purpose:** Root orchestrator decomposes missions into tagged Gherkin that binds specialists, risk, and caps.  
**Constraint:** Templates only — no application runtime.

---

## 1. Decomposition pipeline (normative)

```
Mission (user intent + constraints)
  → Feature (business/system capability)
    → Scenario (observable behaviour)
      → Task envelope (JSON) assigned to @agent card
```

Rules:

1. Every Scenario that mutates state or spends money **must** carry `@risk` and `@agent`.  
2. Background steps are shared preconditions; do not hide payments in Background.  
3. Examples tables carry only non-secret data.  
4. Task envelopes are the only artifact leaves execute against (not free chat).

---

## 2. Tag vocabulary

| Tag | Meaning | Required when |
|---|---|---|
| `@agent:<card_id>` | Target specialist card | All executable scenarios |
| `@risk:T0..T4` | G4 agent risk tier | Always |
| `@edge:deterministic\|dynamic\|hitl` | Decision boundary class | Always |
| `@pattern:P-*` | Topology pattern id | Optional |
| `@payment` | Touches AP2/x402 | Any commercial path |
| `@lro` | Expected >10s | Long tasks |
| `@parallel` | Safe for fan-out | Independent scenarios |
| `@hitl` | Hard pause | High stakes |
| `@option2` / `@option3` | Overlay availability | Divergent paths |

---

## 3. Task envelope schema (logical)

```yaml
task_envelope:
  task_id: string
  parent_trace_id: string
  mission_id: string
  feature: string
  scenario: string
  card_id: string
  edge_kind: deterministic | dynamic | hitl
  inputs:
    content_type: string
    body: object
  expected_outputs:
    content_type: string
    schema_ref: string
  caps:
    timeout_ms: int
    max_tokens: int
    max_tool_calls: int
    max_spend_minor_units: int
    currency: string
  gherkin_ref: string
  mandate_ref: string | null
  join_group: string | null
```

---

## 4. Feature template — factory mission

```gherkin
@domain:G4 @option2
Feature: Hierarchical mission decomposition
  As a Systems Architect
  I want the root orchestrator to decompose intent into specialist tasks
  So that multi-agent work stays auditable and policy-bound

  Background:
    Given resume token context includes G1 G2 G3 locks
    And the private Agent Card registry is loadable
    And policy intercept seat is DECLARED_NOT_WIRED or wired

  @agent:card.root.orchestrator @risk:T2 @edge:dynamic
  Scenario: Decompose a declarative-only mission
    Given a mission "Author G4 failure mode matrix"
    When the root decomposes the mission
    Then a Feature pack exists with at least 1 Scenario
    And every Scenario has @agent and @risk tags
    And no Scenario requests L4 AgentCreator

  @agent:card.root.orchestrator @risk:T2 @edge:deterministic
  Scenario: Reject unregistered specialist
    Given a task targeting card_id "card.unknown"
    When card resolve runs
    Then the handshake enters DENY_TERMINAL
    And no leaf is invoked
```

---

## 5. Feature template — sequential assembly line

```gherkin
@domain:G4 @pattern:P-SEQ @option2
Feature: Sequential declarative delivery line
  Spec specialist produces Gherkin, coding specialist emits YAML/MD only,
  security and critic review before eval packaging.

  @agent:card.leaf.spec_gherkin @risk:T1 @edge:dynamic
  Scenario: Author acceptance scenarios from mission
    Given mission_id "M-SEQ-001"
    When the spec specialist runs
    Then output content_type is application/gherkin
    And scenarios are tagged with downstream @agent ids

  @agent:card.leaf.strong_coder @risk:T2 @edge:dynamic
  Scenario: Emit declarative artifacts only
    Given a task envelope with allowed paths under specs/
    When the coding specialist completes
    Then artifacts are YAML or Markdown or Gherkin
    And no raw secrets appear in files
    And host-Windows Python was not used

  @agent:card.leaf.security_review @risk:T2 @edge:dynamic
  Scenario: Security review blocks secret leakage
    Given a diff that contains a leaked credential placeholder pattern
    When security specialist reviews
    Then recommendation is deny
    And root verdict is escalate_HITL or fail
```

---

## 6. Feature template — parallel fan-out

```gherkin
@domain:G4 @pattern:P-PAR @option2 @parallel
Feature: Parallel research fan-out with join barrier
  Independent research slices join before root narrative aggregate.

  @agent:card.leaf.research @risk:T2 @edge:dynamic @parallel
  Scenario Outline: Research slice
    Given join_group "JG-RES-1" and slice "<topic>"
    When research specialist retrieves with citations
    Then result includes sources[]
    And no unbrokered egress occurs

    Examples:
      | topic              |
      | a2a_agent_card     |
      | ap2_mandate_rules  |
      | circuit_breakers   |

  @agent:card.root.orchestrator @risk:T2 @edge:deterministic
  Scenario: Join requires all_success
    Given join_group "JG-RES-1" with 3 tasks
    And one task TIMED_OUT
    When join barrier evaluates
    Then aggregate status is partial_failure
    And root applies failure mode FM-TIMEOUT recovery policy
```

---

## 7. Feature template — payments (schema path)

```gherkin
@domain:G4 @payment @hitl
Feature: AP2 mandate-bounded micro payment path
  Payments are schema-real but live settle defaults false by default policy.

  @agent:card.root.orchestrator @risk:T4 @edge:hitl @payment
  Scenario: Create mandate requires human
    Given no mandate_ref on session
    When root attempts payment path
    Then HITL_WAIT is entered
    And ledger has no capture entries

  @agent:card.leaf.security_review @risk:T2 @edge:deterministic @payment
  Scenario: Ceiling breach rejects capture
    Given mandate max_per_tx minor_units 2500
    And merchant quote minor_units 5000
    When AP2 ceiling compare runs
    Then kind reject is ledgered
    And state DENY_TERMINAL or PAYMENT_HOLD with fail
```

---

## 8. Feature template — handshake

```gherkin
@domain:G4
Feature: A2A discovery handshake
  @agent:card.root.orchestrator @risk:T2 @edge:deterministic
  Scenario: Happy path to RUNNING
    Given an allowlisted leaf card with valid schema
    When handshake runs
    Then states include CARD_RESOLVE SECURITY_EVAL QUOTE_CAPS POLICY_CHECK TASK_OFFER ACCEPTED RUNNING
    And caps.timeout_ms is set

  @agent:card.remote.billing_specialist_example @risk:T4 @edge:deterministic
  Scenario: Remote example denied by policy
    Given active security policy
    When root attempts delegate to remote billing example
    Then decision is deny
    And enabled flag remains false
```

---

## 9. Structural test skeleton (post-gate Step E hint)

```text
tests/test_g4_orchestration.py  # deferred until token — do not deposit unless E scoped
- parse domain workflow_graph.yaml
- assert resume_token_expected == G4_TOPOLOGY_APPROVED_v1
- assert l4_enabled is false
- load all agent_cards/*.json; required keys present
- assert remote example option_2.enabled is false
- assert failure matrix contains timeout, region_collision, budget_ceiling
```

---

## 10. Anti-patterns

| Anti-pattern | Why banned |
|---|---|
| Scenario without `@agent` | Unassignable / unauditable |
| Payment in Background | Hidden high-stakes |
| Leaf free-chat without envelope | Skips policy caps |
| Treating UI click as mandate | AP2 authenticity failure |
| Parallelizing dependent SEQ steps | Race / regional collision |

---

*G4 Step D Gherkin templates — declarative only*
