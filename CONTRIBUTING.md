# Contributing to Agentic R&D & Implementation Blueprint

## Welcome

Thank you for your interest in contributing to the **Agentic R&D & Implementation Blueprint** — a formally-specified, three-harness Factory Model for autonomous agent systems. This project spans domains G1–G10 and bridges WP-F* (Course-1: November 2025) and WP-S* (Course-2: June 2026) whitepaper architectures.

## Architecture Contract

All contributions operate under the **Three-Harness Factory Model**:

| Harness | Constraint |
|---|---|
| **Context** | Six context types (Instructions, Knowledge, Memory, Examples, Tools, Guardrails); static/dynamic split; progressive disclosure via skills |
| **Constraint** | Deterministic hooks, linters, sandboxes; every `C-*` ID enforceable; L4 disabled until G7 gate |
| **Evaluation** | Tests for deterministic parts; evals for trajectory/semantic; LLM-as-Judge optional in CI |

The binding constitution lives at:
- [`HARNESS_SPEC.md`](./HARNESS_SPEC.md) — deep architectural spec
- [`AGENTS.md`](./AGENTS.md) — global runtime rules, model-routing matrix, HITL gate map
- [`specs/workflow_graph.yaml`](./specs/workflow_graph.yaml) — machine-readable topology

## Getting Started

1. **Environment:** WSL2 Ubuntu 24.04 with project venv `.venv-hermes` (Python 3.12)
2. **Fork & clone** the repository
3. **Conventional Commits** are mandatory: `feat(domain):`, `fix(domain):`, `docs:`, `chore:`
4. Constitution changes (to `AGENTS.md`, `HARNESS_SPEC.md`, `specs/workflow_graph.yaml`) require the `harness` label in the PR

## Development Workflow

### Domain Structure
Each domain G1–G10 follows the Blueprint's 6-step runbook:
- **A)** Ingestion & Synthesis (Premium Frontier)
- **B)** Capability Discovery (Fast Flash)
- **C)** Feature Decomposition (Strong Coding)
- **D)** Workspace Branching & Skill Drafting (Strong Coding)
- **E)** Code Generation & Testing (Strong Coding)
- **F)** Sandbox Verification (Fast Flash)

Every domain includes a **HITL (Human-in-the-Loop) Gate Contract** with explicit GIVEN/WHEN/THEN decision matrices and resume tokens.

### Model Tier Assignment
| Tier | Use |
|---|---|
| **Premium Frontier** | Architecture, ADRs, threat models, research synthesis |
| **Strong Coding** | Scaffolds, declarative configs, Gherkin, meta-prompt execution |
| **Fast Flash** | Validation, syntax checks, mechanical commits |

### Substrate Isolation
All shell/Python/package commands route through WSL2:
```bash
wsl -d Ubuntu-24.04 bash -c "cd /home/carlospg/workspace/agentic-rd && source .venv-hermes/bin/activate && <command>"
```
Host Windows Python/uv is never used for project work.

## Pull Requests

1. Branch naming: `feat/G{domain}-{brief}` or `fix/G{domain}-{brief}`
2. PR description must cite governing Gherkin/spec IDs when changing code on production paths (C-CODE-03)
3. All PRs require:
   - Syntactic/structural lint pass
   - No secret leakage (pre-commit scan)
   - Conventional commit message
4. Constitution-level PRs (`harness` label) require explicit HITL approval
5. L4 (Self-Evolving) capability changes are frozen until `G7_SELF_IMPROVE_BOUNDED`

## Style & Guardrails

- Declarative specs in `specs/`; no raw application code from G1 meta-prompts
- Skills follow agentskills.io layout (L1 metadata → L2 body → L3 references)
- OWASP Top-10 posture; local network treated as untrusted by default
- No hallucinated or slopsquat packages; lockfiles are source of truth
- Skills: progressive disclosure (`SKILL.md` + optional `references/`, `scripts/`, `assets/`)

## G1 Gate Status

| Gate | Status |
|---|---|
| G1 HARNESS | `APPROVED` (`G1_HARNESS_APPROVED_v1` — `OPTION_2_STANDARD`) |
| G2–G10 | READY_FOR_DOMAIN (each has own HITL gate) |

## Questions?

Review the Blueprint at `specs/references/AGENTIC R&D & IMPLEMENTATION BLUE.md` or open an issue tagged `question`.

---

*This project is governed by its architectural constitution. "Vibe coding" stays in prototype dunes. Production paths are agentic engineering.*