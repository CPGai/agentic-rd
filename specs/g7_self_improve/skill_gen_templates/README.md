# G7 — Skill Generation Template (Step D)
# Declarative template for generating SKILL.md specs
# Status: DRAFT_PRE_GATE
# Upstream: vibecoding-v1.0.0 (G6 LOCKED)
# BLUE resume: G7_IMPROVEMENT_BOUNDS_v1

This directory contains declarative templates for generating new SKILL.md
files when the improvement loop detects a capability gap (IT-03, T3 skill
generation).

---

## Template: gap_filling_skill.tmpl.md

Use this template when the DETECT phase identifies a capability gap that no
existing T1/T2 skill covers. The agent fills in the placeholders, then the
generated SKILL.md passes through the quality gates defined in
SELF_IMPROVEMENT_ARCHITECTURE.md section 3.4.

### Placeholder Convention

All placeholders use `{{PLACEHOLDER}}` syntax. The generator must replace
every placeholder before submitting to VALIDATE.

### Quality Gate Checklist (must pass before HITL review)

1. Structural conformance — YAML frontmatter valid; name, description, tags present
2. Progressive disclosure — L1 less than or equal to 50 tokens; L2 body on trigger; L3 references optional
3. Trigger correctness — Trigger condition matches the detected gap class
4. No hallucinated APIs — All tool names verified against workspace or MCP registry
5. Generalization-gap test — Skill trigger matches a class of failures, not a single instance
6. Secret scan — Zero credential patterns
7. Eval gate — Skill exercised against at least 1 benchmark scenario from G5 EVAL_DATASET_BENCHMARKS.json
8. Complexity ceiling — L2 body less than or equal to 2000 tokens

---

## Template Body

```
---
name: {{skill_name}}
description: "{{one_line_description_under_50_tokens}}"
version: 1.0.0
author: "G7 Self-Improvement Loop (generated)"
license: MIT
platforms: [linux, macos, windows]
metadata:
  hermes:
    tags: [{{tag1}}, {{tag2}}, {{tag3}}]
    related_skills: [{{related_skill1}}, {{related_skill2}}]
    generated_by: "G7-improvement-loop"
    generation_trigger: "{{trigger_id_from_triggers_yaml}}"
    gap_class: "{{failure_class_not_single_instance}}"
---

# {{Skill Title}}

## Overview

{{2-3 sentence overview of what this skill does and why it exists.}}

**Core principle:** {{the single most important rule of this skill}}

## When to Use

- {{trigger condition 1}}
- {{trigger condition 2}}
- {{trigger condition 3}}

## When NOT to Use

- {{anti-trigger condition 1}}
- {{anti-trigger condition 2}}

## Procedure

### Step 1: {{step_name}}
{{step_description_with_exact_commands_or_actions}}

### Step 2: {{step_name}}
{{step_description}}

### Step 3: Verify
{{verification_step_with_telemetry_expectation}}

## Pitfalls

| Pitfall | Do instead |
|---|---|
| {{pitfall_1}} | {{corrective_action_1}} |
| {{pitfall_2}} | {{corrective_action_2}} |

## Related

- **Related skills:** {{related_skills_list}}
- **Source spec:** specs/g7_self_improve/SELF_IMPROVEMENT_ARCHITECTURE.md
- **Trigger:** {{trigger_id}}
- **Gap class:** {{gap_class}}
```

---

## Generation Process

1. DETECT phase identifies gap (trigger fires from triggers.yaml)
2. ACQUIRE phase determines no T1/T2 skill covers the gap
3. Agent fills template placeholders using:
   - Trajectory context from the failure that triggered detection
   - Root cause analysis (from systematic-debugging skill if applicable)
   - API/tool verification via context7 MCP
4. Generated SKILL.md passes through quality gates (8 checks above)
5. If any gate fails → DEBUG operator → REFINE (fix template output)
6. If all gates pass → VALIDATE in prototype dune
7. If dune validation passes → HITL gate (HG-02) for production integration
8. If HITL approves → IMPROVE operator commits skill to profile skills/

---

## Template Variables Reference

| Variable | Source | Constraint |
|---|---|---|
| `{{skill_name}}` | Gap analysis | lowercase-hyphen, max 64 chars |
| `{{one_line_description_under_50_tokens}}` | Gap summary | Must fit L1 budget |
| `{{tag1..3}}` | Gap classification | From taxonomy IT-01 to IT-10 |
| `{{related_skill1..2}}` | Skills inventory search | Must exist in profile |
| `{{trigger_id_from_triggers_yaml}}` | triggers.yaml | Valid trigger ID |
| `{{failure_class_not_single_instance}}` | Root cause analysis | Must generalize (section 4.2) |
| `{{step_name}}` | Procedure design | Action-oriented verb phrase |
| `{{exact_commands}}` | Tool/API verification | Must exist in workspace or MCP |
| `{{pitfall_N}}` | Validation failures | From DEBUG operator output |

---

*skill_gen_templates/README.md v1.0.0-draft — G7 Step D — 2026-07-24*
