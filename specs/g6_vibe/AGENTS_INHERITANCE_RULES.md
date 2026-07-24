# G6 — AGENTS.md Inheritance Rules for Vibe Coding Surfaces

**Domain:** G6 — Vibe Coding / Agentic IDEs  
**Status:** DRAFT_PRE_GATE  
**Upstream:** G5 APPROVED · `eval-v1.0.0`  
**BLUE resume:** `G6_VIBE_ENV_LOCKED_v1`  
**Overlay:** OPTION_2_STANDARD

---

## 1. Inheritance Principle

WP-S5 (p. 11) and the G1 constitution establish that instruction placement follows a strict hierarchy. Module-level `GEMINI.md` / `CLAUDE.md` files **tighten** the root `AGENTS.md` — they never relax it. This document defines how G6 vibe-coding surfaces inherit and extend the root constitution.

### 1.1 Inheritance Chain

```
Root AGENTS.md (always-on static Instructions)
  ↓ tightens
Module GEMINI.md / CLAUDE.md (project-specific constraints)
  ↓ tightens
AGENTS_INHERITANCE_RULES.md (this file — surface-specific rules)
  ↓ applies to
Surface configs (vibe_environment.yaml, slash_command_mappings.yaml)
```

### 1.2 Core Rule

Any vibe-coding surface configuration may:
- **Tighten** constraints from AGENTS.md (add stricter rules)
- **Clarify** how AGENTS.md rules apply to a specific surface
- **Add** surface-specific constraints that do not conflict with AGENTS.md

A vibe-coding surface configuration may **never**:
- **Relax** a constraint from AGENTS.md
- **Bypass** a HITL gate
- **Disable** a guardrail marked as inviolable
- **Pin** a frozen model version (C-MODEL-01: dynamic routing only)

---

## 2. Surface-Specific Inheritance Rules

### 2.1 Hermes CLI Surface

| AGENTS.md Rule | Inheritance | Surface-Specific Application |
|---|---|---|
| WSL2 routing mandatory (§3.1) | Inherited | All Hermes CLI commands in WSL2 substrate via `.venv-hermes` |
| No host-Windows Python (§3.2) | Inherited | Hermes CLI runs in WSL2; no host Python fallback |
| No secrets (§3.3) | Inherited | `/config` output must be redacted; `.env` never echoed |
| Dynamic model routing (§3.6) | Inherited | `/model` command changes model dynamically; no frozen pins |
| HITL hard stop at gates (§3.7) | Inherited | `/goal` must not proceed past a domain gate without resume token |
| Fail-fast (§3.10) | Inherited | Non-zero exit → halt → diagnose; no brute-force |
| Glass-box (§1 Pillar I) | Inherited | Explanation precedes execution on all CLI commands |
| Sandbox respect (§1 Pillar II) | Inherited | `appendWindowsPath=false` respected; no boundary bypass |

### 2.2 Hermes Desktop App Surface

| AGENTS.md Rule | Inheritance | Surface-Specific Application |
|---|---|---|
| All Hermes CLI rules | Inherited | Desktop app shares same agent core |
| Glass-box | Extended | File browser, terminal pane, review pane provide visual transparency |
| Progressive disclosure (§2 Context) | Inherited | Skills load via same L1→L2→L3 mechanism |

### 2.3 Hermes ACP (IDE Integration) Surface

| AGENTS.md Rule | Inheritance | Surface-Specific Application |
|---|---|---|
| All Hermes CLI rules | Inherited | ACP server shares same agent core |
| Conductor mode default | Clarified | IDE integration primarily supports Conductor mode (real-time pair coding) |
| Spec over vibes (§1 Pillar) | Inherited | IDE completions on production paths require specs to exist |

### 2.4 Antigravity CLI (`agy`) Surface

| AGENTS.md Rule | Inheritance | Surface-Specific Application |
|---|---|---|
| WSL2 routing mandatory | Inherited | `agy` must run in WSL2 substrate; not on Windows host |
| No host-Windows Python | Inherited | `agy` uses its own model backend; project Python stays in `.venv-hermes` |
| Dynamic model routing | Extended | `agy --model` selects model per task; tier mapping applies |
| HITL hard stop at gates | Inherited | `agy` delegated tasks must not cross domain gates |
| Sandbox respect | Inherited | `agy` sandbox must not access host Windows paths |
| No secrets | Inherited | `agy` auth via OS keyring; no secrets in prompts or configs |

### 2.5 Delegate Task / Background Surface

| AGENTS.md Rule | Inheritance | Surface-Specific Application |
|---|---|---|
| All Hermes CLI rules | Inherited | Subagents share same constitution |
| L3 requires G4 gate (§3) | Inherited | `delegate_task` with `role: orchestrator` requires G4 approval |
| max_concurrent_children=3 | Observed | Live Hermes substrate cap; not a constitutional pin |
| max_spawn_depth=1 | Observed | Orchestrator forced to leaf; not a constitutional pin |
| Not durable | Clarified | Background children lost if parent exits; use `cronjob` for durability |
| Trajectory emission | Extended | Child trajectories are advisory observations at parent level (G5) |

### 2.6 Cronjob Surface

| AGENTS.md Rule | Inheritance | Surface-Specific Application |
|---|---|---|
| All Hermes CLI rules | Inherited | Cron jobs run in fresh sessions with full constitution |
| No recursive cron | Extended | Cron-run sessions must not schedule more cron jobs |
| skip_memory=True | Observed | Cron sessions skip memory by default; not a constitutional pin |
| Workdir injection | Extended | `workdir` loads `AGENTS.md` / `CLAUDE.md` from target directory |
| Self-contained prompts | Extended | Cron prompts must be fully self-contained (no chat context) |

---

## 3. Prototype Dune Inheritance

When `/yolo` mode is active (prototype dune), the following rules are **relaxed within the dune only**:

| AGENTS.md Rule | Dune Behavior | Production Behavior |
|---|---|---|
| HITL hard stop at gates | Not enforced (dune) | Enforced (inviolable) |
| Fail-fast | Still enforced | Enforced |
| No secrets | Still enforced | Enforced |
| WSL2 routing | Still enforced | Enforced |
| Glass-box | Still enforced | Enforced |
| Evaluation gates (G5) | Disabled (dune) | Enforced |
| Circuit breaker (G5) | Disabled (dune) | Enforced |
| Checkpoint protocol | Optional (dune) | Mandatory |
| Trajectory emission | Optional (dune) | Mandatory |
| Spec-first (SDD) | Not required (dune) | Required |
| Approval bypass | Allowed (dune) | Forbidden |

**Critical:** The dune relaxation applies ONLY when ALL of these conditions are met:
1. `/yolo` is explicitly toggled on
2. Branch is `prototype/*` or `dune/*`
3. No production secrets in environment
4. No production database access
5. Time-boxed to a single session

If any condition is violated, the dune collapses and full AGENTS.md rules apply immediately.

---

## 4. Module-Level Tightening Rules

Module-level `GEMINI.md` / `CLAUDE.md` files may add constraints for specific project directories:

### 4.1 Permitted Tightening

- Add stricter model tier requirements for specific directories
- Require additional review steps before commits
- Mandate specific test coverage thresholds
- Add project-specific forbidden actions
- Require specific skills to be loaded for certain task types

### 4.2 Forbidden Relaxation

- Cannot relax WSL2 routing
- Cannot enable L4 (until G7 gate)
- Cannot bypass HITL gates
- Cannot disable secret scanning
- Cannot pin frozen model versions
- Cannot relax sandbox boundaries

### 4.3 Conflict Resolution

When root `AGENTS.md` and module files conflict:
1. Root `AGENTS.md` always wins on inviolable rules (§3 Global Rules)
2. Module file wins on project-specific clarifications
3. If uncertainty remains → halt and request HITL clarification (Glass-box principle)

---

## 5. G5 Evaluation Inheritance for Surfaces

All surfaces inherit the G5 evaluation framework with surface-specific application:

| G5 Mechanism | Hermes CLI | Desktop | ACP/IDE | Antigravity | Delegate | Cron |
|---|---|---|---|---|---|---|
| Trajectory schema | mandatory | mandatory | mandatory | mandatory | mandatory (child=advisory) | mandatory |
| Trust score | enforced | enforced | enforced | enforced | enforced | enforced |
| 5%/15% thresholds | enforced | enforced | enforced | enforced | enforced | enforced |
| Circuit breaker | active | active | active | active | active | active |
| Checkpoint | mandatory | mandatory | mandatory | mandatory | mandatory | mandatory |
| PII scrubbing | mandatory | mandatory | mandatory | mandatory | mandatory | mandatory |
| LLM-as-Judge | enforced | enforced | enforced | enforced | enforced | enforced |
| AgBOM | mandatory | mandatory | mandatory | mandatory | mandatory | mandatory |

**Note:** The above applies to **production path** only. Prototype dune relaxations are defined in §3 above.

---

## 6. Surface Configuration Precedence

When multiple surface configs apply:

1. `vibe_environment.yaml` — workspace mode (vibe/structured/agentic)
2. `slash_command_mappings.yaml` — command routing and model tiers
3. `SURFACE_CAPABILITY_MATRIX.yaml` — surface availability and capability inventory
4. `AGENTS_INHERITANCE_RULES.md` (this file) — inheritance and tightening rules
5. Root `AGENTS.md` — inviolable constitution
6. `HARNESS_SPEC.md` — deep architecture and constraint catalog

Later files in this list have **higher authority** — they may tighten but never relax earlier files.

---

## 7. Transition Discipline

When a transition trigger fires (see `vibe_environment.yaml` §transition_triggers):

1. The agent must acknowledge the transition in the trajectory (`Verdict: escalate_HITL` if mode change affects production)
2. Workspace mode must be updated in `vibe_environment.yaml`
3. If transitioning TO `agentic_engineering`: SDD checklist must be satisfied before any further codegen
4. If transitioning FROM `vibe_coding`: all dune-generated code must be reviewed against the new standard
5. The transition itself is auditable — trajectory must record the trigger, the from-mode, and the to-mode

---

*AGENTS_INHERITANCE_RULES.md · G6 DRAFT_PRE_GATE · upstream `eval-v1.0.0` · 2026-07-24*
