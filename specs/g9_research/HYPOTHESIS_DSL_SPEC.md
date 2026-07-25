# Hypothesis DSL Specification

**Domain:** G9 — Autonomous Research Loops
**Tier:** Strong Coding (Step C)
**Status:** DRAFT_PRE_GATE
**Overlay:** OPTION_2_STANDARD
**Upstream:** multitenant-v1.0.0 (G8 LOCKED)
**BLUE Resume Token:** `G9_RESEARCH_FLEET_LOCKED_v1`
**Primary Harness Touch:** H_CONSTRAINT

**Anchors:**
- BLUE §G9 L450: "Hypothesis formalized as Gherkin specs"
- WP-S5: SDD — spec is durable, code is disposable; hybrid Markdown+YAML; token economics
- G6 VIBECODING_SPECTRUM.md: SDD pattern (spec → review → codegen → eval → HITL)
- G4 GHERKIN_DECOMPOSITION_TEMPLATES.md: Mission→Feature→Scenario→task_envelope
- G7 PIVOT_REFINE_TREE.md: DRAFT/DEBUG/IMPROVE operator state machine

---

## 1. Purpose

This document defines the deterministic EBNF grammar for Gherkin-based research hypotheses, structural and semantic validation rules, swarm routing topology, decision vocabulary, and fail-closed citation verification. The grammar is the durable artifact (SDD principle); research investigations generated from it are disposable.

---

## 2. EBNF Grammar

### 2.1 Top-Level Grammar

```ebnf
research_hypothesis    = feature_header, { scenario }, [ metadata_block ] ;

feature_header          = "@hypothesis", "@research", [ "@domain:" domain_tag ],
                        "Feature:", hypothesis_title, newline,
                        "As a", role_description, newline,
                        "I want to", objective_description, newline,
                        "So that", goal_description, newline ;

scenario               = primary_scenario
                       | contradiction_scenario
                       | synthesis_scenario
                       | validation_scenario
                       | ethics_scenario ;

primary_scenario        = tags, "Scenario:", scenario_name, newline,
                         given_block, when_block, then_block ;

contradiction_scenario  = tags, "Scenario:", scenario_name, newline,
                         given_block, when_block, then_block ;

synthesis_scenario      = tags, "Scenario:", scenario_name, newline,
                         given_block, when_block, then_block ;

validation_scenario     = tags, "Scenario:", scenario_name, newline,
                         given_block, when_block, then_block ;

ethics_scenario         = tags, "Scenario:", scenario_name, newline,
                         given_block, when_block, then_block ;

given_block             = "Given", given_condition, newline,
                         { "And", given_condition, newline } ;

when_block              = "When", when_condition, newline,
                         { "And", when_condition, newline } ;

then_block              = "Then", then_condition, newline,
                         { "And", then_condition, newline } ;

tags                   = { "@", tag_name, [ ":", tag_value ], newline } ;

metadata_block         = "# @metadata", newline,
                         "domain:", domain_tag, newline,
                         "confidence_threshold:", float, newline,
                         "max_improve_cycles:", integer, newline,
                         "fleet_topology:", fleet_topology_ref, newline,
                         "citation_policy:", citation_policy_ref, newline ;
```

### 2.2 Terminal Definitions

```ebnf
domain_tag             = letter, { letter | digit | "_" } ;
hypothesis_title        = printable_string ;
scenario_name           = printable_string ;
role_description        = printable_string ;
objective_description   = printable_string ;
goal_description        = printable_string ;
given_condition         = printable_string ;
when_condition          = printable_string ;
then_condition          = printable_string ;
tag_name                = letter, { letter | digit | "_" } ;
tag_value               = printable_string ;
float                  = digit, { digit }, [ ".", digit, { digit } ] ;
integer                = digit, { digit } ;
printable_string        = ? any UTF-8 printable character except newline ? ;
fleet_topology_ref      = "hierarchical_coordinator_specialists"
                         | "debate_protocol"
                         | "single_agent" ;
citation_policy_ref     = "fail_closed" | "advisory" | "lenient" ;
```

### 2.3 Required Tags

| Tag | Required | Values | Purpose |
|---|---|---|---|
| `@hypothesis` | Yes | (present) | Marks feature as a research hypothesis |
| `@research` | Yes | (present) | Marks for research fleet routing |
| `@domain` | Yes | string | Domain tag for specialist routing (e.g. `ml`, `biomed`, `econ`) |
| `@risk` | No | `low`, `medium`, `high` | Risk classification (maps to G8 RT-1–RT-4) |
| `@payment` | No | (present) | Marks scenarios involving paid API calls |
| `@ethics` | No | (present) | Marks scenarios requiring ethics review (HG-RS-05) |

---

## 3. Structural Validation Rules

Structural validation is deterministic — no LLM involvement.

| Rule ID | Rule | Enforcement |
|---|---|---|
| SV-01 | Feature must have `@hypothesis` and `@research` tags | Parser rejects untagged features |
| SV-02 | Feature must have at least one `primary_scenario` | Parser rejects features with only contradiction/synthesis scenarios |
| SV-03 | `given_block` must include `prior_knowledge_context` | Keyword check: at least one Given line references prior knowledge |
| SV-04 | `when_block` must include `investigation_procedure` | Keyword check: at least one When line describes a procedure |
| SV-05 | `then_block` must include `citation_grounded_assertion` | Keyword check: at least one Then line references citation or evidence |
| SV-06 | `confidence_threshold` must be in [0.0, 1.0] | Float range check |
| SV-07 | `max_improve_cycles` must be in [1, 3] | Integer range check (G7 version ceiling) |
| SV-08 | `fleet_topology` must be a valid reference | Enum check |
| SV-09 | `citation_policy` must be `fail_closed` under OPTION_2 | Enum check (OPTION_2 enforces fail-closed) |
| SV-10 | Ethics scenarios must have `@ethics` tag | Tag check on ethics_scenario |

---

## 4. Semantic Validation Rules

Semantic validation uses LLM advisory + deterministic enforcement (G8 hybrid model — LLM proposes, deterministic disposes).

| Rule ID | Rule | Method | Enforcement |
|---|---|---|---|
| SEM-01 | Hypothesis is scientifically testable | LLM advisory + human review (HG-RS-01) | Human gate before investigation |
| SEM-02 | Investigation procedure is methodologically sound | LLM-as-Judge (G5 dual-judge) | Advisory; flag for HITL if score < 0.85 |
| SEM-03 | Acceptance criteria are falsifiable | LLM advisory | Advisory; flag for HITL if not falsifiable |
| SEM-04 | Domain tag matches available specialist fleet | Deterministic fleet registry lookup | Reject if no specialists available |
| SEM-05 | Confidence threshold is appropriate for domain | LLM advisory + deterministic range | Reject if < 0.50 or > 0.99 |
| SEM-06 | Citation policy is fail_closed | Deterministic (SV-09) | Reject if not fail_closed under OPTION_2 |

---

## 5. Swarm Routing Topology

### 5.1 Topology Selection

The `fleet_topology` metadata field determines the routing topology:

| Topology | Description | When to Use |
|---|---|---|
| `hierarchical_coordinator_specialists` | G4 pattern: coordinator routes to specialists | Default; most research hypotheses |
| `debate_protocol` | Specialists debate conflicting findings | When contradiction detection triggers debate mode |
| `single_agent` | One agent handles the full investigation | Simple hypotheses; low-complexity domains |

### 5.2 Hierarchical Coordinator Specialists Routing

```
Hypothesis Spec
    ↓
[Structural Validation: SV-01 to SV-10]
    ↓ PASS
[Semantic Validation: SEM-01 to SEM-06]
    ↓ PASS (HG-RS-01 authorized)
[Coordinator Agent]
    ↓ route by domain_tag
[Literature Search Specialist] → [Data Analysis Specialist]
    ↓                              ↓
[Citation Verification Specialist] ← [Methodology Audit Specialist]
    ↓
[Synthesis Composer Specialist]
    ↓
[DRAFT Synthesis]
```

### 5.3 Specialist Routing Matrix

| Domain Tag | Primary Specialists | Optional Specialists |
|---|---|---|
| `ml` / `ai` | Literature Search, Citation Verification | Data Analysis, Methodology Audit |
| `biomed` | Literature Search, Methodology Audit | Citation Verification, Data Analysis |
| `econ` | Literature Search, Data Analysis | Citation Verification |
| `physics` | Literature Search, Citation Verification | Data Analysis |
| `security` | Literature Search, Methodology Audit | Citation Verification |
| `general` | Literature Search, Citation Verification | Methodology Audit, Data Analysis |

### 5.4 A2A Task Envelope (G4 Inheritance)

Each sub-task routed to a specialist is wrapped in a G4 A2A task envelope:

```json
{
  "task_id": "ULID",
  "hypothesis_id": "ULID",
  "specialist_role": "literature_search | data_analysis | methodology_audit | citation_verification | synthesis_composer",
  "mission": "sub-task objective",
  "context": "relevant hypothesis excerpt + prior results",
  "tools_allowed": ["tool_id list from CAPABILITY_DISCOVERY"],
  "svid_required": true,
  "tenant_id": "from G8 SVID",
  "deadline_cycles": 5,
  "state": "PROPOSED → ACCEPTED → IN_PROGRESS → COMPLETED | FAILED | NEEDS_INPUT"
}
```

---

## 6. Decision Vocabulary

The decision vocabulary defines the finite set of outcomes for each operator cycle:

### 6.1 DRAFT Decisions

| Decision | Meaning | Next State |
|---|---|---|
| `DRAFT_SUCCESS` | Synthesis composed with citation placeholders | DEBUG |
| `DRAFT_PARTIAL` | Some sub-tasks failed; synthesis incomplete | DEBUG (with gaps) |
| `DRAFT_FAILED` | Critical sub-task failure; no synthesis possible | PROPOSED (retry or HITL) |
| `DRAFT_NEEDS_TOOLS` | Required tools not available | HG-RS-02 (Tool Access) |

### 6.2 DEBUG Decisions

| Decision | Meaning | Next State |
|---|---|---|
| `DEBUG_CLEAN` | All citations verified; no contradictions | IMPROVE (finalize) |
| `DEBUG_CITATION_FAILURES` | Some citations unresolvable | IMPROVE (fix citations) |
| `DEBUG_CONTRADICTIONS` | Contradictory evidence found | IMPROVE (resolve) or debate_protocol |
| `DEBUG_METHODOLOGY_FAIL` | Methodology audit found S2 issues | IMPROVE (fix methodology) |
| `DEBUG_S1_FABRICATION` | Fabricated citation detected (S1) | HG-RS-04 (Low Evidence) — freeze |
| `DEBUG_HIGH_DRIFT` | Hypothesis scope drifted > 30% | HG-RS-03 (High Drift) |

### 6.3 IMPROVE Decisions

| Decision | Meaning | Next State |
|---|---|---|
| `IMPROVE_SUCCESS` | All findings fixed; citations verified | VALIDATED |
| `IMPROVE_PARTIAL` | Some findings fixed; S3/S4 remain | VALIDATED (with caveats) |
| `IMPROVE_THRASHING` | Max 3 cycles reached; not converging | HG-RS-05 (Synthesis Sign-off) |
| `IMPROVE_FAILED` | Cannot resolve S1/S2 findings | HG-RS-04 (Low Evidence) |
| `IMPROVE_DRIFT` | Scope changed during improvement | HG-RS-03 (High Drift) |

### 6.4 HITL Decisions

| Decision | Meaning | Next State |
|---|---|---|
| `HITL_APPROVE` | Human approves | Next gate or APPROVED |
| `HITL_REJECT` | Human rejects | REJECTED (terminal) |
| `HITL_REQUEST_CHANGES` | Human requests modifications | Back to IMPROVE |
| `HITL_ESCALATE` | Human escalates to higher gate | Higher HITL gate |

---

## 7. Fail-Closed Citation Verification

### 7.1 Principle

Citation verification is **fail-closed**: if a citation cannot be resolved, the assertion is marked `CITATION_FAILED` and the synthesis cannot proceed to VALIDATED. This is the anti-hallucination core (C-RS-05, C-RS-07).

### 7.2 Verification State Machine

```
CITATION_PLACEHOLDER
    ↓
[Resolve to source URI]
    ├── SOURCE_NOT_FOUND → CITATION_FAILED (S2) → IMPROVE
    ├── SOURCE_ACCESS_DENIED → CITATION_FAILED (S2) → IMPROVE
    └── SOURCE_FOUND
        ↓
        [Extract verbatim quote]
        ├── QUOTE_NOT_FOUND → CITATION_FAILED (S2) → IMPROVE
        └── QUOTE_FOUND
            ↓
            [Contextual accuracy check]
            ├── MISREPRESENTED → CITATION_MISREPRESENTED (S1) → HG-RS-04
            ├── PARTIALLY_SUPPORTS → CITATION_PARTIAL (S3) → IMPROVE
            └── SUPPORTS → CITATION_VERIFIED → assertion confirmed
```

### 7.3 Citation Status Values

| Status | Severity | Meaning | Action |
|---|---|---|---|
| `CITATION_VERIFIED` | — | Source found, quote supports assertion | Assertion confirmed |
| `CITATION_PARTIAL` | S3 | Source found, quote partially supports | IMPROVE: rephrase assertion |
| `CITATION_FAILED` | S2 | Source not found or inaccessible | IMPROVE: find alternative source or remove |
| `CITATION_MISREPRESENTED` | S1 | Source found but quote contradicts assertion | HG-RS-04: freeze + HITL |
| `CITATION_PENDING` | — | Verification in progress | Wait |
| `UNVERIFIED` | S4 | No citation placeholder provided | IMPROVE: add citation or mark as speculation |

### 7.4 Fail-Closed Enforcement

Under OPTION_2_STANDARD, the following are **non-negotiable**:

1. A synthesis with any `CITATION_FAILED` or `CITATION_MISREPRESENTED` status **cannot** transition to VALIDATED
2. A synthesis with `UNVERIFIED` assertions **can** transition to VALIDATED only if explicitly marked as speculation in the text
3. S1 findings (`CITATION_MISREPRESENTED`) **always** trigger HG-RS-04 (Low Evidence gate) — no auto-fix
4. The verification pipeline is deterministic for source resolution and quote extraction; LLM advisory only for contextual accuracy (G8 hybrid model)

---

## 8. Example Hypothesis (Complete)

```gherkin
@hypothesis @research @domain:ml
Feature: LLM Reasoning Chain Length Correlates with Multi-Step Math Accuracy
  As a research agent fleet
  I want to investigate whether chain-of-thought reasoning length correlates with accuracy on multi-step mathematical reasoning tasks
  So that we can determine if longer reasoning chains improve mathematical problem-solving

  Scenario: Primary Investigation
    Given prior knowledge of chain-of-thought prompting literature
      And access to GSM8K and MATH benchmark datasets
      And fleet configured with literature_search and data_analysis specialists
    When the fleet retrieves papers on chain-of-thought reasoning
      And analyzes benchmark results across reasoning chain lengths
      And verifies all citations against source papers
    Then the synthesis reports correlation coefficient with confidence interval
      And all citations are verified against source papers
      And confidence_threshold of 0.85 is met

  Scenario: Contradiction Detection
    Given hypothesis_state is DRAFT
    When contradictory evidence is detected in the literature
    Then hypothesis_state transitions to DEBUG
      And contradiction is logged with full provenance

  Scenario: Synthesis Sign-off
    Given hypothesis_state is IMPROVE_COMPLETE
      And all citations are verified
      And confidence_threshold of 0.85 is met
    When synthesis is drafted
    Then synthesis_state is PENDING_HITL_SIGNOFF

# @metadata
# domain: ml
# confidence_threshold: 0.85
# max_improve_cycles: 3
# fleet_topology: hierarchical_coordinator_specialists
# citation_policy: fail_closed
```

---

## 9. Grammar Validation Pipeline

```
Raw Gherkin Text
    ↓
[1. EBNF Parse] — structural syntax check
    ↓ PASS
[2. Required Tags Check] — @hypothesis, @research, @domain
    ↓ PASS
[3. Structural Validation] — SV-01 to SV-10
    ↓ PASS
[4. Semantic Validation] — SEM-01 to SEM-06 (LLM advisory + deterministic)
    ↓ PASS
[5. HITL HG-RS-01] — human hypothesis authorization
    ↓ APPROVED
[6. Fleet Routing] — coordinator dispatches to specialists
```

Any failure at steps 1–4 returns the hypothesis to PROPOSED with an error report. Step 5 is the first HITL gate.

---

## 10. Cross-Artifact Consistency

All references in this spec:
- **BLUE resume token:** `G9_RESEARCH_FLEET_LOCKED_v1`
- **Upstream tag:** `multitenant-v1.0.0`
- **Overlay:** `OPTION_2_STANDARD`
- **Constraint IDs:** C-RS-01 (Gherkin formalization), C-RS-05 (fail-closed), C-RS-07 (zero ungrounded)
- **HITL gates:** HG-RS-01 (Hypothesis Auth), HG-RS-02 (Tool Access), HG-RS-03 (High Drift), HG-RS-04 (Low Evidence), HG-RS-05 (Synthesis Sign-off)
- **G4 inheritance:** A2A task envelope, hierarchical_coordinator_specialists
- **G7 inheritance:** DRAFT/DEBUG/IMPROVE operators, max 3 cycles
- **G8 inheritance:** SVID required, policy server passthrough, per-tenant isolation

---

*HYPOTHESIS_DSL_SPEC.md · G9 Step C · Strong Coding · DRAFT_PRE_GATE · 2026-07-25*
