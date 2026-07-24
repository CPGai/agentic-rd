---
name: agentic-rd-g-domain-runbook
description: >
  Execute Blueprint domains G1–G10: whitepaper ingestion, declarative specs,
  HITL Decision-Support matrices, and HARD_STOP gates. Use when launching or
  locking a G-domain. Do NOT use for ad-hoc app features outside the blueprint.
priority: 80
---

# Agentic R&D G-Domain Runbook (workspace seed)

## Sequence
A ingestion → B capability → C decompose → D specs → E structural tests → F verify/tag

## Rules
1. Course-2 (WP-S*) supersedes Course-1 (WP-F*) on overlap
2. BLUE `RESUME_TOKEN` is authoritative over session aliases
3. Hard-stop at each domain gate; never unlock G(n+1) silently
4. Declarative artifacts only until a domain gate opens codegen
5. WSL2 + `.venv-hermes` for all execution

## G3 lock anchors
- Resume: `G3_CONTEXT_LAYER_LOCKED_v1`
- Pack: `specs/g3_memory/`
- Tag: `context-v1.0.0`
