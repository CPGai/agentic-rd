# G7 — Improvement Taxonomy & Safety Bounds (Step C)
# Model Tier: Strong Coding
# Status: DRAFT_PRE_GATE
# Upstream: vibecoding-v1.0.0 (G6 LOCKED)
# Overlay: OPTION_2_STANDARD
# BLUE resume: G7_IMPROVEMENT_BOUNDS_v1

---

## 1. Improvement Type Classification Matrix

| ID | Type | Description | Target Artifact | Severity Range | Autonomy (OPTION_2) | HITL Gate |
|---|---|---|---|---|---|---|
| **IT-01** | Prompt Refinement | Token-level adjustment to agent instructions, system prompt, or skill trigger text | AGENTS.md, skill SKILL.md frontmatter, `instructions` field | S3–S4 | Auto-integrate (S4); advisory queue (S3) | Post-log (S4); pre-review if behavioral (S3) |
| **IT-02** | Skill Acquisition (T1/T2) | Load existing skill from profile or agentskills.io hub | Profile `skills/` directory, G3 co-load registry | S3 | Auto-integrate after co-load validation | Post-log |
| **IT-03** | Skill Generation (T3) | LLM drafts new SKILL.md for a detected capability gap | Profile `skills/` (dune) → `skills/` (production after HITL) | S2 | Propose only — dune validation | Before production integration |
| **IT-04** | Spec Augmentation | Add or modify declarative spec artifacts (YAML/MD in `specs/`) | `specs/**` directory | S2 | Propose only | Before spec committed |
| **IT-05** | Tool Adapter Patch (Schema) | Modify tool schema, MCP config, or agent card definition | `specs/g2_tools/`, `specs/g4_orchestration/agent_cards/` | S2 | Propose only | Before schema change |
| **IT-06** | Tool Adapter Patch (Runtime) | Modify runtime tool behavior, MCP server config, or execution path | Runtime config, MCP server args | S1 | **Forbidden** without HITL | Before any runtime change |
| **IT-07** | Constitution Tightening | Propose new constraint or tighten existing constraint in AGENTS.md/HARNESS_SPEC.md | `AGENTS.md`, `HARNESS_SPEC.md` | S1 | Propose only — human must edit | Before any edit |
| **IT-08** | Circuit Rule Modification | Modify G5 trust score thresholds, decay penalties, or quarantine states | `CIRCUIT_BREAKER_RULES.yaml` | S1 | **Forbidden** — G5 is locked | Never (requires G5 gate reopen) |
| **IT-09** | L4 AgentCreator Enablement | Enable L4 self-evolving agent creation capability | `workflow_graph.yaml` L4 node | S1 | **Forbidden** — requires G7 resume token | G7 HITL gate |
| **IT-10** | Memory Fact Recording | Persist improvement outcome as a memory or Honcho conclusion | `memories/`, Honcho Dialectic API | S3–S4 | Auto-integrate | Post-log |

---

## 2. Classification Decision Logic

```
IMPROVEMENT PROPOSED
    │
    ├── Does it modify production code directly?
    │   └── YES → IT-06 (Runtime) or reject → S1 → HITL mandatory
    │
    ├── Does it modify AGENTS.md or HARNESS_SPEC.md?
    │   └── YES → IT-07 (Constitution) → S1 → Human must edit
    │
    ├── Does it modify CIRCUIT_BREAKER_RULES.yaml?
    │   └── YES → IT-08 → S1 → FORBIDDEN (G5 locked)
    │
    ├── Does it enable L4 AgentCreator?
    │   └── YES → IT-09 → S1 → FORBIDDEN (G7 gate)
    │
    ├── Does it create a new skill (SKILL.md)?
    │   └── YES → IT-03 (T3 Generation) → S2 → Dune + HITL
    │
    ├── Does it load an existing skill?
    │   └── YES → IT-02 (T1/T2 Acquisition) → S3 → Auto-integrate
    │
    ├── Does it modify a spec in specs/?
    │   └── YES → IT-04 (Spec Augmentation) → S2 → HITL
    │
    ├── Does it modify a tool schema or MCP config?
    │   └── YES → IT-05 (Schema Patch) → S2 → HITL
    │
    ├── Does it adjust prompt text or trigger wording?
    │   └── YES → IT-01 (Prompt Refinement) → S3/S4 → Auto-integrate
    │
    └── Does it record an outcome or lesson?
        └── YES → IT-10 (Memory Fact) → S3/S4 → Auto-integrate
```

---

## 3. Hard Safety Bounds

### 3.1 Non-Negotiable Bounds (Cannot be relaxed under OPTION_2)

| ID | Bound | Rationale | Enforcement |
|---|---|---|---|
| **HB-01** | L4 AgentCreator remains disabled until `G7_IMPROVEMENT_BOUNDS_v1` | C-LOOP-02; most dangerous capability | `workflow_graph.yaml` `l4_enabled: false`; feature flag |
| **HB-02** | No self-modification of constraint catalog | Agent may propose tightenings but cannot apply them | AGENTS.md §3; `skill_manage` cannot edit AGENTS.md |
| **HB-03** | No circuit breaker bypass | G5 trust score and quarantine states are inviolable | G5 CIRCUIT_BREAKER_RULES.yaml is locked |
| **HB-04** | No production code mutation without SDD | G6: spec → human review → codegen → eval → HITL | G6 vibe_environment.yaml `production_path` activation list |
| **HB-05** | No secret/credential generation | Generated skills/prompts must not create or store credentials | Secret scan quality gate (§3.4.6 of architecture) |
| **HB-06** | No cross-profile writes | Improvements target current profile only | Hermes cross-profile write guard |
| **HB-07** | No host-Windows execution | All validation runs in WSL2 substrate | C-CODE-03; WSL2 routing mandate |
| **HB-08** | Loop budget cap: 10 proposals/session | Prevents infinite improvement loops | Thrashing detection §2.4 of architecture |
| **HB-09** | No relaxation of G6 transition triggers | Improvements cannot lower the vibe→structured→agentic threshold | G6 transition_triggers are declarative; enforcement deferred |
| **HB-10** | No auto-merge of HITL-gated improvements | S1/S2 improvements require explicit human approval | Autonomy table §5.2 of architecture |

### 3.2 Conditional Bounds (Active in production, relaxed in dune)

| ID | Bound | Production | Prototype Dune |
|---|---|---|---|
| **CB-01** | Trajectory emission | Mandatory | Optional |
| **CB-02** | Trust score enforcement | Enforced | Not enforced |
| **CB-03** | Circuit breaker | Active (15 FM triggers) | Disabled |
| **CB-04** | Checkpoint protocol | Mandatory | Optional |
| **CB-05** | PII scrubbing | Mandatory | Optional |
| **CB-06** | LLM-as-Judge | Enforced (different model family) | Not applicable |
| **CB-07** | AgBOM | Mandatory (drift detection) | Not applicable |
| **CB-08** | SDD (spec before code) | Required | Not required |
| **CB-09** | Secret scan on generated skills | Mandatory | Recommended |
| **CB-10** | Generalization-gap test | Mandatory | Recommended |

---

## 4. Improvement Type × Severity × Autonomy Matrix

| Type | S1 (Critical) | S2 (High) | S3 (Medium) | S4 (Low) |
|---|---|---|---|---|
| **IT-01** Prompt Refinement | N/A | HITL review | Auto-integrate (if token-level) | Auto-integrate + log |
| **IT-02** Skill Acquisition (T1/T2) | N/A | N/A | Auto-integrate after validation | Auto-integrate + log |
| **IT-03** Skill Generation (T3) | N/A | Dune + HITL before prod | N/A | N/A |
| **IT-04** Spec Augmentation | N/A | Propose → HITL | N/A | N/A |
| **IT-05** Tool Schema Patch | N/A | Propose → HITL | N/A | N/A |
| **IT-06** Tool Runtime Patch | HITL mandatory | N/A | N/A | N/A |
| **IT-07** Constitution Tightening | Propose → human edits | N/A | N/A | N/A |
| **IT-08** Circuit Rule Change | FORBIDDEN | N/A | N/A | N/A |
| **IT-09** L4 Enablement | FORBIDDEN | N/A | N/A | N/A |
| **IT-10** Memory Fact | N/A | N/A | Auto-integrate | Auto-integrate + log |

---

## 5. Operator → Improvement Type Mapping

| Operator | Applicable Types | Input | Output |
|---|---|---|---|
| **DRAFT** | IT-01, IT-03, IT-04, IT-05, IT-07 | Detected gap + trajectory context | Declarative proposal (spec/skill/prompt/constraint) |
| **DEBUG** | All (when validation fails) | Failed proposal + validation error | Root cause analysis + revised proposal |
| **IMPROVE** | All (after approval) | Approved proposal + integration plan | Integrated artifact + post-integration telemetry |
| **PIVOT** | All (when thrashing/flat curve) | Failed approach + thrashing signal | New direction declaration + fresh DRAFT |
| **REFINE** | All (when partial success) | Partially working proposal | Iterated proposal (v2, v3...) |

---

## 6. Workspace Mode Interaction

| Workspace Mode | IT-01 | IT-03 | IT-04 | IT-07 | IT-09 |
|---|---|---|---|---|---|
| **vibe_coding** (dune) | Auto-integrate | Auto-generate in dune | Auto-draft | Log only | Disabled |
| **structured_assisted** | Advisory queue | Propose → HITL | Propose → HITL | Propose → human | Disabled |
| **agentic_engineering** | HITL if behavioral | Propose → HITL → eval | Propose → HITL → eval | Propose → human | Disabled (G7 gate) |

---

## 7. Telemetry Requirements

| Metric | Source | Threshold | Action |
|---|---|---|---|
| Detection accuracy | DETECT phase | <80% → investigate | S2 improvement on detection itself |
| False positive rate | VALIDATE phase | >20% → investigate | S2 improvement on detection tuning |
| Thrashing events | Loop monitor | ≥3 per session → pause | HB-08 loop budget |
| Degradation count | MEASURE phase | Any post-integration → rollback | Rollback policy §4.4 |
| Improvement proposals/session | Loop counter | >10 → pause | HB-08 |
| Auto-integration success rate | MEASURE phase | <90% → tighten autonomy | Escalate S3→S2 for affected type |
| HITL approval rate | HITL queue | <50% → improve proposal quality | S2 meta-improvement |

---

*TAXONOMY_AND_BOUNDS.md v1.0.0-draft — G7 Step C · 2026-07-24*
