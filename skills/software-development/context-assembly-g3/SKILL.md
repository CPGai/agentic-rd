---
name: context-assembly-g3
description: >
  Assemble agent context per G3/HARNESS order: static pack → skills → tools
  (RAG-for-tools) → knowledge → memory window. Use when budgeting tokens,
  co-loading skills, or diagnosing context rot. Do NOT use for multi-agent
  topology (G4) or eval rubrics alone (G5).
priority: 90
---

# Context Assembly G3 (workspace seed)

## Binding order
```
STATIC (Instructions ∩ Guardrails ∩ pinned Memory)
  → Skills L1 scan → L2/L3 on trigger
  → Tools intent-match (G2 RAG-for-tools)
  → Knowledge retrieve + cite
  → Memory window / observations
  → Model
```

## Caps
- Static pack ≤ 20% of active window
- Soft ≤ 3 concurrent L2 bodies
- Flag if co-loaded L2 > ~8k tokens (~32k chars hedge)
- Isolation-only skill eval is forbidden

## Authority
- Specs: `SESSION_STATE_SPEC.md`, `token_budget.yaml`, `SKILL_COLOAD_AUDIT.yaml`
- Precedence: constraints > AGENTS.md > user turn > module tightener > skills > memory

## L3
See `references/assembly-checklist.md` when needed.
